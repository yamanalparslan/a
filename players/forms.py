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

    new_court_name = forms.CharField(
        required=False, 
        label="Yeni Kort Adı",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Bostanlı Padel'})
    )
    
    class Meta:
        model = Match
        # Set skorlarını ekledik (score_team1 ve 2'yi kaldırdık, onları otomatik hesaplayacağız)
        fields = ['court','new_court_name','teammate', 'team2_players', 
                  'set1_team1', 'set1_team2', 
                  'set2_team1', 'set2_team2', 
                  'set3_team1', 'set3_team2']
        
        widgets = {
            'court': forms.Select(attrs={
                'class': 'form-select', 
                'style': 'background-color: #1e293b; color: white; border: 1px solid #64748b;'
            }),
            'team2_players': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 150px;'}),
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
    

    # players/forms.py içine eklenecek

from django import forms
from .models import MatchLookup, MatchLookupResponse
from datetime import date, timedelta

class MatchLookupForm(forms.ModelForm):
    class Meta:
        model = MatchLookup
        fields = [
            'looking_for', 
            'preferred_date', 
            'preferred_time_start', 
            'preferred_time_end',
            'city', 
            'preferred_court',
            'skill_level_min', 
            'skill_level_max',
            'description'
        ]
        
        widgets = {
            'looking_for': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat(),
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
            'preferred_time_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
            'preferred_time_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'İzmir',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
            'preferred_court': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
            'skill_level_min': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
            'skill_level_max': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Örn: Cumartesi sabahları düzenli oynuyorum, aynı seviyede partner arıyorum...',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Kullanıcının şehrini varsayılan yap
        if user and hasattr(user, 'player'):
            self.fields['city'].initial = user.player.city
            self.fields['skill_level_min'].initial = user.player.skill_level
            self.fields['skill_level_max'].initial = user.player.skill_level
        
        # Seviye seçeneklerini Player modelinden al
        from .models import Player
        skill_choices = [('', '-- Seçiniz --')] + list(Player.SKILL_CHOICES)
        self.fields['skill_level_min'].widget.choices = skill_choices
        self.fields['skill_level_max'].widget.choices = skill_choices
        
        # Kort seçeneklerine "Farketmez" ekle
        self.fields['preferred_court'].required = False
        self.fields['preferred_court'].empty_label = "-- Farketmez --"
    
    def clean(self):
        cleaned_data = super().clean()
        preferred_date = cleaned_data.get('preferred_date')
        time_start = cleaned_data.get('preferred_time_start')
        time_end = cleaned_data.get('preferred_time_end')
        
        # Tarih kontrolü
        if preferred_date and preferred_date < date.today():
            raise forms.ValidationError("Geçmiş bir tarih seçemezsiniz.")
        
        # Saat kontrolü
        if time_start and time_end and time_start >= time_end:
            raise forms.ValidationError("Bitiş saati, başlangıç saatinden sonra olmalıdır.")
        
        return cleaned_data


class MatchLookupResponseForm(forms.ModelForm):
    class Meta:
        model = MatchLookupResponse
        fields = ['message']
        
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Merhaba! Ben de o saatlerde müsaitim, oynayalım mı?',
                'style': 'background-color: #0f172a; color: white; border-color: #334155;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].required = False