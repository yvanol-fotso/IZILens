#!/usr/bin/env bash
# Première installation sur un serveur Ubuntu 24.04 (exécuter en root). Voir docs/deployment/production.md.
set -euo pipefail

apt-get update
apt-get install -y python3.12 python3.12-venv python3-pip postgresql nginx certbot python3-certbot-nginx git libgl1 libglib2.0-0 curl
# Node.js 22 pour le dashboard (dépôt NodeSource)
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs

id izilens >/dev/null 2>&1 || useradd --system --create-home --home-dir /opt/izilens --shell /usr/sbin/nologin izilens
install -d -o izilens -g izilens -m 750 /var/lib/izilens /var/lib/izilens/storage /var/log/izilens /etc/izilens
install -d -o izilens -g izilens -m 700 /var/backups/izilens

echo "1. Cloner le dépôt dans /opt/izilens (git clone <url> /opt/izilens)"
echo "2. Créer la base : sudo -u postgres psql -f /opt/izilens/infrastructure/deployment/production/provision-postgres.sql"
echo "3. Copier backend.env.example vers /etc/izilens/backend.env et le remplir (chmod 640 root:izilens)"
echo "4. Copier les unités systemd : cp /opt/izilens/infrastructure/deployment/production/*.service *.timer /etc/systemd/system/"
echo "5. bash /opt/izilens/infrastructure/deployment/production/deploy.sh main"
echo "6. python scripts/bootstrap.py --email <super-admin>   (sans --demo)"
echo "7. systemctl enable --now izilens-backend izilens-maintenance.timer izilens-backup.timer"
echo "8. Dashboard : cp dashboard.env.example /etc/izilens/dashboard.env, le remplir, puis systemctl enable --now izilens-dashboard"
echo "9. nginx + certbot : nginx-izilens.conf (API) et nginx-izilens-dashboard.conf (site)"
