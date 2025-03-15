from django.db.models import Avg

from feedbackApp import models
from feedbackApp.models import YemekYorumu


def yemek_istatistik(user, tarih=None):
    sehir = user.sehir
    yurt = user.yurt.isim
    if tarih is None:
        ortalama_puanlar = YemekYorumu.objects.filter(yurt = yurt).exclude(yorum_puanı="-1").exclude(yorum_puanı="0").values("yemek").annotate(
            ortalama_puan=Avg("yorum_puanı")  # Yemeklerin ortalama puanını hesaplıyoruz
        )
        return ortalama_puanlar
    else:
        ortalama_puanlar = YemekYorumu.objects.filter(sehir_id = sehir, tarih = tarih,yurt = yurt).exclude(yorum_puanı="-1").exclude(yorum_puanı="0").values("yemek").annotate(
        ortalama_puan=Avg("yorum_puanı")  # Yemeklerin ortalama puanını hesaplıyoruz
        )
        return ortalama_puanlar


def yurt_istatistik(user, tarih=None):
    sehir = user.sehir
    if tarih is None:
        ortalama_puanlar = YemekYorumu.objects.filter(sehir_id = sehir).exclude(yorum_puanı="-1").exclude(yorum_puanı="0").values("yurt").annotate(
            ortalama_puan=Avg("yorum_puanı")  # Yemeklerin ortalama puanını hesaplıyoruz
        )
        return ortalama_puanlar
    else:
        ortalama_puanlar = YemekYorumu.objects.filter(sehir_id = sehir, tarih = tarih).exclude(yorum_puanı="-1").exclude(yorum_puanı="0").values("yurt").annotate(
        ortalama_puan=Avg("yorum_puanı")  # Yemeklerin ortalama puanını hesaplıyoruz
        )
        return ortalama_puanlar
    
def sehir_istatistik():
    # Yorum puanı 0 ve -1 olanları exclude edip, yurt ve şehire göre gruplandırıyoruz
    ortalama_puanlar = YemekYorumu.objects.exclude(yorum_puanı="-1").exclude(yorum_puanı="0").values("sehir_id").annotate(
        ortalama_puan=Avg("yorum_puanı")  # Yemeklerin ortalama puanını hesaplıyoruz
    )

    return ortalama_puanlar

