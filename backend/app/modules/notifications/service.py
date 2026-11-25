import logging
import smtplib
import uuid
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import session_scope
from app.modules.notifications.models import EmailOutbox
from app.shared.i18n.emails import render

logger = logging.getLogger("app.email")
MAX_ATTEMPTS = 5


def queue_email(
    db: Session, *, to: str, template: str, locale: str, params: dict, related_id: uuid.UUID | None = None
) -> EmailOutbox:
    """Enregistre un e-mail à envoyer ; le rendu FR/EN est figé à la mise en file."""
    subject, body = render(template, locale, params)
    row = EmailOutbox(
        template=template, locale=locale, message={"to": to, "subject": subject, "body": body}, related_id=related_id
    )
    db.add(row)
    return row


def _send_smtp(message: dict) -> None:
    settings = get_settings()
    email = EmailMessage()
    email["From"], email["To"], email["Subject"] = settings.email_from, message["to"], message["subject"]
    email.set_content(message["body"])
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password or "")
        smtp.send_message(email)


def dispatch_pending(limit: int = 50) -> dict[str, int]:
    """Envoie les e-mails en attente ; en mode « console » le contenu est journalisé (développement uniquement)."""
    from app.core.time import utcnow

    backend = get_settings().email_backend
    sent = failed = 0
    if backend == "disabled":
        return {"sent": 0, "failed": 0}
    with session_scope() as db:
        rows = db.scalars(
            select(EmailOutbox).where(EmailOutbox.status == "pending").order_by(EmailOutbox.created_at).limit(limit)
        ).all()
        for row in rows:
            row.attempts += 1
            try:
                if backend == "smtp":
                    _send_smtp(row.message)
                else:
                    logger.info(
                        "email (console, développement uniquement)",
                        extra={
                            "template": row.template,
                            "to": row.message["to"],
                            "subject": row.message["subject"],
                            "body": row.message["body"],
                        },
                    )
                row.status, row.sent_at, row.last_error = "sent", utcnow(), None
                sent += 1
            except Exception as exc:  # noqa: BLE001
                row.last_error = type(exc).__name__[:100]
                if row.attempts >= MAX_ATTEMPTS:
                    row.status = "failed"
                    failed += 1
        db.commit()
    return {"sent": sent, "failed": failed}
