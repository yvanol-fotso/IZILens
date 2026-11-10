#!/usr/bin/env python3
"""
Initialisation de l'architecture IZILens.
À exécuter depuis la racine du dépôt (le dossier qui contient LICENSE).
Le script crée les dossiers et fichiers manquants sans écraser les fichiers existants.
"""

from pathlib import Path

ROOT = Path.cwd()

FILES = {
    # Racine
    ".gitignore": """# Python
__pycache__/
*.py[cod]
.venv/
venv/
.env
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Node
node_modules/
dist/
build/
.vite/

# IDE / OS
.vscode/
.idea/
.DS_Store
Thumbs.db
""",
    ".env.example": """# Copier ce fichier vers .env et renseigner les valeurs localement.
APP_NAME=IZILens
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
DATABASE_URL=sqlite:///./izilens_dev.db
SECRET_KEY=replace-this-with-a-long-random-secret
""",
    "README.md": """# IZILens

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
""",
    "THIRD_PARTY_LICENSES.md": """# Third-party licenses

Lister ici les bibliothèques et composants tiers utilisés par IZILens, avec leur version et leur licence.
""",

    # Backend
    "ocr-service/app/__init__.py": "",
    "ocr-service/app/main.py": """from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, version="0.1.0")
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.APP_NAME}
""",
    "ocr-service/app/core/__init__.py": "",
    "ocr-service/app/core/config.py": """import os


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "IZILens API")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./izilens_dev.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-only-change-me")


settings = Settings()
""",
    "ocr-service/app/core/security.py": """\"\"\"Fonctions de sécurité à compléter avant toute mise en production.\"\"\"


def get_password_hash(password: str) -> str:
    raise NotImplementedError("Brancher une bibliothèque de hachage adaptée (Argon2/bcrypt).")


def verify_password(plain_password: str, password_hash: str) -> bool:
    raise NotImplementedError("Implémenter la vérification du mot de passe.")
""",
    "ocr-service/app/core/database.py": """\"\"\"Point de centralisation de la configuration de base de données.

La connexion SQLAlchemy et la gestion des sessions seront ajoutées dans une étape dédiée.
\"\"\"
""",
    "ocr-service/app/core/exceptions.py": """class IZILensError(Exception):
    \"\"\"Exception métier de base pour IZILens.\"\"\"
""",
    "ocr-service/app/core/dependencies.py": """\"\"\"Dépendances FastAPI partagées (authentification, base de données, etc.).\"\"\"
""",
    "ocr-service/app/api/__init__.py": "",
    "ocr-service/app/api/v1/__init__.py": "",
    "ocr-service/app/api/v1/router.py": """from fastapi import APIRouter

from app.api.v1.endpoints import router as health_router
from app.modules.kyc.routes import router as kyc_router
from app.modules.kyb.routes import router as kyb_router
from app.modules.biometrics.liveness.routes import router as liveness_router
from app.modules.biometrics.face_match.routes import router as face_match_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(kyc_router, prefix="/kyc", tags=["kyc"])
api_router.include_router(kyb_router, prefix="/kyb", tags=["kyb"])
api_router.include_router(liveness_router, prefix="/biometrics/liveness", tags=["liveness"])
api_router.include_router(face_match_router, prefix="/biometrics/face-match", tags=["face-match"])
""",
    "ocr-service/app/api/v1/endpoints.py": """from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def api_root() -> dict[str, str]:
    return {"message": "IZILens API v1"}
""",
    "ocr-service/app/modules/__init__.py": "",
    "ocr-service/app/modules/kyc/__init__.py": "",
    "ocr-service/app/modules/kyc/routes.py": """from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def kyc_status() -> dict[str, str]:
    return {"module": "kyc", "status": "initialized"}
""",
    "ocr-service/app/modules/kyc/service.py": """\"\"\"Logique métier KYC à implémenter.\"\"\"


class KYCService:
    pass
""",
    "ocr-service/app/modules/kyc/schemas.py": """from pydantic import BaseModel


class KYCCheckRequest(BaseModel):
    document_type: str
""",
    "ocr-service/app/modules/kyc/models.py": """\"\"\"Modèles de données KYC à définir avec l'ORM retenu.\"\"\"
""",
    "ocr-service/app/modules/kyc/repository.py": """\"\"\"Accès aux données KYC à implémenter.\"\"\"


class KYCRepository:
    pass
""",
    "ocr-service/app/modules/kyb/__init__.py": "",
    "ocr-service/app/modules/kyb/routes.py": """from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def kyb_status() -> dict[str, str]:
    return {"module": "kyb", "status": "initialized"}
""",
    "ocr-service/app/modules/kyb/service.py": """\"\"\"Logique métier KYB à implémenter.\"\"\"


class KYBService:
    pass
""",
    "ocr-service/app/modules/kyb/schemas.py": """from pydantic import BaseModel


class KYBCheckRequest(BaseModel):
    organization_name: str
""",
    "ocr-service/app/modules/kyb/models.py": """\"\"\"Modèles de données KYB à définir avec l'ORM retenu.\"\"\"
""",
    "ocr-service/app/modules/kyb/repository.py": """\"\"\"Accès aux données KYB à implémenter.\"\"\"


class KYBRepository:
    pass
""",
    "ocr-service/app/modules/biometrics/__init__.py": "",
    "ocr-service/app/modules/biometrics/liveness/__init__.py": "",
    "ocr-service/app/modules/biometrics/liveness/routes.py": """from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def liveness_status() -> dict[str, str]:
    return {"module": "liveness", "status": "initialized"}
""",
    "ocr-service/app/modules/biometrics/liveness/service.py": """\"\"\"Service de détection de vivacité à implémenter.\"\"\"
""",
    "ocr-service/app/modules/biometrics/liveness/schemas.py": """from pydantic import BaseModel


class LivenessRequest(BaseModel):
    session_id: str
""",
    "ocr-service/app/modules/biometrics/liveness/models.py": """\"\"\"Modèles de données pour la détection de vivacité.\"\"\"
""",
    "ocr-service/app/modules/biometrics/face_match/__init__.py": "",
    "ocr-service/app/modules/biometrics/face_match/routes.py": """from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def face_match_status() -> dict[str, str]:
    return {"module": "face_match", "status": "initialized"}
""",
    "ocr-service/app/modules/biometrics/face_match/service.py": """\"\"\"Service de comparaison faciale à implémenter.\"\"\"
""",
    "ocr-service/app/modules/biometrics/face_match/schemas.py": """from pydantic import BaseModel


class FaceMatchRequest(BaseModel):
    reference_image_id: str
    capture_image_id: str
""",
    "ocr-service/app/modules/biometrics/face_match/models.py": """\"\"\"Modèles de données pour la comparaison faciale.\"\"\"
""",
    "ocr-service/app/shared/__init__.py": "",
    "ocr-service/app/shared/ocr/.gitkeep": "",
    "ocr-service/app/shared/image_processing/.gitkeep": "",
    "ocr-service/app/shared/document_processing/.gitkeep": "",
    "ocr-service/app/shared/storage/.gitkeep": "",
    "ocr-service/app/shared/validation/.gitkeep": "",
    "ocr-service/app/shared/notifications/.gitkeep": "",
    "ocr-service/app/infrastructure/__init__.py": "",
    "ocr-service/app/infrastructure/database/.gitkeep": "",
    "ocr-service/app/infrastructure/object_storage/.gitkeep": "",
    "ocr-service/app/infrastructure/task_queue/.gitkeep": "",
    "ocr-service/app/infrastructure/logging/.gitkeep": "",
    "ocr-service/app/common/__init__.py": "",
    "ocr-service/app/common/constants.py": """APP_VERSION = "0.1.0"
""",
    "ocr-service/app/common/enums.py": """from enum import StrEnum


class VerificationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
""",
    "ocr-service/tests/unit/.gitkeep": "",
    "ocr-service/tests/integration/.gitkeep": "",
    "ocr-service/tests/e2e/.gitkeep": "",
    "ocr-service/scripts/.gitkeep": "",
    "ocr-service/requirements.txt": """fastapi>=0.115,<1.0
uvicorn[standard]>=0.30,<1.0
pydantic>=2.8,<3.0
pydantic-settings>=2.4,<3.0
pytest>=8.0,<9.0
httpx>=0.27,<1.0
""",
    "ocr-service/alembic.ini": """[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = sqlite:///./izilens_dev.db
""",
    "ocr-service/.env.example": """APP_NAME=IZILens API
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
DATABASE_URL=sqlite:///./izilens_dev.db
SECRET_KEY=replace-with-a-secure-random-value
""",
    "ocr-service/README.md": """# IZILens OCR Service

Backend modulaire FastAPI. Les modules et routes présents sont des squelettes d'initialisation : la logique KYC/KYB, OCR et biométrique reste à développer.

## Installation (Windows CMD)

```bat
cd ocr-service
py -m venv .venv
.venv\\Scripts\\activate
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

API : http://127.0.0.1:8000  
Documentation interactive : http://127.0.0.1:8000/docs
""",
    "ocr-service/migrations/.gitkeep": "",

    # Frontend
    "dashboard/public/.gitkeep": "",
    "dashboard/src/assets/.gitkeep": "",
    "dashboard/src/components/ui/.gitkeep": "",
    "dashboard/src/components/layout/.gitkeep": "",
    "dashboard/src/components/shared/.gitkeep": "",
    "dashboard/src/pages/auth/.gitkeep": "",
    "dashboard/src/pages/dashboard/.gitkeep": "",
    "dashboard/src/pages/kyc/.gitkeep": "",
    "dashboard/src/pages/kyb/.gitkeep": "",
    "dashboard/src/pages/biometrics/.gitkeep": "",
    "dashboard/src/pages/users/.gitkeep": "",
    "dashboard/src/pages/settings/.gitkeep": "",
    "dashboard/src/services/api.ts": """// Client HTTP centralisé à implémenter.
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
""",
    "dashboard/src/services/auth.service.ts": "export {};\n",
    "dashboard/src/services/kyc.service.ts": "export {};\n",
    "dashboard/src/services/kyb.service.ts": "export {};\n",
    "dashboard/src/services/biometrics.service.ts": "export {};\n",
    "dashboard/src/hooks/.gitkeep": "",
    "dashboard/src/contexts/.gitkeep": "",
    "dashboard/src/routes/.gitkeep": "",
    "dashboard/src/types/.gitkeep": "",
    "dashboard/src/utils/.gitkeep": "",
    "dashboard/package.json": """{
  "name": "izilens-dashboard",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "typescript": "^5.5.4",
    "vite": "^5.4.0"
  }
}
""",
    "dashboard/README.md": """# IZILens Dashboard

Frontend React + TypeScript. Le socle est initialisé ; TailwindCSS et les écrans métier seront ajoutés dans une étape dédiée.

## Installation

```bash
npm install
npm run dev
```
""",

    # Documentation
    "docs/architecture/system-architecture.md": "# Architecture système IZILens\n\nVue d'ensemble des composants et de leurs interactions.\n",
    "docs/architecture/backend-architecture.md": "# Architecture backend\n\nBackend FastAPI organisé en modules métier.\n",
    "docs/architecture/frontend-architecture.md": "# Architecture frontend\n\nApplication React organisée par composants, pages et services.\n",
    "docs/architecture/modular-monolith.md": "# Architecture modulaire\n\nPrincipes de séparation des modules dans un monolithe modulaire.\n",
    "docs/api/api-conventions.md": "# Conventions API\n\nConventions de routes, schémas, erreurs et versionnement.\n",
    "docs/database/database-schema.md": "# Schéma de base de données\n\nÀ compléter lors de la conception du modèle de données.\n",
    "docs/security/security-guidelines.md": "# Sécurité\n\nNe jamais committer de secrets ou de données personnelles réelles. Définir ici les contrôles de sécurité.\n",
    "docs/specifications/kyc.md": "# Spécification KYC\n\nÀ compléter.\n",
    "docs/specifications/kyb.md": "# Spécification KYB\n\nÀ compléter.\n",
    "docs/specifications/biometrics.md": "# Spécification biométrie\n\nÀ compléter.\n",
    "docs/deployment/deployment-guide.md": "# Guide de déploiement\n\nÀ compléter.\n",

    # Infrastructure et tests transversaux
    "infrastructure/storage/.gitkeep": "",
    "infrastructure/scripts/.gitkeep": "",
    "infrastructure/deployment/.gitkeep": "",
    "tests/.gitkeep": "",
}

def main() -> None:
    print(f"Initialisation de IZILens dans : {ROOT}")
    created = 0
    skipped = 0

    for relative_path, content in FILES.items():
        destination = ROOT / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            print(f"[CONSERVÉ] {relative_path}")
            skipped += 1
            continue

        destination.write_text(content, encoding="utf-8", newline="\n")
        print(f"[CRÉÉ]     {relative_path}")
        created += 1

    print("\nInitialisation terminée.")
    print(f"Fichiers créés : {created}")
    print(f"Fichiers existants conservés : {skipped}")
    print("\nIMPORTANT : les fichiers générés sont des squelettes de départ,")
    print("pas une implémentation complète des fonctionnalités KYC/KYB.")

if __name__ == "__main__":
    main()
