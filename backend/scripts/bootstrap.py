""" Pr Init la plateforme avec super admini et autres avec mode --demo un tenant de demo

use : python scripts/bootstrap.py --email admin@izilens.com [--demo]
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--email", required=True, help="Email du super administrateur")
    parser.add_argument("--demo", action="store_true", help="Crée aussi une organisation de démonstration")
    args = parser.parse_args()

    password = getpass.getpass("Mot de passe du super administrateur (12 caractères min.) : ")
    validate_password_strength(password)

    with session_scope() as db:
        ensure_user(db, email=args.email.lower(), full_name="Super Admin", role=UserRole.SUPER_ADMIN, password=password)
        print(f"+ super administrateur : {args.email.lower()}")

        if args.demo:
            organization = db.scalar(select(Organization).where(Organization.slug == "demo-bank"))
            if organization is None:
                organization = Organization(name="Demo Bank", slug="demo-bank", enabled_modules=["kyc"])
                db.add(organization)
                db.flush()
            admin_password = secrets.token_urlsafe(12) + "A1"
            reviewer_password = secrets.token_urlsafe(12) + "A1"
            admin = ensure_user(
                db,
                email="admin@demo-bank.com",
                full_name="Admin Demo",
                role=UserRole.ADMIN,
                password=admin_password,
                organization_id=organization.id,
            )
            reviewer = ensure_user(
                db,
                email="reviewer@demo-bank.com",
                full_name="Reviewer Demo",
                role=UserRole.REVIEWER,
                password=reviewer_password,
                organization_id=organization.id,
            )
            db.commit()
            print(f"+ organisation de démonstration : {organization.name} (modules : {', '.join(organization.enabled_modules)})")
            if admin:
                print(f"+ admin    : admin@demo-bank.com    / {admin_password}")
            if reviewer:
                print(f"+ reviewer : reviewer@demo-bank.com / {reviewer_password}")
            if admin:
                principal = Principal("user", admin.id, organization.id, UserRole.ADMIN, frozenset(organization.enabled_modules))
                _, raw_key = create_api_key(db, principal, ApiKeyCreate(name="Clé de démonstration", expires_in_days=30))
                print(f"+ clé API  : {raw_key}")
                print("  (affichée une seule fois)")
        db.commit()


if __name__ == "__main__":
    main()
