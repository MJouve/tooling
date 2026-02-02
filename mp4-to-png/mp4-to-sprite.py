#!/usr/bin/env python3
"""
MP4 to Sprite Sheet Converter
Convertit une vidéo MP4 en sprite sheet PNG avec détection automatique de transparence
"""

import argparse
import subprocess
import os
import sys
from pathlib import Path
from PIL import Image
import tempfile
import shutil
import json
from collections import deque

def check_dependencies():
    """Vérifie que ffmpeg est installé"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Erreur: ffmpeg n'est pas installé")
        print("   Installez-le avec: sudo apt install ffmpeg")
        sys.exit(1)

def extract_frames(video_path, start_time, end_time, fps, temp_dir):
    """Extrait les frames de la vidéo avec ffmpeg"""
    duration = end_time - start_time
    
    print(f"📹 Extraction des frames de {start_time}s à {end_time}s ({duration}s)...")
    
    # Commande ffmpeg pour extraire les frames
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-vf', f'fps={fps}',
        '-q:v', '1',  # Qualité maximale
        f'{temp_dir}/frame_%04d.png'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'extraction: {e.stderr.decode()}")
        sys.exit(1)
    
    # Compte les frames extraites
    frames = sorted(Path(temp_dir).glob('frame_*.png'))
    print(f"✅ {len(frames)} frames extraites")
    
    return frames

def detect_background_color(image_path, sample_size=5, detect_checkerboard=True):
    """
    Détecte la couleur de fond en échantillonnant les bords de l'image
    Gère aussi les fonds quadrillés (checkerboard) gris/blanc si activé
    """
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    
    # Échantillonne les bords de l'image (pas seulement le coin)
    colors = []
    
    # Bord supérieur
    for x in range(min(sample_size * 10, width)):
        colors.append(img.getpixel((x, 0)))
    
    # Bord inférieur
    for x in range(min(sample_size * 10, width)):
        colors.append(img.getpixel((x, height - 1)))
    
    # Bord gauche
    for y in range(min(sample_size * 10, height)):
        colors.append(img.getpixel((0, y)))
    
    # Bord droit
    for y in range(min(sample_size * 10, height)):
        colors.append(img.getpixel((width - 1, y)))
    
    # Détecte si c'est un pattern quadrillé (checkerboard)
    unique_colors = list(set(colors))
    
    # Si la détection de checkerboard est activée et qu'on a 2 couleurs, vérifie si c'est vraiment un checkerboard
    if detect_checkerboard and len(unique_colors) == 2:
        r1, g1, b1 = unique_colors[0]
        r2, g2, b2 = unique_colors[1]
        
        # Vérifie si ce sont des nuances de gris (checkerboard typique)
        is_gray1 = abs(r1 - g1) < 10 and abs(g1 - b1) < 10
        is_gray2 = abs(r2 - g2) < 10 and abs(g2 - b2) < 10
        
        # Vérifie aussi que les couleurs sont très différentes (typique d'un checkerboard)
        color_diff = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
        
        # Vérifie qu'il y a vraiment un pattern alterné (checkerboard)
        # Échantillonne quelques pixels pour vérifier l'alternance
        has_checkerboard_pattern = False
        if is_gray1 and is_gray2 and color_diff > 100:  # Couleurs très différentes
            # Vérifie l'alternance sur le bord supérieur
            pattern_found = 0
            sample_count = min(20, width)
            for x in range(sample_count):
                pixel = img.getpixel((x, 0))
                expected_color = unique_colors[0] if (x // 8) % 2 == 0 else unique_colors[1]  # Pattern 8x8 typique
                # Vérifie si le pixel correspond à la couleur attendue
                dist1 = abs(pixel[0] - expected_color[0]) + abs(pixel[1] - expected_color[1]) + abs(pixel[2] - expected_color[2])
                dist2 = abs(pixel[0] - unique_colors[0][0]) + abs(pixel[1] - unique_colors[0][1]) + abs(pixel[2] - unique_colors[0][2])
                dist3 = abs(pixel[0] - unique_colors[1][0]) + abs(pixel[1] - unique_colors[1][1]) + abs(pixel[2] - unique_colors[1][2])
                if min(dist2, dist3) < 30:  # Le pixel correspond à une des 2 couleurs
                    pattern_found += 1
            
            # Si au moins 70% des pixels correspondent au pattern, c'est probablement un checkerboard
            if pattern_found / sample_count > 0.7:
                has_checkerboard_pattern = True
        
        if has_checkerboard_pattern:
            print(f"🔍 Fond quadrillé détecté: {unique_colors[0]} et {unique_colors[1]}")
            return unique_colors  # Retourne les 2 couleurs
    
    # Sinon, prend la couleur la plus fréquente
    most_common = max(set(colors), key=colors.count)
    
    # Si la couleur dominante est très claire (blanc ou presque blanc), 
    # on ne cherche pas de checkerboard pour éviter les faux positifs
    r, g, b = most_common
    is_very_light = (r + g + b) > 700  # Très clair (sur 765 max)
    
    # Si c'est très clair, on désactive la détection de checkerboard même si activée
    if is_very_light and detect_checkerboard and len(unique_colors) == 2:
        print(f"🔍 Couleur de fond très claire détectée: RGB{most_common}")
        print(f"   (Détection de checkerboard ignorée pour éviter les faux positifs)")
        return [most_common]
    
    print(f"🔍 Couleur de fond détectée: RGB{most_common}")
    return [most_common]

def is_color_match(pixel, bg_color, tolerance):
    """Vérifie si un pixel correspond à une couleur de fond avec tolérance"""
    r, g, b = pixel[:3]  # Prend seulement RGB
    br, bg_val, bb = bg_color
    color_distance = abs(r - br) + abs(g - bg_val) + abs(b - bb)
    return color_distance < tolerance

def remove_background(image_path, bg_colors, tolerance=30):
    """
    Supprime le fond de l'image en rendant transparent uniquement les zones
    connectées aux bords (pas les zones intérieures du sprite)
    bg_colors: liste de couleurs à rendre transparentes
    """
    img = Image.open(image_path).convert('RGBA')
    width, height = img.size
    
    # Crée un masque pour marquer les pixels de fond connectés aux bords
    # 0 = à rendre transparent, 1 = à garder
    mask = [[1] * width for _ in range(height)]
    
    # Marque les pixels de fond sur les bords et utilise flood fill avec queue
    queue = deque()
    
    # Vérifie tous les bords et ajoute les pixels de fond à la queue
    for y in range(height):
        for x in range(width):
            # Si c'est sur un bord
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                pixel = img.getpixel((x, y))
                # Vérifie si c'est une couleur de fond
                for bg_color in bg_colors:
                    if is_color_match(pixel, bg_color, tolerance):
                        mask[y][x] = 0  # Marque comme fond
                        queue.append((x, y))
                        break
    
    # Flood fill depuis les bords pour trouver tous les pixels de fond connectés
    # Utilise une queue pour une efficacité optimale
    while queue:
        x, y = queue.popleft()
        
        # Vérifie les 4 voisins (filtre les None)
        neighbors = []
        if x > 0:
            neighbors.append((x-1, y))
        if x < width-1:
            neighbors.append((x+1, y))
        if y > 0:
            neighbors.append((x, y-1))
        if y < height-1:
            neighbors.append((x, y+1))
        
        for nx, ny in neighbors:
            if mask[ny][nx] == 1:
                # Vérifie si ce voisin est aussi une couleur de fond
                pixel = img.getpixel((nx, ny))
                for bg_color in bg_colors:
                    if is_color_match(pixel, bg_color, tolerance):
                        mask[ny][nx] = 0  # Marque comme fond
                        queue.append((nx, ny))
                        break
    
    # Applique le masque : rend transparent uniquement les pixels marqués comme fond
    new_data = []
    pixels_made_transparent = 0
    
    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            if mask[y][x] == 0:
                # Rendre transparent
                new_data.append((pixel[0], pixel[1], pixel[2], 0))
                pixels_made_transparent += 1
            else:
                # Garder le pixel tel quel
                new_data.append(pixel)
    
    img.putdata(new_data)
    
    return img, pixels_made_transparent

def resize_image(img, target_height, target_width=None):
    """
    Redimensionne l'image en gardant le ratio
    Si target_width est spécifié, force cette largeur (avec crop ou padding)
    """
    width, height = img.size
    
    if target_width is None:
        # Mode normal : garde le ratio
        ratio = target_height / height
        new_width = int(width * ratio)
        return img.resize((new_width, target_height), Image.LANCZOS)
    else:
        # Mode largeur fixe : redimensionne d'abord pour couvrir, puis crop/pad
        # Calcule le ratio pour que l'image couvre au moins target_width x target_height
        ratio_h = target_height / height
        ratio_w = target_width / width
        ratio = max(ratio_h, ratio_w)  # Prend le plus grand pour couvrir
        
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Redimensionne (assure-toi que c'est en RGBA)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Centre et crop/pad pour obtenir exactement target_width x target_height
        final_img = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
        
        # Calcule la position pour centrer
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Si l'image est plus grande, on crop depuis le centre
        if new_width > target_width:
            crop_x = (new_width - target_width) // 2
            resized = resized.crop((crop_x, 0, crop_x + target_width, new_height))
            x_offset = 0
        
        if new_height > target_height:
            crop_y = (new_height - target_height) // 2
            resized = resized.crop((0, crop_y, resized.width, crop_y + target_height))
            y_offset = 0
        
        # Colle l'image centrée (avec masque alpha si RGBA)
        final_img.paste(resized, (x_offset, y_offset), resized)
        
        return final_img

def load_config(config_path):
    """Charge un fichier de configuration JSON"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"📋 Configuration chargée depuis: {config_path}")
        return config
    except FileNotFoundError:
        print(f"⚠️  Fichier de config non trouvé: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON dans {config_path}: {e}")
        sys.exit(1)

