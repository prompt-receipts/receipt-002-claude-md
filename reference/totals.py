from app.money import fmt_money, parse_money


def monthly_total(entries, month):
    return fmt_money(sum(parse_money(a) for d, a in entries if d.startswith(month + "-")))
