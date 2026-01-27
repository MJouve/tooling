#!/bin/bash
# Script d'installation des dépendances pour resize_images

echo "📦 Installation des dépendances pour resize_images..."
echo ""

# Vérifie que Python 3 est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: Python 3 n'est pas installé"
    echo "   Installez-le avec: sudo apt install python3 python3-venv"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Crée l'environnement virtuel s'il n'existe pas ou s'il est incomplet
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    # Supprime le venv incomplet s'il existe
    if [ -d "$VENV_DIR" ]; then
        echo "🧹 Nettoyage de l'environnement virtuel incomplet..."
        rm -rf "$VENV_DIR"
    fi
    
    echo "🔧 Création de l'environnement virtuel..."
    if ! python3 -m venv "$VENV_DIR"; then
        echo "❌ Erreur: Impossible de créer l'environnement virtuel"
        echo "   Vérifiez que python3-venv est installé:"
        echo "   sudo apt install python3-venv"
        exit 1
    fi
    
    # Vérifie que le fichier activate a bien été créé
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo "❌ Erreur: L'environnement virtuel n'a pas été créé correctement"
        echo "   Le fichier $VENV_DIR/bin/activate est manquant"
        exit 1
    fi
    
    echo "✅ Environnement virtuel créé"
    echo ""
fi

# Active l'environnement virtuel et installe les dépendances
echo "📥 Installation des dépendances dans l'environnement virtuel..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$SCRIPT_DIR/requirements.txt"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation terminée !"
    echo ""
    echo "💡 Utilisation:"
    echo "   ./resize_images.sh <dossier> [options]"
    echo "   python3 resize_images.py <dossier> [options]"
    echo ""
    echo "   L'environnement virtuel est géré automatiquement par le script."
else
    echo ""
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi
