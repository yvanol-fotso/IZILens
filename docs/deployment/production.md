# Déploiement en production (sans Docker)

Cible : un serveur Ubuntu 24.04, PostgreSQL installé sur la machine (ou un service PostgreSQL géré), uvicorn (API) et Node.js (dashboard et site public) sous systemd, nginx en frontal TLS.

## Architecture

```
Internet → nginx app.example.com → Node.js 127.0.0.1:3000 (dashboard + site public) ─┐
         → nginx api.example.com → uvicorn 127.0.0.1:8000 (2 workers) ←──────────────┘
                                          ├→ PostgreSQL
                                          └→ /var/lib/izilens/storage (fichiers chiffrés)
timers systemd : maintenance (chaque minute : expiration, webhooks, e-mails), sauvegarde (quotidienne)
```

Le dashboard appelle l'API côté serveur (`BACKEND_SERVICE_URL`) : l'API peut rester sur `127.0.0.1` et n'être exposée publiquement que pour les intégrations des clients.

## 1. Première installation

```bash
sudo bash infrastructure/deployment/production/install.sh     # paquets, utilisateur izilens, répertoires
sudo git clone <depot> /opt/izilens && sudo chown -R izilens:izilens /opt/izilens
sudo -u postgres psql -f /opt/izilens/infrastructure/deployment/production/provision-postgres.sql   # après avoir changé le mot de passe
```

## 2. Configuration

```bash
sudo cp infrastructure/deployment/production/backend.env.example /etc/izilens/backend.env
sudo chown root:izilens /etc/izilens/backend.env && sudo chmod 640 /etc/izilens/backend.env
sudo -u izilens /opt/izilens/backend/.venv/bin/python /opt/izilens/backend/scripts/generate_secrets.py   # copier les 3 valeurs
```

Le démarrage échoue volontairement si un secret de démonstration (`change-me`), `CORS_ORIGINS=*` ou `WEBHOOK_ALLOW_HTTP=true` subsiste en production.
Conservez `DATA_ENCRYPTION_KEYS` dans un coffre de secrets séparé : sans elle, les documents et les données chiffrées sont illisibles, y compris depuis une sauvegarde.

## 3. Déployer

```bash
sudo -u izilens bash infrastructure/deployment/production/deploy.sh main
sudo -u izilens bash -c 'set -a; . /etc/izilens/backend.env; set +a; cd /opt/izilens/backend && .venv/bin/python scripts/bootstrap.py --email <super-admin>'   # sans --demo
sudo cp infrastructure/deployment/production/*.service infrastructure/deployment/production/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo cp infrastructure/deployment/production/dashboard.env.example /etc/izilens/dashboard.env   # puis le remplir (ORIGIN, GOOGLE_*)
sudo systemctl enable --now izilens-backend izilens-dashboard izilens-maintenance.timer izilens-backup.timer
```

`deploy.sh` met à jour le code, installe les dépendances, applique les migrations Alembic **avant** le redémarrage, joue les tests unitaires et vérifie `/health/ready`.

## 4. nginx et TLS

Adapter `nginx-izilens.conf` (nom de domaine), l'installer dans `/etc/nginx/sites-available/`, l'activer, puis `sudo certbot --nginx -d api.example.com`. L'accès à `/docs` est bloqué par défaut.

## 4 bis. E-mails

`EMAIL_BACKEND=smtp` est obligatoire en production (le mode `console`, qui journalise le contenu, est refusé au démarrage). Les messages (confirmation de demande, invitation d'un administrateur, décision d'accès développeur) sont écrits dans la table `email_outbox` puis envoyés par le timer de maintenance, avec 5 tentatives. Renseignez `SALES_EMAIL` et `PARTNERSHIPS_EMAIL` pour recevoir l'alerte interne de chaque nouvelle demande publique.

## 5. Mise à jour et retour arrière

- Mise à jour : `sudo -u izilens bash deploy.sh <branche>`.
- Retour arrière du code : `git checkout <tag-precedent>` puis `deploy.sh`.
- Retour arrière du schéma : `alembic downgrade -1` (les migrations 0001 à 0003 sont réversibles). Sauvegardez avant toute migration destructrice.

## 6. Exploitation

| Sujet | Commande ou emplacement |
|---|---|
| Journaux applicatifs (JSON) | `journalctl -u izilens-backend -f` |
| État | `curl http://127.0.0.1:8000/health/ready` |
| Maintenance (expiration, webhooks) | `journalctl -u izilens-maintenance` |
| Sauvegardes | `/var/backups/izilens` (14 jours) ; restauration : `pg_restore -d izilens db-<date>.dump` |
| Rotation des clés de chiffrement | ajouter la nouvelle clé **en tête** de `DATA_ENCRYPTION_KEYS` (liste séparée par des virgules) ; l'ancienne reste pour lire l'existant |
| Rotation du secret JWT | changer `JWT_SECRET` et redémarrer : toutes les sessions sont invalidées |

## 7. Points de vigilance

- **Mémoire** : chaque worker charge PaddleOCR (plusieurs centaines de Mo). Ajuster `--workers` et `MemoryMax`.
- **Limiteur de débit** : par processus. Avec plusieurs instances, le déplacer vers Redis.
- **OCR en tâche de fond** : exécuté dans le processus de l'API. Une file de tâches (Celery + Redis) sera nécessaire pour un fort volume.
- **IP client** : nginx transmet `X-Forwarded-For` ; uvicorn ne l'accepte que depuis 127.0.0.1 (`--forwarded-allow-ips`).
- **Rétention** : aucune suppression automatique des documents n'est en place ; la durée doit être fixée avec le juridique.
