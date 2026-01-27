#!/bin/bash
# Script pour installer resize_images de manière globale (accessible depuis partout)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Vérifie si ~/.local/bin existe, sinon le crée
LOCAL_BIN="$HOME/.local/bin"
if [ ! -d "$LOCAL_BIN" ]; then
    echo "📁 Création du dossier $LOCAL_BIN..."
    mkdir -p "$LOCAL_BIN"
fi

# Crée un lien symbolique
LINK_PATH="$LOCAL_BIN/resize_images"
if [ -L "$LINK_PATH" ] || [ -f "$LINK_PATH" ]; then
    echo "⚠️  Le lien $LINK_PATH existe déjà"
    read -p "   Voulez-vous le remplacer ? (o/N): " response
    if [[ "$response" =~ ^[oO]$ ]]; then
        rm -f "$LINK_PATH"
    else
        echo "❌ Installation annulée"
        exit 1
    fi
fi

echo "🔗 Création du lien symbolique..."
ln -s "$SCRIPT_DIR/resize_images.sh" "$LINK_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Lien symbolique créé: $LINK_PATH"
    echo ""
    
    # Vérifie si ~/.local/bin est dans le PATH
    if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
        echo "⚠️  Attention: $LOCAL_BIN n'est pas dans votre PATH"
        echo ""
        echo "Ajoutez cette ligne à votre ~/.bashrc ou ~/.zshrc :"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "Puis rechargez votre shell avec:"
        echo "  source ~/.bashrc  # ou source ~/.zshrc"
        echo ""
    else
        echo "✅ $LOCAL_BIN est déjà dans votre PATH"
        echo ""
    fi
    
    echo "💡 Vous pouvez maintenant utiliser 'resize_images' depuis n'importe où !"
    echo "   Exemple: resize_images"
    echo "   Exemple: resize_images ./photos/ --width 800"
else
    echo "❌ Erreur lors de la création du lien symbolique"
    exit 1
fi
