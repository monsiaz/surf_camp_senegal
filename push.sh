#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  push.sh  —  Build → Commit → Deploy en une commande
#
#  Usage:
#    ./push.sh "message de commit"
#    ./push.sh                      # utilise un message auto
#
#  Ce script :
#   1. Lance build.py pour s'assurer que les HTML sont à jour
#   2. Stage tous les changements
#   3. Commit avec le message fourni (ou auto)
#   4. Fetch le remote (récupère le chore: bump version du CI)
#   5. Push avec --force-with-lease (safe override des version bumps)
# ─────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

MSG="${1:-"chore: mise à jour site $(date '+%Y-%m-%d %H:%M')"}"

echo ""
echo "🏄  Ngor Surfcamp — Push Pipeline"
echo "────────────────────────────────────────────"

# 1. Build
echo "▶  build.py..."
python3 build.py 2>&1 | tail -5

# 2. Stage + commit (ignore si rien à committer)
echo ""
echo "▶  Commit: \"$MSG\""
git add -A
if git diff --cached --quiet; then
  echo "   (rien à committer — working tree propre)"
else
  git commit -m "$MSG"
fi

# 3. Fetch (récupère les chore:bump du CI sans merger)
echo ""
echo "▶  Fetch origin/main..."
git fetch origin

# 4. Push avec force-with-lease (safe: protège contre pertes accidentelles)
#    Si le remote n'a que des chore:bump [skip ci], on écrase proprement.
echo "▶  Push --force-with-lease..."
if git push --force-with-lease; then
  echo ""
  echo "✅  Pushé avec succès ! Déploiement Vercel en cours..."
  echo ""
  # Afficher l'URL du run CI
  REPO=$(git remote get-url origin | sed 's/.*github\.com[:/]//' | sed 's/\.git$//')
  echo "   👉 Suivi CI : https://github.com/$REPO/actions"
  echo "   👉 Site live : https://surf-camp-senegal.vercel.app"
else
  echo ""
  echo "❌  Push échoué. Essai avec push normal..."
  git pull --rebase origin main
  git push
fi
