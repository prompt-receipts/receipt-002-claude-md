def refund_amount(price, fee_bps):
    if fee_bps < 0 or fee_bps > 10000:
        raise ValueError("bad fee")
    cents = int(float(price) * 100)
    return cents - cents * fee_bps // 10000
