# posture_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    """Profil utilisateur étendu"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='default.jpg'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"

class PostureSession(models.Model):
    """Session d'analyse de posture"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Statistiques de la session
    total_bad_posture_time = models.DurationField(default=timezone.timedelta)
    bad_posture_percentage = models.FloatField(default=0.0)
    alert_count = models.IntegerField(default=0)
    average_neck_angle = models.FloatField(null=True, blank=True)
    average_back_angle = models.FloatField(null=True, blank=True)
    average_shoulder_diff = models.FloatField(null=True, blank=True)
    
    # Score global
    posture_score = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"
    
    def calculate_score(self):
        """Calcule le score de la session (0-100)"""
        if self.duration and self.duration.total_seconds() > 0:
            good_posture_percentage = 100 - self.bad_posture_percentage
            return round(good_posture_percentage, 2)
        return 0.0
    
    def save(self, *args, **kwargs):
        # Calculer la durée si end_time est défini
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        
        # Calculer le score
        if self.duration:
            self.posture_score = self.calculate_score()
        
        super().save(*args, **kwargs)

class PostureAlert(models.Model):
    """Alerte de mauvaise posture"""
    session = models.ForeignKey(PostureSession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    
    ALERT_TYPES = [
        ('neck', 'Cou penché'),
        ('back', 'Dos courbé'),
        ('shoulders', 'Épaules déséquilibrées'),
        ('multiple', 'Problèmes multiples'),
    ]
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    
    # Angles au moment de l'alerte
    neck_angle = models.FloatField()
    back_angle = models.FloatField()
    shoulder_diff = models.FloatField()
    
    duration = models.DurationField()  # Durée de la mauvaise posture
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Alerte {self.alert_type} - {self.timestamp.strftime('%H:%M:%S')}"

class DailyStats(models.Model):
    """Statistiques quotidiennes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    
    total_time = models.DurationField(default=timezone.timedelta)
    bad_posture_time = models.DurationField(default=timezone.timedelta)
    session_count = models.IntegerField(default=0)
    alert_count = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"Stats {self.user.username} - {self.date.strftime('%d/%m/%Y')}"
