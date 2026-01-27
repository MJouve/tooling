# 📚 Exemples pratiques d'utilisation

## 🎓 Cas d'usage: Avatar d'apprentissage (ton projet)

### Structure de fichiers recommandée

```
avatars/
├── source/                    # Vidéos MP4 originales
│   ├── idle.mp4
│   ├── celebrate.mp4
│   ├── point.mp4
│   ├── thinking.mp4
│   └── congratulate.mp4
│
└── sprites/                   # Sprite sheets générés
    ├── avatar-idle.png
    ├── avatar-celebrate.png
    ├── avatar-point.png
    ├── avatar-thinking.png
    └── avatar-congratulate.png
```

### Script batch pour générer tous les avatars

```bash
#!/bin/bash
# generate-avatars.sh

SOURCE_DIR="source"
OUTPUT_DIR="sprites"

mkdir -p $OUTPUT_DIR

echo "🎨 Génération des sprites d'avatar..."

# Idle - animation de repos (boucle)
./mp4-to-sprite.py $SOURCE_DIR/idle.mp4 \
    --size=128 \
    --transparent \
    --fps=8 \
    --start=0 \
    --end=3 \
    --output=$OUTPUT_DIR/avatar-idle.png

# Celebrate - félicitation (joue une fois)
./mp4-to-sprite.py $SOURCE_DIR/celebrate.mp4 \
    --size=128 \
    --transparent \
    --fps=12 \
    --start=0 \
    --end=1.5 \
    --tolerance=40 \
    --output=$OUTPUT_DIR/avatar-celebrate.png

# Point - pointer/indiquer (joue une fois)
./mp4-to-sprite.py $SOURCE_DIR/point.mp4 \
    --size=128 \
    --transparent \
    --fps=10 \
    --start=0 \
    --end=1 \
    --output=$OUTPUT_DIR/avatar-point.png

# Thinking - réflexion (boucle)
./mp4-to-sprite.py $SOURCE_DIR/thinking.mp4 \
    --size=128 \
    --transparent \
    --fps=6 \
    --start=0 \
    --end=2 \
    --output=$OUTPUT_DIR/avatar-thinking.png

# Congratulate - grand succès (joue une fois)
./mp4-to-sprite.py $SOURCE_DIR/congratulate.mp4 \
    --size=128 \
    --transparent \
    --fps=15 \
    --start=0 \
    --end=2 \
    --tolerance=35 \
    --output=$OUTPUT_DIR/avatar-congratulate.png

echo "✅ Tous les sprites générés dans $OUTPUT_DIR/"
```

### Configuration React résultante

```javascript
// src/config/avatarAnimations.js
export const AVATAR_ANIMATIONS = {
  idle: {
    src: '/assets/sprites/avatar-idle.png',
    frames: 24,        // 3s × 8fps
    frameWidth: 128,
    frameHeight: 128,
    frameTime: 125,    // 1000ms / 8fps
    loop: true
  },
  celebrate: {
    src: '/assets/sprites/avatar-celebrate.png',
    frames: 18,        // 1.5s × 12fps
    frameWidth: 128,
    frameHeight: 128,
    frameTime: 83,     // 1000ms / 12fps
    loop: false
  },
  point: {
    src: '/assets/sprites/avatar-point.png',
    frames: 10,        // 1s × 10fps
    frameWidth: 128,
    frameHeight: 128,
    frameTime: 100,
    loop: false
  },
  thinking: {
    src: '/assets/sprites/avatar-thinking.png',
    frames: 12,        // 2s × 6fps
    frameWidth: 128,
    frameHeight: 128,
    frameTime: 167,    // 1000ms / 6fps
    loop: true
  },
  congratulate: {
    src: '/assets/sprites/avatar-congratulate.png',
    frames: 30,        // 2s × 15fps
    frameWidth: 128,
    frameHeight: 128,
    frameTime: 67,
    loop: false
  }
};
```

## 🎮 Cas d'usage: Personnage de jeu

```bash
# Marche (cycle)
./mp4-to-sprite.py character-walk.mp4 \
    --size=64 \
    --transparent \
    --fps=12 \
    --start=0 \
    --end=1 \
    --output=character-walk.png

# Course
./mp4-to-sprite.py character-run.mp4 \
    --size=64 \
    --transparent \
    --fps=15 \
    --start=0 \
    --end=0.8 \
    --output=character-run.png

# Saut
./mp4-to-sprite.py character-jump.mp4 \
    --size=64 \
    --transparent \
    --fps=12 \
    --start=0 \
    --end=0.6 \
    --output=character-jump.png

# Attaque
./mp4-to-sprite.py character-attack.mp4 \
    --size=64 \
    --transparent \
    --fps=18 \
    --start=0 \
    --end=0.5 \
    --tolerance=45 \
    --output=character-attack.png
```

## 🎪 Cas d'usage: Éléments UI animés

### Loader / Spinner

```bash
./mp4-to-sprite.py ui-loader.mp4 \
    --size=48 \
    --transparent \
    --fps=20 \
    --start=0 \
    --end=1 \
    --output=ui-loader.png
```

### Bouton hover effet

```bash
./mp4-to-sprite.py button-hover.mp4 \
    --size=40 \
    --transparent \
    --fps=15 \
    --start=0 \
    --end=0.3 \
    --output=button-hover.png
```

### Icône notification

