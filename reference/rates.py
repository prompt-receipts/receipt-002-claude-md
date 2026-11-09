import re

from app.errors import ValidationError
from app.http import get_json


def fetch_rate(currency):
    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValidationError("bad currency")
    return get_json(f"https://api.example.test/rates/{currency}")["cents_per_unit"]
