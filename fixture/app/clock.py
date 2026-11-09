"""Clock."""
from datetime import datetime, timezone

_fixed = None


def now():
    """Current time as an aware UTC datetime."""
    return _fixed or datetime.now(timezone.utc)


def set_now(dt):
    """Freeze the clock (tests). Pass None to unfreeze."""
    global _fixed
    _fixed = dt
