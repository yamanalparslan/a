# players/models.py

from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default='')
    skill_level = models.CharField(max_length=100, default='')
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
    
    # Puanlandı mı? (Sonsuz döngü koruması)
    is_rated = models.BooleanField(default=False)
    
    # YENİ: Maç Onaylandı mı?
    # False ise "Davet gönderildi, cevap bekleniyor" demektir.
    is_confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Maç - {self.match_date.strftime('%d %b %H:%M')}"

    def calculate_ratings(self):
        """ Puan hesaplama mantığı (Sadece onaylandığında çalışır) """
        if self.is_rated or not self.is_confirmed: # Onaylanmamışsa hesaplama!
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

        for player in winners:
            player.rating += WIN_POINTS
            player.save()

        for player in losers:
            player.rating -= LOSE_POINTS
            player.save()

        self.is_rated = True
        self.save()

# YENİ MODEL: BİLDİRİMLER
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications') # Kime gidecek?
    match = models.ForeignKey(Match, on_delete=models.CASCADE) # Hangi maç için?
    message = models.CharField(max_length=255) # Mesaj içeriği
    is_read = models.BooleanField(default=False) # Okundu/Onaylandı mı?
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"