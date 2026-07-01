import time
import json
import traceback
import threading
import requests
from kivy.utils import platform

PC_SERVER_URL = "http://192.168.1.109:8080/pil-guncelle"

GONDERIM_ARALIGI = 60          
BLE_TIMEOUT = 12                
BLE_BATTERY_SERVICE_UUID = "0000180f-0000-1000-8000-00805f9b34fb"
BLE_BATTERY_CHAR_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
SAAT_AD_FILTRESI = "Watch7"     

if platform == 'android':
    from jnius import autoclass, cast, java_method, PythonJavaClass

# Aynı TCP baglantisini tekrar tekrar kullanmak icin tek bir Session nesnesi.
_HTTP_SESSION = requests.Session()


class GattCallback:
    def __new__(cls, on_battery_level, on_error):
        class _GattCallbackImpl(PythonJavaClass):
            __javacontext__ = 'app'
            __javainterfaces__ = ['android/bluetooth/BluetoothGattCallback']

            def __init__(self, on_battery_level, on_error):
                super().__init__()
                self._on_battery_level = on_battery_level
                self._on_error = on_error
                self.gatt_ref = None

            @java_method('(Landroid/bluetooth/BluetoothGatt;II)V')
            def onConnectionStateChange(self, gatt, status, newState):
                self.gatt_ref = gatt
                BluetoothProfile = autoclass('android.bluetooth.BluetoothProfile')
                try:
                    if newState == BluetoothProfile.STATE_CONNECTED:
                        gatt.discoverServices()
                    elif newState == BluetoothProfile.STATE_DISCONNECTED:
                        self._on_error("Baglanti koptu")
                        # KRİTİK DÜZELTME: Sızıntıyı önlemek için önce disconnect sonra close
                        try: gatt.disconnect()
                        except: pass
                        gatt.close()
                except Exception as e:
                    self._on_error(f"Baglanti hatasi: {e}")
                    try: gatt.disconnect()
                    except: pass
                    try: gatt.close()
                    except: pass

            @java_method('(Landroid/bluetooth/BluetoothGatt;I)V')
            def onServicesDiscovered(self, gatt, status):
                try:
                    UUID = autoclass('java.util.UUID')
                    service_uuid = UUID.fromString(BLE_BATTERY_SERVICE_UUID)
                    char_uuid = UUID.fromString(BLE_BATTERY_CHAR_UUID)

                    service = gatt.getService(service_uuid)
                    if service is None:
                        self._on_error("Battery Service bulunamadi")
                        gatt.disconnect()
                        gatt.close()
                        return

                    characteristic = service.getCharacteristic(char_uuid)
                    if characteristic is None:
                        self._on_error("Characteristic bulunamadi")
                        gatt.disconnect()
                        gatt.close()
                        return

                    if not gatt.readCharacteristic(characteristic):
                        self._on_error("Okuma baslatilamadi")
                        gatt.disconnect()
                        gatt.close()
                except Exception as e:
                    self._on_error(f"Kesif hatasi: {e}")
                    try:
                        gatt.disconnect()
                        gatt.close()
                    except Exception:
                        pass

            @java_method('(Landroid/bluetooth/BluetoothGatt;Landroid/bluetooth/BluetoothGattCharacteristic;I)V')
            def onCharacteristicRead(self, gatt, characteristic, status):
                BluetoothGatt = autoclass('android.bluetooth.BluetoothGatt')
                try:
                    if status == BluetoothGatt.GATT_SUCCESS:
                        value = characteristic.getValue()
                        if value and len(value) > 0:
                            battery_level = value[0] & 0xFF
                            self._on_battery_level(battery_level)
                        else:
                            self._on_error("Bos pil verisi")
                    else:
                        self._on_error(f"Okuma basarisiz status: {status}")
                finally:
                    gatt.disconnect()
                    gatt.close()

        return _GattCallbackImpl(on_battery_level, on_error)


def saat_pilini_oku_ble(bt_device, sonuc_kutusu, activity):
    finally_event = threading.Event()

    def on_battery_level(level):
        sonuc_kutusu["deger"] = int(level)
        finally_event.set()

    def on_error(msg):
        if sonuc_kutusu["deger"] is None:
            sonuc_kutusu["hata"] = msg
        finally_event.set()

    callback = GattCallback(on_battery_level, on_error)

    try:
        gatt = bt_device.connectGatt(activity, False, callback, 2)
        callback.gatt_ref = gatt
    except Exception as e:
        sonuc_kutusu["hata"] = f"Gatt baglanti hatasi: {e}"
        return

    if not finally_event.wait(timeout=BLE_TIMEOUT):
        sonuc_kutusu["hata"] = "Zaman asimi"
        try:
            gatt.disconnect()
            gatt.close()
        except Exception:
            pass


def telefon_pilini_oku(activity):
    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
    battery_status = activity.registerReceiver(None, ifilter)

    if battery_status is None:
        return -1, "Bilinmiyor"

    level = battery_status.getIntExtra("level", -1)
    scale = battery_status.getIntExtra("scale", -1)
    phone_battery = int((level / float(scale)) * 100) if scale > 0 else -1

    status = battery_status.getIntExtra("status", -1)
    phone_status = {2: "Sarj Oluyor", 5: "Dolu", 4: "Sarj Olmuyor"}.get(status, "Pilde")
    return phone_battery, phone_status


