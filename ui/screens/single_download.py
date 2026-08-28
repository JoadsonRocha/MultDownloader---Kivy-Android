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

class SingleDownloadScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "single_download"
        self.selected_quality = "720p"
        self.current_video_info = None

        # Scroll principal
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.container = BoxLayout(
            orientation='vertical',
            spacing=12,
            padding=[12, 10, 12, 16],
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        # 1. Campo de Entrada da URL com botões Colar e Buscar
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
            hint_text="Cole o link do vídeo aqui...",
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
            text="Colar",
            font_size="12sp",
            bg_color=Theme.get_input_bg(self.app.is_dark),
            text_color=Theme.get_text(self.app.is_dark),
            size_hint=(None, 1),
            width=58,
            radius=[6, 6, 6, 6]
        )
        self.btn_paste.bind(on_release=self.paste_from_clipboard)
        input_card.add_widget(self.btn_paste)

        # Botão Buscar
        self.btn_fetch = CustomButton(
            text="Buscar",
            font_size="12sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            size_hint=(None, 1),
            width=58,
            radius=[6, 6, 6, 6]
        )
        self.btn_fetch.bind(on_release=lambda x: self.fetch_video_info())
        input_card.add_widget(self.btn_fetch)

        self.container.add_widget(input_card)

        # 2. Card de Prévia do Vídeo
        self.preview_card = VideoPreviewCard(is_dark=self.app.is_dark)
        self.preview_card.opacity = 0.5
        self.container.add_widget(self.preview_card)

        # 3. Seleção de Qualidade (Chips)
        quality_box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None, height=75)
        self.quality_title = Label(
            text="Qualidade Desejada:",
            font_size="13sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            size_hint_y=None,
            height=20,
            halign='left'
        )
        self.quality_title.bind(size=lambda *x: setattr(self.quality_title, 'text_size', (self.quality_title.width, None)))
        quality_box.add_widget(self.quality_title)

        chips_row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=36)
        self.quality_buttons = {}
        qualities = ["1080p", "720p", "480p", "360p", "Áudio"]

        for q in qualities:
            is_active = (q == "720p")
            bg = Theme.BLUE_ACTION if is_active else Theme.get_input_bg(self.app.is_dark)
            fg = [1, 1, 1, 1] if is_active else Theme.get_text(self.app.is_dark)
            btn = CustomButton(
                text=q,
                font_size="12sp",
                bg_color=bg,
                text_color=fg,
                radius=[18, 18, 18, 18],
                size_hint_x=0.2
            )
            btn.bind(on_release=lambda instance, val=q: self.select_quality(val))
            self.quality_buttons[q] = btn
            chips_row.add_widget(btn)

        quality_box.add_widget(chips_row)
        self.container.add_widget(quality_box)

        # 4. Botões de Ação Principais
        action_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=46)

        self.btn_download_video = CustomButton(
            text="Baixar Vídeo",
            font_size="14sp",
            bg_color=Theme.RED_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[8, 8, 8, 8],
            size_hint_x=0.5
        )
        self.btn_download_video.bind(on_release=lambda x: self.start_download(is_audio=False))
        action_row.add_widget(self.btn_download_video)

        self.btn_download_audio = CustomButton(
            text="Baixar Áudio",
            font_size="14sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[8, 8, 8, 8],
            size_hint_x=0.5
        )
        self.btn_download_audio.bind(on_release=lambda x: self.start_download(is_audio=True))
        action_row.add_widget(self.btn_download_audio)

        self.container.add_widget(action_row)

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
            self.fetch_video_info()

    def select_quality(self, quality):
        self.selected_quality = quality
        for q, btn in self.quality_buttons.items():
            is_active = (q == quality)
            bg = Theme.BLUE_ACTION if is_active else Theme.get_input_bg(self.app.is_dark)
            fg = [1, 1, 1, 1] if is_active else Theme.get_text(self.app.is_dark)
            btn.set_color(bg, fg)

    def fetch_video_info(self, url=None):
        target_url = url or self.url_input.text.strip()
        if not target_url:
            self.app.show_message("Aviso", "Por favor, insira ou cole a URL.")
            return

        self.btn_fetch.text = "..."

        def _fetch():
            try:
                info = self.app.downloader.extract_info(target_url)
                Clock.schedule_once(lambda dt: self._on_info_fetched(info))
            except Exception as e:
                err_msg = str(e)  # captura antes do lambda — evita NameError no Python 3.11+
                Clock.schedule_once(lambda dt: self._on_info_error(err_msg))

        threading.Thread(target=_fetch, daemon=True).start()

    def _on_info_fetched(self, info):
        self.btn_fetch.text = "Buscar"
        self.current_video_info = info
        self.preview_card.set_data(
            title=info.get("title", ""),
            thumbnail_url=info.get("thumbnail", ""),
            uploader=info.get("uploader", ""),
            duration=info.get("duration", "00:00"),
            views=info.get("views", "0")
        )

    def _on_info_error(self, err_msg):
        self.btn_fetch.text = "Buscar"
        self.app.show_message("Erro", f"Não foi possível obter dados da URL:\n{err_msg}")

    def start_download(self, is_audio=False):
        url = self.url_input.text.strip()
        if not url:
            self.app.show_message("Aviso", "Insira a URL do vídeo.")
            return

        # Fix #9: áudio usa qualidade mp3_320kbps para ativar o pós-processador FFmpeg
        quality = "mp3_320kbps" if is_audio else self.selected_quality
        status_msg = "Extraindo áudio MP3..." if is_audio else f"Baixando vídeo ({quality})..."
        
        self.btn_download_video.disabled = True
        self.btn_download_audio.disabled = True
        self.progress_panel.show(status_text=status_msg)
        self.progress_panel.set_progress(0, status_text=status_msg)

        def on_progress(percent, speed, eta, downloaded, total):
            Clock.schedule_once(lambda dt: self.progress_panel.set_progress(
                percent=percent,
                speed_str=speed,
                eta_str=eta,
                status_text=f"Baixando... {int(percent)}%"
            ))

        def on_complete(title, filepath, thumbnail, item_type):
            Clock.schedule_once(lambda dt: self._on_download_success(title, filepath, thumbnail, item_type))

        def on_error(err):
            Clock.schedule_once(lambda dt: self._on_download_failed(err))

        self.app.downloader.download_single(
            url=url,
            quality=quality,
            on_progress=on_progress,
            on_complete=on_complete,
            on_error=on_error,
            is_audio=is_audio
        )

    def _on_download_success(self, title, filepath, thumbnail, item_type):
        self.btn_download_video.disabled = False
        self.btn_download_audio.disabled = False
        self.progress_panel.set_progress(100, status_text="Download concluído com sucesso!")
        
        # Salva no histórico
        self.app.history.add_item(
            title=title,
            url=self.url_input.text.strip(),
            file_path=filepath,
            item_type=item_type,
            thumbnail=thumbnail or (self.current_video_info.get("thumbnail") if self.current_video_info else "")
        )
        self.app.show_message("Sucesso", f"Download finalizado:\n{title}\n\nSalvo em:\n{filepath}")

    def _on_download_failed(self, err):
        self.btn_download_video.disabled = False
        self.btn_download_audio.disabled = False
        self.progress_panel.set_progress(0, status_text="Falha no download")
        self.app.show_message("Aviso", f"Resultado: {err}")

    def cancel_download(self):
        self.app.downloader.cancel()
        self.btn_download_video.disabled = False
        self.btn_download_audio.disabled = False
        self.progress_panel.hide()

    def update_theme(self, is_dark):
        self.input_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.url_input.foreground_color = Theme.get_text(is_dark)
        self.btn_paste.set_color(Theme.get_input_bg(is_dark), Theme.get_text(is_dark))
        self.preview_card.update_theme(is_dark)
        self.quality_title.color = Theme.get_text(is_dark)
        self.select_quality(self.selected_quality)
        self.progress_panel.update_theme(is_dark)
