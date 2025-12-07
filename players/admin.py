from django.contrib import admin
from .models import Player, Match, Court, Notification

# Admin site customization
admin.site.site_header = "Courtmax Padel Mate Admin"
admin.site.site_title = "Admin Paneli"
admin.site.index_title = "Hoş Geldiniz"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'skill_level', 'rating', 'city']
    list_filter = ['skill_level', 'city', 'rating']
    search_fields = ['user__username', 'first_name', 'last_name', 'phone']
    readonly_fields = ['rating']
    
    fieldsets = (
        ('Kullanıcı Bilgisi', {
            'fields': ('user', 'first_name', 'last_name')
        }),
        ('İletişim', {
            'fields': ('phone', 'city')
        }),
        ('Padel Bilgisi', {
            'fields': ('skill_level', 'rating')
        }),
        ('Profil Fotoğrafı', {
            'fields': ('profile_picture',)
        }),
    )


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city']
    list_filter = ['city']
    search_fields = ['name', 'city']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'match_date', 'court', 'score_team1', 'score_team2', 'is_confirmed', 'is_rated']
    list_filter = ['match_date', 'court', 'is_confirmed', 'is_rated']
    search_fields = ['created_by__username']
    readonly_fields = ['match_date', 'score_team1', 'score_team2']
    
    fieldsets = (
        ('Maç Bilgisi', {
            'fields': ('match_date', 'created_by', 'court')
        }),
        ('Takım 1', {
            'fields': ('team1_players', 'set1_team1', 'set2_team1', 'set3_team1')
        }),
        ('Takım 2', {
            'fields': ('team2_players', 'set1_team2', 'set2_team2', 'set3_team2')
        }),
        ('Sonuç', {
            'fields': ('score_team1', 'score_team2', 'is_confirmed', 'is_rated')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'match', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['recipient__username', 'message']
    readonly_fields = ['created_at']


# players/admin.py içine eklenecek

from .models import MatchLookup, MatchLookupResponse

@admin.register(MatchLookup)
class MatchLookupAdmin(admin.ModelAdmin):
    list_display = ['player', 'looking_for', 'preferred_date', 'city', 'status', 'created_at']
    list_filter = ['status', 'looking_for', 'city', 'preferred_date']
    search_fields = ['player__first_name', 'player__last_name', 'city']
    date_hierarchy = 'preferred_date'

@admin.register(MatchLookupResponse)
class MatchLookupResponseAdmin(admin.ModelAdmin):
    list_display = ['responder', 'lookup', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['responder__first_name', 'lookup__player__first_name']