# players/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Match  # Player ve Match modellerini import ediyoruz

# 1. Kullanıcı Bilgileri Formu (Username, Password) - Güzelleştirilmiş
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Her alana Bootstrap stili ekliyoruz
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': ' '})
            

# 2. Oyuncu Profili Formu (Ad, Soyad, Şehir, Seviye) - Güzelleştirilmiş
class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'city', 'skill_level']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adınız'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyadınız'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şehir'}),
            'skill_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seviye'}),
        }


# 3. Maç Ekleme Formu (GÜNCELLENMİŞ HALİ: Partner Seçimi Eklendi)
class MatchForm(forms.ModelForm):
    # YENİ ALAN: Takım Arkadaşı Seçimi
    # Modelde olmayan "sanal" bir alan ekliyoruz.
    teammate = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        required=False, # Zorunlu değil (Tek başına da oynayabilirsin)
        label="Takım Arkadaşın (Opsiyonel)",
        widget=forms.Select(attrs={'class': 'form-select'}) # Şık açılır kutu
    )

    class Meta:
        model = Match
        # 'teammate' alanını da listeye ekliyoruz
        fields = ['teammate', 'team2_players', 'score_team1', 'score_team2']
        
        widgets = {
            # SelectMultiple: Çoklu seçim kutusu.
            'team2_players': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 150px;'}),
            
            # Skor kutuları
            'score_team1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'SİZİN Skorunuz'}),
            'score_team2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'RAKİP Skoru'}),
        }
        
        labels = {
            'team2_players': 'Rakip Oyuncuları Seçin (CTRL/CMD ile çoklu seçim)',
            'score_team1': 'Sizin Takımın Skoru',
            'score_team2': 'Rakip Takımın Skoru',
        }