# IZI LENS — Dashboard (SvelteKit)

Site vitrine bilingue (FR/EN) + tableau de bord client + espace d'administration Kafintech, dans un seul projet.
Pile : SvelteKit 2 · Svelte 5 · TypeScript · SCSS par composant · `@lucide/svelte` · adaptateur Node.

## Démarrage

```bash
cd dashboard
npm install
cp .env.example .env        # renseignez BACKEND_SERVICE_URL (+ GOOGLE_* si besoin)
npm run dev                 # http://localhost:5173
npm run check && npm run build
```

Le backend (`../backend`) doit tourner sur `BACKEND_SERVICE_URL` (défaut `http://127.0.0.1:8000`).
Contrat des routes : [`docs/BACKEND_CONTRACT.md`](docs/BACKEND_CONTRACT.md).

## Organisation

```
src/
  app.css                   ← TOUTES les couleurs/rayons/typo (changer le thème = modifier ce fichier)
  hooks.server.ts           ← langue, thème, session JWT (refresh transparent), garde-fous
  content/{fr,en}/*.md      ← pages légales en Markdown (éditables / régénérables par IA)
  lib/
    components/<route>/     ← composants PROPRES à chaque route + index.ts
      home/ auth/ privacy/ terms/ cookies/ dashboard/ verifications/ liveness/
      biometrics/ aml/ analytics/ api-keys/ team/ audit/ settings/ developers/ admin/
      shared/               ← composants réutilisables (Button, Input, Modal, Table, Markdown…)
      layout/               ← Navbar, Footer, CookieBanner, Sidebar, Topbar
    actions/                ← clickOutside, copy, reveal, focusTrap
    stores/                 ← toast, ui, consent (cookies versionnés)
    config/                 ← navigation, modules, permissions, site
    i18n/                   ← fr.ts (source des clés) · en.ts (même forme, vérifiée par TypeScript)
    server/                 ← backend, endpoints, api, proxy, markdown, analytics
      auth/                 ← config · session · google · policy · service
  routes/
    (marketing)/            ← accueil, /privacy, /terms, /cookies
    login  register
    app/                    ← dashboard (verifications, liveness, biometrics, aml, analytics,
                              api-keys, team, audit, settings, developers)
    app/admin/              ← super_admin Kafintech (tenants, members, announcements, system)
    verify/liveness/[token] ← parcours mobile (lien / QR)
    api/auth/{login,logout,refresh,session,oauth}   api/v1/[...path]   api/admin/[...path]
```

## Authentification
- **JWT e-mail + mot de passe** : action de `/login` → cookies `httpOnly` (`izi_at`, `izi_rt`), refresh automatique dans `hooks.server.ts`.
- **Continuer avec Google (OIDC, code + PKCE + state + nonce)** : `/api/auth/oauth?provider=google`. Le backend vérifie l'`id_token` et émet ses JWT (voir contrat).
- Garde-fous centralisés dans `lib/server/auth/policy.ts` : `/app/*` connecté, `/app/admin/*` super_admin, `/login` si déjà connecté.
- Rôles : `super_admin`, `admin`, `reviewer`, `viewer`, `integration` (`lib/config/permissions.ts`).

## Multilingue
Langue = cookie `izi_locale` > `Accept-Language` > FR. Changer de langue ne change pas l'URL : la page équivalente existe toujours.
Ajouter une langue : `i18n/locales.ts`, un fichier typé sur `fr.ts`, et `src/content/<lang>/`.

## Conformité à la spec « Global Website Elements »
Pied de page à 6 zones, sélecteur de langue en en-tête **et** en pied de page, bannière cookies (Accepter/Refuser de même poids), centre de préférences à 6 catégories avec version + horodatage, aucun traceur chargé sans consentement (`utils/tracking.ts#onConsent`), lien « Préférences de cookies » permanent, liens non publiés non rendus (`config/navigation.ts`, `config/site.ts`).

## À compléter avant la mise en production
- Contenus de chaque page (dossier Drive « CONTENUS POUR CHAQUE PAGE ») → `src/lib/i18n/*.ts`.
- URL officielles des réseaux sociaux (`config/site.ts`, `url: null` = icône masquée).
- Nom légal exact (« Kafintech Group » / « Inc. ») et adresse à vérifier.
- Textes légaux : brouillons à valider par un juriste (marqués *[À compléter]*).
- Modules **liveness, biométrie, AML** : interface prête, backend non branché.
- `PUBLIC_DOCS_URL` : tant qu'il est vide, le lien « Développeurs » n'est pas affiché.
