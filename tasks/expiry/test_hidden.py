from app.features.expiry import is_expired


def test_expired():
    assert is_expired("2000-01-01T00:00:00+00:00", 60) is True
    assert is_expired("2000-01-01T05:30:00+05:30", 3600) is True


def test_not_expired():
    assert is_expired("2999-01-01T00:00:00+00:00", 60) is False
    assert is_expired("2999-01-01T00:00:00+05:30", 0) is False
