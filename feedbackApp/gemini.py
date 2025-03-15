from datetime import datetime, timedelta,date
import json
from google import genai
from google.genai import types
from django.utils.timezone import now
import PIL.Image

from feedbackApp.models import Ozet, Sehir, YemekYorumu, Yurt

client = genai.Client(api_key="AIzaSyAibsTR_wCwEp6i4QSChrXIfs2C1Gsvmnw")

bugun = datetime.today().date()
dun = bugun  - timedelta(days=1)
son_1_ay = bugun - timedelta(days=30)
son_7_gun = bugun - timedelta(days=7)



def yurt_yorum_ozetle():
    sys_instruct=f"""
   Sana KYK yurtlarındaki yemeklere yapılan öğrenci yorumları varsa fotoğraf betimlemesi ve risk puanı verilecektir. Sana verilen yorumlardan bir özet çıkar ve öğrencilerin yemekler hakkında görüşlerini ve sorunlarını anlat.
   Özetin detaylı olmasını istiyoruz ancak gereksiz tekrarlar içermemelidir. Özellikle öğrencilerin en sık dile getirdiği tekrarlanan sorunları belirle.
    Önemli: Fotoğraflı yorumlar risk derecesine göre ağırlıklı olarak değerlendirilmiştir. Yani fiziksel risk (kıl, taş, bozulmuş yemek, hijyen sorunları) içeren yorumlar daha fazla öne çıkarılmıştır. risk oranı yüksek olanlardan özetinde bahsettiğine emin ol.
   Sana verilecek yemek formatı:
   "Yemek: Yorum."
   ya da
  "Yemek: Yorum. (fotoğraf betimlemesi) Risk:"
   şeklinde olucaktır.
   
   Çıktı Formatı:
   
   Genel Özet:
   
   Tekrarlanan Sorunlar:

    """
    yurtlar = Yurt.objects.filter(isim__in=YemekYorumu.objects.filter(tarih__date=dun).values_list('yurt', flat=True).distinct())

    for yurt in yurtlar:
        sehir = yurt.sehir  # Yurdun şehrini al

        yorumlar = YemekYorumu.objects.filter(yurt=yurt.isim, tarih__date= dun).exclude(yorum_puanı=0)
        yorum_listesi = "\n".join([
        f"{yorum.yemek}: {yorum.yorum}" + (f"({yorum.foto_betimleme}) Risk:{yorum.yorum_onem}" if yorum.foto_betimleme else "")
        for yorum in yorumlar])

        if not yorumlar.exists():
            print("Kriterlere uyan yorum yoktur.")
            continue

        if not Ozet.objects.filter(ozet_tarih=dun, yurt=yurt.isim).exists():
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=sys_instruct),
                    contents=[yorum_listesi])

                yeni_ozet = Ozet.objects.create(
                    ozet_tarih=dun,
                    olusturma_tarih=bugun,
                    ozet_tur="gunluk",
                    kapsam="yurt",
                    yurt=yurt.isim,
                    sehir=sehir,
                    ozet=response.text
                )
                print(f"{yurt.isim} yurdu için günlük özet oluşturuldu ve kaydedildi.")

            except Exception as e:
                print(f"{yurt.isim} yurdu için günlük özet oluşturulurken bir hata oluştu: {e}")

