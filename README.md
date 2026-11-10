# IZILens

Plateforme modulaire de KYC/KYB assistée par l'IA, construite autour d'un backend Python/FastAPI et d'un frontend React.

## Architecture

- `ocr-service/` : API et services backend (KYC, KYB, biométrie, OCR).
- `dashboard/` : application web React.
- `docs/` : documentation technique et fonctionnelle.
- `infrastructure/` : scripts et ressources de déploiement.
- `tests/` : tests transversaux.

## Démarrage

Voir `ocr-service/README.md` et `dashboard/README.md`.

Ne jamais versionner les fichiers `.env`, secrets, clés privées ou données personnelles réelles.
