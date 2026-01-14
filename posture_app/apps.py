# posture_app/apps.py

from django.apps import AppConfig


class PostureAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posture_app'
    verbose_name = 'Analyse de Posture'
    
    def ready(self):
        # Import signal handlers if needed
        pass