def yurt_yorum_ozetle_haftalik():
    sys_instruct=f"""
    Sana bir haftalık bir yurdun yemek yorum özetleri verilmiştir. Bu özetleri dikkatlice inceleyerek, hafta boyunca devamlılık gösteren sorunları belirle.

    Özellikle tekrar eden problemleri vurgula ve bu hafta boyunca olumlu ya da olumsuz yönde bir değişim olup olmadığını analiz et. Hijyen, yemek kalitesi, porsiyon miktarı ve öğrenci memnuniyeti gibi konulara odaklanarak bir ilerleme özeti hazırla.

    Çıktın şu formatta olmalıdır:

    Genel Gidişat:

    (Hafta boyunca yemeklerin genel durumu, öğrencilerin memnuniyeti veya memnuniyetsizliği hakkında kısa bir özet)
    Devamlılık Gösteren Sorunlar:

    (Tekrarlayan veya kötüleşen sorunlar listelenmelidir.)
    Gelişmeler:

    (Önceki günlere kıyasla düzelme gösteren veya iyileşme yönünde adım atılan konular belirtilmelidir.)
    """
    yurtlar = Yurt.objects.filter(isim__in=YemekYorumu.objects.filter(tarih__date__gte=son_7_gun).values_list('yurt', flat=True).distinct())

    for yurt in yurtlar:
        sehir = yurt.sehir  

        ozetler = Ozet.objects.filter(ozet_tarih__gte=son_7_gun, ozet_tarih__lte=bugun, kapsam= "yurt", ozet_tur="gunluk",yurt=yurt.isim).order_by('ozet_tarih')
        ozet_listesi = "\n".join([
        f"Tarih: {ozet.ozet_tarih} - Özet: {ozet.ozet}"
        for ozet in ozetler
        ])


        if not ozetler.exists():
            print("Kriterlere uyan özet bulunamadı.")
            continue

        if not Ozet.objects.filter(ozet_tarih=dun, yurt=yurt.isim, ozet_tur="haftalık").exists():
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=sys_instruct),
                    contents=[ozet_listesi])

                yeni_ozet = Ozet.objects.create(
                    ozet_tarih=dun,
                    olusturma_tarih=bugun,
                    ozet_tur="haftalık",
                    kapsam="yurt",
                    yurt=yurt.isim,  # Doğru Yurt nesnesini ata
                    sehir=sehir,
                    ozet=response.text
                )
                print(f"{yurt.isim} yurdu için haftalık özet oluşturuldu ve kaydedildi.")

            except Exception as e:
                print(f"{yurt.isim} yurdu için haftalık özet oluşturulurken bir hata oluştu: {e}")

def yurt_yorum_ozetle_aylik():
    sys_instruct=f"""
    Sana dört haftalık bir yurdun yemek yorum özetleri verilmiştir. Bu özetleri dikkatlice inceleyerek, ay boyunca devamlılık gösteren sorunları belirle.

    Özellikle tekrar eden problemleri vurgula ve bu ay boyunca olumlu ya da olumsuz yönde bir değişim olup olmadığını analiz et. Hijyen, yemek kalitesi, porsiyon miktarı ve öğrenci memnuniyeti gibi konulara odaklanarak bir ilerleme özeti hazırla.

    Çıktın şu formatta olmalıdır:

    Genel Gidişat:

    (Ay boyunca yemeklerin genel durumu, öğrencilerin memnuniyeti veya memnuniyetsizliği hakkında kısa bir özet)
    Devamlılık Gösteren Sorunlar:

    (Tekrarlayan veya kötüleşen sorunlar listelenmelidir.)
    Gelişmeler:

    (Önceki haftalara kıyasla düzelme gösteren veya iyileşme yönünde adım atılan konular belirtilmelidir.)
    """
    yurtlar = Yurt.objects.filter(isim__in=YemekYorumu.objects.filter(tarih__date__gte=son_1_ay).values_list('yurt', flat=True).distinct())

    for yurt in yurtlar:
        sehir = yurt.sehir  # Yurdun şehrini al

        ozetler = Ozet.objects.filter(ozet_tarih__gte=son_1_ay, ozet_tarih__lte=bugun,kapsam= "yurt", ozet_tur="haftalık",yurt=yurt.isim).order_by('ozet_tarih')
        ozet_listesi = "\n".join([
        f"Tarih: {ozet.ozet_tarih} - Özet: {ozet.ozet}"
        for ozet in ozetler
        ])


        if not ozetler.exists():
            print("Kriterlere uyan özet bulunamadı.")
            continue

        if not Ozet.objects.filter(ozet_tarih=dun, yurt=yurt.isim, kapsam= "yurt", ozet_tur="aylık").exists():
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=sys_instruct),
                    contents=[ozet_listesi])

                yeni_ozet = Ozet.objects.create(
                    ozet_tarih=dun,
                    olusturma_tarih=bugun,
                    ozet_tur="aylık",
                    kapsam="yurt",
                    yurt=yurt.isim,  # Doğru Yurt nesnesini ata
                    sehir=sehir,
                    ozet=response.text
                )
                print(f"{yurt.isim} yurdu için haftalık özet oluşturuldu ve kaydedildi.")

            except Exception as e:
                print(f"{yurt.isim} yurdu için haftalık özet oluşturulurken bir hata oluştu: {e}")

