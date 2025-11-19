# players/admin.py

from django.contrib import admin
from .models import Player, Match

# Player modelini admin paneline kaydediyoruz
admin.site.register(Player)

# Match modelini daha gelişmiş seçeneklerle kaydediyoruz
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_date', 'score_team1', 'score_team2')
    
    # Bu, 'Çoka-Çok' alanlarımızı admin panelinde
    # çok daha kullanışlı bir "seçim kutusu" olarak gösterir.
    filter_horizontal = ('team1_players', 'team2_players')

# Not: admin.site.register(Match) satırını sildik çünkü
#      yukarıdaki @admin.register(Match) dekoratörü
#      artık onun yerini alıyor.