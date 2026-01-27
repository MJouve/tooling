# 🚀 Démarrage rapide - MP4toSprite

Guide ultra-rapide pour commencer en 5 minutes.

## ⚡ Installation express (Linux/Ubuntu)

```bash
# 1. Télécharge et dézippe le projet
unzip mp4-to-sprite.zip
cd mp4-to-sprite

# 2. Lance l'installation automatique
./install.sh

# 3. C'est prêt !
```

## 🎯 Premier usage

### Exemple simple : Convertir une vidéo

```bash
# Ta vidéo : celebrate.mp4 (2 secondes)
# Tu veux : Sprite transparent, 128px de haut, première seconde seulement

./mp4-to-sprite.py celebrate.mp4 --size=128 --transparent --start=0 --end=1
```

**Résultat :** `celebrate-sprite.png` créé avec transparence ! 🎉

## 📋 Commandes essentielles

### Sans transparence (fond conservé)
```bash
./mp4-to-sprite.py video.mp4 --size=200
```

### Avec transparence (fond supprimé)
```bash
./mp4-to-sprite.py video.mp4 --size=200 --transparent
```

### Segment spécifique (0.5s à 2s)
```bash
./mp4-to-sprite.py video.mp4 --size=128 --transparent --start=0.5 --end=2
```

### Plus de frames (animation fluide)
```bash
./mp4-to-sprite.py video.mp4 --size=128 --transparent --fps=15
```

### Fond difficile (augmente tolérance)
```bash
./mp4-to-sprite.py video.mp4 --size=128 --transparent --tolerance=50
```

## 🎓 Ton cas : Avatar d'apprentissage

### Structure recommandée

```
mon-projet/
├── source/              # Mets tes MP4 ici
│   ├── idle.mp4
│   ├── celebrate.mp4
│   └── point.mp4
└── sprites/            # Les PNG générés iront ici
```

### Génération des avatars

```bash
# 1. Crée les dossiers
mkdir -p source sprites

# 2. Copie tes vidéos dans source/
cp ~/Downloads/*.mp4 source/

# 3. Génère les sprites
./mp4-to-sprite.py source/idle.mp4 --size=128 --transparent --fps=8 --output=sprites/avatar-idle.png
./mp4-to-sprite.py source/celebrate.mp4 --size=128 --transparent --fps=12 --start=0 --end=1.5 --output=sprites/avatar-celebrate.png
./mp4-to-sprite.py source/point.mp4 --size=128 --transparent --fps=10 --start=0 --end=1 --output=sprites/avatar-point.png

# 4. Copie dans ton projet React
cp sprites/*.png /chemin/vers/ton-app/src/assets/sprites/
```

### Ou utilise le script batch (recommandé)

```bash
# 1. Place tes vidéos dans source/
mkdir source
cp tes-videos/*.mp4 source/

# 2. Lance la génération automatique
./generate-avatars.sh

# 3. Les sprites sont dans sprites/
# 4. Le fichier de config React est généré automatiquement !
```

## 🎨 Code React pour utiliser les sprites

```jsx
// Avatar.jsx
import { useState, useEffect } from 'react';

function Avatar({ animation = 'idle' }) {
  const [frame, setFrame] = useState(0);
  
  const config = {
    idle: { src: '/assets/sprites/avatar-idle.png', frames: 24, frameTime: 125 },
    celebrate: { src: '/assets/sprites/avatar-celebrate.png', frames: 18, frameTime: 83 }
  }[animation];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setFrame(f => (f + 1) % config.frames);
    }, config.frameTime);
    return () => clearInterval(interval);
  }, [animation, config]);
  
  return (
    <div 
      style={{
        width: '128px',
        height: '128px',
        backgroundImage: `url(${config.src})`,
        backgroundPosition: `-${frame * 128}px 0px`
      }}
    />
  );
}

// Utilisation
<Avatar animation="celebrate" />
```

## 🐛 Problèmes courants

### "command not found: ffmpeg"
```bash
sudo apt install ffmpeg
```

### "No module named 'PIL'"
```bash
pip3 install Pillow --break-system-packages
```

### La transparence ne marche pas bien
```bash
# Augmente la tolérance
./mp4-to-sprite.py video.mp4 --transparent --tolerance=50
```

### Le fichier est trop gros
```bash
# Réduis la taille ou les FPS
./mp4-to-sprite.py video.mp4 --size=64 --fps=8
```

## 📱 Pour Capacitor

```bash
# 1. Génère tes sprites optimisés
./mp4-to-sprite.py video.mp4 --size=128 --transparent --fps=10

# 2. Copie dans ton projet
cp *.png /ton-projet/src/assets/sprites/

# 3. Build et sync
cd /ton-projet
npm run build
npx cap sync
```

## 💡 Paramètres recommandés par usage

### Avatar app mobile (ton cas)
```bash
--size=128 --fps=10 --transparent
```

### Personnage de jeu
```bash
--size=64 --fps=12 --transparent
```

### Icône/UI
```bash
--size=32 --fps=15 --transparent
```

### Grand visuel
```bash
--size=256 --fps=15 --transparent
```

## 🎯 Checklist avant de déployer

- [ ] Sprite transparent (pas de fond blanc)
- [ ] Taille < 300 KB
- [ ] Animation fluide (pas de saccades)
- [ ] Boucle correctement (si animation en loop)
- [ ] Testé dans ton app React

## 📚 Pour aller plus loin

- **README.md** : Documentation complète
- **EXAMPLES.md** : Cas d'usage détaillés
- **test.sh** : Teste le script avec des vidéos synthétiques

## 🆘 Besoin d'aide ?

```bash
# Affiche l'aide complète
./mp4-to-sprite.py --help

# Teste avec une vidéo synthétique
./test.sh
```

## ✅ C'est tout !

Tu es prêt à créer des sprites animés pour ton app d'apprentissage ! 🎓🚀

**Workflow typique :**
1. Export tes animations en MP4 (After Effects, Blender, IA...)
2. Lance `./mp4-to-sprite.py` avec tes paramètres
3. Copie le PNG dans ton projet React
4. Utilise le composant Avatar
5. Profit ! 🎉
