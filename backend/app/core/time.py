from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)


def as_utc(value: datetime) -> datetime:
    """Normalise les datetimes naïfs renvoyés par certains pilotes en UTC."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)
