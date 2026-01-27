# 🎨 Sprite Cutter - Outil de Découpe de Sprites

Outil automatique pour découper des sprites depuis une image et rendre le fond transparent.

## 📋 Fonctionnalités

- ✂️ **Découpe automatique** : Détecte et découpe automatiquement chaque sprite dans l'image
- 🎭 **Fond transparent intelligent** : Supprime uniquement le fond blanc externe, préservant les zones blanches internes (yeux, détails)
- 🔗 **Fusion de sprites** : Regroupe automatiquement les parties d'un même personnage (corps + yeux, etc.)
- 🔍 **Filtrage par taille** : Ignore les petits sprites indésirables (taille minimale configurable)
- 📐 **Normalisation de taille** : Ajoute du padding transparent pour que tous les sprites aient la même taille
- 💾 **Sauvegarde PNG** : Sauvegarde chaque sprite en PNG avec canal alpha
- 🎯 **Paramétrable** : Ajustez tous les paramètres selon vos besoins

## 🚀 Installation

### Prérequis

- Python 3.6 ou supérieur
- pip

### Installation des dépendances

**Sur Ubuntu/Debian (recommandé) :**

```bash
sudo apt install python3-pil
```

**Avec environnement virtuel Python :**

```bash
python3 -m venv venv
source venv/bin/activate
pip install Pillow
```

**Avec pip (si autorisé) :**

```bash
pip install -r requirements_sprite_cutter.txt
# ou directement :
pip install Pillow
```

### Installation globale (accessible depuis n'importe où)

Pour pouvoir utiliser `sprite-cutter` depuis n'importe quel dossier :

```bash
cd /home/marc/tooling/sprite_cutter
./install.sh
```

Le script d'installation va :
- Créer un wrapper `sprite-cutter` dans `~/.local/bin`
- Vous proposer d'ajouter `~/.local/bin` à votre PATH si nécessaire
- Rendre la commande accessible depuis n'importe quel dossier

Après l'installation, vous pourrez utiliser :

```bash
# Depuis n'importe quel dossier
sprite-cutter mon_image.png
sprite-cutter mon_image.png -o output/ -t 230
```

💡 **Note** : Si vous avez ajouté `~/.local/bin` au PATH, vous devrez peut-être exécuter `source ~/.bashrc` ou redémarrer votre terminal.

## 📖 Utilisation

### Utilisation basique

**Méthode 1 - Commande globale (recommandé après installation) :**

```bash
sprite-cutter mon_image.png
```

**Méthode 2 - Via le script shell (depuis le dossier du projet) :**

```bash
./cut_sprites.sh mon_image.png
```

**Méthode 3 - Directement avec Python :**

```bash
python3 sprite_cutter.py mon_image.png
```

Cela va :
- Charger `mon_image.png`
- Détecter tous les sprites
- Supprimer le fond blanc
- Sauvegarder les sprites dans le dossier `./mon_image/` (nom du fichier sans extension)

**Exemples :**
- `sprite-cutter sorceress.png` → sortie dans `./sorceress/`
- `sprite-cutter characters.png` → sortie dans `./characters/`
- `sprite-cutter icons/set1.png` → sortie dans `./set1/`

### Options avancées

```bash
# Spécifier le dossier de sortie
sprite-cutter mon_image.png -o mes_sprites/

# Ajuster le seuil de détection (0-255)
sprite-cutter mon_image.png -t 230

# Ajouter plus de padding autour des sprites
sprite-cutter mon_image.png -p 10

# Ajuster la distance de fusion (pour regrouper les parties)
sprite-cutter mon_image.png -m 30

# Désactiver la fusion (garder chaque partie séparée)
sprite-cutter mon_image.png -m 0

# Filtrer les petits sprites (garder >= 150px)
sprite-cutter mon_image.png --min-size 150

# Normaliser tous les sprites à la taille du plus grand
sprite-cutter mon_image.png -n auto

# Normaliser à une taille fixe (512x512 pixels)
sprite-cutter mon_image.png -n 512x512

# Combiner plusieurs options
sprite-cutter mon_image.png -o sprites/ -t 230 -p 10 -m 25 --min-size 100 -n auto
```

