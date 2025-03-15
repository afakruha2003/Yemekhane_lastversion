# Yemekhane_lastversion
Bu proje, yurtlarda sunulan yemeklerin öğrenciler tarafından değerlendirilmesi ve geri bildirim sağlanması amacıyla geliştirilmiş bir web uygulamasıdır. Flask framework'ü kullanılarak geliştirilmiştir ve öğrencilerin yemekler hakkındaki yorumlarını kolayca iletebilmeleri için kullanıcı dostu bir arayüze sahiptir. Ayrıca, yöneticiler için bir admin paneli de içerir.

## Özellikler

*   **Kullanıcı Arayüzü:**
    *   Güncel yemek listesini görüntüleme.
    *   Yemekler hakkında yorum yapma.
    *   Kullanıcı dostu ve sezgisel tasarım.

*   **Yorum Özetleme:**
    *   Google Gemini API entegrasyonu ile günlük yorumların otomatik olarak özetlenmesi.
    *   Özetler, beğenilen ve eleştirilen yemekler, tekrar eden şikayetler, genel eğilimler ve yorum dağılımları gibi bilgileri içerir.

*   **Zamanlanmış Görevler:**
    *   Her gün gece 01:00'de otomatik olarak yorum özetleme görevi.

*   **Kullanıcı Kimlik Doğrulaması:**
    *   Admin paneline erişim için güvenli kullanıcı adı ve şifre tabanlı kimlik doğrulama.

## Teknolojiler

*   **Django:** Web framework.
*   **SQLite:** Veritabanı.
*   **HTML/CSS:** Kullanıcı arayüzü.
*   **Bootstrap:** CSS framework.
*   **Python:** Backend mantığı.
*   **Google Gemini API:** Yorum özetleme.
*   **Djando-Login:** Kullanıcı kimlik doğrulaması.
*   **Schedule:** Zamanlanmış görevler.
*   **Markdown:** Yorum özetini biçimlendirme.

## Kurulum

1.  **Python'ı Yükleyin:** Eğer sisteminizde Python yüklü değilse, [python.org](https://www.python.org/downloads/) adresinden indirin ve kurun.

2.  **Gerekli Kütüphaneleri Kurun:** Proje klasöründe bir sanal ortam oluşturun ve gerekli kütüphaneleri `pip` ile yükleyin:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate.bat  # Windows
    pip install django djangorestframework djangorestframework-simplejwt
    pip install pandas openpyxl
    pip install google-generativeai
    pip install matplotlib seaborn
    pip install python-dotenv
    pip install Pillow
    pip install xlsxwriter```

3.  **Veritabanını Oluşturun:**

    ```bash
    sqlite3 yemekhane.db < schema.sql #Eğer varsa şemayı buraya ekleyin
    ```

4.  **Google Gemini API Anahtarını Ayarlayın:** `app.py` dosyasında `genai.configure(api_key="...")` kısmına Google Gemini API anahtarınızı girin.  API anahtarını [Google AI Studio](https://makersuite.google.com/) adresinden alabilirsiniz.

5.  **Uygulamayı Başlatın:**

    ```bash
    python manage.py runserver
    ```

    Uygulama genellikle `http://127.0.0.1:8000/` adresinde çalışacaktır.


Kullanım
Ana Sayfa: http://127.0.0.1:8000/ adresini ziyaret ederek güncel yemek listesini görebilir ve yorum yapabilirsiniz.




DOSYA YAPISI

gsb_yemekhane_site_copy/  
│── manage.py  
│── db.sqlite3  # Veritabanı dosyası  
│── gsb_yemekhane_site_copy/  # Ana proje klasörü  
│   │── __init__.py  
│   │── settings.py  # Django yapılandırma dosyası  
│   │── urls.py  # URL yönlendirmeleri  
│   │── wsgi.py  # WSGI sunucu dosyası  
│   └── asgi.py  # ASGI sunucu dosyası  
│  
└── feedback/  # Django uygulaması  
    │── migrations/  # Veritabanı geçiş dosyaları  
    │── static/  # Statik dosyalar (CSS, JS, resimler vb.)  
    │── templates/  # HTML şablonlarının bulunduğu klasör  
    │   └── feedback/  
    │       ├── admin_login.html
    │       ├─anasayfa.html
    │       ├─  base.html
    │       ├─ login.html
    │       ├─ map.html
    │       ├─ not_available.html
    │       ├─ ozetler.html
    │       ├─ profile.html
    │       ├─ register.html
    │       ├─ sehir_dashboard.html
    │       ├─ turkiye_dashboard.html 
    │       ├─ yemek_guncelle.html
    │       ├─ yemek_listesi_panel.html
    │       ├─ yemek_listesi_sil.html
    │       ├─ yemek-yorumla.html
    │       ├─ yorumlar.html
    │       ├─ yurt_dashboard.html 
    │  
    │── __init__.py  
    │── admin.py  # Django admin paneli yapılandırması  
    │── apps.py  # Django uygulama ayarları  
    │── models.py  # Veritabanı modelleri  
    │── tests.py  # Test dosyaları  
    │── views.py  # Görünümleri yöneten dosya  
    │── urls.py  # Uygulama özelinde URL yönlendirmeleri  
    │── gamini.py  # Özel bir Python betiği  
    └── statistics.py  # İstatistik hesaplamaları için özel betik  
    └── forms.py  #formların bulunduğu dosya 
