# players/serializers.py

from rest_framework import serializers
from .models import Player, Match, Notification
from django.contrib.auth.models import User

# Django'nun kendi User modelini serileştiriyoruz (Gerekli temel bilgiler)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class PlayerSerializer(serializers.ModelSerializer):
    # Oyuncu profilini çekerken kullanıcı adını da dahil ediyoruz
    user = UserSerializer(read_only=True) 

    class Meta:
        model = Player
        fields = ['id', 'user', 'city', 'skill_level', 'rating']

class MatchSerializer(serializers.ModelSerializer):
    # Takımları çekerken her oyuncunun detayını göstermek için PlayerSerializer'ı kullanıyoruz
    team1_players = PlayerSerializer(many=True, read_only=True)
    team2_players = PlayerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'created_by', 'match_date', 'score_team1', 'score_team2', 
            'is_confirmed', 'team1_players', 'team2_players'
        ]