from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage, Image
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.core.clipboard import Clipboard
from ui.theme import Theme

class RoundedCard(BoxLayout):
    def __init__(self, bg_color=None, radius=[12, 12, 12, 12], border_color=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or Theme.LIGHT_CARD
        self.border_color = border_color
        self.radius = radius
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def set_bg_color(self, color, border_color=None):
        self.bg_color = color
        if border_color:
            self.border_color = border_color
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            if self.border_color:
                Color(*self.border_color)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius[0]), width=1.1)

class CustomButton(Button):
    def __init__(self, bg_color=Theme.RED_ACTION, text_color=[1, 1, 1, 1], radius=[8, 8, 8, 8], border_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.radius = radius
        self.color = text_color
        self.bold = True
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def set_color(self, bg_color, text_color=None, border_color=None):
        self.bg_color = bg_color
        if text_color:
            self.text_color = text_color
            self.color = text_color
        if border_color is not None:
            self.border_color = border_color
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            if self.border_color:
                Color(*self.border_color)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius[0]), width=1.1)

class VideoPreviewCard(RoundedCard):
    def __init__(self, is_dark=False, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', 10)
        kwargs.setdefault('spacing', 8)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 240)
        super().__init__(bg_color=Theme.get_card(is_dark), border_color=Theme.get_border(is_dark), **kwargs)

        # Imagem / Thumbnail
        self.thumbnail = AsyncImage(
            source='',
            fit_mode="cover",
            size_hint_y=None,
            height=140
        )
        self.add_widget(self.thumbnail)

        # Informações de texto
        self.info_box = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None, height=75)
        
        self.title_label = Label(
            text="Título do Vídeo",
            font_size="14sp",
            bold=True,
            color=Theme.get_text(is_dark),
            size_hint_y=None,
            height=36,
            text_size=(None, None),
            halign='left',
            valign='middle',
            shorten=True,
            shorten_from='right'
        )
        self.title_label.bind(width=lambda *x: setattr(self.title_label, 'text_size', (self.title_label.width, None)))
        self.info_box.add_widget(self.title_label)

        # Linha com Canal, Duração e Views
        self.meta_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=25)
        
        self.author_label = Label(
            text="Canal",
            font_size="12sp",
            color=Theme.get_subtext(is_dark),
            halign='left',
            size_hint_x=0.5
        )
        self.meta_box.add_widget(self.author_label)

        self.duration_label = Label(
            text="Tempo: 00:00",
            font_size="12sp",
            color=Theme.get_subtext(is_dark),
            size_hint_x=0.25
        )
        self.meta_box.add_widget(self.duration_label)

        self.views_label = Label(
            text="Views: 0",
            font_size="12sp",
            color=Theme.get_subtext(is_dark),
            size_hint_x=0.25
        )
        self.meta_box.add_widget(self.views_label)

        self.info_box.add_widget(self.meta_box)
        self.add_widget(self.info_box)

    def set_data(self, title, thumbnail_url, uploader, duration, views):
        self.title_label.text = title
        if thumbnail_url:
            self.thumbnail.source = thumbnail_url
        self.author_label.text = uploader
        self.duration_label.text = f"Tempo: {duration}"
        self.views_label.text = f"Views: {views}"
        self.opacity = 1

    def update_theme(self, is_dark):
        self.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.title_label.color = Theme.get_text(is_dark)
        self.author_label.color = Theme.get_subtext(is_dark)
        self.duration_label.color = Theme.get_subtext(is_dark)
        self.views_label.color = Theme.get_subtext(is_dark)

class ProgressPanel(RoundedCard):
    def __init__(self, is_dark=False, on_cancel=None, auto_hide=True, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', [0, 0, 0, 0] if auto_hide else 12)
        kwargs.setdefault('spacing', 6)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 0 if auto_hide else 105)
        super().__init__(bg_color=Theme.get_card(is_dark), border_color=Theme.get_border(is_dark), **kwargs)

        self.is_dark = is_dark
        self.on_cancel = on_cancel
        self.is_visible = not auto_hide
        self.opacity = 0 if auto_hide else 1
        self.disabled = auto_hide

        # Linha Superior: Status e Porcentagem
        top_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=24)
        self.status_label = Label(
            text="Pronto para baixar",
            font_size="13sp",
            bold=True,
            color=Theme.get_text(is_dark),
            halign='left',
            size_hint_x=0.7
        )
        self.status_label.bind(size=lambda *x: setattr(self.status_label, 'text_size', (self.status_label.width, None)))
        top_box.add_widget(self.status_label)

        self.percent_label = Label(
            text="0%",
            font_size="13sp",
            bold=True,
            color=Theme.BLUE_ACTION,
            halign='right',
            size_hint_x=0.3
        )
        top_box.add_widget(self.percent_label)
        self.add_widget(top_box)

        # Barra de Progresso
        self.bar = ProgressBar(max=100, value=0, size_hint_y=None, height=14)
        self.add_widget(self.bar)

        # Linha Inferior: Velocidade, ETA e Botão Cancelar
        bottom_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=26, spacing=6)
        self.speed_label = Label(
            text="Velocidade: --",
            font_size="11sp",
            color=Theme.get_subtext(is_dark),
            size_hint_x=0.4
        )
        bottom_box.add_widget(self.speed_label)

        self.eta_label = Label(
            text="Tempo: --",
            font_size="11sp",
            color=Theme.get_subtext(is_dark),
            size_hint_x=0.35
        )
        bottom_box.add_widget(self.eta_label)

        self.cancel_btn = CustomButton(
            text="Cancelar",
            font_size="11sp",
            bg_color=Theme.RED_ACTION,
            size_hint=(None, 1),
            width=75,
            radius=[6, 6, 6, 6]
        )
        if on_cancel:
            self.cancel_btn.bind(on_release=on_cancel)
        bottom_box.add_widget(self.cancel_btn)

        self.add_widget(bottom_box)

    def show(self, status_text=None):
        """Torna o painel de progresso visível ao iniciar download."""
        self.is_visible = True
        self.disabled = False
        self.padding = [12, 10, 12, 10]
        self.height = 105
        self.opacity = 1
        if status_text:
            self.status_label.text = status_text
        self._update_canvas()

    def hide(self):
        """Oculta o painel de progresso."""
        self.is_visible = False
        self.disabled = True
        self.padding = [0, 0, 0, 0]
        self.height = 0
        self.opacity = 0
        self.reset()
        self._update_canvas()

    def set_progress(self, percent, speed_str="", eta_str="", status_text=None):
        if not self.is_visible:
            self.show()
        self.bar.value = percent
        self.percent_label.text = f"{int(percent)}%"
        if speed_str:
            self.speed_label.text = f"Vel: {speed_str}"
        if eta_str:
            self.eta_label.text = f"ETA: {eta_str}"
        if status_text:
            self.status_label.text = status_text

    def reset(self):
        self.bar.value = 0
        self.percent_label.text = "0%"
        self.speed_label.text = "Velocidade: --"
        self.eta_label.text = "Tempo: --"
        self.status_label.text = "Pronto para baixar"

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        if self.is_visible:
            self.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        else:
            self.set_bg_color((0, 0, 0, 0), None)
        self.status_label.color = Theme.get_text(is_dark)
        self.speed_label.color = Theme.get_subtext(is_dark)
        self.eta_label.color = Theme.get_subtext(is_dark)
