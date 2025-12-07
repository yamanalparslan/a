# players/models.py

from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils import timezone
from datetime import timedelta

# --- YENİ MODEL: KORTLAR ---
class Court(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kort Adı")
    city = models.CharField(max_length=100, default="İzmir", verbose_name="Şehir")
    
    def __str__(self):
        return f"{self.name} ({self.city})"

class Player(models.Model):
    # --- PADEL SEVİYE SEÇENEKLERİ ---
    SKILL_CHOICES = [
        ('0-1.0 Beginner', '🟩 0 – 1.0: Tam Başlangıç (Beginner)'),
        ('1.5 Novice', '🟩 1.5: Yeni Öğrenen (Novice)'),
        ('2.0-2.5 Improver', '🟨 2.0 – 2.5: Gelişen Oyuncu (Improver)'),
        ('3.0 Intermediate', '🟨 3.0: Orta Seviye (Intermediate)'),
        ('3.5 Upper Int', '🟨 3.5: Orta-Üst Seviye (Upper Int)'),
        ('4.0 Advanced', '🟧 4.0: İyi Seviye (Advanced)'),
        ('4.5 High Advanced', '🟧 4.5: İleri (High Advanced)'),
        ('5.0 Semi Pro', '🟥 5.0: Yarı-Pro (Semi Pro)'),
        ('5.5-6.0 Pro', '🟥 5.5 – 6.0: Pro (Professional)'),
        ('6.5-7.0 Elite', '🟥 6.5 – 7.0: Elit / Dünya Sınıfı'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Profil Fotoğrafı
    profile_picture = CloudinaryField('image', folder='avatars', blank=True, null=True)

    phone = models.CharField(max_length=20, default='', blank=True)
    city = models.CharField(max_length=100, default='')

    skill_level = models.CharField(
        max_length=100,
        choices=SKILL_CHOICES,
        default='0-1.0 Beginner'
    )

    rating = models.IntegerField(default=1000)

    def __str__(self):
        return f"{self.user.username} ({self.rating})"


class Match(models.Model):
    match_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_matches', null=True)
    
    # --- YENİ EKLENEN ALAN: KORT BİLGİSİ ---
    # Kort silinirse maç silinmez, sadece boş kalır (SET_NULL)
    court = models.ForeignKey(Court, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Oynanan Kort")

    team1_players = models.ManyToManyField(Player, related_name="team1_matches", blank=True)
    team2_players = models.ManyToManyField(Player, related_name="team2_matches", blank=True)
    
    # Set Skorları
    set1_team1 = models.IntegerField(default=0)
    set1_team2 = models.IntegerField(default=0)
    
    set2_team1 = models.IntegerField(default=0)
    set2_team2 = models.IntegerField(default=0)
    
    set3_team1 = models.IntegerField(default=0, blank=True, null=True)
    set3_team2 = models.IntegerField(default=0, blank=True, null=True)

    # Maç Sonucu (Hesaplanan)
    score_team1 = models.IntegerField(default=0)
    score_team2 = models.IntegerField(default=0)
    
    is_rated = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Maç - {self.match_date.strftime('%d %b %H:%M')}"

    # --- OTOMATİK SKOR HESAPLAMA ---
    def calculate_set_winner(self):
        """Set skorlarına bakarak maç sonucunu (2-0, 2-1 vb.) hesaplar."""
        t1_sets = 0
        t2_sets = 0

        # Set 1
        if self.set1_team1 > self.set1_team2: t1_sets += 1
        elif self.set1_team2 > self.set1_team1: t2_sets += 1

        # Set 2
        if self.set2_team1 > self.set2_team2: t1_sets += 1
        elif self.set2_team2 > self.set2_team1: t2_sets += 1

        # Set 3
        if self.set3_team1 is not None and self.set3_team2 is not None:
            if self.set3_team1 > 0 or self.set3_team2 > 0:
                if self.set3_team1 > self.set3_team2: t1_sets += 1
                elif self.set3_team2 > self.set3_team1: t2_sets += 1

        self.score_team1 = t1_sets
        self.score_team2 = t2_sets
        self.save()

    # --- KONSENSÜS VE PUANLAMA ---
    def check_consensus_and_calculate(self):
        if self.is_rated: return

        total_players = self.team1_players.count() + self.team2_players.count()
        if total_players == 0: return 

        approval_count = 1 
        approved_notifications = self.notification_set.filter(is_read=True).count()
        approval_count += approved_notifications

        approval_ratio = approval_count / total_players
        
        if approval_ratio >= 0.74:
            self.calculate_ratings()
            self.is_confirmed = True
            self.save()

    def calculate_ratings(self):
        if self.is_rated: return
        
        self.calculate_set_winner()

        if self.score_team1 == self.score_team2: return

        WIN_POINTS = 150
        LOSE_POINTS = 100

        if self.score_team1 > self.score_team2:
            winners = self.team1_players.all()
            losers = self.team2_players.all()
        else:
            winners = self.team2_players.all()
            losers = self.team1_players.all()
        
        for player in winners:
            player.rating += WIN_POINTS
            player.save()

        for player in losers:
            player.rating = max(0, player.rating - LOSE_POINTS)
            player.save()

        self.is_rated = True
        self.save()


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"
    
# players/models.py içine eklenecek

from django.utils import timezone
from datetime import timedelta

class MatchLookup(models.Model):
    """Maç arama ilanları - Oyuncular partner veya rakip bulabilir"""
    
    LOOKING_FOR_CHOICES = [
        ('partner', '🤝 Takım Arkadaşı Arıyorum'),
        ('opponents', '⚔️ Rakip Arıyorum'),
        ('both', '🎯 Her İkisi de Olur'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('matched', 'Eşleşti'),
        ('expired', 'Süresi Doldu'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    # Kim arıyor?
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='match_lookups')
    
    # Ne arıyor?
    looking_for = models.CharField(max_length=20, choices=LOOKING_FOR_CHOICES, default='both')
    
    # Ne zaman?
    preferred_date = models.DateField(verbose_name="Tercih Edilen Tarih")
    preferred_time_start = models.TimeField(verbose_name="Başlangıç Saati", null=True, blank=True)
    preferred_time_end = models.TimeField(verbose_name="Bitiş Saati", null=True, blank=True)
    
    # Nerede?
    city = models.CharField(max_length=100, verbose_name="Şehir")
    preferred_court = models.ForeignKey(Court, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tercih Edilen Kort")
    
    # Hangi seviyede?
    skill_level_min = models.CharField(max_length=100, verbose_name="Min. Seviye", blank=True)
    skill_level_max = models.CharField(max_length=100, verbose_name="Maks. Seviye", blank=True)
    
    # Açıklama
    description = models.TextField(max_length=500, blank=True, verbose_name="Not/Açıklama")
    
    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Tarih bilgileri
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(verbose_name="Son Geçerlilik")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Maç Arama İlanı"
        verbose_name_plural = "Maç Arama İlanları"
    
    def __str__(self):
        return f"{self.player.first_name} - {self.get_looking_for_display()} ({self.preferred_date})"
    
    def save(self, *args, **kwargs):
        # İlk kaydedildiğinde otomatik olarak 7 gün sonra bitir
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    def is_active(self):
        """İlan hala aktif mi?"""
        return self.status == 'active' and self.expires_at > timezone.now()
    
    def mark_as_matched(self):
        """İlan eşleştiğinde çağrılır"""
        self.status = 'matched'
        self.save()
    
    def can_contact(self, requesting_player):
        """Başka bir oyuncu bu ilana yanıt verebilir mi?"""
        # Kendi ilanına yanıt veremez
        if requesting_player == self.player:
            return False
        # İlan aktif olmalı
        if not self.is_active():
            return False
        return True


class MatchLookupResponse(models.Model):
    """İlanlara gelen yanıtlar"""
    
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
    ]
    
    lookup = models.ForeignKey(MatchLookup, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='lookup_responses')
    message = models.TextField(max_length=300, blank=True, verbose_name="Mesaj")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['lookup', 'responder']  # Aynı kişi 2 kere yanıt veremesin
    
    def __str__(self):
        return f"{self.responder.first_name} → {self.lookup.player.first_name} ({self.status})"