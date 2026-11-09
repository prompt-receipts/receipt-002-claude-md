import importlib.util, pathlib, sys, pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
def load(name, func):
    """Find the module that defines `func`: prefer <name>.py, else any non-test source file defining it."""
    cands = [p for p in sorted(ROOT.rglob("*.py"))
             if not ({"_hidden", "tests", "__pycache__"} & set(p.relative_to(ROOT).parts))]
    cands.sort(key=lambda p: p.stem != name)
    for p in cands:
        if ("def %s(" % func) in p.read_text():
            sys.path[:0] = [str(ROOT), str(ROOT / "src")]
            spec = importlib.util.spec_from_file_location("hidden_target_" + p.stem, p)
            m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
    raise AssertionError("no module defining %s found" % func)
m = load("movavg", "moving_average")
def test_cases():
    f = m.moving_average
    assert f([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]
    assert f([5], 1) == [5.0]
    assert f([1, 2, 3], 3) == [2.0]
    assert f([2, 4, 6, 8], 1) == [2.0, 4.0, 6.0, 8.0]
    assert all(isinstance(x, float) for x in f([1, 2, 3], 2))
@pytest.mark.parametrize("k", [0, -1, 4])
def test_bad(k):
    with pytest.raises(ValueError):
        m.moving_average([1, 2, 3], k)
