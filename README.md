# MultDownload 4.2.0 - Versão Mobile Android

Aplicativo moderno e multiplataforma de download de vídeos e músicas para Android e Desktop, desenvolvido em Python utilizando o framework **Kivy / KivyMD** e o motor **yt-dlp**.

Desenvolvido por **Joadson Rocha © 2026**.

---

## 📱 Funcionalidades

- 🌐 **Navegador Integrado**: Navegue no YouTube, TikTok, Instagram e baixe com 1 clique através dos botões de ação rápida (**🔴 Baixar Vídeo** e **🔵 Baixar Áudio**).
- 📥 **Download Único**: Prévia com Thumbnail, Título, Duração, Canal, Views, seleção de resolução (1080p, 720p, 480p, 360p, Áudio) e métricas em tempo real (velocidade em MB/s, tempo restante e porcentagem).
- 📑 **Download de Playlists**: Baixe playlists completas ou parciais em lote com acompanhamento item a item.
- 🎵 **Extração de Áudio Dedicada**: Baixe músicas em MP3/M4A com controle de bitrate (320kbps, 256kbps, 192kbps, 128kbps).
- 📜 **Histórico de Downloads**: Lista dos seus downloads com opções de Abrir, Compartilhar via WhatsApp/Apps e Excluir.
- ⚙️ **Configurações e Temas**: Alternador de Tema Claro / Escuro (☀️/🌙) e gerenciamento de pasta de destino.
- 🚀 **Compatibilidade Android**: Suporte do Android 9 ao Android 14+ com Scoped Storage e notificações inteligentes.

---

## 🛠️ Estrutura do Projeto

```text
MultDownloader---Kivy-Android/
├── assets/                     # Ícones e splash screen (512x512, presplash)
├── core/
│   ├── downloader.py           # Motor yt-dlp assíncrono e cancelamento
│   ├── history_manager.py      # Persistência de histórico em JSON
│   ├── notifier.py             # Notificações com rate-limiting
│   └── platform_helper.py      # Permissões Android e Scoped Storage
├── ui/
│   ├── theme.py                # Paleta de cores oficial MultDownload
│   ├── components.py           # Cards arredondados e botões estilizados
│   └── screens/
│       ├── browser_screen.py   # Tela de Navegação Web
│       ├── single_download.py  # Tela de Download Único
│       ├── playlist_screen.py  # Tela de Playlists
│       ├── audio_screen.py     # Tela de Extração de Áudio
│       ├── history_screen.py   # Tela de Histórico
│       ├── settings_screen.py  # Tela de Configurações
│       └── developer_screen.py # Tela do Desenvolvedor
├── .github/workflows/
│   └── build_apk.yml           # CI/CD para compilação automática do APK
├── buildozer.spec              # Configuração oficial do Buildozer
├── main.py                     # Inicialização do aplicativo
└── requirements.txt            # Dependências Python
```

---

## 📦 Como Compilar o APK para Android

### Opção 1: Automático na Nuvem (GitHub Actions - Recomendado)
1. Faça o `git push` deste repositório para o GitHub:
   ```bash
   git add .
   git commit -m "feat: Versão Mobile MultDownload 4.2.0"
   git push origin main
   ```
2. Acesse a aba **Actions** no seu repositório no GitHub.
3. O workflow `Build MultDownload Android APK` será executado automaticamente.
4. Quando finalizar, baixe o arquivo `.apk` pronto na seção **Artifacts** e instale no seu celular!

### Opção 2: Localmente via Buildozer (Linux ou WSL2)
```bash
pip install buildozer cython virtualenv
buildozer android debug
```
O APK será gerado na pasta `bin/`.

---

## 💻 Execução no Desktop

```bash
pip install -r requirements.txt
python main.py
```
