import os
import tempfile
import uuid
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="izilens_tests_"))
os.environ.update(
    {
        "ENVIRONMENT": "test",
        "DATABASE_URL": os.environ.get("TEST_DATABASE_URL", f"sqlite:///{_TMP / 'test.db'}"),
        "JWT_SECRET": "test-jwt-secret-test-jwt-secret-0123456789",
        "API_KEY_PEPPER": "test-pepper-test-pepper-test-pepper-0123",
        "DATA_ENCRYPTION_KEYS": "w6m5WVnsOXnvtKQ3R1kzcUCawLVk8-EF7KuFfWF7vSE=",
        "STORAGE_DIR": str(_TMP / "storage"),
        "RATE_LIMIT_ENABLED": "true",
        "RATE_LIMIT_LOGIN_PER_MINUTE": "50",
        "OCR_PRELOAD": "false",
    }
)

import pytest  # noqa: E402
from argon2 import PasswordHasher  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.common.enums import UserRole  # noqa: E402
from app.core import security  # noqa: E402
from app.core.database import Base, get_engine, session_scope  # noqa: E402
from app.core.rate_limit import limiter  # noqa: E402
from app.core.security import hash_password  # noqa: E402

security._hasher = PasswordHasher(time_cost=1, memory_cost=1024, parallelism=1)  # hachage allégé : tests rapides
from app.main import app  # noqa: E402
from app.models_registry import User  # noqa: E402
from app.modules.kyc.journeys import ensure_platform_defaults  # noqa: E402
from app.shared.ocr.engine import set_engine  # noqa: E402
from tests.helpers import FakeEngine, cni_lines  # noqa: E402

PASSWORD = "Sup3rSecretPass99"


@pytest.fixture(scope="session", autouse=True)
def _schema():
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _clean_state():
    engine = get_engine()
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
    limiter.reset()
    with session_scope() as db:
        ensure_platform_defaults(db, validate_coverage=True)
        db.commit()
    set_engine(FakeEngine(cni_lines()))
    yield
    set_engine(None)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def _create_user(email: str, role: UserRole, organization_id=None, password: str | None = PASSWORD) -> uuid.UUID:
    with session_scope() as db:
        user = User(
            email=email,
            full_name=email.split("@")[0],
            role=role,
            organization_id=organization_id,
            password_hash=hash_password(password) if password else None,
        )
        db.add(user)
        db.commit()
        return user.id


def _login(client: TestClient, email: str, password: str = PASSWORD) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def super_admin(client):
    _create_user("root@izilens.com", UserRole.SUPER_ADMIN)
    return _login(client, "root@izilens.com")


@pytest.fixture
def platform(client, super_admin):
    """Analyste conformité IZI LENS (back-office)."""
    _create_user("compliance@izilens.com", UserRole.PLATFORM_COMPLIANCE)
    return _login(client, "compliance@izilens.com")


@pytest.fixture
def make_org(client, super_admin):
    """Crée une organisation avec un admin, un reviewer, un viewer et une clé API."""

    def factory(slug: str, modules: list[str] | None = None) -> dict:
        response = client.post(
            "/api/v1/organizations",
            json={"name": slug.title(), "slug": slug, "enabled_modules": modules or ["kyc"]},
            headers=super_admin,
        )
        assert response.status_code == 201, response.text
        organization = response.json()
        org_id = uuid.UUID(organization["id"])
        _create_user(f"admin@{slug}.com", UserRole.ADMIN, org_id)
        _create_user(f"reviewer@{slug}.com", UserRole.REVIEWER, org_id)
        _create_user(f"viewer@{slug}.com", UserRole.VIEWER, org_id)
        admin = _login(client, f"admin@{slug}.com")
        key = client.post("/api/v1/api-keys", json={"name": "test"}, headers=admin)
        assert key.status_code == 201, key.text
        return {
            "organization": organization,
            "admin": admin,
            "reviewer": _login(client, f"reviewer@{slug}.com"),
            "viewer": _login(client, f"viewer@{slug}.com"),
            "api_key": {"X-API-Key": key.json()["key"]},
            "api_key_id": key.json()["id"],
        }

    return factory


@pytest.fixture
def org(make_org):
    return make_org("alpha")


class WebhookSink:
    """Remplace le réseau sortant : enregistre chaque appel et renvoie le statut configuré."""

    def __init__(self) -> None:
        self.requests: list = []
        self.status = 200

    def handler(self, request):
        import httpx

        self.requests.append(request)
        return httpx.Response(self.status)


@pytest.fixture(autouse=True)
def webhook_sink(monkeypatch):
    from types import SimpleNamespace

    import httpx

    from app.modules.webhooks import service as webhook_service

    sink = WebhookSink()
    monkeypatch.setattr(
        webhook_service,
        "httpx",
        SimpleNamespace(Client=lambda **_: httpx.Client(transport=httpx.MockTransport(sink.handler)), HTTPError=httpx.HTTPError),
    )
    monkeypatch.setattr(webhook_service, "_resolve", lambda host: ["93.184.216.34"])
    return sink


@pytest.fixture
def staff(client):
    """Crée un compte de la plateforme avec le rôle voulu et renvoie ses en-têtes d'authentification."""
    counter = iter(range(1, 100))

    def factory(role: UserRole) -> dict[str, str]:
        email = f"{role.value}{next(counter)}@izilens.com"
        _create_user(email, role)
        return _login(client, email)

    return factory


def outbox() -> list[dict]:
    """E-mails mis en file (déchiffrés) : permet de vérifier les envois sans SMTP."""
    from app.models_registry import EmailOutbox

    with session_scope() as db:
        return [
            {"template": r.template, "locale": r.locale, "status": r.status, **r.message}
            for r in db.query(EmailOutbox).order_by(EmailOutbox.created_at).all()
        ]
