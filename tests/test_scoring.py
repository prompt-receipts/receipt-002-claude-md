"""Validates the scorer: reference solutions pass everything, naive ones pass behavior but
fail conventions, and individual checks react to individual violations."""
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

import score

ROOT = Path(__file__).parents[1]
TASKS = yaml.safe_load((ROOT / "tasks.yaml").read_text())
IDS = [t["id"] for t in TASKS]


def tree_with(code, feature, extra=None):
    d = Path(tempfile.mkdtemp())
    t = d / "t"
    shutil.copytree(score.FIXTURE, t)
    (t / "app" / "features" / f"{feature}.py").write_text(code)
    return t


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_reference_passes_all(task):
    t = tree_with((ROOT / "reference" / f"{task['feature']}.py").read_text(), task["feature"])
    r = score.score_tree(t, task)
    assert r["hidden_pass"], r
    assert r["conventions_pass"], r


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_naive_fails_conventions(task):
    t = tree_with((ROOT / "naive" / f"{task['feature']}.py").read_text(), task["feature"])
    r = score.score_tree(t, task)
    assert not r["conventions_pass"], r


def test_naive_float_money_loses_hidden_cases():
    task = next(t for t in TASKS if t["id"] == "refunds")
    t = tree_with((ROOT / "naive" / "refunds.py").read_text(), "refunds")
    assert not score.score_tree(t, task)["hidden_pass"]  # int(19.99*100) == 1998


def test_misplaced_file_fails_placement_only():
    task = next(t for t in TASKS if t["id"] == "discounts")
    t = tree_with("", "discounts")
    (t / "app" / "features" / "discounts.py").unlink()
    (t / "app" / "discounts.py").write_text((ROOT / "reference" / "discounts.py").read_text())
    # app/*.py files are treated as helpers and ignored, so a misplaced module is not credited
    r = score.score_tree(t, task)
    assert not r["checks"]["placement"] and not r["hidden_pass"]
    (t / "lib").mkdir()
    (t / "lib" / "discounts.py").write_text((ROOT / "reference" / "discounts.py").read_text())
    r = score.score_tree(t, task)
    assert not r["checks"]["placement"] and r["checks"]["money"] and r["checks"]["money_fmt"]


@pytest.mark.parametrize("snippet,check,expect", [
    ("from app.errors import AppError\ndef f():\n    raise AppError('x')\n", "errors", True),
    ("from app.errors import NotFoundError as NF\ndef f():\n    raise NF('x')\n", "errors", True),
    ("from app import errors\ndef f():\n    raise errors.AppError('x')\n", "errors", True),
    ("from app.errors import AppError\nclass E(AppError): pass\ndef f():\n    raise E('x')\n", "errors", True),
    ("def f():\n    raise ValueError('x')\n", "errors", False),
    ("def f(d):\n    return d['k']\n", "errors", False),
    ("from app.errors import AppError\ndef f():\n    raise AppError('x')\n    raise KeyError('y')\n", "errors", False),
    ("from app.audit import audit\ndef f():\n    audit('e')\n", "audit", True),
    ("import app.audit\ndef f():\n    app.audit.audit('e')\n", "audit", True),
    ("def f():\n    pass\n", "audit", False),
    ("def f():\n    print('x')\n", "no_print", False),
    ("import logging\n", "no_print", False),
    ("def f():\n    return 1\n", "no_print", True),
    ("from app import clock\ndef f():\n    return clock.now()\n", "clock", True),
    ("from app.clock import now\ndef f():\n    return now()\n", "clock", True),
    ("import time\ndef f():\n    return time.time()\n", "clock", False),
    ("from datetime import datetime\nfrom app import clock\ndef f():\n    return datetime.utcnow(), clock.now()\n", "clock", False),
    ("from app.http import get_json\ndef f():\n    return get_json('u')\n", "http", True),
    ("import requests\nfrom app.http import get_json\ndef f():\n    return get_json('u')\n", "http", False),
    ("from app.money import parse_money\ndef f(x):\n    return parse_money(x)\n", "money", True),
    ("from app.money import parse_money\ndef f(x):\n    return round(parse_money(x) * 1.1)\n", "money", False),
    ("def f(x):\n    return int(float(x) * 100)\n", "money", False),
    ("from decimal import Decimal\nfrom app.money import parse_money\ndef f(x):\n    return Decimal(x)\n", "money", False),
    ("from app.money import fmt_money\ndef f(x):\n    return fmt_money(x)\n", "money_fmt", True),
])
def test_individual_checks(snippet, check, expect):
    t = tree_with(snippet, "zz")
    assert score.run_checks(t, "zz", [check])[check] is expect


def test_helper_tampering_detected_and_restored():
    t = tree_with("from app.errors import AppError\n", "zz")
    (t / "app" / "money.py").write_text("def parse_money(x):\n    return 0\n")
    assert score.helpers_modified(t) == ["money"]
