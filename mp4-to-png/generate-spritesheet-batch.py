#!/usr/bin/env python3
"""
Script de génération batch pour créer un spritesheet multilignes
Vérifie que tous les fichiers requis sont présents avant de générer
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

# ============================================================================
# CONFIGURATION : Liste des fichiers requis (émotions/actions)
# ============================================================================
# Modifiez cette liste selon vos besoins
# Format: (nom_fichier_sans_extension, numéro_ligne, description)
REQUIRED_FILES = [
    ("joyeux", 0, "Animation joyeuse"),
    ("triste", 1, "Animation triste"),
    ("neutre", 2, "Animation neutre"),
    ("fatigue", 3, "Animation fatigue"),
    # Ajoutez d'autres animations ici :
    # ("action1", 4, "Description action1"),
    # ("action2", 5, "Description action2"),
]

# Configuration par défaut pour la génération
DEFAULT_CONFIG = {
    "size": 128,
    "width": 128,
    "transparent": True,
    "tolerance": 30,
    "fps": 12,
    "start": 0,
    "end": None,  # None = durée totale de la vidéo
}

# ============================================================================
# FONCTIONS
# ============================================================================

def check_required_files(source_dir):
    """
    Vérifie que tous les fichiers requis sont présents dans le dossier source
    Retourne: (fichiers_trouvés, fichiers_manquants)
    """
    source_path = Path(source_dir)
    found = []
    missing = []
    
    for file_name, line_num, description in REQUIRED_FILES:
        # Cherche le fichier avec différentes extensions possibles
        possible_extensions = ['.mp4', '.MP4', '.mov', '.MOV']
        file_found = None
        
        for ext in possible_extensions:
            file_path = source_path / f"{file_name}{ext}"
            if file_path.exists():
                file_found = file_path
                break
        
        if file_found:
            found.append((file_name, line_num, description, file_found))
        else:
            missing.append((file_name, line_num, description))
    
    return found, missing

def display_status(found, missing):
    """Affiche le statut des fichiers requis"""
    print("=" * 70)
    print("📋 VÉRIFICATION DES FICHIERS REQUIS")
    print("=" * 70)
    print()
    
    if found:
        print(f"✅ Fichiers trouvés ({len(found)}/{len(REQUIRED_FILES)}):")
        for file_name, line_num, description, file_path in found:
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   ✓ {file_name:15} → Ligne {line_num:2} | {description:30} | {file_size:.2f} MB")
        print()
    
    if missing:
        print(f"❌ Fichiers manquants ({len(missing)}/{len(REQUIRED_FILES)}):")
        print()
        for file_name, line_num, description in missing:
            print(f"   ✗ {file_name:15} → Ligne {line_num:2} | {description}")
            # Affiche les extensions possibles
            print(f"      Cherché: {file_name}.mp4, {file_name}.MP4, {file_name}.mov, {file_name}.MOV")
        print()
        print("⚠️" * 35)
        print("⚠️  ALERTE : CERTAINS FICHIERS SONT MANQUANTS !")
        print("⚠️" * 35)
        print()
        print("   Le spritesheet sera généré avec les fichiers disponibles uniquement.")
        print("   Les lignes manquantes seront laissées vides dans le spritesheet.")
        print()
    
    return len(missing) == 0

def generate_spritesheet(source_dir, output_file, config_file=None):
    """
    Génère le spritesheet multilignes en appelant mp4-to-sprite.py pour chaque fichier
    """
    found, missing = check_required_files(source_dir)
    
    if not found:
        print("❌ Erreur: Aucun fichier requis trouvé dans le dossier source")
        sys.exit(1)
    
    # Affiche le statut
    all_present = display_status(found, missing)
    
    if not all_present:
        response = input("Voulez-vous continuer malgré les fichiers manquants ? (o/N): ")
        if response.lower() not in ['o', 'oui', 'y', 'yes']:
            print("❌ Génération annulée")
            sys.exit(1)
    
    print("=" * 70)
    print("🎬 GÉNÉRATION DU SPRITESHEET MULTILIGNES")
    print("=" * 70)
    print(f"📁 Dossier source: {source_dir}")
    print(f"📁 Fichier de sortie: {output_file}")
    print()
    
    # Vérifie que mp4-to-sprite.py existe
    script_path = Path(__file__).parent / "mp4-to-sprite.py"
    if not script_path.exists():
        print(f"❌ Erreur: mp4-to-sprite.py non trouvé dans {script_path.parent}")
        sys.exit(1)
    
    # Construit la commande de base
    base_cmd = [
        sys.executable,
        str(script_path),
    ]
    
    # Ajoute les options de config si un fichier est fourni
    if config_file:
        base_cmd.extend(["--config", config_file])
    
    # Génère chaque ligne du spritesheet
    success_count = 0
    fail_count = 0
    
    print(f"🔄 Génération de {len(found)} ligne(s)...")
    print()
    
    for file_name, line_num, description, file_path in found:
        print(f"📹 [{line_num}/{len(found)}] Ligne {line_num}: {file_name} ({description})")
        
        # Construit la commande pour ce fichier
        cmd = base_cmd.copy()
        cmd.extend([
            str(file_path),
            "--size", str(DEFAULT_CONFIG["size"]),
            "--fps", str(DEFAULT_CONFIG["fps"]),
            "--start", str(DEFAULT_CONFIG["start"]),
            "--output", output_file,
            "--line", str(line_num),
        ])
        
        # Ajoute les options conditionnelles
        if DEFAULT_CONFIG["width"]:
            cmd.extend(["--width", str(DEFAULT_CONFIG["width"])])
        
        if DEFAULT_CONFIG["transparent"]:
            cmd.append("--transparent")
            cmd.extend(["--tolerance", str(DEFAULT_CONFIG["tolerance"])])
        
        if DEFAULT_CONFIG["end"]:
            cmd.extend(["--end", str(DEFAULT_CONFIG["end"])])
        
        # Exécute la commande
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"      ✅ Ligne {line_num} générée avec succès")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Erreur lors de la génération de la ligne {line_num}")
            # Affiche seulement les dernières lignes de l'erreur pour ne pas surcharger
            error_lines = e.stderr.strip().split('\n')
            if len(error_lines) > 5:
                print(f"      ... ({len(error_lines) - 5} lignes supprimées)")
                for line in error_lines[-5:]:
                    print(f"      {line}")
            else:
                print(f"      {e.stderr}")
            fail_count += 1
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
            fail_count += 1
    
    # Résumé
    print()
    print("=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ Lignes générées avec succès: {success_count}/{len(found)}")
    if fail_count > 0:
        print(f"❌ Lignes en erreur: {fail_count}")
    
    if success_count > 0 and os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"💾 Fichier généré: {output_file} ({file_size:.2f} MB)")
        print()
        print("💡 Utilisation dans React:")
        print(f"   const spriteSheet = {{")
        print(f"     src: '/assets/{Path(output_file).name}',")
        print(f"     frameHeight: {DEFAULT_CONFIG['size']},")
        if DEFAULT_CONFIG['width']:
            print(f"     frameWidth: {DEFAULT_CONFIG['width']},")
        print(f"     animations: {{")
        for file_name, line_num, description, _ in found:
            print(f"       {file_name}: {{ line: {line_num} }},  // {description}")
        print(f"     }}")
        print(f"   }};")
    
    if fail_count > 0:
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Génère un spritesheet multilignes à partir de vidéos MP4',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s ./videos --output=familier.png
  %(prog)s ./videos --output=familier.png --config=config.json
  %(prog)s ./videos --output=familier.png --size=256 --width=256

Le script vérifie d'abord que tous les fichiers requis sont présents,
puis génère un spritesheet multilignes où chaque animation est placée
sur sa ligne respective (définie dans REQUIRED_FILES).
        """
    )
    
    parser.add_argument('source_dir', 
                       help='Dossier contenant les fichiers MP4')
    parser.add_argument('--output', '-o', required=True,
                       help='Fichier PNG de sortie (spritesheet multilignes)')
    parser.add_argument('--config', '-c',
                       help='Fichier de configuration JSON (optionnel)')
    parser.add_argument('--size', type=int,
                       help=f'Hauteur des frames (défaut: {DEFAULT_CONFIG["size"]})')
    parser.add_argument('--width', type=int,
                       help='Largeur fixe des frames (optionnel)')
    parser.add_argument('--fps', type=int,
                       help=f'FPS pour l\'extraction (défaut: {DEFAULT_CONFIG["fps"]})')
    
    args = parser.parse_args()
    
    # Met à jour la config avec les arguments
    if args.size:
        DEFAULT_CONFIG["size"] = args.size
    if args.width:
        DEFAULT_CONFIG["width"] = args.width
    if args.fps:
        DEFAULT_CONFIG["fps"] = args.fps
    
    # Vérifie que le dossier source existe
    if not os.path.isdir(args.source_dir):
        print(f"❌ Erreur: Le dossier '{args.source_dir}' n'existe pas")
        sys.exit(1)
    
    # Génère le spritesheet
    generate_spritesheet(args.source_dir, args.output, args.config)

if __name__ == '__main__':
    main()
