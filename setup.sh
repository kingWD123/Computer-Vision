#!/bin/bash

echo "=================================="
echo "PostureMonitor Pro - Installation"
echo "=================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Python détecté"

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement
echo "🔧 Activation de l'environnement..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer les migrations
echo "🗄️  Configuration de la base de données..."
python manage.py makemigrations
python manage.py migrate

# Créer les dossiers media si nécessaire
mkdir -p media/profile_pics

echo ""
echo "=================================="
echo "✅ Installation terminée !"
echo "=================================="
echo ""
echo "Prochaines étapes :"
echo "1. Activer l'environnement : source venv/bin/activate"
echo "2. Créer un superuser : python manage.py createsuperuser"
echo "3. Lancer le serveur : python manage.py runserver"
echo ""
echo "Ensuite, ouvrez http://127.0.0.1:8000 dans votre navigateur"
echo ""
