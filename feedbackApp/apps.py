import threading
from django.apps import AppConfig


class FeedbackappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feedbackApp'

    def ready(self):
        #  Zamanlanmış görevleri arka planda başlat
        from feedbackApp.scheduler import schedule_runner
        t = threading.Thread(target=schedule_runner, daemon=True)
        t.start()
