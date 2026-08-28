import json
import os
import time

class HistoryManager:
    def __init__(self, storage_path=None):
        if storage_path is None:
            # Fix #8: usa user_data_dir do Kivy (gravável no Android) como prioridade
            data_dir = self._get_data_dir()
            self.file_path = os.path.join(data_dir, "download_history.json")
        else:
            self.file_path = os.path.join(storage_path, "download_history.json")

        self.history = self._load()

    @staticmethod
    def _get_data_dir():
        """Retorna o diretório de dados gravável em qualquer plataforma."""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and hasattr(app, 'user_data_dir') and app.user_data_dir:
                os.makedirs(app.user_data_dir, exist_ok=True)
                return app.user_data_dir
        except Exception:
            pass
        # Fallback: pasta home do usuário (seguro em Desktop e Android com permissão)
        fallback = os.path.join(os.path.expanduser("~"), ".multdownloader")
        os.makedirs(fallback, exist_ok=True)
        return fallback

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[HistoryManager] Erro ao carregar histórico: {e}")
                return []
        return []

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[HistoryManager] Erro ao salvar histórico: {e}")

    def add_item(self, title, url, file_path, item_type="video", thumbnail=None, file_size=None):
        """Adiciona um item ao histórico de downloads."""
        item = {
            "id": str(int(time.time() * 1000)),
            "title": title,
            "url": url,
            "file_path": file_path,
            "item_type": item_type,  # "video" ou "audio"
            "thumbnail": thumbnail or "",
            "file_size": file_size or "",
            "timestamp": time.strftime("%d/%m/%Y %H:%M:%S"),
        }
        # Evita duplicatas consecutivas do mesmo arquivo
        self.history = [h for h in self.history if h.get("file_path") != file_path]
        self.history.insert(0, item)
        # Mantém até 200 itens
        if len(self.history) > 200:
            self.history = self.history[:200]
        self._save()
        return item

    def get_items(self):
        """Retorna todos os itens do histórico."""
        return self.history

    def remove_item(self, item_id):
        """Remove um item do histórico por ID."""
        self.history = [item for item in self.history if item.get("id") != item_id]
        self._save()

    def clear_history(self):
        """Limpa todo o histórico."""
        self.history = []
        self._save()

