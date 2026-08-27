from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard

class BrowserScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "browser"

        self.layout = BoxLayout(orientation='vertical', spacing=8, padding=[10, 8, 10, 8])

        # 1. Barra de Navegação Web
        nav_card = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            size_hint_y=None,
            height=48,
            padding=[6, 4, 6, 4],
            spacing=4
        )
        self.nav_card = nav_card

        # Botão Voltar
        self.btn_back = CustomButton(
            text="<",
            font_size="15sp",
            bg_color=Theme.get_input_bg(self.app.is_dark),
            text_color=Theme.get_text(self.app.is_dark),
            size_hint=(None, 1),
            width=32,
            radius=[6, 6, 6, 6]
        )
        nav_card.add_widget(self.btn_back)

        # Botão Avançar
        self.btn_forward = CustomButton(
            text=">",
            font_size="15sp",
            bg_color=Theme.get_input_bg(self.app.is_dark),
            text_color=Theme.get_text(self.app.is_dark),
            size_hint=(None, 1),
            width=32,
            radius=[6, 6, 6, 6]
        )
        nav_card.add_widget(self.btn_forward)

        # Botão Home
        self.btn_home = CustomButton(
            text="Home",
            font_size="11sp",
            bg_color=Theme.get_input_bg(self.app.is_dark),
            text_color=Theme.get_text(self.app.is_dark),
            size_hint=(None, 1),
            width=48,
            radius=[6, 6, 6, 6]
        )
        self.btn_home.bind(on_release=lambda x: self.navigate_to("https://m.youtube.com"))
        nav_card.add_widget(self.btn_home)

        # Campo de URL
        self.url_input = TextInput(
            text="https://m.youtube.com",
            multiline=False,
            font_size="12sp",
            background_normal='',
            background_color=(0, 0, 0, 0),
            foreground_color=Theme.get_text(self.app.is_dark),
            padding=[8, 8, 8, 8]
        )
        nav_card.add_widget(self.url_input)

        # Botão Ir
        self.btn_go = CustomButton(
            text="Ir",
            font_size="12sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            size_hint=(None, 1),
            width=42,
            radius=[6, 6, 6, 6]
        )
        self.btn_go.bind(on_release=lambda x: self.navigate_to(self.url_input.text))
        nav_card.add_widget(self.btn_go)

        self.layout.add_widget(nav_card)

        # 2. Barra de Ação Rápida: "Baixar Vídeo" e "Baixar Áudio"
        action_bar = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=44)
        
        self.btn_download_video = CustomButton(
            text="Baixar Vídeo",
            font_size="13sp",
            bg_color=Theme.RED_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[8, 8, 8, 8],
            size_hint_x=0.5
        )
        self.btn_download_video.bind(on_release=self.on_download_video_clicked)
        action_bar.add_widget(self.btn_download_video)

        self.btn_download_audio = CustomButton(
            text="Baixar Áudio",
            font_size="13sp",
            bg_color=Theme.BLUE_ACTION,
            text_color=[1, 1, 1, 1],
            radius=[8, 8, 8, 8],
            size_hint_x=0.5
        )
        self.btn_download_audio.bind(on_release=self.on_download_audio_clicked)
        action_bar.add_widget(self.btn_download_audio)

        self.layout.add_widget(action_bar)

        # 3. Área Central
        self.content_area = RoundedCard(
            bg_color=Theme.get_card(self.app.is_dark),
            border_color=Theme.get_border(self.app.is_dark),
            orientation='vertical',
            padding=16,
            spacing=10
        )
        
        self.info_title = Label(
            text="Navegador MultDownload",
            font_size="17sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            size_hint_y=None,
            height=30
        )
        self.content_area.add_widget(self.info_title)

        self.info_desc = Label(
            text="Navegue no YouTube, TikTok, Instagram ou qualquer site de vídeo.\nQuando encontrar o vídeo desejado, basta clicar nos botões acima:\n\n• [b]Baixar Vídeo[/b] para baixar em MP4\n• [b]Baixar Áudio[/b] para extrair em MP3\n\nOu acesse a aba [b]Download Único[/b] para colar o link diretamente.",
            markup=True,
            font_size="13sp",
            color=Theme.get_subtext(self.app.is_dark),
            halign='center',
            valign='middle'
        )
        self.info_desc.bind(size=lambda *x: setattr(self.info_desc, 'text_size', (self.info_desc.width - 20, None)))
        self.content_area.add_widget(self.info_desc)

        self.layout.add_widget(self.content_area)
        self.add_widget(self.layout)

    def navigate_to(self, url):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self.url_input.text = url
        self.info_title.text = f"URL Carregada"

    def on_download_video_clicked(self, instance):
        url = self.url_input.text.strip()
        if url:
            self.app.switch_to_single_download(url, auto_fetch=True, is_audio=False)

    def on_download_audio_clicked(self, instance):
        url = self.url_input.text.strip()
        if url:
            self.app.switch_to_single_download(url, auto_fetch=True, is_audio=True)

    def update_theme(self, is_dark):
        self.nav_card.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.btn_back.set_color(Theme.get_input_bg(is_dark), Theme.get_text(is_dark))
        self.btn_forward.set_color(Theme.get_input_bg(is_dark), Theme.get_text(is_dark))
        self.btn_home.set_color(Theme.get_input_bg(is_dark), Theme.get_text(is_dark))
        self.url_input.foreground_color = Theme.get_text(is_dark)
        self.content_area.set_bg_color(Theme.get_card(is_dark), Theme.get_border(is_dark))
        self.info_title.color = Theme.get_text(is_dark)
        self.info_desc.color = Theme.get_subtext(is_dark)
