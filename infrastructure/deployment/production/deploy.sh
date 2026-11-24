#!/usr/bin/env bash
# Déploiement / mise à jour en production, sans Docker : bash deploy.sh [branche]
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/izilens}"
BRANCH="${1:-main}"
VENV="$APP_DIR/backend/.venv"

cd "$APP_DIR"
git fetch --prune origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

cd backend
[ -d "$VENV" ] || python3.12 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip wheel
"$VENV/bin/pip" install -r requirements.txt -r requirements.additions.txt

set -a
# shellcheck disable=SC1091
. /etc/izilens/backend.env
set +a
"$VENV/bin/alembic" upgrade head          # migrations avant redémarrage
"$VENV/bin/python" -m pytest -q tests/unit  # contrôle rapide ; les tests d'intégration tournent en CI

sudo systemctl restart izilens-backend
sleep 5
curl --fail --silent http://127.0.0.1:8000/health/ready && echo " <- API prête"

# Dashboard et site public (Node.js 22) : build puis redémarrage
if [ -d "$APP_DIR/dashboard" ]; then
  cd "$APP_DIR/dashboard"
  npm ci --no-audit --no-fund
  npm run build
  sudo systemctl restart izilens-dashboard
  sleep 3
  curl --fail --silent --output /dev/null http://127.0.0.1:3000/login && echo "dashboard prêt"
fi
