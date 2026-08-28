import io
import os
import re
import shutil
import sys
import threading
from contextlib import contextmanager
from yt_dlp import YoutubeDL
from core.platform_helper import PlatformHelper
from core.notifier import Notifier


class DownloadCancelledException(Exception):
    pass


class _YtdlpLogger:
    """Logger customizado para yt-dlp que evita o erro 'str has no attribute write'.
    Substitui quiet=True e no_warnings=True que causam conflitos nas versões 2025+."""
    def debug(self, msg):
        if msg.startswith('[debug]'):
            pass  # ignora mensagens de debug verbose
    def info(self, msg):
        pass
    def warning(self, msg):
        print(f'[yt-dlp warn] {msg}')
    def error(self, msg):
        print(f'[yt-dlp error] {msg}')


def _get_ffmpeg_location():
    """Retorna o caminho do binário ffmpeg: sistema ou imageio-ffmpeg como fallback."""
    path = shutil.which('ffmpeg')
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


# Caminho do ffmpeg resolvido uma única vez ao importar o módulo
_FFMPEG_PATH = _get_ffmpeg_location()
if _FFMPEG_PATH:
    print(f'[DownloaderEngine] ffmpeg encontrado: {_FFMPEG_PATH}')
else:
    print('[DownloaderEngine] ffmpeg não encontrado — conversão de áudio desabilitada')


def _friendly_error(raw: str) -> str:
    """Converte mensagens de erro do yt-dlp para português amigável ao usuário."""
    msg = raw.lower()
    if 'not available' in msg or 'video unavailable' in msg:
        return '❌ Este vídeo não está disponível no YouTube (pode ser privado, removido ou bloqueado no seu país).'
    if 'private video' in msg:
        return '🔒 Este vídeo é privado e não pode ser baixado.'
    if 'age' in msg and ('restrict' in msg or 'limit' in msg):
        return '🔞 Este vídeo tem restrição de idade e não pode ser baixado sem login.'
    if 'copyright' in msg or 'removed' in msg:
        return '⚖️ Este vídeo foi removido por violação de direitos autorais.'
    if 'members only' in msg or 'join' in msg:
        return '👥 Este vídeo é exclusivo para membros do canal.'
    if 'live event' in msg or 'is live' in msg:
        return '🔴 Transmissões ao vivo não podem ser baixadas.'
    if 'playlist' in msg and ('empty' in msg or 'not found' in msg):
        return '📋 Playlist não encontrada ou está vazia.'
    if 'urlopen error' in msg or 'network' in msg or 'connection' in msg or 'timeout' in msg:
        return '🌐 Erro de conexão. Verifique sua internet e tente novamente.'
    if 'unable to extract' in msg or 'no video formats' in msg:
        return '⚠️ Não foi possível extrair o vídeo. O link pode estar desatualizado ou inválido.'
    if 'format' in msg and 'not available' in msg:
        return '📹 O formato de qualidade solicitado não está disponível para este vídeo.'
    if 'sign in' in msg or 'login' in msg:
        return '🔑 Este vídeo requer login no YouTube para ser acessado.'
    if 'rate limit' in msg or '429' in msg:
        return '⏱️ Muitas requisições. Aguarde alguns minutos e tente novamente.'
    if 'cancelled' in msg or 'cancelado' in msg:
        return '⛔ Download cancelado pelo usuário.'
    # Fallback: remove o prefixo técnico do yt-dlp e retorna limpo
    cleaned = re.sub(r'^ERROR:\s*\[[\w\s]+\]\s*[\w-]+:\s*', '', raw, flags=re.IGNORECASE).strip()
    return f'⚠️ {cleaned}' if cleaned else '⚠️ Ocorreu um erro inesperado. Tente novamente.'


