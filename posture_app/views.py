# posture_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Max, Min
from datetime import timedelta, datetime
import json
import cv2
import base64
import numpy as np

from .models import UserProfile, PostureSession, PostureAlert, DailyStats
from .analyzer.config import PostureConfig


# ==================== VUES D'AUTHENTIFICATION ====================

def home(request):
    """Page d'accueil"""
    return render(request, 'home.html')


def register_view(request):
    """Inscription d'un nouvel utilisateur"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Créer le profil utilisateur
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username}!')
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Connexion utilisateur"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """Déconnexion utilisateur"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')


# ==================== VUES PRINCIPALES ====================

@login_required
def dashboard(request):
    """Dashboard principal de l'utilisateur"""
    user = request.user

    # Récupérer les sessions récentes
    recent_sessions = PostureSession.objects.filter(user=user)[:10]

    # Statistiques globales
    total_sessions = PostureSession.objects.filter(user=user).count()

    # Temps total
    total_time = PostureSession.objects.filter(user=user).aggregate(
        total=Sum('duration')
    )['total'] or timedelta()

    # Score moyen
    avg_score = PostureSession.objects.filter(user=user).aggregate(
        avg=Avg('posture_score')
    )['avg'] or 0

    # Alertes totales
    total_alerts = PostureAlert.objects.filter(
        session__user=user
    ).count()

    # Statistiques des 7 derniers jours
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_stats = DailyStats.objects.filter(
        user=user,
        date__gte=seven_days_ago.date()
    ).order_by('date')

    # Préparer les données pour les graphiques
    dates = [stat.date.strftime('%d/%m') for stat in recent_stats]
    scores = [stat.average_score for stat in recent_stats]
    times = [stat.total_time.total_seconds() / 60 for stat in recent_stats]  # En minutes

    context = {
        'recent_sessions': recent_sessions,
        'total_sessions': total_sessions,
        'total_time': total_time,
        'avg_score': round(avg_score, 1),
        'total_alerts': total_alerts,
        'chart_dates': json.dumps(dates),
        'chart_scores': json.dumps(scores),
        'chart_times': json.dumps(times),
    }

    return render(request, 'dashboard.html', context)

@login_required
def posture_guide(request):
    """Page du guide de posture détaillé"""
    return render(request, 'posture_guide.html')

@login_required
def analysis_view(request):
    """Page d'analyse en temps réel"""
    return render(request, 'analysis.html')


@login_required
def profile_view(request):
    """Page de profil utilisateur"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Mise à jour du profil
        profile.occupation = request.POST.get('occupation', '')

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('profile')

    context = {
        'profile': profile,
    }
    return render(request, 'profile.html', context)


@login_required
def statistics_view(request):
    """Page de statistiques détaillées"""
    user = request.user

    # Filtre par période
    period = request.GET.get('period', '30')  # 7, 30, 90 jours
    days_ago = timezone.now() - timedelta(days=int(period))

    # Toutes les sessions de la période
    sessions = PostureSession.objects.filter(
        user=user,
        start_time__gte=days_ago
    )

    # Statistiques détaillées
    stats = {
        'total_sessions': sessions.count(),
        'total_time': sessions.aggregate(Sum('duration'))['duration__sum'] or timedelta(),
        'avg_score': sessions.aggregate(Avg('posture_score'))['posture_score__avg'] or 0,
        'best_score': sessions.aggregate(max_score=Max('posture_score'))['max_score'] or 0,
        'worst_score': sessions.aggregate(min_score=Min('posture_score'))['min_score'] or 0,
        'total_alerts': PostureAlert.objects.filter(session__in=sessions).count(),
    }

    # Distribution des alertes par type
    alert_distribution = PostureAlert.objects.filter(
        session__in=sessions
    ).values('alert_type').annotate(count=Count('id'))

    context = {
        'stats': stats,
        'period': period,
        'alert_distribution': alert_distribution,
        'sessions': sessions[:20],  # 20 dernières sessions
    }

    return render(request, 'statistics.html', context)


@login_required
def session_detail(request, session_id):
    """Détails d'une session spécifique"""
    session = get_object_or_404(PostureSession, id=session_id, user=request.user)
    alerts = PostureAlert.objects.filter(session=session)

    context = {
        'session': session,
        'alerts': alerts,
    }
    return render(request, 'session_detail.html', context)


# ==================== API ENDPOINTS ====================

@login_required
@csrf_exempt
def start_session_api(request):
    """API pour démarrer une nouvelle session"""
    if request.method == 'POST':
        session = PostureSession.objects.create(user=request.user)
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'start_time': session.start_time.isoformat()
        })
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@login_required
@csrf_exempt
def end_session_api(request, session_id):
    """API pour terminer une session"""
    if request.method == 'POST':
        try:
            session = PostureSession.objects.get(id=session_id, user=request.user)
            session.end_time = timezone.now()

            # Récupérer les données de la session depuis POST
            data = json.loads(request.body)
            session.total_bad_posture_time = timedelta(seconds=data.get('bad_posture_time', 0))
            session.bad_posture_percentage = data.get('bad_posture_percentage', 0)
            session.alert_count = data.get('alert_count', 0)
            session.average_neck_angle = data.get('avg_neck_angle')
            session.average_back_angle = data.get('avg_back_angle')
            session.average_shoulder_diff = data.get('avg_shoulder_diff')

            session.save()

            # Mettre à jour les statistiques quotidiennes
            update_daily_stats(request.user, session)

            return JsonResponse({
                'success': True,
                'session_id': session.id,
                'duration': str(session.duration),
                'score': session.posture_score
            })
        except PostureSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@login_required
@csrf_exempt
def save_alert_api(request):
    """API pour sauvegarder une alerte"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session = PostureSession.objects.get(
                id=data.get('session_id'),
                user=request.user
            )

            alert = PostureAlert.objects.create(
                session=session,
                alert_type=data.get('alert_type', 'multiple'),
                neck_angle=data.get('neck_angle', 0),
                back_angle=data.get('back_angle', 0),
                shoulder_diff=data.get('shoulder_diff', 0),
                duration=timedelta(seconds=data.get('duration', 0))
            )

            return JsonResponse({
                'success': True,
                'alert_id': alert.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@login_required
@csrf_exempt
def process_frame_api(request):
    """API pour traiter une frame vidéo"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Décoder l'image base64
            image_data = data.get('frame', '')
            image_data = image_data.split(',')[1] if ',' in image_data else image_data
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Analyser la posture
            from .analyzer.posture_analyzer import analyze_frame

            result = analyze_frame(frame)

            return JsonResponse({
                'success': True,
                'result': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


# ==================== FONCTIONS UTILITAIRES ====================

def update_daily_stats(user, session):
    """Met à jour les statistiques quotidiennes"""
    today = timezone.now().date()

    daily_stat, created = DailyStats.objects.get_or_create(
        user=user,
        date=today
    )

    # Récupérer toutes les sessions du jour
    today_sessions = PostureSession.objects.filter(
        user=user,
        start_time__date=today
    )

    # Calculer les stats
    daily_stat.session_count = today_sessions.count()
    daily_stat.total_time = today_sessions.aggregate(
        total=Sum('duration')
    )['total'] or timedelta()
    daily_stat.bad_posture_time = today_sessions.aggregate(
        total=Sum('total_bad_posture_time')
    )['total'] or timedelta()
    daily_stat.alert_count = PostureAlert.objects.filter(
        session__in=today_sessions
    ).count()
    daily_stat.average_score = today_sessions.aggregate(
        avg=Avg('posture_score')
    )['avg'] or 0

    daily_stat.save()