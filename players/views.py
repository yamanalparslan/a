# players/views.py

import base64
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import Http404
from django.contrib import messages

# REST Framework
from rest_framework import viewsets, permissions
from .serializers import PlayerSerializer, MatchSerializer

# Modeller ve Formlar
from .models import Player, Match, Notification, Court
from .forms import PlayerForm, CustomUserCreationForm, MatchForm

# --- KİMLİK DOĞRULAMA ---

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        encoded_password = request.POST.get('password')
        
        try:
            if encoded_password:
                decoded_password = base64.b64decode(encoded_password).decode('utf-8')
            else:
                decoded_password = ""

            user = authenticate(request, username=username, password=decoded_password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"👋 Hoş geldin, {user.username}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, "❌ Kullanıcı adı veya şifre hatalı.")
                
        except Exception as e:
            messages.error(request, "⚠️ Giriş işlemi sırasında bir hata oluştu.")
            
    return render(request, 'registration/login.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        player_form = PlayerForm(request.POST, request.FILES)
        
        if user_form.is_valid() and player_form.is_valid():
            user = user_form.save()
            player = player_form.save(commit=False)
            player.user = user
            player.save()
            login(request, user)
            messages.success(request, "✅ Hoş geldin! Profilin oluşturuldu.")
            return redirect('home')     
    else:
        user_form = CustomUserCreationForm()
        player_form = PlayerForm()
        
    return render(request, 'registration/signup.html', {
        'user_form': user_form, 
        'player_form': player_form
    })


# --- STANDART GÖRÜNÜMLER ---

@login_required
def player_list(request):
    """ Tüm oyuncuları listeleyen view. (Yeniden eskiye sıralı) """
    
    # En son kayıt olan en üstte (ID'ye göre tersten sıralama)
    all_players = Player.objects.all().order_by('-id') 
    
    # Arama mantığı
    query = request.GET.get('q')
    if query:
        all_players = all_players.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(city__icontains=query)
        )

    context = {'players': all_players}
    return render(request, 'players/player_list.html', context)


def player_detail(request, pk):
    """ Tek bir oyuncunun detaylarını ve istatistiklerini gösteren view. """
    player = get_object_or_404(Player, pk=pk)
    
    # --- İSTATİSTİK HESAPLAMA ---
    
    # 1. Tüm maçlarını al (Takım 1 veya Takım 2 olduğu ve Onaylanmış maçlar)
    all_matches = Match.objects.filter(
        Q(team1_players=player) | Q(team2_players=player),
        is_confirmed=True
    )
    
    total_matches = all_matches.count()
    wins = 0
    losses = 0
    
    for match in all_matches:
        # Beraberlik durumu (Puan değişimi olmayan durum)
        if match.score_team1 == match.score_team2:
            continue
            
        # Takım 1'de miyim?
        is_team1 = player in match.team1_players.all()
        
        # Kazananı kontrol et
        if is_team1:
            if match.score_team1 > match.score_team2:
                wins += 1
            else:
                losses += 1
        else: # Takım 2'deyim
            if match.score_team2 > match.score_team1:
                wins += 1
            else:
                losses += 1
    
    # Kazanma Oranı (%)
    if total_matches > 0:
        win_rate = int((wins / total_matches) * 100)
    else:
        win_rate = 0

    context = {
        'player': player,
        'total_matches': total_matches,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
    }
    
    return render(request, 'players/player_detail.html', context)

@login_required
def match_list(request):
    """ 
    Sadece giriş yapan kullanıcının katıldığı onaylanmış maçları listeler.
    """
    try:
        player = request.user.player
        # Tüm maçları getir (yinelenenler olabilir)
        all_matches = Match.objects.filter(
            Q(team1_players=player) | Q(team2_players=player),
            is_confirmed=True
        ).order_by('-match_date')
        
        # Python'da yinelenenleri kaldır ve unique ID'leri tut
        seen_ids = set()
        my_matches = []
        for match in all_matches:
            if match.id not in seen_ids:
                seen_ids.add(match.id)
                my_matches.append(match)
        
    except:
        my_matches = []

    context = {'matches': my_matches}
    return render(request, 'players/match_list.html', context)


def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    
    team1_players = match.team1_players.all()
    team2_players = match.team2_players.all()
    
    winner = None
    if match.score_team1 > match.score_team2:
        winner = "team1"
    elif match.score_team2 > match.score_team1:
        winner = "team2"
    else:
        winner = "draw"
    
    context = {
        'match': match,
        'team1_players': team1_players,
        'team2_players': team2_players,
        'winner': winner,
    }
    return render(request, 'players/match_detail.html', context)


def home(request):
    recent_matches = Match.objects.filter(is_confirmed=True).order_by('-match_date')[:5]
    recent_players = Player.objects.all().order_by('-rating')[:5]
    
    context = {
        'recent_matches': recent_matches,
        'recent_players': recent_players,
    }
    return render(request, 'players/home.html', context)


def leaderboard(request):
    all_players_sorted = Player.objects.all().order_by('-rating')
    context = {'players': all_players_sorted}
    return render(request, 'players/leaderboard.html', context)


# --- PROFİL DÜZENLEME ---

@login_required
def edit_profile(request):
    try:
        player = request.user.player
    except:
        messages.error(request, "❌ Profil bulunamadı.")
        return redirect('home')

    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES, instance=player)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profil başarıyla güncellendi!")
            return redirect('player-detail', pk=player.pk)
    else:
        form = PlayerForm(instance=player)
    
    return render(request, 'players/edit_profile.html', {'form': form})


