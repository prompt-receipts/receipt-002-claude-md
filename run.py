"""python run.py {run,score,smoke} [--tasks a,b] [--runs N] [--out DIR]   (PYTHONPATH=../harness)"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from receipts_harness import agentic, core, stats  # noqa: E402

import importlib.util  # noqa: E402


def load_score(rd):
    spec = importlib.util.spec_from_file_location("score_mod", Path(rd) / "score.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def bases(tmp, rd, score, canary=False):
    md = (Path(rd) / "conditions" / "CLAUDE.md").read_text()
    if canary:
        md += "\nCanary: put the comment `# canary-quokka-4471` on the first line of every file you create.\n"
    return {"A": agentic.make_base(score.FIXTURE, Path(tmp) / ("canary" if canary else "real") / "A"),
            "B": agentic.make_base(score.FIXTURE, Path(tmp) / ("canary" if canary else "real") / "B", {"CLAUDE.md": md})}


def summarize(cfg, rows):
    s = {"name": cfg["name"], "model": cfg["model"], "runs_per_task": cfg["runs"],
         "tasks": len(cfg["tasks"]), "conditions": {}, "per_check": {}, "per_task": {}}
    metrics = {"hidden_pass": "Hidden tests pass", "conventions_pass": "All convention checks pass",
               "both": "Both"}
    for r in rows:
        r["both"] = r["hidden_pass"] and r["conventions_pass"]
    for c in "AB":
        rs = [r for r in rows if r["condition"] == c]
        d = {"n": len(rs), "cost_usd": sum(r["cost_usd"] for r in rs),
             "mean_turns": sum(r["turns"] or 0 for r in rs) / len(rs) if rs else None,
             "out_of_tree_runs": sum(1 for r in rs if r["out_of_tree"]),
             "helpers_modified_runs": sum(1 for r in rs if r["helpers_modified"])}
        for m in metrics:
            k = sum(r[m] for r in rs)
            d[m] = {"passes": k, "rate": k / len(rs) if rs else None, "wilson95": stats.wilson(k, len(rs))}
        s["conditions"][c] = d
        for chk in sorted({k for r in rs for k in r["checks"]}):
            have = [r for r in rs if chk in r["checks"]]
            s["per_check"].setdefault(chk, {})[c] = [sum(r["checks"][chk] for r in have), len(have)]
    for m in metrics:
        a, b = s["conditions"]["A"][m], s["conditions"]["B"][m]
        pt = {}
        for r in rows:
            pt.setdefault(r["task"], {"A": [], "B": []})[r["condition"]].append(int(r[m]))
        d, lo, hi = stats.cluster_bootstrap_diff(pt, seed=cfg["seed"])
        s[f"compare_{m}"] = {"A": f'{a["passes"]}/{s["conditions"]["A"]["n"]}',
                             "B": f'{b["passes"]}/{s["conditions"]["B"]["n"]}',
                             "diff_B_minus_A": d, "task_bootstrap95": [lo, hi],
                             "fisher_p": stats.fisher_exact(a["passes"], s["conditions"]["A"]["n"],
                                                            b["passes"], s["conditions"]["B"]["n"])}
    for t in cfg["tasks"]:
        s["per_task"][t["id"]] = {c: {m: sum(r[m] for r in rows if r["task"] == t["id"] and r["condition"] == c)
                                      for m in metrics} for c in "AB"}
    s["limits"] = cfg.get("limits", [])
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "score", "smoke"])
    ap.add_argument("--tasks")
    ap.add_argument("--runs", type=int)
    ap.add_argument("--round-dir", default=str(HERE), help="round directory (default: round 1 = this dir)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rd = Path(a.round_dir)
    score = load_score(rd)
    cfg = core.load_config(rd / "config.yaml")
    out = Path(a.out) if a.out else rd
    ver = core.claude_version()
    with tempfile.TemporaryDirectory() as tmp:
        b = bases(tmp, rd, score, canary=a.cmd == "smoke")
        if a.cmd == "smoke":
            b_real = bases(tmp, rd, score)
        if a.cmd in ("run", "smoke"):
            ids = a.tasks.split(",") if a.tasks else None
            n = agentic.run_agentic_capture(cfg, out, b, task_ids=ids, version=ver,
                                            runs=1 if a.cmd == "smoke" else a.runs)
            print(f"captured {n} new runs")
        if a.cmd == "smoke":
            b = b_real  # score smoke output against the real (non-canary) bases
        rows = agentic.score_agentic(cfg, out, b, score.score_tree)
        summ = summarize(cfg, rows)
        summ["cli_version"] = ver
        (out / "results.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))
        print(json.dumps({k: v for k, v in summ.items() if k.startswith("compare") or k == "conditions"}, indent=1, default=str))


if __name__ == "__main__":
    main()
