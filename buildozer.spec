[app]

# (str) Title of your application
title = MultDownload

# (str) Package name
package.name = multdownload

# (str) Package domain (needed for android/ios packaging)
package.domain = org.joadsonrocha

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ico,json,txt

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,core/*,ui/*,ui/screens/*

# (str) Application version
version = 4.2.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd,yt-dlp,plyer,requests,urllib3,certifi,openssl,pillow,android,pyjnius

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
android.presplash_color = #F5F7FA

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/presplash.png

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,POST_NOTIFICATIONS,FOREGROUND_SERVICE,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android architectures to build for, can be any of
# 'armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64'
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (list) Gradle dependencies to add
android.gradle_dependencies = androidx.core:core:1.10.1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

