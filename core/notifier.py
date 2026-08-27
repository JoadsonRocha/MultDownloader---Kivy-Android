import time
from kivy.utils import platform

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
                print(f"[Notifier] Erro ao enviar notificação: {e}")
        else:
            # Em desktop apenas loga ou usa plyer se disponível
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name="MultDownloader"
                )
            except Exception:
                pass

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
