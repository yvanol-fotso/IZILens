# IZILens – Backend

 authentification,
 organisations, 
 clés API, 
 dossiers KYC avec OCR (PaddleOCR), 
 revue humaine,
 et journal d'audit. 
 Bd : PostgreSQL.

## Démarrage

```powershell
# 1. Base de données (Docker) ou PostgreSQL installé localement
docker compose -f ../infrastructure/deployment/docker-compose.dev.yml up -d

# 2. Environnement
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements.additions.txt
copy .env.example .env    
# Use  : python scripts/generate_secrets.py   pour create les secret    

# 3. Schema + premiers comptes
alembic upgrade head
python scripts/bootstrap.py --email admin@izilens.com --demo

# 4. Lancement
uvicorn app.main:app --reload   # http://127.0.0.1:8000/docs
```

## Parcours de démonstration (Swagger `/docs`)

1. **Authorize** avec `admin@demo-bank.com` (mot de passe affiché par `bootstrap`) → `POST /api/v1/api-keys` (la clé n'est visible qu'une fois).
2. Cliquer **Authorize → X-API-Key** et coller la clé → `POST /api/v1/kyc/cases` avec le recto de la CNI.
3. `GET /api/v1/kyc/cases/{id}` : champs extraits, scores, signaux de risque (`pending_review`).
4. Se reconnecter avec `reviewer@demo-bank.com` → `GET .../documents/{id}/content` puis `POST .../decision`.
5. `GET /api/v1/audit-logs` (admin) : traçabilité complète.

## Architecture

| Dossier | Rôle |
|---|---|
| `app/core` | Configuration, base, sécurité, exceptions, middleware, dépendances d'accès |
| `app/modules/<module>` | `models`, `schemas`, `service`, `routes` par domaine (auth, users, organizations, api_keys, audit, kyc) |
| `app/shared/ocr` | Moteur PaddleOCR et extraction par étiquettes de la CNI camerounaise |
| `app/shared/validation` | Contrôle des fichiers et des champs |
| `app/shared/storage` | Stockage chiffré au repos (interface remplaçable) |
| `migrations` | Migrations Alembic |

## Qualité

```powershell
pytest                       # je make tests tempos 85 tests, BD SQLite temporaire
$env:TEST_DATABASE_URL="postgresql+psycopg://izilens:izilens_dev@localhost:5432/izilens_test"; pytest
ruff check app tests scripts
```

## Sécurité

Mots de passe Argon2id, verrouillage de compte, JWT court + refresh, clés API hachées (HMAC + poivre), isolation par organisation sur chaque requête, modules activables par client, images validées sur le contenu réel et ré-encodées sans métadonnées, fichiers et données personnelles chiffrés au repos (rotation de clés), audit en ajout seul sans donnée personnelle, limitation de débit, en-têtes de sécurité, secrets de démonstration refusés en production.

## Limites connues

Limiteur de débit et traitement OCR en mémoire (un seul process) : Redis + Celery pour la montée en charge. Jetons de rafraîchissement sans liste de révocation. Now Seul le recto de la CNI est lu ; le verso est stocké.
