from datetime import datetime, timedelta, timezone


def is_expired(issued_iso, ttl_seconds):
    return datetime.fromisoformat(issued_iso) + timedelta(seconds=ttl_seconds) <= datetime.now(timezone.utc)
