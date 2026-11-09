import pytest
from app.features.refunds import refund_amount


def test_values():
    assert refund_amount("12.50", 0) == 1250
    assert refund_amount("12.50", 250) == 1219
    assert refund_amount("100", 10000) == 0
    assert refund_amount("0.99", 100) == 99
    assert refund_amount("19.99", 1500) == 1700
    assert refund_amount("19.99", 0) == 1999


@pytest.mark.parametrize("price,bps", [("12.50", -1), ("12.50", 10001), ("abc", 100), ("", 100)])
def test_errors(price, bps):
    with pytest.raises(Exception):
        refund_amount(price, bps)
