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

def resize_image(img, target_height):
    """Redimensionne l'image en gardant le ratio"""
    width, height = img.size
    ratio = target_height / height
    new_width = int(width * ratio)
    
    return img.resize((new_width, target_height), Image.LANCZOS)

def create_sprite_sheet(frames, output_path, target_height, transparent, tolerance):
    """Crée la sprite sheet à partir des frames"""
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
        img = resize_image(img, target_height)
        processed_frames.append(img)
    
    print()  # Nouvelle ligne après la progression
    
    if transparent:
        avg_transparent = total_transparent_pixels // len(frames)
        print(f"✅ Transparence appliquée (~{avg_transparent} pixels/frame)")
    
    # Calcule les dimensions de la sprite sheet
    frame_width = processed_frames[0].width
    frame_height = processed_frames[0].height
    sprite_width = frame_width * len(processed_frames)
    sprite_height = frame_height
    
    print(f"📐 Dimensions: {len(processed_frames)} frames de {frame_width}x{frame_height}px")
    print(f"📐 Sprite sheet finale: {sprite_width}x{sprite_height}px")
    
    # Crée la sprite sheet
    sprite_sheet = Image.new('RGBA', (sprite_width, sprite_height), (0, 0, 0, 0))
    
    for i, frame in enumerate(processed_frames):
        x_offset = i * frame_width
        sprite_sheet.paste(frame, (x_offset, 0))
    
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
            args.tolerance
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