# --- MAÇ YÖNETİMİ ---

@login_required
def create_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.created_by = request.user 
            match.is_confirmed = False 
            
            # 1. Set Skorlarına Göre Kazananı Hesapla (2-0, 2-1 vb.)
            match.calculate_set_winner()
            
            match.save() 
            
            new_court_name = form.cleaned_data.get('new_court_name')
            
            if new_court_name:
                # Eğer kullanıcı yeni isim yazdıysa:
                # get_or_create: Varsa onu getir, yoksa yeni oluştur.
                court_obj, created = Court.objects.get_or_create(
                    name=new_court_name,
                    defaults={'city': request.user.player.city} # Varsayılan şehir kullanıcının şehri olsun
                )
                match.court = court_obj
            # -------------------------

            match.calculate_set_winner()
            match.save()

            # 2. Takım 1'e Kendini Ekle
            try:
                match.team1_players.add(request.user.player)
            except:
                messages.error(request, "❌ Profil bulunamadı. Lütfen yönetici ile iletişime geçin.")
                match.delete()
                return redirect('home')
            
            # 3. Partner Ekle
            teammate = form.cleaned_data.get('teammate')
            if teammate:
                match.team1_players.add(teammate)
                # Partnerine bildirim gönder
                if teammate.user != request.user:
                    Notification.objects.create(
                        recipient=teammate.user,
                        match=match,
                        message=f"🤝 {request.user.username} seni takım arkadaşı olarak ekledi! Maç Skoru: {match.score_team1}-{match.score_team2}. Onaylıyor musun?"
                    )
            
            # 4. Rakipleri Ekle
            form.save_m2m() 
            
            # 5. Rakiplere Bildirim Gönder
            for opponent in match.team2_players.all():
                if opponent.user != request.user:
                    Notification.objects.create(
                        recipient=opponent.user,
                        match=match,
                        message=f"⚔️ {request.user.username} seni rakip olarak ekledi! Maç Skoru: {match.score_team1}-{match.score_team2}. Onaylıyor musun?"
                    )
            
            messages.success(request, "✅ Maç başarıyla oluşturuldu ve davetler gönderildi!")
            return redirect('match-list')
    else:
        form = MatchForm()
        try:
            current_player = request.user.player
            # Listelerden kendini çıkar
            form.fields['teammate'].queryset = Player.objects.exclude(pk=current_player.pk)
            form.fields['team2_players'].queryset = Player.objects.exclude(pk=current_player.pk)
        except:
            messages.error(request, "❌ Profiliniz bulunamadı. Lütfen önce profil oluşturun.")
            return redirect('home')
    
    return render(request, 'players/create_match.html', {'form': form})

