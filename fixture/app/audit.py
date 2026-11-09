"""Audit log."""

EVENTS = []


def audit(event, **fields):
    """Record an audit event."""
    EVENTS.append({"event": event, **fields})
