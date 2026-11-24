# KYC V1 – Traçabilité des exigences et des critères d'acceptation

Ce document relie chaque exigence du cahier des charges « KYC V1 – version finale consolidée » à son implémentation et à un test automatisé.
Légende : ✅ couvert par le backend et testé · 🟡 couvert côté API, l'interface graphique relève du front-end · 🔶 préparé, dépend du module 2 (Biométrie/Liveness) · ⚠️ limite connue.

Les tests référencés sont dans `backend/tests/` (`unit/` et `integration/`). Ils s'exécutent avec `pytest` (SQLite) et sur PostgreSQL avec `TEST_DATABASE_URL`.

## 1. Fonctionnalités KYC-01 à KYC-19

| Réf. | Exigence | État | Implémentation | Tests |
|---|---|---|---|---|
| KYC-01 | Dossier unique par demande, lié au client et à sa référence | ✅ | `POST /kyc/cases`, référence unique par organisation | `test_creation_with_documents_runs_the_whole_pipeline`, `test_reference_rules_and_tenant_isolation` |
| KYC-02 | Collecte des informations personnelles | ✅ | Identité déclarée (nom, prénoms, date de naissance, nationalité) stockée chiffrée, séparée des données lues | `test_declared_identity_is_required_before_the_comparison`, `test_declared_identity_validation` |
| KYC-03 | Pays et documents réellement pris en charge | ✅ | Matrice `kyc_document_coverage` (planned, testing, supported, disabled) ; `GET /kyc/coverage` ne renvoie que `supported` et liste les lacunes | `test_only_validated_documents_are_presented_and_gaps_are_reported`, `test_country_and_document_are_mandatory_and_must_be_supported` |
| KYC-04 | Capture, dépôt et contrôle de qualité | ✅ | Validation du contenu réel, résolution minimale, netteté, ré-encodage sans métadonnées | `test_poor_image_requests_a_recapture_and_history_is_preserved`, `test_invalid_uploads_never_create_a_case`, `test_oversized_file_is_rejected`, `test_files_storage_ocr` |
| KYC-05 | Lecture des données par IZI LENS | ✅ | PaddleOCR interne, extraction par étiquettes avec repli positionnel | `test_extractor`, `test_creation_with_documents_runs_the_whole_pipeline` |
| KYC-06 | Comparaison déclaré / lu, avec provenance | ✅ | Contrôle `declared_match` ; les valeurs ne sont jamais recopiées dans les résultats de contrôle | `test_matching_analysis`, `test_discrepancy_between_declared_and_read_data_is_classified` |
| KYC-07 | Contrôles documentaires disponibles | ✅ ⚠️ | Qualité, reconnaissance du type, lecture, expiration, doublons d'image et d'identité. ⚠️ Pas d'analyse d'authenticité visuelle (falsification) en V1 : elle n'est pas annoncée | `test_duplicates_are_flagged_and_sent_to_review`, `test_expiry_is_checked_only_when_it_can_be_read` |
| KYC-08 | Biométrie conditionnelle | 🔶 | `required_checks` du parcours peut exiger `face_match` et `liveness` ; le dossier attend (`in_progress`, `AWAITING_*`) et le module 2 pousse ses résultats via le même mécanisme de contrôles | `test_mandatory_biometrics_hold_the_case_and_gate_the_decision`, `test_biometric_results_complete_the_flow_without_changing_the_document_data` |
| KYC-09 | Décision automatique uniquement sur critères approuvés | ✅ | Moteur de règles `rules.evaluate`, auto-décision désactivée par défaut et configurable | `test_rules`, `test_clear_case_is_verified_automatically_when_the_journey_allows_it` |
| KYC-10 | Revue humaine des cas ambigus | ✅ | File de revue, assignation, décision motivée, demande de complément, deux équipes (client / IZI LENS) | `test_review_queue_assignment_and_decision_rules`, `test_two_review_teams_share_the_work_according_to_the_journey` |
| KYC-11 | Tentatives et reprises | ✅ | Recapture, correction de données, reprise technique ; limites par parcours, exception contrôlée par la plateforme | `test_attempt_limits_then_controlled_exception`, `test_data_correction_attempts_are_limited`, `test_technical_retries_are_limited` |
| KYC-12 | Parcours hébergé | 🟡 | `/kyc/session/*` : consentement, identité, dépôt, résultat, consignes localisées ; l'écran est réalisé par le front-end | `test_hosted_journey_end_to_end_in_french`, `test_hosted_journey_in_english_and_recapture_guidance` |
| KYC-13 | Intégration API/SDK | 🟡 | API REST documentée en OpenAPI (`/docs`) ; un SDK se génère depuis le schéma OpenAPI (non livré) | `test_api_and_hosted_modes_give_the_same_business_result` |
| KYC-14 | Statuts, résultats, notifications | ✅ 🟡 | Statuts du cahier des charges, webhooks signés ; le tableau de bord est réalisé par le front-end | `test_status_changes_are_signed_delivered_and_free_of_personal_data`, `test_failed_deliveries_are_retried_then_marked_failed` |
| KYC-15 | Traçabilité | ✅ | Historique du dossier (`kyc_events`) et journal d'audit en ajout seul, sans donnée personnelle | `test_audit_and_events_contain_no_personal_data`, `test_decision_requirements_and_trace` |
| KYC-16 | Pas d'accès croisé entre clients | ✅ | Filtre par organisation sur chaque lecture, projection par rôle, données masquées pour les lecteurs | `test_reference_rules_and_tenant_isolation`, `test_field_level_visibility_by_role` |
| KYC-17 | Français et anglais | ✅ 🟡 | Libellés, motifs, signaux et consignes en FR/EN (`?lang=` ou langue du dossier) ; `GET /kyc/messages` fournit le catalogue | `test_messages_follow_the_requested_language`, `test_every_status_and_reason_has_french_and_english_text` |
| KYC-18 | Expiration configurable | ✅ | `expiry_hours` par parcours, expiration paresseuse et tâche `maintenance` | `test_expired_request_is_neither_verified_nor_refused`, `test_maintenance_expires_due_cases` |
| KYC-19 | Facturation | ✅ | Registre `billing_events` ; facturabilité selon la politique du parcours | `test_billing_counts_requests_and_follows_the_approved_policy`, `test_technical_failures_are_never_billable_even_when_attempts_are` |

