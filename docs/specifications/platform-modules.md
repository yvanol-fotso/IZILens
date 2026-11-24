# Modules de plateforme : demandes publiques, contenus, accès développeur, sécurité, facturation

Ces modules couvrent ce que le dashboard n'implémente pas lui-même (facturation, Super Admin complet, CMS éditorial, portail développeur, formulaires publics). Le backend est complet et testé ; **les écrans correspondants restent à construire côté front-end** et ne doivent pas être présentés comme disponibles avant.
Légende : ✅ en place et testé · ⚠️ limite à connaître.

## 1. Demandes publiques (contact, devis, démonstration)

| Élément | Détail |
|---|---|
| Envoi | `POST /public/contact-requests` (sans authentification) ; corps `{kind: contact\|demo, locale, fields{…}}` conforme à `dashboard/docs/BACKEND_CONTRACT.md` |
| Garanties | consentement de confidentialité obligatoire, numéro de référence `IZL-AAAA-NNNNNN` séquentiel sans trou, confirmation par e-mail dans la langue de la personne |
| Anti-abus | limite par adresse IP (`PUBLIC_REQUEST_LIMIT_PER_10MIN`, 10 par défaut) et par e-mail (5 par heure) ; champs bornés ; types et services inconnus neutralisés |
| Routage | équipe `sales` (vente, devis, démonstration, autre) ou `partnerships` (partenariat, intégration, institutionnel, développeur) ; alerte interne vers `SALES_EMAIL` / `PARTNERSHIPS_EMAIL` |
| Données | coordonnées et message chiffrés au repos ; pays, secteur, volume, services en clair pour les statistiques ; adresse IP et e-mail conservés uniquement sous forme d'empreinte |
| Traitement | `GET /admin/public-requests` (filtres statut, type, équipe, recherche par référence), détail, changement de statut `new → in_review → contacted → qualified → closed` (réouverture possible), assignation, notes internes, historique, `GET …/stats` ; rôles `sales_agent`, `platform_compliance`, `super_admin` |

⚠️ Aucune relance automatique ni intégration CRM.

## 2. Contenus éditoriaux (blog, guides, FAQ)

| Élément | Détail |
|---|---|
| Public | `GET /public/content?kind=&locale=&category=&search=&tag=` et `GET /public/content/{kind}/{slug}?locale=` : uniquement les contenus publiés, mise en cache 60 s |
| Administration | `/admin/cms` : création en brouillon, modification, publication, dépublication, archivage, suppression ; rôles `content_editor` et `super_admin` |
| Règles | un contenu par type, langue et identifiant ; FAQ triée par position ; corps en Markdown ; balises actives (`<script>`, `<iframe>`, `javascript:`, gestionnaires `on…=`) refusées |

⚠️ Le Markdown est stocké brut : le front doit le rendre avec un moteur qui n'exécute pas de HTML (`markdown-it` avec `html: false`). Pas d'historique de versions ni de téléversement d'images.

## 3. Portail développeur et environnements Sandbox / Production

| Étape | Appel |
|---|---|
| Créer un compte | `POST /auth/register` : compte sans organisation ni droit d'accès |
| Demander l'accès Sandbox | `POST /developers/access-requests` `{environment: "sandbox", company_name, use_case, …}` |
| Approuver | `POST /admin/developers/access-requests/{id}/decision` : crée l'organisation (modules `kyc`, `api`, Production désactivée), rattache la personne comme administrateur, e-mail de décision ; un refus exige un motif |
| Clés | `POST /api-keys` : Sandbox par défaut tant que la Production n'est pas activée (préfixe `izl_test_`) ; `environment: "production"` refusé avec `PRODUCTION_ACCESS_REQUIRED` |
| Passer en Production | demande `environment: "production"` par l'administrateur, approbation par l'équipe commerciale ou le super administrateur |
| Suivi | `GET /developers/overview` : accès, clés actives par environnement, webhooks, demande en cours |

