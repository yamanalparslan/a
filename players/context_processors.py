from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        # Okunmamış bildirim var mı kontrol et
        unread_exists = Notification.objects.filter(recipient=request.user, is_read=False).exists()
        return {'unread_notifications': unread_exists}
    return {'unread_notifications': False}