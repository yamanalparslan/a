# players/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
# --- ÖNEMLİ DEĞİŞİKLİK: Unfold ModelAdmin import edildi ---
from unfold.admin import ModelAdmin 
from .models import Player, Match, Court, Notification, MatchLookup, MatchLookupResponse

admin.site.site_header = "🎾 Courtmax Padel Mate Admin"
admin.site.site_title = "Courtmax Admin Paneli"
admin.site.index_title = "Padel Yönetim Paneli - Hoş Geldiniz"

# ================================
# PLAYER ADMIN
# ================================
@admin.register(Player)
class PlayerAdmin(ModelAdmin):  # <--- (Eski: admin.ModelAdmin)
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
    
    # Unfold özellikleri
    list_fullwidth = True
    
    def colored_id(self, obj):
        return format_html(
            '<span class="font-bold text-green-600">#{}</span>',
            obj.id
        )
    colored_id.short_description = 'ID'
    
    def player_info(self, obj):
        img_html = ''
        if obj.profile_picture:
            img_html = f'<img src="{obj.profile_picture.url}" class="w-8 h-8 rounded-full border border-gray-200 mr-2 object-cover">'
        else:
             img_html = f'<div class="w-8 h-8 rounded-full bg-gray-800 border border-gray-600 mr-2 flex items-center justify-center text-xs text-white font-bold">{obj.first_name[0].upper()}</div>'
        
        return format_html(
            '<div class="flex items-center">{}<div><div class="font-medium text-gray-900 dark:text-gray-200">{} {}</div><div class="text-xs text-gray-500">@{}</div></div></div>',
            format_html(img_html),
            obj.first_name,
            obj.last_name,
            obj.user.username
        )
    player_info.short_description = 'Oyuncu'
    
    def contact_info(self, obj):
        return format_html(
            '<div class="text-sm"><span class="mr-1">📞</span>{}</div>',
            obj.phone or '-'
        )
    contact_info.short_description = 'İletişim'
    
    def skill_badge(self, obj):
        colors = {
            '0-1.0 Beginner': 'bg-emerald-500',
            '1.5 Novice': 'bg-emerald-500',
            '2.0-2.5 Improver': 'bg-amber-500',
            '3.0 Intermediate': 'bg-amber-500',
            '3.5 Upper Int': 'bg-amber-500',
            '4.0 Advanced': 'bg-orange-500',
            '4.5 High Advanced': 'bg-orange-500',
            '5.0 Semi Pro': 'bg-red-500',
            '5.5-6.0 Pro': 'bg-red-500',
            '6.5-7.0 Elite': 'bg-red-600',
        }
        bg_class = colors.get(obj.skill_level, 'bg-slate-500')
        return format_html(
            '<span class="{} text-white px-2 py-0.5 rounded text-xs font-bold whitespace-nowrap">{}</span>',
            bg_class,
            obj.skill_level.split(' ')[0]
        )
    skill_badge.short_description = 'Seviye'
    
    def rating_badge(self, obj):
        color_class = "text-slate-500"
        icon = '🎯'
        if obj.rating >= 1500:
            color_class = "text-lime-500"
            icon = '🏆'
        elif obj.rating >= 1200:
            color_class = "text-blue-500"
            icon = '⭐'
        elif obj.rating >= 1000:
            color_class = "text-slate-400"
            icon = '👍'
            
        return format_html(
            '<span class="{} font-bold text-sm">{} {}</span>',
            color_class, icon, obj.rating
        )
    rating_badge.short_description = 'Puan'
    
    def city_badge(self, obj):
        return format_html(
            '<span class="px-2 py-1 rounded bg-gray-700 text-gray-200 text-xs">📍 {}</span>',
            obj.city or '-'
        )
    city_badge.short_description = 'Şehir'
    
    def match_count(self, obj):
        team1_count = obj.team1_matches.filter(is_confirmed=True).count()
        team2_count = obj.team2_matches.filter(is_confirmed=True).count()
        total = team1_count + team2_count
        return format_html(
            '<span class="text-lime-500 font-bold">{}</span> <small class="text-gray-500">maç</small>',
            total
        )
    match_count.short_description = 'Maç'
    
    def profile_status(self, obj):
        if obj.profile_picture:
            return format_html('<span class="text-emerald-500 text-xs">✓ Var</span>')
        return format_html('<span class="text-slate-500 text-xs">✗ Yok</span>')
    profile_status.short_description = 'Foto'


