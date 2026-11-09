def monthly_total(entries, month):
    total = sum(float(a) for d, a in entries if d[:7] == month)
    return f"${total:.2f}"