### Paramètres

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `input` | Chemin de l'image source | (requis) |
| `-o`, `--output` | Dossier de sortie | Nom du fichier sans extension |
| `-t`, `--threshold` | Seuil de détection du blanc (0-255) | `240` |
| `-p`, `--padding` | Pixels de padding autour du sprite | `5` |
| `-m`, `--merge` | Distance max pour fusionner sprites proches | `20` |
| `--min-size` | Taille minimale d'un côté (pixels) | `200` |
| `-n`, `--normalize` | Normalisation: `auto` ou `WIDTHxHEIGHT` | Désactivé |

### À propos du seuil (threshold)

Le paramètre `--threshold` contrôle la sensibilité de la détection du fond blanc :

- **240 (défaut)** : Détecte uniquement le blanc très pur
- **230-235** : Détecte le blanc et les gris très clairs
- **200-220** : Détecte aussi les gris clairs
- **< 200** : Peut détecter des parties de sprites comme du fond

💡 **Conseil** : Si vos sprites ont des bords gris clairs, utilisez un seuil plus élevé (245-250). Si le fond n'est pas blanc pur, baissez le seuil.

### À propos de la fusion (merge)

Le paramètre `--merge` contrôle la distance maximale pour regrouper les sprites proches :

- **20 (défaut)** : Fusionne les parties d'un personnage (corps + yeux + accessoires)
- **30-50** : Fusion plus agressive, peut regrouper des sprites qui se touchent presque
- **10** : Fusion conservatrice, uniquement les parties très proches
- **0** : Désactive la fusion, chaque région détectée reste séparée

💡 **Conseil** : Si des parties de vos personnages (comme les yeux) sont séparées du corps, augmentez la valeur. Si des sprites différents sont fusionnés à tort, diminuez-la ou désactivez-la avec `-m 0`.

### À propos de la taille minimale (min-size)

Le paramètre `--min-size` filtre les sprites trop petits :

- **200 (défaut)** : Garde uniquement les sprites d'au moins 200px de côté (largeur OU hauteur)
- **100** : Moins restrictif, garde des sprites plus petits
- **300** : Plus restrictif, uniquement les grands sprites
- **0** : Désactive le filtrage, garde tous les sprites

💡 **Conseil** : Utilisez ce paramètre pour éliminer les petits artefacts ou détails indésirables détectés par erreur.

### À propos de la normalisation (normalize)

Le paramètre `-n` ou `--normalize` uniformise la taille de tous les sprites :

- **`auto`** : Tous les sprites auront la taille du plus grand sprite détecté
- **`512x512`** : Tous les sprites auront exactement 512x512 pixels
- **`256x256`**, **`1024x1024`**, etc. : Taille personnalisée

Les sprites plus petits sont **centrés** et entourés de **transparence**.

