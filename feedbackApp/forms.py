from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, YemekYorumu, YemekListesiGuncelleme, Sehir, KULLANICI_TIPI_CHOICES, YemekListesi
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import os

CustomUser = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    kullanici_tipi = forms.ChoiceField(choices=KULLANICI_TIPI_CHOICES)
    sehir = forms.ModelChoiceField(queryset=Sehir.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'kullanici_tipi','sehir','yurt']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Şifreler eşleşmiyor!")

        return cleaned_data

# Login Formu
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput())

# Yemek Yorum Formu
class YemekListesiModelForm(forms.ModelForm):
    # ModelForm'a ekstra bir dosya alanı ekliyoruz.
    excel_file = forms.FileField(label="Yemek Listesi Dosyası", required=True)
    
    class Meta:
        model = YemekListesi
        # Formda sadece excel_file alanını gösteriyoruz,
        # çünkü diğer alanlar excel dosyasından otomatik doldurulacak.
        fields = ['excel_file']
    
    def clean_excel_file(self):
        file = self.cleaned_data.get("excel_file")
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.xlsx', '.ods']:
            raise forms.ValidationError("Lütfen sadece .xlsx veya .ods uzantılı dosya yükleyin.")
        return file

class YemekListesiSilForm(forms.Form):
    yemek_listesi_id = forms.ModelChoiceField(
        queryset=YemekListesi.objects.all(),
        label="Silinecek Yemek Listesi",
        empty_label="Seçiniz",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
