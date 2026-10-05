# Cognitive-Debt Paydown Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web tool that scores a GitHub repo's files on a Cognitive Debt Index (0–100), then autonomously refactors the worst file, adds a passing test, writes an explanation-gate intent note, and opens a pull request — with a dashboard showing the debt trend dropping.

**Architecture:** Local ingestion + static analyzer compute a deterministic per-file debt score (zero LLM tokens). An agent loop (Nemotron Super via Nebius Token Factory) plans refactors, edits, writes/validates tests, and opens PRs through the GitHub API. A FastAPI web app serves an overview, file drill-down, and audit trail. A Tavily runtime call resolves deprecated APIs. A sqlite knowledge base persists intent notes (feeds the Intent-coverage signal).

**Tech Stack:** Python 3.12, uv, FastAPI, OpenAI SDK (→ Nebius Token Factory), Nemotron 3 Super + Lightning, Tavily SDK, GitHub API, radon, tree-sitter, sqlite3.

**Spec:** `docs/design-spec.md` (travels with this plan; executors read both).

## Global Constraints

- Python >= 3.12; manage deps with **uv** (no pip/requirements.txt manually).
- Every LLM call must hit Nebius **Token Factory** at `https://api.tokenfactory.nebius.com/v1/` via the OpenAI SDK with an `nvidia/*` model ID.
- Reasoning/agent calls use `nvidia/nemotron-3-super-120b-a12b`; cheap routing uses `nvidia/Nemotron-3_5-Lightning`.
- Do not hardcode API keys — read `NEBIUS_API_KEY`, `GITHUB_TOKEN`, `TAVILY_API_KEY` from env.
- The Debt Index must be computed **locally with no LLM calls** (budget constraint).
- Every task ends with a test that passes and a git commit.

## Review Focus

- A file the analyzer cannot parse must be skipped, not crash the whole run.
- A repo with zero git history (fresh clone, no commits) must still score by code signals only — Churn must not divide by zero.
- Missing env API keys must produce a clear error message, not a traceback.
- The agent must not open a PR when the refactor changes behavior (test fails) — it must surface the failure, not submit broken code.
- A file with no docstrings/comments must score low on Intent coverage (high debt), never an exception.

---
## Task 1: Project Scaffolding + Config

**Files:**
- Create: `pyproject.toml`
- Create: `config/signals.yaml`
- Create: `src/paydown/config.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `load_signal_weights() -> dict[str, float]` and `load_thresholds() -> dict[str, dict]` (from `config/signals.yaml`), `get_env(key: str) -> str` (raises `ConfigError` with a clear message if unset).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
def test_load_signal_weights_returns_six_signals():
    from paydown.config import load_signal_weights
    w = load_signal_weights()
    assert set(w) == {"cognitive_complexity", "size_cyclomatic", "churn",
                      "coupling", "intent_coverage", "ai_provenance"}
    assert sum(w.values()) == 1.0

def test_get_env_missing_key_raises_config_error():
    import os, pytest
    from paydown.config import get_env, ConfigError
    os.environ.pop("NEVER_SET_XYZ", None)
    with pytest.raises(ConfigError):
        get_env("NEVER_SET_XYZ")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL (module `paydown` not found)

- [ ] **Step 3: Scaffold the project**

Run: `uv init --name paydown --python 3.12` then `uv add fastapi openai tavily-python radon tree-sitter httpx pyyaml pytest`

- [ ] **Step 4: Create `config/signals.yaml`**

Weights sum to 1.0: cognitive_complexity 0.30, size_cyclomatic 0.20, churn 0.15, coupling 0.15, intent_coverage 0.10, ai_provenance 0.10. Under `thresholds:` add a `generic` profile with each signal's high/low reference values (reasonable defaults for a mid-size Python file).

- [ ] **Step 5: Implement `src/paydown/config.py`**

`load_signal_weights()` reads `signals.yaml` `weights:` dict; `load_thresholds()` reads `thresholds:`; `get_env(key)` returns `os.environ[key]` or raises `ConfigError`.

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: scaffold project and config loading"
```

## Task 2: Source Files + Dependency Graph

