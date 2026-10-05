# Cognitive-Debt Paydown Agent — Design Spec

> For the NVIDIA x Nebius Global AI Hackathon (2026).
> Track: Coding & Agentic Engineering. Status: v1 (MVP core + knowledge layer).

## Problem

Cognitive debt — "the gap between what a codebase is and what anyone understands it to be" — is real, measurable, and currently unmeasured. Teams can't see which files nobody understands, so confusing code accumulates until it becomes unchangeable. No tool today ships a *numeric comprehension metric* plus an automated fix loop.

## Product

**A "confusion meter for code" that automatically fixes the most confusing files and proves it by showing the score drop.**

- Point the tool at a GitHub repo.
- It scores every file **0–100** on a "cognitive debt index" (higher = harder to understand).
- Click **Fix** on the worst file → an agent refactors it, adds a passing test, writes an "explanation gate" intent note, and opens a **pull request**.
- A dashboard shows the debt trend going down after each PR.

## Goals / Non-Goals

**Goals (MVP core):**
- Compute a deterministic, explainable per-file Cognitive Debt Index.
- Rank files worst-first.
- One agent pass on a chosen file: refactor + add test + explanation-gate note + open PR.
- Web dashboard: overview, file drill-down, PR/audit trail.
- Meet the hackathon gate: runtime Nebius Token Factory call + NVIDIA Nemotron model.
- Functional runtime Tavily call (for the $3K Best Use of Tavily bonus).

**Non-Goals (v1):**
- Multi-file batch fixes, full AI-provenance ledger, multimodal analysis, deployment to Nebius Serverless (stretch, not required).

## Cognitive Debt Index (the metric)

Per-file score **0–100**, weighted blend of six deterministic signals (computed locally, zero LLM tokens):

| Signal | Weight | What it measures |
|---|---|---|
| A. Cognitive complexity | 30% | Nesting depth + control-flow branches + breaks |
| B. Size & cyclomatic overhead | 20% | Function length + branching paths a reviewer must hold |
| C. Churn & instability | 15% | Commit frequency / file age from git history |
| D. Coupling / blast radius | 15% | Incoming dependencies + layering violations |
| E. Intent coverage | 10% | Presence of docstrings/comments/tests explaining "why" |
| F. AI-provenance signal | 10% | Heuristic flag: agent-generated style + no explanation attached |

`debt_index = 100 × (0.30·norm(A) + 0.20·norm(B) + 0.15·norm(C) + 0.15·norm(D) + 0.10·norm(E) + 0.10·norm(F))`

`norm(X)` maps each raw signal to 0–1 using file-type-aware thresholds. Weights are configurable via YAML so judges see it is principled and tunable.

## Architecture

| Layer | Responsibility | Runs |
|---|---|---|
| **Ingestion** | Clone repo, enumerate files, build dependency graph | Local, free |
| **Static analyzer** | Compute signals A–F, produce per-file Debt Index | Local, free (radon / tree-sitter) |
| **Agent loop** | Nemotron Super: plan refactor → edit → write test → validate | Token Factory (small) |
| **Fast router** | Nemotron Lightning/Nano for cheap classification/retrieval | Token Factory (cheap) |
| **Explanation Gate** | Write "what/why/what-breaks" intent note before merge | Token Factory (small) |
| **Tavily** | Live-fetch current docs for deprecated APIs/patterns | Tavily (bonus) |
| **Delivery** | Open PR via GitHub API | Free |
| **Dashboard** | FastAPI + web UI: overview, file drill-down, audit trail | Local |

## Stack

- Python 3.12 + **uv**
- **FastAPI** backend + lightweight frontend
- **OpenAI SDK** → Nebius **Token Factory** (`https://api.tokenfactory.nebius.com/v1/`)
- **Nemotron 3 Super** (`nvidia/nemotron-3-super-120b-a12b`) for reasoning
- **Nemotron 3.5 Lightning** (`nvidia/Nemotron-3_5-Lightning`) for cheap routing
- **Tavily SDK** for runtime docs lookup
- **GitHub API** for clone + PR
- **radon** + **tree-sitter** for local static analysis
- **sqlite** for the knowledge base (intent notes)

## Knowledge & Questioning Layer (stretch, final pillar)

- **Knowledge layer:** every Explanation Gate output is persisted into a structured per-file store (what it does, why, what breaks). Feeds Intent-coverage signal E (stale/missing entries → higher debt).
- **Questioning layer:** natural-language query over the knowledge base + code with evidence-cited answers ("cite a real file or omit"). Uses Token Factory embeddings + local vector store.

Build order: Debt Index → Agent auto-fix + PR + Explanation Gate → Knowledge layer → Questioning layer. If time runs short, core (1+2) is still complete.

## Submission-Gate Compliance

- ✅ Runtime calls to **Nebius Token Factory** (every AI call).
- ✅ Uses **NVIDIA Nemotron** (Super + Lightning), open-source.
- ✅ Functional **Tavily** runtime call → $3K bonus.
- ✅ Coding & Agentic Engineering track (agent plans→writes→tests→iterates on a real repo).
- ✅ Public repo + README + ≤3-min video (produced at end).

## Open Questions / Constraints

- ~$50 Token Factory credit budget → token-efficient design (metric is local/free; LLM only on reasoning).
- Verify exact `nvidia/*` model IDs via `GET /v1/models` before finalizing.
- Nemotron model availability/pricing changes frequently.