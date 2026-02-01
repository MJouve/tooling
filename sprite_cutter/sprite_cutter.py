#!/usr/bin/env python3
"""
Outil de découpe de sprites
============================
Cet outil permet de :
- Charger une image contenant plusieurs sprites
- Détecter et découper automatiquement chaque sprite
- Supprimer le fond blanc pour le rendre transparent
- Sauvegarder chaque sprite en PNG avec canal alpha
"""

import os
import sys
from PIL import Image, ImageChops
import argparse


def remove_white_background(image, threshold=240):
    """
    Supprime le fond blanc d'une image et le rend transparent.
    Seuls les pixels blancs connectés aux bords sont supprimés,
    préservant ainsi les zones blanches internes (comme les yeux).
    
    Args:
        image: Image PIL en mode RGB ou RGBA
        threshold: Seuil pour considérer un pixel comme blanc (0-255)
    
    Returns:
        Image PIL avec fond transparent
    """
    # Convertir en RGBA si nécessaire
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    width, height = image.size
    pixels = image.load()
    
    # Créer une matrice pour marquer les pixels blancs connectés aux bords
    is_background = [[False] * width for _ in range(height)]
    visited = [[False] * width for _ in range(height)]
    
    def is_white(x, y):
        """Vérifie si un pixel est blanc selon le seuil"""
        if x < 0 or x >= width or y < 0 or y >= height:
            return False
        r, g, b = pixels[x, y][:3]
        return r > threshold and g > threshold and b > threshold
    
    def flood_fill_background(start_x, start_y):
        """Marque tous les pixels blancs connectés aux bords comme fond"""
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if visited[y][x] or not is_white(x, y):
                continue
            
            visited[y][x] = True
            is_background[y][x] = True
            
            # Ajouter les voisins (8-connectivité)
            stack.extend([
                (x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)
            ])
    
    # Lancer le flood-fill depuis tous les pixels blancs des bords
    # Bord haut et bas
    for x in range(width):
        if is_white(x, 0):
            flood_fill_background(x, 0)
        if is_white(x, height - 1):
            flood_fill_background(x, height - 1)
    
    # Bord gauche et droite
    for y in range(height):
        if is_white(0, y):
            flood_fill_background(0, y)
        if is_white(width - 1, y):
            flood_fill_background(width - 1, y)
    
    # Créer la nouvelle image avec transparence seulement pour le fond
    new_data = []
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y] if image.mode == 'RGBA' else (*pixels[x, y], 255)
            
            if is_background[y][x]:
                # Rendre le fond transparent
                new_data.append((255, 255, 255, 0))
            else:
                # Conserver le pixel (même s'il est blanc mais à l'intérieur)
                new_data.append((r, g, b, a))
    
    image.putdata(new_data)
    return image


