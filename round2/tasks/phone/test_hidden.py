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
m = load("phones", "normalize_phone")
def test_ok():
    f = m.normalize_phone
    assert f("(415) 555-2671") == "+14155552671"
    assert f("1-415-555-2671") == "+14155552671"
    assert f("415.555.2671") == "+14155552671"
    assert f("+1 415 555 2671") == "+14155552671"
    assert f("4155552671") == "+14155552671"
@pytest.mark.parametrize("bad", ["555-2671", "24155552671", "", "abc", "141555526712", "415555267100"])
def test_bad(bad):
    with pytest.raises(ValueError):
        m.normalize_phone(bad)
