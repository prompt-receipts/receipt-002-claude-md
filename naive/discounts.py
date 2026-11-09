def apply_discount(price, percent):
    if percent < 0 or percent > 100:
        raise ValueError("bad percent")
    cents = round(float(price) * 100)
    cents -= cents * percent // 100
    return f"${cents // 100}.{cents % 100:02d}"
