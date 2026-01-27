#!/bin/bash
# Script d'installation de MP4toSprite

echo "🚀 Installation de MP4toSprite..."
echo ""

# Vérifie si on est sur Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Ce script est conçu pour Linux"
    echo "   Mais peut fonctionner sur macOS/WSL"
    echo ""
fi

# Vérifie et installe ffmpeg
echo "📦 Vérification de ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "   ffmpeg n'est pas installé"
    echo "   Installation de ffmpeg..."
    
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y ffmpeg ffprobe
    elif command -v yum &> /dev/null; then
        sudo yum install -y ffmpeg
    elif command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Impossible d'installer ffmpeg automatiquement"
        echo "   Veuillez l'installer manuellement:"
        echo "   - Ubuntu/Debian: sudo apt install ffmpeg"
        echo "   - CentOS/RHEL: sudo yum install ffmpeg"
        echo "   - macOS: brew install ffmpeg"
        exit 1
    fi
else
    echo "   ✅ ffmpeg est déjà installé"
fi

# Vérifie Python
echo ""
echo "🐍 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "   Installez-le avec: sudo apt install python3 python3-pip"
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION trouvé"
fi

# Installe les dépendances Python
echo ""
echo "📚 Installation des dépendances Python..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt
    echo "   ✅ Pillow installé"
else
    echo "❌ pip3 n'est pas installé"
    echo "   Installez-le avec: sudo apt install python3-pip"
    exit 1
fi

# Rend le script exécutable
echo ""
echo "🔧 Configuration du script..."
chmod +x mp4-to-sprite.py

# Crée un lien symbolique dans /usr/local/bin (optionnel)
echo ""
read -p "❓ Voulez-vous installer mp4-to-sprite globalement (accessible partout) ? (o/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]]; then
    SCRIPT_PATH=$(pwd)/mp4-to-sprite.py
    sudo ln -sf "$SCRIPT_PATH" /usr/local/bin/mp4-to-sprite
    echo "   ✅ Commande 'mp4-to-sprite' disponible globalement"
else
    echo "   ℹ️  Utilisez ./mp4-to-sprite.py pour exécuter"
fi

echo ""
echo "=" * 60
echo "✅ Installation terminée !"
echo "=" * 60
echo ""
echo "📖 Utilisation:"
echo "   ./mp4-to-sprite.py video.mp4 --size=300 --transparent"
echo ""
echo "   ou (si installé globalement):"
echo "   mp4-to-sprite video.mp4 --size=300 --transparent"
echo ""
echo "💡 Aide complète:"
echo "   ./mp4-to-sprite.py --help"
echo ""
