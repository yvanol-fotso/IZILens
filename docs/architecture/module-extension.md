# Étendre sans casser : liveness (module 2) et KYB

Le module KYC a été conçu pour que le module 2 se branche **sans migration de données** ni modification du moteur existant.

## Ajouter la biométrie (face match, liveness)

1. **Contrôles génériques** : la table `kyc_checks` stocke un contrôle par ligne (`check_type`, `status`, `details`, `engine`, `version`). `face_match` et `liveness` sont déjà des types connus ; aucune colonne ni table à ajouter.
2. **Déclenchement** : l'exigence est dans `kyc_journeys.required_checks`. Ajouter `face_match` / `liveness` à un parcours suffit : le dossier attend (`in_progress`, motif `AWAITING_FACE_MATCH` puis `AWAITING_LIVENESS`).
3. **Résultats** : le module 2 appelle `record_external_check(db, case, actor, check_type, status, details, engine, version)` dans `app/modules/kyc/service.py` (ou `POST /admin/kyc/cases/{id}/checks` en dehors du processus). Le service enregistre le contrôle, facture `extra_check`, historise l'événement et réévalue le dossier.
4. **Règles** : un `face_match` ou `liveness` en échec ou non concluant déclenche `biometric_failure` (revue humaine par défaut, configurable) ; un liveness en échec n'est jamais masqué par un face match positif.
5. **Garde de décision** : un dossier ne peut pas passer à `verified` tant qu'un contrôle biométrique requis n'est pas `passed`, sauf exception formelle de la plateforme, tracée.
6. **Portrait du document** : les images restent dans `kyc_documents` (chiffrées) ; le module 2 lit le portrait via `repository.get_case` et le stockage chiffré, sans nouveau schéma.
7. **À créer côté module 2 seulement** : ses propres tables de captures et de tentatives biométriques (préfixe `bio_`), et ses routes de capture.

## Ajouter KYB

Réutilisables sans changement : `organizations` (isolation, modules souscrits : `kyb` est déjà un module connu), `users` et rôles, `api_keys`, `audit_logs`, `webhooks`, `billing_events`, file de revue et schéma d'états `states.py` (à dupliquer pour les statuts KYB propres).
À créer : `app/modules/kyb/` avec ses propres modèles (dossier entreprise, personnes liées, propriété), ses règles et ses routes ; une migration Alembic dédiée.
Les personnes liées se rattachent à un dossier KYC par identifiant, sans fusionner les données KYB et KYC.

## Principes à conserver

- Un contrôle = une ligne ; la valeur courante est le dernier résultat par type.
- Les résultats de contrôle ne contiennent jamais de donnée personnelle ; ils vont dans `details` en JSON non chiffré.
- Toute évolution de statut passe par `transition()`, qui valide, historise, facture et notifie.
- Les paramètres métier restent configurables (parcours), jamais codés en dur.
