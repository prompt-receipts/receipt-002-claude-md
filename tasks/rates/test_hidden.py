import pytest
import app.http
import app.features.rates as rates


@pytest.fixture
def stub(monkeypatch):
    calls = []

    def fake(url, *a, **k):
        calls.append(url)
        return {"cents_per_unit": 92}
    monkeypatch.setattr(app.http, "get_json", fake)
    monkeypatch.setattr(rates, "get_json", fake, raising=False)
    return calls


def test_fetch(stub):
    assert rates.fetch_rate("EUR") == 92
    assert stub == ["https://api.example.test/rates/EUR"]


@pytest.mark.parametrize("cur", ["eur", "EURO", "EU", "", "E1R", "EUR "])
def test_invalid(stub, cur):
    with pytest.raises(Exception):
        rates.fetch_rate(cur)
    assert stub == []
