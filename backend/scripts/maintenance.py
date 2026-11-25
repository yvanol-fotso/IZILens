"""Tâche périodique (timer systemd ou cron, chaque minute) : expire les demandes dues et envoie les webhooks en attente."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import models_registry  # noqa: E402,F401
from app.core.database import session_scope  # noqa: E402
from app.infrastructure.logging.setup import configure_logging  # noqa: E402
from app.modules.kyc.service import expire_due_cases  # noqa: E402
from app.modules.notifications.service import dispatch_pending as dispatch_emails  # noqa: E402
from app.modules.webhooks.service import dispatch_pending  # noqa: E402


def main() -> None:
    configure_logging("INFO")
    with session_scope() as db:
        expired = expire_due_cases(db)
    result = dispatch_pending()
    emails = dispatch_emails()
    logging.getLogger("app.maintenance").info(
        "maintenance", extra={"expired_cases": expired, **result, "emails_sent": emails["sent"]}
    )


if __name__ == "__main__":
    main()
