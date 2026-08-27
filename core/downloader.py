import os
import re
import threading
from yt_dlp import YoutubeDL
from core.platform_helper import PlatformHelper
from core.notifier import Notifier

class DownloadCancelledException(Exception):
    pass

class DownloaderEngine:
    def __init__(self):
        self.notifier = Notifier()
        self._is_cancelled = False
        self._current_ydl = None

    def cancel(self):
        """Cancela o download em andamento."""
        self._is_cancelled = True

    def reset_cancel(self):
        self._is_cancelled = False

    def format_duration(self, seconds):
        if not seconds:
            return "00:00"
        seconds = int(seconds)
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def format_views(self, count):
        if not count:
            return "0"
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        if count >= 1_000:
            return f"{count / 1_000:.1f}k"
        return str(count)

    def extract_info(self, url):
        """Extrai metadados da URL de forma segura."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': 'in_playlist',
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            is_playlist = 'entries' in info or info.get('_type') == 'playlist'
            entries = list(info.get('entries', [])) if is_playlist else []
            
            # Pega thumbnail de alta qualidade se disponível
            thumbnail = info.get('thumbnail')
            if not thumbnail and 'thumbnails' in info and len(info['thumbnails']) > 0:
                thumbnail = info['thumbnails'][-1].get('url')

            return {
                "id": info.get('id', ''),
                "title": info.get('title', 'Sem título'),
                "uploader": info.get('uploader', info.get('channel', 'Desconhecido')),
                "duration_raw": info.get('duration', 0),
                "duration": self.format_duration(info.get('duration', 0)),
                "views": self.format_views(info.get('view_count', 0)),
                "thumbnail": thumbnail or "",
                "is_playlist": is_playlist,
                "playlist_count": len(entries),
                "entries": entries,
                "url": url
            }

    def _get_format_spec(self, quality, is_audio=False):
        """Retorna o seletor de formato otimizado com fallbacks para evitar erros de FFmpeg."""
        if is_audio:
            if quality == "mp3_320" or quality == "320kbps":
                return "bestaudio/best"
            elif quality == "mp3_128" or quality == "128kbps":
                return "bestaudio[abr<=128]/bestaudio/best"
            return "bestaudio/best"

        q_lower = quality.lower()
        if "1080" in q_lower:
            return "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]/best"
        elif "720" in q_lower:
            return "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]/best"
        elif "480" in q_lower:
            return "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]/best"
        elif "360" in q_lower:
            return "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]/best"
        elif "áudio" in q_lower or "audio" in q_lower:
            return "bestaudio/best"
        else:
            return "best[ext=mp4]/best"

    def download_single(self, url, quality, output_dir=None, on_progress=None, on_complete=None, on_error=None, is_audio=False):
        """Executa o download de um vídeo ou áudio individual."""
        self.reset_cancel()
        if not output_dir:
            output_dir = PlatformHelper.get_download_directory()

        def _worker():
            try:
                format_spec = self._get_format_spec(quality, is_audio)
                
                # Se for áudio, define extensão de áudio
                outtmpl = os.path.join(output_dir, '%(title)s.%(ext)s')

                def progress_hook(d):
                    if self._is_cancelled:
                        raise DownloadCancelledException("Download cancelado pelo usuário.")

                    if d.get('status') == 'downloading':
                        # Cálculo seguro de progresso
                        downloaded = d.get('downloaded_bytes', 0)
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        
                        percent = 0.0
                        if total > 0:
                            percent = (downloaded / total) * 100.0
                        else:
                            # Fallback usando regex em _percent_str se disponível
                            raw_percent = d.get('_percent_str', '0%')
                            clean_str = re.sub(r'\x1b\[[0-9;]*m', '', raw_percent).replace('%', '').strip()
                            try:
                                percent = float(clean_str)
                            except ValueError:
                                percent = 0.0

                        speed = d.get('_speed_str', '')
                        eta = d.get('_eta_str', '')
                        filename = d.get('filename', 'Arquivo')
                        
                        # Limpa cores ANSI
                        if speed:
                            speed = re.sub(r'\x1b\[[0-9;]*m', '', speed).strip()
                        if eta:
                            eta = re.sub(r'\x1b\[[0-9;]*m', '', eta).strip()

                        # Notificação inteligente a cada 10%
                        self.notifier.notify_progress(percent, os.path.basename(filename))

                        if on_progress:
                            on_progress(percent, speed, eta, downloaded, total)

                ydl_opts = {
                    'format': format_spec,
                    'outtmpl': outtmpl,
                    'progress_hooks': [progress_hook],
                    'noplaylist': True,
                    'no_warnings': True,
                    'quiet': True,
                    'windowsfilenames': True,
                }

                # Se for áudio puro e usuário pediu mp3/m4a, tenta pós-processador se ffmpeg existir
                if is_audio:
                    ydl_opts['extract_flat'] = False
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3' if 'mp3' in quality.lower() else 'm4a',
                        'preferredquality': '192',
                    }]

                with YoutubeDL(ydl_opts) as ydl:
                    self._current_ydl = ydl
                    info = ydl.extract_info(url, download=True)
                    
                    # Nome do arquivo final salvo
                    saved_filename = ydl.prepare_filename(info)
                    if is_audio and not os.path.exists(saved_filename):
                        # Caso tenha sido convertido para .mp3 / .m4a
                        base, _ = os.path.splitext(saved_filename)
                        for ext in ['.mp3', '.m4a', '.webm', '.opus']:
                            if os.path.exists(base + ext):
                                saved_filename = base + ext
                                break

                    title = info.get('title', os.path.basename(saved_filename))
                    thumbnail = info.get('thumbnail', '')
                    
                    # Notifica sucesso
                    self.notifier.notify_success(title)
                    
                    if on_complete:
                        on_complete(title, saved_filename, thumbnail, "audio" if is_audio else "video")

            except DownloadCancelledException:
                if on_error:
                    on_error("Download cancelado.")
            except Exception as e:
                print(f"[DownloaderEngine] Erro no download: {e}")
                self.notifier.notify_error(str(e))
                if on_error:
                    on_error(str(e))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    def download_playlist(self, url, quality, output_dir=None, on_item_start=None, on_progress=None, on_item_complete=None, on_all_complete=None, on_error=None, is_audio=False):
        """Executa o download de todos os itens de uma playlist."""
        self.reset_cancel()
        if not output_dir:
            output_dir = PlatformHelper.get_download_directory()

        def _worker():
            try:
                # 1. Extrai a lista de vídeos da playlist
                info = self.extract_info(url)
                entries = info.get('entries', [])
                if not entries:
                    if on_error:
                        on_error("Nenhum vídeo encontrado nesta playlist.")
                    return

                total_items = len(entries)
                completed_items = 0

                for index, entry in enumerate(entries):
                    if self._is_cancelled:
                        break

                    video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    video_title = entry.get('title', f"Vídeo {index + 1}")

                    if on_item_start:
                        on_item_start(index + 1, total_items, video_title)

                    format_spec = self._get_format_spec(quality, is_audio)
                    outtmpl = os.path.join(output_dir, '%(title)s.%(ext)s')

                    def progress_hook(d):
                        if self._is_cancelled:
                            raise DownloadCancelledException()
                        if d.get('status') == 'downloading':
                            downloaded = d.get('downloaded_bytes', 0)
                            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                            percent = (downloaded / total * 100.0) if total > 0 else 0.0
                            speed = d.get('_speed_str', '')
                            eta = d.get('_eta_str', '')
                            if on_progress:
                                on_progress(index + 1, total_items, percent, speed, eta)

                    ydl_opts = {
                        'format': format_spec,
                        'outtmpl': outtmpl,
                        'progress_hooks': [progress_hook],
                        'noplaylist': True,
                        'no_warnings': True,
                        'quiet': True,
                        'windowsfilenames': True,
                    }

                    try:
                        with YoutubeDL(ydl_opts) as ydl:
                            item_info = ydl.extract_info(video_url, download=True)
                            saved_file = ydl.prepare_filename(item_info)
                            completed_items += 1
                            if on_item_complete:
                                on_item_complete(index + 1, total_items, item_info.get('title', video_title), saved_file)
                    except DownloadCancelledException:
                        break
                    except Exception as item_err:
                        print(f"[Playlist] Erro no item {index + 1}: {item_err}")

                if on_all_complete:
                    on_all_complete(completed_items, total_items)

            except Exception as e:
                print(f"[Playlist] Erro geral: {e}")
                if on_error:
                    on_error(str(e))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

