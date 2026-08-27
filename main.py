import os
import sys

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import platform

# Define o tamanho padrão da janela no Desktop para simular um celular perfeitamente
if platform != 'android':
    Window.size = (420, 760)

from core.platform_helper import PlatformHelper
from core.downloader import DownloaderEngine
from core.history_manager import HistoryManager
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard
from ui.screens.browser_screen import BrowserScreen
from ui.screens.single_download import SingleDownloadScreen
from ui.screens.playlist_screen import PlaylistScreen
from ui.screens.audio_screen import AudioScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.developer_screen import DeveloperScreen

class MultDownloadApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "MultDownload 4.2.0"
        self.icon = "logo.png" if os.path.exists("logo.png") else "logo.ico"
        self.is_dark = False

        # Instâncias do Core
        self.downloader = DownloaderEngine()
        self.history = HistoryManager()

        # Drawer State
        self.drawer_open = False

    def build(self):
        # Permissões Android
        PlatformHelper.request_android_permissions()

        # Configurações de Janela
        Window.clearcolor = Theme.get_bg(self.is_dark)

        # Layout Raiz
        self.root_layout = FloatLayout()

        # Layout Principal (Conteúdo Vertical)
        self.main_box = BoxLayout(orientation='vertical', spacing=0)

        # 1. Top Bar / Cabeçalho
        self.top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=54,
            padding=[10, 6, 10, 6],
            spacing=8
        )
        self._update_top_bar_canvas()
        self.top_bar.bind(pos=self._update_top_bar_canvas, size=self._update_top_bar_canvas)

        # Botão Menu Hambúrguer (≡)
        self.btn_menu = CustomButton(
            text="Menu",
            font_size="12sp",
            bg_color=Theme.get_input_bg(self.is_dark),
            text_color=Theme.get_text(self.is_dark),
            size_hint=(None, 1),
            width=54,
            radius=[8, 8, 8, 8]
        )
        self.btn_menu.bind(on_release=lambda x: self.toggle_drawer())
        self.top_bar.add_widget(self.btn_menu)

        # Logo Ícone
        logo_path = "logo.png" if os.path.exists("logo.png") else "logo.ico"
        self.logo_img = Image(
            source=logo_path,
            size_hint=(None, 1),
            width=36,
            allow_stretch=True
        )
        self.top_bar.add_widget(self.logo_img)

        # Título do App
        self.title_label = Label(
            text="[b][color=2196F3]Mult[/color][color=FA5858]Download[/color][/b] [size=11sp]4.2.0[/size]",
            markup=True,
            font_size="15sp",
            halign='left',
            valign='middle',
            size_hint_x=0.6
        )
        self.title_label.bind(size=lambda *x: setattr(self.title_label, 'text_size', (self.title_label.width, None)))
        self.top_bar.add_widget(self.title_label)

        # Botão Tema (Claro / Escuro)
        self.btn_theme = CustomButton(
            text="Tema" if not self.is_dark else "Escuro",
            font_size="11sp",
            bg_color=Theme.get_input_bg(self.is_dark),
            text_color=Theme.get_text(self.is_dark),
            size_hint=(None, 1),
            width=56,
            radius=[8, 8, 8, 8]
        )
        self.btn_theme.bind(on_release=lambda x: self.toggle_theme())
        self.top_bar.add_widget(self.btn_theme)

        self.main_box.add_widget(self.top_bar)

        # 2. Screen Manager (Telas)
        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))
        
        self.screen_browser = BrowserScreen(self)
        self.screen_single = SingleDownloadScreen(self)
        self.screen_playlist = PlaylistScreen(self)
        self.screen_audio = AudioScreen(self)
        self.screen_history = HistoryScreen(self)
        self.screen_settings = SettingsScreen(self)
        self.screen_developer = DeveloperScreen(self)

        self.sm.add_widget(self.screen_browser)
        self.sm.add_widget(self.screen_single)
        self.sm.add_widget(self.screen_playlist)
        self.sm.add_widget(self.screen_audio)
        self.sm.add_widget(self.screen_history)
        self.sm.add_widget(self.screen_settings)
        self.sm.add_widget(self.screen_developer)

        self.sm.current = "browser"
        self.main_box.add_widget(self.sm)

        # 3. Bottom Bar / Abas Rápidas
        self.bottom_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            padding=[4, 4, 4, 4],
            spacing=4
        )
        self._update_bottom_bar_canvas()
        self.bottom_bar.bind(pos=self._update_bottom_bar_canvas, size=self._update_bottom_bar_canvas)

        self.bottom_nav_buttons = {}
        tabs = [
            ("browser", "Navegar"),
            ("single_download", "Único"),
            ("playlist", "Playlist"),
            ("audio", "Áudio"),
            ("history", "Histórico")
        ]

        for screen_name, label in tabs:
            is_active = (screen_name == "browser")
            bg = Theme.BLUE_ACTION if is_active else [0, 0, 0, 0]
            fg = [1, 1, 1, 1] if is_active else Theme.get_subtext(self.is_dark)

            btn = CustomButton(
                text=label,
                font_size="11sp",
                bg_color=bg,
                text_color=fg,
                radius=[8, 8, 8, 8],
                size_hint_x=0.2
            )
            btn.bind(on_release=lambda inst, s=screen_name: self.switch_screen(s))
            self.bottom_nav_buttons[screen_name] = btn
            self.bottom_bar.add_widget(btn)

        self.main_box.add_widget(self.bottom_bar)
        self.root_layout.add_widget(self.main_box)

        # 4. Navigation Drawer Overlay (Menu Lateral)
        self._build_drawer()

        return self.root_layout

    def _update_top_bar_canvas(self, *args):
        self.top_bar.canvas.before.clear()
        with self.top_bar.canvas.before:
            Color(*Theme.get_card(self.is_dark))
            Rectangle(pos=self.top_bar.pos, size=self.top_bar.size)
            Color(*Theme.get_border(self.is_dark))
            Rectangle(pos=(self.top_bar.x, self.top_bar.y), size=(self.top_bar.width, 1))

    def _update_bottom_bar_canvas(self, *args):
        self.bottom_bar.canvas.before.clear()
        with self.bottom_bar.canvas.before:
            Color(*Theme.get_card(self.is_dark))
            Rectangle(pos=self.bottom_bar.pos, size=self.bottom_bar.size)
            Color(*Theme.get_border(self.is_dark))
            Rectangle(pos=(self.bottom_bar.x, self.bottom_bar.top - 1), size=(self.bottom_bar.width, 1))

    def _build_drawer(self):
        """Constrói o menu lateral com todas as opções da imagem do Desktop."""
        self.drawer_overlay = FloatLayout(size_hint=(1, 1), pos_hint={'x': -1, 'y': 0})
        
        # Fundo semi-transparente para fechar ao tocar fora
        self.drawer_dim = Button(
            size_hint=(1, 1),
            background_color=(0, 0, 0, 0.4),
            background_normal=''
        )
        self.drawer_dim.bind(on_release=lambda x: self.toggle_drawer(False))
        self.drawer_overlay.add_widget(self.drawer_dim)

        # Painel do Menu Lateral
        self.drawer_panel = RoundedCard(
            bg_color=Theme.get_card(self.is_dark),
            border_color=Theme.get_border(self.is_dark),
            orientation='vertical',
            size_hint=(0.80, 1),
            pos_hint={'x': 0, 'y': 0},
            padding=[12, 16, 12, 16],
            spacing=8,
            radius=[0, 16, 16, 0]
        )

        # Cabeçalho do Drawer
        drawer_header = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        logo_path = "logo.png" if os.path.exists("logo.png") else "logo.ico"
        drawer_logo = Image(source=logo_path, size_hint=(None, 1), width=40)
        drawer_header.add_widget(drawer_logo)

        drawer_title = Label(
            text="[b][color=2196F3]Mult[/color][color=FA5858]Download[/color][/b]\n[size=11sp]Versão 4.2.0 Mobile[/size]",
            markup=True,
            font_size="15sp",
            halign='left',
            valign='middle'
        )
        drawer_title.bind(size=lambda *x: setattr(drawer_title, 'text_size', (drawer_title.width, None)))
        drawer_header.add_widget(drawer_title)
        self.drawer_panel.add_widget(drawer_header)

        # Linha divisória
        div = BoxLayout(size_hint_y=None, height=1)
        with div.canvas:
            Color(*Theme.get_border(self.is_dark))
            Rectangle(pos=div.pos, size=div.size)
        self.drawer_panel.add_widget(div)

        # Itens do Menu (Idênticos ao Desktop)
        menu_items = [
            ("browser", "Navegador YouTube"),
            ("single_download", "Download Único"),
            ("playlist", "Baixar Playlist"),
            ("audio", "Baixar Áudio"),
            ("history", "Histórico de Downloads"),
            ("settings", "Configurações"),
            ("developer", "Desenvolvedor")
        ]

        self.drawer_buttons = {}
        for screen_name, title in menu_items:
            is_active = (screen_name == "browser")
            bg = Theme.RED_ACTION if is_active else [0, 0, 0, 0]
            fg = [1, 1, 1, 1] if is_active else Theme.get_text(self.is_dark)

            btn = CustomButton(
                text=title,
                font_size="13sp",
                bg_color=bg,
                text_color=fg,
                size_hint_y=None,
                height=44,
                radius=[8, 8, 8, 8]
            )
            btn.bind(on_release=lambda inst, s=screen_name: self._on_drawer_item_click(s))
            self.drawer_buttons[screen_name] = btn
            self.drawer_panel.add_widget(btn)

        # Espaçador
        self.drawer_panel.add_widget(Label())

        # Rodapé do Drawer
        drawer_footer = Label(
            text="By Joadson Rocha © 2026",
            font_size="11sp",
            color=Theme.get_subtext(self.is_dark),
            size_hint_y=None,
            height=24,
            halign='center'
        )
        self.drawer_panel.add_widget(drawer_footer)
        self.drawer_overlay.add_widget(self.drawer_panel)

        # O drawer_overlay NÃO é adicionado no root_layout inicialmente para não bloquear cliques

    def toggle_drawer(self, force_state=None):
        if force_state is not None:
            self.drawer_open = force_state
        else:
            self.drawer_open = not self.drawer_open

        if self.drawer_open:
            if self.drawer_overlay not in self.root_layout.children:
                self.root_layout.add_widget(self.drawer_overlay)
        else:
            if self.drawer_overlay in self.root_layout.children:
                self.root_layout.remove_widget(self.drawer_overlay)

    def _on_drawer_item_click(self, screen_name):
        self.toggle_drawer(False)
        self.switch_screen(screen_name)

    def switch_screen(self, screen_name):
        self.sm.current = screen_name
        
        # Atualiza botões da barra inferior
        for name, btn in self.bottom_nav_buttons.items():
            is_active = (name == screen_name)
            bg = Theme.BLUE_ACTION if is_active else [0, 0, 0, 0]
            fg = [1, 1, 1, 1] if is_active else Theme.get_subtext(self.is_dark)
            btn.set_color(bg, fg)

        # Atualiza botões do Drawer
        for name, btn in self.drawer_buttons.items():
            is_active = (name == screen_name)
            bg = Theme.RED_ACTION if is_active else [0, 0, 0, 0]
            fg = [1, 1, 1, 1] if is_active else Theme.get_text(self.is_dark)
            btn.set_color(bg, fg)

    def switch_to_single_download(self, url, auto_fetch=True, is_audio=False):
        """Transfere uma URL do Navegador diretamente para a tela de Download."""
        if is_audio:
            self.switch_screen("audio")
            self.screen_audio.url_input.text = url
            if auto_fetch:
                self.screen_audio.fetch_audio_info()
        else:
            self.switch_screen("single_download")
            self.screen_single.url_input.text = url
            if auto_fetch:
                self.screen_single.fetch_video_info(url)

    def toggle_theme(self, is_dark_val=None):
        if is_dark_val is not None:
            self.is_dark = is_dark_val
        else:
            self.is_dark = not self.is_dark

        Window.clearcolor = Theme.get_bg(self.is_dark)
        self.btn_theme.text = "Tema" if not self.is_dark else "Escuro"
        self.btn_theme.set_color(Theme.get_input_bg(self.is_dark), Theme.get_text(self.is_dark))
        self.btn_menu.set_color(Theme.get_input_bg(self.is_dark), Theme.get_text(self.is_dark))

        self._update_top_bar_canvas()
        self._update_bottom_bar_canvas()

        # Atualiza telas
        self.screen_browser.update_theme(self.is_dark)
        self.screen_single.update_theme(self.is_dark)
        self.screen_playlist.update_theme(self.is_dark)
        self.screen_audio.update_theme(self.is_dark)
        self.screen_history.update_theme(self.is_dark)
        self.screen_settings.update_theme(self.is_dark)
        self.screen_developer.update_theme(self.is_dark)

        # Atualiza drawer
        self.drawer_panel.set_bg_color(Theme.get_card(self.is_dark), Theme.get_border(self.is_dark))
        self.switch_screen(self.sm.current)

    def show_message(self, title, message):
        """Exibe um diálogo modal moderno e arredondado compatível com o tema."""
        def _show(dt):
            modal = ModalView(
                size_hint=(0.85, None),
                height=220,
                auto_dismiss=True,
                background_color=(0, 0, 0, 0.5)
            )
            card = RoundedCard(
                bg_color=Theme.get_card(self.is_dark),
                border_color=Theme.get_border(self.is_dark),
                orientation='vertical',
                padding=16,
                spacing=10,
                radius=[16, 16, 16, 16]
            )
            
            title_lbl = Label(
                text=f"[b]{title}[/b]",
                markup=True,
                font_size="16sp",
                color=Theme.get_text(self.is_dark),
                size_hint_y=None,
                height=26,
                halign='center'
            )
            card.add_widget(title_lbl)

            msg_lbl = Label(
                text=message,
                font_size="13sp",
                color=Theme.get_subtext(self.is_dark),
                halign='center',
                valign='middle'
            )
            msg_lbl.bind(size=lambda *x: setattr(msg_lbl, 'text_size', (msg_lbl.width - 20, None)))
            card.add_widget(msg_lbl)

            btn_ok = CustomButton(
                text="OK",
                font_size="13sp",
                bg_color=Theme.BLUE_ACTION,
                size_hint_y=None,
                height=40,
                radius=[8, 8, 8, 8]
            )
            btn_ok.bind(on_release=lambda x: modal.dismiss())
            card.add_widget(btn_ok)

            modal.add_widget(card)
            modal.open()

        Clock.schedule_once(_show)

if __name__ == '__main__':
    MultDownloadApp().run()