#!/usr/bin/env python3
"""
Outil de redimensionnement d'images
====================================
Redimensionne toutes les images d'un dossier pour qu'elles aient les mêmes dimensions.
Par défaut, les images sont étirées pour correspondre aux dimensions cibles.
Avec l'option --padding, les images conservent leur ratio d'aspect avec du padding transparent.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse

# Extensions d'images supportées
SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif'}


def get_image_files(directory):
    """
    Récupère tous les fichiers d'images dans un dossier.
    
    Args:
        directory: Chemin du dossier
        
    Returns:
        Liste des chemins des fichiers images triés
    """
    image_files = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"❌ Erreur: Le dossier '{directory}' n'existe pas")
        sys.exit(1)
    
    if not directory_path.is_dir():
        print(f"❌ Erreur: '{directory}' n'est pas un dossier")
        sys.exit(1)
    
    for file_path in directory_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            image_files.append(file_path)
    
    if not image_files:
        print(f"⚠️  Aucune image trouvée dans '{directory}'")
        print(f"   Extensions supportées: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)
    
    return sorted(image_files)


def get_target_size_for_image(image_size, target_width=None, target_height=None, reference_size=None):
    """
    Détermine la taille cible pour le redimensionnement d'une image.
    
    Args:
        image_size: Tuple (width, height) de l'image actuelle
        target_width: Largeur cible (optionnel)
        target_height: Hauteur cible (optionnel)
        reference_size: Tuple (width, height) de référence (première image si aucune dimension spécifiée)
        
    Returns:
        Tuple (width, height) pour la taille cible
    """
    original_width, original_height = image_size
    
    if target_width is not None and target_height is not None:
        # Les deux dimensions sont spécifiées
        return (target_width, target_height)
    elif target_width is not None:
        # Seule la largeur est spécifiée : on garde la hauteur originale
        return (target_width, original_height)
    elif target_height is not None:
        # Seule la hauteur est spécifiée : on garde la largeur originale
        return (original_width, target_height)
    else:
        # Aucune dimension spécifiée, on utilise la taille de référence (première image)
        if reference_size:
            return reference_size
        else:
            return (original_width, original_height)


def resize_image(image_path, target_size, output_path, use_padding=False):
    """
    Redimensionne une image aux dimensions cibles.
    
    Args:
        image_path: Chemin de l'image source
        target_size: Tuple (width, height) pour la taille cible
        output_path: Chemin de l'image de sortie
        use_padding: Si True, conserve le ratio d'aspect avec padding transparent (défaut: False)
        
    Returns:
        True si succès, False sinon
    """
    try:
        img = Image.open(image_path)
        target_width, target_height = target_size
        original_width, original_height = img.size
        
        if use_padding:
            # Mode padding : on garde l'image à sa taille originale et on ajoute du padding transparent
            # Vérifie que l'image originale rentre dans les dimensions cibles
            if original_width > target_width or original_height > target_height:
                print(f"   ⚠️  Image {image_path.name} ({original_width}x{original_height}) plus grande que la cible ({target_width}x{target_height}), elle sera rognée")
            
            # Convertit l'image en RGBA si nécessaire pour gérer la transparence
            if img.mode == 'P':
                # Mode palette : convertit en RGBA pour préserver la transparence
                img = img.convert('RGBA')
            elif img.mode not in ('RGBA', 'LA'):
                # Convertit en RGBA pour avoir un fond transparent
                img = img.convert('RGBA')
            elif img.mode == 'LA':
                # Mode LA (Luminance + Alpha) : convertit en RGBA
                img = img.convert('RGBA')
            
            # Crée un canvas transparent de la taille cible exacte
            canvas = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
            
            # Calcule les offsets pour centrer l'image (padding équilibré)
            x_offset = (target_width - original_width) // 2
            y_offset = (target_height - original_height) // 2
            
            # Colle l'image originale (sans redimensionnement) au centre du canvas
            if img.mode == 'RGBA':
                canvas.paste(img, (x_offset, y_offset), img)
            else:
                canvas.paste(img, (x_offset, y_offset))
            
            resized_img = canvas
            
            # Vérification : le canvas final doit avoir exactement la taille cible
            assert resized_img.size == (target_width, target_height), \
                f"Taille du canvas incorrecte: {resized_img.size} au lieu de {(target_width, target_height)}"
        else:
            # Redimensionne en étirant (pas de padding)
            resized_img = img.resize(target_size, Image.LANCZOS)
        
        # Sauvegarde en préservant le format original si possible
        # Convertit en RGB pour les formats qui ne supportent pas RGBA
        if resized_img.mode == 'RGBA' and image_path.suffix.lower() in {'.jpg', '.jpeg'}:
            # JPG ne supporte pas la transparence : on utilise un fond blanc
            # IMPORTANT: préserver la taille exacte lors de la conversion
            background = Image.new('RGB', resized_img.size, (255, 255, 255))
            background.paste(resized_img, mask=resized_img.split()[3] if resized_img.mode == 'RGBA' else None)
            resized_img = background
        
        # Vérification finale : l'image doit avoir la taille cible
        if use_padding:
            assert resized_img.size == (target_width, target_height), \
                f"Taille finale incorrecte: {resized_img.size} au lieu de {(target_width, target_height)}"
        
        resized_img.save(output_path, quality=95, optimize=True)
        return True
    except Exception as e:
        print(f"   ❌ Erreur lors du traitement de {image_path.name}: {e}")
        return False


def ask_confirmation(directory, num_images, target_info):
    """
    Demande confirmation à l'utilisateur avant de redimensionner.
    
    Args:
        directory: Chemin du dossier
        num_images: Nombre d'images à traiter
        target_info: Information sur la taille cible
        
    Returns:
        True si l'utilisateur confirme, False sinon
    """
    print("=" * 60)
    print("🖼️  Redimensionnement d'images")
    print("=" * 60)
    print(f"📁 Dossier source: {directory}")
    print(f"📊 Nombre d'images: {num_images}")
    print(f"📐 {target_info}")
    print("=" * 60)
    print()
    
    response = input("⚠️  Continuer le redimensionnement ? (o/N): ").strip().lower()
    return response in ['o', 'oui', 'y', 'yes']


def resize_images(directory, output_subdir='resized', target_width=None, target_height=None, confirm=True, use_padding=False):
    """
    Redimensionne toutes les images d'un dossier.
    
    Args:
        directory: Chemin du dossier contenant les images
        output_subdir: Nom du sous-dossier de sortie (défaut: 'resized')
        target_width: Largeur cible (optionnel)
        target_height: Hauteur cible (optionnel)
        confirm: Demander confirmation avant de traiter (défaut: True)
        use_padding: Utiliser le padding transparent au lieu d'étirer (défaut: False)
    """
    # Récupère les fichiers images
    image_files = get_image_files(directory)
    
    # Obtient la taille de référence (première image) si aucune dimension n'est spécifiée
    reference_size = None
    mode_text = "avec padding transparent" if use_padding else "étirement"
    if target_width is None and target_height is None:
        first_image = Image.open(image_files[0])
        reference_size = first_image.size
        first_image.close()
        target_info = f"Taille cible: {reference_size[0]}x{reference_size[1]}px (basée sur la première image, mode: {mode_text})"
    elif target_width is not None and target_height is not None:
        target_info = f"Taille cible: {target_width}x{target_height}px (dimensions spécifiées, mode: {mode_text})"
    elif target_width is not None:
        target_info = f"Largeur cible: {target_width}px (hauteur originale conservée pour chaque image, mode: {mode_text})"
    else:
        target_info = f"Hauteur cible: {target_height}px (largeur originale conservée pour chaque image, mode: {mode_text})"
    
    # Obtient la taille de référence (première image) si aucune dimension n'est spécifiée
    reference_size = None
    if target_width is None and target_height is None:
        first_image = Image.open(image_files[0])
        reference_size = first_image.size
        first_image.close()
    
    # Demande confirmation
    if confirm:
        if not ask_confirmation(directory, len(image_files), target_info):
            print("❌ Opération annulée par l'utilisateur")
            return
        print()
    
    # Affiche les informations de traitement
    print("=" * 60)
    print("🖼️  Traitement en cours...")
    print("=" * 60)
    print(f"📁 Dossier source: {directory}")
    print(f"📊 {len(image_files)} image(s) à traiter")
    print(f"📐 {target_info}")
    
    # Crée le dossier de sortie
    directory_path = Path(directory)
    output_dir = directory_path / output_subdir
    output_dir.mkdir(exist_ok=True)
    print(f"📂 Dossier de sortie: {output_dir}")
    print()
    
    # Traite chaque image
    success_count = 0
    failed_count = 0
    
    for i, image_path in enumerate(image_files, 1):
        print(f"   [{i}/{len(image_files)}] {image_path.name}...", end=' ')
        
        # Obtient les dimensions originales
        original_img = Image.open(image_path)
        original_size = original_img.size
        original_img.close()
        
        # Calcule la taille cible pour cette image spécifique
        target_size = get_target_size_for_image(
            original_size,
            target_width,
            target_height,
            reference_size
        )
        
        # Chemin de sortie
        output_path = output_dir / image_path.name
        
        # Redimensionne
        if resize_image(image_path, target_size, output_path, use_padding=use_padding):
            print(f"✅ {original_size[0]}x{original_size[1]} → {target_size[0]}x{target_size[1]}")
            success_count += 1
        else:
            failed_count += 1
    
    print()
    print("=" * 60)
    print("✅ TERMINÉ !")
    print("=" * 60)
    print(f"📊 Résumé:")
    print(f"   • Images traitées: {success_count}")
    if failed_count > 0:
        print(f"   • Échecs: {failed_count}")
    print(f"   • Dossier de sortie: {output_dir}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Redimensionne toutes les images d\'un dossier pour qu\'elles aient les mêmes dimensions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s                                    # Redimensionne le dossier actuel selon la première image
  %(prog)s ./images/                          # Redimensionne selon la première image
  %(prog)s ./images/ --width 800              # Largeur 800px, hauteur originale conservée
  %(prog)s ./images/ --height 600             # Hauteur 600px, largeur originale conservée
  %(prog)s ./images/ --width 800 --height 600 # Dimensions exactes 800x600px
  %(prog)s ./images/ --padding                # Mode padding transparent (ratio conservé)
  %(prog)s ./images/ -w 800 -h 600 --padding  # 800x600px avec padding transparent
  %(prog)s ./images/ -o resized_images        # Dossier de sortie personnalisé
  %(prog)s ./images/ --no-confirm             # Pas de confirmation
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Dossier contenant les images à redimensionner (défaut: dossier actuel)'
    )
    
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Ne pas demander de confirmation avant de traiter'
    )
    
    parser.add_argument(
        '--width', '-w',
        type=int,
        default=None,
        help='Largeur cible en pixels (optionnel)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=None,
        help='Hauteur cible en pixels (optionnel)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='resized',
        help='Nom du sous-dossier de sortie (défaut: resized)'
    )
    
    parser.add_argument(
        '--padding',
        action='store_true',
        help='Conserve le ratio d\'aspect avec padding transparent au lieu d\'étirer les images'
    )
    
    args = parser.parse_args()
    
    # Valide les arguments
    if args.width is not None and args.width <= 0:
        print("❌ Erreur: --width doit être un nombre positif")
        sys.exit(1)
    
    if args.height is not None and args.height <= 0:
        print("❌ Erreur: --height doit être un nombre positif")
        sys.exit(1)
    
    # Convertit le chemin en chemin absolu
    directory = os.path.abspath(args.directory)
    
    # Lance le redimensionnement
    try:
        resize_images(
            directory,
            args.output,
            args.width,
            args.height,
            confirm=not args.no_confirm,
            use_padding=args.padding
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
