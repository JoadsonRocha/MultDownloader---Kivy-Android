import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard

class YouTubeVideoCard(RoundedCard):
    def __init__(self, video_data, app_instance, is_dark=False, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', 8)
        kwargs.setdefault('spacing', 6)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 250)
        super().__init__(bg_color=Theme.get_card(is_dark), border_color=Theme.get_border(is_dark), **kwargs)

        self.video_data = video_data
        self.app = app_instance

        # 1. Thumbnail com tempo sobreposto
        self.thumb = AsyncImage(
            source=video_data.get('thumbnail', ''),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=None,
            height=135
        )
        self.add_widget(self.thumb)

        # 2. Informações do Vídeo
        info_box = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None, height=52)
        
        self.title_lbl = Label(
            text=video_data.get('title', 'Sem título'),
            font_size="13sp",
            bold=True,
            color=Theme.get_text(is_dark),
            halign='left',
            valign='top',
            shorten=True,
            shorten_from='right',
            size_hint_y=None,
            height=32
        )
        self.title_lbl.bind(size=lambda *x: setattr(self.title_lbl, 'text_size', (self.title_lbl.width, None)))
        info_box.add_widget(self.title_lbl)

        meta_lbl = Label(
            text=f"{video_data.get('uploader', 'YouTube')} • {video_data.get('duration', '00:00')} • {video_data.get('views', '0')} views",
            font_size="11sp",
            color=Theme.get_subtext(is_dark),
            halign='left',
            size_hint_y=None,
            height=18
        )
        meta_lbl.bind(size=lambda *x: setattr(meta_lbl, 'text_size', (meta_lbl.width, None)))
        info_box.add_widget(meta_lbl)
        self.add_widget(info_box)

        # 3. Botões Rápidos: Baixar Vídeo e Baixar Áudio
        btn_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=36)
        
        btn_vid = CustomButton(
            text="Baixar Vídeo",
            font_size="12sp",
            bg_color=Theme.RED_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[6, 6, 6, 6],
            size_hint_x=0.5
        )
        btn_vid.bind(on_release=lambda x: self.app.switch_to_single_download(self.video_data.get('url', ''), auto_fetch=True, is_audio=False))
        btn_box.add_widget(btn_vid)

        btn_aud = CustomButton(
            text="Baixar Áudio",
            font_size="12sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[6, 6, 6, 6],
            size_hint_x=0.5
        )
        btn_aud.bind(on_release=lambda x: self.app.switch_to_single_download(self.video_data.get('url', ''), auto_fetch=True, is_audio=True))
        btn_box.add_widget(btn_aud)

        self.add_widget(btn_box)

class BrowserScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "browser"
        self.has_loaded_initial = False

        self.layout = BoxLayout(orientation='vertical', spacing=8, padding=[10, 8, 10, 8])

        # 1. Barra de Busca / URL
        nav_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            size_hint_y=None,
            height=48,
            padding=[8, 4, 8, 4],
            spacing=6
        )
        self.nav_card = nav_card

        self.search_input = TextInput(
            hint_text="Pesquisar no YouTube ou colar link...",
            multiline=False,
            font_size="13sp",
            background_normal='',
            background_color=(0, 0, 0, 0),
            foreground_color=Theme.get_text(self.app.is_dark),
            padding=[6, 10, 6, 10]
        )
        nav_card.add_widget(self.search_input)

        # Botão Buscar
        self.btn_search = CustomButton(
            text="Buscar",
            font_size="12sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            size_hint=(None, 1),
            width=62,
            radius=[6, 6, 6, 6]
        )
        self.btn_search.bind(on_release=lambda x: self.perform_search(self.search_input.text))
        nav_card.add_widget(self.btn_search)

        self.layout.add_widget(nav_card)

        # 2. Categorias Rápidas do YouTube
        cat_scroll = ScrollView(do_scroll_x=True, do_scroll_y=False, size_hint_y=None, height=36)
        cat_box = BoxLayout(orientation='horizontal', spacing=6, size_hint_x=None)
        cat_box.bind(minimum_width=cat_box.setter('width'))

        categories = ["Em Alta", "Músicas", "Podcasts", "Jogos", "Notícias", "Futebol"]
        for cat in categories:
            btn = CustomButton(
                text=cat,
                font_size="11sp",
                bg_color=Theme.get_input_bg(self.app.is_dark),
                text_color=Theme.get_text(self.app.is_dark),
                radius=[14, 14, 14, 14],
                size_hint=(None, 1),
                width=80
            )
            btn.bind(on_release=lambda inst, c=cat: self.perform_search(c))
            cat_box.add_widget(btn)

        cat_scroll.add_widget(cat_box)
        self.layout.add_widget(cat_scroll)

        # 3. Feed de Vídeos com Scroll
        self.feed_scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.feed_container = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None
        )
        self.feed_container.bind(minimum_height=self.feed_container.setter('height'))
        self.feed_scroll.add_widget(self.feed_container)

        self.layout.add_widget(self.feed_scroll)
        self.add_widget(self.layout)

    def on_enter(self, *args):
        if not self.has_loaded_initial:
            self.has_loaded_initial = True
            self.perform_search("músicas mais tocadas brasil")

    def perform_search(self, query):
        q = query.strip() if query else "músicas mais tocadas brasil"
        self.search_input.text = q if not q.startswith("músicas mais") else ""
        self.btn_search.text = "..."
        
        self.feed_container.clear_widgets()
        loading_lbl = Label(
            text="Carregando vídeos do YouTube...",
            font_size="13sp",
            color=Theme.get_subtext(self.app.is_dark),
            size_hint_y=None,
            height=100
        )
        self.feed_container.add_widget(loading_lbl)

        def _search_thread():
            try:
                results = self.app.downloader.search_youtube(q, max_results=8)
                Clock.schedule_once(lambda dt: self._display_results(results))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._display_error(str(e)))

        threading.Thread(target=_search_thread, daemon=True).start()

    def _display_results(self, results):
        self.btn_search.text = "Buscar"
        self.feed_container.clear_widgets()

        if not results:
            empty_lbl = Label(
                text="Nenhum vídeo encontrado. Tente pesquisar outro termo.",
                font_size="13sp",
                color=Theme.get_subtext(self.app.is_dark),
                size_hint_y=None,
                height=100
            )
            self.feed_container.add_widget(empty_lbl)
            return

        for video in results:
            card = YouTubeVideoCard(video, self.app, is_dark=self.app.is_dark)
            self.feed_container.add_widget(card)

    def _display_error(self, err):
        self.btn_search.text = "Buscar"
        self.feed_container.clear_widgets()
        err_lbl = Label(
            text=f"Erro ao buscar no YouTube:\n{err}",
            font_size="12sp",
            color=Theme.get_subtext(self.app.is_dark),
            size_hint_y=None,
            height=100,
            halign='center'
        )
        self.feed_container.add_widget(err_lbl)

    def update_theme(self, is_dark):
        self.nav_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.search_input.foreground_color = Theme.get_text(is_dark)
        if self.has_loaded_initial:
            self.perform_search(self.search_input.text or "músicas em alta")
