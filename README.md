# 🍽️ Yemekhane_LastVersion

Bu proje, yurtlarda sunulan yemeklerin öğrenciler tarafından değerlendirilmesi ve geri bildirim sağlanması amacıyla geliştirilmiş bir web uygulamasıdır. **Django** framework' üzerinde geliştirilmiştir ve kullanıcı dostu bir arayüz sunmaktadır. Ayrıca, yöneticiler için bir **admin paneli** içermektedir.

---

## 🚀 Özellikler

### 🖥️ Kullanıcı Arayüzü
✅ Güncel yemek listesini görüntüleme.  
✅ Yemekler hakkında yorum yapma.  
✅ Kullanıcı dostu ve sezgisel tasarım.  

### ✍️ Yorum Özetleme
✅ **Google Gemini API** ile günlük yorumların otomatik olarak özetlenmesi.  
✅ Özetlerde, beğenilen ve eleştirilen yemekler, tekrar eden şikayetler ve genel eğilimler yer alır.  

### ⏳ Zamanlanmış Görevler
✅ **Gece 01:00'de** otomatik yorum özetleme görevi.  

### 🔒 Kullanıcı Kimlik Doğrulama
✅ **Admin paneline** güvenli giriş sistemi.  

---

## 🛠️ Teknolojiler

| Teknoloji | Açıklama |
|-----------|---------|
| **Django** | Web framework |
| **SQLite** | Veritabanı |
| **HTML/CSS** | Kullanıcı arayüzü |
| **Bootstrap** | CSS framework |
| **Python** | Backend mantığı |
| **Google Gemini API** | Yorum özetleme |
| **Django-Login** | Kullanıcı kimlik doğrulama |
| **Schedule** | Zamanlanmış görevler |
| **Markdown** | Yorum özet biçimlendirme |

---

## 📌 Kurulum

1️⃣ **Python’ı Yükleyin**  
[Python resmi sitesi](https://www.python.org/downloads/) üzerinden sisteminize uygun versiyonu yükleyin.  

2️⃣ **Gerekli Bağımlılıkları Kurun**  
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows
pip install django djangorestframework djangorestframework-simplejwt
pip install pandas openpyxl
tpip install google-generativeai
pip install matplotlib seaborn
pip install python-dotenv
pip install Pillow
pip install xlsxwriter
```

3️⃣ **Veritabanını Hazırlayın**  
```bash
python manage.py migrate
python manage.py createsuperuser  # Admin kullanıcısı oluştur
```

4️⃣ **Google Gemini API Anahtarını Ayarlayın**  
`settings.py` dosyanızda aşağıdaki gibi API anahtarını tanımlayın:  
```python
import google.generativeai as genai
genai.configure(api_key="API_ANAHTARINIZ")
```
API anahtarını almak için: [Google AI Studio](https://makersuite.google.com/)  

5️⃣ **Uygulamayı Başlatın**  
```bash
python manage.py runserver
```
Uygulama genellikle şu adreste çalışacaktır: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  

---

## 📂 Dosya Yapısı

```
yemekhane_lastversion/  
│── manage.py  
│── db.sqlite3  # Veritabanı dosyası
│── static/  # Statik dosyalar (CSS, JS, resimler vb.)  
│── gsb_yemekhane/  # Ana proje klasörü  
│   │── __init__.py  
│   │── settings.py  # Django yapılandırma dosyası  
│   │── urls.py  # URL yönlendirmeleri  
│   │── wsgi.py  # WSGI sunucu dosyası  
│   └── asgi.py  # ASGI sunucu dosyası  
│  
└── feedbackApp/  # Django uygulaması  
    │── migrations/  # Veritabanı geçiş dosyaları  
    │── templates/  # HTML şablonlarının bulunduğu klasör  
    │   └── feedback/  
    │       ├── admin_login.html  
    │       ├── anasayfa.html  
    │       ├── base.html  
    │       ├── login.html  
    │       ├── map.html  
    │       ├── not_available.html  
    │       ├── ozetler.html  
    │       ├── profile.html  
    │       ├── register.html  
    │       ├── yemek_guncelle.html  
    │       ├── yemek_listesi_panel.html  
    │       ├── yemek_listesi_sil.html  
    │       ├── yemek-yorumla.html  
    │       ├── yorumlar.html  
    │       ├── yurt_dashboard.html  
    │  
    │── __init__.py  
    │── admin.py  # Django admin paneli yapılandırması  
    │── apps.py  # Django uygulama ayarları  
    │── models.py  # Veritabanı modelleri  
    │── forms.py  # Formların bulunduğu dosya  
    │── tests.py  # Test dosyaları  
    │── views.py  # Görünümleri yöneten dosya  
    │── urls.py  # Uygulama özelinde URL yönlendirmeleri  
    │── gemini.py  # Özel bir Python betiği
    │── scheduler.py
    │── tests.py    
    └── statistics.py  # İstatistik hesaplamaları için özel betik  
```

---

## 🎯 Kullanım

**📌 Ana Sayfa:**  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/) adresini ziyaret ederek güncel yemek listesini görebilir ve yorum yapabilirsiniz.