# ================================
# COURT ADMIN
# ================================
@admin.register(Court)
class CourtAdmin(ModelAdmin):
    list_display = ['colored_id', 'court_name', 'city_info', 'match_count']
    list_filter = ['city']
    search_fields = ['name', 'city']
    list_per_page = 20
    
    def colored_id(self, obj):
        return format_html('<span class="font-bold text-green-600">#{}</span>', obj.id)
    colored_id.short_description = 'ID'
    
    def court_name(self, obj):
        return format_html('<strong class="text-gray-200 text-base">🏟️ {}</strong>', obj.name)
    court_name.short_description = 'Kort Adı'
    
    def city_info(self, obj):
        return format_html('<span class="px-2 py-1 rounded bg-gray-700 text-gray-200 text-xs">📍 {}</span>', obj.city)
    city_info.short_description = 'Şehir'
    
    def match_count(self, obj):
        count = obj.match_set.count()
        return format_html('<span class="text-blue-400 font-bold">{}</span> <small class="text-gray-500">maç</small>', count)
    match_count.short_description = 'Toplam Maç'


# ================================
# MATCH ADMIN
# ================================
@admin.register(Match)
class MatchAdmin(ModelAdmin):
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
    
    # Unfold Fieldsets (Collapse özelliği için classes aynı kalabilir)
    fieldsets = (
        ('⚔️ Maç Bilgisi', {
            'fields': ('match_date', 'created_by', 'court'),
            'classes': ('tab',), # Unfold tab özelliği
        }),
        ('Skor Detayları', {
            'fields': ('score_team1', 'score_team2', 'set1_team1', 'set1_team2', 'set2_team1', 'set2_team2', 'set3_team1', 'set3_team2'),
            'classes': ('tab',),
        }),
        ('Durum', {
             'fields': ('is_confirmed', 'is_rated'),
             'classes': ('tab',),
        }),
    )
    
    def colored_id(self, obj):
        return format_html('<span class="font-bold text-green-600">#{}</span>', obj.id)
    colored_id.short_description = 'ID'
    
    def match_date_formatted(self, obj):
        return format_html(
            '<div><div class="font-medium text-gray-200">{}</div><div class="text-xs text-gray-500">{}</div></div>',
            obj.match_date.strftime('%d %B %Y'),
            obj.match_date.strftime('%H:%M')
        )
    match_date_formatted.short_description = 'Tarih'
    
    def court_info(self, obj):
        if obj.court:
            return format_html(
                '<div><div class="text-gray-300">🏟️ {}</div><div class="text-xs text-gray-500">{}</div></div>',
                obj.court.name, obj.court.city
            )
        return format_html('<span class="text-gray-500">-</span>')
    court_info.short_description = 'Kort'
    
    def score_display(self, obj):
        w_color = "text-emerald-500"
        l_color = "text-slate-400"
        
        c1 = w_color if obj.score_team1 > obj.score_team2 else l_color
        c2 = w_color if obj.score_team2 > obj.score_team1 else l_color
        
        return format_html(
            '<div class="flex flex-col items-center">'
            '<div class="text-lg font-mono font-bold tracking-widest">'
            '<span class="{}">{}</span><span class="text-gray-600 mx-1">-</span><span class="{}">{}</span>'
            '</div>'
            '<div class="text-xs text-gray-500 mt-1">({}-{}) ({}-{})</div>'
            '</div>',
            c1, obj.score_team1,
            c2, obj.score_team2,
            obj.set1_team1, obj.set1_team2,
            obj.set2_team1, obj.set2_team2
        )
    score_display.short_description = 'Skor'
    
    def status_badges(self, obj):
        badges = ""
        if obj.is_confirmed:
            badges += '<span class="bg-green-600/20 text-green-400 border border-green-600/30 px-2 py-0.5 rounded text-xs mr-1">✓ Onaylı</span>'
        else:
            badges += '<span class="bg-amber-600/20 text-amber-400 border border-amber-600/30 px-2 py-0.5 rounded text-xs mr-1">⏳ Bekliyor</span>'
        
        if obj.is_rated:
            badges += '<span class="bg-blue-600/20 text-blue-400 border border-blue-600/30 px-2 py-0.5 rounded text-xs">⭐ Puanlandı</span>'
            
        return format_html('<div class="flex items-center">{}</div>', format_html(badges))
    status_badges.short_description = 'Durum'
    
    def creator_info(self, obj):
        return format_html('<small class="text-gray-400">@{}</small>', obj.created_by.username if obj.created_by else '-')
    creator_info.short_description = 'Oluşturan'