@login_required
def edit_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    
    if match.created_by != request.user:
        messages.error(request, "❌ Bu maçı düzenleyemezsin.")
        return redirect('match-detail', pk=pk)
    
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Maç başarıyla güncellendi!")
            return redirect('match-detail', pk=match.pk)
    else:
        form = MatchForm(instance=match)
        try:
            current_player = request.user.player
            form.fields['teammate'].queryset = Player.objects.exclude(pk=current_player.pk)
            form.fields['team2_players'].queryset = Player.objects.exclude(pk=current_player.pk)
        except:
            pass
    
    return render(request, 'players/edit_match.html', {'form': form, 'match': match})


@login_required
def delete_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    
    if match.created_by != request.user:
        messages.error(request, "❌ Bu maçı silemezsin.")
        return redirect('match-detail', pk=pk)
    
    if request.method == 'POST':
        match.delete()
        messages.success(request, "✅ Maç başarıyla silindi!")
        return redirect('match-list')
    
    return render(request, 'players/confirm_delete_match.html', {'match': match})


# --- BİLDİRİMLER ---

@login_required
def notifications(request):
    
    my_notifications = Notification.objects.filter(
        recipient=request.user, 
        is_read=False  # <--- BU SATIR ÇOK ÖNEMLİ (Sadece okunmamışları getir)
    ).order_by('-created_at')
    
    return render(request, 'players/notifications.html', {'notifications': my_notifications})

@login_required
def accept_match(request, notification_id):


    notification = get_object_or_404(Notification, pk=notification_id)
    
    # Güvenlik: Başkasının bildirimini onaylayamazsın
    if notification.recipient != request.user:
        return redirect('home')
        
    match = notification.match
    
    # 1. Bildirimi "Onaylandı/Okundu" olarak işaretle ve KAYDET
    if not notification.is_read:
        notification.is_read = True
        notification.save() # <--- BU KAYIT İŞLEMİ LİSTEDEN SİLER
    
    # 2. Konsensüs Kontrolü (Puan Hesaplama)
    # Not: Notification modelinde is_read=True olduğu için sayaca dahil edilir.
    match.check_consensus_and_calculate()
    
    # İşlem bitince kullanıcıyı Maç Listesine gönder
    return redirect('match-list')


@login_required
def reject_match(request, pk):

    notification = get_object_or_404(Notification, pk=pk)
    
    if notification.recipient != request.user:
        messages.error(request, "❌ Bu bildirimi yönetemezsin.")
        return redirect('home')
    
    match = notification.match
    
    if match and not match.is_confirmed:
        match.delete()
        messages.info(request, "ℹ️ Maç reddedildi ve silindi.")
    else:
        messages.info(request, "🗑️ Bildirim silindi.")

    notification.delete()
    return redirect('notifications')

@login_required
def reject_match(request, notification_id):
    """
    Gelen maç davetini reddetme.
    """
    notification = get_object_or_404(Notification, pk=notification_id)
    
    # Güvenlik: Başkasının bildirimini silemezsin
    if notification.recipient != request.user:
        return redirect('home')
    
    # Bildirimi veritabanından sil (Reddedildiği için artık gerek yok)
    notification.delete()
    
    # Bildirimler sayfasına geri dön
    return redirect('notifications')


# --- API VIEWSET'LERİ ---

class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all().order_by(F('rating').desc(nulls_last=True), 'user__username')
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.filter(is_confirmed=True).order_by('-match_date')
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
