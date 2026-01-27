#!/bin/bash
# Script d'installation pour rendre sprite_cutter accessible depuis n'importe où

set -e

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎨 Installation de Sprite Cutter${NC}"
echo ""

# Obtenir le répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_PATH="${SCRIPT_DIR}/sprite_cutter.py"
WRAPPER_PATH="${SCRIPT_DIR}/cut_sprites.sh"

# Vérifier que les fichiers existent
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ Erreur: sprite_cutter.py introuvable dans $SCRIPT_DIR${NC}"
    exit 1
fi

# Déterminer où installer le lien symbolique
# Préférer ~/.local/bin (pas besoin de sudo)
LOCAL_BIN="$HOME/.local/bin"
SYSTEM_BIN="/usr/local/bin"

# Créer ~/.local/bin s'il n'existe pas
if [ ! -d "$LOCAL_BIN" ]; then
    mkdir -p "$LOCAL_BIN"
    echo -e "${YELLOW}📁 Création du dossier $LOCAL_BIN${NC}"
fi

# Vérifier si ~/.local/bin est dans le PATH
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo -e "${YELLOW}⚠️  $LOCAL_BIN n'est pas dans votre PATH${NC}"
    echo ""
    echo "Ajoutez cette ligne à votre ~/.bashrc ou ~/.zshrc :"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
    read -p "Voulez-vous que je l'ajoute automatiquement ? (o/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[OoYy]$ ]]; then
        SHELL_RC="$HOME/.bashrc"
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_RC="$HOME/.zshrc"
        fi
        
        if ! grep -q "$LOCAL_BIN" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# Ajout de ~/.local/bin au PATH pour sprite_cutter" >> "$SHELL_RC"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
            echo -e "${GREEN}✅ Ajouté à $SHELL_RC${NC}"
            echo -e "${YELLOW}💡 Exécutez 'source $SHELL_RC' ou redémarrez votre terminal${NC}"
        else
            echo -e "${GREEN}✅ Déjà présent dans $SHELL_RC${NC}"
        fi
    fi
fi

# Créer le script wrapper dans ~/.local/bin
WRAPPER_NAME="sprite-cutter"
TARGET_WRAPPER="$LOCAL_BIN/$WRAPPER_NAME"

echo -e "${GREEN}📝 Création du wrapper dans $TARGET_WRAPPER${NC}"

# Créer un wrapper simple qui utilise le chemin absolu du script
cat > "$TARGET_WRAPPER" << EOF
#!/bin/bash
# Wrapper pour sprite_cutter.py - accessible depuis n'importe où
exec python3 "$SCRIPT_PATH" "\$@"
EOF

chmod +x "$TARGET_WRAPPER"
echo -e "${GREEN}✅ Wrapper créé et rendu exécutable${NC}"

echo ""
echo -e "${GREEN}🎉 Installation terminée !${NC}"
echo ""
echo "Vous pouvez maintenant utiliser sprite-cutter depuis n'importe quel dossier :"
echo ""
echo -e "  ${YELLOW}sprite-cutter mon_image.png${NC}"
echo -e "  ${YELLOW}sprite-cutter mon_image.png -o output/ -t 230${NC}"
echo ""
echo "Si vous avez ajouté ~/.local/bin au PATH, vous devrez peut-être :"
echo -e "  ${YELLOW}source ~/.bashrc${NC}  (ou redémarrer votre terminal)"
echo ""
echo "Pour désinstaller, supprimez simplement :"
echo -e "  ${YELLOW}rm $TARGET_WRAPPER${NC}"
