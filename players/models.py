# players/models.py

from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    # --- PADEL SEVİYE SEÇENEKLERİ ---
    SKILL_CHOICES = [
        ('0-1.0 Beginner', '🟩 0 – 1.0: Tam Başlangıç (Beginner)'),
        ('1.5 Novice', '🟩 1.5: Yeni Öğrenen (Novice)'),
        ('2.0-2.5 Improver', '🟨 2.0 – 2.5: Gelişen Oyuncu (Improver)'),
        ('3.0 Intermediate', '🟨 3.0: Orta Seviye (Intermediate)'),
        ('3.5 Upper Intermediate', '🟨 3.5: Orta-Üst Seviye (Upper Intermediate)'),
        ('4.0 Advanced', '🟧 4.0: İyi Seviye (Advanced)'),
        ('4.5 High Advanced', '🟧 4.5: İleri (High Advanced)'),
        ('5.0 Semi Pro', '🟥 5.0: Yarı-Pro (Semi Pro)'),
        ('5.5-6.0 Pro', '🟥 5.5 – 6.0: Pro (Professional)'),
        ('6.5-7.0 Elite', '🟥 6.5 – 7.0: Elit / Dünya Sınıfı'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, default='', blank=True)
    city = models.CharField(max_length=100, default='')

    # Seviye Alanı
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
    
    # Maçı sisteme giren kişi (Kurucu)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_matches', null=True)
    
    team1_players = models.ManyToManyField(Player, related_name="team1_matches", blank=True)
    team2_players = models.ManyToManyField(Player, related_name="team2_matches", blank=True)
    
    score_team1 = models.IntegerField(default=0)
    score_team2 = models.IntegerField(default=0)
    
    # Puanlandı mı? (Sonsuz döngü ve tekrar puanlama koruması)
    is_rated = models.BooleanField(default=False)
    
    # Maç Onaylandı mı? (Yeterli çoğunluk sağlandı mı?)
    is_confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Maç - {self.match_date.strftime('%d %b %H:%M')}"

    # --- YENİ EKLENEN KONSENSÜS MANTIĞI ---
    def check_consensus_and_calculate(self):
        """
        Oyuncuların %74'ü onayladıysa puanları hesaplar.
        Bu fonksiyon her 'Onayla' butonuna basıldığında çağrılmalıdır.
        """
        # 1. GÜVENLİK: Zaten puanlandıysa işlem yapma
        if self.is_rated:
            return

        # 2. Toplam Oyuncu Sayısını Bul
        total_players = self.team1_players.count() + self.team2_players.count()
        if total_players == 0: return 

        # 3. Onaylayanları Say
        # A) Maçı kuran kişi (created_by) zaten doğal olarak onaylamıştır (+1)
        approval_count = 1 
        
        # B) Bildirimleri "Okundu/Onaylandı" (is_read=True) olanları say
        # (Notification modeline ters ilişki ile erişiyoruz)
        approved_notifications = self.notification_set.filter(is_read=True).count()
        approval_count += approved_notifications

        # 4. Oranı Hesapla
        approval_ratio = approval_count / total_players
        
        # Eşik Değer: %74 (0.74)
        # Örn: 4 oyuncu varsa, 3 kişi onaylarsa (3/4 = 0.75) eşik geçilir.
        if approval_ratio >= 0.74:
            self.calculate_ratings() # Puanları hesapla
            self.is_confirmed = True # Maçı resmen onayla
            self.save()

    def calculate_ratings(self):
        """ Puan hesaplama mantığı (Sadece yukarıdaki fonksiyon çağırır) """
        # İkinci bir güvenlik kontrolü
        if self.is_rated:
            return
        
        if self.score_team1 == self.score_team2:
            return

        # Sizin belirlediğiniz puanlar
        WIN_POINTS = 150
        LOSE_POINTS = 100

        if self.score_team1 > self.score_team2:
            winners = self.team1_players.all()
            losers = self.team2_players.all()
        else:
            winners = self.team2_players.all()
            losers = self.team1_players.all()
        
        if not winners or not losers:
            return

        for player in winners:
            player.rating += WIN_POINTS
            player.save()

        for player in losers:
            player.rating -= LOSE_POINTS
            player.save()

        # İŞLEM BİTTİ: Kilidi kapat
        self.is_rated = True
        self.save()

# BİLDİRİM MODELİ
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False) # True olduğunda "Onaylandı" kabul edilir
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"