def find_sprite_bounds(image, threshold=240):
    """
    Trouve les limites de chaque sprite dans l'image.
    
    Args:
        image: Image PIL
        threshold: Seuil pour considérer un pixel comme fond blanc
    
    Returns:
        Liste de tuples (x1, y1, x2, y2) représentant les boîtes englobantes
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    width, height = image.size
    pixels = image.load()
    
    # Créer une matrice booléenne pour les pixels non-blancs
    non_white = [[False] * width for _ in range(height)]
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if r < threshold or g < threshold or b < threshold:
                non_white[y][x] = True
    
    # Trouver les sprites en utilisant un algorithme de remplissage (flood fill)
    visited = [[False] * width for _ in range(height)]
    sprites = []
    
    def flood_fill(start_x, start_y):
        """Remplissage récursif pour trouver tous les pixels connectés"""
        stack = [(start_x, start_y)]
        min_x = start_x
        max_x = start_x
        min_y = start_y
        max_y = start_y
        
        while stack:
            x, y = stack.pop()
            
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if visited[y][x] or not non_white[y][x]:
                continue
            
            visited[y][x] = True
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            
            # Ajouter les voisins (4-connectivité)
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
            # Ajouter les diagonales (8-connectivité pour de meilleurs résultats)
            stack.extend([(x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)])
        
        return (min_x, min_y, max_x + 1, max_y + 1)
    
    # Parcourir l'image pour trouver tous les sprites
    for y in range(height):
        for x in range(width):
            if non_white[y][x] and not visited[y][x]:
                bounds = flood_fill(x, y)
                # Ignorer les très petits sprites (probablement du bruit)
                width_sprite = bounds[2] - bounds[0]
                height_sprite = bounds[3] - bounds[1]
                if width_sprite > 10 and height_sprite > 10:
                    sprites.append(bounds)
    
    return sprites


def merge_nearby_sprites(sprites, max_distance=20):
    """
    Fusionne les sprites qui sont proches les uns des autres.
    Cela permet de regrouper les parties d'un même personnage (corps + yeux, etc.)
    
    Args:
        sprites: Liste de tuples (x1, y1, x2, y2)
        max_distance: Distance maximale pour considérer deux sprites comme proches
    
    Returns:
        Liste de sprites fusionnés
    """
    if not sprites:
        return []
    
    # Créer une liste de sprites avec un indicateur de groupe
    sprite_groups = [[sprite] for sprite in sprites]
    
    # Fonction pour vérifier si deux boîtes sont proches
    def are_close(box1, box2, max_dist):
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculer la distance entre les boîtes
        # Distance horizontale
        if x2_1 < x1_2:
            dx = x1_2 - x2_1
        elif x2_2 < x1_1:
            dx = x1_1 - x2_2
        else:
            dx = 0
        
        # Distance verticale
        if y2_1 < y1_2:
            dy = y1_2 - y2_1
        elif y2_2 < y1_1:
            dy = y1_1 - y2_2
        else:
            dy = 0
        
        # Distance euclidienne
        distance = (dx**2 + dy**2)**0.5
        return distance <= max_dist
    
    # Fonction pour fusionner deux boîtes
    def merge_boxes(box1, box2):
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        return (
            min(x1_1, x1_2),
            min(y1_1, y1_2),
            max(x2_1, x2_2),
            max(y2_1, y2_2)
        )
    
    # Fusionner itérativement les sprites proches
    changed = True
    while changed:
        changed = False
        new_groups = []
        used = set()
        
        for i, group1 in enumerate(sprite_groups):
            if i in used:
                continue
            
            # Calculer la boîte englobante du groupe
            box1 = group1[0]
            for sprite in group1[1:]:
                box1 = merge_boxes(box1, sprite)
            
            # Chercher d'autres groupes à fusionner
            merged = False
            for j, group2 in enumerate(sprite_groups[i+1:], i+1):
                if j in used:
                    continue
                
                # Calculer la boîte englobante du groupe 2
                box2 = group2[0]
                for sprite in group2[1:]:
                    box2 = merge_boxes(box2, sprite)
                
                # Si les boîtes sont proches, fusionner les groupes
                if are_close(box1, box2, max_distance):
                    group1.extend(group2)
                    used.add(j)
                    changed = True
                    merged = True
            
            new_groups.append(group1)
        
        sprite_groups = new_groups
    
    # Créer les boîtes englobantes finales
    merged_sprites = []
    for group in sprite_groups:
        box = group[0]
        for sprite in group[1:]:
            box = merge_boxes(box, sprite)
        merged_sprites.append(box)
    
    return merged_sprites


def add_padding(bounds, padding, image_width, image_height):
    """
    Ajoute du padding autour d'une boîte englobante.
    
    Args:
        bounds: Tuple (x1, y1, x2, y2)
        padding: Nombre de pixels de padding
        image_width: Largeur de l'image source
        image_height: Hauteur de l'image source
    
    Returns:
        Tuple (x1, y1, x2, y2) avec padding
    """
    x1, y1, x2, y2 = bounds
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(image_width, x2 + padding)
    y2 = min(image_height, y2 + padding)
    return (x1, y1, x2, y2)


def normalize_sprite_size(sprite, target_width, target_height):
    """
    Normalise la taille d'un sprite en ajoutant du padding transparent.
    Le sprite est centré dans la nouvelle taille.
    
    Args:
        sprite: Image PIL
        target_width: Largeur cible
        target_height: Hauteur cible
    
    Returns:
        Image PIL normalisée
    """
    if sprite.size[0] == target_width and sprite.size[1] == target_height:
        return sprite
    
    # Créer une nouvelle image transparente
    normalized = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
    
    # Calculer la position pour centrer le sprite
    x_offset = (target_width - sprite.size[0]) // 2
    y_offset = (target_height - sprite.size[1]) // 2
    
    # Coller le sprite au centre
    normalized.paste(sprite, (x_offset, y_offset), sprite if sprite.mode == 'RGBA' else None)
    
    return normalized


def remove_background_only(input_path, output_path, threshold=240):
    """
    Supprime uniquement le fond blanc d'une image sans découper ni redimensionner.
    
    Args:
        input_path: Chemin de l'image source
        output_path: Chemin de l'image de sortie
        threshold: Seuil pour la détection du fond blanc (0-255)
    """
    # Charger l'image
    print(f"📁 Chargement de l'image: {input_path}")
    image = Image.open(input_path)
    print(f"   Taille: {image.size[0]}x{image.size[1]} pixels")
    
    # Supprimer le fond blanc
    print(f"🎨 Suppression du fond blanc (seuil: {threshold})...")
    image = remove_white_background(image, threshold)
    
    # Créer le dossier de sortie si nécessaire
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder l'image
    image.save(output_path, 'PNG')
    print(f"✅ Image sauvegardée: {output_path}")
    print(f"\n🎉 Terminé ! Fond blanc supprimé et sauvegardé dans {output_path}")


def cut_sprites(input_path, output_dir, threshold=240, padding=5, merge_distance=20, 
                min_size=200, normalize_size=None):
    """
    Découpe les sprites d'une image et les sauvegarde.
    
    Args:
        input_path: Chemin de l'image source
        output_dir: Dossier de sortie pour les sprites
        threshold: Seuil pour la détection du fond blanc (0-255)
        padding: Pixels de padding autour de chaque sprite
        merge_distance: Distance max pour fusionner les sprites proches (0 = désactivé)
        min_size: Taille minimale d'un côté pour garder un sprite (0 = désactivé)
        normalize_size: Tuple (width, height) pour normaliser ou "auto" pour la taille max
    """
    # Charger l'image
    print(f"📁 Chargement de l'image: {input_path}")
    image = Image.open(input_path)
    print(f"   Taille: {image.size[0]}x{image.size[1]} pixels")
    
    # Trouver les sprites
    print(f"🔍 Détection des sprites (seuil: {threshold})...")
    sprite_bounds = find_sprite_bounds(image, threshold)
    print(f"   🔎 {len(sprite_bounds)} région(s) détectée(s)")
    
    if len(sprite_bounds) == 0:
        print("⚠️  Aucun sprite détecté. Essayez d'ajuster le paramètre --threshold")
        return
    
    # Fusionner les sprites proches (ex: corps + yeux)
    if merge_distance > 0:
        sprite_bounds = merge_nearby_sprites(sprite_bounds, merge_distance)
        print(f"   🔗 {len(sprite_bounds)} sprite(s) après fusion (distance: {merge_distance}px)")
    else:
        print(f"   ✅ {len(sprite_bounds)} sprite(s) (fusion désactivée)")
    
    # Filtrer par taille minimale
    if min_size > 0:
        original_count = len(sprite_bounds)
        sprite_bounds = [
            bounds for bounds in sprite_bounds
            if (bounds[2] - bounds[0] >= min_size or bounds[3] - bounds[1] >= min_size)
        ]
        if len(sprite_bounds) < original_count:
            print(f"   🔍 {len(sprite_bounds)} sprite(s) après filtrage (taille min: {min_size}px)")
    
    if len(sprite_bounds) == 0:
        print("⚠️  Aucun sprite ne respecte la taille minimale")
        return
    
    # Créer le dossier de sortie
    os.makedirs(output_dir, exist_ok=True)
    print(f"📂 Dossier de sortie: {output_dir}")
    
    # Extraire tous les sprites d'abord
    sprites_data = []
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    for i, bounds in enumerate(sprite_bounds, 1):
        # Ajouter du padding
        padded_bounds = add_padding(bounds, padding, image.size[0], image.size[1])
        
        # Découper le sprite
        sprite = image.crop(padded_bounds)
        
        # Supprimer le fond blanc
        sprite = remove_white_background(sprite, threshold)
        
        sprites_data.append({
            'sprite': sprite,
            'index': i,
            'bounds': padded_bounds
        })
    
    # Calculer la taille de normalisation si nécessaire
    target_width = None
    target_height = None
    
    if normalize_size == "auto":
        # Trouver la taille maximale
        max_width = max(data['sprite'].size[0] for data in sprites_data)
        max_height = max(data['sprite'].size[1] for data in sprites_data)
        target_width = max_width
        target_height = max_height
        print(f"📐 Normalisation automatique: {target_width}x{target_height}px")
    elif normalize_size and isinstance(normalize_size, tuple):
        target_width, target_height = normalize_size
        print(f"📐 Normalisation à la taille: {target_width}x{target_height}px")
    
    # Sauvegarder les sprites
    for data in sprites_data:
        sprite = data['sprite']
        
        # Normaliser la taille si demandé
        if target_width and target_height:
            sprite = normalize_sprite_size(sprite, target_width, target_height)
        
        # Sauvegarder
        output_path = os.path.join(output_dir, f"{base_name}_sprite_{data['index']:03d}.png")
        sprite.save(output_path, 'PNG')
        
        width = sprite.size[0]
        height = sprite.size[1]
        print(f"   ✅ Sprite {data['index']:2d}: {width}x{height}px → {output_path}")
    
    print(f"\n🎉 Terminé ! {len(sprites_data)} sprite(s) sauvegardé(s) dans {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Découpe automatiquement des sprites d'une image et rend le fond transparent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s sprites.png                         # Sortie dans ./sprites/
  %(prog)s sorceress.png                       # Sortie dans ./sorceress/
  %(prog)s sprites.png -o mes_sprites/         # Sortie dans ./mes_sprites/
  %(prog)s sprites.png -t 230 -p 10            # Seuil 230, padding 10px
  %(prog)s sprites.png -m 30                   # Fusion plus agressive (30px)
  %(prog)s sprites.png --min-size 150          # Garder sprites >= 150px
  %(prog)s sprites.png -n auto                 # Normaliser à la taille du plus grand
  %(prog)s sprites.png -n 512x512              # Normaliser à 512x512px
  %(prog)s sprites.png --min-size 100 -n auto  # Filtrer + normaliser
  %(prog)s image.png --remove-background-only  # Supprime uniquement le fond blanc
  %(prog)s image.png --remove-background-only -o output.png  # Spécifier le fichier de sortie
        """
    )
    
    parser.add_argument(
        'input',
        help='Chemin de l\'image source contenant les sprites'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Dossier de sortie pour les sprites (défaut: nom du fichier sans extension)'
    )
    
    parser.add_argument(
        '-t', '--threshold',
        type=int,
        default=240,
        help='Seuil pour détecter le fond blanc, 0-255 (défaut: 240). '
             'Plus la valeur est basse, plus les pixels gris clairs seront considérés comme fond.'
    )
    
    parser.add_argument(
        '-p', '--padding',
        type=int,
        default=5,
        help='Pixels de padding autour de chaque sprite (défaut: 5)'
    )
    
    parser.add_argument(
        '-m', '--merge',
        type=int,
        default=20,
        help='Distance max (pixels) pour fusionner les sprites proches, '
             'ex: regrouper corps+yeux (défaut: 20, 0=désactivé)'
    )
    
    parser.add_argument(
        '--min-size',
        type=int,
        default=200,
        help='Taille minimale (pixels) d\'un côté pour garder un sprite (défaut: 200, 0=désactivé)'
    )
    
    parser.add_argument(
        '-n', '--normalize',
        type=str,
        default=None,
        help='Normaliser la taille des sprites: "auto" pour la taille du plus grand, '
             'ou "WIDTHxHEIGHT" (ex: "512x512") pour une taille fixe'
    )
    
    parser.add_argument(
        '--remove-background-only',
        action='store_true',
        help='Supprime uniquement le fond blanc sans découper ni redimensionner l\'image'
    )
    
    args = parser.parse_args()
    
    # Vérifier que le fichier existe
    if not os.path.exists(args.input):
        print(f"❌ Erreur: Le fichier '{args.input}' n'existe pas")
        sys.exit(1)
    
    # Si l'option --remove-background-only est activée
    if args.remove_background_only:
        # Déterminer le chemin de sortie
        if args.output is None:
            # Utiliser le nom du fichier avec "_no_bg" ajouté
            base_name = os.path.splitext(os.path.basename(args.input))[0]
            input_dir = os.path.dirname(args.input) or '.'
            output_path = os.path.join(input_dir, f"{base_name}_no_bg.png")
        else:
            # Si c'est un dossier, créer un nom de fichier
            if os.path.isdir(args.output) or args.output.endswith('/'):
                base_name = os.path.splitext(os.path.basename(args.input))[0]
                output_path = os.path.join(args.output, f"{base_name}_no_bg.png")
            else:
                # C'est un chemin de fichier
                output_path = args.output
        
        try:
            remove_background_only(args.input, output_path, args.threshold)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Mode normal : découper les sprites
        # Si aucun dossier de sortie n'est spécifié, utiliser le nom du fichier sans extension
        if args.output is None:
            base_name = os.path.splitext(os.path.basename(args.input))[0]
            args.output = base_name
        
        # Parser la normalisation
        normalize_size = None
        if args.normalize:
            if args.normalize.lower() == "auto":
                normalize_size = "auto"
            else:
                try:
                    parts = args.normalize.lower().split('x')
                    if len(parts) == 2:
                        normalize_size = (int(parts[0]), int(parts[1]))
                    else:
                        print(f"❌ Erreur: Format de normalisation invalide. Utilisez 'auto' ou 'WIDTHxHEIGHT'")
                        sys.exit(1)
                except ValueError:
                    print(f"❌ Erreur: Format de normalisation invalide. Utilisez 'auto' ou 'WIDTHxHEIGHT'")
                    sys.exit(1)
        
        # Découper les sprites
        try:
            cut_sprites(args.input, args.output, args.threshold, args.padding, args.merge,
                       args.min_size, normalize_size)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()