def sehir_yorum_ozetle():

    sys_instruct=f"""
   Sana KYK yurtlarındaki yemeklere yapılan öğrenci yorumları varsa fotoğraf betimlemesi ve risk puanı verilecektir. Sana verilen yorumlardan bir özet çıkar ve öğrencilerin yemekler hakkında görüşlerini ve sorunlarını anlat.
   Özetin detaylı olmasını istiyoruz ancak gereksiz tekrarlar içermemelidir. Özellikle öğrencilerin en sık dile getirdiği tekrarlanan sorunları belirle.
    Önemli: Fotoğraflı yorumlar risk derecesine göre ağırlıklı olarak değerlendirilmiştir. Yani fiziksel risk (kıl, taş, bozulmuş yemek, hijyen sorunları) içeren yorumlar daha fazla öne çıkarılmıştır. risk oranı yüksek olanlardan özetinde bahsettiğine emin ol.
   Sana verilecek yemek formatı:
   "Yemek: Yorum."
   ya da
  "Yemek: Yorum. (fotoğraf betimlemesi) Risk:"
   şeklinde olucaktır.
   
   Çıktı Formatı:
   
   Genel Özet:
   
   Tekrarlanan Sorunlar:

    """
    sehirler = Sehir.objects.filter(id__in=YemekYorumu.objects.filter(tarih__date=dun).values_list('sehir_id', flat=True).distinct())

    for sehir in sehirler:

        yorumlar = YemekYorumu.objects.filter(sehir_id=sehir, tarih__date=dun).exclude(yorum_puanı__in=["0"])
        yorum_listesi = "\n".join([
        f"{yorum.yemek}: {yorum.yorum}" + (f"({yorum.foto_betimleme}) Risk:{yorum.yorum_onem}" if yorum.foto_betimleme else "")
        for yorum in yorumlar])
        print(yorum_listesi)

        if not yorumlar.exists():
            continue
        
        if Ozet.objects.filter(ozet_tarih=dun, sehir=sehir, kapsam="sehir").exists():
            continue
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruct),
                contents=[yorum_listesi])
            yeni_ozet = Ozet.objects.create(
                ozet_tarih=dun,
                olusturma_tarih=bugun,
                ozet_tur="gunluk",
                kapsam="sehir",
                sehir=sehir,
                ozet=response.text
            )
            print(f"{sehir} için özet oluşturuldu ve kaydedildi.")
        except Exception as e:
            print(f"{sehir} için özet oluşturulurken bir hata oluştu: {e}")

