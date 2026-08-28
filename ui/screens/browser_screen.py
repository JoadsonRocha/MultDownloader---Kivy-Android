import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Rectangle
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard


# ─────────────────────────────────────────────
# Skeleton Card — placeholder animado
# ─────────────────────────────────────────────
class SkeletonCard(RoundedCard):
    """Card de placeholder com animação de pulso durante o carregamento."""

    def __init__(self, is_dark=False, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', 8)
        kwargs.setdefault('spacing', 6)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 250)
        super().__init__(bg_color=Theme.get_card(is_dark), border_color=Theme.get_border(is_dark), **kwargs)

        self._is_dark = is_dark
        self._anim_event = None

        # Thumb skeleton
        self.thumb_box = BoxLayout(size_hint_y=None, height=135)
        self._thumb_rect_color = None
        self._thumb_rect = None
        self.thumb_box.bind(pos=self._draw_skeleton, size=self._draw_skeleton)
        self.add_widget(self.thumb_box)

        # Linha título skeleton
        self.title_box = BoxLayout(size_hint_y=None, height=18)
        self.title_box.bind(pos=self._draw_skeleton, size=self._draw_skeleton)
        self.add_widget(self.title_box)

        # Linha subtítulo skeleton (mais curta)
        self.sub_box = BoxLayout(size_hint_y=None, height=12)
        self.sub_box.bind(pos=self._draw_skeleton, size=self._draw_skeleton)
        self.add_widget(self.sub_box)

        # Botões skeleton
        btn_row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=36)
        self.btn_box1 = BoxLayout(size_hint_x=0.5)
        self.btn_box1.bind(pos=self._draw_skeleton, size=self._draw_skeleton)
        self.btn_box2 = BoxLayout(size_hint_x=0.5)
        self.btn_box2.bind(pos=self._draw_skeleton, size=self._draw_skeleton)
        btn_row.add_widget(self.btn_box1)
        btn_row.add_widget(self.btn_box2)
        self.add_widget(btn_row)

        self._skeleton_items = [
            (self.thumb_box, 1.0),
            (self.title_box, 0.75),
            (self.sub_box, 0.5),
            (self.btn_box1, 1.0),
            (self.btn_box2, 1.0),
        ]
        self._skeleton_rects = {}

        Clock.schedule_once(self._start_pulse, 0.1)

    def _get_shimmer_color(self, alpha):
        if self._is_dark:
            return (0.25, 0.27, 0.32, alpha)
        return (0.85, 0.87, 0.90, alpha)

    def _draw_skeleton(self, *args):
        for box, width_ratio in self._skeleton_items:
            box.canvas.before.clear()
            with box.canvas.before:
                Color(*self._get_shimmer_color(1.0))
                RoundedRectangle(
                    pos=(box.x, box.y),
                    size=(box.width * width_ratio, box.height),
                    radius=[6, 6, 6, 6]
                )

    def _start_pulse(self, dt):
        self._draw_skeleton()
        self._pulse_in()

    def _pulse_in(self):
        self._anim_event = Clock.schedule_once(lambda dt: self._pulse_out(), 0.7)

    def _pulse_out(self):
        # Alterna entre cor clara e escura para efeito shimmer
        for box, width_ratio in self._skeleton_items:
            box.canvas.before.clear()
            with box.canvas.before:
                Color(*self._get_shimmer_color(0.45))
                RoundedRectangle(
                    pos=(box.x, box.y),
                    size=(box.width * width_ratio, box.height),
                    radius=[6, 6, 6, 6]
                )
        self._anim_event = Clock.schedule_once(lambda dt: self._restore(), 0.7)

    def _restore(self):
        self._draw_skeleton()
        self._anim_event = Clock.schedule_once(lambda dt: self._pulse_out(), 0.7)

    def stop_pulse(self):
        if self._anim_event:
            self._anim_event.cancel()
            self._anim_event = None


