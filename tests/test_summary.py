import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import run  # noqa: E402


def row(c, t, hidden, conv, cost=0.01):
    return {"condition": c, "task": t, "run": 0, "hidden_pass": hidden, "conventions_pass": conv,
            "checks": {"placement": True, "audit": conv}, "cost_usd": cost, "turns": 5,
            "out_of_tree": [], "helpers_modified": []}


def test_summarize_counts_and_separate_metrics():
    cfg = {"name": "n", "model": "haiku", "runs": 1, "seed": 1, "tasks": [{"id": "x"}, {"id": "y"}]}
    rows = [row("A", "x", True, False), row("A", "y", True, False),
            row("B", "x", True, True), row("B", "y", False, True)]
    s = run.summarize(cfg, rows)
    assert s["compare_hidden_pass"]["A"] == "2/2" and s["compare_hidden_pass"]["B"] == "1/2"
    assert s["compare_conventions_pass"]["A"] == "0/2" and s["compare_conventions_pass"]["B"] == "2/2"
    assert s["compare_both"]["B"] == "1/2" and s["compare_both"]["A"] == "0/2"
    assert s["per_check"]["audit"] == {"A": [0, 2], "B": [2, 2]}
    assert abs(s["conditions"]["A"]["cost_usd"] - 0.02) < 1e-9
    assert s["per_task"]["x"]["B"]["both"] == 1
