# Redimensionnement d'images

Outil pour redimensionner toutes les images d'un dossier afin qu'elles aient les mêmes dimensions. Les images sont **étirées** (pas de padding) pour correspondre aux dimensions cibles.

## Installation

Le script utilise un environnement virtuel Python pour éviter les conflits avec les packages système :

```bash
./install.sh
```

Cela créera un environnement virtuel dans le dossier `venv/` et installera les dépendances nécessaires. L'environnement virtuel est géré automatiquement par le script `resize_images.sh`.

### Installation globale (optionnel)

Pour rendre la commande accessible depuis n'importe où :

```bash
./install-global.sh
```

Cela créera un lien symbolique dans `~/.local/bin/`. Assurez-vous que ce dossier est dans votre PATH.

## Utilisation

### Redimensionnement du dossier actuel (par défaut)

Si aucun dossier n'est spécifié, le script traite le dossier actuel :

```bash
./resize_images.sh
# ou depuis n'importe où (après install-global.sh)
resize_images
```

### Redimensionnement selon la première image

Par défaut, le script redimensionne toutes les images selon les dimensions de la première image trouvée :

```bash
./resize_images.sh ./images/
# ou
python3 resize_images.py ./images/
```

**Note** : Le script demande confirmation avant de traiter, affichant le nombre d'images et le dossier concerné.

### Redimensionnement avec largeur spécifiée

Redimensionne toutes les images à une largeur donnée, en conservant la hauteur originale de chaque image :

```bash
./resize_images.sh ./images/ --width 800
# ou
python3 resize_images.py ./images/ -w 800
```

### Redimensionnement avec hauteur spécifiée

Redimensionne toutes les images à une hauteur donnée, en conservant la largeur originale de chaque image :

```bash
./resize_images.sh ./images/ --height 600
# ou
python3 resize_images.py ./images/ -h 600
```

### Redimensionnement avec dimensions exactes

Redimensionne toutes les images aux dimensions exactes spécifiées (étirement) :

```bash
./resize_images.sh ./images/ --width 800 --height 600
# ou
python3 resize_images.py ./images/ -w 800 -h 600
```

### Dossier de sortie personnalisé

Par défaut, les images redimensionnées sont sauvegardées dans un sous-dossier `resized/`. Vous pouvez spécifier un autre nom :

```bash
./resize_images.sh ./images/ -o images_redimensionnees
```

## Options

- `--width`, `-w` : Largeur cible en pixels
- `--height` : Hauteur cible en pixels (note: `-h` est réservé pour `--help`)
- `--output`, `-o` : Nom du sous-dossier de sortie (défaut: `resized`)
- `--no-confirm` : Ne pas demander de confirmation avant de traiter

## Formats supportés

- PNG
- JPG/JPEG
- GIF
- BMP
- WEBP
- TIFF

## Exemples

```bash
# Redimensionne le dossier actuel selon la première image
./resize_images.sh

# Redimensionne selon la première image
./resize_images.sh ./photos/

# Redimensionne à 1920px de largeur
./resize_images.sh ./photos/ --width 1920

# Redimensionne à 1080px de hauteur
./resize_images.sh ./photos/ --height 1080

# Redimensionne à 800x600px exactement
./resize_images.sh ./photos/ --width 800 --height 600

# Avec dossier de sortie personnalisé
./resize_images.sh ./photos/ -w 1024 -o photos_1024

# Sans confirmation (pour les scripts)
./resize_images.sh ./photos/ --no-confirm
```

## Notes

- Les images sont **étirées** pour correspondre aux dimensions cibles (pas de padding, pas de conservation du ratio si les deux dimensions sont spécifiées)
- Les images originales ne sont pas modifiées
- Les images redimensionnées sont sauvegardées dans un sous-dossier du dossier source
- Le format original est préservé (PNG reste PNG, JPG reste JPG, etc.)
- L'environnement virtuel (`venv/`) est créé automatiquement lors de l'installation et géré par le script
