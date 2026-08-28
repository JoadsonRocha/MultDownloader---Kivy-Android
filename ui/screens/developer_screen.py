from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard

class DeveloperScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "developer"

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.container = BoxLayout(
            orientation='vertical',
            spacing=14,
            padding=[16, 16, 16, 20],
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        # Card Principal do Desenvolvedor
        self.card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            orientation='vertical',
            padding=20,
            spacing=12,
            size_hint_y=None,
            height=360
        )

        # Logo
        import os
        logo_path = 'logo.png' if os.path.exists('logo.png') else 'assets/icon.png'
        self.logo_img = Image(
            source=logo_path,
            size_hint=(None, None),
            size=(72, 72),
            pos_hint={'center_x': 0.5},
            fit_mode="contain"
        )
        self.card.add_widget(self.logo_img)

        # Nome do App
        self.app_title = Label(
            text="MultDownload 4.2.0",
            font_size="22sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            size_hint_y=None,
            height=32,
            halign='center'
        )
        self.card.add_widget(self.app_title)

        self.app_sub = Label(
            text="Aplicativo Multiplataforma de Download de Vídeos e Músicas",
            font_size="12sp",
            color=Theme.get_subtext(self.app.is_dark),
            size_hint_y=None,
            height=20,
            halign='center'
        )
        self.card.add_widget(self.app_sub)

        # Divisor visual / Créditos
        self.dev_label = Label(
            text="Desenvolvido por:\n[b][color=2196F3]Joadson Rocha[/color][/b]",
            markup=True,
            font_size="15sp",
            color=Theme.get_text(self.app.is_dark),
            size_hint_y=None,
            height=50,
            halign='center'
        )
        self.card.add_widget(self.dev_label)

        # Detalhes de suporte
        self.features_label = Label(
            text="• Suporte a YouTube, TikTok, Instagram, X/Twitter e mais\n• Extração direta de áudio MP3 em alta definição\n• Download de Playlists completas\n• Compatível com Android 9, 10, 11, 12, 13 e 14+",
            font_size="12sp",
            color=Theme.get_subtext(self.app.is_dark),
            size_hint_y=None,
            height=70,
            halign='center'
        )
        self.card.add_widget(self.features_label)

        # Copyright
        self.copyright_label = Label(
            text="© 2026 Joadson Rocha. Todos os direitos reservados.",
            font_size="11sp",
            color=Theme.get_subtext(self.app.is_dark),
            size_hint_y=None,
            height=24,
            halign='center'
        )
        self.card.add_widget(self.copyright_label)

        self.container.add_widget(self.card)
        scroll.add_widget(self.container)
        self.add_widget(scroll)

    def update_theme(self, is_dark):
        self.card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.app_title.color = Theme.get_text(is_dark)
        self.app_sub.color = Theme.get_subtext(is_dark)
        self.dev_label.color = Theme.get_text(is_dark)
        self.features_label.color = Theme.get_subtext(is_dark)
        self.copyright_label.color = Theme.get_subtext(is_dark)
