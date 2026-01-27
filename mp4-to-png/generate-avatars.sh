#!/bin/bash
# generate-avatars.sh
# Script pour générer tous les sprites d'avatar d'un coup

# Configuration
SOURCE_DIR="source"
OUTPUT_DIR="sprites"
SIZE=128
TOLERANCE=35

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 Générateur de sprites d'avatar${NC}"
echo "=================================="
echo ""

# Vérifie que le répertoire source existe
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${YELLOW}⚠️  Le répertoire '$SOURCE_DIR' n'existe pas${NC}"
    echo "   Créez-le et ajoutez vos vidéos MP4 :"
    echo "   mkdir $SOURCE_DIR"
    echo "   cp vos-videos/*.mp4 $SOURCE_DIR/"
    exit 1
fi

# Compte les vidéos
VIDEO_COUNT=$(ls -1 $SOURCE_DIR/*.mp4 2>/dev/null | wc -l)
if [ $VIDEO_COUNT -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Aucun fichier MP4 trouvé dans '$SOURCE_DIR'${NC}"
    exit 1
fi

echo "📁 Répertoire source: $SOURCE_DIR/"
echo "📁 Répertoire sortie: $OUTPUT_DIR/"
echo "📊 Vidéos trouvées: $VIDEO_COUNT"
echo "📏 Taille cible: ${SIZE}px"
echo "🎯 Tolérance: $TOLERANCE"
echo ""

# Crée le répertoire de sortie
mkdir -p $OUTPUT_DIR

# Configurations spécifiques par type d'animation
# Format: "nom_fichier:fps:start:end:loop"
declare -A CONFIGS=(
    ["idle"]="8:0:3:true"
    ["celebrate"]="12:0:1.5:false"
    ["point"]="10:0:1:false"
    ["thinking"]="6:0:2:true"
    ["congratulate"]="15:0:2:false"
    ["sad"]="8:0:2:true"
    ["surprise"]="12:0:1:false"
    ["nod"]="10:0:0.8:false"
    ["wave"]="10:0:1.5:false"
    ["dance"]="15:0:2:true"
)

# Fonction pour générer un sprite
generate_sprite() {
    local input_file=$1
    local base_name=$(basename "$input_file" .mp4)
    local output_file="$OUTPUT_DIR/avatar-${base_name}.png"
    
    # Récupère la config si elle existe
    local config="${CONFIGS[$base_name]}"
    local fps=10
    local start=0
    local end=""
    local loop="unknown"
    
    if [ -n "$config" ]; then
        IFS=':' read -r fps start end loop <<< "$config"
    fi
    
    echo -e "${BLUE}▶ $base_name${NC}"
    echo "  └─ FPS: $fps | Début: ${start}s | Fin: ${end}s | Boucle: $loop"
    
    # Construit la commande
    local cmd="./mp4-to-sprite.py \"$input_file\" \
        --size=$SIZE \
        --transparent \
        --tolerance=$TOLERANCE \
        --fps=$fps \
        --start=$start"
    
    if [ -n "$end" ]; then
        cmd="$cmd --end=$end"
    fi
    
    cmd="$cmd --output=\"$output_file\""
    
    # Exécute
    if eval $cmd > /dev/null 2>&1; then
        local file_size=$(ls -lh "$output_file" | awk '{print $5}')
        echo -e "  └─ ${GREEN}✓ Généré: $output_file ($file_size)${NC}"
        return 0
    else
        echo -e "  └─ ${YELLOW}✗ Erreur lors de la génération${NC}"
        return 1
    fi
}

# Génère tous les sprites
success_count=0
fail_count=0

for video in $SOURCE_DIR/*.mp4; do
    echo ""
    if generate_sprite "$video"; then
        ((success_count++))
    else
        ((fail_count++))
    fi
done

# Résumé
echo ""
echo "=================================="
echo -e "${GREEN}✅ Génération terminée${NC}"
echo "=================================="
echo "📊 Réussis: $success_count"
if [ $fail_count -gt 0 ]; then
    echo "⚠️  Échecs: $fail_count"
fi
echo ""

# Liste les fichiers générés avec leurs tailles
if [ $success_count -gt 0 ]; then
    echo "📁 Fichiers générés:"
    ls -lh $OUTPUT_DIR/avatar-*.png | awk '{printf "   • %s (%s)\n", $9, $5}'
    echo ""
    
    # Calcule la taille totale
    total_size=$(du -sh $OUTPUT_DIR | awk '{print $1}')
    echo "💾 Taille totale: $total_size"
    echo ""
fi

# Génère un fichier de configuration React
if [ $success_count -gt 0 ]; then
    echo "⚙️  Génération de la configuration React..."
    
    config_file="$OUTPUT_DIR/avatarAnimations.js"
    
    cat > "$config_file" << 'EOF'
// Généré automatiquement par generate-avatars.sh
// Configuration des animations d'avatar pour React

export const AVATAR_ANIMATIONS = {
EOF
    
    for video in $SOURCE_DIR/*.mp4; do
        base_name=$(basename "$video" .mp4)
        sprite_file="$OUTPUT_DIR/avatar-${base_name}.png"
        
        if [ -f "$sprite_file" ]; then
            # Récupère les dimensions du sprite
            dimensions=$(identify "$sprite_file" 2>/dev/null | awk '{print $3}')
            if [ -n "$dimensions" ]; then
                width=$(echo $dimensions | cut -d'x' -f1)
                height=$(echo $dimensions | cut -d'x' -f2)
                
                # Récupère la config
                config="${CONFIGS[$base_name]}"
                fps=10
                start=0
                end=""
                loop="true"
                
                if [ -n "$config" ]; then
                    IFS=':' read -r fps start end loop <<< "$config"
                fi
                
                # Calcule le nombre de frames
                frame_width=$height
                frames=$((width / frame_width))
                frame_time=$((1000 / fps))
                
                cat >> "$config_file" << EOF
  ${base_name}: {
    src: '/assets/sprites/avatar-${base_name}.png',
    frames: ${frames},
    frameWidth: ${frame_width},
    frameHeight: ${height},
    frameTime: ${frame_time},
    loop: ${loop}
  },
EOF
            fi
        fi
    done
    
    echo "};" >> "$config_file"
    
    echo -e "${GREEN}✓ Configuration générée: $config_file${NC}"
    echo ""
fi

# Instructions pour la suite
echo "🚀 Prochaines étapes:"
echo "   1. Vérifiez les sprites générés dans $OUTPUT_DIR/"
echo "   2. Copiez-les dans votre projet React:"
echo "      cp $OUTPUT_DIR/avatar-*.png /chemin/vers/projet/src/assets/sprites/"
echo "   3. Copiez la configuration:"
echo "      cp $OUTPUT_DIR/avatarAnimations.js /chemin/vers/projet/src/config/"
echo "   4. Importez dans votre composant:"
echo "      import { AVATAR_ANIMATIONS } from './config/avatarAnimations';"
echo ""
echo "💡 Pour optimiser davantage les PNG:"
echo "   optipng -o7 $OUTPUT_DIR/*.png"
echo ""
