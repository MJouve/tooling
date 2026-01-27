# 🎬 MP4toSprite - Convertisseur vidéo vers sprite sheet

Outil en ligne de commande pour convertir des vidéos MP4 en sprite sheets PNG optimisés pour React/Capacitor, avec détection automatique et suppression de fond.

## ✨ Fonctionnalités

- ✅ Extraction de frames depuis n'importe quelle portion de vidéo
- 🎨 Détection automatique du fond (couleur unie ou quadrillage checkerboard)
- 👻 Suppression de fond avec canal alpha transparent
- 📏 Redimensionnement intelligent avec préservation du ratio
- 🚀 Optimisé pour les apps React avec Capacitor
- 💾 Export PNG optimisé avec compression

## 📋 Prérequis

- Linux (Ubuntu/Debian recommandé) ou macOS
- Python 3.7+
- FFmpeg

## 🚀 Installation

### Installation automatique (recommandé)

```bash
chmod +x install.sh
./install.sh
```

Le script va installer automatiquement:
- FFmpeg (si non présent)
- Pillow (bibliothèque d'images Python)
- Configurer les permissions

### Installation manuelle

```bash
# Installer FFmpeg
sudo apt update
sudo apt install ffmpeg ffprobe

# Installer les dépendances Python
pip3 install -r requirements.txt --break-system-packages

# Rendre le script exécutable
chmod +x mp4-to-sprite.py
```

### Installation globale (optionnel)

Pour utiliser `mp4-to-sprite` depuis n'importe où:

```bash
sudo ln -s $(pwd)/mp4-to-sprite.py /usr/local/bin/mp4-to-sprite
```

## 📖 Utilisation

### Syntaxe de base

```bash
./mp4-to-sprite.py VIDEO.mp4 [OPTIONS]
```

### Exemples

#### 1. Conversion simple (première seconde, 300px de haut)

```bash
./mp4-to-sprite.py video.mp4 --size=300 --transparent --start=0 --end=1
```

#### 2. Avatar d'apprentissage (célébration)

```bash
./mp4-to-sprite.py celebrate.mp4 \
  --size=128 \
  --transparent \
  --fps=12 \
  --start=0 \
  --end=1.5 \
  --output=avatar-celebrate.png
```

#### 3. Animation complète avec haute tolérance

```bash
./mp4-to-sprite.py character-walk.mp4 \
  --size=256 \
  --transparent \
  --tolerance=50 \
  --fps=15
```

#### 4. Segment spécifique (de 2s à 4s)

```bash
./mp4-to-sprite.py video.mp4 \
  --start=2 \
  --end=4 \
  --size=200 \
  --transparent
```

## ⚙️ Options

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `input` | string | - | **Requis.** Fichier MP4 en entrée |
| `--size` | int | 128 | Hauteur cible en pixels |
| `--transparent` | flag | false | Active la détection et suppression du fond |
| `--tolerance` | int | 30 | Tolérance de détection de couleur (0-255) |
| `--start` | float | 0 | Temps de début en secondes |
| `--end` | float | durée totale | Temps de fin en secondes |
| `--fps` | int | 10 | Images par seconde à extraire |
| `--output` | string | input-sprite.png | Nom du fichier de sortie |

### 💡 Conseils sur les options

**`--size`**: La hauteur du sprite final
- Avatar: 128-256px
- Personnage de jeu: 64-128px
- Grand élément UI: 256-512px

**`--transparent`**: Active la suppression de fond
- Détecte automatiquement les fonds unis
- Reconnaît les quadrillages gris/blanc (checkerboard)
- Échantillonne le coin supérieur gauche

**`--tolerance`**: Sensibilité de la détection
- `10-20`: Fond très uniforme (uni)
- `30-40`: Fond légèrement variable (défaut)
- `50-80`: Fond avec variations (dégradés légers)

**`--fps`**: Nombre d'images par seconde
- Animation rapide: 15-24 fps
- Animation normale: 10-12 fps (défaut)
- Animation lente: 6-8 fps

## 🎨 Détection de fond

Le script détecte automatiquement deux types de fonds:

### 1. Fond uni
Couleur unique (ex: blanc, vert, bleu)

### 2. Fond quadrillé (checkerboard)
Pattern gris clair/gris foncé souvent utilisé par:
- Adobe After Effects
- Blender
- DaVinci Resolve
- Outils de génération d'images IA

Le script détecte les deux couleurs et les rend transparentes.

## 📱 Intégration React/Capacitor

Le script affiche automatiquement le code React à utiliser:

```javascript
// Configuration générée automatiquement
const config = {
  src: '/assets/avatar-celebrate.png',
  frames: 12,
  frameWidth: 143,
  frameHeight: 128
};

// Utilisation dans ton composant
<Avatar animation="celebrate" />
```

### Exemple complet

```jsx
import { useState, useEffect } from 'react';

const ANIMATIONS = {
  celebrate: {
    src: '/assets/sprites/avatar-celebrate.png',
    frames: 12,
    frameWidth: 143,
    frameHeight: 128,
    frameTime: 100
  }
};

function Avatar({ animation }) {
  const [frame, setFrame] = useState(0);
  const config = ANIMATIONS[animation];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setFrame(prev => (prev + 1) % config.frames);
    }, config.frameTime);
    
    return () => clearInterval(interval);
  }, [animation, config]);
  
  return (
    <div 
      style={{
        width: `${config.frameWidth}px`,
        height: `${config.frameHeight}px`,
        backgroundImage: `url(${config.src})`,
        backgroundPosition: `-${frame * config.frameWidth}px 0px`
      }}
    />
  );
}
```

## 🔧 Workflow complet

### 1. Prépare ta vidéo
- Export depuis After Effects, Blender, ou outil IA
- Assure-toi que le fond est uni ou en checkerboard
- Durée recommandée: 1-3 secondes par animation

### 2. Converti en sprite sheet

```bash
# Animation idle (boucle)
./mp4-to-sprite.py idle.mp4 \
  --size=128 \
  --transparent \
  --output=avatar-idle.png

# Animation célébration (une fois)
./mp4-to-sprite.py celebrate.mp4 \
  --size=128 \
  --transparent \
  --start=0 \
  --end=1.5 \
  --output=avatar-celebrate.png

# Animation pointer
./mp4-to-sprite.py point.mp4 \
  --size=128 \
  --transparent \
  --start=0 \
  --end=1 \
  --output=avatar-point.png
```

### 3. Optimise les PNG (optionnel)

```bash
# Avec optipng
optipng -o7 avatar-*.png

# Ou avec pngquant (réduction palette)
pngquant --quality=80-95 avatar-*.png
```

### 4. Intègre dans ton projet

```bash
# Copie dans ton projet React
cp avatar-*.png /chemin/vers/ton-projet/src/assets/sprites/

# Build pour mobile
cd /chemin/vers/ton-projet
npm run build
npx cap sync
```

## 🐛 Dépannage

### "ffmpeg n'est pas installé"

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Vérifie l'installation
ffmpeg -version
```

### "ModuleNotFoundError: No module named 'PIL'"

```bash
pip3 install Pillow --break-system-packages
```

### La transparence ne fonctionne pas bien

1. Augmente la tolérance: `--tolerance=50`
2. Vérifie que le fond est bien uniforme
3. Essaie d'échantillonner une autre zone (modifie le code si nécessaire)

### Les frames sont floues

1. Augmente le FPS: `--fps=20`
2. Vérifie la qualité de la vidéo source
3. Utilise une vidéo plus haute résolution

### Le fichier PNG est trop gros

```bash
# Réduis la hauteur
./mp4-to-sprite.py video.mp4 --size=64

# Réduis le FPS
./mp4-to-sprite.py video.mp4 --fps=8

# Optimise après coup
optipng -o7 output.png
```

## 📊 Performance

Pour une app Capacitor optimale:

- **Taille recommandée**: 64-128px de haut
- **FPS recommandé**: 8-12 fps
- **Durée recommandée**: 1-2 secondes
- **Poids final**: 50-300 KB par sprite sheet

Exemple de résultats:
- Avatar 128px, 12 frames, 1.2s: ~180 KB
- Avatar 256px, 15 frames, 1.5s: ~420 KB
- Avatar 64px, 8 frames, 0.8s: ~85 KB

## 🎯 Cas d'usage

### Avatar d'apprentissage (ton cas)

```bash
# Idle (repos)
./mp4-to-sprite.py idle.mp4 --size=128 --transparent --fps=8 --output=avatar-idle.png

# Célébration
./mp4-to-sprite.py celebrate.mp4 --size=128 --transparent --fps=12 --start=0 --end=1 --output=avatar-celebrate.png

# Pointer/indiquer
./mp4-to-sprite.py point.mp4 --size=128 --transparent --fps=10 --start=0 --end=0.8 --output=avatar-point.png

# Réfléchir
./mp4-to-sprite.py think.mp4 --size=128 --transparent --fps=8 --output=avatar-think.png
```

### Personnage de jeu

```bash
# Marche
./mp4-to-sprite.py walk.mp4 --size=64 --transparent --fps=12

# Saut
./mp4-to-sprite.py jump.mp4 --size=64 --transparent --start=0 --end=0.5

# Attaque
./mp4-to-sprite.py attack.mp4 --size=64 --transparent --start=0 --end=0.6
```

### Icône animée

```bash
./mp4-to-sprite.py icon-loading.mp4 --size=32 --transparent --fps=15
```

## 📝 Licence

MIT - Utilisation libre pour projets personnels et commerciaux

## 🤝 Contribution

Suggestions et améliorations bienvenues!

## 📧 Support

Pour toute question ou problème, ouvre une issue sur le dépôt.

---

Fait avec ❤️ pour les développeurs React/Capacitor
