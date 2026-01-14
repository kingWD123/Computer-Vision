# posture_app/admin.py

from django.contrib import admin
from .models import UserProfile, PostureSession, PostureAlert, DailyStats

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'occupation', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(PostureSession)
class PostureSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'start_time', 'duration', 'posture_score', 'alert_count']
    list_filter = ['start_time', 'user']
    search_fields = ['user__username']
    readonly_fields = ['posture_score']
    
    fieldsets = (
        ('Informations de session', {
            'fields': ('user', 'start_time', 'end_time', 'duration')
        }),
        ('Statistiques', {
            'fields': ('total_bad_posture_time', 'bad_posture_percentage', 'alert_count', 
                      'average_neck_angle', 'average_back_angle', 'average_shoulder_diff')
        }),
        ('Score', {
            'fields': ('posture_score',)
        }),
    )

@admin.register(PostureAlert)
class PostureAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'alert_type', 'timestamp', 'duration']
    list_filter = ['alert_type', 'timestamp']
    search_fields = ['session__user__username']

@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'session_count', 'average_score', 'alert_count']
    list_filter = ['date', 'user']
    search_fields = ['user__username']
    date_hierarchy = 'date'
