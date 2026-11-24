# Contrat attendu du backend FastAPI

Le dashboard appelle le backend **uniquement côté serveur SvelteKit** (`BACKEND_SERVICE_URL` + `BACKEND_API_PREFIX`).
Le navigateur ne voit jamais les jetons JWT (cookies `httpOnly`).
Toutes les routes ci-dessous sont centralisées dans `src/lib/server/endpoints.ts` : si l'une diffère chez vous, c'est le seul fichier à modifier.

| Usage | Route | Corps / réponse attendue |
|---|---|---|
| Connexion | `POST /auth/login` | `{email,password}` (ou form `username/password` si `BACKEND_LOGIN_FORMAT=form`) → `{access_token, refresh_token}` |
| Rafraîchir | `POST /auth/refresh` | `{refresh_token}` → `{access_token[, refresh_token]}` |
| Déconnexion | `POST /auth/logout` | optionnelle (meilleur effort) |
| Profil | `GET /auth/me` | `{id,email,full_name,role,organization_id,is_active,last_login_at}` |
| Inscription | `POST /auth/register` | `{full_name,email,password}` |
| Mot de passe | `POST /auth/change-password` | `{current_password,new_password}` |
| **OIDC Google** | `POST /auth/oauth/google` | `{id_token, nonce}` → `{access_token, refresh_token}` |
| Organisation courante | `GET /organizations/me` | `{id,name,slug,is_active,enabled_modules}` |
| Organisations (super_admin) | `GET/POST /organizations`, `GET/PATCH /organizations/{id}` | `enabled_modules` = liste ou objet booléen |
| Utilisateurs | `GET/POST /users`, `PATCH /users/{id}`, `PATCH /users/me` | |
| Clés API | `GET/POST /api-keys`, `DELETE /api-keys/{id}` | `POST` renvoie `{key}` **une seule fois** |
| Dossiers KYC | `GET /kyc/cases` (filtres `status`, `risk_level`, `search`, `page`, `page_size`) | tableau **ou** `{items,total}` |
| | `POST /kyc/cases` (multipart `document_type`, `reference`, `front`, `back`) | `{id,…}` |
| | `GET /kyc/cases/{id}` | dossier + `documents[]` |
| | `GET /kyc/cases/{id}/documents/{docId}/content` | image |
| | `POST /kyc/cases/{id}/decision` | `{decision:"approved"\|"rejected", reason}` ; `409` si déjà décidé |
| Audit | `GET /audit-logs` | tableau ou `{items,total}` |
| Santé | `GET /health` | 200 |
| **Demandes publiques** (contact, devis, démo) | `POST /public/contact-requests` | `{kind:"contact"\|"demo", locale, fields:{full_name,company,email,country,role,type,subject,message,services[],sector,volume,consent_privacy,consent_marketing}}` → `{reference}` (+ e-mail de confirmation, routage Sales / Partnerships, statuts New → Closed) |
| *(à venir)* Vivacité | `POST /liveness/sessions`, `GET/PATCH /liveness/settings` | si absent, l'UI passe en mode démonstration |

## Ajouter `POST /auth/oauth/google` côté FastAPI

Le dashboard dialogue avec Google (code + PKCE), puis envoie l'`id_token` au backend, qui **vérifie la signature** et émet ses propres JWT.

```python
from google.oauth2 import id_token as google_id
from google.auth.transport import requests as g_requests

@router.post("/auth/oauth/google", response_model=TokenPair)
def oauth_google(body: OAuthIn, db: Session = Depends(get_db)):
    try:
        claims = google_id.verify_oauth2_token(body.id_token, g_requests.Request(), settings.GOOGLE_CLIENT_ID)
    except ValueError:
        raise HTTPException(401, "invalid_id_token")
    if claims.get("nonce") != body.nonce or not claims.get("email_verified"):
        raise HTTPException(401, "invalid_claims")
    user = users.get_by_email(db, claims["email"])
    if not user or not user.is_active:
        raise HTTPException(403, "no_account")   # → /login?error=oauth_denied
    return issue_tokens(user)                      # mêmes JWT que /auth/login
```

Décision produit : refuser (403, comme ci-dessus) ou **créer** le compte à la première connexion Google.

## Google Cloud Console
Type *Application Web* ; URI de redirection : `https://<domaine>/api/auth/oauth` (et `http://localhost:5173/api/auth/oauth` en dev).

## Hors périmètre de cette livraison (backend à construire)
Facturation (forfaits, consommation, avoirs, multi-devises), Super Admin complet (rôles, MFA, centre de sécurité, rapports),
CMS éditorial (blog, guides, FAQ administrable), portail développeur (comptes, demandes d'accès, Sandbox/Production, webhooks).
Le dashboard actuel n'affiche aucune de ces fonctionnalités comme opérationnelle.


---

## État du backend (version finale)

Le backend FastAPI du dépôt fournit désormais tout ce contrat : authentification (JWT, Google OIDC, MFA TOTP, inscription), organisations, utilisateurs, clés API, dossiers KYC (parcours API et hébergé), audit, `POST /public/contact-requests`, ainsi que les modules **facturation**, **Super Admin** (rôles, centre de sécurité, rapports), **contenus éditoriaux** et **portail développeur** (Sandbox/Production) dont les écrans restent à construire dans ce dashboard.
Statuts d'un dossier : `created`, `in_progress`, `action_required`, `processing`, `manual_review`, `verified`, `not_verified`, `failed`, `expired`.
Référence complète : `docs/api/frontend-integration.md` et `docs/specifications/platform-modules.md` (dépôt racine).