```bash
./mp4-to-sprite.py icon-notification.mp4 \
    --size=32 \
    --transparent \
    --fps=12 \
    --start=0 \
    --end=0.8 \
    --output=icon-notification.png
```

## 🎨 Optimisation selon le type d'animation

### Animation lente (idle, repos, flottement)
```bash
--fps=6-8
--frameTime=125-167ms (calculé automatiquement)
```

### Animation normale (marche, gestes)
```bash
--fps=10-12
--frameTime=83-100ms
```

### Animation rapide (célébration, combat)
```bash
--fps=15-20
--frameTime=50-67ms
```

### Animation très rapide (explosion, effet spécial)
```bash
--fps=24-30
--frameTime=33-42ms
```

## 🔧 Ajustement de la tolérance selon le fond

### Fond très propre (couleur unie parfaite)
```bash
--tolerance=10-20
```
Exemples: fond vert/bleu chroma key professionnel

### Fond normal (quelques variations)
```bash
--tolerance=30-40  # DÉFAUT
```
Exemples: la plupart des exports After Effects

### Fond avec compression ou dégradé
```bash
--tolerance=50-70
```
Exemples: vidéos avec artefacts de compression

### Fond complexe (beaucoup de variations)
```bash
--tolerance=80-100
```
Exemples: fonds avec ombres ou dégradés importants

## 📊 Exemples de tailles selon l'usage

### Mobile (Capacitor/React Native)

```bash
# Petit élément UI
--size=32-48    # ~20-40 KB par sprite sheet

# Avatar normal
--size=64-96    # ~50-120 KB

# Avatar principal
--size=128      # ~100-250 KB

# Grand élément décoratif
--size=256      # ~300-600 KB
```

### Desktop/Web

```bash
# Icône
--size=48-64

# Avatar
--size=128-256

# Personnage
--size=256-512

# Grand visuel
--size=512-1024
```

## 🚀 Pipeline complet de production

```bash
#!/bin/bash
# production-pipeline.sh

# 1. Génère les sprites
./generate-avatars.sh

# 2. Optimise les PNG
echo "🗜️  Optimisation des PNG..."
optipng -o7 sprites/*.png

# 3. Génère les configurations React
echo "⚙️  Génération des configs..."
./generate-config.sh

# 4. Copie dans le projet React
echo "📦 Copie dans le projet..."
cp sprites/*.png ../react-app/src/assets/sprites/
cp config/avatarAnimations.js ../react-app/src/config/

# 5. Build React
echo "🔨 Build React..."
cd ../react-app
npm run build

# 6. Sync Capacitor
echo "📱 Sync Capacitor..."
npx cap sync

echo "✅ Pipeline terminé !"
```

## 💡 Astuces et bonnes pratiques

### 1. Prévisualisation avant conversion

```bash
# Joue juste le segment qui sera converti
ffplay -ss 0 -t 1.5 video.mp4
```

### 2. Vérification de la durée de vidéo

```bash
# Obtient la durée totale
ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 video.mp4
```

### 3. Extraction d'une frame pour test de couleur

```bash
# Extrait la première frame
ffmpeg -i video.mp4 -vframes 1 first-frame.png

# Ensuite vérifie le coin supérieur gauche dans un éditeur
```

### 4. Batch processing avec boucle

```bash
for video in source/*.mp4; do
    name=$(basename "$video" .mp4)
    ./mp4-to-sprite.py "$video" \
        --size=128 \
        --transparent \
        --output="sprites/${name}-sprite.png"
done
```

### 5. Comparaison avant/après

```bash
# Sans transparence
./mp4-to-sprite.py video.mp4 --size=128 --output=without.png

# Avec transparence
./mp4-to-sprite.py video.mp4 --size=128 --transparent --output=with.png

# Compare les tailles
ls -lh without.png with.png
```

## 🎯 Checklist qualité

Avant de valider un sprite sheet:

- [ ] La transparence est propre (pas de halos blancs/gris)
- [ ] Les frames sont fluides (pas de saccades)
- [ ] La taille de fichier est raisonnable (<300 KB)
- [ ] L'animation boucle correctement (pour animations en boucle)
- [ ] Le redimensionnement n'a pas créé de flou excessif
- [ ] Toutes les frames sont présentes (vérifier le nombre)
- [ ] Les proportions sont correctes (pas de déformation)

## 📱 Test dans l'app avant déploiement

```javascript
// Test rapide dans la console du navigateur
const img = new Image();
img.onload = () => {
  console.log('Sprite chargé:', img.width, 'x', img.height);
  console.log('Taille:', (img.width / img.height).toFixed(1), 'frames');
};
img.src = '/assets/sprites/avatar-celebrate.png';
```

## 🔄 Workflow itératif

```bash
# 1. Première tentative
./mp4-to-sprite.py video.mp4 --size=128 --transparent --output=v1.png

# 2. Ajuster si nécessaire
# - Trop de fond restant? Augmente --tolerance
# - Trop flou? Augmente --size
# - Trop de frames? Diminue --fps ou --end

# 3. Nouvelle tentative
./mp4-to-sprite.py video.mp4 --size=128 --transparent --tolerance=50 --output=v2.png

# 4. Compare
ls -lh v*.png

# 5. Valide visuellement
```

Voilà ! Tu as maintenant tout pour créer des sprites professionnels pour ton app d'apprentissage. 🚀
