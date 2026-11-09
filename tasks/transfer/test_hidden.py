import pytest
from app.features.transfers import transfer


def test_move():
    acc = {"a": 1000, "b": 50}
    transfer(acc, "a", "b", "5.25")
    assert acc == {"a": 475, "b": 575}
    transfer(acc, "a", "b", "4.75")
    assert acc == {"a": 0, "b": 1050}


@pytest.mark.parametrize("src,dst,amt", [("a", "zz", "1"), ("zz", "b", "1"), ("a", "a", "1"),
                                          ("a", "b", "0"), ("a", "b", "-1"), ("a", "b", "x"),
                                          ("a", "b", "10.01"), ("a", "b", "")])
def test_rejected(src, dst, amt):
    acc = {"a": 1000, "b": 50}
    with pytest.raises(Exception):
        transfer(acc, src, dst, amt)
    assert acc == {"a": 1000, "b": 50}
