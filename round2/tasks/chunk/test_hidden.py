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
m = load("chunking", "chunk")
def test_cases():
    f = m.chunk
    assert f([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert f([], 3) == []
    assert f([1, 2], 5) == [[1, 2]]
    assert f([1, 2, 3], 1) == [[1], [2], [3]]
    assert f(["a", "b", "c", "d"], 2) == [["a", "b"], ["c", "d"]]
def test_bad():
    for n in (0, -1):
        with pytest.raises(ValueError):
            m.chunk([1], n)
