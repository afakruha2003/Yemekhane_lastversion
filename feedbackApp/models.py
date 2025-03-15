from django.contrib.auth.models import AbstractUser
from django.db import models
import pandas as pd
import os
from django.conf import settings

# Kullanıcı Tipleri
KULLANICI_TIPI_CHOICES = [
    ('ogrenci', 'Öğrenci'),
    ('yurt_yetkilisi', 'Yurt Yetkilisi'),
    ('sehir_yetkilisi', 'Şehir Yetkilisi'),
    ('turkiye_yetkilisi', 'Türkiye Yetkilisi'),
]

# Öğün Seçenekleri
OGUN_CHOICES = [
    ('kahvaltı', 'Kahvaltı'),
    ('akşam', 'Akşam'),
]

KAPSAM_CHOICES = [
    ('yurt', 'yurt'),
    ('sehir', 'şehir'),
    ('turkiye', 'türkiye'),
]

OZET_TUR_CHOICES = [
    ('gunluk', 'gunluk'),
    ('haftalık', 'haftalık'),
    ('aylık', 'aylık'),
]
# Şehir Modeli
class Sehir(models.Model):
    isim = models.CharField(max_length=100)
   
    def __str__(self):
        return self.isim
    
# Yurt Modeli
class Yurt(models.Model):
    isim = models.CharField(max_length=100)
    sehir = models.ForeignKey(Sehir, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.isim} - {self.sehir.isim}"

class CustomUser(AbstractUser):
    kullanici_tipi = models.CharField(max_length=20, choices=KULLANICI_TIPI_CHOICES)
    sehir = models.ForeignKey(Sehir, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    yurt = models.ForeignKey(Yurt, on_delete=models.SET_NULL, null=True, blank=True, related_name='yurt')
    
    # Çakışmayı engellemek için related_name parametreleri ekliyoruz
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='customuser_groups',  # Çakışmayı engellemek için
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='customuser_permissions',  # Çakışmayı engellemek için
        blank=True
    )

    def __str__(self):
        return self.username  # veya 'self.email' gibi farklı bir temsil kullanabilirsiniz

# Yemek Modeli
class Yemek(models.Model):
    isim = models.CharField(max_length=100)
    ogun = models.CharField(max_length=20, choices=OGUN_CHOICES)
    sehir = models.ForeignKey(Sehir, on_delete=models.CASCADE, null=True, blank=True)
    tarih = models.DateField()

    def __str__(self):
        return f"{self.isim} ({self.get_ogun_display()}) - {self.yurt.isim} ({self.tarih})"

# Yemek Listesi Modeli
class YemekListesi(models.Model):
    tarih = models.DateField()
    il = models.ForeignKey(Sehir, on_delete=models.CASCADE)
    ogun = models.CharField(max_length=20, choices=OGUN_CHOICES)
    yemek_1 = models.CharField(max_length=100, blank=True, null=True)
    yemek_2 = models.CharField(max_length=100, blank=True, null=True)
    yemek_3 = models.CharField(max_length=100, blank=True, null=True)
    yemek_4 = models.CharField(max_length=100, blank=True, null=True)
    yemek_5 = models.CharField(max_length=100, blank=True, null=True)
    yemek_6 = models.CharField(max_length=100, blank=True, null=True)
    yemek_7 = models.CharField(max_length=100, blank=True, null=True)
    yemek_8 = models.CharField(max_length=100, blank=True, null=True)
    yemek_9 = models.CharField(max_length=100, blank=True, null=True)
    yemek_10 = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.il.isim} - {self.tarih} - {self.get_ogun_display()}"

# Yemek Listesi Güncelleme Modeli
class YemekListesiGuncelleme(models.Model):
    sehir = models.ForeignKey(Sehir, on_delete=models.CASCADE)
    excel_dosyasi = models.FileField(upload_to="yemek_listeleri/")
    yuklenme_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sehir.isim} için yemek listesi ({self.yuklenme_tarihi})"

    def process_excel(self):
        if not self.excel_dosyasi:
            return

        excel_path = self.excel_dosyasi.path
        df = pd.read_excel(excel_path)

        required_columns = {"tarih", "ogun", "yemek_1", "yemek_2", "yemek_3", "yemek_4", "yemek_5","yemek_6", "yemek_7", "yemek_8", "yemek_9", "yemek_10"}
        if not required_columns.issubset(df.columns):
            raise ValueError("Excel dosyası uygun formatta değil. Gerekli sütunlar eksik!")

        YemekListesi.objects.filter(il=self.sehir).delete()

        yemek_listesi = []
        for _, row in df.iterrows():
            yemek_listesi.append(
                YemekListesi(
                    tarih=row["tarih"],
                    il=self.sehir,
                    ogun=row["ogun"],
                    yemek_1=row.get("yemek_1"),
                    yemek_2=row.get("yemek_2"),
                    yemek_3=row.get("yemek_3"),
                    yemek_4=row.get("yemek_4"),
                    yemek_5=row.get("yemek_5"),
                    yemek_6=row.get("yemek_6"),
                    yemek_7=row.get("yemek_7"),
                    yemek_8=row.get("yemek_8"),
                    yemek_9=row.get("yemek_9"),
                    yemek_10=row.get("yemek_10"),
                )
            )

        YemekListesi.objects.bulk_create(yemek_listesi)
        os.remove(excel_path)

# Yemek Yorumu Modeli
class YemekYorumu(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    yemek = models.TextField()
    yorum = models.TextField()
    yorum_puanı = models.CharField(max_length=10,
        choices=[
            (0, '0 - Anlamsız'),
            (1, '1 - Yenilmez'),
            (2, '2 - Kötü'),
            (3, '3 - Orta'),
            (4, '4 - İyi'),
            (5, '5 - Mükemmel'),
        ], default="-1")
    tarih = models.DateTimeField(auto_now_add=True)
    yurt = models.TextField(default="yurtsuz")
    sehir_id = models.ForeignKey(Sehir, on_delete=models.CASCADE, default=1)
    foto = models.ImageField(upload_to="yemek_foto/", null=True, blank=True)
    foto_betimleme = models.TextField(null=True, blank=True)
    yorum_onem = models.CharField(max_length=10,
        choices=[
            (0, '0 - Anlamsız'),
            (1, '1 - Düşük'),
            (2, '2 - Önemsiz'),
            (3, '3 - Orta'),
            (4, '4 - Önemli'),
            (5, '5 - Kritik'),
        ], default="0")

    def __str__(self):
        return f"{self.user} - {self.yemek} - {self.yorum_puanı}"


class Ozet(models.Model):
    olusturma_tarih = models.DateTimeField(auto_now_add=True)
    ozet_tarih = models.DateField()  # Tarih alanı için DateField kullanıldı
    ozet_tur = models.CharField(max_length=100, choices=OZET_TUR_CHOICES)
    kapsam = models.CharField(max_length=100, choices=KAPSAM_CHOICES)  # CharField olarak değiştirildi
    yurt = models.CharField(max_length=255,null=True, blank=True)
    sehir = models.ForeignKey(Sehir, on_delete=models.CASCADE,null=True, blank=True)
    ozet = models.TextField()

    def __str__(self):
        return f"{self.ozet_tarih} - {self.yurt}"