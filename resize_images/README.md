# 🖼️ Redimensionnement d'images

Outil en ligne de commande pour redimensionner toutes les images d'un dossier afin qu'elles aient les mêmes dimensions. Par défaut, les images sont **étirées** pour correspondre aux dimensions cibles. Avec l'option `--padding`, les images conservent leur ratio d'aspect avec du padding transparent.

## ✨ Fonctionnalités

- ✅ Redimensionnement batch de toutes les images d'un dossier
- 📐 Redimensionnement selon la première image ou dimensions personnalisées
- 🎨 Mode padding transparent pour conserver le ratio d'aspect
- 🔄 Préservation automatique du format original (PNG, JPG, WEBP, etc.)
- 🚀 Environnement virtuel Python pour éviter les conflits
- 💾 Sauvegarde dans un dossier séparé (images originales préservées)

## 📋 Prérequis

- Linux (Ubuntu/Debian recommandé) ou macOS
- Python 3.7+
- Pillow (installé automatiquement)

## 🚀 Installation

### Installation automatique (recommandé)

```bash
chmod +x install.sh
./install.sh
```

Le script va installer automatiquement:
- Un environnement virtuel Python dans `venv/`
- Pillow (bibliothèque d'images Python)
- Configurer les permissions

L'environnement virtuel est géré automatiquement par le script `resize_images.sh`.

### Installation globale (optionnel)

Pour rendre la commande accessible depuis n'importe où :

```bash
chmod +x install-global.sh
./install-global.sh
```

Cela créera un lien symbolique dans `~/.local/bin/`. Assurez-vous que ce dossier est dans votre PATH :

```bash
# Ajoutez à votre ~/.bashrc ou ~/.zshrc si nécessaire
export PATH="$HOME/.local/bin:$PATH"
```

## 📖 Utilisation

### Syntaxe de base

```bash
./resize_images.sh [DOSSIER] [OPTIONS]
# ou depuis n'importe où (après install-global.sh)
resize_images [DOSSIER] [OPTIONS]
```

### Exemples

#### 1. Redimensionnement du dossier actuel (selon la première image)

```bash
./resize_images.sh
```

#### 2. Redimensionnement selon la première image

```bash
./resize_images.sh ./images/
```

Toutes les images seront redimensionnées aux dimensions de la première image trouvée.

#### 3. Redimensionnement avec largeur spécifiée

```bash
./resize_images.sh ./images/ --width 800
```

Redimensionne toutes les images à 800px de largeur, en conservant la hauteur originale de chaque image.

#### 4. Redimensionnement avec hauteur spécifiée

```bash
./resize_images.sh ./images/ --height 600
```

Redimensionne toutes les images à 600px de hauteur, en conservant la largeur originale de chaque image.

#### 5. Redimensionnement avec dimensions exactes (étirement)

```bash
./resize_images.sh ./images/ --width 800 --height 600
```

Redimensionne toutes les images aux dimensions exactes 800x600px (les images seront étirées si nécessaire).

#### 6. Redimensionnement avec padding transparent (ratio conservé)

```bash
./resize_images.sh ./images/ --width 800 --height 600 --padding
```

Les images gardent leur taille originale et sont centrées dans un canvas 800x600px avec du padding transparent équilibré.

#### 7. Dossier de sortie personnalisé

```bash
./resize_images.sh ./images/ --width 1920 --output images_1920
```

Les images redimensionnées seront sauvegardées dans `./images/images_1920/` au lieu de `./images/resized/`.

#### 8. Sans confirmation (pour les scripts)

```bash
./resize_images.sh ./images/ --width 1024 --no-confirm
```

## ⚙️ Options

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `directory` | string | `.` | Dossier contenant les images (défaut: dossier actuel) |
| `--width`, `-w` | int | - | Largeur cible en pixels (optionnel) |
| `--height` | int | - | Hauteur cible en pixels (optionnel) |
| `--output`, `-o` | string | `resized` | Nom du sous-dossier de sortie |
| `--padding` | flag | false | Conserve le ratio d'aspect avec padding transparent |
| `--no-confirm` | flag | false | Ne pas demander de confirmation avant de traiter |

### 💡 Conseils sur les options

**`--width` et `--height`** : Dimensions cibles
- Si seule la largeur est spécifiée : la hauteur originale est conservée pour chaque image
- Si seule la hauteur est spécifiée : la largeur originale est conservée pour chaque image
- Si les deux sont spécifiées : toutes les images sont redimensionnées aux dimensions exactes (étirement)

**`--padding`** : Mode padding transparent
- Les images **ne sont pas redimensionnées**, elles gardent leur taille originale
- L'image est centrée dans un canvas de la taille cible avec du padding transparent équilibré
- Utile pour conserver le ratio d'aspect sans déformation
- Le padding transparent fonctionne mieux avec PNG/WEBP (JPG/JPEG aura un fond blanc)
- Si une image est plus grande que les dimensions cibles, elle sera rognée avec un avertissement

**`--output`** : Dossier de sortie
- Par défaut, les images sont sauvegardées dans un sous-dossier `resized/` du dossier source
- Les images originales ne sont jamais modifiées
- Le format original est préservé (PNG reste PNG, JPG reste JPG, etc.)

## 🎨 Formats supportés

- PNG (avec transparence)
- JPG/JPEG
- GIF
- BMP
- WEBP (avec transparence)
- TIFF

## 🔧 Workflow complet

### 1. Préparez vos images

Placez toutes vos images dans un dossier :

```bash
mkdir photos
cp *.jpg photos/
```

### 2. Redimensionnez selon vos besoins

```bash
# Option A : Selon la première image
./resize_images.sh ./photos/

# Option B : Dimensions spécifiques
./resize_images.sh ./photos/ --width 1920 --height 1080

# Option C : Avec padding transparent (ratio conservé)
./resize_images.sh ./photos/ --width 1920 --height 1080 --padding
```

### 3. Vérifiez les résultats

Les images redimensionnées sont dans `./photos/resized/` (ou le dossier spécifié avec `--output`).

## 🎯 Cas d'usage

### Préparation d'images pour un site web

```bash
# Redimensionne toutes les photos à 1920px de largeur
./resize_images.sh ./photos/ --width 1920 --output web_photos
```

### Uniformisation pour un carousel

```bash
# Toutes les images à 800x600px avec padding transparent
./resize_images.sh ./carousel/ --width 800 --height 600 --padding
```

### Préparation pour un sprite sheet

```bash
# Toutes les images à 128x128px exactement
./resize_images.sh ./sprites/ --width 128 --height 128
```

### Redimensionnement batch sans interaction

```bash
# Pour les scripts automatisés
./resize_images.sh ./images/ --width 1024 --no-confirm
```

## 🐛 Dépannage

### "Environnement virtuel non trouvé"

```bash
cd /chemin/vers/resize_images
./install.sh
```

### "ModuleNotFoundError: No module named 'PIL'"

```bash
# Si vous utilisez directement Python (sans le script wrapper)
pip3 install Pillow --break-system-packages
```

### Les images sont déformées

Utilisez l'option `--padding` pour conserver le ratio d'aspect :

```bash
./resize_images.sh ./images/ --width 800 --height 600 --padding
```

### Le padding est blanc au lieu de transparent

Le padding transparent fonctionne uniquement avec les formats qui supportent la transparence :
- ✅ PNG, WEBP : padding transparent
- ❌ JPG/JPEG : padding blanc (format ne supporte pas la transparence)

### Une image est plus grande que les dimensions cibles avec `--padding`

Un avertissement sera affiché et l'image sera rognée. Pour éviter cela, redimensionnez d'abord l'image ou augmentez les dimensions cibles.

## 📊 Comportement détaillé

### Mode normal (sans `--padding`)

- Les images sont **étirées** pour correspondre aux dimensions cibles
- Si seule la largeur est spécifiée : la hauteur originale est conservée
- Si seule la hauteur est spécifiée : la largeur originale est conservée
- Si les deux dimensions sont spécifiées : étirement pour correspondre exactement

### Mode padding (avec `--padding`)

- Les images **ne sont pas redimensionnées**, elles gardent leur taille originale
- L'image est centrée dans un canvas de la taille cible
- Du padding transparent (ou blanc pour JPG) est ajouté autour
- Le padding est équilibré (haut/bas et gauche/droite)
- Si l'image est plus grande que les dimensions cibles, elle sera rognée

## 📝 Notes importantes

- ✅ Les images originales ne sont **jamais modifiées**
- ✅ Les images redimensionnées sont sauvegardées dans un sous-dossier séparé
- ✅ Le format original est préservé (PNG reste PNG, JPG reste JPG, etc.)
- ✅ L'environnement virtuel est géré automatiquement par le script wrapper
- ⚠️ Par défaut, le script demande confirmation avant de traiter (utilisez `--no-confirm` pour les scripts)

## 📝 Licence

MIT - Utilisation libre pour projets personnels et commerciaux

## 🤝 Contribution

Suggestions et améliorations bienvenues!

---

Fait avec ❤️ pour les développeurs
