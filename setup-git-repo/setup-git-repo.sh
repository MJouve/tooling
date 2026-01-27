#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <nom_projet>"
    exit 1
fi

PROJECT_NAME="$1"
KEY_NAME="id_ed25519_${PROJECT_NAME}"
KEY_PATH="$HOME/.ssh/${KEY_NAME}"
EMAIL="${2:-$(git config user.email 2>/dev/null || echo '')}"

if [ -z "$EMAIL" ]; then
    read -p "Email pour la clé SSH: " EMAIL
fi

echo "=== Création de la clé SSH ==="
ssh-keygen -t ed25519 -C "$EMAIL" -f "$KEY_PATH" -N ""

echo ""
echo "=== Clé publique ==="
echo "Copiez cette clé et ajoutez-la sur GitHub/GitLab :"
echo ""
cat "${KEY_PATH}.pub"
echo ""

read -p "Appuyez sur Entrée une fois la clé ajoutée sur GitHub/GitLab..."

echo ""
echo "=== Configuration SSH ==="
if [ ! -f ~/.ssh/config ]; then
    touch ~/.ssh/config
    chmod 600 ~/.ssh/config
fi

if grep -q "Host git-${PROJECT_NAME}" ~/.ssh/config; then
    echo "La configuration SSH pour ce projet existe déjà."
else
    read -p "Hostname Git (github.com ou gitlab.com) [github.com]: " GIT_HOST
    GIT_HOST=${GIT_HOST:-github.com}
    
    cat >> ~/.ssh/config << EOF

Host git-${PROJECT_NAME}
    HostName ${GIT_HOST}
    User git
    IdentityFile ${KEY_PATH}
EOF
    echo "Configuration SSH ajoutée."
fi

echo ""
echo "=== Ajout de la clé au ssh-agent ==="
eval "$(ssh-agent -s)" > /dev/null 2>&1
ssh-add "$KEY_PATH" 2>/dev/null || true

echo ""
echo "=== Initialisation Git ==="
if [ -d .git ]; then
    echo "Le dépôt Git existe déjà."
else
    git init
    git add .
    git commit -m "Initial commit" || echo "Aucun fichier à committer."
fi

echo ""
echo "=== Configuration du remote ==="
read -p "Username GitHub/GitLab: " GIT_USERNAME
read -p "Nom du repository: " REPO_NAME

REMOTE_URL="git@git-${PROJECT_NAME}:${GIT_USERNAME}/${REPO_NAME}.git"

if git remote get-url origin > /dev/null 2>&1; then
    read -p "Le remote 'origin' existe déjà. Le remplacer ? (o/N): " REPLACE
    if [[ "$REPLACE" =~ ^[Oo]$ ]]; then
        git remote set-url origin "$REMOTE_URL"
    else
        git remote add "$PROJECT_NAME" "$REMOTE_URL"
        REMOTE_NAME="$PROJECT_NAME"
    fi
else
    git remote add origin "$REMOTE_URL"
fi

echo ""
echo "=== Push vers Git ==="
read -p "Branche à utiliser [main]: " BRANCH
BRANCH=${BRANCH:-main}

git branch -M "$BRANCH" 2>/dev/null || true
git push -u origin "$BRANCH"

echo ""
echo "=== Terminé ==="
echo "Repository configuré avec succès !"