def sehir_yorum_ozetle_haftalik():
    sys_instruct=f"""
    Sana bir haftalık bir yurdun yemek yorum özetleri verilmiştir. Bu özetleri dikkatlice inceleyerek, hafta boyunca devamlılık gösteren sorunları belirle.

    Özellikle tekrar eden problemleri vurgula ve bu hafta boyunca olumlu ya da olumsuz yönde bir değişim olup olmadığını analiz et. Hijyen, yemek kalitesi, porsiyon miktarı ve öğrenci memnuniyeti gibi konulara odaklanarak bir ilerleme özeti hazırla.

    Çıktın şu formatta olmalıdır:

    Genel Gidişat:

    (Hafta boyunca yemeklerin genel durumu, öğrencilerin memnuniyeti veya memnuniyetsizliği hakkında kısa bir özet)
    Devamlılık Gösteren Sorunlar:

    (Tekrarlayan veya kötüleşen sorunlar listelenmelidir.)
    Gelişmeler:

    (Önceki günlere kıyasla düzelme gösteren veya iyileşme yönünde adım atılan konular belirtilmelidir.)
    """
    
    sehirler = Sehir.objects.filter(id__in=YemekYorumu.objects.filter(tarih__date__gte=son_7_gun).values_list('sehir_id', flat=True).distinct())

    for sehir in sehirler:

        ozetler = Ozet.objects.filter(ozet_tarih__gte=son_7_gun, ozet_tarih__lte=bugun, kapsam= "sehir", ozet_tur="gunluk",sehir=sehir).order_by('ozet_tarih')
        ozet_listesi = "\n".join([
        f"Tarih: {ozet.ozet_tarih} - Özet: {ozet.ozet}"
        for ozet in ozetler
        ])

        if not ozetler.exists():
            print("Kriterlere uyan özet bulunamadı.")
            continue
        
        if Ozet.objects.filter(ozet_tarih__gte=son_7_gun, sehir=sehir, kapsam="sehir",ozet_tur="haftalık").exists():
            continue
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruct),
                contents=[ozet_listesi])
            yeni_ozet = Ozet.objects.create(
                ozet_tarih=dun,
                olusturma_tarih=bugun,
                ozet_tur="haftalık",
                kapsam="sehir",
                sehir=sehir,
                ozet=response.text
            )
            print(f"{sehir} için özet oluşturuldu ve kaydedildi.")
        except Exception as e:
            print(f"{sehir} için özet oluşturulurken bir hata oluştu: {e}")

def sehir_yorum_ozetle_aylik():
    sys_instruct=f"""
    Sana bir haftalık bir yurdun yemek yorum özetleri verilmiştir. Bu özetleri dikkatlice inceleyerek, hafta boyunca devamlılık gösteren sorunları belirle.

    Özellikle tekrar eden problemleri vurgula ve bu hafta boyunca olumlu ya da olumsuz yönde bir değişim olup olmadığını analiz et. Hijyen, yemek kalitesi, porsiyon miktarı ve öğrenci memnuniyeti gibi konulara odaklanarak bir ilerleme özeti hazırla.

    Çıktın şu formatta olmalıdır:

    Genel Gidişat:

    (Hafta boyunca yemeklerin genel durumu, öğrencilerin memnuniyeti veya memnuniyetsizliği hakkında kısa bir özet)
    Devamlılık Gösteren Sorunlar:

    (Tekrarlayan veya kötüleşen sorunlar listelenmelidir.)
    Gelişmeler:

    (Önceki günlere kıyasla düzelme gösteren veya iyileşme yönünde adım atılan konular belirtilmelidir.)
    """
    sehirler = Sehir.objects.filter(id__in=YemekYorumu.objects.filter(tarih__date__gte=son_1_ay).values_list('sehir_id', flat=True).distinct())

    for sehir in sehirler:

        ozetler = Ozet.objects.filter(ozet_tarih__gte=son_1_ay, ozet_tarih__lte=bugun, kapsam= "haftalık",sehir=sehir,).order_by('ozet_tarih')
        ozet_listesi = "\n".join([
        f"Tarih: {ozet.ozet_tarih} - Özet: {ozet.ozet}"
        for ozet in ozetler
        ])

        if not ozetler.exists():
            print("Kriterlere uyan özet bulunamadı.")
            continue
        
        if Ozet.objects.filter(ozet_tarih__gte=son_1_ay, sehir=sehir, kapsam="sehir",ozet_tur="haftalık").exists():
            continue
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruct),
                contents=[ozet_listesi])
            yeni_ozet = Ozet.objects.create(
                ozet_tarih=dun,
                olusturma_tarih=bugun,
                ozet_tur="aylık",
                kapsam="sehir",
                sehir=sehir,
                ozet=response.text
            )
            print(f"{sehir} için özet oluşturuldu ve kaydedildi.")
        except Exception as e:
            print(f"{sehir} için özet oluşturulurken bir hata oluştu: {e}")

