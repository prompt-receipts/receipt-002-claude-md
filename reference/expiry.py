from datetime import datetime, timedelta

from app import clock


def is_expired(issued_iso, ttl_seconds):
    return datetime.fromisoformat(issued_iso) + timedelta(seconds=ttl_seconds) <= clock.now()
