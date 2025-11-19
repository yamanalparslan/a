# players/apps.py

from django.apps import AppConfig

class PlayersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "players"

    # YENİ EKLEDİĞİMİZ METOD:
    # Bu uygulama (players) hazır olduğunda,
    # 'signals.py' dosyamızı import etmesini söylüyoruz.
    def ready(self):
        import players.signals
