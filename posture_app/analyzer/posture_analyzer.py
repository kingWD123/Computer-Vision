# posture_app/analyzer/posture_analyzer.py

import cv2
import mediapipe as mp
import numpy as np
import math
import base64
from collections import deque

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Initialiser MediaPipe Pose (singleton)
_pose_detector = None


def get_pose_detector():
    """Obtenir l'instance du détecteur de pose (singleton)"""
    global _pose_detector
    if _pose_detector is None:
        _pose_detector = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1  # Ajouté pour de meilleures performances
        )
    return _pose_detector


def calculate_angle(a, b, c):
    """Calcule l'angle entre 3 points"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - \
              math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(math.degrees(radians))

    if angle > 180:
        angle = 360 - angle

    return angle


def calculate_vertical_angle(a, b):
    """Calcule l'angle par rapport à la verticale"""
    angle = math.degrees(math.atan2(b[0] - a[0], a[1] - b[1]))
    return abs(angle)


def analyze_neck_posture(landmarks):
    """Analyse la posture du cou"""
    try:
        nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                landmarks[mp_pose.PoseLandmark.NOSE.value].y]
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        mid_shoulder = [(left_shoulder[0] + right_shoulder[0]) / 2,
                        (left_shoulder[1] + right_shoulder[1]) / 2]

        neck_angle = calculate_vertical_angle(nose, mid_shoulder)

        return neck_angle, neck_angle < 15
    except Exception as e:
        print(f"Erreur analyse cou: {e}")
        return 0, True


def analyze_back_posture(landmarks):
    """Analyse la posture du dos"""
    try:
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

        back_angle = calculate_angle(left_shoulder, left_hip, left_knee)

        return back_angle, back_angle >= 160
    except Exception as e:
        print(f"Erreur analyse dos: {e}")
        return 180, True


def analyze_shoulder_alignment(landmarks):
    """Analyse l'alignement des épaules"""
    try:
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        shoulder_diff = abs(left_shoulder.y - right_shoulder.y) * 100

        return shoulder_diff, shoulder_diff <= 15
    except Exception as e:
        print(f"Erreur analyse épaules: {e}")
        return 0, True


def get_posture_problems(neck_ok, back_ok, shoulders_ok):
    """Identifie les problèmes de posture spécifiques"""
    problems = []

    if not neck_ok:
        problems.append("Tête trop penchée")
    if not back_ok:
        problems.append("Dos courbé")
    if not shoulders_ok:
        problems.append("Épaules déséquilibrées")

    return problems


def analyze_frame(frame):
    """
    Analyse une frame vidéo et retourne les résultats

    Args:
        frame: Image numpy array (BGR)

    Returns:
        dict avec les résultats de l'analyse
    """
    try:
        pose = get_pose_detector()

        # Vérifier que frame est valide
        if frame is None or frame.size == 0:
            return {
                'success': False,
                'error': 'Frame invalide'
            }

        # Convertir BGR → RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Détection de la posture
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Analyser chaque composant
            neck_angle, neck_ok = analyze_neck_posture(landmarks)
            back_angle, back_ok = analyze_back_posture(landmarks)
            shoulder_diff, shoulders_ok = analyze_shoulder_alignment(landmarks)

            # Déterminer si la posture est globalement correcte
            is_good_posture = neck_ok and back_ok and shoulders_ok

            # Identifier les problèmes
            problems = get_posture_problems(neck_ok, back_ok, shoulders_ok)

            # Dessiner le squelette sur l'image
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(0, 165, 255), thickness=2, circle_radius=2)
            )

            # Encoder l'image en base64 pour l'envoyer au frontend
            _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            return {
                'success': True,
                'detected': True,
                'is_good_posture': is_good_posture,
                'neck_angle': float(neck_angle),
                'back_angle': float(back_angle),
                'shoulder_diff': float(shoulder_diff),
                'neck_ok': neck_ok,
                'back_ok': back_ok,
                'shoulders_ok': shoulders_ok,
                'problems': problems,
                'image': f'data:image/jpeg;base64,{image_base64}',
            }
        else:
            return {
                'success': True,
                'detected': False,
                'message': 'Personne non détectée'
            }

    except Exception as e:
        print(f"Erreur dans analyze_frame: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


class PostureAnalyzerSession:
    """
    Classe pour gérer une session d'analyse complète
    """

    def __init__(self):
        self.bad_posture_start_time = None
        self.total_bad_posture_time = 0
        self.alert_count = 0
        self.posture_history = deque(maxlen=100)
        self.neck_angles = []
        self.back_angles = []
        self.shoulder_diffs = []

    def update(self, is_good_posture, neck_angle, back_angle, shoulder_diff):
        """Met à jour l'état de la session"""
        import time

        # Ajouter à l'historique
        self.posture_history.append(1 if is_good_posture else 0)
        self.neck_angles.append(neck_angle)
        self.back_angles.append(back_angle)
        self.shoulder_diffs.append(shoulder_diff)

        current_time = time.time()

        if not is_good_posture:
            if self.bad_posture_start_time is None:
                self.bad_posture_start_time = current_time

            bad_posture_duration = current_time - self.bad_posture_start_time

            # Déclencher alerte après 10 secondes
            if bad_posture_duration >= 10:
                self.alert_count += 1
                return True, bad_posture_duration
        else:
            if self.bad_posture_start_time is not None:
                self.total_bad_posture_time += current_time - self.bad_posture_start_time
                self.bad_posture_start_time = None

        return False, 0

    def get_statistics(self, total_time):
        """Calcule les statistiques de la session"""
        bad_posture_percentage = (self.total_bad_posture_time / total_time * 100) if total_time > 0 else 0

        avg_neck = sum(self.neck_angles) / len(self.neck_angles) if self.neck_angles else 0
        avg_back = sum(self.back_angles) / len(self.back_angles) if self.back_angles else 0
        avg_shoulder = sum(self.shoulder_diffs) / len(self.shoulder_diffs) if self.shoulder_diffs else 0

        return {
            'bad_posture_time': self.total_bad_posture_time,
            'bad_posture_percentage': bad_posture_percentage,
            'alert_count': self.alert_count,
            'avg_neck_angle': avg_neck,
            'avg_back_angle': avg_back,
            'avg_shoulder_diff': avg_shoulder,
        }