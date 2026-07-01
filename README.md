# Pil-Projesi
# Centralized Battery Monitoring System (ADB to APK) 🔋

Bu proje; akıllı telefon, akıllı saat ve bilgisayarın pil durumlarını tek bir merkezi panelden anlık olarak takip etmek amacıyla geliştirilmiş bir IoT ve haberleşme projesidir. Proje, süreç içerisinde daha efektif, kablosuz ve bağımsız bir mimariye kavuşması için iki ana aşamada geliştirilmiştir.

---

## 🚀 Projenin Evrimi (Evolution of the Project)

### 🔹 Aşama 1: ADB Tabanlı Altyapı (`v1-adb-version`)
İlk versiyonda, Android cihazlardan pil verilerini çekmek için **Python ve ADB (Android Debug Bridge)** tabanlı bir mimari kuruldu.
* **Çalışma Mantığı:** Bilgisayar, USB veya Wi-Fi üzerinden bağlı olan Android cihazlara (Telefon ve Galaxy Watch7) arka planda periyodik olarak `adb shell dumpsys battery` komutunu gönderir. Gelen çıktı Python tarafında Regex (`re`) ile parse edilerek terminal/arayüz paneline aktarılır.
* **Gelişmiş Özellikler:** Standart dumpsys komutunun yanıt vermediği durumlarda, arka planda logcat çıktılarını (`!@new_battery_dump`) analiz eden yedek bir **"C Planı"** mekanizması entegre edilmiştir. Ayrıca cihazların kablosuz şarj durumunu (`Wireless powered`) da algılayabilir.
* **Kısıtlamalar:** Sürekli ADB bağımlılığı, bilgisayarda ADB servislerinin açık olma zorunluluğu ve kablo/port yönetim yükü.

### 🔹 Aşama 2: APK ile Kablosuz Özgürlük (`v2-apk-version`) — Geliştirilmiş Sürüm
Sistemi tamamen kablosuz, arka planda bağımsız çalışan ve daha kararlı bir yapıya ulaştırmak için ADB bağımlılığı tamamen ortadan kaldırılmıştır.
* **Çalışma Mantığı:** Android cihazlar için arka planda (*Background Service*) çalışan özel bir APK (Mobil Uygulama) geliştirilmiştir.
* **Avantajları:** Telefon ve saat, kendi pil durumlarını yerel ağ üzerinden (*Socket Programming - TCP/UDP*) doğrudan bilgisayardaki merkezi Python sunucusuna fırlatır. Bilgisayarda ADB kurulumuna gerek kalmaz, cihazlar ağa bağlı olduğu sürece sistem tamamen özgür ve kesintisiz çalışır.
* **⚠️ Güncel Durum (BLE Entegrasyonu):** Cihazlar arası ağ bağımlılığını daha da azaltmak adına **BLE (Bluetooth Low Energy)** protokolü projeye dahil edilmektedir. Ancak şu anki aşamada, BLE veri iletim katmanında anlık senkronizasyon hataları (*real-time synchronization lag / packet drop*) gözlemlenmekte olup, geliştirme süreci devam etmektedir.

---
## 📌 Bilinen Sorunlar & Yol Haritası (Known Issues & Roadmap)

- [x] ADB bağımlılığının kaldırılması ve Soket mimarisine (TCP/UDP) geçiş.
- [x] Arka planda kesintisiz çalışan Android APK servisinin yazılması.
- [ ] **[Geliştiriliyor]** BLE (Bluetooth Low Energy) entegrasyonundaki anlık senkronizasyon ve veri paket kaçırma hatalarının giderilmesi.
- [ ] Merkezi panel için gelişmiş bir masaüstü arayüzü (GUI) entegrasyonu.
---
## 🛠️ Kullanılan Teknolojiler & Kütüphaneler

* **Python 3.x** (Merkezi Panel, `subprocess`, `re`, `psutil`, `socket`)
* **Android SDK / Java-Kotlin** (Cihaz tarafında çalışan arka plan servisli APK için)
* **ADB (Android Debug Bridge)** (İlk versiyon haberleşme köprüsü)
* **Socket Programming** (İkinci versiyon kablosuz ağ iletişimi)
* **BLE (Bluetooth Low Energy)** (Cihazlar arası yerel senkronizasyon protokolü)

---

## 📋 Kurulum ve Çalıştırma (v1 Sürümü İçin)