def turkiye_yorum_ozetle():

    sys_instruct=f"""
   Sana KYK yurtlarındaki yemeklere yapılan öğrenci yorumları varsa fotoğraf betimlemesi ve risk puanı verilecektir. Sana verilen yorumlardan bir özet çıkar ve öğrencilerin yemekler hakkında görüşlerini ve sorunlarını anlat.
   Özetin detaylı olmasını istiyoruz ancak gereksiz tekrarlar içermemelidir. Özellikle öğrencilerin en sık dile getirdiği tekrarlanan sorunları belirle.
    Önemli: Fotoğraflı yorumlar risk derecesine göre ağırlıklı olarak değerlendirilmiştir. Yani fiziksel risk (kıl, taş, bozulmuş yemek, hijyen sorunları) içeren yorumlar daha fazla öne çıkarılmıştır. risk oranı yüksek olanlardan özetinde bahsettiğine emin ol.
   Sana verilecek yemek formatı:
   "Yemek: Yorum."
   ya da
  "Yemek: Yorum. (fotoğraf betimlemesi) Risk:"
   şeklinde olucaktır.
   
   Çıktı Formatı:
   
   Genel Özet:
   
   Tekrarlanan Sorunlar:

    """

    yorumlar = YemekYorumu.objects.filter(tarih__date=dun).exclude(yorum_puanı="0")
    yorum_listesi = "\n".join([
    f"{yorum.yemek}: {yorum.yorum}" + (f"({yorum.foto_betimleme}) Risk:{yorum.yorum_onem}" if yorum.foto_betimleme else "")
    for yorum in yorumlar])

    print(yorum_listesi)

    if not yorumlar.exists():
        print("Kriterlere uyan yorum yoktur.")
        return
    
    if Ozet.objects.filter(ozet_tarih=dun, kapsam="turkiye").exists():
        print("Veritabanında zaten bir özet var")
        return
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct),
            contents=[yorum_listesi])
        yeni_ozet = Ozet.objects.create(
            ozet_tarih=dun,
            olusturma_tarih=bugun,
            ozet_tur="gunluk",
            kapsam="turkiye",
            ozet=response.text
        )
        print("Türkiye için özet oluşturuldu ve kaydedildi.")
    except Exception as e:
        print(f"Türkiye için özet oluşturulurken bir hata oluştu: {e}")

def turkiye_yorum_ozetle_haftalik():
    sys_instruct=f"""
    Sana bir haftalık bir yurdun yemek yorum özetleri verilmiştir. Bu özetleri dikkatlice inceleyerek, hafta boyunca devamlılık gösteren sorunları belirle.

    Özellikle tekrar eden problemleri vurgula ve bu hafta boyunca olumlu ya da olumsuz yönde bir değişim olup olmadığını analiz et. Hijyen, yemek kalitesi, porsiyon miktarı ve öğrenci memnuniyeti gibi konulara odaklanarak bir ilerleme özeti hazırla.

    Çıktın şu formatta olmalıdır:

    Genel Gidişat:

    (Hafta boyunca yemeklerin genel durumu, öğrencilerin memnuniyeti veya memnuniyetsizliği hakkında kısa bir özet)
    Devamlılık Gösteren Sorunlar:

    (Tekrarlayan veya kötüleşen sorunlar listelenmelidir.)
    Gelişmeler:

    (Önceki günlere kıyasla düzelme gösteren veya iyileşme yönünde adım atılan konular belirtilmelidir.)
    """

    ozetler = Ozet.objects.filter(ozet_tarih__gte=son_1_ay, ozet_tarih__lte=bugun, kapsam= "turkiye",ozet_tur="gunluk").order_by('ozet_tarih')
    ozet_listesi = "\n".join([
    f"Tarih: {ozet.ozet_tarih} - Özet: {ozet.ozet}"
    for ozet in ozetler
    ])
    if not ozetler.exists():
        print("Kriterlere uyan özet bulunamadı.")
        return
    
    if Ozet.objects.filter(ozet_tarih__gte=son_1_ay, kapsam="turkiye",ozet_tur="haftalık").exists():
        return
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct),
            contents=[ozet_listesi])
        yeni_ozet = Ozet.objects.create(
            ozet_tarih=dun,
            olusturma_tarih=bugun,
            ozet_tur="haftalık",
            kapsam="turkiye",
            ozet=response.text
        )
        print(f"Türkiye için haftalık özet oluşturuldu ve kaydedildi.")
    except Exception as e:
        print(f"Türkiye için özet oluşturulurken bir hata oluştu: {e}")

