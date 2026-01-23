# padel_community/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings            # Medya ayarları için
from django.conf.urls.static import static  # Medya ayarları için
from players import views as player_views 

urlpatterns = [
    # Ana Sayfa
    path("", player_views.home, name="home"),
    
    # Admin Paneli
    path("admin/", admin.site.urls),
    
    # --- DÜZELTİLEN KISIM ---
    # 'accounts.urls' YERİNE Django'nun kendi auth sistemini kullanıyoruz.
    # Bu sayede login, logout, password_reset gibi sayfalar otomatik çalışır.
    path("accounts/", include("django.contrib.auth.urls")),
    
    # Kayıt Ol (Bizim özel view'imiz)
    path("signup/", player_views.signup, name="signup"),
    
    # Players uygulaması
    path("players/", include("players.urls")),
]

# --- PROFİL FOTOĞRAFLARI İÇİN GEREKLİ AYAR ---
# Geliştirme modundayken (DEBUG=True) yüklenen resimleri sunmak için:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    admin.site.site_header = "🎾 Courtmax Padel Mate Admin"
admin.site.site_title = "Courtmax Admin"
admin.site.index_title = "Padel Yönetim Paneli"