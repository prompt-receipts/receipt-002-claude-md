from app.features.importer import import_rows


def test_mixed():
    lines = ["alice,10.50", "bad", "bob,abc", ",5", "carol,3", "dan,1.234", "eve,2,3", "fay,0.07"]
    assert import_rows(lines) == [("alice", 1050), ("carol", 300), ("fay", 7)]


def test_empty():
    assert import_rows([]) == []


def test_all_valid_order():
    assert import_rows(["b,1", "a,2"]) == [("b", 100), ("a", 200)]
