from datetime import datetime, timedelta,date
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout,get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.http import HttpResponse
from django.views import View
from .statistics import sehir_istatistik, yurt_istatistik
import google.generativeai as genai
import markdown
import markupsafe
from feedbackApp.gemini import do_everything, sehir_yorum_ozetle, turkiye_yorum_ozetle, yorum_puanla, yurt_yorum_ozetle
from feedbackApp.statistics import sehir_istatistik, yemek_istatistik
from .models import Ozet, YemekYorumu, CustomUser,YemekListesiGuncelleme, Sehir, Yurt, Yemek,YemekListesi
from .forms import LoginForm, RegisterForm,YemekListesiModelForm,YemekListesiSilForm
import pandas as pd
from textblob import TextBlob
from itertools import groupby
from feedbackApp import models
from collections import Counter
import os
import io

User = get_user_model()

# 📌 Yorum Ekleme Fonksiyonu
@login_required
def yemek_yorumla(request):
    today = datetime.today().date()
    current_hour = datetime.now().hour
    user_city = request.user.sehir_id if request.user.is_authenticated else None
    
    if 6 <= current_hour < 13:
        ogun = "kahvaltı"
    elif 16 <= current_hour < 24:
        ogun = "Akşam"
    else:
        return render(request, 'not_available.html')

    yemek_kaydi = YemekListesi.objects.filter(tarih=today, ogun=ogun, il_id=user_city).first()

    yemekler = []
    
    if yemek_kaydi:
        yemekler = [
            yemek_kaydi.yemek_1, yemek_kaydi.yemek_2, yemek_kaydi.yemek_3, yemek_kaydi.yemek_4,
            yemek_kaydi.yemek_5, yemek_kaydi.yemek_6, yemek_kaydi.yemek_7, yemek_kaydi.yemek_8,yemek_kaydi.yemek_9, yemek_kaydi.yemek_10
        ]
        # Boş olan yemekleri listeden çıkar (NULL değerleri önlemek için)
        yemekler = [yemek for yemek in yemekler if yemek]

    if not yemek_kaydi:
        messages.warning(request, "Bugün için yemek listesi bulunmamaktadır.")
       

    if request.method == "POST":
        yemekler = request.POST.getlist("yemek_isim")  # Tüm yemek isimlerini alın
        yorumlar = request.POST.getlist("yorum")  # Tüm yorumları alın

        # Yeni: Kullanıcının yurdu ve şehri
        yurt = request.user.yurt.isim if hasattr(request.user, 'yurt') else "yurtsuz"
        sehir_id = request.user.sehir_id
        sehir = Sehir.objects.filter(id=sehir_id).first()
        fotograflar = [request.FILES.get(f"foto_{i+1}") for i in range(len(yemekler))]

        # Yorumları ve puanları tek tek işle
        for i, yemek_isim in enumerate(yemekler):
            yorum_metni = yorumlar[i]
            yorum_puanı = -1
            fotoğraf = fotograflar[i] if i < len(fotograflar) else None  # Fotoğraf varsa al


            if not yorum_metni.strip():  # Boşlukları temizleyip kontrol et
              continue

            # Veritabanına kaydet
            try:
                YemekYorumu.objects.create(
                    user=request.user,
                    yemek=yemek_isim,  # Doğru Yemek nesnesini kullan
                    yorum=yorum_metni,
                    yorum_puanı=yorum_puanı,
                    yurt=yurt,
                    tarih=datetime.now(),
                    sehir_id=sehir,
                    foto=fotoğraf 
                )
            except Exception as e:
                messages.error(request, f"{yemek_isim} için yorum kaydedilirken bir hata oluştu: {e}")
                return render(request, "yemek-yorumla.html")
        messages.success(request, "Yorumlarınız başarıyla kaydedildi!")
        return redirect("anasayfa")

    return render(request, "yemek-yorumla.html", {"yemekler": yemekler, "bugun_tarih": today})

