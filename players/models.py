# players/models.py

from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField # Cloudinary kütüphanesi

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
    
    # YENİ EKLENEN ALAN: Profil Fotoğrafı
    # Cloudinary üzerinde 'avatars' klasöründe tutulacak.
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

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_matches',
        null=True
    )

    team1_players = models.ManyToManyField(Player, related_name="team1_matches", blank=True)
    team2_players = models.ManyToManyField(Player, related_name="team2_matches", blank=True)

    score_team1 = models.IntegerField(default=0)
    score_team2 = models.IntegerField(default=0)

    is_rated = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Maç - {self.match_date.strftime('%d %b %H:%M')}"

    # --- KONSENSÜS VE PUANLAMA ---
    def check_consensus_and_calculate(self):
        """
        Oyuncuların %74'ü onayladıysa puanları hesaplar.
        """
        if self.is_rated:
            return

        total_players = self.team1_players.count() + self.team2_players.count()
        if total_players == 0:
            return

        # Onaylayanlar: kurucu + bildirim onaylayanlar
        approval_count = 1
        approved_notifications = self.notification_set.filter(is_read=True).count()
        approval_count += approved_notifications

        approval_ratio = approval_count / total_players

        if approval_ratio >= 0.74:
            self.calculate_ratings()
            self.is_confirmed = True
            self.save()

    def calculate_ratings(self):
        """ Puan hesaplama mantığı """
        if self.is_rated:
            return

        if self.score_team1 == self.score_team2:
            return

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

        # Kazananlara puan ekle
        for player in winners:
            player.rating += WIN_POINTS
            player.save()

        # Kaybedenlerden puan düş (0 altına inmeyecek)
        for player in losers:
            player.rating = max(0, player.rating - LOSE_POINTS)
            player.save()

        # İşaretle ve kapat
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