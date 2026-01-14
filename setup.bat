@echo off
echo ==================================
echo PostureMonitor Pro - Installation
echo ==================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.

REM Créer l'environnement virtuel
echo 📦 Création de l'environnement virtuel...
python -m venv venv

REM Activer l'environnement
echo 🔧 Activation de l'environnement...
call venv\Scripts\activate.bat

REM Installer les dépendances
echo 📥 Installation des dépendances...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Créer les migrations
echo 🗄️  Configuration de la base de données...
python manage.py makemigrations
python manage.py migrate

REM Créer les dossiers media
if not exist media\profile_pics mkdir media\profile_pics

echo.
echo ==================================
echo ✅ Installation terminée !
echo ==================================
echo.
echo Prochaines étapes :
echo 1. Activer l'environnement : venv\Scripts\activate
echo 2. Créer un superuser : python manage.py createsuperuser
echo 3. Lancer le serveur : python manage.py runserver
echo.
echo Ensuite, ouvrez http://127.0.0.1:8000 dans votre navigateur
echo.
pause
