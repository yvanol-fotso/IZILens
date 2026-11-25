from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.billing.models import DocumentCounter


def next_value(db: Session, key: str) -> int:
    """Numéro séquentiel sans trou par clé (verrou de ligne) : références, factures, avoirs."""
    row = db.get(DocumentCounter, key, with_for_update=True)
    if row is None:
        try:
            with db.begin_nested():
                db.add(DocumentCounter(key=key, value=1))
            return 1
        except IntegrityError:
            row = db.get(DocumentCounter, key, with_for_update=True)
    row.value += 1
    db.flush()
    return row.value
