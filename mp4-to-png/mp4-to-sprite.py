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

def detect_background_color(image_path, sample_size=5):
    """
    Détecte la couleur de fond en échantillonnant le coin supérieur gauche
    Gère aussi les fonds quadrillés (checkerboard) gris/blanc
    """
    img = Image.open(image_path).convert('RGB')
    
    # Échantillonne plusieurs pixels du coin supérieur gauche
    colors = []
    for x in range(sample_size):
        for y in range(sample_size):
            colors.append(img.getpixel((x, y)))
    
    # Détecte si c'est un pattern quadrillé (checkerboard)
    unique_colors = list(set(colors))
    
    # Si on a 2 couleurs proches de gris clair et gris foncé -> c'est un checkerboard
    if len(unique_colors) == 2:
        r1, g1, b1 = unique_colors[0]
        r2, g2, b2 = unique_colors[1]
        
        # Vérifie si ce sont des nuances de gris
        is_gray1 = abs(r1 - g1) < 10 and abs(g1 - b1) < 10
        is_gray2 = abs(r2 - g2) < 10 and abs(g2 - b2) < 10
        
        if is_gray1 and is_gray2:
            print(f"🔍 Fond quadrillé détecté: {unique_colors[0]} et {unique_colors[1]}")
            return unique_colors  # Retourne les 2 couleurs
    
    # Sinon, prend la couleur la plus fréquente
    most_common = max(set(colors), key=colors.count)
    print(f"🔍 Couleur de fond détectée: RGB{most_common}")
    return [most_common]

def remove_background(image_path, bg_colors, tolerance=30):
    """
    Supprime le fond de l'image en rendant transparent
    bg_colors: liste de couleurs à rendre transparentes
    """
    img = Image.open(image_path).convert('RGBA')
    data = img.getdata()
    
    new_data = []
    pixels_made_transparent = 0
    
    for pixel in data:
        r, g, b, a = pixel
        
        # Vérifie si le pixel correspond à une des couleurs de fond
        is_background = False
        for bg_color in bg_colors:
            br, bg_val, bb = bg_color
            
            # Calcule la distance de couleur
            color_distance = abs(r - br) + abs(g - bg_val) + abs(b - bb)
            
            if color_distance < tolerance:
                is_background = True
                pixels_made_transparent += 1
                break
        
        if is_background:
            new_data.append((r, g, b, 0))  # Transparent
        else:
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

def create_sprite_sheet(frames, output_path, target_height, transparent, tolerance, line=None, target_width=None):
    """Crée la sprite sheet à partir des frames, avec support multilignes"""
    print(f"\n🎨 Création de la sprite sheet...")
    
    if not frames:
        print("❌ Aucune frame à traiter")
        sys.exit(1)
    
    # Détecte la couleur de fond sur la première frame
    bg_colors = None
    if transparent:
        bg_colors = detect_background_color(frames[0])
    
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
    
    # Calcule les dimensions de la nouvelle ligne de sprite
    frame_width = processed_frames[0].width
    frame_height = processed_frames[0].height
    new_line_width = frame_width * len(processed_frames)
    new_line_height = frame_height
    
    if target_width:
        print(f"📐 Dimensions nouvelle ligne: {len(processed_frames)} frames de {frame_width}x{frame_height}px (largeur fixe)")
    else:
        print(f"📐 Dimensions nouvelle ligne: {len(processed_frames)} frames de {frame_width}x{frame_height}px")
    print(f"📐 Largeur ligne: {new_line_width}px")
    
    # Gestion du mode multilignes
    if line is not None:
        # Calcule la position Y de la ligne (0-indexed)
        y_position = line * target_height
        
        # Vérifie si le fichier existe
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"📂 Fichier existant détecté: {output_path}")
            existing_sheet = Image.open(output_path).convert('RGBA')
            existing_width, existing_height = existing_sheet.size
            
            # Calcule la largeur maximale
            final_width = max(existing_width, new_line_width)
            
            # Vérifie si on a besoin d'ajouter des lignes
            required_height = y_position + target_height
            if existing_height < required_height:
                print(f"📏 Extension du fichier: {existing_height}px → {required_height}px")
                # Crée une nouvelle image avec la bonne hauteur
                extended_sheet = Image.new('RGBA', (final_width, required_height), (0, 0, 0, 0))
                # Copie l'image existante
                extended_sheet.paste(existing_sheet, (0, 0))
                existing_sheet = extended_sheet
            else:
                # Utilise l'image existante, mais peut-être besoin d'étendre la largeur
                if existing_width < new_line_width:
                    print(f"📏 Extension de la largeur: {existing_width}px → {final_width}px")
                    extended_sheet = Image.new('RGBA', (final_width, existing_height), (0, 0, 0, 0))
                    extended_sheet.paste(existing_sheet, (0, 0))
                    existing_sheet = extended_sheet
                else:
                    final_width = existing_width
            
            sprite_sheet = existing_sheet
            print(f"📐 Dimensions finales: {final_width}x{sprite_sheet.height}px")
            print(f"📍 Insertion à la ligne {line} (y={y_position}px)")
        else:
            # Fichier n'existe pas ou est vide, on crée un nouveau
            print(f"📄 Création d'un nouveau fichier")
            required_height = y_position + target_height
            sprite_sheet = Image.new('RGBA', (new_line_width, required_height), (0, 0, 0, 0))
            final_width = new_line_width
            print(f"📐 Dimensions finales: {final_width}x{required_height}px")
            print(f"📍 Insertion à la ligne {line} (y={y_position}px)")
        
        # Colle la nouvelle ligne de sprite à la position Y
        new_line_sprite = Image.new('RGBA', (new_line_width, new_line_height), (0, 0, 0, 0))
        for i, frame in enumerate(processed_frames):
            x_offset = i * frame_width
            new_line_sprite.paste(frame, (x_offset, 0))
        
        sprite_sheet.paste(new_line_sprite, (0, y_position))
        
    else:
        # Mode normal (une seule ligne)
        sprite_width = new_line_width
        sprite_height = new_line_height
        
        print(f"📐 Sprite sheet finale: {sprite_width}x{sprite_height}px")
        
        # Crée la sprite sheet
        sprite_sheet = Image.new('RGBA', (sprite_width, sprite_height), (0, 0, 0, 0))
        
        for i, frame in enumerate(processed_frames):
            x_offset = i * frame_width
            sprite_sheet.paste(frame, (x_offset, 0))
        
        final_width = sprite_width
    
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
  %(prog)s video.mp4 --size=300 --transparent --start=0 --end=1 --output=avatar.png --line=3
  %(prog)s video.mp4 --size=128 --width=128 --transparent --fps=12
  %(prog)s video.mp4 --config=config.json --output=avatar.png --line=2

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
    parser.add_argument('--line', type=int, default=None,
                       help='Numéro de ligne (0-indexed) où placer l\'animation dans un spritesheet multilignes')
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
    if args.line is not None:
        print(f"📍 Ligne: {args.line} (y={args.line * args.size}px)")
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
            args.line,
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
