import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard
from core.platform_helper import PlatformHelper

class SettingsScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "settings"

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.container = BoxLayout(
            orientation='vertical',
            spacing=14,
            padding=[12, 12, 12, 16],
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        # Título
        self.title_label = Label(
            text="⚙️ Configurações",
            font_size="18sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            size_hint_y=None,
            height=30,
            halign='left'
        )
        self.title_label.bind(size=lambda *x: setattr(self.title_label, 'text_size', (self.title_label.width, None)))
        self.container.add_widget(self.title_label)

        # 1. Card Pasta de Destino
        self.dir_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            orientation='vertical',
            padding=12,
            spacing=4,
            size_hint_y=None,
            height=90
        )
        self.dir_title = Label(
            text="Pasta de Download:",
            font_size="13sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            halign='left',
            size_hint_y=None,
            height=20
        )
        self.dir_title.bind(size=lambda *x: setattr(self.dir_title, 'text_size', (self.dir_title.width, None)))
        self.dir_card.add_widget(self.dir_title)

        download_path = PlatformHelper.get_download_directory()
        self.dir_path_label = Label(
            text=download_path,
            font_size="12sp",
            color=Theme.BLUE_ACTION,
            halign='left',
            shorten=True,
            shorten_from='left',
            size_hint_y=None,
            height=24
        )
        self.dir_path_label.bind(size=lambda *x: setattr(self.dir_path_label, 'text_size', (self.dir_path_label.width, None)))
        self.dir_card.add_widget(self.dir_path_label)

        self.container.add_widget(self.dir_card)

        # 2. Card Tema
        self.theme_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            orientation='horizontal',
            padding=12,
            spacing=10,
            size_hint_y=None,
            height=60
        )
        self.theme_label = Label(
            text="Modo Escuro (Dark Mode):",
            font_size="13sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            halign='left'
        )
        self.theme_label.bind(size=lambda *x: setattr(self.theme_label, 'text_size', (self.theme_label.width, None)))
        self.theme_card.add_widget(self.theme_label)

        self.theme_switch = Switch(active=self.app.is_dark, size_hint=(None, 1), width=60)
        self.theme_switch.bind(active=self.on_theme_switch)
        self.theme_card.add_widget(self.theme_switch)
        self.container.add_widget(self.theme_card)

        # 3. Card Notificações
        self.notif_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            orientation='horizontal',
            padding=12,
            spacing=10,
            size_hint_y=None,
            height=60
        )
        self.notif_label = Label(
            text="Notificações de Progresso:",
            font_size="13sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            halign='left'
        )
        self.notif_label.bind(size=lambda *x: setattr(self.notif_label, 'text_size', (self.notif_label.width, None)))
        self.notif_card.add_widget(self.notif_label)

        self.notif_switch = Switch(active=True, size_hint=(None, 1), width=60)
        self.notif_card.add_widget(self.notif_switch)
        self.container.add_widget(self.notif_card)

        scroll.add_widget(self.container)
        self.add_widget(scroll)

    def on_theme_switch(self, instance, value):
        self.app.toggle_theme(value)

    def update_theme(self, is_dark):
        self.title_label.color = Theme.get_text(is_dark)
        self.dir_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.dir_title.color = Theme.get_text(is_dark)
        self.theme_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.theme_label.color = Theme.get_text(is_dark)
        self.notif_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.notif_label.color = Theme.get_text(is_dark)
        self.theme_switch.active = is_dark

