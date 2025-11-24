# players/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# --- 1. DRF Router Tanımı (Doğru ve En Basit Hali) ---
# YALNIZCA kaynak adlarını ('players', 'matches') kullanıyoruz.
router = DefaultRouter()
router.register(r'players', views.PlayerViewSet, basename='api-player')
router.register(r'matches', views.MatchViewSet, basename='api-match')


urlpatterns = [
    # --- API YOLLARI ---
    # Router'ı direkt 'api/v1/' altına dahil ediyoruz.
    # Bu sayede URL'ler: /players/api/v1/players/ şeklinde olacak.
    path('api/v1/', include(router.urls)),
    
    # --- MEVCUT HTML YOLLARI ---
    path('', views.player_list, name='player-list'),
    path('<int:pk>/', views.player_detail, name='player-detail'),
    path('matches/', views.match_list, name='match-list'),
    path('matches/<int:pk>/', views.match_detail, name='match-detail'),
    path('add-match/', views.create_match, name='create-match'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('accept-match/<int:notification_id>/', views.accept_match, name='accept-match'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('match/<int:pk>/edit/', views.edit_match, name='edit-match'), 
    path('match/<int:pk>/delete/', views.delete_match, name='delete-match'),
    path('notification/<int:notification_id>/reject/', views.reject_match, name='reject-match'),
]