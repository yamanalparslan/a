# players/urls.py

from django.urls import path, include
from django.contrib.auth import views as auth_views # Logout işlemi için gerekli
from rest_framework.routers import DefaultRouter
from . import views

# API Router Ayarları
router = DefaultRouter()
router.register(r'players', views.PlayerViewSet, basename='api-player')
router.register(r'matches', views.MatchViewSet, basename='api-match')

urlpatterns = [
    # --- API URL'leri ---
    path('api/v1/', include(router.urls)),

    # --- KİMLİK DOĞRULAMA (AUTH) ---
    # Standart login yerine senin yazdığın Base64 çözen 'custom_login'e gidiyor:
    path('login/', views.custom_login, name='login'),
    
    path('signup/', views.signup, name='signup'),
    
    # Çıkış işlemi için Django'nun hazır view'ini kullanabiliriz (veya logout sonrası login'e yönlendirir)
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Şifre Sıfırlama (Opsiyonel - Eğer şablonları varsa çalışır)
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # --- SAYFALAR ---
    # Ana sayfa olarak views.home'u ayarladım (Daha mantıklı bir karşılama ekranı)
    path('', views.home, name='home'),
    
    # Oyuncu Listesi (Eskiden ana sayfaydı, şimdi /players/ altına aldım)
    path('players/', views.player_list, name='player-list'),
    
    path('player/<int:pk>/', views.player_detail, name='player-detail'), # 'player/' ön eki eklendi
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    
    # --- MAÇ İŞLEMLERİ ---
    path('matches/', views.match_list, name='match-list'),
    path('matches/<int:pk>/', views.match_detail, name='match-detail'),
    path('add-match/', views.create_match, name='create-match'),
    path('match/<int:pk>/edit/', views.edit_match, name='edit-match'), 
    path('match/<int:pk>/delete/', views.delete_match, name='delete-match'),
    
    # --- DİĞER ---
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    # --- BİLDİRİMLER ---
    path('notifications/', views.notifications, name='notifications'),
    path('accept-match/<int:notification_id>/', views.accept_match, name='accept-match'),
    path('notification/<int:pk>/reject/', views.reject_match, name='reject-match'),
]