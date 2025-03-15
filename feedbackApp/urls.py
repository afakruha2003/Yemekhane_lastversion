from django.urls import path
from django.conf.urls.static import static
from gsb_yemekhane import settings
from . import views
from .views import yemek_listesi_panel, yemek_listesi_sil, yemek_listesi_indir,profil

urlpatterns = [
    path('', views.anasayfa, name='anasayfa'),
    path('yemek_yorumla/', views.yemek_yorumla, name='yemek_yorumla'),
    path('sehir-dashboard/', views.sehir_dashboard, name='sehir-dashboard'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', profil, name='profil'),
    path('yorumlar/', views.yorumlar, name='yorumlar'),
    path('ozetler/', views.ozetler, name='ozetler'),
    path('logout/', views.logout_view, name='logout'),

    path("get-yurtlar/", views.get_yurtlar, name="get_yurtlar"),
    path('get-sehir/', views.get_sehir, name='get_sehir'),
    path('panel/', yemek_listesi_panel, name='yemek_listesi_panel'),
    path('yemek-guncelle/', views.yemek_listesi_upload, name='yemek_guncelle'),
    path('panel/sil/<int:liste_id>/', yemek_listesi_sil, name='yemek_listesi_sil'),
    path('panel/indir/', yemek_listesi_indir, name='yemek_listesi_indir'),
]

if settings.DEBUG:  # Sadece geliştirme ortamında medya dosyalarını sun
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
