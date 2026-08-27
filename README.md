<div align="center">

  <img src="logo.png" alt="MultDownload Logo" width="120" height="120" style="border-radius: 24px; margin-bottom: 16px;">

  # MultDownload 4.2.0 (Mobile Android & Multiplataforma) 📥
  
  **O aplicativo mobile moderno, rápido e definitivo para download de vídeos, músicas e playlists do YouTube e redes sociais.**

  [![Version](https://img.shields.io/badge/version-4.2.0-blue.svg?style=for-the-badge&logo=android)](https://github.com/JoadsonRocha/MultDownloader---Kivy-Android)
  [![Platform](https://img.shields.io/badge/platform-Android%20%7C%20Windows%20%7C%20Linux-green.svg?style=for-the-badge&logo=android)](https://github.com/JoadsonRocha/MultDownloader---Kivy-Android)
  [![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB.svg?style=for-the-badge&logo=python)](https://www.python.org/)
  [![Kivy / KivyMD](https://img.shields.io/badge/KivyMD-1.2.0-blueviolet.svg?style=for-the-badge&logo=kivy)](https://kivymd.readthedocs.io/)
  [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](LICENSE)
  [![GitHub Actions CI](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg?style=for-the-badge&logo=githubactions)](https://github.com/JoadsonRocha/MultDownloader---Kivy-Android/actions)
  [![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa.svg?style=for-the-badge&logo=githubsponsors)](https://github.com/sponsors/JoadsonRocha)

  <p align="center">
    <a href="#-sobre-o-projeto">Sobre</a> •
    <a href="#-funcionalidades-principais">Funcionalidades</a> •
    <a href="#-tecnologias-e-bibliotecas">Tecnologias</a> •
    <a href="#-estrutura-do-projeto">Arquitetura</a> •
    <a href="#-como-gerar-o-apk-android">Gerar APK</a> •
    <a href="#-como-executar-no-desktop">Como Rodar</a> •
    <a href="#-apoie-o-projeto">Apoie</a> •
    <a href="#-licença">Licença</a>
  </p>

</div>

---

## 📖 Sobre o Projeto

O **MultDownload 4.2.0** é a versão mobile oficial desenvolvida em **Python** com os frameworks **Kivy** e **KivyMD**, trazendo a mesma identidade visual consagrada e alta performance da versão Desktop para dispositivos **Android** e computadores.

Projetado para oferecer uma experiência fluida, moderna e sem anúncios, o aplicativo conta com integração nativa com o **Scoped Storage** do Android, permissões granulares da API 33/34 (Android 13 e 14+), downloads multithread ultra-rápidos com o motor **yt-dlp** e sistema inteligente de notificações de progresso com controle de taxa (*throttling*).

---

## ✨ Funcionalidades Principais

| Recurso | Descrição |
| :--- | :--- |
| 🌐 **Navegador Integrado** | Navegue no YouTube, TikTok, Instagram, Twitter/X e baixe com 1 toque através dos botões de ação rápida (**🔴 Baixar Vídeo** e **🔵 Baixar Áudio**). |
| 📥 **Download Único com Prévia** | Campo de URL com botão inteligente de **Colar**, busca instantânea de **Thumbnail em HD, Título, Duração, Canal e Visualizações**. |
| 🎬 **Seleção Granular de Qualidade** | Suporte a resoluções **1080p, 720p, 480p, 360p** em formato **MP4** com fallbacks automáticos. |
| 🎵 **Extração Dedicada de Áudio (MP3)** | Extraia músicas e faixas de áudio com ajuste de bitrate (**320 kbps Alta Definição, 256 kbps, 192 kbps ou 128 kbps**). |
| 📑 **Download de Playlists em Lote** | Baixe playlists inteiras de forma sequencial com monitoramento de progresso individual por vídeo. |
| 📊 **Métricas de Download em Tempo Real** | Barra de progresso detalhada exibindo **Velocidade (MB/s)**, **Tempo Restante (ETA)**, **Porcentagem** e botão de **Cancelar**. |
| 📜 **Histórico Interativo com Ações** | Lista dos seus downloads com botões rápidos para **▶ Abrir/Reproduzir**, **📤 Compartilhar** (via WhatsApp/outros apps) e **🗑 Excluir**. |
| 🌓 **Tema Claro & Escuro (Dark Mode)** | Alternância dinâmica entre modo claro e escuro no topo do app (☀️/🌙) com persistência automática. |
| 🔔 **Notificações Nativas no Android** | Alertas do sistema operacional a cada 10% e na conclusão do download sem travar o dispositivo. |
| 🛡️ **Compatível com Android 9 até 14+** | Suporte total ao Android Scoped Storage salvando na pasta pública padrão `/Download`. |

---

## 🛠️ Tecnologias e Bibliotecas

- **[Python](https://www.python.org/)** — Linguagem principal do ecossistema.
- **[Kivy](https://kivy.org/)** & **[KivyMD](https://kivymd.readthedocs.io/)** — Framework moderno para desenvolvimento de interfaces ricas baseadas em Material Design.
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — Motor de extração ultra-rápido com suporte a centenas de plataformas de vídeo e áudio.
- **[Plyer](https://github.com/kivy/plyer)** — API Python para acesso a recursos nativos de hardware e notificações no Android.
- **[PyJNIus](https://github.com/kivy/pyjnius)** — Ponte de comunicação direta com a API do Java/Android (Intents, Storage, FileProvider).
- **[Buildozer](https://github.com/kivy/buildozer)** & **[python-for-android](https://github.com/kivy/python-for-android)** — Ferramenta de compilação e empacotamento para Android (`.apk` / `.aab`).

---

## 🏗️ Estrutura do Projeto

```plaintext
MultDownloader---Kivy-Android/
├── assets/
│   ├── icon.png                 # Ícone do aplicativo em alta resolução (512x512)
│   ├── presplash.png            # Tela de carregamento do app (1080x1920)
│   └── logo.png                 # Logo oficial transparente
├── core/
│   ├── __init__.py
│   ├── downloader.py            # Motor yt-dlp assíncrono, métricas e cancelamento
│   ├── history_manager.py       # Persistência e gerenciamento do histórico JSON
│   ├── notifier.py              # Notificações nativas com taxa controlada (throttling)
│   └── platform_helper.py       # Gerenciamento de permissões e storage no Android
├── ui/
│   ├── __init__.py
│   ├── theme.py                 # Paleta de cores oficial (Claro / Escuro)
│   ├── components.py            # Cards arredondados, botões e barras de progresso
│   └── screens/
│       ├── __init__.py
│       ├── browser_screen.py    # Tela de Navegação Web com ações rápidas
│       ├── single_download.py   # Download individual com prévia e qualidades
│       ├── playlist_screen.py   # Download de playlists completas
│       ├── audio_screen.py      # Extração de músicas em MP3 (320kbps a 128kbps)
│       ├── history_screen.py    # Histórico com reprodução e compartilhamento
│       ├── settings_screen.py   # Ajustes de pasta, tema e notificações
│       └── developer_screen.py  # Apresentação do desenvolvedor Joadson Rocha
├── .github/
│   └── workflows/
│       └── build_apk.yml        # CI/CD no GitHub Actions para compilação automática do APK
├── buildozer.spec               # Especificação oficial do Buildozer
├── main.py                      # Ponto de entrada do aplicativo
├── requirements.txt             # Dependências do projeto
├── LICENSE                      # Licença GNU General Public License v3.0 (GPL-3.0)
└── README.md                    # Documentação oficial
```

---

## 📱 Como Gerar o APK para Android

### Opção 1: Compilação Automática na Nuvem (GitHub Actions - Recomendado) ⚡
1. Envie as alterações para o repositório no GitHub:
   ```bash
   git add .
   git commit -m "feat: atualizacoes do app"
   git push origin main
   ```
2. Acesse a aba **[Actions](https://github.com/JoadsonRocha/MultDownloader---Kivy-Android/actions)** no seu repositório.
3. O workflow `Build MultDownload Android APK` será executado automaticamente no ambiente Ubuntu 22.04 LTS.
4. Quando finalizar, vá na seção **Artifacts** no final da página da execução e baixe o arquivo:
   📦 **`MultDownload-4.2.0-Android-APK.zip`**
5. Extraia o `.apk` e instale no seu celular!

---

### Opção 2: Compilação Local com Buildozer (Linux ou WSL2)
```bash
# 1. Instalar dependências de build no Ubuntu/Debian
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev cmake libffi-dev libssl-dev libltdl-dev ccache

# 2. Instalar o Buildozer e Cython
pip install --upgrade buildozer "Cython<3.0" virtualenv

# 3. Compilar o APK em modo Debug
buildozer android debug
```
O arquivo APK gerado estará disponível na pasta `bin/`.

---

## 💻 Como Executar no Desktop (Windows / Linux / macOS)

### Pré-requisitos
- Python 3.10 ou 3.11 instalado.

```bash
# 1. Clonar o repositório
git clone https://github.com/JoadsonRocha/MultDownloader---Kivy-Android.git
cd MultDownloader---Kivy-Android

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Executar o aplicativo
python main.py
```

---

## ❤️ Apoie o Projeto

Se o **MultDownload** facilitou o seu dia a dia, agregou valor ou te ajudou em seus estudos e trabalho, considere apoiar o desenvolvimento contínuo:

- 💖 **[GitHub Sponsors](https://github.com/sponsors/JoadsonRocha)** — Apoie mensalmente ou com uma contribuição única pelo GitHub.
- ☕ **[Página de Apoio Direto](https://joadsonrocha.github.io/apoieme/apoie-me.html)** — Outras formas de apoio e chave PIX.

---

## 📜 Licença

Distribuído sob a licença **GNU General Public License v3.0 (GPL-3.0)**. Consulte o arquivo [LICENSE](LICENSE) para mais informações.

---

<div align="center">
  Desenvolvido com carinho por <b>Joadson Rocha</b> & Equipe MultDownload 🚀
</div>
