# players/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Player, Match, Notification, Court

# 1. Genel Admin Başlıkları
admin.site.site_header = "Courtmax Yönetim Paneli"
admin.site.site_title = "Courtmax Admin"
admin.site.index_title = "Yönetim Paneline Hoş Geldiniz"

# --- USER & PLAYER ENTEGRASYONU ---
# Kullanıcı paneline "Oyuncu Profili"ni ekleyelim (Inline)
class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'Oyuncu Profili'
    fk_name = 'user'

# Varsayılan User admin'i iptal edip, kendi versiyonumuzu (Inline eklenmiş) kaydediyoruz
class UserAdmin(BaseUserAdmin):
    inlines = (PlayerInline,)
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_player_city', 'is_staff')
    
    def get_player_city(self, obj):
        # Eğer kullanıcının oyuncu profili varsa şehrini göster
        return obj.player.city if hasattr(obj, 'player') else "-"
    get_player_city.short_description = "Şehir (Oyuncu)"

# Önce varsayılanı kaldır, sonra yenisini ekle
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- DİĞER MODELLER ---

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('username_display', 'full_name', 'skill_level', 'rating', 'city')
    list_filter = ('skill_level', 'city')
    search_fields = ('user__username', 'first_name', 'last_name', 'city')
    ordering = ('-rating',) # Puana göre sıralı gelsin

    def username_display(self, obj):
        return obj.user.username
    username_display.short_description = "Kullanıcı Adı"

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Ad Soyad"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_id_display', 'match_date', 'court', 'score_display', 'is_confirmed')
    list_filter = ('is_confirmed', 'is_rated', 'match_date', 'court')
    search_fields = ('court__name', 'created_by__username')
    date_hierarchy = 'match_date' # Tarih bazlı hızlı gezinme çubuğu
    filter_horizontal = ('team1_players', 'team2_players') # Çoklu seçim kutusu
    
    def match_id_display(self, obj):
        return f"Maç #{obj.id}"
    match_id_display.short_description = "ID"

    def score_display(self, obj):
        return f"{obj.score_team1} - {obj.score_team2}"
    score_display.short_description = "Skor"


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    list_filter = ('city',)
    search_fields = ('name', 'city')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')