#!/bin/bash
# Script wrapper pour resize_images.py

# Trouve le vrai dossier du script, même s'il est appelé via un lien symbolique
if [ -L "${BASH_SOURCE[0]}" ]; then
    # Si c'est un lien symbolique, on suit le lien
    SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
else
    # Sinon, on utilise le chemin normal
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

VENV_DIR="$SCRIPT_DIR/venv"

# Vérifie si l'environnement virtuel existe
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
    # Active l'environnement virtuel et exécute le script
    source "$VENV_DIR/bin/activate"
    python "$SCRIPT_DIR/resize_images.py" "$@"
    deactivate
else
    # Si pas d'environnement virtuel, utilise python3 système
    # (mais il faudra installer les dépendances manuellement)
    echo "⚠️  Environnement virtuel non trouvé."
    echo "   Exécutez: cd $SCRIPT_DIR && ./install.sh"
    echo ""
    python3 "$SCRIPT_DIR/resize_images.py" "$@"
fi