# 📌 Şehir Bazlı Yorum Analizi Dashboard
@login_required
def sehir_dashboard(request):
    kullanici_tipi = request.user.kullanici_tipi 
    kullanici_yurdu = request.user.yurt.isim

    if request.user.is_authenticated:
        kullanici_tipi = request.user.kullanici_tipi
        if kullanici_tipi == 'ogrenci':
            template_name = 'anasayfa.html'
        elif kullanici_tipi == 'yurt_yetkilisi':
            
            user_yurt = request.user.yurt.isim
            toplam_ogrenci = 1111
            bugun = now().date()
            bugun_yorum_yapan = YemekYorumu.objects.filter(tarih__date=bugun, yurt = kullanici_yurdu).values("user").distinct().count()
            kahvalti_yapan = 666
            aksam_yiyen = 444

            son_10_yorum = YemekYorumu.objects.order_by("-tarih")[:10]
            gunluk_ozet = Ozet.objects.filter(kapsam="yurt", ozet_tur="gunluk", yurt = user_yurt).order_by('-ozet_tarih').first()
            haftalik_ozet = Ozet.objects.filter(kapsam="yurt", ozet_tur="haftalık", yurt = user_yurt).order_by('-ozet_tarih').first()
            aylik_ozet = Ozet.objects.filter(kapsam="yurt", ozet_tur="aylık", yurt = user_yurt).order_by('-ozet_tarih').first()

            # Eğer None değilse Markdown'a çevir
            if gunluk_ozet:
                gunluk_ozet.ozet = markdown.markdown(gunluk_ozet.ozet)

            if haftalik_ozet:
                haftalik_ozet.ozet = markdown.markdown(haftalik_ozet.ozet)

            if aylik_ozet:
                aylik_ozet.ozet = markdown.markdown(aylik_ozet.ozet)
        
            # Son 10 yorum
            son_10_yorum = YemekYorumu.objects.filter(yurt = kullanici_yurdu).order_by("-tarih")[:10]
        
            # Dünün Yorum Özeti
            dun = bugun - timedelta(days=1)
            dun_yorumlar = YemekYorumu.objects.filter(tarih__date=dun)
            dun_toplam_yorum = dun_yorumlar.count()

            
            ortalama_puanlar = yemek_istatistik(request.user)
            ortalama_puanlar_dun = yemek_istatistik(request.user, dun)
        
            return render(request, "yurt_dashboard.html", {
                
                "ortalama_puanlar": ortalama_puanlar,
                "ortalama_puanlar_dun": ortalama_puanlar_dun,
                "toplam_ogrenci": toplam_ogrenci,
                "bugun_yorum_yapan": bugun_yorum_yapan,
                "kahvalti_yapan": kahvalti_yapan,
                "aksam_yiyen": aksam_yiyen,
                "son_10_yorum": son_10_yorum,
                "dun_toplam_yorum": dun_toplam_yorum,
                "gunluk_ozet": gunluk_ozet,
                "haftalik_ozet": haftalik_ozet,
                "aylik_ozet": aylik_ozet,
                "son_10_yorum": son_10_yorum,
                "yurt": user_yurt
            })
        elif kullanici_tipi == 'sehir_yetkilisi':
            user_sehir = request.user.sehir
            bugun = datetime.today().date()
            dun = bugun  - timedelta(days=1)
            son_10_yorum = YemekYorumu.objects.filter(sehir_id=user_sehir).order_by("-tarih")[:10]
            gunluk_ozet = Ozet.objects.filter(kapsam="sehir", sehir_id=user_sehir, ozet_tur="gunluk").order_by('-ozet_tarih').first()
            haftalik_ozet = Ozet.objects.filter(kapsam="sehir",sehir_id=user_sehir, ozet_tur="haftalık").order_by('-ozet_tarih').first()
            aylik_ozet = Ozet.objects.filter(kapsam="aehir",sehir_id=user_sehir, ozet_tur="aylık").order_by('-ozet_tarih').first()

            # Eğer None değilse Markdown'a çevir
            if gunluk_ozet:
                gunluk_ozet.ozet = markdown.markdown(gunluk_ozet.ozet)

            if haftalik_ozet:
                haftalik_ozet.ozet = markdown.markdown(haftalik_ozet.ozet)

            if aylik_ozet:
                aylik_ozet.ozet = markdown.markdown(aylik_ozet.ozet)
            ortalama_puanlar = yurt_istatistik(request.user)
            ortalama_puanlar_dun = yurt_istatistik(request.user, dun)
            ozetler = Ozet.objects.all() 
            for ozet in ozetler:
                ozet.ozet = markdown.markdown(ozet.ozet)
            return render(request, "sehir_dashboard.html", {
                "ortalama_puanlar": ortalama_puanlar,
                "ortalama_puanlar_dun": ortalama_puanlar_dun,
                "gunluk_ozet": gunluk_ozet,
                "haftalik_ozet": haftalik_ozet,
                "aylik_ozet": aylik_ozet,
                "son_10_yorum": son_10_yorum,
                "sehir" : user_sehir
            })
        elif kullanici_tipi == 'turkiye_yetkilisi':
            son_10_yorum = YemekYorumu.objects.order_by("-tarih")[:10]
            gunluk_ozet = Ozet.objects.filter(kapsam="turkiye", ozet_tur="gunluk").order_by('-ozet_tarih').first()
            haftalik_ozet = Ozet.objects.filter(kapsam="turkiye", ozet_tur="haftalık").order_by('-ozet_tarih').first()
            aylik_ozet = Ozet.objects.filter(kapsam="turkiye", ozet_tur="aylık").order_by('-ozet_tarih').first()

            # Eğer None değilse Markdown'a çevir
            if gunluk_ozet:
                gunluk_ozet.ozet = markdown.markdown(gunluk_ozet.ozet)

            if haftalik_ozet:
                haftalik_ozet.ozet = markdown.markdown(haftalik_ozet.ozet)

            if aylik_ozet:
                aylik_ozet.ozet = markdown.markdown(aylik_ozet.ozet)
            ortalama_puanlar = sehir_istatistik()
            ozetler = Ozet.objects.all() 
            for ozet in ozetler:
                ozet.ozet = markdown.markdown(ozet.ozet)
            return render(request, "turkiye_dashboard.html", {
                "ortalama_puanlar": ortalama_puanlar,
                "gunluk_ozet": gunluk_ozet,
                "haftalik_ozet": haftalik_ozet,
                "aylik_ozet": aylik_ozet,
                "son_10_yorum": son_10_yorum,
            })
        else:
            template_name = 'anasayfa.html'  # Giriş yapmamış kullanıcılar için

    return render(request, template_name)


