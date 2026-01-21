# players/views.py

import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.paginator import Paginator
from .models import MatchLookup, MatchLookupResponse
from .forms import MatchLookupForm, MatchLookupResponseForm

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
        password = request.POST.get('password')

        try:
            user = authenticate(request, username=username, password=password)

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
   # 1. Sıralama Parametresini Al (Varsayılan: 'newest')
    sort_by = request.GET.get('sort', 'newest')

    # 2. Temel Sorgu
    all_players = Player.objects.all()

    # 3. Sıralama Mantığı
    if sort_by == 'city':
        # Şehre göre (A-Z), şehirleri aynı olanları puana göre sırala
        all_players = all_players.order_by('city', '-rating')
    elif sort_by == 'rating':
        # Puana göre (En yüksek en üstte)
        all_players = all_players.order_by('-rating')
    else:
        # Varsayılan: En yeni üyeler en üstte
        all_players = all_players.order_by('-id')

    # 4. Arama Mantığı (Mevcut kodun aynısı)
    query = request.GET.get('q')
    if query:
        all_players = all_players.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(city__icontains=query)
        )

    # 5. Sayfalama (Pagination)
    paginator = Paginator(all_players, 10) # Sayfada 20 oyuncu
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'players': page_obj,
        'current_sort': sort_by  # Şablonda hangi sıralamanın seçili olduğunu göstermek için
    }
    return render(request, 'players/player_list.html', context)


def player_detail(request, pk):
    """ Tek bir oyuncunun detaylarını ve istatistiklerini gösteren view. """
    player = get_object_or_404(Player, pk=pk)

    # --- İSTATİSTİK HESAPLAMA ---

    # 1. Tüm maçlarını al
    # GÜNCELLEME: Sonuna .distinct() ekledik.
    all_matches = Match.objects.filter(
        Q(team1_players=player) | Q(team2_players=player),
        is_confirmed=True
    ).distinct() # <--- BU KOMUT AYNI MAÇIN 2 KERE SAYILMASINI ENGELLER

    total_matches = all_matches.count()
    wins = 0
    losses = 0

    for match in all_matches:
        # Beraberlik durumu
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
    Sadece giriş yapan kullanıcının katıldığı onaylanmış maçları listeler. (Sayfalamalı - 10 Maç)
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

    # --- SAYFALAMA (PAGINATION) ---
    paginator = Paginator(my_matches, 10) # Sayfada 10 maç
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'matches': page_obj}
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
    # 1. Herkes için genel veriler
    recent_matches = Match.objects.filter(is_confirmed=True).order_by('-match_date')[:5]
    recent_players = Player.objects.all().order_by('-rating')[:5]

    context = {
        'recent_matches': recent_matches,
        'recent_players': recent_players,
    }

    # 2. PERFORMANS İSTATİSTİKLERİ
    if request.user.is_authenticated:
        try:
            player = request.user.player

            # TÜM onaylanan maçları al
            all_matches = Match.objects.filter(
                Q(team1_players=player) | Q(team2_players=player),
                is_confirmed=True
            ).distinct()

            # İstatistikleri hesapla
            wins = 0
            losses = 0
            total_won_sets = 0
            total_lost_sets = 0

            for match in all_matches:
                # Beraberlik atla
                if match.score_team1 == match.score_team2:
                    continue

                # Oyuncu hangi takımda?
                is_team1 = player in match.team1_players.all()

                # Kazanıp kaybettiğini kontrol et
                if is_team1:
                    if match.score_team1 > match.score_team2:
                        wins += 1
                        total_won_sets += match.score_team1
                        total_lost_sets += match.score_team2
                    else:
                        losses += 1
                        total_won_sets += match.score_team1
                        total_lost_sets += match.score_team2
                else:  # Takım 2'de
                    if match.score_team2 > match.score_team1:
                        wins += 1
                        total_won_sets += match.score_team2
                        total_lost_sets += match.score_team1
                    else:
                        losses += 1
                        total_won_sets += match.score_team2
                        total_lost_sets += match.score_team1

            # Toplam maç sayısı
            total_matches = wins + losses

            # Kazanma oranı
            win_rate = int((wins / total_matches * 100)) if total_matches > 0 else 0

            # Ortalama set sayısı
            avg_won_sets = round(total_won_sets / total_matches, 2) if total_matches > 0 else 0
            avg_lost_sets = round(total_lost_sets / total_matches, 2) if total_matches > 0 else 0

            # Context'e ekle
            context['perf_stats'] = {
                'total_matches': total_matches,
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate,
                'avg_won_sets': avg_won_sets,
                'avg_lost_sets': avg_lost_sets,
            }

        except Exception as e:
            print(f"Performans Hatası: {e}")
            pass

    return render(request, 'players/home.html', context)
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


