from django.contrib import admin
from .models import CustomUser, Sehir, Yurt, Yemek, YemekListesi, YemekListesiGuncelleme, YemekYorumu

# CustomUser Modeli için Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "kullanici_tipi", "sehir")  
    list_filter = ("kullanici_tipi", "sehir")  
    search_fields = ("username", "email")



# Yurt Modeli için Admin
@admin.register(Yurt)
class YurtAdmin(admin.ModelAdmin):
    list_display = ("isim", "sehir")
    list_filter = ("sehir",)
    search_fields = ("isim",)

# Yemek Modeli için Admin
@admin.register(Yemek)
class YemekAdmin(admin.ModelAdmin):
    list_display = ("isim", "ogun", "sehir", "tarih")
    list_filter = ("ogun", "sehir", "tarih")
    search_fields = ("isim",)

# Yemek Listesi Modeli için Admin
@admin.register(YemekListesi)
class YemekListesiAdmin(admin.ModelAdmin):
    list_display = ("il", "tarih", "ogun", "yemek_1", "yemek_2", "yemek_3", "yemek_4", "yemek_5")
    list_filter = ("il", "tarih", "ogun")
    search_fields = ("il__isim",)

# Yemek Listesi Güncelleme Modeli için Admin
@admin.register(YemekListesiGuncelleme)
class YemekListesiGuncellemeAdmin(admin.ModelAdmin):
    list_display = ("sehir", "excel_dosyasi", "yuklenme_tarihi")
    list_filter = ("sehir", "yuklenme_tarihi")

# Yemek Yorumu Modeli için Admin
@admin.register(YemekYorumu)
class YemekYorumuAdmin(admin.ModelAdmin):
    list_display = ("user", "yemek", "yorum_puanı", "tarih")
    list_filter = ("yorum_puanı", "tarih")
    search_fields = ("user_username", "yemek_isim")