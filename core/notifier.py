import time
import os
import sys

try:
    from kivy.utils import platform
except ImportError:
    if sys.platform.startswith('win'):
        platform = 'win'
    elif sys.platform.startswith('darwin'):
        platform = 'macosx'
    elif 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_ROOT' in os.environ:
        platform = 'android'
    else:
        platform = 'linux'


class Notifier:
    def __init__(self):
        self._last_notify_time = 0
        self._notify_interval = 2.0  # Mínimo de 2 segundos entre notificações de progresso
        self._last_percent = -1

    def notify(self, title, message, force=False):
        """Envia notificação nativa no Android com proteção de taxa (throttling)."""
        now = time.time()
        if not force and (now - self._last_notify_time < self._notify_interval):
            return

        self._last_notify_time = now

        if platform == 'android':
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name="MultDownloader"
                )
            except Exception as e:
                print(f"[Notifier] Erro ao enviar notificação Android: {e}")
        else:
            # Em Desktop apenas loga no console — plyer/balloontip é instável no Windows sem bandeja
            print(f"[Notifier] {title}: {message}")

    def notify_progress(self, percent, filename="Vídeo"):
        """Notifica o progresso a cada 10% para não sobrecarregar o Android."""
        int_percent = int(percent)
        if int_percent != self._last_percent and int_percent % 10 == 0:
            self._last_percent = int_percent
            self.notify(
                title="MultDownloader - Baixando",
                message=f"{filename}: {int_percent}% concluído",
                force=True
            )

    def notify_success(self, title_text):
        self.notify(
            title="Download Concluído! 🎉",
            message=f"{title_text} baixado com sucesso!",
            force=True
        )

    def notify_error(self, message):
        self.notify(
            title="Erro no Download ⚠️",
            message=str(message),
            force=True
        )
