# 🧠 PostureMonitor Pro - Analyse de Posture en Temps Réel

Application web Django utilisant l'IA pour analyser et améliorer votre posture au travail.

![Django](https://img.shields.io/badge/Django-4.2.7-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange)

## 📋 Fonctionnalités

✅ **Analyse en temps réel** - Détection de posture via webcam avec MediaPipe AI  
✅ **Dashboard interactif** - Statistiques et graphiques personnalisés  
✅ **Alertes intelligentes** - Notifications visuelles et sonores  
✅ **Historique complet** - Sauvegarde de toutes vos sessions  
✅ **Multi-utilisateurs** - Gestion de comptes individuels  
✅ **API REST** - Endpoints pour extensions futures  

## 🚀 Installation Rapide

### Prérequis

- Python 3.8+
- pip
- Webcam

### Étape 1 : Cloner le projet

```bash
git clone <url-du-repo>
cd posture_monitor_django
```

### Étape 2 : Créer l'environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Étape 3 : Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 4 : Configurer la base de données

```bash
python manage.py makemigrations
python manage.py migrate
```

### Étape 5 : Créer un superuser (admin)

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte admin.

### Étape 6 : Lancer le serveur

```bash
python manage.py runserver
```

### 🎉 C'est prêt !

Ouvrez votre navigateur : **http://127.0.0.1:8000**

## 📁 Structure du Projet

```
posture_monitor_django/
├── config/                     # Configuration Django
│   ├── settings.py            # Paramètres du projet
│   ├── urls.py                # URLs principales
│   ├── wsgi.py                # Configuration WSGI
│   └── asgi.py                # Configuration ASGI
│
├── posture_app/                # Application principale
│   ├── models.py              # Modèles de données
│   ├── views.py               # Vues Django
│   ├── urls.py                # URLs de l'app
│   ├── api_urls.py            # URLs API
│   ├── admin.py               # Interface admin
│   │
│   ├── analyzer/              # Module d'analyse
│   │   ├── posture_analyzer.py   # Logique d'analyse
│   │   └── config.py             # Configuration
│   │
│   ├── templates/             # Templates HTML
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── analysis.html
│   │   └── registration/
│   │       ├── login.html
│   │       └── register.html
│   │
│   └── static/                # Fichiers statiques
│       ├── css/
│       ├── js/
│       └── images/
│
├── media/                      # Fichiers uploadés
├── manage.py                   # Script de gestion Django
├── requirements.txt            # Dépendances Python
└── README.md                   # Ce fichier
```

## 🎯 Utilisation

### 1. Créer un compte

- Accédez à http://127.0.0.1:8000
- Cliquez sur "S'inscrire"
- Remplissez le formulaire

### 2. Lancer une analyse

- Connectez-vous
- Allez dans "Analyse"
- Cliquez sur "Démarrer"
- Autorisez l'accès à la webcam

### 3. Consulter vos statistiques

- Dashboard : Vue d'ensemble
- Statistiques : Analyses détaillées
- Profil : Gérer votre compte

## 🔧 Configuration

### Modifier les seuils de détection

Éditez `posture_app/analyzer/config.py` :

```python
class PostureConfig:
    NECK_ANGLE_MIN = 150      # Angle cou
    BACK_ANGLE_MIN = 160      # Angle dos
    SHOULDER_DIFF_MAX = 15    # Épaules
    BAD_POSTURE_ALERT_TIME = 10  # Temps avant alerte (s)
```

### Changer la langue

Dans `config/settings.py` :

```python
LANGUAGE_CODE = 'fr-fr'  # Français
TIME_ZONE = 'Africa/Dakar'
```

## 🛠️ Commandes Utiles

```bash
# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Lancer les tests
python manage.py test

# Accéder au shell Django
python manage.py shell
```

## 🌐 Accès Admin

URL : http://127.0.0.1:8000/admin/

Connectez-vous avec votre compte superuser pour :
- Gérer les utilisateurs
- Voir toutes les sessions
- Consulter les alertes
- Modifier les données

## 📊 Modèles de Données

### UserProfile
- Extension du modèle User
- Photo de profil
- Occupation
- Date de naissance

### PostureSession
- Utilisateur
- Date/heure
- Durée
- Score
- Statistiques

### PostureAlert
- Session associée
- Type d'alerte
- Angles
- Durée

### DailyStats
- Statistiques quotidiennes
- Temps total
- Score moyen

## 🔌 API REST

### Endpoints disponibles

```
POST /api/session/start/           # Démarrer une session
POST /api/session/<id>/end/        # Terminer une session
POST /api/alert/save/              # Sauvegarder une alerte
POST /api/frame/process/           # Traiter une frame vidéo
```

### Exemple d'utilisation

```python
import requests

# Démarrer une session
response = requests.post('http://127.0.0.1:8000/api/session/start/')
session_id = response.json()['session_id']
```

## 🚀 Déploiement

### Option 1 : Heroku

```bash
# Installer Heroku CLI
heroku login
heroku create votre-app

# Configurer la base de données
heroku addons:create heroku-postgresql

# Déployer
git push heroku main
heroku run python manage.py migrate
```

### Option 2 : DigitalOcean / AWS

Voir la documentation officielle Django pour le déploiement en production.

### ⚠️ Production Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY dans variable d'environnement
- [ ] Configurer ALLOWED_HOSTS
- [ ] Utiliser PostgreSQL au lieu de SQLite
- [ ] Configurer HTTPS
- [ ] Activer WhiteNoise pour les fichiers statiques

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT.

## 🆘 Support

En cas de problème :

1. Consultez la [Documentation Django](https://docs.djangoproject.com/)
2. Ouvrez une issue sur GitHub
3. Contactez-nous

## 🎓 Crédits

- **MediaPipe** - Google Research
- **Django** - Django Software Foundation
- **Bootstrap** - Twitter
- **Chart.js** - Chart.js Team

## 📧 Contact

Pour toute question : votre-email@example.com

---

**Développé avec ❤️ pour améliorer votre santé au travail**