def reject_match(request, notification_id):
    # 1. İlgili bildirimi çek (Sadece alıcısı işlem yapabilsin diye recipient kontrolü ekledik)
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    # 2. Bildirimin bağlı olduğu maçı al
    match_to_delete = notification.match

    # 3. Güvenlik önlemi: Maç zaten onaylanıp puanlanmışsa silinemesin (Opsiyonel ama önerilir)
    if match_to_delete.is_rated:
        messages.error(request, "Bu maç zaten onaylanıp puanlandığı için silinemez.")
        return redirect('notifications') # veya bildirimler sayfası

    # 4. MAÇI SİL
    # Not: Match modelinde notification için on_delete=models.CASCADE olduğu için
    # maçı silince ona bağlı tüm bildirimler de otomatik silinir.
    match_to_delete.delete()

    messages.warning(request, "Maçı reddettiniz. Maç kaydı ve tüm bildirimler silindi.")

    return redirect('notifications') # Kullanıcıyı yönlendirmek istediğin sayfa

def leaderboard(request):
  # Rating'e göre yüksekten düşüğe sırala ve SADECE ilk 10 kişiyi al
    players = Player.objects.order_by('-rating')[:10]

    return render(request, 'players/leaderboard.html', {
        'players': players
    })

# --- API VIEWSET'LERİ ---

