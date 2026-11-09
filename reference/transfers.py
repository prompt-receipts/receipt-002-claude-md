from app.audit import audit
from app.errors import InsufficientFunds, NotFoundError, ValidationError
from app.money import parse_money


def transfer(accounts, src, dst, amount):
    if src not in accounts or dst not in accounts:
        raise NotFoundError("unknown account")
    if src == dst:
        raise ValidationError("same account")
    cents = parse_money(amount)
    if cents <= 0:
        raise ValidationError("amount must be positive")
    if accounts[src] < cents:
        raise InsufficientFunds(src)
    accounts[src] -= cents
    accounts[dst] += cents
    audit("transfer", src=src, dst=dst, cents=cents)