def saat_cihazini_bul(activity):
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    bt_adapter = BluetoothAdapter.getDefaultAdapter()
    if not bt_adapter or not bt_adapter.isEnabled():
        return None

    bonded_devices = bt_adapter.getBondedDevices().toArray()
    for device in bonded_devices:
        device = cast('android.bluetooth.BluetoothDevice', device)
        name = device.getName()
        if name and SAAT_AD_FILTRESI in name:
            return device
    return None


def tum_pilleri_oku(activity):
    try:
        phone_battery, phone_status = telefon_pilini_oku(activity)
    except Exception as e:
        phone_battery, phone_status = -1, f"Hata: {e}"

    watch_battery_str = "Baglanti Yok"
    try:
        bt_device = saat_cihazini_bul(activity)
        if bt_device is None:
            watch_battery_str = "Saat Bulunamadi"
        else:
            sonuc_kutusu = {"deger": None, "hata": None}
            saat_pilini_oku_ble(bt_device, sonuc_kutusu, activity)
            if sonuc_kutusu["deger"] is not None:
                watch_battery_str = f"%{sonuc_kutusu['deger']}"
            else:
                watch_battery_str = f"Hata ({sonuc_kutusu['hata']})"
    except Exception as e:
        watch_battery_str = f"BLE Hatasi: {e}"

    return phone_battery, phone_status, watch_battery_str


def bildirimi_guncelle(activity, baslik, icerik):
    try:
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        Context = autoclass('android.content.Context')
        BuildVersion = autoclass('android.os.Build$VERSION')

        channel_id = "pil_takip_kanal"
        channel_name = "Pil Takip Servis Kanali"

        notification_manager = activity.getSystemService(Context.NOTIFICATION_SERVICE)

        if BuildVersion.SDK_INT >= 26:
            importance = NotificationManager.IMPORTANCE_LOW
            mChannel = NotificationChannel(channel_id, channel_name, importance)
            notification_manager.createNotificationChannel(mChannel)
            builder = NotificationBuilder(activity, channel_id)
        else:
            builder = NotificationBuilder(activity)

        builder.setContentTitle(baslik)
        builder.setContentText(icerik)
        
        pack_name = activity.getPackageName()
        icon_res = activity.getResources().getIdentifier("icon", "drawable", pack_name)
        if icon_res > 0:
            builder.setSmallIcon(icon_res)
        
        builder.setOngoing(True)
        notification = builder.build()

        # KRITIK DUZELTME: Android 14 (API 34) itibariyle startForeground()
        # cagrisinin KENDISI de servis tipini bilmek zorunda - sadece
        # buildozer.spec'teki "android.manifest.foregroundServiceType = dataSync"
        # ve manifest izni (FOREGROUND_SERVICE_DATA_SYNC) yeterli degil.
        # Bu olmadan "MissingForegroundServiceTypeException: Starting FGS
        # without a type" hatasi alinir ve bildirim hic gosterilmez.
        if BuildVersion.SDK_INT >= 29:
            ServiceInfo = autoclass('android.content.pm.ServiceInfo')
            activity.startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
        else:
            activity.startForeground(1, notification)
    except Exception as e:
        print(f"[Pil Servis] Bildirim hatasi: {e}")


def servis_dongusu(activity):
    failed_counter = 0

    while True:
        loop_start = time.time()
        try:
            phone_battery, phone_status, watch_pil = tum_pilleri_oku(activity)

            bildirimi_guncelle(
                activity,
                "Pil Takip Aktif",
                f"Tel: %{phone_battery} ({phone_status}) | Saat: {watch_pil}"
            )

            if PC_SERVER_URL:
                payload = {
                    "phone_battery": f"%{phone_battery}",
                    "phone_status": phone_status,
                    "watch_pil": watch_pil,
                }
                try:
                    response = _HTTP_SESSION.post(PC_SERVER_URL, json=payload, timeout=8)
                    response.raise_for_status()
                    failed_counter = 0
                except requests.exceptions.RequestException as req_err:
                    failed_counter += 1
                    print(f"[Pil Servis] HTTP Hatasi ({failed_counter}): {req_err}")
            
        except Exception as e:
            failed_counter += 1
            print(f"[Pil Servis] Dongu hatasi: {e}")
            traceback.print_exc()

        add_waiting = min(failed_counter * 15, 240) if failed_counter > 0 else 0
        total_Waiting = max(GONDERIM_ARALIGI - (time.time() - loop_start), 5) + add_waiting
        
        time.sleep(total_Waiting)


def calistir():
    PythonService = autoclass('org.kivy.android.PythonService')
    activity = PythonService.mService

    bildirimi_guncelle(activity, "Pil Takip", "Servis baslatiliyor...")

    t = threading.Thread(target=servis_dongusu, args=(activity,), name="PilServisDongusu")
    t.daemon = True
    t.start()
    return t


if __name__ == "__main__":
    if platform == 'android':
        servis_thread = calistir()
        while True:
            time.sleep(30)
            if not servis_thread.is_alive():
                print("[Pil Servis] Dongu thread'i durdu, yeniden baslatiliyor...")
                servis_thread = calistir()
