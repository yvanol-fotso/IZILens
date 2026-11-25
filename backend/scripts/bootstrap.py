"""Initialise la plateforme : parcours par défaut, super administrateur et, avec --demo, une organisation de démonstration.

Usage : python scripts/bootstrap.py --email admin@izilens.com [--demo]
"""

import argparse
import getpass
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app import models_registry  # noqa: E402,F401
from app.common.enums import UserRole  # noqa: E402
from app.core.database import session_scope  # noqa: E402
from app.core.principal import Principal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.modules.api_keys.schemas import ApiKeyCreate  # noqa: E402
from app.modules.api_keys.service import create_api_key  # noqa: E402
from app.modules.kyc.journeys import ensure_platform_defaults  # noqa: E402
from app.modules.organizations.models import Organization  # noqa: E402
from app.modules.users.models import User  # noqa: E402
from app.modules.users.schemas import validate_password_strength  # noqa: E402


def ensure_user(db, *, email: str, full_name: str, role: UserRole, password: str, organization_id=None) -> User | None:
    if db.scalar(select(User).where(User.email == email)):
        print(f"= {email} existe déjà, ignoré")
        return None
    user = User(
        email=email, full_name=full_name, role=role, organization_id=organization_id, password_hash=hash_password(password)
    )
    db.add(user)
    db.flush()
    return user


def new_password() -> str:
    return secrets.token_urlsafe(12) + "A1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--email", required=True, help="Email du super administrateur")
    parser.add_argument(
        "--demo", action="store_true", help="Crée une organisation de démonstration et valide la couverture CNI Cameroun"
    )
    args = parser.parse_args()

    password = getpass.getpass("Mot de passe du super administrateur (12 caractères min.) : ")
    validate_password_strength(password)

    with session_scope() as db:
        journey = ensure_platform_defaults(db, validate_coverage=args.demo)
        print(f"+ parcours plateforme : {journey.code} (paramètres à valider : {not journey.parameters_validated})")
        if args.demo:
            print("+ couverture CNI Cameroun marquée « supported » (démonstration uniquement)")
        ensure_user(db, email=args.email.lower(), full_name="Super Admin", role=UserRole.SUPER_ADMIN, password=password)
        print(f"+ super administrateur : {args.email.lower()}")

        if args.demo:
            organization = db.scalar(select(Organization).where(Organization.slug == "demo-bank"))
            if organization is None:
                organization = Organization(name="Demo Bank", slug="demo-bank", enabled_modules=["kyc", "api"])
                db.add(organization)
                db.flush()
            created: dict[str, tuple[User | None, str]] = {}
            for key, email, name, role, org_id in (
                ("admin", "admin@demo-bank.com", "Admin Demo", UserRole.ADMIN, organization.id),
                ("reviewer", "reviewer@demo-bank.com", "Reviewer Demo", UserRole.REVIEWER, organization.id),
                ("viewer", "viewer@demo-bank.com", "Viewer Demo", UserRole.VIEWER, organization.id),
                ("compliance", "compliance@izilens.com", "Conformité IZI LENS", UserRole.PLATFORM_COMPLIANCE, None),
            ):
                pwd = new_password()
                created[key] = (
                    ensure_user(db, email=email, full_name=name, role=role, password=pwd, organization_id=org_id),
                    pwd,
                )
            db.commit()
            print(f"+ organisation de démonstration : {organization.name} (modules : {', '.join(organization.enabled_modules)})")
            for key, email in (
                ("admin", "admin@demo-bank.com"),
                ("reviewer", "reviewer@demo-bank.com"),
                ("viewer", "viewer@demo-bank.com"),
                ("compliance", "compliance@izilens.com"),
            ):
                user, pwd = created[key]
                if user:
                    print(f"+ {key:<10}: {email:<26} / {pwd}")
            admin = created["admin"][0]
            if admin:
                principal = Principal("user", admin.id, organization.id, UserRole.ADMIN, frozenset(organization.enabled_modules))
                _, raw_key = create_api_key(db, principal, ApiKeyCreate(name="Clé de démonstration", expires_in_days=30))
                print(f"+ clé API  : {raw_key}")
                print("  (affichée une seule fois)")
        db.commit()


if __name__ == "__main__":
    main()
