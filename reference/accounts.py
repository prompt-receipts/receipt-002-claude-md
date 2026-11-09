from app.audit import audit
from app.errors import NotFoundError


def close_account(accounts, account_id):
    if account_id not in accounts:
        raise NotFoundError(account_id)
    balance = accounts.pop(account_id)
    audit("account_closed", account_id=account_id, balance=balance)
    return balance
