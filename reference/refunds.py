from app.audit import audit
from app.errors import ValidationError
from app.money import parse_money


def refund_amount(price, fee_bps):
    if not 0 <= fee_bps <= 10000:
        raise ValidationError("fee_bps out of range")
    cents = parse_money(price)
    out = cents - cents * fee_bps // 10000
    audit("refund_calculated", cents=cents, fee_bps=fee_bps)
    return out
