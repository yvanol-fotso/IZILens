# IZILens – Backend

API FastAPI (monolithe modulaire) : authentification (mot de passe, Google OpenID Connect, MFA TOTP, inscription), organisations, clés API, **module KYC** complet (parcours API et hébergé, OCR PaddleOCR, règles de décision, revue humaine, back-office, webhooks), et les modules de plateforme : demandes publiques, contenus éditoriaux, portail développeur Sandbox/Production, centre de sécurité et rapports, facturation multi-devises, e-mails. Base de données : PostgreSQL.

| Besoin | Document |
|---|---|
| Lancer en développement (Docker pour PostgreSQL) | `docs/deployment/development.md` |
| Déployer en production (sans Docker) | `docs/deployment/production.md` |
| Appels attendus du front-end | `docs/api/frontend-integration.md` |
| Exigences, règles et critères d'acceptation : preuve par test | `docs/specifications/kyc-v1.md` |
| Brancher le liveness, ajouter le KYB | `docs/architecture/module-extension.md` |
| Demandes publiques, contenus, accès développeur, sécurité, facturation | `docs/specifications/platform-modules.md` |

## Démarrage rapide

```powershell
docker compose -f ../infrastructure/deployment/docker-compose.dev.yml up -d
pip install -r requirements.txt ; pip install -r requirements.additions.txt
copy .env.example .env ; python scripts/generate_secrets.py     # coller les 3 secrets dans .env
alembic upgrade head
python scripts/bootstrap.py --email admin@izilens.com --demo
uvicorn app.main:app --reload                                    # http://127.0.0.1:8000/docs
```

## Architecture

| Dossier | Rôle |
|---|---|
| `app/core` | Configuration, base, sécurité, exceptions, middleware, dépendances d'accès |
| `app/modules/kyc` | Dossiers, tentatives, contrôles, règles, parcours, couverture, session hébergée |
| `app/modules/backoffice` | Endpoints d'administration IZI LENS |
| `app/modules/{auth,users,organizations,api_keys,audit,webhooks}` | Identité, MFA, clients, traçabilité, notifications |
| `app/modules/{public_requests,cms,developers,security,billing,notifications}` | Demandes publiques, contenus, accès développeur, sécurité et rapports, facturation, e-mails |
| `app/shared` | OCR, validation de fichiers, stockage chiffré, libellés FR/EN |
| `migrations` | Alembic (0001 base, 0002 KYC V1 complet, 0003 extensions de plateforme) |
| `scripts` | `bootstrap`, `generate_secrets`, `maintenance` |

## Qualité

```powershell
pytest                       # 250 tests, SQLite temporaire
$env:TEST_DATABASE_URL="postgresql+psycopg://izilens:izilens_dev@localhost:5432/izilens_test"; pytest
ruff check app tests scripts
```

## Sécurité

Argon2id, verrouillage de compte, JWT court + refresh, Google OIDC (jeton vérifié : signature, émetteur, audience, e-mail vérifié, nonce), clés API hachées (HMAC + poivre), isolation par organisation sur chaque requête, rôles et modules souscrits, jeton de session limité à un dossier, images validées sur le contenu réel et ré-encodées sans métadonnées, fichiers et données personnelles chiffrés au repos (rotation de clés), webhooks signés avec protection SSRF, audit en ajout seul sans donnée personnelle, limitation de débit, en-têtes de sécurité, secrets de démonstration refusés en production.

## Limites connues

Voir la section 6 de `docs/specifications/kyc-v1.md` : pas d'analyse d'authenticité visuelle, seul le recto de la CNI camerounaise est lu, module 2 non implémenté, conservation des données à définir, limiteur de débit et OCR par processus.
