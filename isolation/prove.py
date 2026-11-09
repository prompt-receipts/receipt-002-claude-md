"""Isolation proof for receipt 002. Run: OWNER_PROBE=<phrase> PYTHONPATH=../harness python isolation/prove.py

1. Positive control: with --setting-sources user,project the model can quote a rule that exists only in
   the owner's global CLAUDE.md. With the flags the real runs use (project only), it must say NONE.
2. Project canary: a CLAUDE.md in the working directory (the only thing condition B adds) IS loaded
   with the real flags, and is absent when the file is absent (condition A).
3. Records the init event (tools, MCP servers, plugins, skills, agents, memory path) for both settings.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from receipts_harness import agentic

import hashlib
import os

# The probe phrase names a rule that exists only in the owner's private global CLAUDE.md. It is read
# from the environment so it is never committed: OWNER_PROBE="<phrase>" python isolation/prove.py
PROBE = os.environ.get("OWNER_PROBE", "")
Q_GLOBAL = (f"If you were given an instruction about a phrase '{PROBE}', quote the trigger rule "
            "in under 12 words. If you were not given any such instruction, reply exactly NONE.")
Q_CANARY = ("If your project instructions contain a canary word, reply with that word only. "
            "If they do not, reply exactly NONE.")


def ask(prompt, sources, cwd):
    flags = [f for f in agentic.AGENT_FLAGS]
    flags[flags.index("--setting-sources") + 1] = sources
    flags[flags.index("--tools") + 1] = ""
    flags = [f for f in flags if f != "--allowedTools" and f != agentic.TOOLS]
    cmd = ["claude", *flags, "--model", "haiku"]
    r = subprocess.run(cmd, input=prompt, cwd=cwd, env=agentic.clean_env(), capture_output=True, text=True)
    ev = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    res = next(e for e in reversed(ev) if e.get("type") == "result")
    init = next(e for e in ev if e.get("subtype") == "init")
    ans = res["result"].strip()
    redact = prompt == Q_GLOBAL and ans != "NONE"
    return {"answer": "[owner global rule, redacted]" if redact else ans,
            "global_rule_seen": (ans != "NONE") if prompt == Q_GLOBAL else None,
            "answer_sha256_12": hashlib.sha256(ans.encode()).hexdigest()[:12] if redact else None,
            "cost_usd": res["total_cost_usd"],
            "init": {"mcp_servers": init.get("mcp_servers"), "agent_count": len(init.get("agents") or []),
                     "skill_count": len(init.get("skills") or []),
                     "plugin_names": [p.get("name") for p in init.get("plugins") or []],
                     "memory_paths": init.get("memory_paths")}}


def main():
    out = {}
    with tempfile.TemporaryDirectory() as empty, tempfile.TemporaryDirectory() as canary:
        Path(canary, "CLAUDE.md").write_text("Canary word for this project: QUOKKA-4471.\n")
        out["global_rule_visible_with_user_source"] = ask(Q_GLOBAL, "user,project", empty)
        out["global_rule_visible_with_real_flags"] = ask(Q_GLOBAL, "project", empty)
        out["project_canary_present_condition_B_like"] = ask(Q_CANARY, "project", canary)
        out["project_canary_absent_condition_A_like"] = ask(Q_CANARY, "project", empty)
    out["total_cost_usd"] = sum(v["cost_usd"] for v in out.values() if isinstance(v, dict))
    Path(__file__).with_name("proof.json").write_text(json.dumps(out, indent=1))
    for k, v in out.items():
        if isinstance(v, dict):
            print(k, "->", v["answer"][:100])
            print("   seen:", v["global_rule_seen"], "agents:", v["init"]["agent_count"], "mcp:", v["init"]["mcp_servers"])


main()
