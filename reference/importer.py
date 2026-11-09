from app.audit import audit
from app.errors import AppError
from app.money import parse_money


def import_rows(lines):
    rows = []
    for line in lines:
        parts = line.split(",")
        try:
            if len(parts) != 2 or not parts[0].strip():
                raise AppError("bad shape")
            rows.append((parts[0].strip(), parse_money(parts[1])))
        except AppError:
            audit("row_skipped", line=line)
    return rows
