# accounts/urls.py

from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import path

urlpatterns = [
    # Giriş/Çıkış
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Şifre Değiştir (aktif oturumdayken)
    path('password_change/', PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/password_change_done/'
    ), name='password_change'),
    
    path('password_change_done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    
    # Şifre Sıfırla (unutulunca)
    path('password_reset/', PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        success_url='/accounts/password_reset_done/'
    ), name='password_reset'),
    
    path('password_reset_done/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password_reset_complete/'
    ), name='password_reset_confirm'),
    
    path('password_reset_complete/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]