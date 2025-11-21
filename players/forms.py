# players/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Match

# 1. Kullanıcı Bilgileri Formu (GÜNCELLENDİ: E-posta Eklendi)
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # Username'in yanına 'email' de ekledik
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Alanlara stil ekle
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': ' '})
        
        # E-posta alanını zorunlu yap (Şifre sıfırlama için şart)
        self.fields['email'].required = True


# 2. Oyuncu Profili Formu
class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'phone', 'city', 'skill_level', 'profile_picture']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adınız'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyadınız'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '05XX XXX XX XX'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şehir'}),
            'skill_level': forms.Select(attrs={'class': 'form-select'}),
            
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control', 
                'style': 'background-color: #0f172a; color: white; border: 1px solid #334155;'
            }),
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
            'team2_players': 'Rakip Oyuncuları Seçin',
            'score_team1': 'Sizin Takımın Skoru',
            'score_team2': 'Rakip Takımın Skoru',
        }

    def clean_team2_players(self):
        players = self.cleaned_data['team2_players']
        
        if len(players) > 2:
            raise forms.ValidationError("En fazla 2 rakip oyuncu seçebilirsiniz.")
        
        if len(players) < 1:
             raise forms.ValidationError("En az 1 rakip seçmelisiniz.")
             
        return players