# ================================
# NOTIFICATION ADMIN
# ================================
@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ['colored_id', 'recipient_info', 'message_preview', 'read_status', 'time_ago']
    list_filter = ['is_read', 'created_at']
    search_fields = ['recipient__username', 'message']
    
    def colored_id(self, obj):
        return format_html('<span class="font-bold text-green-600">#{}</span>', obj.id)
    colored_id.short_description = 'ID'
    
    def recipient_info(self, obj):
        return format_html('<strong class="text-gray-200">@{}</strong>', obj.recipient.username)
    recipient_info.short_description = 'Alıcı'
    
    def message_preview(self, obj):
        return format_html('<span class="text-gray-400 text-sm">{}</span>', obj.message[:50])
    message_preview.short_description = 'Mesaj'
    
    def read_status(self, obj):
        if obj.is_read:
             return format_html('<span class="text-xs bg-green-900 text-green-300 px-2 py-1 rounded">Okundu</span>')
        return format_html('<span class="text-xs bg-red-900 text-red-300 px-2 py-1 rounded">Yeni</span>')
    read_status.short_description = 'Durum'
    
    def time_ago(self, obj):
        from django.utils import timezone
        diff = timezone.now() - obj.created_at
        if diff.days > 0: return f"{diff.days} gün önce"
        return "Bugün"
    time_ago.short_description = 'Zaman'


# ================================
# MATCH LOOKUP ADMIN
# ================================
@admin.register(MatchLookup)
class MatchLookupAdmin(ModelAdmin):
    list_display = ['colored_id', 'player_info', 'looking_for_badge', 'location_info', 'status_badge']
    list_filter = ['status', 'looking_for', 'city']
    
    def colored_id(self, obj):
        return format_html('<span class="font-bold text-green-600">#{}</span>', obj.id)
    colored_id.short_description = 'ID'

    def player_info(self, obj):
        return format_html(
            '<strong class="text-gray-200">{} {}</strong><br><small class="text-gray-400">@{}</small>',
            obj.player.first_name, obj.player.last_name, obj.player.user.username
        )
    player_info.short_description = 'Oyuncu'

    def looking_for_badge(self, obj):
        color = "bg-gray-600"
        if obj.looking_for == 'partner': color = "bg-blue-600"
        elif obj.looking_for == 'opponents': color = "bg-red-600"
        elif obj.looking_for == 'both': color = "bg-green-600"
        
        return format_html(
            '<span class="{} text-white px-2 py-1 rounded text-xs font-bold">{}</span>',
            color, obj.get_looking_for_display()
        )
    looking_for_badge.short_description = 'Aranan'
    
    def location_info(self, obj):
        return format_html(
            '<div class="text-sm"><span class="text-gray-300">📍 {}</span></div>',
            obj.city
        )
    location_info.short_description = 'Konum'

    def status_badge(self, obj):
        color = "bg-gray-600"
        if obj.status == 'active': color = "bg-green-600"
        elif obj.status == 'matched': color = "bg-blue-600"
        elif obj.status == 'expired': color = "bg-yellow-600"
        elif obj.status == 'cancelled': color = "bg-red-600"
        
        return format_html(
            '<span class="{} text-white px-2 py-1 rounded text-xs">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Durum'


@admin.register(MatchLookupResponse)
class MatchLookupResponseAdmin(ModelAdmin):
    list_display = ['id', 'responder', 'status', 'created_at']