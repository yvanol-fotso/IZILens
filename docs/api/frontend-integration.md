# Guide d'intégration front-end (KYC V1)

Base : `/api/v1`. Authentification : en-tête `Authorization: Bearer <access_token>` (dashboard, back-office), `X-API-Key` (intégration serveur) ou `X-Session-Token` (parcours hébergé de la personne).
Toutes les erreurs ont la forme `{"error": {"code", "message", "request_id", "details?"}}` : le front s'appuie sur `code`, jamais sur `message`.

## Changements par rapport à la première version

| Sujet | Avant | Maintenant |
|---|---|---|
| Création `POST /kyc/cases` | champs optionnels, recto obligatoire | `country_code` et `document_type` **obligatoires** ; `front` optionnel (sans fichier : parcours hébergé) ; champs `declared_*`, `language`, `journey_code`, `consent_terms_version` |
| Réponse de création | résumé du dossier | idem + `session` (`token` affiché une fois, `hosted_url`, `expires_at`) |
| Statuts | `processing`, `pending_review`, `approved`, `rejected`, `failed` | `created`, `in_progress`, `action_required`, `processing`, `manual_review`, `verified`, `not_verified`, `failed`, `expired` |
| Décision `POST /kyc/cases/{id}/decision` | `approved` / `rejected` | **inchangé** (`approved` → `verified`, `rejected` → `not_verified`) |
| `failure_reason` | motif d'échec | remplacé par `status_reason` (+ `status_message` localisé) |
| Détail dossier | champs extraits, signaux | + `declared_identity`, `checks`, `attempts`, `attempts_summary`, `scope`, `allowed_actions`, `journey_code`, `failure_kind`, signaux avec `message` localisé |
| Signaux | `message` statique FR | `message` selon `?lang=fr|en` (ou langue du dossier) |

## Principe : le front ne décide pas, il affiche `allowed_actions`

`GET /kyc/cases/{id}` renvoie `allowed_actions` selon le statut et le rôle : `upload_documents`, `update_declared_identity`, `assign`, `decide`, `request_action`, `reprocess`, `view_documents`, `grant_attempts`, `transition`. N'affichez un bouton que si l'action y figure.

## 1. Entreprise cliente (API key ou dashboard)