Les dossiers créés avec une clé Sandbox, ou par une organisation sans accès Production, sont marqués `is_sandbox` : **jamais facturés** et exclus des rapports par défaut.
⚠️ L'environnement Sandbox utilise le même moteur de traitement que la Production (pas de données simulées).

## 4. Sécurité et Super Admin

| Fonction | Détail |
|---|---|
| Rôles | catalogue `GET /admin/roles` (rôles plateforme : `super_admin`, `platform_compliance`, `sales_agent`, `content_editor`, `billing_manager` ; rôles clients : `admin`, `reviewer`, `viewer`, `integration`) ; attribution par `PATCH /users/{id}` ; seul le super administrateur crée ou attribue un rôle plateforme |
| MFA TOTP | `POST /auth/mfa/enroll` (secret et URI pour QR code), `/verify` (active et renvoie 8 codes de secours, une seule fois), `/recovery-codes`, `/disable` (mot de passe et code), `GET /auth/mfa/status` ; à la connexion, `mfa_code` est exigé (`MFA_REQUIRED`) ; un même code n'est pas rejouable ; les échecs comptent dans le verrouillage |
| Sessions | chaque jeton porte une version : changer le mot de passe, le rôle, désactiver un compte ou le MFA révoque les sessions ; `POST /admin/security/users/{id}/revoke-sessions` |
| Centre de sécurité | `GET /admin/security/overview` (échecs de connexion 24 h, comptes verrouillés, comptes plateforme sans MFA, clés actives ou expirant sous 30 jours, organisations désactivées), comptes verrouillés, déverrouillage, réinitialisation du MFA, événements filtrables et export CSV protégé contre l'injection de formules |
| Rapports | `GET /admin/reports/kyc` (statuts, risques, pays, jours, taux de vérification, délai moyen, JSON ou CSV, Sandbox exclu par défaut), `GET /admin/reports/organizations` |

⚠️ Le MFA est facultatif : il n'est pas imposé aux comptes plateforme (à décider). Les rôles et permissions sont définis dans le code, pas créables depuis une interface.

## 5. Facturation

| Fonction | Détail |
|---|---|
| Forfaits | `POST /admin/billing/plans` : frais mensuel et prix unitaires **par devise** (`XAF`, `XOF`, `EUR`, `USD`, `CAD`, `NGN`, `GHS`, `CDF`). **Aucun prix n'est défini par défaut** : la grille tarifaire reste une décision commerciale |
| Abonnements | `POST /admin/billing/subscriptions` : forfait, devise, taux de taxe ; un nouvel abonnement remplace l'actif |
| Consommation | événements facturables (`case_created`, `attempt`, `manual_review`, `extra_check`) selon la politique du parcours ; incidents techniques et Sandbox jamais facturés ; `GET /billing/consumption` donne l'estimation à l'organisation |
| Factures | génération en brouillon pour une période (une seule par période hors annulées), émission avec numéro `INV-AAAA-NNNNNN` sans trou et échéance à 30 jours, paiement, annulation (brouillon ou émise sans avoir) |
| Avoirs | `CN-AAAA-NNNNNN`, partiels ou totaux, plafonnés au montant de la facture |
| Visibilité | les administrateurs d'organisation voient leurs factures émises (jamais les brouillons) ; rôles `billing_manager` et `super_admin` pour la gestion |

⚠️ Pas de génération de PDF, pas de passerelle de paiement (le paiement est enregistré manuellement), calcul de taxe simple (un taux par abonnement), un abonnement de forfait mensuel facturé une fois par période générée.

## 6. E-mails

File `email_outbox` alimentée dans la transaction métier, envoi par SMTP (`EMAIL_BACKEND=smtp`) via la tâche de maintenance ou en arrière-plan, 5 tentatives. Modèles FR/EN : confirmation de demande, alerte interne, invitation d'administrateur, décision d'accès développeur. Mode `console` réservé au développement.