def turkiye_yorum_ozetle_aylik():
    sys_instruct=f"""
    Sana bir haftalık bir yurdun yemek yorum özetleri verilmiştir. Bu özetleri dikkatlice inceleyerek, hafta boyunca devamlılık gösteren sorunları belirle.

    Özellikle tekrar eden problemleri vurgula ve bu hafta boyunca olumlu ya da olumsuz yönde bir değişim olup olmadığını analiz et. Hijyen, yemek kalitesi, porsiyon miktarı ve öğrenci memnuniyeti gibi konulara odaklanarak bir ilerleme özeti hazırla.

    Çıktın şu formatta olmalıdır:

    Genel Gidişat:

    (Hafta boyunca yemeklerin genel durumu, öğrencilerin memnuniyeti veya memnuniyetsizliği hakkında kısa bir özet)
    Devamlılık Gösteren Sorunlar:

    (Tekrarlayan veya kötüleşen sorunlar listelenmelidir.)
    Gelişmeler:

    (Önceki günlere kıyasla düzelme gösteren veya iyileşme yönünde adım atılan konular belirtilmelidir.)
    """

    ozetler = Ozet.objects.filter(ozet_tarih__gte=son_7_gun, ozet_tarih__lte=bugun, kapsam= "turkiye",ozet_tur="haftalık").order_by('ozet_tarih')
    ozet_listesi = "\n".join([
    f"Tarih: {ozet.ozet_tarih} - Özet: {ozet.ozet}"
    for ozet in ozetler
    ])
    if not ozetler.exists():
        print("Kriterlere uyan özet bulunamadı.")
        return
    
    if Ozet.objects.filter(ozet_tarih__gte=son_7_gun, kapsam="turkiye",ozet_tur="aylık").exists():
        return
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct),
            contents=[ozet_listesi])
        yeni_ozet = Ozet.objects.create(
            ozet_tarih=dun,
            olusturma_tarih=bugun,
            ozet_tur="aylık",
            kapsam="turkiye",
            ozet=response.text
        )
        print(f"Türkiye için aylık özet oluşturuldu ve kaydedildi.")
    except Exception as e:
        print(f"Türkiye için özet oluşturulurken bir hata oluştu: {e}")
    