## 2. Règles métier R-01 à R-17

| Règle | État | Où / comment | Test |
|---|---|---|---|
| R-01 Pays connu avant les règles documentaires | ✅ | `country_code` et `document_type` obligatoires | `test_country_and_document_are_mandatory_and_must_be_supported` |
| R-02 Document non supporté jamais présenté comme vérifiable | ✅ | Seul `supported` est proposé et accepté | `test_only_validated_documents_are_presented_and_gaps_are_reported` |
| R-03 Image insuffisante : nouvelle capture si autorisée | ✅ | `ACTION_REQUIRED` / `IMAGE_QUALITY` tant qu'il reste des reprises | `test_poor_image_requests_a_recapture_and_history_is_preserved` |
| R-04 Informations obligatoires avant les contrôles dépendants | ✅ | `DECLARED_IDENTITY_REQUIRED` ; le parcours hébergé l'impose avant le dépôt | `test_declared_identity_is_required_before_the_comparison`, `test_hosted_journey_end_to_end_in_french` |
| R-05 Divergences identifiées et classées | ✅ | `match`, `partial`, `mismatch` par champ | `test_name_matching_primitives`, `test_discrepancy_between_declared_and_read_data_is_classified` |
| R-06 Expiration du document signalée si fiable | ✅ | Contrôle `expiry` : `not_run` tant que la date n'est pas lisible | `test_expiry_is_checked_only_when_it_can_be_read` |
| R-07 Ambigu jamais validé automatiquement | ✅ | Tout déclencheur ou contrôle non réussi mène à la revue | `test_ambiguity_goes_to_review_and_rules_can_reject`, `test_required_check_not_passed_is_never_silently_verified` |
| R-08 Incident technique ≠ échec de vérification | ✅ | `FAILED` avec `failure_kind=technical`, jamais `NOT_VERIFIED` ; non facturé | `test_technical_incident_is_not_a_refusal_and_can_be_retried`, `test_a_technical_failure_cannot_become_a_refusal_directly` |
| R-09 Tentatives configurables, exceptions contrôlées | ✅ | `max_attempts` par parcours ; `grant-attempts` réservé à la plateforme | `test_attempt_limits_then_controlled_exception` |
| R-10 Revue humaine ≠ vérifié | ✅ | `MANUAL_REVIEW` est un statut distinct, non final | `test_creation_with_documents_runs_the_whole_pipeline` |
| R-11 Contrôle biométrique obligatoire non satisfait bloque la validation | 🔶 | Moteur de règles et garde de décision ; exception formelle plateforme tracée | `test_mandatory_biometrics_hold_the_case_and_gate_the_decision`, `test_liveness_failure_cannot_be_hidden_by_a_positive_face_match` |
| R-12 Nouvelle demande = nouvelle vérification ; reprise = même historique | ✅ | Tentatives numérotées, documents conservés, états finaux immuables | `test_poor_image_requests_a_recapture_and_history_is_preserved`, `test_every_status_is_described_and_terminal_states_are_final` |
| R-13 Facturation selon politique approuvée | ✅ | Politique par parcours, valeurs marquées « à valider » | `test_billing_counts_requests_and_follows_the_approved_policy` |
| R-14 Demande expirée ≠ validation ni refus | ✅ | Statut `EXPIRED`, message dédié | `test_expired_request_is_neither_verified_nor_refused` |
| R-15 Accès limité aux dossiers autorisés | ✅ | Isolation par organisation, rôles, modules souscrits | `test_reference_rules_and_tenant_isolation`, `test_module_not_enabled_blocks_kyc` |
| R-16 Résultat KYC ≠ approbation de conformité complète | ✅ | `scope` : contrôles exécutés, non exécutés, avertissement FR/EN | `test_hosted_journey_end_to_end_in_french` |
| R-17 Aucun fournisseur externe de vérification | ✅ | OCR et règles internes ; aucun appel sortant sauf webhooks du client et Google (connexion) | — |

