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

### 🔹 Aşama 2: APK ile Kablosuz Özgürlük (`v2-apk-version`) — *Geliştirilmiş Sürüm*
Sistemi tamamen kablosuz, arka planda bağımsız çalışan ve daha kararlı bir yapıya ulaştırmak için ADB bağımlılığı tamamen ortadan kaldırılmıştır.
* **Çalışma Mantığı:** Android cihazlar için arka planda (Background Service) çalışan özel bir **APK (Mobil Uygulama)** geliştirilmiştir. 
* **Avantajları:** Telefon ve saat, kendi pil durumlarını yerel ağ üzerinden (Socket Programming - TCP/UDP) doğrudan bilgisayardaki merkezi Python sunucusuna fırlatır. Bilgisayarda ADB kurulumuna gerek kalmaz, cihazlar ağa bağlı olduğu sürece sistem tamamen özgür ve kesintisiz çalışır.

---

## 🛠️ Kullanılan Teknolojiler & Kütüphaneler

* **Python 3.x** (Merkezi Panel, `subprocess`, `re`, `psutil`, `socket`)
* **Android SDK / Java-Kotlin** (Cihaz tarafında çalışan arka plan servisli APK için)
* **ADB (Android Debug Bridge)** (İlk versiyon haberleşme köprüsü)
* **Socket Programming** (İkinci versiyon kablosuz ağ iletişimi)

---

## 📋 Kurulum ve Çalıştırma (v1 Sürümü İçin)

1. Bilgisayarınıza ADB (Android Debug Bridge) kurulumunu yapın ve ortam değişkenlerine ekleyin.
2. Gerekli Python kütüphanesini yükleyin:
   ```bash
   pip install psutil
3. battery_monitor_adb.py dosyasını açarak WATCH_WIFI_IP ve PHONE_WIFI_IP değişkenlerine kendi cihazlarınızın IP adreslerini yazın.
4. Projeyi çalıştırın:python battery_monitor_adb.py

   Geliştirici
   Bayram Ay- Elektronik-Elektrik Mühendisliği Öğrencisi
## Katkıda Bulunanlar

| [<img src="https://www.gstatic.com/lamda/images/gemini_sparkle_v2.svg" width="100px;"/><br /><sub><b>Gemini</b></sub>](https://gemini.google.com/) |
| :---: |
| 🤖 (Yapay Zeka Yardımı) |
