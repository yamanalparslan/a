# players/admin.py

from django.contrib import admin
from .models import Player, Match, Notification, Court

admin.site.register(Player)
admin.site.register(Notification)
admin.site.register(Court)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_date', 'court', 'score_team1', 'score_team2') 
    filter_horizontal = ('team1_players', 'team2_players')