**Files:**
- Create: `src/paydown/repo.py`
- Test: `tests/test_repo.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `analyze_repo(path: Path) -> RepoAnalysis` where `RepoAnalysis` has `.files: list[SourceFile]`, and `SourceFile` has `.path`, `.language`, `.lines`, `.source`, `.imports: list[str]`, `.incoming_deps: list[str]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_repo.py
def test_analyze_repo_skips_non_parseable_and_lists_files(tmp_path):
    from paydown.repo import analyze_repo
    p = tmp_path / "proj"
    (p / "a.py").write_text("def f():\n    return 1\n")
    (p / "b.txt").write_text("just text")
    (p / "broken.py").write_text("def (\n")  # unparseable
    res = analyze_repo(p)
    langs = {f.language for f in res.files}
    assert "python" in langs
    assert len(res.files) == 1  # broken.py skipped, b.txt not a code file
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_repo.py -v`
Expected: FAIL (module `paydown.repo` not found)

- [ ] **Step 3: Implement `src/paydown/repo.py`**

Walk the tree for code files (`.py`, `.js`, `.ts`, `.go`, `.rs`, `.java`, `.cpp`, `.c`). Parse with tree-sitter (Python grammar). Record `imports` from import/require/using statements. Compute `incoming_deps` by scanning all files' imports. Wrap parsing in try/except — an unparseable file is skipped, never fatal.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_repo.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: parse source files and dependency graph"
```

## Task 3: Debt Index Signals A–F

**Files:**
- Create: `src/paydown/signals.py`
- Test: `tests/test_signals.py`

**Interfaces:**
- Consumes: `analyze_repo`/`SourceFile`; `load_signal_weights`/`load_thresholds`.
- Produces: `signal_a_complexity(src: str) -> float`, `signal_b_size(src: str) -> float`, `signal_c_churn(repo: RepoAnalysis) -> dict[str, float]`, `signal_d_coupling(repo: RepoAnalysis) -> dict[str, float]`, `signal_e_intent(src: str) -> float`, `signal_f_provenance(src: str) -> float`, and `debt_index(file, signals_dict, weights, thresholds) -> float`. Churn and coupling return dicts keyed by file path; pure-code signals return a single float.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_signals.py
def test_debt_index_high_complexity_and_low_intent():
    from paydown.signals import debt_index, signal_a_complexity, signal_e_intent
    complex_src = "def a():\n  if x:\n    for i in y:\n      if z:\n        return 1\n"
    simple_src = "def b():\n    return 1\n"
    signals = {
        "cognitive_complexity": signal_a_complexity(complex_src),
        "size_cyclomatic": 0.9, "churn": 0.1, "coupling": 0.1,
        "intent_coverage": signal_e_intent(complex_src),
        "ai_provenance": 0.5,
    }
    w = {"cognitive_complexity": .30, "size_cyclomatic": .20, "churn": .15,
         "coupling": .15, "intent_coverage": .10, "ai_provenance": .10}
    hi = debt_index(signals, w, {})
    low_signals = dict(signals, cognitive_complexity=0.1, intent_coverage=0.9)
    lo = debt_index(low_signals, w, {})
    assert hi > lo

def test_signal_c_churn_empty_history_no_div_by_zero(tmp_path):
    from paydown.signals import signal_c_churn
    import subprocess
    # empty repo: no commits
    res = signal_c_churn(tmp_path)
    assert isinstance(res, dict)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_signals.py -v`
Expected: FAIL (module `paydown.signals` not found)

- [ ] **Step 3: Implement `src/paydown/signals.py`**

- `signal_a_complexity`: count `if/for/while/catch/else` + nesting depth (use `radon.complexity`).
- `signal_b_size`: normalized function length + cyclomatic from radon.
- `signal_c_churn`: `git log --format= --name-only` counts per file ÷ repo age; return `{path: 0.0}` for a repo with no commits (guard divide-by-zero).
- `signal_d_coupling`: len(`incoming_deps`) + layering-violation count, normalized.
- `signal_e_intent`: fraction of functions with a docstring or preceding comment; 0.0 if none.
- `signal_f_provenance`: heuristic — duplication ratio + missing-comment ratio; 0.0 baseline.
- `debt_index`: `100 * sum(weight * norm(signal))` where `norm` maps via thresholds (or a 0–1 default when thresholds are empty).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_signals.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: compute cognitive debt index signals"
```

## Task 4: File Ranking

**Files:**
- Create: `src/paydown/rank.py`
- Test: `tests/test_rank.py`

**Interfaces:**
- Consumes: `debt_index`, `analyze_repo`.
- Produces: `rank_files(repo: RepoAnalysis) -> list[FileScore]` where `FileScore` is `(path, score: float, breakdown: dict[str, float])`, sorted descending by score.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_rank.py
def test_rank_files_descending(tmp_path):
    from paydown.rank import rank_files
    from paydown.repo import analyze_repo
    p = tmp_path / "r"
    (p / "good.py").write_text("def f():\n    return 1\n")
    (p / "bad.py").write_text("def f():\n    if a:\n      for b in c:\n        if d:\n          pass\n")
    repo = analyze_repo(p)
    ranked = rank_files(repo)
    assert ranked[0].score >= ranked[-1].score
    assert ranked[0].path.name == "bad.py"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_rank.py -v`
Expected: FAIL (module `paydown.rank` not found)

- [ ] **Step 3: Implement `src/paydown/rank.py`**

For each `SourceFile`, compute all signals, call `debt_index`, collect into `FileScore`; sort descending by score.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_rank.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: rank files by cognitive debt index"
```

