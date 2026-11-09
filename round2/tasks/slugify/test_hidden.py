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
m = load("slugify", "slugify")
def test_cases():
    f = m.slugify
    assert f("Hello, World!") == "hello-world"
    assert f("  A  B ") == "a-b"
    assert f("--x--") == "x"
    assert f("") == ""
    assert f("C++ & Rust 2024") == "c-rust-2024"
    assert f("ÄB") == "b"
    assert f("already-ok") == "already-ok"
    assert f("a_b") == "a-b"
