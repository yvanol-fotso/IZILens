# LICENCES TIERCES ET SOURCES DE DONNÉES

**Projet :** IZILens
**Objet :** Inventaire des logiciels tiers, jeux de données et références externes utilisés ou envisagés.
**Dernière révision :** 13 novembre 2026

> L'inclusion d'une ressource dans ce document ne signifie pas qu'elle est intégrée à IZILens ni approuvée pour un usage commercial.

---

## 1. Dépendances logicielles

| Composant | Usage | Licence | Source |
|---|---|---|---|
| FastAPI | API REST | MIT | https://github.com/fastapi/fastapi |
| Uvicorn | Serveur ASGI | BSD-3-Clause | https://github.com/encode/uvicorn |
| Pydantic | Validation de données | MIT | https://github.com/pydantic/pydantic |
| Pydantic Settings | Configuration | MIT | https://github.com/pydantic/pydantic-settings |
| PaddlePaddle | Apprentissage profond | Apache-2.0 | https://github.com/PaddlePaddle/Paddle |
| PaddleOCR | OCR | Apache-2.0 | https://github.com/PaddlePaddle/PaddleOCR |
| OpenCV | Traitement d'images | Apache-2.0 | https://github.com/opencv/opencv |
| Pillow | Manipulation d'images | MIT-CMU | https://github.com/python-pillow/Pillow |
| Requests | Client HTTP | Apache-2.0 | https://github.com/psf/requests |
| HTTPX | Client HTTP et tests d'API | BSD-3-Clause | https://github.com/encode/httpx |
| Pytest | Tests automatisés | MIT | https://github.com/pytest-dev/pytest |
| python-multipart | Téléversement de fichiers | Apache-2.0 | https://github.com/Kludex/python-multipart |

Les mentions de droit d'auteur et les textes de licence doivent être conservés lors de la distribution. L'inventaire complet des dépendances transitives doit être généré depuis l'environnement installé avant toute publication.

## 2. Jeux de données

| Jeu de données | Éditeur | Contenu | Licence | Usage commercial |
|---|---|---|---|---|
| [Synthetic Cameroon National ID Card OCR](https://huggingface.co/datasets/thekfp/synthetic-cameroon-national-id-card-orc-dataset) | thekfp | ~60 000 cartes d'identité camerounaises synthétiques (texte OCR, champs extraits) | Non confirmée | En attente de vérification |
| [African ID Documents](https://huggingface.co/datasets/jonathansuru/african-id-documents) | jonathansuru | ~21 documents d'identité africains (images, champs structurés) | Non confirmée | En attente de vérification |
| [Africa Identity Fraud National ID](https://huggingface.co/datasets/electricsheepafrica/africa-identity-fraud-national-id) | Electric Sheep Africa | ~10 000 enregistrements (analyse de fraude) | MIT (métadonnées) | À vérifier : les droits des sources d'origine restent aux fournisseurs |
| [Indonesian ID Card Dummy](https://huggingface.co/datasets/cloverx-id/indonesian-id-card-dummy) | cloverx-id | ~24 000 cartes KTP synthétiques + sous-ensemble augmenté | CC BY 4.0 | Attribution requise ; échantillons négatifs tiers à vérifier |
| [Selfie and Official ID Photo](https://huggingface.co/datasets/AxonData/Selfie_and_Official_ID_Photo_Dataset) | AxonData | Selfies et photos d'identité (comparaison faciale) | CC BY 4.0 (échantillon public) | Version complète payante ; droits à l'image à vérifier |
| [MIDV-2020](https://l3i-share.univ-lr.fr/MIDV2020/midv2020.html) | Univ. La Rochelle (L3i) | 3 000 vidéos/scans/photos de faux documents (~124 Go) | Accès demandé, en attente | Non autorisé tant que la licence n'est pas validée |

**Notes :**
- Le dataset AxonData sert à la comparaison faciale uniquement ; il ne valide pas une détection de vivacité (liveness).
- MIDV-2020 impose de citer : K.B. Bulatov et al., *MIDV-2020: A Comprehensive Benchmark Dataset for Identity Document Analysis*, Computer Optics, 2021 ([article](https://arxiv.org/ftp/arxiv/papers/2107/2107.00396.pdf)).

## 3. Références externes (non intégrées)

- **identite-ts** (https://github.com/lau-sam/identite-ts) : référence technique, licence MIT à vérifier selon la version. Aucune intégration de code, hors dépendances d'exécution.
- **Image de test « Mohamed »** (https://x.com/Adesolive/status/1490447092795514888) : référence visuelle pour les tests. Droits de réutilisation non vérifiés ; redistribution commerciale interdite sans confirmation.

## 4. Exigences de conformité

Avant toute inclusion dans une version commerciale d'IZILens :

1. Vérifier la licence exacte de chaque ressource (logiciel, modèle, jeu de données, image).
2. Conserver les mentions de droit d'auteur et d'attribution.
3. Respecter les conditions de redistribution et de modification.
4. Vérifier l'usage commercial indépendamment de l'usage recherche/évaluation.
5. Examiner la provenance et les enjeux de vie privée des documents d'identité et images biométriques.
6. Documenter les versions et sources exactes.
7. Obtenir une autorisation écrite en cas de doute sur la licence ou la propriété.

## 5. Protection des données

- Stocker les jeux de test séparément des données de production.
- Ne jamais commiter de vrais documents d'identité ou échantillons biométriques dans un dépôt public.
- Contrôler l'accès aux jeux de données, images de test et poids de modèles.

Ce document doit être mis à jour à chaque ajout de dépendance, modèle, jeu de données ou ressource externe.