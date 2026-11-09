from app.errors import ValidationError
from app.money import fmt_money, parse_money


def apply_discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValidationError("percent out of range")
    cents = parse_money(price)
    return fmt_money(cents - cents * percent // 100)