# ─────────────────────────────────────────────
# Card de vídeo rico
# ─────────────────────────────────────────────
class YouTubeVideoCard(RoundedCard):
    def __init__(self, video_data, app_instance, is_dark=False, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', 8)
        kwargs.setdefault('spacing', 6)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 258)
        super().__init__(bg_color=Theme.get_card(is_dark), border_color=Theme.get_border(is_dark), **kwargs)

        self.video_data = video_data
        self.app = app_instance
        self.opacity = 0  # começa invisível para animar entrada

        # ── Thumbnail + badge de duração ──────────────────
        thumb_container = FloatLayout(size_hint_y=None, height=138)

        self.thumb = AsyncImage(
            source=video_data.get('thumbnail', ''),
            fit_mode="cover",
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        thumb_container.add_widget(self.thumb)

        # Badge duração (canto inferior direito)
        duration = video_data.get('duration', '')
        if duration and duration != '00:00':
            dur_badge = Label(
                text=f" {duration} ",
                font_size="10sp",
                bold=True,
                color=[1, 1, 1, 1],
                size_hint=(None, None),
                size=(58, 20),
                pos_hint={'right': 0.99, 'y': 0.03},
                halign='center'
            )
            with dur_badge.canvas.before:
                Color(0, 0, 0, 0.72)
                RoundedRectangle(pos=dur_badge.pos, size=dur_badge.size, radius=[4, 4, 4, 4])
            dur_badge.bind(
                pos=lambda w, v: self._update_badge_canvas(w),
                size=lambda w, v: self._update_badge_canvas(w)
            )
            thumb_container.add_widget(dur_badge)

        self.add_widget(thumb_container)

        # ── Info ────────────────────────────────────────
        info_box = BoxLayout(orientation='vertical', spacing=3, size_hint_y=None, height=54)

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

        uploader = video_data.get('uploader', 'YouTube')
        views = video_data.get('views', '0')
        meta_lbl = Label(
            text=f"📺 {uploader}  •  👁 {views}",
            font_size="11sp",
            color=Theme.get_subtext(is_dark),
            halign='left',
            size_hint_y=None,
            height=18
        )
        meta_lbl.bind(size=lambda *x: setattr(meta_lbl, 'text_size', (meta_lbl.width, None)))
        info_box.add_widget(meta_lbl)
        self.add_widget(info_box)

        # ── Botões ──────────────────────────────────────
        btn_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=36)

        btn_vid = CustomButton(
            text="⬇ Vídeo",
            font_size="12sp",
            bg_color=Theme.RED_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[8, 8, 8, 8],
            size_hint_x=0.5
        )
        btn_vid.bind(on_release=lambda x: self.app.switch_to_single_download(
            self.video_data.get('url', ''), auto_fetch=True, is_audio=False))
        btn_box.add_widget(btn_vid)

        btn_aud = CustomButton(
            text="🎵 Áudio",
            font_size="12sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[8, 8, 8, 8],
            size_hint_x=0.5
        )
        btn_aud.bind(on_release=lambda x: self.app.switch_to_single_download(
            self.video_data.get('url', ''), auto_fetch=True, is_audio=True))
        btn_box.add_widget(btn_aud)

        self.add_widget(btn_box)

        # Anima entrada
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.3).start(self), 0.05)

    def _update_badge_canvas(self, widget):
        widget.canvas.before.clear()
        with widget.canvas.before:
            Color(0, 0, 0, 0.72)
            RoundedRectangle(pos=widget.pos, size=widget.size, radius=[4, 4, 4, 4])

    def update_theme(self, is_dark):
        self.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.title_lbl.color = Theme.get_text(is_dark)


