# 🎬 MP4toSprite - Convertisseur vidéo vers sprite sheet

Outil en ligne de commande pour convertir des vidéos MP4 en sprite sheets PNG optimisés pour React/Capacitor, avec détection automatique et suppression de fond.

## ✨ Fonctionnalités

- ✅ Extraction de frames depuis n'importe quelle portion de vidéo
- 🎨 Détection automatique du fond (couleur unie ou quadrillage checkerboard)
- 👻 Suppression de fond avec canal alpha transparent
- 📏 Redimensionnement intelligent avec préservation du ratio
- 📐 **Largeur fixe** pour uniformiser toutes les frames
- 📋 **Fichiers de configuration JSON** pour simplifier les générations batch
- 🔢 **Spritesheets multilignes** pour organiser plusieurs animations dans un seul fichier
- 🤖 **Génération batch automatique** avec vérification des fichiers requis
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

#### 5. Largeur fixe (pour uniformiser toutes les frames)

```bash
./mp4-to-sprite.py video.mp4 \
  --size=128 \
  --width=128 \
  --transparent
```

#### 6. Spritesheet multilignes (ajouter une ligne à un fichier existant)

```bash
# Première ligne (ligne 0)
./mp4-to-sprite.py joyeux.mp4 --size=128 --width=128 --transparent --output=familier.png --line=0

# Deuxième ligne (ligne 1)
./mp4-to-sprite.py triste.mp4 --size=128 --width=128 --transparent --output=familier.png --line=1

# Troisième ligne (ligne 2)
./mp4-to-sprite.py neutre.mp4 --size=128 --width=128 --transparent --output=familier.png --line=2
```

#### 7. Utilisation avec fichier de configuration

```bash
# Créez config.json
cat > config.json << EOF
{
  "size": 128,
  "width": 128,
  "transparent": true,
  "tolerance": 30,
  "fps": 12,
  "start": 0,
  "end": 1.5
}
EOF

# Utilisez la config
./mp4-to-sprite.py video.mp4 --config=config.json --output=avatar.png --line=3
```

## ⚙️ Options

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `input` | string | - | **Requis.** Fichier MP4 en entrée |
| `--size` | int | 128 | Hauteur cible en pixels |
| `--width` | int | - | Largeur fixe en pixels (force crop/pad si nécessaire) |
| `--transparent` | flag | false | Active la détection et suppression du fond |
| `--tolerance` | int | 30 | Tolérance de détection de couleur (0-255) |
| `--start` | float | 0 | Temps de début en secondes |
| `--end` | float | durée totale | Temps de fin en secondes |
| `--fps` | int | 10 | Images par seconde à extraire |
| `--output`, `-o` | string | input-sprite.png | Nom du fichier de sortie |
| `--line` | int | - | Numéro de ligne (0-indexed) pour spritesheet multilignes |
| `--config`, `-c` | string | - | Fichier de configuration JSON avec options par défaut |

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

**`--width`**: Largeur fixe pour toutes les frames
- Utile pour uniformiser les dimensions dans un spritesheet multilignes
- Si l'image est plus large: crop centré
- Si l'image est plus étroite: padding transparent centré
- **Recommandé** pour les spritesheets multilignes

**`--line`**: Position dans un spritesheet multilignes
- Numéro de ligne (0-indexed) où placer l'animation
- Si le fichier existe, l'animation est ajoutée à la ligne spécifiée
- Si le fichier n'existe pas, il est créé avec la bonne hauteur
- Les lignes manquantes sont automatiquement remplies de transparence

**`--config`**: Fichier de configuration JSON
- Permet de définir des options par défaut
- Les arguments en ligne de commande ont toujours priorité
- Utile pour les générations batch répétitives

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

## 🎬 Génération batch avec spritesheets multilignes

### Script de génération batch automatique

Le script `generate-spritesheet-batch.py` permet de générer automatiquement un spritesheet multilignes en vérifiant que tous les fichiers requis sont présents.