# 📌 Ana Sayfa - O günün yemeklerini gösterir
def anasayfa(request):
    today = datetime.today().date()
    user_city = request.user.sehir_id if request.user.is_authenticated else None
    city  = Sehir.objects.filter(id=user_city).first()
    kahvalti = YemekListesi.objects.filter(tarih=today, ogun="kahvaltı", il=user_city).first()
    aksam = YemekListesi.objects.filter(tarih=today, ogun="Akşam", il=user_city).first()

    first_day = today.replace(day=1)  # Ayın ilk günü
    last_day = today.replace(day=28) + timedelta(days=4)  # En fazla 31 gün
    last_day = last_day.replace(day=1) - timedelta(days=1)  # Ayın son günü
    aylik_yemekler = YemekListesi.objects.filter(tarih__range=[first_day, last_day], il=user_city).order_by("tarih", "ogun")
    grouped_meals = {}
    for key, group in groupby(aylik_yemekler, key=lambda x: x.tarih):
        grouped_meals[key] = list(group)

  
    return render(request, "anasayfa.html", {
        "today": today,
        "city": city,
        "kahvalti": kahvalti,
        "aksam": aksam,
        "grouped_meals": grouped_meals
    })


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True  # Kullanıcıyı aktif hale getiriyoruz
            user.save()
            login(request, user)  # Kullanıcı giriş yapıyor
            messages.success(request, f"Hoş geldiniz, {user.username}! Kayıt başarılı.")
            return redirect("anasayfa")
        else:
            messages.error(request, "Lütfen formu doğru doldurduğunuzdan emin olun!")
        
        return render(request, self.template_name, {"form": form})
    
