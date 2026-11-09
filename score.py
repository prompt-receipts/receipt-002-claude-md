"""Deterministic scoring for receipt 002: hidden tests plus static convention checks.

Both are computed from a tree = pristine fixture + the diff the agent produced, so a result can be
re-scored from the saved patch alone.
"""
import ast
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
FIXTURE = HERE / "fixture"
HELPERS = ["errors", "money", "audit", "clock", "http"]  # restored before tests; never scored
WALL_CLOCK = {("datetime", "now"), ("datetime", "utcnow"), ("datetime", "today"), ("date", "today"),
              ("time", "time"), ("time", "monotonic"), ("time", "time_ns")}
NET_MODULES = {"requests", "urllib", "httpx", "http", "aiohttp", "urllib3", "socket"}


def candidate_files(tree):
    """Python files the agent added under app/ (excluding helpers) or outside app/ and tests/."""
    tree = Path(tree)
    out = []
    for p in sorted(tree.rglob("*.py")):
        rel = p.relative_to(tree)
        parts = rel.parts
        if parts[0] in ("tests", ".venv") or "__pycache__" in parts or parts[0].startswith("."):
            continue
        if parts[0] == "app" and (len(parts) == 2 or rel.as_posix() in
                                  ("app/features/__init__.py", "app/features/greeting.py")):
            continue  # helpers and pristine fixture files
        out.append(p)
    return out


def _calls(trees):
    """Names of everything called: foo() -> foo, a.b.foo() -> foo, plus (obj, attr) pairs."""
    names, pairs = set(), set()
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name):
                    names.add(f.id)
                elif isinstance(f, ast.Attribute):
                    names.add(f.attr)
                    base = f.value
                    if isinstance(base, ast.Name):
                        pairs.add((base.id, f.attr))
                    elif isinstance(base, ast.Attribute):
                        pairs.add((base.attr, f.attr))
    return names, pairs


def _imports(trees):
    mods, froms = set(), {}
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, ast.Import):
                mods |= {a.name.split(".")[0] for a in n.names}
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                mods.add(n.module.split(".")[0])
                mods.add(n.module)
                for a in n.names:
                    froms.setdefault(n.module, set()).add(a.name)
    return mods, froms


def _raises_ok(trees):
    """True if there is at least one raise and every raised class comes from app.errors."""
    allowed = set()
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, ast.ImportFrom) and n.module == "app.errors":
                allowed |= {a.asname or a.name for a in n.names}
    modules = set()
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, ast.ImportFrom) and n.module == "app" and any(a.name == "errors" for a in n.names):
                modules.add("errors")
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name == "app.errors":
                        modules.add("app")
    for t in trees:  # classes defined here that extend an allowed class
        for n in ast.walk(t):
            if isinstance(n, ast.ClassDef) and any(_name_ok(b, allowed, modules) for b in n.bases):
                allowed.add(n.name)
    seen = False
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, ast.Raise) and n.exc is not None:
                seen = True
                e = n.exc.func if isinstance(n.exc, ast.Call) else n.exc
                if not _name_ok(e, allowed, modules):
                    return False
    return seen


def _name_ok(node, allowed, modules):
    if isinstance(node, ast.Name):
        return node.id in allowed
    if isinstance(node, ast.Attribute):  # errors.AppError / app.errors.AppError
        root = node.value
        if isinstance(root, ast.Name) and root.id in modules:
            return True
        if isinstance(root, ast.Attribute) and root.attr == "errors":
            return True
    return False


def run_checks(tree, feature, wanted):
    files = candidate_files(tree)
    trees = []
    for p in files:
        try:
            trees.append(ast.parse(p.read_text()))
        except SyntaxError:
            pass
    names, pairs = _calls(trees)
    mods, froms = _imports(trees)
    src_names = {n.id for t in trees for n in ast.walk(t) if isinstance(n, ast.Name)}
    attrs = {n.attr for t in trees for n in ast.walk(t) if isinstance(n, ast.Attribute)}
    res = {}
    res["placement"] = (Path(tree) / "app" / "features" / f"{feature}.py").is_file()
    res["money"] = ("parse_money" in names
                    and not ({"float", "round"} & names)
                    and not ({"Decimal", "Fraction"} & (src_names | attrs)))
    res["money_fmt"] = "fmt_money" in names
    res["audit"] = "audit" in names
    res["no_print"] = ("print" not in names and "logging" not in mods and "warnings" not in mods
                       and "stderr" not in attrs and "stdout" not in attrs)
    res["clock"] = ("now" in names and not (WALL_CLOCK & pairs)
                    and ("app.clock" in mods or "clock" in froms.get("app", set())))
    res["http"] = ("get_json" in names and not (NET_MODULES & mods))
    res["errors"] = _raises_ok(trees)
    return {k: bool(res[k]) for k in wanted}


def run_hidden(tree, task_id, timeout=60):
    """Run the hidden test file against the tree (helpers restored to pristine first)."""
    with tempfile.TemporaryDirectory() as d:
        work = Path(d) / "w"
        shutil.copytree(tree, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        for h in HELPERS:
            shutil.copy(FIXTURE / "app" / f"{h}.py", work / "app" / f"{h}.py")
        (work / "tests").mkdir(exist_ok=True)
        t = work / "tests" / f"test_hidden_{task_id}.py"
        shutil.copy(HERE / "tasks" / task_id / "test_hidden.py", t)
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(t)],
                               cwd=work, env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"pass": False, "reason": "timeout"}
    if r.returncode == 0:
        return {"pass": True, "reason": "ok"}
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:] or ["error"]
    return {"pass": False, "reason": tail[0][:200]}


def helpers_modified(tree):
    return [h for h in HELPERS
            if (Path(tree) / "app" / f"{h}.py").read_bytes() != (FIXTURE / "app" / f"{h}.py").read_bytes()]


def score_tree(tree, task):
    hidden = run_hidden(tree, task["id"])
    checks = run_checks(tree, task["feature"], task["checks"])
    return {"hidden_pass": hidden["pass"], "hidden_reason": hidden["reason"], "checks": checks,
            "conventions_pass": all(checks.values()), "helpers_modified": helpers_modified(tree)}
