import logging

log = logging.getLogger(__name__)


def import_rows(lines):
    rows = []
    for line in lines:
        parts = line.split(",")
        if len(parts) != 2 or not parts[0].strip():
            log.warning("skipped %s", line)
            continue
        try:
            rows.append((parts[0].strip(), round(float(parts[1]) * 100)))
        except ValueError:
            log.warning("skipped %s", line)
    return rows