def get_yurtlar(request):
    sehir_id = request.GET.get("sehir_id")
    if sehir_id:
        yurtlar = Yurt.objects.filter(sehir_id=sehir_id).values("id", "isim")
        return JsonResponse(list(yurtlar), safe=False)
    return JsonResponse([], safe=False)

# 📌 Kullanıcı Girişi
class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("anasayfa")
        messages.error(request, "Kullanıcı adı veya şifre hatalı!")
        return render(request, self.template_name, {"form": form})

# 📌 Kullanıcı Çıkış
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def yemek_listesi_upload(request):
    if request.user.kullanici_tipi != 'sehir_yetkilisi':
        messages.error(request, "Bu işlemi yapmaya yetkiniz yok.")
        return redirect("anasayfa")
    
    if request.method == "POST":
        form = YemekListesiModelForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["excel_file"]
            ext = os.path.splitext(file.name)[1].lower()
            try:
                if ext == '.xlsx':
                    df = pd.read_excel(file)
                elif ext == '.ods':
                    df = pd.read_excel(file, engine='odf')
            except Exception as e:
                messages.error(request, f"Dosya okunurken hata oluştu: {e}")
                return redirect("yemek_guncelle")
            
            # Boş değerleri None yap
            df = df.where(pd.notna(df), None)
            # Tüm hücreleri kontrol edip "non0" yazanları None ile değiştir.
            df = df.applymap(lambda x: None if isinstance(x, str) and x.strip().lower() == "non0" else x)
            
            # Gerekli sütunları kontrol et
            required_columns = [
                'tarih', 'il', 'ogun', 'Yemek_1', 'Yemek_2', 'Yemek_3', 'Yemek_4', 
                'Yemek_5', 'Yemek_6', 'Yemek_7', 'Yemek_8', 'Yemek_9', 'Yemek_10'
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                messages.error(request, f"Dosyada eksik sütunlar var: {', '.join(missing)}")
                return redirect("yemek_guncelle")
            
            today = date.today()
            user_city = request.user.sehir.isim.strip().lower() if request.user.sehir else ""
            
            # Dosyadaki tüm satırların şehir bilgisi, eğer dolu ise, kullanıcının yetkili olduğu şehirle eşleşmeli.
            for index, row in df.iterrows():
                uploaded_city = str(row['il']).strip().lower() if row['il'] is not None else ""
                # Eğer il sütunu boş değilse ve eşleşmiyorsa hata ver.
                if uploaded_city and uploaded_city != user_city:
                    messages.error(request, f"{index + 1}. satırdaki şehir yetkili olduğunuz şehir ile eşleşmiyor. Dosya yüklenmedi.")
                    return redirect("yemek_guncelle")
            
            # Tüm satırları işleyelim.
            for index, row in df.iterrows():
                try:
                    uploaded_date = row['tarih']
                    if not isinstance(uploaded_date, pd.Timestamp):
                        try:
                            uploaded_date = pd.to_datetime(uploaded_date)
                        except Exception:
                            messages.error(request, f"{index + 1}. satırdaki tarih formatı hatalı.")
                            continue  # Hatalı satırı atla
                    uploaded_date = uploaded_date.date()
                    
                    # Geçmiş tarih kontrolü
                    if uploaded_date.year < today.year or (uploaded_date.year == today.year and uploaded_date.month < today.month):
                        messages.warning(request, f"{index + 1}. satırdaki yemek listesi geçmiş bir tarihe ait; eklenmedi.")
                        continue
                    
                    ogun = row['ogun']
                    # Her boş hücre zaten None olacak.
                    yemek_fields = {f"yemek_{i}": row.get(f"Yemek_{i}", None) for i in range(1, 11)}
                    
                    # Aynı tarih, il ve öğün kombinasyonunda kayıt varsa güncelle, yoksa yeni kayıt oluştur.
                    meal_list = YemekListesi.objects.filter(tarih=uploaded_date, il=request.user.sehir, ogun=ogun).first()
                    if meal_list:
                        for field, value in yemek_fields.items():
                            setattr(meal_list, field, value)
                        meal_list.save()
                    else:
                        YemekListesi.objects.create(
                            tarih=uploaded_date,
                            il=request.user.sehir,
                            ogun=ogun,
                            **yemek_fields
                        )
                except Exception as e:
                    messages.error(request, f"{index + 1}. satır eklenirken hata oluştu: {e}")
                    continue
            
            messages.success(request, "Yemek listesi başarıyla güncellendi ve eklendi.")
            return redirect("sehir-dashboard")
        else:
            messages.error(request, "Formda hata var, lütfen tekrar deneyin.")
            return redirect("yemek_guncelle")
    else:
        form = YemekListesiModelForm()
    
    return render(request, "yemek_guncelle.html", {"form": form})



# --- Custom Decorator ---
def sehir_yetkilisi_gerekli(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.kullanici_tipi != "sehir_yetkilisi":
            return HttpResponse("Bu işleme erişim yetkiniz yok!", status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@sehir_yetkilisi_gerekli
def yemek_listesi_panel(request):
    # Get the filter parameters from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    ogun = request.GET.get('ogun')

    # Start with all yemek_listeleri for the user's city
    yemek_listeleri = YemekListesi.objects.filter(il=request.user.sehir)

    # Apply filters for start and end date if they are provided
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        yemek_listeleri = yemek_listeleri.filter(tarih__gte=start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        yemek_listeleri = yemek_listeleri.filter(tarih__lte=end_date)

    # Apply filter for meal type (ogun) if provided
    if ogun:
        yemek_listeleri = yemek_listeleri.filter(ogun=ogun)

    return render(request, 'yemek_listesi_panel.html', {
        'yemek_listeleri': yemek_listeleri
    })

# --- Yemek Listesi Silme ---
@login_required
@sehir_yetkilisi_gerekli
def yemek_listesi_sil(request, liste_id):
    # Sadece kullanıcının şehrine ait yemek listesi silinebilir
    yemek_listesi = get_object_or_404(YemekListesi, id=liste_id, il=request.user.sehir)
    yemek_listesi.delete()
    return redirect("yemek_listesi_panel")

@login_required
@sehir_yetkilisi_gerekli
def yemek_listesi_indir(request):
    # Filtre parametrelerini GET isteğinden al
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    ogun = request.GET.get('ogun')
    
    # Kullanıcının şehri için yemek listelerini al
    yemek_listeleri = YemekListesi.objects.filter(il=request.user.sehir)
    
    # Tarih aralığı filtresi uygulandıysa
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        yemek_listeleri = yemek_listeleri.filter(tarih__gte=start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        yemek_listeleri = yemek_listeleri.filter(tarih__lte=end_date)

    # Öğün filtresi uygulandıysa
    if ogun:
        # "ogun" parametresini kontrol et ve ona göre filtrele
        yemek_listeleri = yemek_listeleri.filter(ogun=ogun)
    
    # Seçilen yemek verilerini al
    yemek_listeleri = yemek_listeleri.values("tarih", "ogun", "yemek_1", "yemek_2", "yemek_3", "yemek_4", "yemek_5")
    
    # DataFrame'e dönüştür
    df = pd.DataFrame(list(yemek_listeleri))
    
    # "şehir" kolonunu tarih kolonundan sonra ekle
    df['şehir'] = request.user.sehir  # Kullanıcının şehri
    df = df[['tarih', 'şehir', 'ogun', 'yemek_1', 'yemek_2', 'yemek_3', 'yemek_4', 'yemek_5']]  # Kolon sıralaması
    
    # "tarih" kolonunu doğru biçimde formatla
    df['tarih'] = pd.to_datetime(df['tarih']).dt.strftime('%Y-%m-%d')
    
    # Excel çıktısı hazırlığı
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Yemek Listesi", index=False)
    
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="yemek_listesi.xlsx"'
    
    return response

@login_required
def profil(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        sehir_id = request.POST.get("sehir", "").strip()
        yurt_id = request.POST.get("yurt", "").strip()

        has_error = False  

        # Kullanıcı adı güncelleme
        if username and username != user.username:
            if User.objects.exclude(id=user.id).filter(username=username).exists():
                messages.error(request, "Bu kullanıcı adı zaten kullanılıyor!")
                has_error = True
            else:
                user.username = username
        
        # E-posta güncelleme
        if email and email != user.email:
            if User.objects.exclude(id=user.id).filter(email=email).exists():
                messages.error(request, "Bu e-posta adresi zaten kullanılıyor!")
                has_error = True
            else:
                user.email = email

        # Şehir güncelleme
        if sehir_id and user.kullanici_tipi not in ["turkiye_yetkilisi"]:
            try:
                user.sehir = Sehir.objects.get(id=sehir_id)
            except Sehir.DoesNotExist:
                messages.error(request, "Seçilen şehir bulunamadı!")
                has_error = True

        # Yurt güncelleme
        if yurt_id and user.kullanici_tipi not in ["turkiye_yetkilisi", "sehir_yetkilisi"]:
            try:
                user.yurt = Yurt.objects.get(id=yurt_id)
            except Yurt.DoesNotExist:
                messages.error(request, "Seçilen yurt bulunamadı!")
                has_error = True

        if not has_error:
            user.save()
            messages.success(request, "Profil bilgileriniz başarıyla güncellendi!")
            return redirect("profil")

    # Kullanıcı yorumlarını ve liste verilerini çek
    sehirler = Sehir.objects.all()
    yurtlar = Yurt.objects.all()

    return render(request, 'profile.html', {
        "user": user,
        "sehirler": sehirler,
        "yurtlar": yurtlar
    })



@login_required
def yorumlar(request):
   user_id = request.user.id
   user_yurt = request.user.yurt.isim
   user_sehir = request.user.sehir
   kaynak = request.GET.get('k', 'genel')
   if kaynak == "profil":
    yorumlar = YemekYorumu.objects.filter(user=user_id).order_by('-tarih')
   elif kaynak == "yurt":
       yorumlar = YemekYorumu.objects.filter(yurt=user_yurt).order_by('-tarih')
   elif kaynak == "sehir":
       yorumlar = YemekYorumu.objects.filter(sehir_id=user_sehir).order_by('-tarih')
   elif kaynak == "turkiye":
       yorumlar = YemekYorumu.objects.all().order_by('-tarih')
   else:
       yorumlar=[]
   return render(request, 'yorumlar.html', {
       "yorumlar" : yorumlar,
       'kaynak': kaynak
    })

@login_required
def ozetler(request):
   kaynak = request.GET.get('k', 'genel')
   ozetler = Ozet.objects.all() 
   for ozet in ozetler:
       ozet.ozet = markdown.markdown(ozet.ozet)
   user_id = request.user.id
   user_yurt = request.user.yurt.isim
   user_sehir = request.user.sehir
   kaynak = request.GET.get('k', 'genel')
   if kaynak == "yurt":
       ozetler = Ozet.objects.filter(yurt=user_yurt,kapsam = "yurt").order_by('-ozet_tarih')
   elif kaynak == "sehir":
       ozetler = Ozet.objects.filter(sehir_id=user_sehir,kapsam = "sehir").order_by('-ozet_tarih')
   elif kaynak == "turkiye":
       ozetler = Ozet.objects.filter(kapsam = "turkiye").order_by('-ozet_tarih')
   else:
       ozetler=[]
   return render(request, 'ozetler.html', {
       "ozetler": ozetler,
       'kaynak': kaynak
    })

@login_required
def get_sehir(request):
    sehir_kodu = request.GET.get('sehir_kodu')
    if sehir_kodu:
        ozetler = Ozet.objects.filter(sehir_id=sehir_kodu, kapsam="sehir").values()
        for ozet in ozetler:
            ozet['ozet'] = markdown.markdown(ozet['ozet'])  # Markdown'dan HTML'ye dönüşüm
        return JsonResponse(list(ozetler), safe=False)
    return JsonResponse([], safe=False)