1. Bilgisayarınıza ADB (Android Debug Bridge) kurulumunu yapın ve ortam değişkenlerine ekleyin.
2. Gerekli Python kütüphanesini yükleyin:
   ```bash
   pip install psutil
3. battery_monitor_adb.py dosyasını açarak WATCH_WIFI_IP ve PHONE_WIFI_IP değişkenlerine kendi cihazlarınızın IP adreslerini yazın.
4. Projeyi çalıştırın:python battery_monitor_adb.py

## 📋 Kurulum ve Çalıştırma (v2 Sürümü İçin)

> 💡 **Not:** v2 sürümünde sistem çalışma esnasında ADB bağımlılığı barındırmaz. Ancak geliştirilen `.apk` dosyasını telefonunuza ilk defa yüklemek için bilgisayarınız üzerinden ADB terminalini kullanabilirsiniz.
> 💡 Not:Eğer sunucunuza hiçbir bilgi düşmezse  ağınızı özel ağ olarak ayarlamayı deneyiniz.

1. Telefonunuzda **Geliştirici Seçenekleri** içerisinden **USB Hata Ayıklama (USB Debugging)** modunu aktif hale getirin ve cihazı bilgisayarınıza bağlayın.
2. Terminal (PowerShell / Komut İstemi) üzerinden aşağıdaki komutu kendi dosya yolunuza göre düzenleyerek çalıştırın ve uygulamanın yüklenmesini sağlayın:
   ```bash
   adb install -r /dosya/yolunuz/pilUygulamasi-1.0-arm64-v8a_armeabi-v7a-debug.apk
3. Eğer bilgisayardan manuel başlatmak isterseniz Terminal (PowerShell / Komut İstemi) üzerinden aşağıdaki komutu kendi dosya yolunuza göre düzenleyerek yapabilirsniz:
   ```bash
   adb shell monkey -p org.test.piluygulamasi -c android.intent.category.LAUNCHER 1
4.Yükleme tamamlandıktan sonra cihazınızda uygulamayı açın ve gerekli tüm Arka Plan ve Güç Yönetimi izinlerini verin.
5. Komutu girdikten sonra cihazınızda uygulama beliricektir uygulamayı açın ve izinleri verin
6. İzinler verildikten sonra servisi başlatın
7. Bilgisayarınızda merkezi sunucu kodunu başlatın:
   ```bash
    python server.py
   ```
8. Sunucu ayağa kalktıktan sonra, telefonunuz yerel ağ üzerinden her 60 saniyede bir pil durum verilerini sunucuya fırlatmaya başlayacaktır.
⚠️ Önemli Not: Bilinen BLE senkronizasyon hatası sebebiyle, akıllı saat (Galaxy Watch) batarya verileri şu an için sunucu paneline hatalı veya gecikmeli yansıyabilir. Bu kısım için geliştirme süreci devam etmektedir.

### 🛠️ Yapılan Düzeltmeler ve Dokunuşlar:
* **Terminal Bağımsızlığı:** Sadece Windows (PowerShell) değil, Linux veya macOS kullanan geliştiricilerin de anlayabilmesi için adımları daha genel bir terminal diliyle ifade ettim.
* **İzin Detayı:** Android arka plan servislerinin (Background Service) kararlı çalışması için en kritik şey güç tasarrufu izinleridir. Bu yüzden "İzinleri verin" kısmını "Arka Plan ve Güç Yönetimi izinleri" olarak daha spesifik hale getirdim.
* **BLE Uyarısı:** En son adımdaki BLE uyarısını, GitHub repolarında sıkça kullanılan blok alıntı (`> ⚠️`) içine alarak dikkat çekici ve profesyonel bir "Bilinen Kısıtlamalar" notu haline getirdim.

  ## Geliştirici
   Bayram Ay- Elektronik-Elektrik Mühendisliği Öğrencisi
## 🛠️ Katkıda Bulunanlar (Contributors)

Bu proje aşağıdaki teknolojiler ve araçlar yardımıyla geliştirilmiştir:

| **Claude** | hata ayıklama (debugging) ve algoritma optimizasyonu |
| :---: | :--- |
| **Gemini** | Kod mimarisi, hata ayıklama (debugging) ve algoritma optimizasyonu |

<br>



![Built with Gemini](https://img.shields.io/badge/Built%20with-Gemini-blue?style=for-the-badge&logo=google-gemini)
![Built with Claude](https://img.shields.io/badge/Built%20with-Claude-D97757?style=for-the-badge)