## Task 5: Token Factory Client (Nemotron)

**Files:**
- Create: `src/paydown/llm.py`
- Test: `tests/test_llm.py`

**Interfaces:**
- Consumes: `get_env`.
- Produces: `ChatMessage(role, content)`, `llm_complete(messages: list[ChatMessage], model: str = "nvidia/nemotron-3-super-120b-a12b") -> str` (wraps OpenAI SDK pointed at Token Factory), `llm_complete_cheap(messages) -> str` (uses `nvidia/Nemotron-3_5-Lightning`).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm.py
import pytest
def test_llm_complete_requires_env(monkeypatch):
    from paydown import llm
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    with pytest.raises(Exception):
        llm.llm_complete([{"role": "user", "content": "hi"}])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_llm.py -v`
Expected: FAIL (module `paydown.llm` not found)

- [ ] **Step 3: Implement `src/paydown/llm.py`**

Build `OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=get_env("NEBIUS_API_KEY"))`. `llm_complete` calls `chat.completions.create(model=..., messages=...)`, returns `choices[0].message.content`. `llm_complete_cheap` uses the Lightning model id. Raise a clear `ConfigError` if the key is missing.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_llm.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: Nebius Token Factory LLM client"
```

## Task 6: Agent Loop — Refactor + Test + Explanation Gate

**Files:**
- Create: `src/paydown/agent.py`
- Create: `src/paydown/knowledge.py`
- Test: `tests/test_agent.py`

**Interfaces:**
- Consumes: `llm_complete`, `llm_complete_cheap`, `rank_files`, `SourceFile`, `get_env`.
- Produces: `RefactorResult(path, refactored_source, explanation: str, test_passes: bool)`, `explanation_gate(source_before, source_after) -> str`, `run_fix(file: SourceFile, repo_path: Path) -> RefactorResult`. `knowledge.py` produces `save_intent(file_path: str, note: str)` and `load_intent(file_path: str) -> str | None` (sqlite-backed).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_agent.py
def test_run_fix_writes_explanation_and_does_not_publish_on_test_failure(monkeypatch):
    from paydown.agent import run_fix
    from paydown.repo import SourceFile
    # stub llm to produce a refactor whose test would fail
    def fake_complete(messages, model=""):
        return "# changed behavior incorrectly\ndef f():\n    return 99\n"
    monkeypatch.setattr("paydown.agent.llm_complete", fake_complete)
    sf = SourceFile(path="x.py", language="python", lines=2, source="def f():\n    return 1\n", imports=[], incoming_deps=[])
    res = run_fix(sf, repo_path="/tmp/nonexistent")
    assert res.test_passes is False
    assert res.explanation  # explanation gate always written

def test_save_and_load_intent(tmp_path, monkeypatch):
    from paydown.knowledge import save_intent, load_intent
    monkeypatch.setenv("PAYDOWN_DB", str(tmp_path / "k.db"))
    save_intent("a.py", "note")
    assert load_intent("a.py") == "note"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_agent.py -v`
Expected: FAIL (modules `paydown.agent`, `paydown.knowledge` not found)

- [ ] **Step 3: Implement `src/paydown/knowledge.py`**

sqlite-backed store (table `intents(file_path TEXT PRIMARY KEY, note TEXT)`). `save_intent` upserts; `load_intent` returns the note or `None`. DB path from env `PAYDOWN_DB`, default `paydown.db`.

- [ ] **Step 4: Implement `src/paydown/agent.py`**

`explanation_gate`: ask `llm_complete_cheap` for a note "what this file does / why / what breaks if you change X"; always returns a string. `run_fix`: call `llm_complete` asking for a refactored, simpler version of the file; write it to a temp copy; run its test in a subprocess; set `test_passes`; always write the explanation note to the knowledge base via `save_intent`. Never open a PR when `test_passes` is False.

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_agent.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: agent refactor loop with explanation gate and knowledge store"
```

## Task 7: Tavily Docs Lookup (bonus)

**Files:**
- Create: `src/paydown/tavily.py`
- Test: `tests/test_tavily.py`

