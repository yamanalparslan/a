# padel_community/urls.py

from django.contrib import admin
from django.urls import path, include
from players import views as player_views 

urlpatterns = [
    # DİKKAT: Tırnakların içinde "/" işaretiyle BAŞLAMAYIN
    
    # Ana Sayfa (Boş tırnak doğrudur)
    path("", player_views.home, name="home"),
    
    # Admin Paneli ("admin/" doğru, "/admin/" YANLIŞ)
    path("admin/", admin.site.urls),
    
    # Hesap Yönetimi (Custom accounts uygulaması)
    path("accounts/", include("accounts.urls")),
    
    # Kayıt Ol
    path("signup/", player_views.signup, name="signup"),
    
    # Players uygulaması
    path("players/", include("players.urls")),
]