#!/bin/bash
# Script de test pour mp4-to-sprite

echo "🧪 Test de MP4toSprite"
echo "====================="
echo ""

# Crée un répertoire de test
mkdir -p test-output
cd test-output

echo "📹 Création d'une vidéo de test synthétique..."

# Crée une vidéo de test avec un cercle qui se déplace (avec fond blanc)
ffmpeg -f lavfi -i "color=white:s=400x400:d=2" \
       -vf "drawbox=x='(iw-200)/2':y='(ih-200)/2+(sin(2*PI*t/2))*80':w=200:h=200:color=blue:t=fill" \
       -t 2 -pix_fmt yuv420p -y test-video-simple.mp4 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Vidéo simple créée: test-video-simple.mp4"
else
    echo "❌ Erreur lors de la création de la vidéo"
    exit 1
fi

# Crée une vidéo avec fond en checkerboard (simule la transparence)
ffmpeg -f lavfi -i "color=lightgray:s=400x400:d=2" \
       -f lavfi -i "color=white:s=400x400:d=2" \
       -filter_complex "[0][1]blend=all_expr='if(mod(floor(X/20)+floor(Y/20),2),A,B)':shortest=1[bg]; \
                        [bg]drawbox=x='(iw-150)/2':y='(ih-150)/2':w=150:h=150:color=red:t=fill, \
                        drawbox=x='(iw-150)/2+(sin(2*PI*t/2))*60':y='(ih-150)/2':w=150:h=150:color=blue:t=fill" \
       -t 2 -pix_fmt yuv420p -y test-video-checkerboard.mp4 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Vidéo checkerboard créée: test-video-checkerboard.mp4"
else
    echo "⚠️  Impossible de créer la vidéo checkerboard (normal si ffmpeg est ancien)"
fi

echo ""
echo "🧪 Tests du script..."
echo ""

# Test 1: Conversion basique sans transparence
echo "Test 1: Conversion basique (sans transparence)"
echo "----------------------------------------------"
../mp4-to-sprite.py test-video-simple.mp4 \
    --size=100 \
    --start=0 \
    --end=1 \
    --fps=8 \
    --output=test1-basic.png

echo ""
echo ""

# Test 2: Conversion avec transparence
echo "Test 2: Conversion avec transparence"
echo "-------------------------------------"
../mp4-to-sprite.py test-video-simple.mp4 \
    --size=100 \
    --transparent \
    --tolerance=30 \
    --start=0 \
    --end=1 \
    --fps=8 \
    --output=test2-transparent.png

echo ""
echo ""

# Test 3: Haute résolution, plus de frames
echo "Test 3: Haute résolution, plus de frames"
echo "-----------------------------------------"
../mp4-to-sprite.py test-video-simple.mp4 \
    --size=200 \
    --transparent \
    --start=0 \
    --end=2 \
    --fps=15 \
    --output=test3-hires.png

echo ""
echo ""

# Test 4: Segment spécifique
echo "Test 4: Segment spécifique (0.5s à 1.5s)"
echo "-----------------------------------------"
../mp4-to-sprite.py test-video-simple.mp4 \
    --size=80 \
    --transparent \
    --start=0.5 \
    --end=1.5 \
    --fps=10 \
    --output=test4-segment.png

echo ""
echo ""

# Test avec checkerboard si disponible
if [ -f test-video-checkerboard.mp4 ]; then
    echo "Test 5: Vidéo avec fond checkerboard"
    echo "-------------------------------------"
    ../mp4-to-sprite.py test-video-checkerboard.mp4 \
        --size=120 \
        --transparent \
        --tolerance=40 \
        --fps=10 \
        --output=test5-checkerboard.png
    echo ""
    echo ""
fi

# Résumé
echo "======================================"
echo "✅ Tests terminés !"
echo "======================================"
echo ""
echo "📁 Fichiers générés dans test-output/:"
ls -lh *.png 2>/dev/null | awk '{print "   " $9 " - " $5}'
echo ""
echo "🔍 Pour visualiser les résultats:"
echo "   Ouvre les fichiers PNG dans un viewer d'images"
echo ""

cd ..
