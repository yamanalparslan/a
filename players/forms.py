# players/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Match

# 1. Kullanıcı Bilgileri Formu
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': ' '})
            

# 2. Oyuncu Profili Formu
class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        # DÜZELTME BURADA YAPILDI: 'phone' (Boşluksuz)
        fields = ['first_name', 'last_name', 'phone', 'city', 'skill_level']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adınız'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyadınız'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '05XX XXX XX XX'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şehir'}),
            'skill_level': forms.Select(attrs={'class': 'form-select'}),
        }


# 3. Maç Ekleme Formu
class MatchForm(forms.ModelForm):
    teammate = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        required=False,
        label="Takım Arkadaşın (Opsiyonel)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Match
        fields = ['teammate', 'team2_players', 'score_team1', 'score_team2']
        
        widgets = {
            'team2_players': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 150px;'}),
            'score_team1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'SİZİN Skorunuz'}),
            'score_team2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'RAKİP Skoru'}),
        }
        
        labels = {
            'team2_players': 'Rakip Oyuncuları Seçin (CTRL/CMD ile çoklu seçim)',
            'score_team1': 'Sizin Takımın Skoru',
            'score_team2': 'Rakip Takımın Skoru',
        }