# players/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

# Modellerimizi ve Formlarımızı import ediyoruz
from .models import Player, Match, Notification
from .forms import PlayerForm, CustomUserCreationForm, MatchForm

def player_list(request):
    """ Tüm oyuncuları listeleyen view. """
    all_players = Player.objects.all()
    context = {'players': all_players}
    return render(request, 'players/player_list.html', context)


def player_detail(request, pk):
    """ Tek bir oyuncunun detaylarını çeken view. """
    player = get_object_or_404(Player, pk=pk)
    context = {'player': player}
    return render(request, 'players/player_detail.html', context)


def match_list(request):
    """ Tüm maçları listeleyen view. """
    # Sadece onaylanmış (is_confirmed=True) maçları gösterelim
    all_matches = Match.objects.filter(is_confirmed=True).order_by('-match_date')
    context = {'matches': all_matches}
    return render(request, 'players/match_list.html', context)


def match_detail(request, pk):
    """ Tek bir maçın detaylarını çeken view. """
    match = get_object_or_404(Match, pk=pk)
    context = {'match': match}
    return render(request, 'players/match_detail.html', context)


def home(request):
    """ Ana sayfa view'i. """
    # Sadece onaylı maçları göster
    recent_matches = Match.objects.filter(is_confirmed=True).order_by('-match_date')[:5]
    recent_players = Player.objects.all().order_by('-pk')[:5]
    
    context = {
        'recent_matches': recent_matches,
        'recent_players': recent_players,
    }
    return render(request, 'players/home.html', context)


def leaderboard(request):
    """ Skor tablosu view'i. """
    all_players_sorted = Player.objects.all().order_by('-rating')
    context = {'players': all_players_sorted}
    return render(request, 'players/leaderboard.html', context)


def signup(request):
    """ Kayıt olma view'i. """
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        player_form = PlayerForm(request.POST)
        
        if user_form.is_valid() and player_form.is_valid():
            user = user_form.save()
            player = player_form.save(commit=False)
            player.user = user
            player.save()
            login(request, user)
            return redirect('home')     
    else:
        user_form = CustomUserCreationForm()
        player_form = PlayerForm()
        
    return render(request, 'registration/signup.html', {
        'user_form': user_form, 
        'player_form': player_form
    })


# --- GÜNCELLENEN CREATE_MATCH FONKSİYONU ---
@login_required
def create_match(request):
    """
    Maç oluşturma ve davet gönderme.
    Partner seçimi özelliği eklendi.
    """
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            # 1. Maçı oluştur ama henüz veritabanına tam kaydetme
            match = form.save(commit=False)
            match.created_by = request.user # Maçı kim kurdu?
            match.is_confirmed = False # HENÜZ ONAYLANMADI
            match.save() # Şimdi ID oluştu, kaydedebiliriz
            
            # 2. Takım 1'i Oluştur
            # A) Seni ekle (Zorunlu)
            # (Eğer kullanıcının Player profili yoksa hata vermemesi için try-except)
            try:
                match.team1_players.add(request.user.player)
            except:
                pass 
            
            # B) Partner Ekle (Eğer seçildiyse) -- YENİ KISIM
            teammate = form.cleaned_data.get('teammate')
            if teammate:
                match.team1_players.add(teammate)
            
            # 3. Takım 2 oyuncularını formdan alıp ekle
            form.save_m2m() 
            
            # 4. Rakiplere BİLDİRİM (Davet) Gönder
            for opponent in match.team2_players.all():
                # Kendine bildirim gönderme (Güvenlik)
                if opponent.user != request.user:
                    Notification.objects.create(
                        recipient=opponent.user,
                        match=match,
                        message=f"⚔️ {request.user.username} seni bir maça ekledi! Skor: {match.score_team1}-{match.score_team2}. Onaylıyor musun?"
                    )
            
            # Kullanıcıyı maç listesine gönder (Maç henüz görünmeyecek çünkü onaylanmadı)
            return redirect('match-list')
    else:
        form = MatchForm()
        # Formda kendi ismini listelerden çıkar (Kendini partner veya rakip seçemezsin)
        try:
            current_player = request.user.player
            # Takım arkadaşı listesinden kendini çıkar -- YENİ
            form.fields['teammate'].queryset = Player.objects.exclude(pk=current_player.pk)
            # Rakip listesinden kendini çıkar
            form.fields['team2_players'].queryset = Player.objects.exclude(pk=current_player.pk)
        except:
            pass
    
    return render(request, 'players/create_match.html', {'form': form})


@login_required
def notifications(request):
    """
    Kullanıcının bildirimlerini listeler.
    """
    # Bana gelen ve henüz okunmamış (is_read=False) bildirimleri al
    my_notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
    return render(request, 'players/notifications.html', {'notifications': my_notifications})


@login_required
def accept_match(request, notification_id):
    """
    Gelen maç davetini onaylama.
    """
    # Bildirimi bul
    notification = get_object_or_404(Notification, pk=notification_id)
    
    # Güvenlik: Başkasının bildirimini onaylayamazsın
    if notification.recipient != request.user:
        return redirect('home')
        
    match = notification.match
    
    # 1. Maçı onayla
    match.is_confirmed = True
    match.save()
    
    # 2. Puanları Hesapla (Artık onaylandı!)
    match.calculate_ratings()
    
    # 3. Bildirimi okundu olarak işaretle (Listeden düşsün)
    notification.is_read = True
    notification.save()
    
    return redirect('match-list')


@login_required
def edit_profile(request):
    """
    Kullanıcının kendi profil bilgilerini güncellemesini sağlar.
    """
    # Giriş yapan kullanıcının oyuncu profilini al
    player = request.user.player
    
    if request.method == 'POST':
        # Formu gelen veriyle doldur, AMA 'instance=player' diyerek
        # bunun yeni bir kayıt değil, güncelleme olduğunu belirtiyoruz.
        form = PlayerForm(request.POST, instance=player)
        
        if form.is_valid():
            form.save()
            # Kaydettikten sonra kendi profil sayfasına yönlendir
            return redirect('player-detail', pk=player.pk)
            
    else:
        # Sayfa ilk açıldığında formu mevcut bilgilerle dolu getir
        form = PlayerForm(instance=player)
    
    return render(request, 'players/edit_profile.html', {'form': form})