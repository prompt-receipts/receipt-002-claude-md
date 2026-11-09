# Project conventions

- New feature code goes in `app/features/<name>.py`. Do not put new modules anywhere else.
- Money is integer cents. Parse user text with `app.money.parse_money` and format with `app.money.fmt_money`. Never use float or round() for money.
- Record every state-changing action with `app.audit.audit("event_name", key=value)`. Never use print() or the logging module.
- Get the current time only from `app.clock.now()`. Never call datetime.now, datetime.utcnow, datetime.today or time.time.
- Make network calls only through `app.http.get_json(url)`. Never import requests, urllib, httpx or http.client in feature code.
- Raise only exceptions from `app.errors` (AppError or a subclass). Never raise ValueError, KeyError or a bare Exception.
- Run tests with `python -m pytest -q`.
