# posture_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analysis/', views.analysis_view, name='analysis'),
    path('profile/', views.profile_view, name='profile'),
    path('statistics/', views.statistics_view, name='statistics'),
    
    # Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Détails de session
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),

    # Guide de posture
    path('guide/', views.posture_guide, name='posture_guide'),

    # API Endpoints pour l'analyse en temps réel
    path('api/session/start/', views.start_session_api, name='start_session_api'),
    path('api/session/<int:session_id>/end/', views.end_session_api, name='end_session_api'),
    path('api/alert/save/', views.save_alert_api, name='save_alert_api'),
    path('api/frame/process/', views.process_frame_api, name='process_frame_api'),
]
