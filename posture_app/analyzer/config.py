# posture_app/analyzer/config.py

class PostureConfig:
    """Configuration pour l'analyse de posture"""
    
    # Seuils d'angles (en degrés)
    NECK_ANGLE_MIN = 150  # Angle tête-cou minimum acceptable
    BACK_ANGLE_MIN = 160  # Angle dos minimum acceptable
    SHOULDER_DIFF_MAX = 15  # Différence max entre épaules
    
    # Temps avant alerte (en secondes)
    BAD_POSTURE_ALERT_TIME = 10  # Alerte après 10 secondes de mauvaise posture
    
    # Paramètres de l'alerte sonore
    ALERT_FREQUENCY = 1000  # Hz
    ALERT_DURATION = 500    # ms
    
    # Couleurs du thème (RGB)
    COLOR_PRIMARY = (45, 185, 255)      # Orange moderne
    COLOR_SUCCESS = (50, 205, 50)       # Vert
    COLOR_WARNING = (0, 165, 255)       # Orange
    COLOR_DANGER = (50, 50, 255)        # Rouge
    COLOR_BG_DARK = (20, 20, 20)        # Noir foncé
    COLOR_BG_LIGHT = (40, 40, 40)       # Gris foncé
    COLOR_TEXT = (255, 255, 255)        # Blanc
    
    # Paramètres vidéo
    VIDEO_FPS = 30
    VIDEO_RESOLUTION = (640, 480)
    
    # Paramètres MediaPipe
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE = 0.5
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE = 0.5
