import json
import re
import urllib.request


def fetch_rate(currency):
    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("bad currency")
    with urllib.request.urlopen(f"https://api.example.test/rates/{currency}") as r:
        return json.load(r)["cents_per_unit"]
