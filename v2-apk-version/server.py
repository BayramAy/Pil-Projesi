# server.py
from flask import Flask, request, jsonify
import psutil

def get_PC_Battery():
    pc_batarya = psutil.sensors_battery()
    if pc_batarya is None:
        return "Batarya bulunamadi!"
    
    yuzde = pc_batarya.percent
    sarj_info = "Sarj Oluyor" if pc_batarya.power_plugged else ""
    return f"%{yuzde} [{sarj_info}]"

app = Flask(__name__)
@app.route('/pil-guncelle', methods=['POST'])
def batarya_verisi_al():
    try:
        veri = request.json
        PC_info = get_PC_Battery()
        print("\n--- Pil Verisi  ---")
        print(f"Bilgisayar Pili:{PC_info}")
        print(f"Telefon Pili: {veri.get('phone_battery')} [{veri.get('phone_status')}]")
        print(f"Saat Pili: {veri.get('watch_pil')}")
        print("----------------------------")
        return jsonify({"durum": "basarili"}), 200
    except Exception as e:
        print(f"Veri işleme hatası: {e}")
        return jsonify({"durum": "hata", "mesaj": str(e)}), 400
if __name__ == '__main__':
    # Sunucuyu tüm ağa açıyoruz (0.0.0.0), böylece telefonunuz bu bilgisayara bağlanabilir.
    # service.py içindeki PC_SERVER_URL bu sunucunun port 8080 ve /pil-guncelle route'una göre ayarlandı.
    app.run(host='0.0.0.0', port=8080, debug=True)