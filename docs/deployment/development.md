# Développement local (Windows, PostgreSQL dans Docker)

PostgreSQL tourne dans Docker pour éviter toute installation locale. **La production n'utilise pas Docker** : voir `production.md`.

```powershell
# 1. Base de données
docker compose -f infrastructure/deployment/docker-compose.dev.yml up -d
docker ps                         # izilens-postgres doit être "healthy"

# 2. Backend
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements.additions.txt
copy .env.example .env
python scripts/generate_secrets.py     # coller les 3 lignes dans .env

# 3. Schéma et comptes de démonstration
alembic upgrade head
python scripts/bootstrap.py --email admin@izilens.com --demo

# 4. Lancement
uvicorn app.main:app --reload          # http://127.0.0.1:8000/docs
```

Tests : `pytest` (SQLite temporaire) ou, sur PostgreSQL :
`$env:TEST_DATABASE_URL="postgresql+psycopg://izilens:izilens_dev@localhost:5432/izilens_test"; pytest`
(la base `izilens_test` est créée automatiquement au premier démarrage du conteneur ; sur un volume existant : `docker exec izilens-postgres psql -U izilens -c "CREATE DATABASE izilens_test OWNER izilens;"`).

Tâche de maintenance en local : `python scripts/maintenance.py` (expiration des demandes, envoi des webhooks).
Connexion Google en local : renseigner `OIDC_ENABLED=true`, `GOOGLE_CLIENT_ID` et `OIDC_ALLOWED_REDIRECT_URIS=http://localhost:5173/auth/callback`.

## Dashboard (SvelteKit)

```powershell
cd dashboard
copy .env.example .env      # BACKEND_SERVICE_URL=http://127.0.0.1:8000, ORIGIN, BODY_SIZE_LIMIT=20M
npm ci
npm run dev                 # http://localhost:5173
```

Comptes de démonstration : ceux affichés par `python scripts/bootstrap.py --demo` (admin, reviewer, viewer de « Demo Bank », compliance IZI LENS).
Avec `EMAIL_BACKEND=console` (par défaut en développement), le contenu des e-mails (mot de passe temporaire d'un administrateur invité, référence d'une demande) apparaît dans les journaux de l'API.