| Besoin | Appel |
|---|---|
| Documents supportés et lacunes | `GET /kyc/coverage?country_code=CM` |
| Parcours disponibles | `GET /kyc/journeys` |
| Créer un dossier (mode API) | `POST /kyc/cases` multipart : `country_code`, `document_type`, `declared_surname`, `declared_given_names`, `declared_date_of_birth` (AAAA-MM-JJ), `front`, `back?`, `reference?`, `language?` |
| Créer un dossier (parcours hébergé) | même appel **sans** `front` : redirigez la personne vers `session.hosted_url` |
| Suivre | `GET /kyc/cases/{id}`, `GET /kyc/cases`, `GET /kyc/cases/{id}/timeline`, webhooks |
| Compléter | `PUT /kyc/cases/{id}/declared-identity`, `POST /kyc/cases/{id}/documents` |
| Nouveau lien hébergé | `POST /kyc/cases/{id}/session` (l'ancien jeton est invalidé) |
| Revue (reviewer, admin) | `GET /kyc/review-queue`, `POST …/assign`, `POST …/decision`, `POST …/request-action`, `POST …/reprocess`, `GET …/documents/{id}/content` |
| Facturation, compteurs | `GET /kyc/usage` (admin), `GET /kyc/stats` |
| Notifications | `POST /webhooks`, `GET /webhooks`, `DELETE /webhooks/{id}`, `GET /webhooks/{id}/deliveries` |
| Libellés FR/EN | `GET /kyc/messages` |

Le traitement OCR est asynchrone : après `202`, interrogez `GET /kyc/cases/{id}` toutes les 2 s tant que `status` vaut `processing`, ou utilisez un webhook.

## 2. Parcours hébergé (la personne vérifiée)

La page publique lit le jeton dans l'URL et l'envoie en `X-Session-Token`. Aucun autre identifiant n'est nécessaire.

1. `GET /kyc/session` : `next_action` ∈ `accept_terms`, `provide_identity`, `upload_document`, `wait`, `done` ; `instructions`, `documents_allowed`, `attempts`, `message` localisés.
2. `POST /kyc/session/consent` `{accepted: true, terms_version}`.
3. `PUT /kyc/session/declared-identity` `{surname, given_names, date_of_birth}`.
4. `POST /kyc/session/documents` (multipart `front`, `back?`).
5. Sondage de `GET /kyc/session` puis `GET /kyc/session/result` (`final`, `message`, `scope.disclaimer`).

La réponse de la session ne contient jamais les données lues sur le document.

## 3. Back-office IZI LENS (`platform_compliance`, `super_admin`)

| Besoin | Appel |
|---|---|
| Tous les dossiers | `GET /admin/kyc/cases?organization_id=&status=&country_code=` |
| File de revue plateforme | `GET /admin/kyc/review-queue` |
| Détail, historique, document | `GET /admin/kyc/cases/{id}`, `…/timeline`, `…/documents/{id}/content` |
| Revue | `POST /admin/kyc/cases/{id}/assign|decision|request-action|reprocess` |
| Tentatives supplémentaires | `POST /admin/kyc/cases/{id}/grant-attempts` |
| Changer un statut (super admin) | `POST /admin/kyc/cases/{id}/transition` `{to_status, reason ≥ 10 car., exception?}` |
| Matrice documents | `GET|POST /admin/kyc/coverage`, `PATCH /admin/kyc/coverage/{id}` (super admin) |
| Parcours | `GET|POST /admin/kyc/journeys`, `PATCH /admin/kyc/journeys/{id}` (super admin) |
| Statistiques, facturation | `GET /admin/kyc/stats`, `GET /admin/kyc/usage` |
| Maintenance manuelle | `POST /admin/maintenance/run` (super admin) |
| Utilisateurs plateforme | `POST /users` avec `role: "platform_compliance"` (super admin) |

Le changement de statut vers `verified` est refusé tant qu'un contrôle biométrique obligatoire n'est pas satisfait, sauf `exception: true` justifiée (tracée).

## 4. Connexion Google (OpenID Connect)

`GET /auth/oidc/providers` indique si Google est actif et fournit le `client_id`.

**Bouton Google (recommandé)** : obtenez un `id_token` via Google Identity Services, puis `POST /auth/oidc/google/token` `{id_token, nonce?}` → `{access_token, refresh_token}`.

**Flux code + PKCE** : `GET /auth/oidc/google/authorize?redirect_uri&state&nonce&code_challenge` → `authorization_url` ; au retour, `POST /auth/oidc/google/callback` `{code, redirect_uri, code_verifier, nonce?}`.

Règles : seuls les utilisateurs **déjà invités** (`POST /users` sans mot de passe) peuvent se connecter ; aucun compte n'est créé automatiquement ; l'e-mail Google doit être vérifié ; `redirect_uri` doit figurer dans `OIDC_ALLOWED_REDIRECT_URIS`. Codes d'erreur : `ACCOUNT_NOT_PROVISIONED`, `INVALID_ID_TOKEN`, `EMAIL_NOT_VERIFIED`, `IDENTITY_MISMATCH`, `OIDC_DISABLED`.

## 5. Webhooks

Événements : `case.created`, `case.status_changed`. Corps JSON sans donnée personnelle : `event`, `case_id`, `reference`, `status`, `status_reason`, `previous_status`, `occurred_at`.
En-tête `X-IZILens-Signature: t=<timestamp>,v1=<hmac>` : HMAC-SHA256 de `"<timestamp>." + corps brut` avec le secret `whsec_…` (affiché une seule fois). Rejetez les horodatages de plus de 5 minutes. Répondez `2xx` ; sinon nouvelles tentatives avec attente croissante.

## 6. Codes d'erreur fréquents

`DOCUMENT_NOT_SUPPORTED`, `DOCUMENT_SIDE_REQUIRED`, `REFERENCE_ALREADY_USED`, `INVALID_STATE`, `INVALID_TRANSITION`, `ATTEMPTS_EXHAUSTED`, `CASE_EXPIRED`, `CONSENT_REQUIRED`, `DECLARED_IDENTITY_REQUIRED`, `REASON_REQUIRED_FOR_HIGH_RISK`, `REQUIRED_CHECKS_NOT_SATISFIED`, `REVIEW_TEAM_MISMATCH`, `ASSIGNED_TO_ANOTHER`, `MODULE_NOT_ENABLED`, `INVALID_SESSION`, `FILE_TOO_LARGE`, `UNSUPPORTED_IMAGE_FORMAT`, `IMAGE_TOO_SMALL`.

## 7. Compatibilité avec le dashboard SvelteKit

Le dashboard livré (`dashboard/`) a été vérifié contre ce backend : connexion (avec code MFA si activé), création d'un dossier avec identité déclarée, décision d'un analyste, pages d'administration, formulaires publics. Points de contrat :

| Sujet | Comportement du backend |
|---|---|
| Création de dossier | `country_code` facultatif : déduit du type de document lorsqu'il n'existe que dans un pays supporté, sinon `COUNTRY_REQUIRED` |
| Liste des dossiers | `page_size` jusqu'à 200, filtres `status`, `risk_level`, `search` (référence ou début d'identifiant), `limit` ignoré |
| Détail | en plus des champs structurés : `extracted_data` (valeurs normalisées à plat) et `failure_reason` |
| Utilisateurs et organisations | listes jusqu'à 200 par page (100 par défaut) ; `PATCH /users/{id}`, `PATCH /users/me` ; `POST /organizations` accepte `admin_email` (administrateur invité) |
| Authentification | `POST /auth/register` (202 identique que l'adresse existe ou non), `/auth/logout`, `/auth/oauth/google` (alias), `GET /api/v1/health` |
| Erreurs | enveloppe `{error:{code,message,request_id}}` : le dashboard lit `error.message` et `error.code` |

Nouveaux groupes d'endpoints pour les écrans à construire : voir `docs/specifications/platform-modules.md`.
