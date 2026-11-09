"""Round 2 scoring: hidden behavior tests plus static checks for rules the code cannot reveal."""
import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
FIXTURE = HERE / "fixture"
FORBIDDEN_MODULES = {"re"}


def changed_py(tree):
    """Python files (outside tests/) that are new or differ from the fixture."""
    tree = Path(tree)
    out = []
    for p in sorted(tree.rglob("*.py")):
        rel = p.relative_to(tree)
        if rel.parts[0] in ("tests", ".venv") or "__pycache__" in rel.parts:
            continue
        f = FIXTURE / rel
        if f.is_file() and f.read_bytes() == p.read_bytes():
            continue
        out.append(p)
    return out


def _parse(files):
    trees = []
    for p in files:
        try:
            trees.append(ast.parse(p.read_text()))
        except SyntaxError:
            pass
    return trees


def uses_forbidden_stdlib(trees):
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name.split(".")[0] in FORBIDDEN_MODULES or a.name == "os.path":
                        return True
            elif isinstance(n, ast.ImportFrom):
                mod = n.module or ""
                if mod.split(".")[0] in FORBIDDEN_MODULES or mod == "os.path":
                    return True
                if mod == "os" and any(a.name == "path" for a in n.names):
                    return True
            elif isinstance(n, ast.Attribute) and n.attr == "path" \
                    and isinstance(n.value, ast.Name) and n.value.id == "os":
                return True
    return False


def docstring_ok(trees, func, ticket):
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func:
                doc = ast.get_docstring(n) or ""
                return any(l.strip() == f"Ticket: {ticket}" for l in doc.splitlines())
    return False


def changelog_ok(tree, ticket, feature):
    p = Path(tree) / "CHANGELOG.md"
    if not p.is_file():
        return False
    section, inside = [], False
    for line in p.read_text().splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Unreleased"
            continue
        if inside:
            section.append(line)
    pat = re.compile(rf"^- {re.escape(ticket)}: {re.escape(feature)}: \S.*$")
    return any(pat.match(l) for l in section)


def run_checks(tree, task):
    files = changed_py(tree)
    trees = _parse(files)
    allc = {
        "location": (Path(tree) / "src" / "shop" / "ext" / f"{task['feature']}.py").is_file(),
        "tests_file": (Path(tree) / "tests" / f"test_{task['feature']}_cases.py").is_file(),
        "stdlib": not uses_forbidden_stdlib(trees),
        "docstring": docstring_ok(trees, task["func"], task["ticket"]),
        "changelog": changelog_ok(tree, task["ticket"], task["feature"]),
    }
    return {k: bool(allc[k]) for k in task["checks"]}


def run_hidden(tree, task_id, timeout=60):
    with tempfile.TemporaryDirectory() as d:
        work = Path(d) / "w"
        shutil.copytree(tree, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        (work / "_hidden").mkdir()
        t = work / "_hidden" / f"test_hidden_{task_id}.py"
        shutil.copy(HERE / "tasks" / task_id / "test_hidden.py", t)
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                                "--rootdir", str(work), "-c", "/dev/null", str(t)],
                               cwd=work, env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"pass": False, "reason": "timeout"}
    if r.returncode == 0:
        return {"pass": True, "reason": "ok"}
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:] or ["error"]
    return {"pass": False, "reason": tail[0][:200]}


def helpers_modified(tree):
    """Fixture files the agent changed (e.g. core.py or the package __init__)."""
    return [str(p.relative_to(FIXTURE)) for p in FIXTURE.rglob("*.py")
            if (Path(tree) / p.relative_to(FIXTURE)).read_bytes() != p.read_bytes()]


def score_tree(tree, task):
    hidden = run_hidden(tree, task["id"])
    checks = run_checks(tree, task)
    return {"hidden_pass": hidden["pass"], "hidden_reason": hidden["reason"], "checks": checks,
            "conventions_pass": all(checks.values()), "helpers_modified": helpers_modified(tree)}
