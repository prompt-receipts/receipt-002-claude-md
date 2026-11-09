from app.features.totals import monthly_total

E_ = [("2026-01-05", "10.10"), ("2026-01-20", "0.20"), ("2026-02-01", "99"), ("2025-01-31", "5")]


def test_sum():
    assert monthly_total(E_, "2026-01") == "$10.30"
    assert monthly_total(E_, "2026-02") == "$99.00"


def test_none():
    assert monthly_total(E_, "2026-03") == "$0.00"
    assert monthly_total([], "2026-01") == "$0.00"


def test_many_small():
    ents = [("2026-04-01", "0.01")] * 1000
    assert monthly_total(ents, "2026-04") == "$10.00"
    ents = [("2026-04-01", "0.10"), ("2026-04-02", "0.20"), ("2026-04-03", "0.30")]
    assert monthly_total(ents, "2026-04") == "$0.60"