💡 **Conseil** : La normalisation est très utile pour :
- Les animations (tous les frames doivent avoir la même taille)
- Les spritesheets (facilite l'assemblage)
- Les jeux vidéo (simplifie la gestion des collisions)

## 📝 Exemples d'utilisation

### Exemple 1 : Spritesheet de personnages

Vous avez une image avec plusieurs personnages sur fond blanc :

```bash
sprite-cutter personnages.png
```

Résultat :
```
personnages/
  ├── personnages_sprite_001.png
  ├── personnages_sprite_002.png
  ├── personnages_sprite_003.png
  └── ...
```

Pour un dossier différent :
```bash
sprite-cutter personnages.png -o characters/
```

### Exemple 2 : Icônes sur fond gris clair

Votre image a un fond gris clair au lieu de blanc pur :

```bash
sprite-cutter icones.png -o icons/ -t 220
```

### Exemple 3 : Sprites précis sans marge

Vous voulez des sprites sans padding :

```bash
sprite-cutter sprites.png -p 0
```

### Exemple 4 : Sprites pour un jeu vidéo

Vous voulez des sprites uniformes de 512x512px, en filtrant les petits détails :

```bash
sprite-cutter game_characters.png --min-size 150 -n 512x512
```

Résultat : Tous les sprites font exactement 512x512px, centrés avec fond transparent

### Exemple 5 : Animation avec frames de taille identique

Pour créer une animation, tous les frames doivent avoir la même taille :

```bash
sprite-cutter animation.png -n auto
```

Résultat : Tous les sprites ont la taille du plus grand frame détecté

## 🔧 Comment ça fonctionne ?

1. **Chargement** : L'image est chargée avec PIL/Pillow
2. **Détection** : Algorithme de flood-fill pour détecter toutes les régions connexes non-blanches
3. **Fusion** : Les régions proches sont fusionnées pour regrouper les parties d'un même sprite
4. **Filtrage** : Les sprites trop petits sont éliminés selon la taille minimale
5. **Découpe** : Chaque sprite détecté est extrait avec son padding
6. **Transparence intelligente** : Seuls les pixels blancs connectés aux bords (le fond) deviennent transparents, les zones blanches internes sont préservées
7. **Normalisation** (optionnel) : Les sprites sont redimensionnés avec du padding transparent pour avoir tous la même taille
8. **Sauvegarde** : Chaque sprite est sauvegardé en PNG avec canal alpha

### 🎯 Gestion intelligente du fond blanc

L'outil utilise un algorithme avancé pour distinguer :
- **Fond blanc externe** → rendu transparent
- **Zones blanches internes** (yeux, pupilles, détails) → préservées

Cela évite que les yeux des personnages ou d'autres détails blancs soient rendus transparents !

## 🐛 Dépannage

### Problème : Aucun sprite détecté

**Solutions** :
- Vérifiez que votre image a bien un fond clair (blanc ou proche)
- Ajustez le seuil avec `-t` (essayez 220, 200, etc.)
- Vérifiez que les sprites font plus de 10x10 pixels

### Problème : Trop de petits sprites détectés

**Solutions** :
- Augmentez le seuil `-t` pour ignorer le bruit
- Le script ignore déjà les sprites < 10x10 pixels (modifiable dans le code)

### Problème : Les bords des sprites sont coupés

**Solutions** :
- Augmentez le padding avec `-p 10` ou plus
- Vérifiez que le fond autour des sprites est bien uniforme

### Problème : Des parties du sprite deviennent transparentes

**Solutions** :
- Ce problème devrait être résolu avec la nouvelle version ! Les zones blanches internes sont maintenant préservées
- Si le problème persiste, augmentez le seuil `-t 250`

### Problème : Des parties d'un sprite sont séparées (ex: yeux séparés du corps)

**Solutions** :
- Augmentez la distance de fusion avec `-m 30` ou `-m 50`
- La valeur par défaut est 20 pixels, mais vous pouvez aller jusqu'à 50+ si nécessaire

### Problème : Des sprites différents sont fusionnés ensemble

**Solutions** :
- Diminuez la distance de fusion avec `-m 10` ou `-m 5`
- Désactivez complètement la fusion avec `-m 0`

### Problème : Beaucoup de petits sprites indésirables sont détectés

**Solutions** :
- Augmentez la taille minimale avec `--min-size 250` ou `--min-size 300`
- Ajustez aussi le seuil si nécessaire `-t 245`

### Problème : Sprites de tailles différentes difficiles à utiliser

**Solutions** :
- Utilisez la normalisation automatique `-n auto`
- Ou fixez une taille spécifique `-n 512x512`
- Combinez avec le filtrage : `--min-size 150 -n auto`

## 📄 Licence

Outil libre d'utilisation pour votre projet.

## 🤝 Contribution

N'hésitez pas à modifier le script selon vos besoins !

