# players/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- OYUNCULAR ---
    path('', views.player_list, name='player-list'),
    path('<int:pk>/', views.player_detail, name='player-detail'),
    
    # --- MAÇLAR ---
    path('matches/', views.match_list, name='match-list'),
    path('matches/<int:pk>/', views.match_detail, name='match-detail'),
    
    # Maç Ekleme (Artık Davet Gönderme Olarak Çalışıyor)
    path('add-match/', views.create_match, name='create-match'),

    # --- LEADERBOARD ---
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # --- YENİ: BİLDİRİMLER VE ONAYLAMA ---
    # Bildirimleri listeleme sayfası
    path('notifications/', views.notifications, name='notifications'),
    
    # Maç onaylama linki (Hangi bildirimin onaylandığını ID ile anlar)
    path('accept-match/<int:notification_id>/', views.accept_match, name='accept-match'),

    path('profile/edit/', views.edit_profile, name='edit-profile'),
]