import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard, ProgressPanel

class PlaylistScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "playlist"
        self.playlist_info = None
        self.is_audio_mode = False

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.container = BoxLayout(
            orientation='vertical',
            spacing=12,
            padding=[12, 10, 12, 16],
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        # 1. Campo de URL da Playlist
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
            hint_text="Cole o link da Playlist aqui...",
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

        # Botão Buscar Playlist
        self.btn_fetch = CustomButton(
            text="Buscar",
            font_size="12sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            size_hint=(None, 1),
            width=58,
            radius=[6, 6, 6, 6]
        )
        self.btn_fetch.bind(on_release=lambda x: self.fetch_playlist())
        input_card.add_widget(self.btn_fetch)

        self.container.add_widget(input_card)

        # 2. Card de Resumo da Playlist
        self.info_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            orientation='vertical',
            padding=14,
            spacing=6,
            size_hint_y=None,
            height=100
        )
        self.playlist_title = Label(
            text="Nenhuma playlist carregada",
            font_size="15sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            size_hint_y=None,
            height=26,
            halign='left'
        )
        self.playlist_title.bind(size=lambda *x: setattr(self.playlist_title, 'text_size', (self.playlist_title.width, None)))
        self.info_card.add_widget(self.playlist_title)

        self.playlist_details = Label(
            text="Cole o link da playlist acima para carregar a lista de vídeos.",
            font_size="12sp",
            color=Theme.get_subtext(self.app.is_dark),
            size_hint_y=None,
            height=20,
            halign='left'
        )
        self.playlist_details.bind(size=lambda *x: setattr(self.playlist_details, 'text_size', (self.playlist_details.width, None)))
        self.info_card.add_widget(self.playlist_details)

        self.container.add_widget(self.info_card)

        # 3. Tipo de Download: Vídeo ou Áudio
        mode_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        self.btn_mode_video = CustomButton(
            text="Baixar como Vídeo (MP4)",
            font_size="12sp",
            bg_color=Theme.RED_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[8, 8, 8, 8],
            size_hint_x=0.5
        )
        self.btn_mode_video.bind(on_release=lambda x: self.set_mode(is_audio=False))
        mode_box.add_widget(self.btn_mode_video)

        self.btn_mode_audio = CustomButton(
            text="Baixar como Áudio (MP3)",
            font_size="12sp",
            bg_color=Theme.get_input_bg(self.app.is_dark),
            text_color=Theme.get_text(self.app.is_dark),
            radius=[8, 8, 8, 8],
            size_hint_x=0.5
        )
        self.btn_mode_audio.bind(on_release=lambda x: self.set_mode(is_audio=True))
        mode_box.add_widget(self.btn_mode_audio)

        self.container.add_widget(mode_box)

        # 4. Botão Baixar Playlist Completa
        self.btn_download_all = CustomButton(
            text="BAIXAR PLAYLIST COMPLETA",
            font_size="14sp",
            bg_color=Theme.GREEN_SUCCESS,
            text_color=[1, 1, 1, 1],
            size_hint_y=None,
            height=46,
            radius=[8, 8, 8, 8]
        )
        self.btn_download_all.bind(on_release=lambda x: self.start_playlist_download())
        self.container.add_widget(self.btn_download_all)

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
            self.fetch_playlist()

    def set_mode(self, is_audio):
        self.is_audio_mode = is_audio
        if is_audio:
            self.btn_mode_audio.set_color(Theme.BLUE_ACTION, [1, 1, 1, 1])
            self.btn_mode_video.set_color(Theme.get_input_bg(self.app.is_dark), Theme.get_text(self.app.is_dark))
        else:
            self.btn_mode_video.set_color(Theme.RED_ACTION, [1, 1, 1, 1])
            self.btn_mode_audio.set_color(Theme.get_input_bg(self.app.is_dark), Theme.get_text(self.app.is_dark))

    def fetch_playlist(self):
        url = self.url_input.text.strip()
        if not url:
            self.app.show_message("Aviso", "Insira a URL da playlist.")
            return

        self.btn_fetch.text = "..."
        self.progress_panel.set_progress(0, status_text="Carregando playlist...")

        def _fetch():
            try:
                info = self.app.downloader.extract_info(url)
                Clock.schedule_once(lambda dt: self._on_playlist_fetched(info))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._on_fetch_error(str(e)))

        threading.Thread(target=_fetch, daemon=True).start()

    def _on_playlist_fetched(self, info):
        self.btn_fetch.text = "Buscar"
        self.playlist_info = info
        count = info.get("playlist_count", 0) or len(info.get("entries", []))
        self.playlist_title.text = f"{info.get('title', 'Playlist')}"
        self.playlist_details.text = f"Total de vídeos: {count} • Canal: {info.get('uploader', 'Vários')}"
        self.progress_panel.set_progress(0, status_text="Playlist carregada! Clique em Baixar.")

    def _on_fetch_error(self, err):
        self.btn_fetch.text = "Buscar"
        self.progress_panel.set_progress(0, status_text="Erro ao carregar.")
        self.app.show_message("Erro", f"Falha ao carregar playlist:\n{err}")

    def start_playlist_download(self):
        url = self.url_input.text.strip()
        if not url:
            self.app.show_message("Aviso", "Cole o link da playlist.")
            return

        self.btn_download_all.disabled = True
        self.progress_panel.set_progress(0, status_text="Iniciando download da playlist...")

        def on_item_start(index, total, title):
            Clock.schedule_once(lambda dt: self.progress_panel.set_progress(
                0, status_text=f"Item {index}/{total}: {title[:25]}..."
            ))

        def on_progress(index, total, percent, speed, eta):
            Clock.schedule_once(lambda dt: self.progress_panel.set_progress(
                percent=percent,
                speed_str=speed,
                eta_str=eta,
                status_text=f"Item {index}/{total} ({int(percent)}%)"
            ))

        def on_item_complete(index, total, title, filepath):
            self.app.history.add_item(
                title=title,
                url=url,
                file_path=filepath,
                item_type="audio" if self.is_audio_mode else "video"
            )

        def on_all_complete(completed, total):
            Clock.schedule_once(lambda dt: self._on_playlist_success(completed, total))

        def on_error(err):
            Clock.schedule_once(lambda dt: self._on_playlist_failed(err))

        self.app.downloader.download_playlist(
            url=url,
            quality="audio" if self.is_audio_mode else "720p",
            on_item_start=on_item_start,
            on_progress=on_progress,
            on_item_complete=on_item_complete,
            on_all_complete=on_all_complete,
            on_error=on_error,
            is_audio=self.is_audio_mode
        )

    def _on_playlist_success(self, completed, total):
        self.btn_download_all.disabled = False
        self.progress_panel.set_progress(100, status_text=f"{completed} de {total} itens baixados!")
        self.app.show_message("Sucesso", f"Playlist finalizada!\n{completed} de {total} itens foram salvos com sucesso.")

    def _on_playlist_failed(self, err):
        self.btn_download_all.disabled = False
        self.progress_panel.set_progress(0, status_text="Interrompido")
        self.app.show_message("Aviso", f"Resultado: {err}")

    def cancel_download(self):
        self.app.downloader.cancel()
        self.btn_download_all.disabled = False
        self.progress_panel.reset()

    def update_theme(self, is_dark):
        self.input_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.url_input.foreground_color = Theme.get_text(is_dark)
        self.btn_paste.set_color(Theme.get_input_bg(is_dark), Theme.get_text(is_dark))
        self.info_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.playlist_title.color = Theme.get_text(is_dark)
        self.playlist_details.color = Theme.get_subtext(is_dark)
        self.set_mode(self.is_audio_mode)
        self.progress_panel.update_theme(is_dark)