# ─────────────────────────────────────────────
# Tela do Navegador
# ─────────────────────────────────────────────
class BrowserScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "browser"
        self.has_loaded_initial = False
        self._skeleton_cards = []

        self.layout = BoxLayout(orientation='vertical', spacing=8, padding=[10, 8, 10, 8])

        # ── Barra de Busca ──────────────────────────────
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
            hint_text="🔍  Pesquisar no YouTube ou colar link...",
            multiline=False,
            font_size="13sp",
            background_normal='',
            background_color=(0, 0, 0, 0),
            foreground_color=Theme.get_text(self.app.is_dark),
            padding=[8, 10, 6, 10]
        )
        self.search_input.bind(on_text_validate=lambda x: self.perform_search(self.search_input.text))
        nav_card.add_widget(self.search_input)

        self.btn_search = CustomButton(
            text="Buscar",
            font_size="12sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            size_hint=(None, 1),
            width=66,
            radius=[8, 8, 8, 8]
        )
        self.btn_search.bind(on_release=lambda x: self.perform_search(self.search_input.text))
        nav_card.add_widget(self.btn_search)
        self.layout.add_widget(nav_card)

        # ── Chips de Categoria ──────────────────────────
        cat_scroll = ScrollView(do_scroll_x=True, do_scroll_y=False, size_hint_y=None, height=34)
        cat_box = BoxLayout(orientation='horizontal', spacing=6, size_hint_x=None, padding=[2, 0, 2, 0])
        cat_box.bind(minimum_width=cat_box.setter('width'))

        self._cat_buttons = []
        categories = [
            ("🔥 Em Alta", "em alta"),
            ("🎵 Músicas", "músicas"),
            ("🎙 Podcasts", "podcasts"),
            ("🎮 Jogos", "jogos"),
            ("📰 Notícias", "notícias"),
            ("⚽ Futebol", "futebol"),
            ("😂 Humor", "humor brasil"),
            ("🍳 Culinária", "culinária"),
        ]
        self._active_cat = None
        for label, query in categories:
            btn = CustomButton(
                text=label,
                font_size="11sp",
                bg_color=Theme.get_input_bg(self.app.is_dark),
                text_color=Theme.get_text(self.app.is_dark),
                radius=[14, 14, 14, 14],
                size_hint=(None, 1),
                width=100
            )
            btn.bind(on_release=lambda inst, q=query, b=btn: self._on_cat_press(q, b))
            cat_box.add_widget(btn)
            self._cat_buttons.append(btn)

        cat_scroll.add_widget(cat_box)
        self.layout.add_widget(cat_scroll)

        # ── Feed de Vídeos ──────────────────────────────
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

    # ── Callbacks ───────────────────────────────────────
    def on_enter(self, *args):
        if not self.has_loaded_initial:
            self.has_loaded_initial = True
            self.perform_search("músicas mais tocadas brasil")

    def _on_cat_press(self, query, btn):
        # Destaca o chip selecionado
        self._active_cat = btn
        for b in self._cat_buttons:
            is_active = (b is btn)
            b.set_color(
                Theme.BLUE_ACTION if is_active else Theme.get_input_bg(self.app.is_dark),
                [1, 1, 1, 1] if is_active else Theme.get_text(self.app.is_dark)
            )
        self.perform_search(query)

    def perform_search(self, query):
        q = query.strip() if query else "músicas mais tocadas brasil"
        # Limpa campo se for a busca inicial padrão
        if q.startswith("músicas mais"):
            self.search_input.text = ""
        else:
            self.search_input.text = q

        self.btn_search.text = "⏳"
        self._show_skeletons()

        def _search_thread():
            try:
                results = self.app.downloader.search_youtube(q, max_results=8)
                Clock.schedule_once(lambda dt: self._display_results(results))
            except Exception as e:
                err_msg = str(e)  # captura antes do lambda — evita NameError no Python 3.11+
                Clock.schedule_once(lambda dt: self._display_error(err_msg))

        threading.Thread(target=_search_thread, daemon=True).start()

    def _show_skeletons(self):
        """Exibe 4 skeleton cards animados enquanto carrega."""
        self._stop_skeletons()
        self.feed_container.clear_widgets()
        self._skeleton_cards = []
        for _ in range(4):
            sk = SkeletonCard(is_dark=self.app.is_dark)
            self.feed_container.add_widget(sk)
            self._skeleton_cards.append(sk)

    def _stop_skeletons(self):
        for sk in self._skeleton_cards:
            sk.stop_pulse()
        self._skeleton_cards = []

    def _display_results(self, results):
        self.btn_search.text = "Buscar"
        self._stop_skeletons()
        self.feed_container.clear_widgets()

        if not results:
            self._show_empty()
            return

        # Adiciona cards com delay escalonado para efeito cascata
        for i, video in enumerate(results):
            card = YouTubeVideoCard(video, self.app, is_dark=self.app.is_dark)
            self.feed_container.add_widget(card)

    def _display_error(self, err):
        self.btn_search.text = "Buscar"
        self._stop_skeletons()
        self.feed_container.clear_widgets()

        # Card de erro estilizado
        err_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=[0.98, 0.35, 0.35, 0.4],
            orientation='vertical',
            padding=20,
            spacing=10,
            size_hint_y=None,
            height=160,
            radius=[12, 12, 12, 12]
        )
        icon_lbl = Label(
            text="⚠️",
            font_size="36sp",
            size_hint_y=None,
            height=50,
            halign='center'
        )
        err_lbl = Label(
            text=f"Não foi possível carregar o YouTube.\nVerifique sua conexão e tente novamente.",
            font_size="12sp",
            color=Theme.get_subtext(self.app.is_dark),
            size_hint_y=None,
            height=48,
            halign='center'
        )
        err_lbl.bind(size=lambda *x: setattr(err_lbl, 'text_size', (err_lbl.width - 20, None)))
        retry_btn = CustomButton(
            text="↻  Tentar Novamente",
            font_size="12sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            size_hint_y=None,
            height=36,
            radius=[8, 8, 8, 8]
        )
        retry_btn.bind(on_release=lambda x: self.perform_search(self.search_input.text or "músicas em alta"))
        err_card.add_widget(icon_lbl)
        err_card.add_widget(err_lbl)
        err_card.add_widget(retry_btn)
        self.feed_container.add_widget(err_card)

    def _show_empty(self):
        empty_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            orientation='vertical',
            padding=20,
            spacing=10,
            size_hint_y=None,
            height=160,
            radius=[12, 12, 12, 12]
        )
        icon_lbl = Label(text="🔍", font_size="36sp", size_hint_y=None, height=50, halign='center')
        msg_lbl = Label(
            text="Nenhum resultado encontrado.\nTente um termo diferente.",
            font_size="13sp",
            color=Theme.get_subtext(self.app.is_dark),
            size_hint_y=None,
            height=48,
            halign='center'
        )
        msg_lbl.bind(size=lambda *x: setattr(msg_lbl, 'text_size', (msg_lbl.width - 20, None)))
        empty_card.add_widget(icon_lbl)
        empty_card.add_widget(msg_lbl)
        self.feed_container.add_widget(empty_card)

    def update_theme(self, is_dark):
        self.nav_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.search_input.foreground_color = Theme.get_text(is_dark)
        # Atualiza chips de categoria
        for btn in self._cat_buttons:
            is_active = (btn is self._active_cat)
            btn.set_color(
                Theme.BLUE_ACTION if is_active else Theme.get_input_bg(is_dark),
                [1, 1, 1, 1] if is_active else Theme.get_text(is_dark)
            )
        # Fix #7: atualiza cards existentes sem nova busca
        for card in list(self.feed_container.children):
            if hasattr(card, 'update_theme'):
                card.update_theme(is_dark)
