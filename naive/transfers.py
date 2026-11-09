def transfer(accounts, src, dst, amount):
    if src not in accounts or dst not in accounts or src == dst:
        raise ValueError("bad accounts")
    try:
        cents = round(float(amount) * 100)
    except ValueError:
        raise ValueError("bad amount")
    if cents <= 0 or accounts[src] < cents:
        raise ValueError("bad amount")
    accounts[src] -= cents
    accounts[dst] += cents
    print("transfer", src, dst, cents)
