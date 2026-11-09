"""Money helpers."""
import re

from app.errors import ValidationError

_RE = re.compile(r"^\$?(\d+)(?:\.(\d{1,2}))?$")


def parse_money(text):
    """Parse '12.50', '$12.5' or '12' into integer cents. Raises ValidationError."""
    m = _RE.match(str(text).strip())
    if not m:
        raise ValidationError(f"bad money value: {text!r}")
    return int(m.group(1)) * 100 + int((m.group(2) or "0").ljust(2, "0"))


def fmt_money(cents):
    """Format integer cents as '$12.50'."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"
