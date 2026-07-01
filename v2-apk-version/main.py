# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.clock import Clock


class PilUygulamasi(App):
    def build(self):
        self.kok_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        #Uygulama açılırken ilk yükleme ekranı
        self.status_tag = Label(
            text="Baslatiliyor...",
            font_size='18sp',
            halign='center',
        )
        self.status_tag.bind(size=self._etiket_genislik_guncelle)
        #Buton üzerindeki yazı
        self.service_stop_button = Button(
            text="Servisi Durdur",
            size_hint=(1, 0.2),
            on_press=self.servisi_durdur,
        )

        self.kok_layout.add_widget(self.status_tag)
        self.kok_layout.add_widget(self.service_stop_button)
        
        # Android bağımlılıklarını önbelleğe almak için değişkenler
        self.activity = None
        self.service_class = None
        self.target_service_class = None
        
        return self.kok_layout

    def _etiket_genislik_guncelle(self, instance, value):
        instance.text_size = (value[0], None)

    def on_start(self):
        if platform == 'android':
            # Önbellekleme işlemini burada bir kez yapıyoruz
            from android import mActivity
            from jnius import autoclass
            self.activity = mActivity
            context = self.activity.getApplicationContext()
            self.target_service_class = context.getPackageName() + ".ServicePiltakip"
            
            try:
                self.service_class = autoclass(self.target_service_class)
            #Java sınıfı yüklenemezse oluşacak hata
            except Exception as e:
                self.status_tag.text = f"Servis sınıfı bulunamadı:\n{e}"
                return

            Clock.schedule_once(self._izinleri_iste, 0.5)
        #Bilgisayarda test ederken çıkacak uyarı
        else:
            self.status_tag.text = (
                "Bu uygulama sadece Android cihazlarda calisir.\n"
                "PC ortaminda servis baslatilamaz."
            )

    def _izinleri_iste(self, dt):
        from android.permissions import Permission, request_permissions

        izin_listesi = [
            Permission.INTERNET,
            Permission.BLUETOOTH_CONNECT,
            Permission.BLUETOOTH_SCAN,
            Permission.ACCESS_FINE_LOCATION,
            Permission.FOREGROUND_SERVICE,
            Permission.POST_NOTIFICATIONS,
        ]

        def izin_sonucu(permissions, results):
            Clock.schedule_once(lambda dt: self._izin_sonucunu_isle(permissions, results))
        #İzinler onaylandığında
        request_permissions(izin_listesi, izin_sonucu)

    def _izin_sonucunu_isle(self, permissions, results):
        missing_permissions = [p for p, r in zip(permissions, results) if not r]
        #İzinler eksik olduğunda
        if not missing_permissions:
            self.status_tag.text = "Tum izinler verildi.\nServis durumu kontrol ediliyor..."
            self._servisi_baslat()
        else:
            shortName = [p.split('.')[-1] for p in missing_permissions]
            self.status_tag.text = (
                "Bazi izinler reddedildi:\n"
                f"{', '.join(shortName)}\n\n"
                "Servis yine de baslatilmaya calisiliyor..."
            )
            self._servisi_baslat()

    def _servis_calisiyor_mu(self):
        try:
            from jnius import autoclass
            Context = autoclass('android.content.Context')
            ActivityManager = autoclass('android.app.ActivityManager')
            
            act_manager = self.activity.getSystemService(Context.ACTIVITY_SERVICE)
            running_services = act_manager.getRunningServices(100)
            
            for i in range(running_services.size()):
                service_info = running_services.get(i)
                if service_info.service.getClassName() == self.target_service_class:
                    return True
            return False
        except Exception:
            return False

    def _servisi_baslat(self):
        if not self.service_class or not self.activity:
            return
        #Servis zaten aktifse
        try:
            if self._servis_calisiyor_mu():
                self.status_tag.text = (
                    "Pil Takip Servisi Zaten Aktif\n\n"
                    "Arka planda çalışmaya devam ediyor."
                )
                return

            # Servisi başlat
            self.service_class.start(self.activity, "")

            self.status_tag.text = (
                "Pil Takip Servisi Aktif Edildi\n\n"
                "Arka planda calisiyor.\n"
                "Durdurmak icin asagidaki butonu kullan."
            )
        #Başlatma başarısız olursa
        except Exception as e:
            self.status_tag.text = f"Servis baslatma hatasi:\n{e}"

    def servisi_durdur(self, instance):
        if not self.activity or not self.target_service_class:
            return

        try:
            # OPTİMİZASYON: Durdurma emrini doğrudan Java Intent ile gönderiyoruz.
            # Bu yöntem p4a'nın stop() sarmalayıcısına göre Android 14+'te çok daha hızlı ve güvenlidir.
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Context = autoclass('android.content.Context')

            intent = Intent()
            intent.setClassName(self.activity.getPackageName(), self.target_service_class)

            # Servisi sistem düzeyinde kesin olarak sonlandırır
            self.activity.stopService(intent)
            self.status_tag.text = "Servis durduruldu."
        except Exception as e:
            # FALLBACK: stopService(Intent) bu cihazda/p4a surumunde basarisiz
            # olursa, p4a'nin kendi statik stop() metodunu deniyoruz. Iki
            # yontem de Android'e ayni komutu farkli API katmanlarindan
            # iletir; biri calismazsa diger devreye girsin diye burada
            # tutuyoruz.
            try:
                if self.service_class:
                    self.service_class.stop(self.activity)
                    self.status_tag.text = "Servis durduruldu."
                else:
                    self.status_tag.text = f"Servis durdurma hatasi:\n{e}"
            except Exception as fallback_e:
                self.status_tag.text = (
                    f"Servis durdurma hatasi:\n{e}\n\n"
                    f"Fallback da basarisiz:\n{fallback_e}"
                )


if __name__ == "__main__":
    PilUygulamasi().run()
