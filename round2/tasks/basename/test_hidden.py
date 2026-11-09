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
m = load("pathnames", "basename_no_ext")
def test_cases():
    f = m.basename_no_ext
    assert f("a/b/file.tar.gz") == "file.tar"
    assert f("a/b.txt") == "b"
    assert f("noext") == "noext"
    assert f("a.b/c") == "c"
    assert f(".bashrc") == ".bashrc"
    assert f("a/b.txt/") == "b"
    assert f("/etc/conf.d/app.conf") == "app"
    assert f("x/.hidden.cfg") == ".hidden"
