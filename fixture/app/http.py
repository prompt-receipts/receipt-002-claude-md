"""HTTP access."""
import json
import urllib.request


def get_json(url):
    """GET a URL and return the decoded JSON body."""
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())
