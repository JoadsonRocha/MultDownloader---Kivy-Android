import os
import sys
import subprocess
from kivy.utils import platform

class PlatformHelper:
    @staticmethod
    def is_android():
        return platform == 'android'

    @staticmethod
    def request_android_permissions():
        """Solicita as permissões necessárias para Android (compatível com Android 9 até 14+)."""
        if not PlatformHelper.is_android():
            return

        try:
            from android.permissions import request_permissions, Permission
            permissions = [
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE,
            ]
            
            # Adiciona permissões de armazenamento conforme a API
            if hasattr(Permission, 'READ_EXTERNAL_STORAGE'):
                permissions.append(Permission.READ_EXTERNAL_STORAGE)
            if hasattr(Permission, 'WRITE_EXTERNAL_STORAGE'):
                permissions.append(Permission.WRITE_EXTERNAL_STORAGE)
            if hasattr(Permission, 'POST_NOTIFICATIONS'):
                permissions.append(Permission.POST_NOTIFICATIONS)
            if hasattr(Permission, 'READ_MEDIA_VIDEO'):
                permissions.append(Permission.READ_MEDIA_VIDEO)
            if hasattr(Permission, 'READ_MEDIA_AUDIO'):
                permissions.append(Permission.READ_MEDIA_AUDIO)

            request_permissions(permissions)
        except Exception as e:
            print(f"[PlatformHelper] Erro ao solicitar permissões Android: {e}")

    @staticmethod
    def get_download_directory():
        """Retorna o diretório de downloads padrão para Android ou Desktop."""
        if PlatformHelper.is_android():
            try:
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                download_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
                if os.path.exists(download_dir):
                    return download_dir
            except Exception as e:
                print(f"[PlatformHelper] Falha ao obter diretório via jnius: {e}")

            # Fallbacks comuns no Android
            fallbacks = [
                "/storage/emulated/0/Download",
                "/sdcard/Download",
                "/storage/emulated/0/Download/MultDownloader"
            ]
            for path in fallbacks:
                try:
                    os.makedirs(path, exist_ok=True)
                    if os.access(path, os.W_OK):
                        return path
                except Exception:
                    continue

        # Desktop (Windows, macOS, Linux)
        desktop_download = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(desktop_download, exist_ok=True)
        return desktop_download

    @staticmethod
    def open_file(filepath):
        """Abre o arquivo com o aplicativo padrão do sistema."""
        if not os.path.exists(filepath):
            return False

        if PlatformHelper.is_android():
            try:
                from jnius import autoclass, cast
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                
                context = PythonActivity.mActivity
                file_obj = File(filepath)
                
                # Obter MIME Type
                mime_type = "*/*"
                if filepath.lower().endswith(('.mp4', '.mkv', '.webm', '.avi')):
                    mime_type = "video/*"
                elif filepath.lower().endswith(('.mp3', '.m4a', '.wav', '.flac', '.opus', '.aac')):
                    mime_type = "audio/*"
                
                intent = Intent(Intent.ACTION_VIEW)
                # Tenta usar FileProvider ou Uri direto
                try:
                    FileProvider = autoclass('androidx.core.content.FileProvider')
                    uri = FileProvider.getUriForFile(context, context.getPackageName() + ".fileprovider", file_obj)
                    intent.setDataAndType(uri, mime_type)
                    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                except Exception:
                    uri = Uri.fromFile(file_obj)
                    intent.setDataAndType(uri, mime_type)
                
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(intent)
                return True
            except Exception as e:
                print(f"[PlatformHelper] Erro ao abrir arquivo no Android: {e}")
                return False
        else:
            try:
                if sys.platform.startswith('win'):
                    os.startfile(filepath)
                elif sys.platform.startswith('darwin'):
                    subprocess.Popen(['open', filepath])
                else:
                    subprocess.Popen(['xdg-open', filepath])
                return True
            except Exception as e:
                print(f"[PlatformHelper] Erro ao abrir arquivo no Desktop: {e}")
                return False

    @staticmethod
    def share_file(filepath):
        """Compartilha o arquivo via Intent no Android."""
        if not os.path.exists(filepath):
            return False

        if PlatformHelper.is_android():
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                File = autoclass('java.io.File')
                
                context = PythonActivity.mActivity
                file_obj = File(filepath)
                
                mime_type = "*/*"
                if filepath.lower().endswith(('.mp4', '.mkv', '.webm', '.avi')):
                    mime_type = "video/*"
                elif filepath.lower().endswith(('.mp3', '.m4a', '.wav', '.flac', '.opus', '.aac')):
                    mime_type = "audio/*"

                intent = Intent(Intent.ACTION_SEND)
                intent.setType(mime_type)
                
                try:
                    FileProvider = autoclass('androidx.core.content.FileProvider')
                    uri = FileProvider.getUriForFile(context, context.getPackageName() + ".fileprovider", file_obj)
                    intent.putExtra(Intent.EXTRA_STREAM, uri)
                    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                except Exception:
                    Uri = autoclass('android.net.Uri')
                    intent.putExtra(Intent.EXTRA_STREAM, Uri.fromFile(file_obj))

                chooser = Intent.createChooser(intent, "Compartilhar com")
                chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(chooser)
                return True
            except Exception as e:
                print(f"[PlatformHelper] Erro ao compartilhar no Android: {e}")
                return False
        return False