#### 1. Configurez la liste des fichiers requis

Éditez `generate-spritesheet-batch.py` et modifiez la liste `REQUIRED_FILES` :

```python
REQUIRED_FILES = [
    ("joyeux", 0, "Animation joyeuse"),
    ("triste", 1, "Animation triste"),
    ("neutre", 2, "Animation neutre"),
    ("fatigue", 3, "Animation fatigue"),
    # Ajoutez d'autres animations ici
]
```

#### 2. Préparez vos vidéos

Placez vos fichiers MP4 dans un dossier (ex: `./videos/`) :
```
videos/
├── joyeux.mp4
├── triste.mp4
├── neutre.mp4
└── fatigue.mp4
```

#### 3. Lancez la génération batch

```bash
./generate-spritesheet-batch.py ./videos --output=familier.png --size=128 --width=128
```

Le script va :
- ✅ Vérifier que tous les fichiers requis sont présents
- ⚠️ Afficher une alerte pour les fichiers manquants
- 🎬 Générer le spritesheet multilignes automatiquement
- 📊 Afficher un résumé avec le code React à utiliser

#### 4. Exemple avec fichier de configuration

```bash
# Créez votre config
cat > config-familiers.json << EOF
{
  "size": 128,
  "width": 128,
  "transparent": true,
  "tolerance": 30,
  "fps": 12
}
EOF

# Lancez avec la config
./generate-spritesheet-batch.py ./videos --output=familier.png --config=config-familiers.json
```

#### 5. Utilisation dans React

Le script génère automatiquement le code React à utiliser :

```javascript
const spriteSheet = {
  src: '/assets/familier.png',
  frameHeight: 128,
  frameWidth: 128,
  animations: {
    joyeux: { line: 0 },   // Animation joyeuse
    triste: { line: 1 },   // Animation triste
    neutre: { line: 2 },   // Animation neutre
    fatigue: { line: 3 },  // Animation fatigue
  }
};
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

### Spritesheet multilignes pour familiers

```bash
# Créez un fichier de configuration
cat > config-familiers.json << EOF
{
  "size": 128,
  "width": 128,
  "transparent": true,
  "tolerance": 30,
  "fps": 12
}
EOF

# Méthode 1 : Génération manuelle ligne par ligne
./mp4-to-sprite.py joyeux.mp4 --config=config-familiers.json --output=familier.png --line=0
./mp4-to-sprite.py triste.mp4 --config=config-familiers.json --output=familier.png --line=1
./mp4-to-sprite.py neutre.mp4 --config=config-familiers.json --output=familier.png --line=2
./mp4-to-sprite.py fatigue.mp4 --config=config-familiers.json --output=familier.png --line=3

# Méthode 2 : Génération batch automatique (recommandé)
./generate-spritesheet-batch.py ./videos --output=familier.png --config=config-familiers.json
```

## 📄 Fichier de configuration JSON

Vous pouvez créer un fichier JSON pour définir des options par défaut et éviter de les ressaisir à chaque fois.

### Format du fichier

```json
{
  "size": 128,
  "width": 128,
  "transparent": true,
  "tolerance": 30,
  "fps": 12,
  "start": 0,
  "end": 1.5
}
```

### Utilisation

```bash
./mp4-to-sprite.py video.mp4 --config=config.json --output=avatar.png
```

Les arguments en ligne de commande ont toujours priorité sur le fichier de configuration.

### Exemple de fichier

Un fichier `config-example.json` est fourni dans le dépôt comme référence.

## 📝 Licence

MIT - Utilisation libre pour projets personnels et commerciaux

## 🤝 Contribution

Suggestions et améliorations bienvenues!

## 📧 Support

Pour toute question ou problème, ouvre une issue sur le dépôt.

---

Fait avec ❤️ pour les développeurs React/Capacitor
