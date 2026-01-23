# players/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from unfold.admin import ModelAdmin
from .models import Player, Match, Court, Notification, MatchLookup, MatchLookupResponse

# ================================
# ADMIN PANEL GENEL AYARLARI
# ================================
admin.site.site_header = "🎾 Courtmax Padel Mate Admin"
admin.site.site_title = "Courtmax Admin Paneli"
admin.site.index_title = "Padel Yönetim Paneli - Hoş Geldiniz"


# ================================
# PLAYER ADMIN
# ================================
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = [
        'colored_id', 
        'player_info', 
        'contact_info',
        'skill_badge', 
        'rating_badge', 
        'city_badge',
        'match_count',
        'profile_status'
    ]
    list_filter = ['skill_level', 'city', 'rating']
    search_fields = ['user__username', 'first_name', 'last_name', 'phone', 'city']
    list_per_page = 25
    ordering = ['-rating']
    
    fieldsets = (
        ('👤 Kullanıcı Bilgisi', {
            'fields': ('user', 'first_name', 'last_name'),
            'classes': ('wide',)
        }),
        ('📞 İletişim', {
            'fields': ('phone', 'city'),
            'classes': ('collapse',)
        }),
        ('🎾 Padel Bilgisi', {
            'fields': ('skill_level', 'rating'),
            'classes': ('wide',)
        }),
        ('📸 Profil Fotoğrafı', {
            'fields': ('profile_picture',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = []
    
    def colored_id(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #d9f99d;">#{}</span>',
            obj.id
        )
    colored_id.short_description = 'ID'
    
    def player_info(self, obj):
        profile_pic = ''
        if obj.profile_picture:
            profile_pic = f'<img src="{obj.profile_picture.url}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px; border: 2px solid #d9f99d;">'
        
        return format_html(
            '{}<div style="display: inline-block;"><strong style="color: #fff;">{} {}</strong><br><small style="color: #94a3b8;">@{}</small></div>',
            profile_pic,
            obj.first_name,
            obj.last_name,
            obj.user.username
        )
    player_info.short_description = 'Oyuncu'
    
    def contact_info(self, obj):
        return format_html(
            '<div style="font-size: 0.9em;"><strong>📞</strong> {}</div>',
            obj.phone or '<span style="color: #94a3b8;">-</span>'
        )
    contact_info.short_description = 'İletişim'
    
    def skill_badge(self, obj):
        colors = {
            '0-1.0 Beginner': '#10b981',
            '1.5 Novice': '#10b981',
            '2.0-2.5 Improver': '#f59e0b',
            '3.0 Intermediate': '#f59e0b',
            '3.5 Upper Int': '#f59e0b',
            '4.0 Advanced': '#f97316',
            '4.5 High Advanced': '#f97316',
            '5.0 Semi Pro': '#ef4444',
            '5.5-6.0 Pro': '#ef4444',
            '6.5-7.0 Elite': '#ef4444',
        }
        color = colors.get(obj.skill_level, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold; white-space: nowrap;">{}</span>',
            color,
            obj.skill_level
        )
    skill_badge.short_description = 'Seviye'
    
    def rating_badge(self, obj):
        if obj.rating >= 1500:
            color = '#d9f99d'
            icon = '🏆'
        elif obj.rating >= 1200:
            color = '#60a5fa'
            icon = '⭐'
        elif obj.rating >= 1000:
            color = '#94a3b8'
            icon = '👍'
        else:
            color = '#64748b'
            icon = '🎯'
        
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 1.1em;">{} {}</span>',
            color,
            icon,
            obj.rating
        )
    rating_badge.short_description = 'Puan'
    
    def city_badge(self, obj):
        return format_html(
            '<span style="background-color: #1e293b; border: 1px solid #334155; color: #cbd5e1; padding: 4px 10px; border-radius: 8px; font-size: 0.85em;">📍 {}</span>',
            obj.city or '-'
        )
    city_badge.short_description = 'Şehir'
    
    def match_count(self, obj):
        team1_count = obj.team1_matches.filter(is_confirmed=True).count()
        team2_count = obj.team2_matches.filter(is_confirmed=True).count()
        total = team1_count + team2_count
        
        return format_html(
            '<span style="color: #d9f99d; font-weight: bold;">{}</span> <small style="color: #64748b;">maç</small>',
            total
        )
    match_count.short_description = 'Toplam Maç'
    
    def profile_status(self, obj):
        if obj.profile_picture:
            return format_html('<span style="color: #10b981;">✓ Var</span>')
        return format_html('<span style="color: #64748b;">✗ Yok</span>')
    profile_status.short_description = 'Profil Fotoğrafı'


# ================================
# COURT ADMIN
# ================================
@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['colored_id', 'court_name', 'city_info', 'match_count']
    list_filter = ['city']
    search_fields = ['name', 'city']
    list_per_page = 20
    
    def colored_id(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #d9f99d;">#{}</span>',
            obj.id
        )
    colored_id.short_description = 'ID'
    
    def court_name(self, obj):
        return format_html(
            '<strong style="color: #fff; font-size: 1.05em;">🏟️ {}</strong>',
            obj.name
        )
    court_name.short_description = 'Kort Adı'
    
    def city_info(self, obj):
        return format_html(
            '<span style="background-color: #1e293b; border: 1px solid #334155; color: #cbd5e1; padding: 5px 12px; border-radius: 8px;">📍 {}</span>',
            obj.city
        )
    city_info.short_description = 'Şehir'
    
    def match_count(self, obj):
        count = obj.match_set.count()
        return format_html(
            '<span style="color: #60a5fa; font-weight: bold;">{}</span> <small style="color: #64748b;">maç</small>',
            count
        )
    match_count.short_description = 'Toplam Maç'


# ================================
# MATCH ADMIN
# ================================
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        'colored_id',
        'match_date_formatted',
        'court_info',
        'score_display',
        'status_badges',
        'creator_info'
    ]
    list_filter = ['is_confirmed', 'is_rated', 'match_date', 'court']
    search_fields = ['created_by__username', 'court__name']
    readonly_fields = ['match_date', 'score_team1', 'score_team2']
    list_per_page = 25
    date_hierarchy = 'match_date'
    ordering = ['-match_date']
    
    fieldsets = (
        ('⚔️ Maç Bilgisi', {
            'fields': ('match_date', 'created_by', 'court'),
            'classes': ('wide',)
        }),
        ('🟢 Takım 1', {
            'fields': ('team1_players', 'set1_team1', 'set2_team1', 'set3_team1'),
            'classes': ('collapse',)
        }),
        ('🔴 Takım 2', {
            'fields': ('team2_players', 'set1_team2', 'set2_team2', 'set3_team2'),
            'classes': ('collapse',)
        }),
        ('📊 Sonuç', {
            'fields': ('score_team1', 'score_team2', 'is_confirmed', 'is_rated'),
            'classes': ('wide',)
        }),
    )
    
    def colored_id(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #d9f99d;">#{}</span>',
            obj.id
        )
    colored_id.short_description = 'ID'
    
    def match_date_formatted(self, obj):
        return format_html(
            '<div style="font-size: 0.95em;"><strong style="color: #fff;">{}</strong><br><small style="color: #94a3b8;">{}</small></div>',
            obj.match_date.strftime('%d %B %Y'),
            obj.match_date.strftime('%H:%M')
        )
    match_date_formatted.short_description = 'Tarih & Saat'
    
    def court_info(self, obj):
        if obj.court:
            return format_html(
                '<div style="font-size: 0.9em;"><strong style="color: #cbd5e1;">🏟️ {}</strong><br><small style="color: #64748b;">{}</small></div>',
                obj.court.name,
                obj.court.city
            )
        return format_html('<span style="color: #64748b;">-</span>')
    court_info.short_description = 'Kort'
    
    def score_display(self, obj):
        if obj.score_team1 > obj.score_team2:
            winner_color = '#10b981'
            loser_color = '#64748b'
        elif obj.score_team2 > obj.score_team1:
            winner_color = '#64748b'
            loser_color = '#10b981'
        else:
            winner_color = loser_color = '#f59e0b'
        
        return format_html(
            '<div style="text-align: center; font-size: 1.3em; font-weight: bold; font-family: monospace;">'
            '<span style="color: {};">{}</span>'
            '<span style="color: #64748b; margin: 0 5px;">-</span>'
            '<span style="color: {};">{}</span>'
            '</div>'
            '<div style="text-align: center; font-size: 0.75em; color: #64748b; margin-top: 3px;">'
            '({}-{}) ({}-{}) ({}-{})'
            '</div>',
            winner_color, obj.score_team1,
            loser_color, obj.score_team2,
            obj.set1_team1, obj.set1_team2,
            obj.set2_team1, obj.set2_team2,
            obj.set3_team1 or 0, obj.set3_team2 or 0
        )
    score_display.short_description = 'Skor'
    
    def status_badges(self, obj):
        confirmed = ''
        rated = ''
        
        if obj.is_confirmed:
            confirmed = '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.75em; margin-right: 5px;">✓ Onaylı</span>'
        else:
            confirmed = '<span style="background-color: #f59e0b; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.75em; margin-right: 5px;">⏳ Bekliyor</span>'
        
        if obj.is_rated:
            rated = '<span style="background-color: #3b82f6; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.75em;">⭐ Puanlandı</span>'
        
        return format_html(
            '<div style="white-space: nowrap;">{}{}</div>',
            confirmed,
            rated
        )
    status_badges.short_description = 'Durum'
    
    def creator_info(self, obj):
        return format_html(
            '<small style="color: #94a3b8;">@{}</small>',
            obj.created_by.username if obj.created_by else '-'
        )
    creator_info.short_description = 'Oluşturan'


# ================================
# NOTIFICATION ADMIN
# ================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['colored_id', 'recipient_info', 'message_preview', 'match_link', 'read_status', 'time_ago']
    list_filter = ['is_read', 'created_at']
    search_fields = ['recipient__username', 'message']
    readonly_fields = ['created_at']
    list_per_page = 30
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def colored_id(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #d9f99d;">#{}</span>',
            obj.id
        )
    colored_id.short_description = 'ID'
    
    def recipient_info(self, obj):
        return format_html(
            '<strong style="color: #fff;">@{}</strong>',
            obj.recipient.username
        )
    recipient_info.short_description = 'Alıcı'
    
    def message_preview(self, obj):
        max_length = 60
        message = obj.message[:max_length] + '...' if len(obj.message) > max_length else obj.message
        return format_html(
            '<span style="color: #cbd5e1; font-size: 0.9em;">{}</span>',
            message
        )
    message_preview.short_description = 'Mesaj'
    
    def match_link(self, obj):
        if obj.match:
            url = reverse('admin:players_match_change', args=[obj.match.id])
            return format_html(
                '<a href="{}" style="color: #60a5fa; text-decoration: none;">🔗 Maç #{}</a>',
                url,
                obj.match.id
            )
        return format_html('<span style="color: #64748b;">-</span>')
    match_link.short_description = 'Maç'
    
    def read_status(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.75em;">✓ Okundu</span>'
            )
        return format_html(
            '<span style="background-color: #ef4444; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.75em;">● Yeni</span>'
        )
    read_status.short_description = 'Durum'
    
    def time_ago(self, obj):
        from django.utils import timezone
        diff = timezone.now() - obj.created_at
        
        if diff.days > 0:
            return format_html(
                '<small style="color: #64748b;">{} gün önce</small>',
                diff.days
            )
        elif diff.seconds >= 3600:
            return format_html(
                '<small style="color: #64748b;">{} saat önce</small>',
                diff.seconds // 3600
            )
        else:
            return format_html(
                '<small style="color: #64748b;">{} dk önce</small>',
                diff.seconds // 60
            )
    time_ago.short_description = 'Zaman'


# ================================
# MATCH LOOKUP ADMIN
# ================================
@admin.register(MatchLookup)
class MatchLookupAdmin(admin.ModelAdmin):
    list_display = [
        'colored_id',
        'player_info',
        'looking_for_badge',
        'date_info',
        'location_info',
        'status_badge',
        'response_count'
    ]
    list_filter = ['status', 'looking_for', 'city', 'preferred_date']
    search_fields = ['player__first_name', 'player__last_name', 'city', 'description']
    date_hierarchy = 'preferred_date'
    list_per_page = 25
    ordering = ['-created_at']
    
    def colored_id(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #d9f99d;">#{}</span>',
            obj.id
        )
    colored_id.short_description = 'ID'
    
    def player_info(self, obj):
        return format_html(
            '<strong style="color: #fff;">{} {}</strong><br><small style="color: #94a3b8;">@{}</small>',
            obj.player.first_name,
            obj.player.last_name,
            obj.player.user.username
        )
    player_info.short_description = 'Oyuncu'
    
    def looking_for_badge(self, obj):
        colors = {
            'partner': '#3b82f6',
            'opponents': '#ef4444',
            'both': '#10b981'
        }
        icons = {
            'partner': '🤝',
            'opponents': '⚔️',
            'both': '🎯'
        }
        color = colors.get(obj.looking_for, '#64748b')
        icon = icons.get(obj.looking_for, '❓')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_looking_for_display()
        )
    looking_for_badge.short_description = 'Aranan'
    
    def date_info(self, obj):
        return format_html(
            '<div style="font-size: 0.9em;"><strong style="color: #cbd5e1;">📅 {}</strong><br><small style="color: #64748b;">{} - {}</small></div>',
            obj.preferred_date.strftime('%d %b %Y'),
            obj.preferred_time_start.strftime('%H:%M') if obj.preferred_time_start else '-',
            obj.preferred_time_end.strftime('%H:%M') if obj.preferred_time_end else '-'
        )
    date_info.short_description = 'Tarih & Saat'
    
    def location_info(self, obj):
        court = obj.preferred_court.name if obj.preferred_court else 'Farketmez'
        return format_html(
            '<div style="font-size: 0.9em;"><strong style="color: #cbd5e1;">📍 {}</strong><br><small style="color: #64748b;">{}</small></div>',
            obj.city,
            court
        )
    location_info.short_description = 'Konum'
    
    def status_badge(self, obj):
        colors = {
            'active': '#10b981',
            'matched': '#3b82f6',
            'expired': '#64748b',
            'cancelled': '#ef4444'
        }
        color = colors.get(obj.status, '#64748b')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.75em; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'
    
    def response_count(self, obj):
        count = obj.responses.count()
        pending = obj.responses.filter(status='pending').count()
        
        return format_html(
            '<span style="color: #d9f99d; font-weight: bold;">{}</span> <small style="color: #64748b;">yanıt</small><br>'
            '<small style="color: #f59e0b;">{} bekliyor</small>',
            count,
            pending
        )
    response_count.short_description = 'Yanıtlar'


# ================================
# MATCH LOOKUP RESPONSE ADMIN
# ================================
@admin.register(MatchLookupResponse)
class MatchLookupResponseAdmin(admin.ModelAdmin):
    list_display = [
        'colored_id',
        'responder_info',
        'lookup_info',
        'message_preview',
        'status_badge',
        'time_ago'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['responder__first_name', 'responder__last_name', 'message']
    list_per_page = 25
    ordering = ['-created_at']
    
    def colored_id(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #d9f99d;">#{}</span>',
            obj.id
        )
    colored_id.short_description = 'ID'
    
    def responder_info(self, obj):
        return format_html(
            '<strong style="color: #fff;">{} {}</strong><br><small style="color: #94a3b8;">@{}</small>',
            obj.responder.first_name,
            obj.responder.last_name,
            obj.responder.user.username
        )
    responder_info.short_description = 'Yanıtlayan'
    
    def lookup_info(self, obj):
        url = reverse('admin:players_matchlookup_change', args=[obj.lookup.id])
        return format_html(
            '<a href="{}" style="color: #60a5fa; text-decoration: none;">🔗 İlan #{}</a><br>'
            '<small style="color: #64748b;">{}</small>',
            url,
            obj.lookup.id,
            obj.lookup.get_looking_for_display()
        )
    lookup_info.short_description = 'İlan'
    
    def message_preview(self, obj):
        if obj.message:
            max_length = 50
            message = obj.message[:max_length] + '...' if len(obj.message) > max_length else obj.message
            return format_html(
                '<span style="color: #cbd5e1; font-size: 0.85em; font-style: italic;">"{}"</span>',
                message
            )
        return format_html('<span style="color: #64748b;">-</span>')
    message_preview.short_description = 'Mesaj'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'accepted': '#10b981',
            'rejected': '#ef4444'
        }
        color = colors.get(obj.status, '#64748b')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.75em; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'
    
    def time_ago(self, obj):
        from django.utils import timezone
        diff = timezone.now() - obj.created_at
        
        if diff.days > 0:
            return format_html(
                '<small style="color: #64748b;">{} gün önce</small>',
                diff.days
            )
        elif diff.seconds >= 3600:
            return format_html(
                '<small style="color: #64748b;">{} saat önce</small>',
                diff.seconds // 3600
            )
        else:
            return format_html(
                '<small style="color: #64748b;">{} dk önce</small>',
                diff.seconds // 60
            )
    time_ago.short_description = 'Zaman'