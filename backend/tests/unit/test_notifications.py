import pytest

from app.core.config import Settings, get_settings
from app.core.database import session_scope
from app.models_registry import EmailOutbox
from app.modules.notifications import service
from app.shared.i18n.emails import TEMPLATES, render


def queue(**params):
    with session_scope() as db:
        service.queue_email(
            db,
            to="user@example.com",
            template="request_confirmation",
            locale="fr",
            params={"full_name": "Awa", "reference": "IZL-2026-000001", "team": "sales", **params},
        )
        db.commit()


def statuses():
    with session_scope() as db:
        return [(r.status, r.attempts, r.last_error) for r in db.query(EmailOutbox).all()]


def test_every_template_renders_in_both_languages():
    params = {
        "full_name": "A",
        "reference": "R",
        "team": "sales",
        "kind": "contact",
        "type": "sales",
        "organization": "O",
        "login_url": "u",
        "credentials": "c",
        "decision": "d",
        "note": "n",
    }
    for name in TEMPLATES:
        for locale in ("fr", "en"):
            subject, body = render(name, locale, params)
            assert subject and body
    assert render("request_confirmation", "de", params)[0] == render("request_confirmation", "fr", params)[0]


def test_console_backend_marks_messages_sent_without_network(monkeypatch):
    monkeypatch.setattr(get_settings(), "email_backend", "console")
    queue()
    assert service.dispatch_pending() == {"sent": 1, "failed": 0}
    assert statuses() == [("sent", 1, None)]
    assert service.dispatch_pending() == {"sent": 0, "failed": 0}


def test_disabled_backend_keeps_messages_pending(monkeypatch):
    monkeypatch.setattr(get_settings(), "email_backend", "disabled")
    queue()
    assert service.dispatch_pending() == {"sent": 0, "failed": 0} and statuses() == [("pending", 0, None)]


def test_smtp_backend_sends_with_tls_and_authentication(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            sent["connect"] = (host, port)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def starttls(self):
            sent["tls"] = True

        def login(self, user, password):
            sent["login"] = (user, password)

        def send_message(self, message):
            sent["to"], sent["subject"] = message["To"], message["Subject"]

    settings = get_settings()
    for key, value in {
        "email_backend": "smtp",
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "mailer",
        "smtp_password": "pw",
        "smtp_starttls": True,
    }.items():
        monkeypatch.setattr(settings, key, value)
    monkeypatch.setattr(service.smtplib, "SMTP", FakeSMTP)
    queue()
    assert service.dispatch_pending()["sent"] == 1
    assert sent["connect"] == ("smtp.example.com", 587) and sent["tls"] and sent["login"] == ("mailer", "pw")
    assert sent["to"] == "user@example.com" and "IZL-2026-000001" in sent["subject"]


def test_failures_are_retried_then_marked_failed(monkeypatch):
    def broken(*_args, **_kwargs):
        raise ConnectionRefusedError("secret detail")

    settings = get_settings()
    monkeypatch.setattr(settings, "email_backend", "smtp")
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(service.smtplib, "SMTP", broken)
    queue()
    for _ in range(service.MAX_ATTEMPTS - 1):
        assert service.dispatch_pending() == {"sent": 0, "failed": 0}
    assert statuses() == [("pending", service.MAX_ATTEMPTS - 1, "ConnectionRefusedError")]
    assert service.dispatch_pending() == {"sent": 0, "failed": 1}
    assert statuses()[0][0] == "failed" and "secret" not in str(statuses())


def test_message_content_is_encrypted_at_rest():
    from sqlalchemy import text

    from app.core.database import get_engine

    queue()
    with get_engine().connect() as connection:
        raw = connection.execute(text("SELECT message FROM email_outbox")).scalar_one()
    assert "user@example.com" not in raw and "IZL-2026" not in raw


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"environment": "production", "email_backend": "console"}, "EMAIL_BACKEND=console"),
        ({"email_backend": "smtp"}, "SMTP_HOST"),
    ],
)
def test_email_settings_are_validated(overrides, message):
    base = {
        "database_url": "postgresql://x",
        "jwt_secret": "j" * 40,
        "api_key_pepper": "p" * 40,
        "data_encryption_keys": "w6m5WVnsOXnvtKQ3R1kzcUCawLVk8-EF7KuFfWF7vSE=",
    }
    with pytest.raises(ValueError, match=message):
        Settings(_env_file=None, **{**base, "oidc_enabled": False, **overrides})