class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all().order_by(F('rating').desc(nulls_last=True), 'user__username')
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.filter(is_confirmed=True).order_by('-match_date')
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@login_required
def match_lookup_list(request):
    """Tüm aktif maç arama ilanlarını listele"""

    # Filtreleme parametreleri
    city_filter = request.GET.get('city', '')
    looking_for_filter = request.GET.get('looking_for', '')
    date_filter = request.GET.get('date', '')

    # Temel sorgu: Aktif ve süresi dolmamış ilanlar
    lookups = MatchLookup.objects.filter(
        status='active',
        expires_at__gt=timezone.now(),
        preferred_date__gte=timezone.now().date()
        ).select_related('player', 'preferred_court')

    # Filtreleri uygula
    if city_filter:
        lookups = lookups.filter(city__icontains=city_filter)

    if looking_for_filter:
        lookups = lookups.filter(looking_for=looking_for_filter)

    if date_filter:
        from datetime import datetime
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            lookups = lookups.filter(preferred_date=filter_date)
        except:
            pass

    # Sayfalama
    paginator = Paginator(lookups, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Şehir listesi (Filtre için)
    cities = MatchLookup.objects.filter(
        status='active',
        expires_at__gt=timezone.now()
    ).values_list('city', flat=True).distinct()

    context = {
        'lookups': page_obj,
        'cities': cities,
        'current_filters': {
            'city': city_filter,
            'looking_for': looking_for_filter,
            'date': date_filter,
        }
    }
    return render(request, 'players/match_lookup_list.html', context)


@login_required
def match_lookup_create(request):
    """Yeni maç arama ilanı oluştur"""

    # Kullanıcının profili var mı kontrol et
    try:
        player = request.user.player
    except:
        messages.error(request, "❌ Önce profilinizi oluşturmalısınız.")
        return redirect('edit-profile')

    if request.method == 'POST':
        form = MatchLookupForm(request.POST, user=request.user)
        if form.is_valid():
            lookup = form.save(commit=False)
            lookup.player = player
            lookup.save()

            messages.success(request, "✅ İlanınız yayınlandı! Yakında ilgilenenler size ulaşacak.")
            return redirect('match-lookup-detail', pk=lookup.pk)
    else:
        form = MatchLookupForm(user=request.user)

    return render(request, 'players/match_lookup_create.html', {'form': form})


@login_required
def match_lookup_detail(request, pk):
    """İlan detayları ve yanıtlar"""

    lookup = get_object_or_404(MatchLookup, pk=pk)

    # Yanıtları getir
    responses = lookup.responses.all().select_related('responder__user')

    # İlan sahibi mi?
    is_owner = request.user == lookup.player.user

    # Kullanıcı zaten yanıt vermiş mi?
    has_responded = False
    if not is_owner:
        has_responded = lookup.responses.filter(responder=request.user.player).exists()

    context = {
        'lookup': lookup,
        'responses': responses,
        'is_owner': is_owner,
        'has_responded': has_responded,
    }
    return render(request, 'players/match_lookup_detail.html', context)


@login_required
def match_lookup_respond(request, pk):
    """İlana yanıt ver"""

    lookup = get_object_or_404(MatchLookup, pk=pk)

    # Kendi ilanına yanıt veremez
    if request.user == lookup.player.user:
        messages.error(request, "❌ Kendi ilanınıza yanıt veremezsiniz.")
        return redirect('match-lookup-detail', pk=pk)

    # İlan aktif değilse
    if not lookup.is_active():
        messages.error(request, "❌ Bu ilan artık aktif değil.")
        return redirect('match-lookup-detail', pk=pk)

    # Zaten yanıt verdiyse
    if lookup.responses.filter(responder=request.user.player).exists():
        messages.warning(request, "⚠️ Bu ilana zaten yanıt verdiniz.")
        return redirect('match-lookup-detail', pk=pk)

    if request.method == 'POST':
        form = MatchLookupResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.lookup = lookup
            response.responder = request.user.player
            response.save()

            # İlan sahibine bildirim gönder
            Notification.objects.create(
                recipient=lookup.player.user,
                match=None,  # Maç yerine yanıt bildirimi
                message=f"🔔 {request.user.username} maç arama ilanınıza yanıt verdi! '{lookup.get_looking_for_display()}' - {lookup.preferred_date}"
            )

            messages.success(request, "✅ Yanıtınız gönderildi! İlan sahibi sizinle iletişime geçecek.")
            return redirect('match-lookup-detail', pk=pk)
    else:
        form = MatchLookupResponseForm()

    context = {
        'lookup': lookup,
        'form': form,
    }
    return render(request, 'players/match_lookup_respond.html', context)


@login_required
def match_lookup_my_listings(request):
   # Kullanıcının kendi ilanlarını getir
    lookups = MatchLookup.objects.filter(player=request.user.player).order_by('-created_at')

    return render(request, 'players/match_lookup_my_listings.html', {
        'lookups': lookups
    })


@login_required
def match_lookup_delete(request, pk):
    """İlanı sil (sadece ilan sahibi)"""

    lookup = get_object_or_404(MatchLookup, pk=pk)

    if request.user != lookup.player.user:
        messages.error(request, "❌ Bu ilanı silemezsiniz.")
        return redirect('match-lookup-detail', pk=pk)

    if request.method == 'POST':
        lookup.delete()
        messages.success(request, "✅ İlan silindi.")
        return redirect('match-lookup-my-listings')

    return render(request, 'players/match_lookup_delete_confirm.html', {'lookup': lookup})


@login_required
def match_lookup_accept_response(request, response_id):
    """Gelen yanıtı kabul et"""

    response = get_object_or_404(MatchLookupResponse, pk=response_id)
    lookup = response.lookup

    # Sadece ilan sahibi kabul edebilir
    if request.user != lookup.player.user:
        messages.error(request, "❌ Bu işlemi yapamazsınız.")
        return redirect('home')

    # --- DÜZELTME (YENİ KONTROL) ---
    # Eğer ilan zaten başkasıyla eşleşmişse işlemi durdur
    if lookup.status == 'matched':
        messages.error(request, "⚠️ Bu ilan zaten kapandı veya başka biriyle eşleşti.")
        return redirect('match-lookup-detail', pk=lookup.pk)
    # -------------------------------

    response.status = 'accepted'
    response.save()

    # İlanı "eşleşti" olarak işaretle
    lookup.mark_as_matched()

    # Yanıt verene bildirim gönder
    Notification.objects.create(
        recipient=response.responder.user,
        match=None,
        message=f"🎉 {lookup.player.first_name} yanıtınızı kabul etti! Artık maç planlayabilirsiniz."
    )

    messages.success(request, f"✅ {response.responder.first_name} ile eşleştiniz! Artık maç ekleyebilirsiniz.")
    return redirect('match-lookup-detail', pk=lookup.pk)


@login_required
def match_lookup_reject_response(request, response_id):
    """Gelen yanıtı reddet"""

    response = get_object_or_404(MatchLookupResponse, pk=response_id)
    lookup = response.lookup

    # Sadece ilan sahibi reddedebilir
    if request.user != lookup.player.user:
        messages.error(request, "❌ Bu işlemi yapamazsınız.")
        return redirect('home')

    response.status = 'rejected'
    response.save()

    messages.info(request, "Yanıt reddedildi.")
    return redirect('match-lookup-detail', pk=lookup.pk)
