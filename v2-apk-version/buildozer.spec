[app]
title = Pil Takip
package.name = pilUygulamasi
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
# Python surumu artik sabitlenmiyor. SEBEP: kurulu python-for-android
# surumu (2026.5.9) hostpython3 recipe'inde sabit olarak 3.14.2 bekliyor;
# requirements'ta farkli bir surum zorlamak "python3 should have same
# version as hostpython3" hatasina yol aciyordu. Bu p4a surumu zaten
# 3.14 ile uyumlu sekilde guncellenmis olmali (remote_debugging.c
# sorununu da kapsamis olabilir) - sorun cikarsa burayi tekrar gozden
# geciririz.
requirements = python3,kivy,requests,pyjnius,jnius,android
# Android 14 (API 34) icin FOREGROUND_SERVICE_DATA_SYNC eklendi.
# foregroundServiceType = dataSync deklare edildiginde, sistem bu tipe
# ozel alt-izni de ister; bu izin olmadan startForeground() cagrisi
# Android 14+ cihazlarda SecurityException ile basarisiz olabilir.
android.permissions = INTERNET,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_DATA_SYNC,POST_NOTIFICATIONS,WAKE_LOCK
# *** main.py ILE BIREBIR ESLESMELI (Mükemmel kurgulanmış) ***
services = piltakip:service.py:foreground:foregroundServiceType=dataSync
# KRİTİK EKLEME: Android 14+ çökmelerini engellemek için ön plan servis tipini dataSync yapıyoruz
android.manifest.foregroundServiceType = dataSync
# 2026 Standartları ve kararlılık için API 34'e çekildi
android.api = 34
# API 23 -> 24 yukseltildi. SEBEP: CPython 3.14'teki remote_debugging.c
# modulu preadv/pwritev sistem cagrilarini kullaniyor; bu fonksiyonlar
# Android bionic libc'de API 24 (Android 7.0) itibariyle tanimli.
# API 23'te "call to undeclared function 'preadv'/'pwritev'" derleme
# hatasi olusuyordu. API 24, NDK r28c ve CPython 3.14 ile uyumlu minimum seviye.
android.minapi = 24
android.ndk = 28c
android.archs = arm64-v8a,armeabi-v7a
android.add_permissions = android.permission.BLUETOOTH_ADMIN
orientation = portrait
fullscreen = 0
[buildozer]
log_level = 2
warn_on_root = 1