@contextmanager
def _safe_ydl(opts):
    """Cria YoutubeDL com sys.stderr/stdout reais.

    O Kivy substitui sys.stderr pelo seu Logger (cujo .buffer é uma str),
    o que faz o yt-dlp chamar str.write() e levantar AttributeError.
    Corrigimos restaurando temporariamente streams reais antes de instanciar YoutubeDL.
    """
    devnull = open(os.devnull, 'w', encoding='utf-8', errors='replace')
    old_stderr, old_stdout = sys.stderr, sys.stdout
    try:
        sys.stderr = devnull
        sys.stdout = devnull
        with YoutubeDL(opts) as ydl:
            yield ydl
    finally:
        sys.stderr = old_stderr
        sys.stdout = old_stdout
        try:
            devnull.close()
        except Exception:
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
        return str(count)  # Fix #1: retorno explícito para valores < 1000

    def search_youtube(self, query="músicas em alta", max_results=8):
        """Busca vídeos e músicas no YouTube e retorna uma lista formatada de resultados."""
        if not query or not query.strip():
            query = "músicas em alta brasil"
            
        search_query = query if query.startswith(('http://', 'https://')) else f"ytsearch{max_results}:{query}"
        
        ydl_opts = {
            'logger': _YtdlpLogger(),   # substitui quiet=True/no_warnings — fix write error
            'skip_download': True,
            'extract_flat': True,
        }
        if _FFMPEG_PATH:
            ydl_opts['ffmpeg_location'] = _FFMPEG_PATH
        with _safe_ydl(ydl_opts) as ydl:
            res = ydl.extract_info(search_query, download=False)
            entries = []
            raw_entries = res.get('entries', []) if ('entries' in res) else [res]
            for item in raw_entries:
                if not item:
                    continue
                thumb = item.get('thumbnail')
                if not thumb and 'thumbnails' in item and len(item['thumbnails']) > 0:
                    thumb = item['thumbnails'][-1].get('url')
                if not thumb and item.get('id'):
                    thumb = f"https://i.ytimg.com/vi/{item.get('id')}/hqdefault.jpg"
                
                url = item.get('url')
                if not url or not url.startswith('http'):
                    url = f"https://www.youtube.com/watch?v={item.get('id')}"

                entries.append({
                    "id": item.get('id', ''),
                    "title": item.get('title', 'Sem título'),
                    "uploader": item.get('uploader', item.get('channel', 'YouTube')),
                    "duration": self.format_duration(item.get('duration', 0)),
                    "thumbnail": thumb or "",
                    "url": url,
                    "views": self.format_views(item.get('view_count', 0))
                })
            return entries

    def extract_info(self, url):
        """Extrai metadados da URL de forma segura."""
        ydl_opts = {
            'logger': _YtdlpLogger(),   # substitui quiet=True/no_warnings — fix write error
            'skip_download': True,
            'extract_flat': 'in_playlist',
        }
        if _FFMPEG_PATH:
            ydl_opts['ffmpeg_location'] = _FFMPEG_PATH
        with _safe_ydl(ydl_opts) as ydl:
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
            # Fix #2: normaliza strings como "mp3_320kbps" → extrai o número
            q_lower = quality.lower()
            if "320" in q_lower:
                return "bestaudio[abr<=320]/bestaudio/best"
            elif "256" in q_lower:
                return "bestaudio[abr<=256]/bestaudio/best"
            elif "192" in q_lower:
                return "bestaudio[abr<=192]/bestaudio/best"
            elif "128" in q_lower:
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
        # Fix #14: cada download cria seu próprio flag de cancelamento isolado
        cancel_flag = {'cancelled': False}
        self._is_cancelled = False
        if not output_dir:
            output_dir = PlatformHelper.get_download_directory()

        def _worker():
            try:
                format_spec = self._get_format_spec(quality, is_audio)
                
                # Se for áudio, define extensão de áudio
                outtmpl = os.path.join(output_dir, '%(title)s.%(ext)s')

                def progress_hook(d):
                    # Fix #14: verifica flag local E global
                    if cancel_flag['cancelled'] or self._is_cancelled:
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
                    'logger': _YtdlpLogger(),   # fix: substitui quiet/no_warnings
                    'windowsfilenames': True,
                }
                if _FFMPEG_PATH:
                    ydl_opts['ffmpeg_location'] = _FFMPEG_PATH

                # Se for áudio puro, configura pós-processador FFmpeg para MP3/M4A
                if is_audio:
                    if _FFMPEG_PATH:
                        bitrate_match = re.search(r'(\d+)', quality)
                        preferred_quality = bitrate_match.group(1) if bitrate_match else '192'
                        preferred_codec = 'mp3' if 'mp3' in quality.lower() else 'm4a'
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': preferred_codec,
                            'preferredquality': preferred_quality,
                        }]
                    else:
                        # Sem ffmpeg: baixa no formato nativo (opus/webm) sem conversão
                        print('[DownloaderEngine] ffmpeg ausente — baixando áudio no formato nativo')

                with _safe_ydl(ydl_opts) as ydl:
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
                    on_error("⛔ Download cancelado.")
            except Exception as e:
                friendly = _friendly_error(str(e))
                print(f"[DownloaderEngine] Erro no download: {e}")
                self.notifier.notify_error(friendly)
                if on_error:
                    on_error(friendly)

        # Fix #14: expõe cancel_flag para cancelamento isolado
        self._current_cancel_flag = cancel_flag
        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    def download_playlist(self, url, quality, output_dir=None, on_item_start=None, on_progress=None, on_item_complete=None, on_all_complete=None, on_error=None, is_audio=False):
        """Executa o download de todos os itens de uma playlist."""
        self._is_cancelled = False
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
                        'logger': _YtdlpLogger(),   # fix: substitui quiet/no_warnings
                        'windowsfilenames': True,
                    }
                    if _FFMPEG_PATH:
                        ydl_opts['ffmpeg_location'] = _FFMPEG_PATH

                    try:
                        with _safe_ydl(ydl_opts) as ydl:
                            item_info = ydl.extract_info(video_url, download=True)
                            saved_file = ydl.prepare_filename(item_info)
                            completed_items += 1
                            if on_item_complete:
                                on_item_complete(index + 1, total_items, item_info.get('title', video_title), saved_file)
                    except DownloadCancelledException:
                        break
                    except Exception as item_err:
                        friendly = _friendly_error(str(item_err))
                        print(f"[Playlist] Erro no item {index + 1}: {item_err}")
                        # Continua para o próximo item mesmo com erro

                if on_all_complete:
                    on_all_complete(completed_items, total_items)

            except Exception as e:
                friendly = _friendly_error(str(e))
                print(f"[Playlist] Erro geral: {e}")
                if on_error:
                    on_error(friendly)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

