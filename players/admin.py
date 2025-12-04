from django.contrib import admin
from .models import Player  # Modelin adını Player olarak yazıyorum, sizinkinin adına göre değiştirin

# Admin site customization
admin.site.site_header = "Courtmax Padel Mate Admin"
admin.site.site_title = "Admin Paneli"
admin.site.index_title = "Hoş Geldiniz"


@admin.register(Player)  # Model adını buraya yazın
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone', 'created_at']  # Listelemek istediğiniz alanlar
    list_filter = ['created_at']  # Filtreleme için
    search_fields = ['name', 'email', 'phone']  # Arama yapılabilecek alanlar
    readonly_fields = ['created_at', 'id']  # Sadece okunabilir alanlar
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Tarihler', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # Daraltılabilir section
        }),
    )