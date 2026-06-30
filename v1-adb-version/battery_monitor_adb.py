import subprocess
import re
import time
import os
import psutil
# Andorid telefon ve Watch7 cihazlarında çalıştırılmıştır!
# 🎯 CİHAZ BAĞLANTI AYARLARI (Kendi IP ve Portlarına Göre Düzenle)
WATCH_WIFI_IP = "" 
PHONE_WIFI_IP = ""  # <--- Kablosuz ADB veya donanım kimliğini yaz

# SORGU PERİYODU (SANİYE CİNSİNDEN)
Waiting_time = 15 

def get_phone_battery():
    try:
        # Şarj durumunu analiz etmek için doğrudan dumpsys battery verisini çekiyoruz
        cmd_backup = f"adb -s {PHONE_WIFI_IP} shell dumpsys battery"
        res_backup = subprocess.run(cmd_backup, shell=True, capture_output=True, text=True, errors='ignore')
        output = res_backup.stdout
        
        # 1. Pil Yüzdesini Bul
        match_level = re.search(r"level:\s*(\d+)", output, re.IGNORECASE)
        
        # 2. Şarj Durumunu Bul (status: 2 -> Şarj Oluyor demektir)
        match_status = re.search(r"status:\s*(\d+)", output, re.IGNORECASE)
        

        wireless_power = re.search(r"Wireless powered:\s*true", output, re.IGNORECASE)
        
        charge = "Pilde"
        if (match_status and match_status.group(1) == "2")or wireless_power:
            charge = "Şarj Oluyor"
            
        if match_level:
            return f"%{match_level.group(1)} [{charge}]"
            
        # --- C Planı (Eğer dumpsys bir anlık kaçarsa eski logcat yöntemini dene) ---
        cmd_log = f"adb -s {PHONE_WIFI_IP} logcat -d -v brief *:E *:I"
        output_log = subprocess.check_output(cmd_log, shell=True, text=True, errors='ignore')
        pattern = r"!@new_battery_dump\s*:\s*([\d,]+)"
        matches = re.findall(pattern, output_log)
        if matches:
            data_fields = matches[-1].split(',')
            if len(data_fields) >= 5:
                return f"%{data_fields[4].strip()} [Kilitli/Bilinmiyor]"

    except Exception:
        return "Okunamadı"
    return "Veri bekleniyor..."

def get_laptop_battery():
    #"""Laptop batarya yüzdesini ve şarj durumunu çeker."""
    battery = psutil.sensors_battery() 
    if battery is None: 
        return "battery bulunamadı"
    
    percent = battery.percent
    charge = "Şarj Oluyor" if battery.power_plugged else "Pilde"
    return f"%{percent} [{charge}]"

def get_watch_battery():
    #"""Saate Wi-Fi üzerinden anlık dumpsys sorgusu atar."""
    cmd = f"adb -s {WATCH_WIFI_IP} shell dumpsys battery"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='ignore')
    
    match = re.search(r"level:\s*(\d+)", result.stdout, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def clear_terminal():
    #"""Terminal ekranını temizleyerek verilerin sabit kalmasını sağlar."""
    os.system('cls' if os.name == 'nt' else 'clear')

def start_periodic_monitor():
    print(" Cihazlara bağlanılıyor...")
    subprocess.run(f"adb connect {WATCH_WIFI_IP}", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run(f"adb connect {PHONE_WIFI_IP}", shell=True, stdout=subprocess.DEVNULL)
    
    print(" 🛰️ Periyodik Pil İzleme Sistemi Başlatılıyor...")
    time.sleep(1.5)
    
    try:
        while True:
            watch_info = get_watch_battery()
            laptop_info = get_laptop_battery()
            phone_info = get_phone_battery()
            
            clear_terminal()
            
            print("==================================================")
            print("     🖥️ MERKEZİ CİHAZ BATARYA PANELİ ")
            print("==================================================")
            
            # 1. Saat Satırı
            if watch_info:
                print(f"⌚ Galaxy Watch7      : %{watch_info}")
            else:
                print("⌚ Galaxy Watch7      : ❌ Bağlantı Koptu! (Yeniden deneniyor...)")
                subprocess.run(f"adb connect {WATCH_WIFI_IP}", shell=True, stdout=subprocess.DEVNULL)
            
            # 2. Telefon Satırı
            print(f"📱 Telefon Bataryası  : {phone_info}")
            
            # 3. Laptop Satırı
            print(f"💻 Laptop Bataryası   : {laptop_info}")
            
            print("==================================================")
            print(f"🔄 Döngü Süresi: {Waiting_time} sn | Son Güncelleme: {time.strftime('%H:%M:%S')}")
            print("🛑 Durdurmak için: Ctrl + C")
            print("==================================================")
            
            time.sleep(Waiting_time)
            
    except KeyboardInterrupt:
        print("\n Periyodik izleme sonlandırıldı. Panel kapatılıyor.")

if __name__ == "__main__":
    start_periodic_monitor()