**Interfaces:**
- Consumes: `get_env`.
- Produces: `lookup_docs(query: str) -> str` (calls Tavily search at runtime and returns the top result's content).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tavily.py
def test_lookup_docs_requires_env(monkeypatch):
    from paydown import tavily
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    try:
        tavily.lookup_docs("python 3.13 syntax")
        assert False, "should have raised"
    except Exception:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_tavily.py -v`
Expected: FAIL (module `paydown.tavily` not found)

- [ ] **Step 3: Implement `src/paydown/tavily.py`**

Wrap the Tavily client; `lookup_docs` runs a search and returns the top result content. Raise a clear `ConfigError` if `TAVILY_API_KEY` is missing. (Wire-in from the agent loop is deferred; the runtime call itself is the deliverable.)

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_tavily.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: Tavily runtime docs lookup"
```

## Task 8: FastAPI Dashboard (Overview + Drill-down + Audit)

**Files:**
- Create: `src/paydown/app.py`
- Create: `templates/index.html`
- Create: `templates/file.html`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `rank_files`, `analyze_repo`, `run_fix`, `load_intent`.
- Produces: FastAPI app with routes `GET /` (overview: repo debt trend, worst files, PR list), `GET /file/{path}` (drill-down: score + signal breakdown + intent note + "Auto-fix" button), `POST /file/{path}/fix` (runs `run_fix`, records a PR entry in the audit trail, returns result).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_app.py
def test_index_renders_repo_and_worst_files(tmp_path):
    from fastapi.testclient import TestClient
    from paydown.app import create_app
    app = create_app(project_path=str(tmp_path))
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200
    assert "Cognitive-Debt" in r.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_app.py -v`
Expected: FAIL (module `paydown.app` not found)

- [ ] **Step 3: Implement `src/paydown/app.py` + templates**

`create_app(project_path)` builds the FastAPI app, analyzing the repo at startup and exposing the three routes. Overview shows repo debt index (mean file score), a trend line (scores rerun across the last N commits, computed locally), the worst-5 files, and the audit/PR list. Drill-down shows the six-signal breakdown, the intent note from `load_intent`, and an Auto-fix button calling the fix route.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_app.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: FastAPI dashboard with overview and file drill-down"
```

## Task 9: PR Delivery via GitHub API

**Files:**
- Create: `src/paydown/publish.py`
- Test: `tests/test_publish.py`

**Interfaces:**
- Consumes: `get_env`, `RefactorResult`.
- Produces: `open_pr(repo_slug: str, branch: str, refactor: RefactorResult, base="main") -> str` (returns the PR URL).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_publish.py
def test_open_pr_requires_token(monkeypatch):
    from paydown import publish
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    try:
        publish.open_pr("user/repo", "fix-utils", None)
        assert False
    except Exception:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_publish.py -v`
Expected: FAIL (module `paydown.publish` not found)

- [ ] **Step 3: Implement `src/paydown/publish.py`**

Create a branch, commit the refactored file + added test, push, and open a PR (title/body include before→after score and the explanation note). Raise a clear `ConfigError` if `GITHUB_TOKEN` missing. Return the PR URL.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_publish.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: open pull request via GitHub API"
```

## Task 10: End-to-End Wiring + README

**Files:**
- Create: `src/paydown/cli.py`
- Create: `README.md`
- Modify: `src/paydown/app.py` (wire `open_pr` into the fix route when `test_passes`)
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: everything above.
- Produces: CLI entrypoint `paydown <repo-path>` that prints the ranked files and runs a fix on the worst, and `paydown serve <repo-path>` that starts the dashboard. Wires `publish.open_pr` into the app's fix route.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
def test_cli_help_prints_usage(capsys):
    from paydown.cli import main
    try:
        main(["--help"])
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "paydown" in out.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL (module `paydown.cli` not found)

- [ ] **Step 3: Implement `src/paydown/cli.py` + README + app wiring**

`main` handles `--help`, `analyze`, and `serve` subcommands. Wire `open_pr` into the app fix route (only when `test_passes` is True). README documents setup, env vars, the Debt Index formula, the hard submission-gate compliance, and run instructions.

- [ ] **Step 4: Run full test suite**

Run: `uv run pytest -v`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: CLI, README, and end-to-end wiring"
```

## Out of Scope for this Plan (next iterations)

- Knowledge & Questioning layer beyond `knowledge.py` (Task 6) — a full evidence-cited Q&A (embeddings + vector store) is the stretch pillar to plan separately.
- Multi-file batched fixes.
- Full AI-provenance ledger.
- Nebius Serverless deployment.
- Producing the demo video (done at submission time).