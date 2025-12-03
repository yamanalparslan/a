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
        queryset=Player.objects.all(), required=False, label="Partnerin",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # KAÇ SET OYNANDI? (Sanal Alan)
    SET_CHOICES = [('1', '1 Set (Tek Setlik Maç)'), ('2', '2 Set (Normal Maç)'), ('3', '3 Set (Uzatmalı)')]
    num_sets = forms.ChoiceField(choices=SET_CHOICES, label="Set Sayısı", initial='2', 
                                 widget=forms.Select(attrs={'class': 'form-select', 'id': 'numSetsSelector'}))

    class Meta:
        model = Match
        # Set skorlarını ekledik (score_team1 ve 2'yi kaldırdık, onları otomatik hesaplayacağız)
        fields = ['teammate', 'team2_players', 
                  'set1_team1', 'set1_team2', 
                  'set2_team1', 'set2_team2', 
                  'set3_team1', 'set3_team2']
        
        widgets = {
            'team2_players': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 150px;'}),
            # Set Skorları İçin Küçük Kutular
            'set1_team1': forms.NumberInput(attrs={'class': 'form-control text-center', 'placeholder': '0'}),
            'set1_team2': forms.NumberInput(attrs={'class': 'form-control text-center', 'placeholder': '0'}),
            'set2_team1': forms.NumberInput(attrs={'class': 'form-control text-center', 'placeholder': '0'}),
            'set2_team2': forms.NumberInput(attrs={'class': 'form-control text-center', 'placeholder': '0'}),
            'set3_team1': forms.NumberInput(attrs={'class': 'form-control text-center', 'placeholder': '0'}),
            'set3_team2': forms.NumberInput(attrs={'class': 'form-control text-center', 'placeholder': '0'}),
        }

    def clean_team2_players(self):
        players = self.cleaned_data['team2_players']
        if len(players) > 2: raise forms.ValidationError("En fazla 2 rakip.")
        if len(players) < 1: raise forms.ValidationError("En az 1 rakip.")
        return players