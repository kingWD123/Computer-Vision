# posture_app/api_urls.py

from django.urls import path
from . import views

urlpatterns = [
    # API pour les sessions
    path('session/start/', views.start_session_api, name='api_start_session'),
    path('session/<int:session_id>/end/', views.end_session_api, name='api_end_session'),
    
    # API pour les alertes
    path('alert/save/', views.save_alert_api, name='api_save_alert'),
    
    # API pour le traitement vidéo
    path('frame/process/', views.process_frame_api, name='api_process_frame'),
]