def create_sprite_sheet(frames, output_path, target_height, transparent, tolerance, target_width=None):
    """
    Crée la sprite sheet à partir des frames
    Divise automatiquement en plusieurs lignes si la largeur dépasse 4096px (limite React Native)
    """
    MAX_WIDTH = 4096  # Limite React Native
    
    print(f"\n🎨 Création de la sprite sheet...")
    
    if not frames:
        print("❌ Aucune frame à traiter")
        sys.exit(1)
    
    # Détecte la couleur de fond sur la première frame
    bg_colors = None
    if transparent:
        # Désactive la détection de checkerboard par défaut pour éviter les faux positifs
        # (peut être réactivée si nécessaire)
        bg_colors = detect_background_color(frames[0], detect_checkerboard=False)
    
    # Traite chaque frame
    processed_frames = []
    total_transparent_pixels = 0
    
    for i, frame_path in enumerate(frames, 1):
        print(f"   Traitement frame {i}/{len(frames)}...", end='\r')
        
        # Ouvre et traite la frame
        if transparent and bg_colors:
            img, transparent_pixels = remove_background(frame_path, bg_colors, tolerance)
            total_transparent_pixels += transparent_pixels
        else:
            img = Image.open(frame_path).convert('RGBA')
        
        # Redimensionne
        img = resize_image(img, target_height, target_width)
        processed_frames.append(img)
    
    print()  # Nouvelle ligne après la progression
    
    if transparent:
        avg_transparent = total_transparent_pixels // len(frames)
        print(f"✅ Transparence appliquée (~{avg_transparent} pixels/frame)")
    
    # Calcule les dimensions d'une frame
    frame_width = processed_frames[0].width
    frame_height = processed_frames[0].height
    
    # Calcule la largeur totale nécessaire
    total_width = frame_width * len(processed_frames)
    
    # Si la largeur totale est <= 4096px, une seule ligne suffit
    if total_width <= MAX_WIDTH:
        # Une seule ligne avec la largeur exacte
        num_lines = 1
        actual_width = total_width
        frames_per_line = len(processed_frames)
        
        print(f"📐 Dimensions frame: {frame_width}x{frame_height}px")
        print(f"📐 Total frames: {len(processed_frames)}")
        print(f"📐 Largeur totale: {total_width}px (≤ {MAX_WIDTH}px, une seule ligne)")
        
        # Crée la sprite sheet
        sprite_sheet = Image.new('RGBA', (actual_width, frame_height), (0, 0, 0, 0))
        
        # Place toutes les frames sur une ligne
        for i, frame in enumerate(processed_frames):
            x_offset = i * frame_width
            sprite_sheet.paste(frame, (x_offset, 0))
        
        print(f"📐 Sprite sheet finale: {actual_width}x{frame_height}px (1 ligne)")
    else:
        # Plusieurs lignes nécessaires
        # Calcule combien de frames peuvent tenir sur une ligne (max 4096px)
        frames_per_line = MAX_WIDTH // frame_width
        if frames_per_line == 0:
            frames_per_line = 1  # Au moins une frame par ligne
        
        # Calcule le nombre de lignes nécessaires
        num_lines = (len(processed_frames) + frames_per_line - 1) // frames_per_line  # Arrondi supérieur
        
        # Toutes les lignes ont la même largeur = largeur d'une ligne pleine
        actual_width = frames_per_line * frame_width
        
        print(f"📐 Dimensions frame: {frame_width}x{frame_height}px")
        print(f"📐 Total frames: {len(processed_frames)}")
        print(f"📐 Largeur totale: {total_width}px (> {MAX_WIDTH}px, division en {num_lines} ligne(s))")
        print(f"📐 Frames par ligne: {frames_per_line} (limite: {MAX_WIDTH}px)")
        print(f"📐 Largeur de chaque ligne: {actual_width}px (identique pour toutes)")
        
        # Crée la sprite sheet
        sprite_height = frame_height * num_lines
        sprite_sheet = Image.new('RGBA', (actual_width, sprite_height), (0, 0, 0, 0))
        
        # Place les frames ligne par ligne
        frame_index = 0
        for line in range(num_lines):
            y_offset = line * frame_height
            frames_in_this_line = min(frames_per_line, len(processed_frames) - frame_index)
            
            for i in range(frames_in_this_line):
                x_offset = i * frame_width
                sprite_sheet.paste(processed_frames[frame_index], (x_offset, y_offset))
                frame_index += 1
            
            # Les lignes incomplètes auront automatiquement du transparent à droite
            # (créé par Image.new avec fond transparent)
        
        print(f"📐 Sprite sheet finale: {actual_width}x{sprite_height}px ({num_lines} ligne(s))")
    
    # Sauvegarde
    sprite_sheet.save(output_path, 'PNG', optimize=True)
    file_size = os.path.getsize(output_path)
    print(f"💾 Sprite sheet sauvegardée: {output_path} ({file_size // 1024} KB)")
    
    return len(processed_frames), frame_width, frame_height

