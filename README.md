# Receipt 002: does a CLAUDE.md file change what an AI coding agent does?

**Claim tested:** "A CLAUDE.md file makes Claude Code follow your project's rules."

**Verdict as measured: TRUE.** It matters most for rules the code cannot show.

| Rules the agent... | Without CLAUDE.md | With CLAUDE.md | Runs |
|---|---|---|---|
| **Round 2: cannot see in the code** (file location, test names, banned imports, docstring tag, changelog format) | **0 of 24** runs followed them all | **24 of 24** | 48 |
| **Round 1: can see in the code** (helper modules like `money` and `audit` sit in the repo) | 21 of 24 | 24 of 24 | 48 |

Model: Claude haiku (`claude-haiku-5-5`) running as an agent, Claude Code 2.1.319, 2026-11-07. Each run is a fresh
copy of a small repo, scored by static checks on what the agent wrote (code behavior was also tested, see below).

**In plain English**
- If a rule is something the agent can discover by reading your code, it mostly follows it anyway.
- If a rule lives only in your head (where files go, what to avoid, how to format a changelog line), the agent did not guess it once in 24 tries. The file fixed that every time.
- This is one small model, invented rules and small repos. It shows the direction, not how big the effect is for you.

Want to check it yourself? See [Reproduce](#reproduce). Everything below is as measured, including the parts that cut against the claim (round 1's gap rests on one task, and hidden-test pass rates were about equal).

---

## Round 2: rules the code cannot show (the headline result)

### Round 2 results (48 counted runs: 8 tasks x 3 runs x 2 conditions)

| Measure | A: no CLAUDE.md | B: with CLAUDE.md | B minus A | Task-level 95% interval | Fisher p (rough) |
|---|---|---|---|---|---|
| All convention checks pass | 0/24 (0%) | 24/24 (100%) | +100 points | +100 to +100 | < 0.001 |
| Hidden tests pass | 21/24 (88%) | 23/24 (96%) | +8.3 points | 0 to +25 | 0.61 |
| Both | 0/24 | 23/24 | +95.8 points | +87.5 to +100 | < 0.001 |

By check (A vs B): location 0/24 vs 24/24; tests file name 0/24 vs 24/24; docstring ticket line 0/24 vs
24/24; changelog line 0/24 vs 24/24; forbidden stdlib avoided 12/18 vs 18/18 (the 6 A failures used `re` or
`os.path`; only the 6 tasks that tempt them are counted).

- Not one of the 24 runs without the file met all five rules. It put new code in `core.py` or `src/shop/`, named tests `test_<name>.py`, and left the changelog and docstring tag out.
- Hidden tests: the only failures were `common_dir` (A 0/3, B 2/3), a path-handling task, which is a difficulty difference and not a rules effect. The 8-point gap is not significant.
- 5 of the 24 A runs edited an existing fixture file (`core.py`), 0 of B. No run reached outside its working directory.
- Cost for the 48 counted runs: $0.162 (A $0.071, B $0.091). Model `haiku` (`claude-haiku-5-5`), Claude Code 2.1.319, 2026-11-07.

What round 2 does NOT show: that every kind of instruction is followed (these five rules are simple and
explicit), anything about other models or larger repos, or that rules in a file beat rules given in the
prompt. The rules were invented for this fixture, and the checks are static.

### Round 2 design (pre-registered before any round 2 call)

Round 1 showed the agent mostly followed the rules by reading helper modules in the repo. Round 2 tests
rules that nothing in the code reveals. Round 1 (further down) is unchanged. Round 2 results are reported above this design.

- **Fixture** (`round2/fixture/`): a tiny package `src/shop/` with one function, a `CHANGELOG.md` whose
  Unreleased section is empty and whose only entry is `- initial release`, a `pytest.ini`, and no tests.
- **Rules** (`round2/conditions/CLAUDE.md`, condition B only): new modules in `src/shop/ext/<name>.py`;
  tests in `tests/test_<name>_cases.py`; do not use `re` or `os.path`; every public function's docstring
  has a line `Ticket: <ticket id>`; every change adds `- <ticket id>: <module name>: <short summary>` under
  `## Unreleased` in `CHANGELOG.md`.
- **Tasks** (`round2/tasks.yaml`): 8 small functions (slugify, key=value parsing, hashtags, basename,
  common directory, chunking, phone numbers, moving average). Each prompt gives a ticket id, asks for tests,
  and never mentions the rules. Six tasks tempt `re` or `os.path`; two do not.
- **Scoring:** hidden behavior tests that find the module wherever the agent put it (so a wrong location
  does not fail behavior), and five static checks: location, tests file name, forbidden stdlib, docstring
  ticket line, changelog line format. Reported separately and combined. Scorer validated against reference
  and naive solutions (`round2/tests/test_round2_scoring.py`).
- **Runs:** same as round 1: haiku, agentic `claude -p` with Read, Edit, Write, Bash, fresh copy per run,
  serial, interleaved (seed 32), same isolation flags, 8 tasks x 3 runs x 2 conditions = 48. A smoke run
  (1 task x 1 run x 2 conditions, canary in B's file) comes first; stop and report if the projected cost
  exceeds $3. Command: `python run.py run --round-dir round2`.

**Pre-run scorer fix (after the smoke run, before any counted round 2 run):** the smoke run showed the
agent sometimes puts the new function into the existing `core.py` instead of a new file, which the first
version of the hidden tests could not find. The hidden tests now find the function by name in any source
file, so wrong placement is judged only by the separate `location` check. Smoke runs are not counted.

---

## Round 1: rules visible in the code

**Round 1 summary: mixed, and thin.** With a CLAUDE.md the agent followed every project rule in 24 of 24
runs. Without it, 21 of 24. The whole gap comes from one task of eight (3 runs), where the agent used
`logging` instead of the project's audit helper. On the other seven tasks the agent followed the same rules
with no CLAUDE.md, apparently because it looked at the helper modules in the repo first (every run's transcript opens `app/money.py`). Hidden tests passed 24 of 24 in both
conditions. With this few tasks the interval on the gap includes zero, so this is a hint, not proof.

### Round 1 results (48 counted runs: 8 tasks x 3 runs x 2 conditions)

| Measure | A: no CLAUDE.md | B: with CLAUDE.md | B minus A | Task-level 95% interval | Fisher p (rough) |
|---|---|---|---|---|---|
| Hidden tests pass | 24/24 (100%) | 24/24 (100%) | 0.0 | 0.0 to 0.0 | 1.0 |
| All convention checks pass | 21/24 (88%) | 24/24 (100%) | +12.5 points | 0.0 to +37.5 points | 0.23 |
| Both | 21/24 | 24/24 | +12.5 points | 0.0 to +37.5 points | 0.23 |

Wilson 95% intervals: A conventions 69% to 96%; B conventions 86% to 100%; both hidden-test rates 86% to 100%.

By convention check (runs where the check applies, A vs B):

| Check | A | B |
|---|---|---|
| placement (file in `app/features/`) | 24/24 | 24/24 |
| money (integer cents, helper used, no float or round) | 15/15 | 15/15 |
| money formatting helper | 6/6 | 6/6 |
| errors (only `app.errors` types raised) | 15/15 | 15/15 |
| clock (`clock.now()`, no wall-clock calls) | 3/3 | 3/3 |
| http (`get_json` only) | 3/3 | 3/3 |
| audit (called `audit(...)`) | 9/12 | 12/12 |
| no print or logging | 0/3 | 3/3 |

By task: every task scored 3/3 on both measures in both conditions except `import_rows` (the prompt
asks to "report each skipped line"), where A was 3/3 on tests and 0/3 on conventions (it imported `logging`
and warned, with no `audit` call) and B was 3/3 on both. Per-run data is in `results.json`.

- Cost reported by the CLI for the 48 counted runs: $0.139 (A $0.068, B $0.071). Mean 8.75 turns per run in both conditions.
- No run touched files outside its working directory or looked toward `.claude` (transcripts scanned), and no run modified a helper module.
- Model `haiku`, resolved to `claude-haiku-5-5`. Claude Code 2.1.319. Date 2026-11-07.
- The smoke test (1 task, 1 run, 2 conditions, canary in B's file) cost $0.006 and is not counted. The isolation checks cost about $0.01 and are not counted.

### Round 1: what it does not show

Round 2 (above) tested exactly the hidden-rule case that this round did not.

- That CLAUDE.md files do not matter. In this fixture the rules were mostly visible in the code itself (helper modules named `money`, `audit`, `clock`, `http`, `errors`), and the agent looked at them. Rules that cannot be seen in the code (a team habit, a forbidden library that has no local wrapper, a naming scheme) were not tested, except the print and logging rule, which is where the one difference appeared.
- Anything about other models, larger repos, longer sessions, or ambiguous tasks.
- That the one observed gap is real. It rests on one task, 3 runs per condition, and the interval includes zero.
- Quality, readability or correctness beyond the hidden tests and the static checks.

### Round 1 method and design (committed before any task call, commit `5b1bc88`)

- **Fixture repo** (`fixture/`): a small Python app with helper modules for money (`app/money.py`),
  audit logging (`app/audit.py`), the clock (`app/clock.py`), HTTP (`app/http.py`) and errors
  (`app/errors.py`), plus one tiny feature module in `app/features/`. The helpers have one-line
  docstrings and nothing says which of them must be used.
- **Conventions** (`conditions/CLAUDE.md`): place new code in `app/features/<name>.py`; money is integer
  cents via `parse_money` and `fmt_money` and never float or `round()`; record state changes with
  `audit(...)` and never `print` or `logging`; get the time only from `clock.now()`; network only through
  `get_json`; raise only exceptions from `app.errors`; and the test command.
- **Condition A:** the fixture as is, no CLAUDE.md. **Condition B:** the same fixture plus that one file.
  Nothing else differs, including the task prompts, which never mention the conventions.
- **Tasks:** 8 short feature requests (`tasks.yaml`), e.g. refunds in basis points, token expiry, a rate
  lookup, a discount, closing an account, importing CSV rows, monthly totals, an account transfer.
- **Scoring, two separate measures, both deterministic:**
  1. *Hidden tests* (`tasks/<id>/test_hidden.py`): behavior only. Errors are accepted as any exception.
     The helper modules are restored to their original text before the tests run.
  2. *Convention checks* (`score.py`, AST-based): placement, money handling, audit call, no print or
     logging, clock use, HTTP helper use, and raising only `app.errors` types. Each task has the subset
     that applies to it. A run "passes conventions" only if every applicable check passes.
  A third column reports runs that pass both. The scorer is tested against reference solutions (pass
  everything) and plain "naive" solutions (fail conventions), see `tests/test_scoring.py`.
- **Runs:** `claude -p` as an agent with Read, Edit, Write and Bash, model `haiku`, in a fresh temporary
  copy of the fixture for every run, one run at a time, in randomized interleaved order (seed 31).
  8 tasks x 3 runs x 2 conditions = 48 runs.
- **Isolation:** each run uses `--setting-sources project` (so the owner's global CLAUDE.md, settings
  and hooks are not read), `--strict-mcp-config` with no servers, auto memory off, slash commands and
  skills off, a minimal environment, and no session saving. Proof in `isolation/proof.json`: a rule that
  exists only in the owner's global CLAUDE.md is quoted by the model when the user source is enabled and
  is not seen (`NONE`) with the real flags; a canary word in a project CLAUDE.md is seen with the real
  flags and not seen when the file is absent. The saved transcripts are also scanned for tool calls that
  reach outside the working directory or toward `.claude`.
- **Smoke test first** (1 task x 1 run x 2 conditions, with a canary instruction in B's file that is
  removed for the real run) to check the flags and the per-run cost. Smoke runs are not counted.
- **Cost stop:** if the projected full-run cost exceeds $3 (list-equivalent `total_cost_usd`), stop and
  report before the full run.
- **Statistics:** pass rates with Wilson 95% intervals; the B minus A difference with a bootstrap
  interval that resamples whole tasks; Fisher exact p as a rough pooled figure (runs on the same task
  are not independent). No result is excluded after the fact.

---

## Exact prompts (both rounds)

The 8 task prompts are in `tasks.yaml` and are the same in both conditions. Example (`import_rows`):

> Add a new feature called importer to this app. It should provide import_rows(lines), where each line looks like 'name,amount' (amount is a dollar string like '10.50'). Return a list of (name, cents) tuples for the valid lines, in order. Skip invalid lines: wrong number of fields, empty name, or an invalid amount. Report each skipped line so an operator can see which lines were dropped.

Condition B's only addition is `conditions/CLAUDE.md` copied into the repo root. The agent runs with the
default Claude Code system prompt in both conditions. Every run's saved diff is in
`raw/<condition>/<task>-<run>/patch.diff`, with the full transcript and call metadata beside it.

## Reproduce

```
# Harness: https://github.com/prompt-receipts/harness  (clone it next to this repo, as ../harness)
git clone https://github.com/prompt-receipts/harness ../harness
cd ../harness && python3.12 -m venv .venv && .venv/bin/pip install pyyaml pytest && cd -
export PYTHONPATH=.:../harness
PY=../harness/.venv/bin/python
$PY run.py run                         # round 1: 48 serial agent runs, resumable
$PY run.py run --round-dir round2      # round 2: 48 more
$PY run.py score                       # rescore saved patches, no model calls (add --round-dir round2)
$PY -m pytest tests -q                 # round 1 scorer self-tests
$PY -m pytest round2/tests -q          # round 2 scorer self-tests (run separately: shared module names)
OWNER_PROBE="<your phrase>" $PY isolation/prove.py   # isolation proof, see below
```

**The isolation proof needs your own probe phrase.** `isolation/prove.py` checks that a rule from your
personal global `~/.claude/CLAUDE.md` does not leak into the runs. Set `OWNER_PROBE` to a short, distinctive
phrase that appears only in YOUR global CLAUDE.md (for example the name of a custom rule you wrote there;
if you have no global CLAUDE.md, add a one-line rule with a made-up word first). The script asks the model
about that phrase twice, once with the user settings source enabled (the phrase should be quoted back) and
once with the flags the real runs use (it should answer `NONE`). The published `proof.json` records only
yes or no and a hash, because the author's phrase and rule text are private.

Needs the `claude` CLI logged in. Model outputs vary, so a rerun will not match exactly.
