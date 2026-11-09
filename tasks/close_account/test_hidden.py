import pytest
from app.features.accounts import close_account


def test_close():
    acc = {"a": 500, "b": 0}
    assert close_account(acc, "a") == 500
    assert acc == {"b": 0}
    assert close_account(acc, "b") == 0
    assert acc == {}


def test_unknown():
    acc = {"a": 500}
    with pytest.raises(Exception):
        close_account(acc, "zzz")
    assert acc == {"a": 500}