def main():
    parser = argparse.ArgumentParser(
        description='Convertit une vidéo MP4 en sprite sheet PNG avec transparence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s video.mp4 --size=300
  %(prog)s video.mp4 --size=256 --transparent --start=0 --end=2
  %(prog)s video.mp4 --size=128 --fps=15 --output=avatar-celebrate.png
  %(prog)s video.mp4 --transparent --tolerance=50 --start=1.5 --end=3
  %(prog)s video.mp4 --size=128 --width=128 --transparent --fps=12
  %(prog)s video.mp4 --config=config.json --output=avatar.png

Fichier de configuration (config.json):
  {
    "size": 128,
    "width": 128,
    "transparent": true,
    "tolerance": 30,
    "fps": 12,
    "start": 0,
    "end": 1.5
  }
        """
    )
    
    parser.add_argument('input', help='Fichier MP4 en entrée')
    parser.add_argument('--size', type=int, default=128,
                       help='Hauteur cible en pixels (défaut: 128)')
    parser.add_argument('--transparent', action='store_true',
                       help='Activer la détection et suppression du fond')
    parser.add_argument('--tolerance', type=int, default=30,
                       help='Tolérance de détection de couleur (0-255, défaut: 30)')
    parser.add_argument('--start', type=float, default=0,
                       help='Temps de début en secondes (défaut: 0)')
    parser.add_argument('--end', type=float, default=None,
                       help='Temps de fin en secondes (défaut: durée totale)')
    parser.add_argument('--fps', type=int, default=10,
                       help='Images par seconde à extraire (défaut: 10)')
    parser.add_argument('--output', '-o', 
                       help='Nom du fichier de sortie (défaut: input-sprite.png)')
    parser.add_argument('--width', type=int, default=None,
                       help='Largeur fixe en pixels pour toutes les frames (force crop/pad si nécessaire)')
    parser.add_argument('--config', '-c', type=str, default=None,
                       help='Fichier de configuration JSON avec les options par défaut')
    
    # Parse une première fois pour obtenir --config
    temp_args, _ = parser.parse_known_args()
    
    # Charge la configuration si fournie
    if temp_args.config:
        config = load_config(temp_args.config)
        # Remplace les valeurs par défaut du parser par celles de la config
        # (les arguments en ligne de commande auront toujours priorité)
        if 'size' in config:
            parser.set_defaults(size=config['size'])
        if 'width' in config:
            parser.set_defaults(width=config['width'])
        if 'transparent' in config:
            parser.set_defaults(transparent=config['transparent'])
        if 'tolerance' in config:
            parser.set_defaults(tolerance=config['tolerance'])
        if 'start' in config:
            parser.set_defaults(start=config['start'])
        if 'end' in config:
            parser.set_defaults(end=config['end'])
        if 'fps' in config:
            parser.set_defaults(fps=config['fps'])
        if 'output' in config:
            parser.set_defaults(output=config['output'])
        if 'line' in config:
            parser.set_defaults(line=config['line'])
    
    # Parse définitivement (les arguments CLI ont priorité sur la config)
    args = parser.parse_args()
    
    # Vérifie que le fichier existe
    if not os.path.exists(args.input):
        print(f"❌ Erreur: Le fichier '{args.input}' n'existe pas")
        sys.exit(1)
    
    # Vérifie les dépendances
    check_dependencies()
    
    # Obtient la durée de la vidéo si --end n'est pas spécifié
    if args.end is None:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            args.input
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            args.end = float(result.stdout.strip())
        except:
            print("⚠️  Impossible de détecter la durée, utilisation de 10s")
            args.end = 10
    
    # Valide les paramètres
    if args.start >= args.end:
        print("❌ Erreur: --start doit être inférieur à --end")
        sys.exit(1)
    
    # Génère le nom de sortie
    if args.output is None:
        input_name = Path(args.input).stem
        args.output = f"{input_name}-sprite.png"
    
    print("=" * 60)
    print("🎬 MP4 to Sprite Sheet Converter")
    print("=" * 60)
    print(f"📁 Entrée: {args.input}")
    print(f"📁 Sortie: {args.output}")
    print(f"⏱️  Segment: {args.start}s → {args.end}s")
    print(f"📏 Hauteur: {args.size}px")
    if args.width:
        print(f"📏 Largeur fixe: {args.width}px")
    print(f"🎞️  FPS: {args.fps}")
    print(f"👻 Transparence: {'✅ Activée' if args.transparent else '❌ Désactivée'}")
    if args.transparent:
        print(f"🎯 Tolérance: {args.tolerance}")
    print("=" * 60)
    print()
    
    # Crée un dossier temporaire
    temp_dir = tempfile.mkdtemp(prefix='mp4-sprite-')
    
    try:
        # Extraction des frames
        frames = extract_frames(args.input, args.start, args.end, args.fps, temp_dir)
        
        # Création de la sprite sheet
        num_frames, frame_w, frame_h = create_sprite_sheet(
            frames, 
            args.output, 
            args.size, 
            args.transparent,
            args.tolerance,
            args.width
        )
        
        print()
        print("=" * 60)
        print("✅ TERMINÉ !")
        print("=" * 60)
        print(f"📊 Résumé:")
        print(f"   • Frames: {num_frames}")
        print(f"   • Taille frame: {frame_w}x{frame_h}px")
        print(f"   • Fichier: {args.output}")
        print()
        print("💡 Utilisation dans React:")
        print(f"   const config = {{")
        print(f"     src: '/assets/{Path(args.output).name}',")
        print(f"     frames: {num_frames},")
        print(f"     frameWidth: {frame_w},")
        print(f"     frameHeight: {frame_h}")
        print(f"   }};")
        
    finally:
        # Nettoie le dossier temporaire
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()
