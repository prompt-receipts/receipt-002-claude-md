import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

R2 = Path(__file__).parents[1]
sys.path.insert(0, str(R2))
sys.path.insert(0, str(R2 / "reference"))
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("score_r2", R2 / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
from solutions import NAIVE, REF  # noqa: E402

TASKS = yaml.safe_load((R2 / "tasks.yaml").read_text())
IDS = [t["id"] for t in TASKS]


def fresh():
    t = Path(tempfile.mkdtemp()) / "t"
    shutil.copytree(score.FIXTURE, t)
    return t


def add_changelog(t, line):
    p = t / "CHANGELOG.md"
    p.write_text(p.read_text().replace("## Unreleased\n", f"## Unreleased\n{line}\n", 1))


def ref_tree(task):
    r = REF[task["id"]]
    t = fresh()
    (t / "src/shop/ext").mkdir()
    (t / "src/shop/ext/__init__.py").write_text("")
    (t / "src/shop/ext" / f"{task['feature']}.py").write_text(r["module"])
    (t / "tests").mkdir()
    (t / "tests" / f"test_{task['feature']}_cases.py").write_text(r["tests"])
    add_changelog(t, r["changelog"])
    return t


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_reference_passes_all(task):
    r = score.score_tree(ref_tree(task), task)
    assert r["hidden_pass"], r
    assert r["conventions_pass"], r


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_naive_passes_behavior_fails_conventions(task):
    feature, code = NAIVE[task["id"]]
    t = fresh()
    (t / "src/shop" / f"{feature}.py").write_text(code)
    (t / "tests").mkdir()
    (t / "tests" / f"test_{feature}.py").write_text("def test_x():\n    pass\n")
    r = score.score_tree(t, task)
    assert r["hidden_pass"], r
    assert not r["conventions_pass"], r
    c = r["checks"]
    assert not c["location"] and not c["tests_file"] and not c["docstring"] and not c["changelog"]
    assert c.get("stdlib", True) is (task["id"] in ("chunk", "moving_average", "parse_kv"))


@pytest.mark.parametrize("snippet,expect", [
    ("import re\n", True), ("from re import sub\n", True), ("import os.path\n", True),
    ("from os import path\n", True), ("import os\nx = os.path.join('a')\n", True),
    ("from os.path import join\n", True), ("import os\nx = os.getcwd()\n", False),
    ("from pathlib import Path\n", False), ("import regex_not_re\n", False),
])
def test_forbidden_stdlib(snippet, expect):
    import ast
    assert score.uses_forbidden_stdlib([ast.parse(snippet)]) is expect


def test_docstring_and_changelog_strictness():
    import ast
    ok = ast.parse('def f():\n    """x\n\n    Ticket: PAY-1\n    """\n')
    assert score.docstring_ok([ok], "f", "PAY-1")
    assert not score.docstring_ok([ok], "f", "PAY-2")
    assert not score.docstring_ok([ast.parse('def f():\n    """Ticket PAY-1"""\n')], "f", "PAY-1")
    assert not score.docstring_ok([ast.parse('def g():\n    """Ticket: PAY-1"""\n')], "f", "PAY-1")
    t = fresh()
    assert not score.changelog_ok(t, "PAY-1", "feat")
    (t / "CHANGELOG.md").write_text("# C\n\n## Unreleased\n- PAY-1: feat: did it\n\n## 1.0.0\n- PAY-9: feat: old\n")
    assert score.changelog_ok(t, "PAY-1", "feat")
    assert not score.changelog_ok(t, "PAY-9", "feat")          # outside Unreleased
    (t / "CHANGELOG.md").write_text("## Unreleased\n- PAY-1 feat: did it\n- PAY-1: feat:\n- [PAY-1] feat: x\n")
    assert not score.changelog_ok(t, "PAY-1", "feat")


def test_hidden_tests_find_module_anywhere():
    task = next(t for t in TASKS if t["id"] == "chunk")
    feature, code = NAIVE["chunk"]
    for rel in ("src/shop/chunking.py", "chunking.py", "lib/other_name.py", "src/shop/core.py"):
        t = fresh()
        p = t / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(code)
        assert score.run_hidden(t, "chunk")["pass"], rel
    assert not score.run_hidden(fresh(), "chunk")["pass"]
