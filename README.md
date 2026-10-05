# clarify

**The confusion-meter for code that pays down cognitive debt automatically.**

`clarify` is an agentic developer tool that scores every file in a GitHub repo on a **Cognitive Debt Index (0–100)**, then autonomously refactors the most confusing file, adds a passing test, writes an "explanation gate" intent note, and opens a pull request — so you can watch your codebase's debt trend drop, file by file.

Cognitive debt is the gap between *what a codebase is* and *what anyone understands it to be*. It's real, measurable, and currently unmeasured. Teams can't see which files nobody understands, so confusing code quietly accumulates until it becomes unchangeable. `clarify` makes that debt visible as a number, and then does the boring, risky work of paying it down for you.

## Why it matters

- **Measured, not vibes.** No tool ships a numeric comprehension metric *plus* an automated fix loop. `clarify` is the first confusion-meter that proves its own work by showing the score drop.
- **Explainable.** Every debt score decomposes into six weighted, deterministic signals — no black-box LLM math.
- **Autonomous but safe.** The agent never merges broken code: it validates its own refactor before opening a PR.
- **Self-documenting.** Every fix leaves behind an "explanation gate" — a persisted note on what a file does, why, and what breaks if you change it.

## Key features

- **Cognitive Debt Index (0–100)** — a deterministic, per-file comprehension score (computed locally, zero LLM tokens) that ranks every file worst-first.
- **Agent auto-fix loop** — a coding agent plans, refactors, writes, and validates a test for the worst file with minimal human input.
- **Explanation Gate** — before any merge, the agent writes an intent note (`what / why / what-breaks`) that makes the refactor auditable and feeds the knowledge layer.
- **PR delivery** — creates a branch, commits the refactored file + new test, and opens a pull request via the GitHub API with before→after score in the body.
- **Dashboard** — a FastAPI web UI with repo-level debt trend, worst-file ranking, per-file signal breakdown, an audit/PR trail, and an **Auto-fix** button.
- **Tavily docs lookup** — live web research at runtime to resolve deprecated APIs and outdated patterns against current documentation.
- **Knowledge layer** — every Explanation Gate note is persisted to a per-file SQLite store, feeding the intent-coverage signal and forming the seed of a natural-language Q&A layer.

## How the Cognitive Debt Index works

Each file gets a score from **0 (crystal clear) to 100 (unintelligible)**, a weighted blend of six deterministic signals. The weights are configurable in `config/signals.yaml`:

| Signal | Weight | What it measures |
|---|---|---|
| **A. Cognitive complexity** | 30% | Nesting depth + control-flow branches + breaks |
| **B. Size & cyclomatic overhead** | 20% | Function length + branching paths a reviewer must hold in memory |
| **C. Churn & instability** | 15% | Commit frequency / file age from git history |
| **D. Coupling / blast radius** | 15% | Incoming dependencies + layering violations |
| **E. Intent coverage** | 10% | Presence of docstrings, comments, and tests explaining the "why" |
| **F. AI-provenance signal** | 10% | Heuristic flag: agent-generated style with no explanation attached |

```
debt_index = 100 × (0.30·norm(A) + 0.20·norm(B) + 0.15·norm(C)
                  + 0.15·norm(D) + 0.10·norm(E) + 0.10·norm(F))
```

Each raw signal is normalized to 0–1 against file-type-aware thresholds, so a mid-size Python file is scored fairly against a large TypeScript module. Because the metric is computed locally with static analysis (radon + tree-sitter), scoring an entire repo costs nothing in tokens — the LLM is reserved for the hard reasoning work.

## Tech stack

- **Python 3.12** + **uv** for dependency management
- **FastAPI** backend + lightweight web dashboard
- **OpenAI SDK** → **Nebius Token Factory** inference endpoint
- **NVIDIA Nemotron 3 Super** (`nvidia/nemotron-3-super-120b-a12b`) for reasoning / the agent loop
- **NVIDIA Nemotron 3.5 Lightning** for cheap classification & routing
- **Tavily SDK** for live documentation lookup
- **GitHub API** for cloning repos and opening PRs
- **radon** + **tree-sitter** for local static analysis
- **SQLite** for the knowledge base of intent notes

## Hackathon context

`clarify` is built for the **NVIDIA x Nebius Global AI Hackathon (2026)** — **Coding & Agentic Engineering track** (an agent that *plans, writes, tests, and iterates on a real repo*).

It satisfies the submission gate and sponsor fit by design:

- **Runtime Nebius Token Factory calls** on every AI operation (reasoning via Nemotron 3 Super, cheap routing via Lightning).
- **NVIDIA Nemotron** open-source models throughout, with deliberate token-efficient model routing.
- **Tavily at runtime** — a live docs-lookup call, targeting the Best Use of Tavily bonus.
- A **credible, specific audience**: developers and teams who inherit and maintain code they don't understand.

## Status & roadmap

`clarify` is an **active MVP (v0.1) in development**. The design and implementation plan are finalized; the scoring engine, agent loop, dashboard, and delivery pipeline are being built out task-by-task against a passing test suite.

**Planned / in progress (MVP core):**
- [ ] Signal computation (A–F) and per-file Debt Index
- [ ] File ranking, worst-first
- [ ] Agent auto-fix loop with test validation
- [ ] Explanation Gate + SQLite knowledge store
- [ ] FastAPI dashboard (overview, drill-down, audit trail)
- [ ] GitHub PR delivery
- [ ] CLI (`analyze` / `serve`) and end-to-end wiring

**Stretch / next iterations:**
- Knowledge & Questioning layer — natural-language Q&A over the codebase with evidence-cited answers (embeddings + vector store)
- Multi-file batch fixes
- Full AI-provenance ledger
- Deployment to Nebius Serverless

## Contributing

Help make codebases more human. Whether you're a maintainer tired of `:set nomodeline` archaeology, an agentic-engineering enthusiast, or someone who just wants to see the confusion-meter in action — contributions are welcome.

Open an issue to discuss a feature or bug, and feel free to open a PR. Good first areas: tuning the signal thresholds, adding file-type profiles, improving test coverage, and building out the knowledge layer. If you're exploring the agent loop or the metrics, the docs in `docs/` are a good place to start.

## License

Licensed under the [MIT License](LICENSE).