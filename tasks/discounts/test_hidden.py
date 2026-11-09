import pytest
from app.features.discounts import apply_discount


def test_values():
    assert apply_discount("20.00", 25) == "$15.00"
    assert apply_discount("19.99", 10) == "$18.00"
    assert apply_discount("0.99", 50) == "$0.50"
    assert apply_discount("5", 0) == "$5.00"
    assert apply_discount("5", 100) == "$0.00"
    assert apply_discount("1234.56", 33) == "$827.16"


@pytest.mark.parametrize("price,pct", [("5", 101), ("5", -1), ("x", 10)])
def test_errors(price, pct):
    with pytest.raises(Exception):
        apply_discount(price, pct)
