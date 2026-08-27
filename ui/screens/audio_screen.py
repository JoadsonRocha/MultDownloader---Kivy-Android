import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard, VideoPreviewCard, ProgressPanel

class AudioScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "audio"
        self.selected_bitrate = "320kbps"
        self.audio_info = None

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.container = BoxLayout(
            orientation='vertical',
            spacing=12,
            padding=[12, 10, 12, 16],
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        # 1. Campo de URL
        input_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            size_hint_y=None,
            height=50,
            padding=[8, 4, 8, 4],
            spacing=6
        )
        self.input_card = input_card

        self.url_input = TextInput(
            hint_text="Cole o link da música ou vídeo...",
            multiline=False,
            font_size="13sp",
            background_normal='',
            background_color=(0, 0, 0, 0),
            foreground_color=Theme.get_text(self.app.is_dark),
            padding=[6, 10, 6, 10]
        )
        input_card.add_widget(self.url_input)

        # Botão Colar
        self.btn_paste = CustomButton(
            text="📋 Colar",
            font_size="11sp",
            bg_color=Theme.get_input_bg(self.app.is_dark),
            text_color=Theme.get_text(self.app.is_dark),
            size_hint=(None, 1),
            width=65,
            radius=[6, 6, 6, 6]
        )
        self.btn_paste.bind(on_release=self.paste_from_clipboard)
        input_card.add_widget(self.btn_paste)

        # Botão Buscar
        self.btn_fetch = CustomButton(
            text="🔍 Buscar",
            font_size="11sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            size_hint=(None, 1),
            width=65,
            radius=[6, 6, 6, 6]
        )
        self.btn_fetch.bind(on_release=lambda x: self.fetch_audio_info())
        input_card.add_widget(self.btn_fetch)

        self.container.add_widget(input_card)

        # 2. Preview Card
        self.preview_card = VideoPreviewCard(is_dark=self.app.is_dark)
        self.preview_card.opacity = 0.5
        self.container.add_widget(self.preview_card)

        # 3. Seletor de Qualidade do Áudio
        bitrate_box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None, height=75)
        self.bitrate_title = Label(
            text="Qualidade / Bitrate do Áudio:",
            font_size="13sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            size_hint_y=None,
            height=20,
            halign='left'
        )
        self.bitrate_title.bind(size=lambda *x: setattr(self.bitrate_title, 'text_size', (self.bitrate_title.width, None)))
        bitrate_box.add_widget(self.bitrate_title)

        chips_row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=36)
        self.bitrate_buttons = {}
        bitrates = ["320kbps", "256kbps", "192kbps", "128kbps"]

        for b in bitrates:
            is_active = (b == "320kbps")
            bg = Theme.BLUE_ACTION if is_active else Theme.get_input_bg(self.app.is_dark)
            fg = [1, 1, 1, 1] if is_active else Theme.get_text(self.app.is_dark)
            btn = CustomButton(
                text=b,
                font_size="12sp",
                bg_color=bg,
                text_color=fg,
                radius=[18, 18, 18, 18],
                size_hint_x=0.25
            )
            btn.bind(on_release=lambda instance, val=b: self.select_bitrate(val))
            self.bitrate_buttons[b] = btn
            chips_row.add_widget(btn)

        bitrate_box.add_widget(chips_row)
        self.container.add_widget(bitrate_box)

        # 4. Botão de Extração de Áudio
        self.btn_download_audio = CustomButton(
            text="🔵 EXTRAIR E BAIXAR ÁUDIO (MP3)",
            font_size="14sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            size_hint_y=None,
            height=46,
            radius=[8, 8, 8, 8]
        )
        self.btn_download_audio.bind(on_release=lambda x: self.start_audio_download())
        self.container.add_widget(self.btn_download_audio)

        # 5. Painel de Progresso
        self.progress_panel = ProgressPanel(
            is_dark=self.app.is_dark,
            on_cancel=lambda x: self.cancel_download()
        )
        self.container.add_widget(self.progress_panel)

        scroll.add_widget(self.container)
        self.add_widget(scroll)

    def paste_from_clipboard(self, instance):
        text = Clipboard.paste()
        if text:
            self.url_input.text = text.strip()
            self.fetch_audio_info()

    def select_bitrate(self, bitrate):
        self.selected_bitrate = bitrate
        for b, btn in self.bitrate_buttons.items():
            is_active = (b == bitrate)
            bg = Theme.BLUE_ACTION if is_active else Theme.get_input_bg(self.app.is_dark)
            fg = [1, 1, 1, 1] if is_active else Theme.get_text(self.app.is_dark)
            btn.set_color(bg, fg)

    def fetch_audio_info(self):
        url = self.url_input.text.strip()
        if not url:
            self.app.show_message("Aviso", "Insira a URL.")
            return

        self.btn_fetch.text = "⌛..."
        self.progress_panel.set_progress(0, status_text="Buscando áudio...")

        def _fetch():
            try:
                info = self.app.downloader.extract_info(url)
                Clock.schedule_once(lambda dt: self._on_info_fetched(info))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._on_info_error(str(e)))

        threading.Thread(target=_fetch, daemon=True).start()

    def _on_info_fetched(self, info):
        self.btn_fetch.text = "🔍 Buscar"
        self.audio_info = info
        self.preview_card.set_data(
            title=info.get("title", ""),
            thumbnail_url=info.get("thumbnail", ""),
            uploader=info.get("uploader", ""),
            duration=info.get("duration", "00:00"),
            views=info.get("views", "0")
        )
        self.progress_panel.set_progress(0, status_text="Áudio pronto para extração!")

    def _on_info_error(self, err):
        self.btn_fetch.text = "🔍 Buscar"
        self.progress_panel.set_progress(0, status_text="Erro ao buscar.")
        self.app.show_message("Erro", f"Falha ao obter áudio:\n{err}")

    def start_audio_download(self):
        url = self.url_input.text.strip()
        if not url:
            self.app.show_message("Aviso", "Insira a URL.")
            return

        self.btn_download_audio.disabled = True
        self.progress_panel.set_progress(0, status_text=f"Extraindo áudio ({self.selected_bitrate})...")

        def on_progress(percent, speed, eta, downloaded, total):
            Clock.schedule_once(lambda dt: self.progress_panel.set_progress(
                percent=percent,
                speed_str=speed,
                eta_str=eta,
                status_text=f"Baixando áudio... {int(percent)}%"
            ))

        def on_complete(title, filepath, thumbnail, item_type):
            Clock.schedule_once(lambda dt: self._on_download_success(title, filepath, thumbnail))

        def on_error(err):
            Clock.schedule_once(lambda dt: self._on_download_failed(err))

        self.app.downloader.download_single(
            url=url,
            quality=f"mp3_{self.selected_bitrate}",
            on_progress=on_progress,
            on_complete=on_complete,
            on_error=on_error,
            is_audio=True
        )

    def _on_download_success(self, title, filepath, thumbnail):
        self.btn_download_audio.disabled = False
        self.progress_panel.set_progress(100, status_text="✅ Áudio baixado!")
        self.app.history.add_item(
            title=title,
            url=self.url_input.text.strip(),
            file_path=filepath,
            item_type="audio",
            thumbnail=thumbnail or (self.audio_info.get("thumbnail") if self.audio_info else "")
        )
        self.app.show_message("Áudio Salvo! 🎵", f"{title}\n\nSalvo em:\n{filepath}")

    def _on_download_failed(self, err):
        self.btn_download_audio.disabled = False
        self.progress_panel.set_progress(0, status_text="⚠️ Erro")
        self.app.show_message("Aviso", f"Resultado: {err}")

    def cancel_download(self):
        self.app.downloader.cancel()
        self.btn_download_audio.disabled = False
        self.progress_panel.reset()

    def update_theme(self, is_dark):
        self.input_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.url_input.foreground_color = Theme.get_text(is_dark)
        self.btn_paste.set_color(Theme.get_input_bg(is_dark), Theme.get_text(is_dark))
        self.preview_card.update_theme(is_dark)
        self.bitrate_title.color = Theme.get_text(is_dark)
        self.select_bitrate(self.selected_bitrate)
        self.progress_panel.update_theme(is_dark)