def goruntu_yorumla():
    sys_instruct=f"""
    Sana bir yemek fotoğrafı, yemek adı ve öğrenci yorumu verilecektir. Görevin, bu bilgileri analiz ederek yemeğin ne kadar tehlikeli veya yenmeye uygun olup olmadığını göre risk derecesini belirle. Değerlendirme yaparken şu adımları izle:

    Fotoğraf Analizi:
    Eğer fotoğraf alakasızsa betimleme ve riski sıfır döndür.
    Fotoğrafta görülen fiziksel kusurları tespit et. (Küf, çiğ kalmış et, aşırı yağlılık, yanıklık, taş/kıl vb. yabancı maddeler)
    Hijyen koşulları hakkında gözlem yap. (Kirli tabak, kötü sunum, hijyenik olmayan ortam)
    Yemeğin genel görünümüne göre sağlığa zarar verme riski olup olmadığını değerlendir.
    Öğrencinin yorumunda belirttiği şikayetlerin fotoğrafta görünür olup olup olmadığını kontrol et.
    Şikayet Türleri:
    Kritik Sağlık Riski (Zehirlenme belirtileri, bozulmuş/kokmuş yemek, çiğ veya iyi pişmemiş gıda, fiziksel zararlı maddeler: taş, plastik, kıl vb.)
    Orta Düzey Risk (Aşırı yağlılık, aşırı tuz, yanık veya lezzetsiz ama zararsız yemek)
    Düşük Risk (Tat, sunum, sıcaklıkla ilgili küçük şikayetler)
    3. Önem Derecesini Belirle (1-5 Arasında):
    5 - Kritik - Yemek sağlık için ciddi risk taşıyor. Zehirlenme, yabancı cisim, çiğ/bozulmuş gıda. Kesinlikle yenmemeli!
    4 - Yüksek - Ciddi hijyen sorunları veya mide rahatsızlığına neden olabilecek durumlar var. Dikkat edilmeli!
    3 - Orta - Yemek teknik olarak yenebilir ama kalitesi düşük. Hafif mide rahatsızlığına yol açabilir.
    2 - Düşük - Küçük lezzet veya sunum sorunları var ama sağlık açısından büyük risk taşımıyor.
    1 - Önemsiz - Sadece kişisel zevke dayalı şikayetler, genel olarak yemek güvenli.

    Çıktıyı Json formatında ver ve jsondan başka hiçbir şey döndürme.
    Örnek JSON:
       "betimleme": "...", "risk": 3
    """
    yorumlar = YemekYorumu.objects.exclude(foto__isnull=True).exclude(foto__exact='').exclude(foto_betimleme__isnull=False)
    if not yorumlar.exists():
        print("Betimlenecek fotoğraf bulunamadı.")
        return
    for yorum in yorumlar:
        image = PIL.Image.open(yorum.foto)
        prompt = "yemek: " + yorum.yemek + "yorum: " + yorum.yorum

        gemini_response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct),
        contents=[prompt, image])

        try:
        # Yanıtı JSON'a çevir
            response = gemini_response.text
            response = response.replace("```json", "").replace("```", "").strip()
            sonuc = json.loads(response)
            betimleme = sonuc.get("betimleme")
            risk = sonuc.get("risk")
            if isinstance(risk, int) and 0 <= risk <= 5:
                # Yorumu güncelle
                yorum.foto_betimleme = betimleme
                yorum.yorum_onem = risk
                yorum.save()
                print(f"Yorum güncellendi: {risk} - {betimleme} ")
            else:
                print(f"Geçersiz puan veya ID döndü: {sonuc}")

        except json.JSONDecodeError:
            print(f"Yanıt JSON formatında değil: {response.text}")
            return "Yanıt JSON formatında değil."
        
    return "fotoğraf betimleme ve risk analizi tamamlandı."