## 3. Critères d'acceptation (section 14)

| # | Critère | État | Preuve |
|---|---|---|---|
| 1 | Créer et retrouver une demande | ✅ | `test_creation_with_documents_runs_the_whole_pipeline`, `test_listing_filters_pagination_and_stats` |
| 2 | Parcours hébergé et API cohérents | ✅ 🟡 | `test_api_and_hosted_modes_give_the_same_business_result` |
| 3 | Seuls les documents validés sont proposés | ✅ | `test_only_validated_documents_are_presented_and_gaps_are_reported` |
| 4 | Déclaré distinct de lu | ✅ | `test_declared_and_read_values_stay_separate_and_are_not_leaked_in_check_details` |
| 5 | Image illisible / donnée manquante → action adaptée | ✅ | `test_poor_image_requests_a_recapture_and_history_is_preserved`, `test_recapture_requested_while_attempts_remain_then_review` |
| 6 | Incohérence, document expiré, incertain suivent les règles | ✅ | `test_ambiguity_goes_to_review_and_rules_can_reject` |
| 7 | Contrôles biométriques obligatoires déclenchés | 🔶 | `test_mandatory_biometrics_hold_the_case_and_gate_the_decision` |
| 8 | Incident technique distinct d'un refus | ✅ | `test_technical_incident_is_not_a_refusal_and_can_be_retried` |
| 9 | Cas ambigus assignés à un analyste, décision tracée | ✅ | `test_review_queue_assignment_and_decision_rules`, `test_decision_requirements_and_trace` |
| 10 | Tentatives, expirations, facturation conformes aux paramètres | ✅ | tests des sections KYC-11, 18, 19 |
| 11 | Clients limités à leurs dossiers et champs | ✅ | `test_field_level_visibility_by_role`, `test_reference_rules_and_tenant_isolation` |
| 12 | Statuts, résultats, notifications cohérents et documentés | ✅ | `test_states_i18n`, tests webhooks, section 4 de ce document |
| 13 | Interfaces et instructions FR/EN | ✅ 🟡 | `test_messages_follow_the_requested_language`, `test_hosted_journey_in_english_and_recapture_guidance` |
| 14 | Scénarios nominaux, limites, reprises, erreurs testés | ✅ | 250 tests (`pytest`) |
| 15 | Fonctionne sans fournisseur KYC externe | ✅ | R-17 |

## 4. Statuts et transitions

`created` → `in_progress` → `processing` → `manual_review` | `verified` | `not_verified` ; `action_required` (nouvelle action de la personne) ; `failed` (incident technique, reprise possible) ; `expired` (sans achèvement).
États finaux : `verified`, `not_verified`, `expired`. Le diagramme complet est dans `backend/app/modules/kyc/states.py` et testé dans `test_states_i18n`.

| Ancien (V1 initiale) | Nouveau |
|---|---|
| `processing` | `processing` |
| `pending_review` | `manual_review` |
| `approved` | `verified` |
| `rejected` | `not_verified` |
| `failed` | `failed` (avec `failure_kind: "technical"`) |
| — | `created`, `in_progress`, `action_required`, `expired` |

## 5. Paramètres à arbitrer (non inventés)

Le cahier des charges interdit de fixer ces valeurs sans validation. Le produit les expose comme paramètres de parcours ; les valeurs ci-dessous sont **provisoires** (`parameters_validated = false`) jusqu'à validation par Kafintech via `PATCH /admin/kyc/journeys/{id}`.

| Paramètre | Valeur provisoire | Qui valide |
|---|---|---|
| Tentatives de recapture / correction / reprise technique | 3 / 2 / 3 | Conformité / produit |
| Expiration d'une demande | 72 h | Produit |
| Auto-décision | désactivée | Conformité |
| Équipe de revue | `either` (client ou IZI LENS) | Contrat client |
| Seuils OCR et de correspondance des noms | 0,90 / 0,90 / 0,75 | Conformité |
| Règles de décision (mineur, divergence, doublon, expiré…) | mineur → refus ; autres → revue | Conformité |
| Événements facturables | demande seule | Direction / commercial |
| Durée de conservation des documents | non implémentée (à définir) | Juridique |
| Documents supportés par pays | CNI Cameroun (statut `testing`) | Produit, après jeu de test |

## 6. Limites connues

- Aucune analyse d'authenticité visuelle (falsification) : seuls la cohérence, la qualité, l'expiration et les doublons sont contrôlés.
- Seule la CNI camerounaise (recto) est lue ; le verso est stocké mais non lu.
- Le module 2 (visage, présence réelle) n'est pas implémenté : le KYC attend ses résultats lorsqu'un parcours les exige.
- Durées de conservation et suppression des données : à définir avec le juridique avant production.
- Limiteur de débit et traitement OCR sont par processus ; Redis et une file de tâches seront nécessaires pour monter en charge.
