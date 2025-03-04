from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy.uix.image import Image  # Usando Image do Kivy
from kivy.properties import BooleanProperty
from kivymd.uix.button import MDRaisedButton  # Usando botão do KivyMD
from kivymd.uix.menu import MDDropdownMenu  # Usando Menu do KivyMD
from kivymd.theming import ThemeManager  # Para gerenciar o tema
from plyer import notification  # Para notificações no Android
import threading
import os
from yt_dlp import YoutubeDL
import re

# Verifica se está no Android e solicita permissões
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

    # Configura o aplicativo para abrir em tela cheia
    from android import android_fullscreen
    android_fullscreen.enable_fullscreen()

class MultDownloaderApp(MDApp):
    dark_mode = BooleanProperty(False)  # Propriedade para alternar entre temas

    def build(self):
        print("Iniciando a aplicação...")
        self.title = "MultDownloader"
        self.icon = "logo.ico"  # Ícone personalizado da aplicação
        Window.clearcolor = (1, 1, 1, 1)  # Fundo branco (tema claro padrão)

        # Layout principal
        self.layout = FloatLayout()

        # Adiciona a imagem de fundo
        background = Image(
            source='background.jpg',  # Nome da imagem de fundo
            allow_stretch=True,  # Permite que a imagem estique para cobrir a tela
            keep_ratio=False,  # Não mantém a proporção da imagem
            size_hint=(1, 1)  # Cobre toda a tela
        )
        self.layout.add_widget(background)

        # Campo de entrada da URL
        self.url_input = TextInput(
            hint_text='Cole a URL do vídeo',
            size_hint=(0.8, None),
            height=40,
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            background_color=(0.9, 0.9, 0.9, 1),
            foreground_color=(0, 0, 0, 1),
            background_normal='',
            padding=[10, 10]
        )
        self.layout.add_widget(self.url_input)

        # Botão de download
        self.download_button = MDRaisedButton(
            text='Baixar',
            size_hint=(0.5, None),
            height=40,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            md_bg_color=(0.2, 0.6, 0.2, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        self.download_button.bind(on_press=self.iniciar_download)
        self.layout.add_widget(self.download_button)

        # Imagem de qualidade no canto superior direito
        self.qualidade_img = Image(
            source='config.png',  # Ícone de qualidade
            size_hint=(None, None),
            size=(40, 40),
            pos_hint={'right': 0.98, 'top': 0.98}
        )
        self.qualidade_img.bind(on_touch_down=self.mostrar_opcoes_qualidade)  # Abre o menu ao clicar
        self.layout.add_widget(self.qualidade_img)

        # Barra de progresso
        self.progress_bar = ProgressBar(
            max=100,
            size_hint=(0.8, None),
            height=20,
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
        )
        self.layout.add_widget(self.progress_bar)

        # Label de status
        self.status_label = Label(
            text="",
            size_hint=(0.8, None),
            height=30,
            pos_hint={'center_x': 0.5, 'center_y': 0.35},
            color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.status_label)

        # Rodapé
        rodape = Label(
            text="By Joadson Rocha © 2025",
            size_hint=(1, None),
            height=30,
            pos_hint={'center_x': 0.5, 'y': 0.02},
            color=(0, 0, 0, 1))
        self.layout.add_widget(rodape)

        # Botão para alternar tema
        self.tema_button = MDRaisedButton(
            text='Tema Escuro',
            size_hint=(None, None),
            size=(100, 40),
            pos_hint={'x': 0.02, 'top': 0.98},
            md_bg_color=(0.2, 0.2, 0.2, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        self.tema_button.bind(on_press=self.alternar_tema)
        self.layout.add_widget(self.tema_button)

        # Menu de qualidade (usando KivyMD)
        self.menu_qualidade = MDDropdownMenu(
            caller=self.qualidade_img,
            items=[
                {"text": "Padrão", "on_release": lambda: self.selecionar_qualidade("Padrão")},
                {"text": "1080p", "on_release": lambda: self.selecionar_qualidade("1080p")},
                {"text": "720p", "on_release": lambda: self.selecionar_qualidade("720p")},
                {"text": "480p", "on_release": lambda: self.selecionar_qualidade("480p")},
                {"text": "360p", "on_release": lambda: self.selecionar_qualidade("360p")},
                {"text": "Somente Áudio", "on_release": lambda: self.selecionar_qualidade("Somente Áudio")},
            ],
            width_mult=4,
        )

        print("Interface montada.")
        return self.layout

    def alternar_tema(self, instance):
        """Alterna entre tema claro e escuro."""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.theme_cls.theme_style = "Dark"  # Tema escuro
            self.tema_button.text = 'Tema Claro'
        else:
            self.theme_cls.theme_style = "Light"  # Tema claro
            self.tema_button.text = 'Tema Escuro'

    def validar_url(self, url):
        padrao = r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+'
        return re.match(padrao, url) is not None

    def mostrar_opcoes_qualidade(self, instance, touch):
        """Abre o menu de qualidade ao clicar na imagem."""
        if instance.collide_point(*touch.pos):  # Verifica se o clique foi na imagem
            if not self.menu_qualidade.parent:  # Verifica se o menu já está aberto
                self.menu_qualidade.open()

    def selecionar_qualidade(self, qualidade):
        self.qualidade_selecionada = qualidade.lower()
        print(f"Qualidade selecionada: {self.qualidade_selecionada}")
        self.menu_qualidade.dismiss()  # Fecha o menu após a seleção

    def iniciar_download(self, instance):
        print("Iniciando download...")
        url = self.url_input.text
        qualidade = getattr(self, 'qualidade_selecionada', 'padrão')

        if not url or not self.validar_url(url):
            self.mostrar_popup("Erro", "Por favor, insira uma URL válida do YouTube.")
            return

        self.download_button.disabled = True
        self.download_button.text = "Baixando..."
        self.download_button.md_bg_color = (0.5, 0.5, 0.5, 1)

        # Inicia o download em uma thread separada
        threading.Thread(target=self.executar_download, args=(url, qualidade), daemon=True).start()

    def executar_download(self, url, qualidade):
        print("Iniciando o download...")
        try:
            local_salvar = "/storage/emulated/0/Download/" if platform == 'android' else os.path.expanduser("~/Downloads")
            print(f"Salvando em: {local_salvar}")

            qualidade_map = {
                "padrão": "best",
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
                "somente áudio": "bestaudio"
            }
            formato = qualidade_map.get(qualidade, "best")

            ydl_opts = {
                'format': formato,
                'outtmpl': os.path.join(local_salvar, '%(title)s.%(ext)s'),
                'progress_hooks': [self.atualizar_progresso],
                'noplaylist': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.mostrar_popup("Sucesso", f"Download concluído: {info['title']}")
                # Notificação no Android
                if platform == 'android':
                    notification.notify(
                        title="Download Concluído",
                        message=f"{info['title']} foi baixado com sucesso!",
                        app_name="MultDownloader"
                    )
        except Exception as e:
            Clock.schedule_once(lambda dt: self.mostrar_popup("Erro", f"Ocorreu um erro: {str(e)}"))
        finally:
            Clock.schedule_once(lambda dt: self.reabilitar_botao_download())

    def atualizar_progresso(self, d):
        if d['status'] == 'downloading':
            # Remove caracteres de escape ANSI e converte para float
            percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).strip('%')
            percent = float(percent_str)
            Clock.schedule_once(lambda dt: self.atualizar_ui_progresso(percent))
            # Notificação de progresso no Android
            if platform == 'android':
                notification.notify(
                    title="Download em Progresso",
                    message=f"Progresso: {int(percent)}%",
                    app_name="MultDownloader"
                )

    def atualizar_ui_progresso(self, percent):
        self.progress_bar.value = percent
        self.status_label.text = f"Baixando... {int(percent)}%"

    def reabilitar_botao_download(self):
        self.download_button.disabled = False
        self.download_button.text = "Baixar"
        self.download_button.md_bg_color = (0.2, 0.6, 0.2, 1)
        self.progress_bar.value = 0
        self.status_label.text = ""

    def mostrar_popup(self, titulo, mensagem):
        def _mostrar_popup(dt):
            # Define a cor de fundo do Popup com base no tema
            background_color = self.theme_cls.primary_color if self.dark_mode else (1, 1, 1, 1)
            
            # Cria o Popup
            popup = Popup(
                title=titulo,
                content=Label(text=mensagem, color=(0, 0, 0, 1)),
                size_hint=(0.8, 0.4),
                background_color=background_color,  # Usando background_color em vez de background
            )
            popup.open()
        Clock.schedule_once(_mostrar_popup)

if __name__ == '__main__':
    print("Executando o aplicativo...")
    MultDownloaderApp().run()