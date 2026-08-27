import json
import os
import time

class HistoryManager:
    def __init__(self, storage_path=None):
        if storage_path is None:
            # Salva na pasta do app
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.file_path = os.path.join(base_dir, "download_history.json")
        else:
            self.file_path = os.path.join(storage_path, "download_history.json")
            
        self.history = self._load()

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