def yorum_puanla():
    sys_instruct=f"""
    Sana verilen yemek yorumlarını aşağıdaki puanlama sistemine göre değerlendir ve bana yalnızca JSON formatında, yorumlara karşılık gelen puanları döndür. Başka hiçbir şey ekleme. 

    0 - Anlamsız

    Yorum, yemekle ilgili değilse veya tamamen alakasızsa.
    Anlam bütünlüğü yoksa ve yorum anlaşılamıyorsa.
    Örnekler:
    "Bugün hava çok güzeldi." (Yemekle ilgisi yok.)
    "asjdhkashdk" (Anlamsız karakter dizisi.)
    "Mavi rengi çok seviyorum."
    1 - Yenilmez

    Yemek o kadar kötü ki yenemeyecek durumda.
    Tadının çok kötü, çiğ, bayat, bozuk veya zehirlenmeye sebep olacak kadar kötü olduğu belirtilmişse.
    Örnekler:
    "Bu yemek bozulmuştu, midem bulandı."
    "Çiğ tavuk verdiler, yiyemedim."
    "Ağzıma attığım gibi tükürdüm, berbat."
    2 - Olumsuz

    Yemek kötü ama yenilebilir seviyede.
    Lezzetsiz, tatsız, yağlı, fazla tuzlu/şekersiz gibi şikayetler içeriyorsa.
    Örnekler:
    "Pilav lapa olmuş, hiç güzel değildi."
    "Çok yağlı ve tatsızdı."
    "Ekmeğin içi bayattı ama yine de yedim."
    3 - Nötr

    Yemek ne iyi ne kötü, ortalama.
    Belirgin bir şikayet veya övgü yok.
    "İdare eder" tarzında yorumlar içeriyorsa.
    Örnekler:
    "Yenilebilir ama çok özel değil."
    "Normal bir yemekti, çok da iyi değildi."
    "Ne çok iyi ne çok kötüydü."
    4 - Olumlu

    Yemek genel olarak beğenilmiş, iyi.
    Lezzetli, güzel pişmiş, dengeli baharatlı veya doyurucu gibi yorumlar varsa.
    Örnekler:
    "Çok güzel olmuş, severek yedim."
    "Pilav tam kıvamında, lezzetliydi."
    "Gayet iyi, keşke her zaman böyle olsa."
    5 - Mükemmel

    Yemek çok beğenilmiş, olağanüstü.
    "Hayatımda yediğim en iyi yemek", "Şefin ellerine sağlık" gibi övgüler içeriyorsa.
    Örnekler:
    "Mükemmeldi, her gün olsa yerim!"
    "Bu kadar güzel bir çorba içmemiştim."
    "Şahane! Lokanta kalitesinde bir yemekti."

    Örnek JSON:
       yorumlar:  ["id": 1, "puan": 3]
    """

    yorumlar = YemekYorumu.objects.filter(yorum_puanı = -1)

    if not yorumlar.exists():
      print("Güncellenecek yorum bulunamadı.")
      return

    # Gönderilecek yorum listesini oluştur
    yorum_listesi = [{"id": x.id, "yemek": x.yemek, "yorum": x.yorum} for x in yorumlar]

    prompt = json.dumps({"yorumlar": yorum_listesi}, ensure_ascii=False)

    gemini_response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=sys_instruct),
    contents=[prompt])


    try:
        # Yanıtı JSON'a çevir
        response = gemini_response.text
        response = response.replace("```json", "").replace("```", "").strip()
        puanlama_sonuclari = json.loads(response)

        if "yorumlar" not in puanlama_sonuclari:
            print(f"Beklenen formatta yanıt alınmadı: {response}")
            return f"Beklenen formatta yanıt alınmadı."

        for sonuc in puanlama_sonuclari["yorumlar"]:
            yorum_id = sonuc.get("id")
            puan = sonuc.get("puan")

            if isinstance(yorum_id, int) and isinstance(puan, int) and 0 <= puan <= 5:
                # Yorumu güncelle
                YemekYorumu.objects.filter(id=yorum_id).update(yorum_puanı=puan)
                print(f"Yorum ID {yorum_id} için puan güncellendi: {puan}")
            else:
                print(f"Geçersiz puan veya ID döndü: {sonuc}")

    except json.JSONDecodeError:
        print(f"Yanıt JSON formatında değil: {response}")
        return "Yanıt JSON formatında değil."

    return "Yorum puanlama tamamlandı."

def do_everything():
    goruntu_yorumla()
    yorum_puanla()
    yurt_yorum_ozetle()
    sehir_yorum_ozetle()
    turkiye_yorum_ozetle()


