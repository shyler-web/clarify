# Cognitive Debt & AI Code Comprehension — Landscape Briefing (2025–2026)

> Research by subagent (Task: Map cognitive debt tool landscape). Date: 5 October 2026.
> Purpose: what exists, what won, and where the open gaps are for our product.

## Framing: the problem is now named and quantified

Cognitive/comprehension debt — "the growing gap between how much code exists and how much of it any human genuinely understands" — crystallized in early 2026:

- **Addy Osmani** (Google), *Comprehension Debt* (Mar 2026): AI generates code 5–7x faster than humans comprehend it (140–200 lines/min vs 20–40).
- **Anthropic RCT** (Jan 2026, N=52): AI-assisted devs scored 50% vs 67% on comprehension (17-pt drop, worst in debugging).
- **Margaret-Anne Storey** (Univ. Victoria, *Triple Debt Model*, arXiv 2603.22106): Technical debt (code) + **cognitive debt** (people) + **intent debt** (externalized rationale).
- Supporting evidence: SonarSource survey (96% don't fully trust AI code), Faros AI (review time +91%), METR (AI users 19% slower despite feeling 20% faster), GitClear (duplication up 8x, refactoring halved), CodeRabbit (AI PRs 1.7x more issues, 2.74x more vulns).

## Existing tools — by category

### 1. Code explanation & documentation generation
- **DeepWiki** (Cognition) — repo-level docs, the industry baseline.
- **CodeWiki** (FPT Software, open-source, arXiv 2510.24428) — beats DeepWiki on its own benchmark (68.79% vs 64.06%); supports 7 languages; introduced **CodeWikiBench**.
- **DocAgent**, **RepoAgent** — multi-agent repository documentation.
- **Mintlify**, **GitBook** (auto-MCP + llms.txt, agent traffic analytics), **Promptless** (YC W25), **Fern**, **ReadMe** — docs platforms with AI write-assist and drift detection.
- **Tabnine**, **Codeium/Windsurf**, **Workik**, **Kodesage**, **CodexAgent** (repo summarization, refactor) — inline/legacy-code doc + explanation.
- **CodeSee** (dead) — was the notable "visualize system structure + living dependency maps" tool; its shutdown leaves a gap.

### 2. Comprehension / cognitive-complexity measurement
- **SonarQube/SonarCloud Cognitive Complexity** (Campbell, SonarSource, 2017) — the validated metric for *code* understandability (meta-validated: Muñoz Barón et al., ESEM'20). Note: it measures the code, not the humans' comprehension.
- **SonarQube, CodeClimate, Codiga, DeepSource, Sourcery, PMD, NDepend** — complexity/maintainability gates.
- **Exceeds AI** — blog/emerging product on measuring readability of AI code.
- **"Explanation Gate"** (Sankaranarayanan, Feb 2026) — forcing explanation of AI code before integration cut maintenance failure rate 77%→39%. Currently a research intervention, not a shipped product.
- **AIRELI persona taxonomy** (ACM 3794763.3794804) — research on AI-reliance personas (self-sufficient / understanding-gated / AI-steered), not tooling.

### 3. Architecture visualization & codebase mapping
- **ArchToCode** — AI Mermaid diagram generation (16 diagram types, repo/local, local-agent bridge for privacy).
- **Code2Flow AI** (VS Code ext) — AI flowcharts/architecture/call-graphs + time-complexity insights, multi-language incl. COBOL.
- **CodeScene** — code health/evolution hotspots; **Understand** (SciTools), **NDepend** — deep static metrics & call graphs; **PlantUML/Mermaid**.
- **Augment Code, Greptile** (syntax-tree + call-graph + relationship indexing), **Sourcegraph Cody** — codebase-aware AI with structural maps; **GraphDev** (below) — semantic graph w/ PR impact analysis.

### 4. Intent / code-ADR tooling
- **Archgate** — "Executable ADRs for AI governance."
- **Agent Decision Records (AgDR)** (GitHub) — decision records for agent-driven dev.
- **Catio** — architecture-decision system tied to *live state* (the layer above static ADRs, because ADRs go stale as agents rewrite).
- **metacto** — AI workflow for ADR drafts + diagrams + reviews.
- AI-generated ADRs (adolfi.dev/Claude Code scan; WebsiteInit's ADRs-for-agent-codebases) — working but hacky, prompt-driven, and (per practitioner critique) capture *implementation docs* rather than genuine *decisions*.

### 5. Agent-session comprehension (the emerging "where debt is incurred" category)
- **Maestro AI** — "Cognitive Debt Is a Session Problem, Not a Documentation Problem": measures the engineer–agent session to detect comprehension built vs deferred, intervening *before* the window closes at merge.
- **TraceVault** — captures agent conversations, tool invocations, reasoning chains, tied to commits/diffs — a persisting "reasoning trail."
- **amux** — agent orchestration/harness with task boards, shared memory, dashboards; frames itself around cognitive-debt prevention.

### 6. AI code review & security (adjacent)
- **CodeRabbit** (change walkthroughs + architectural diagrams, pre-merge quality gates), **Cursor Bugbot**, **Snyk**, **SentinelAI** (multi-agent semantic security review), **Greptile** (ripple-effect reviews).

## Notable projects / hackathon winners (2025–2026)

| Project | Event / Result | What it does |
|---|---|---|
| **Provenant** | **Microsoft Build AI Hackathon — National 1st place** (27,787 teams) | Open-source memory layer helping AI agents understand large repos without drowning in them; benchmarked on 500 GitHub issues. |
| **GraphDev** | **GitLab AI Hackathon — Grand Prize / Most Impactful** | Semantic codebase graph (tree-sitter → embeddings → HDBSCAN subsystems → UMAP); BFS ripple analysis reports structural PR impact + risk. |
| **CognitiveDebt** | Microsoft Agents League Hackathon 2026 | Multi-step reasoning agent producing dual-audience output: engineering debt map *and* CEO business case w/ ROI — no raw code sent (metadata only). |
| **CodeAncestry** | **nwHacks 2026 — Warp Best Developer Tool + MLH Best Use of Snowflake** | Turns Git commit history + diffs into a searchable semantic knowledge base (Snowflake Cortex), preserving tribal knowledge. |
| **DoomBot** | Codeissance 2026 (TSEC CodeStorm) winner | AI repo *maintainer*: reads issues, dedupes, flags security, opens draft PRs with fixes; MCP server exposing repo intelligence. |
| **Mytrix** | OpenAI Build Week 2026 | Reconstructs a repo's "memory" (purpose/architecture/decisions/risks) with hard evidence-citation and an anti-hallucination "AI mentor." |
| **REPOMIND** | AMD Developer Hackathon 2026 | On-prem 256K-context repo-scale coding agent on a single MI300X (reads full codebases for ~$4). |
| **Nexo** | MLH International Hacktown winner | Repo → interactive docs + dependency graphs + AI-generated "code podcasts" (ElevenLabs) for multimodal onboarding. |
| **Clarum** | LingHacks VII winner + Honorable Mention | Repo onboarding: overview, architecture, dependency graph, "read-this-first" path. |
| **SentinelAI** | MLH Google x Gemini.exe 2.0 | Multi-agent "Code Review Crew": semantic security auditing + auto `.patch` remediation. |
| **amneAI** | IBM Bob Hackathon 2026 | "Cure for codebase amnesia": 7-section plain-English codebase guide w/ enterprise/local mode. |
| **CodeInsight** | OpenAI Hackathon — Developer Tools | "Google Maps for software": architectural knowledge graph, cited repo Q&A, docs, bug-impact prediction. |
| **RepoLens** | AWS Amazon Nova Hackathon | 1M-token single-context "senior architect" agent (LangGraph) visualizing/auditing/explaining repos, no RAG needed. |
| **Tessera, DevPilot AI, Repository Intelligence Layer** (Kaggle Vibe Coding Capstone), **Code2Flow AI** | Various 2026 | Repo intelligence, doc generation, onboarding guidance. |

## Key gaps / open opportunities

1. **No deployable metric for comprehension itself.** Cognitive complexity measures the *code*; the Triple Debt Model notes cognitive debt "resides in cognition" and "nothing in your measurement system captures it." Everything today is lab studies, manual whiteboarding audits, or anecdotes. **Opportunity: a CI-friendly, continuous comprehension-debt index** (combining churn, coupling, AI-provenance, intent-coverage, and "can-you-explain-it" probes).

2. **Intervention happens after the comprehension window closes.** Maestro's core critique stands and is only partly filled: review-gate/documentation approaches surface debt *after* commit, but debt is incurred *in the agent session*. Most tools document later; almost none shape the live session to force comprehension-building interactions. **Open: session-native tooling that measures acceptance-vs-interrogation and scaffolds comprehension during generation.**

3. **AI provenance / "who understood what" is untracked.** No mainstream tool marks which lines were AI-written, which a human actually verified, and which were accepted on trust. TraceVault is early. This is foundational for any comprehension ledger.

4. **Intent/ADR capture is still manual and post-hoc.** Current ADR generators (adolfi.dev, WebsiteInit) produce *implementation documentation* in ADR shape, not genuine captured decisions; practitioner critique explicitly calls this out. **Open: automatic extraction of decisions + rationale from agent traces, git history, and PR discussions** — and ADRs that verify against *live* system state (Catio's direction, largely unbuilt).

5. **Repo-level docs quality is low and unmeasured.** DeepWiki/CodeWiki top out ~64–69%; cross-module, multi-language, non-hallucinating repo docs are unsolved; there's no standard benchmark beyond CodeWikiBench. **Opportunity: better eval + grounded evidence-cited docs** (Mytrix/amneAI show "cite a real file or omit" as a differentiator few tools enforce).

6. **Multi-repo / enterprise-scale understanding is unsolved.** Augment/others admit 100K+ file, multi-repo comprehension still fails. Combine with no good comprehension benchmark = greenfield.

7. **"Fragile experts" detection is unaddressed at org level.** Epistemic-debt research (77% failure on AI-blackout maintenance) and the junior-hiring data suggest skill erosion is real, but **no tool measures skill/comprehension regression over time** for teams. This is a measurement + training-loop opportunity.

8. **Metrics gaming / Goodhart risk.** SonarQube literature already warns over-extraction → "call-graph labyrinth" (scores look great, code is incomprehensible). Any new metric must be validated like Cognitive Complexity was, or it'll be gamed.

**Highest-leverage white space:** an **organization-level comprehension-health platform** that (1) captures agent-session interaction data, (2) tracks AI provenance + intent coverage, (3) enforces a "explain-it-before-merge" gate, (4) produces evidence-grounded, continuously-updated repo knowledge, and (5) reports a validated, game-resistant comprehension-debt index to leadership — effectively making "the comprehension work" visible the way DORA made delivery visible.

## Source URLs

**Foundational essays/research**
- https://addyosmani.com/blog/comprehension-debt/ (Osmani, Mar 2026)
- https://arxiv.org/abs/2601.20245 (Anthropic "How AI Impacts Skill Formation" RCT)
- https://arxiv.org/abs/2603.22106 (Storey, Triple Debt Model)
- https://arxiv.org/html/2604.13277v1 (Comprehension Debt in GenAI projects, 4 patterns)
- https://arxiv.org/abs/2602.20206 (Epistemic debt / "fragile experts")
- https://newsletter.getdx.com/p/cognitive-debt-the-hidden-risk-in (Abi Noda/Storey)
- https://leaddev.com/ai/ai-coding-creates-two-kinds-of-debt-youre-only-measuring-one
- https://dl.acm.org/doi/pdf/10.1145/3794763.3794804 (AIRELI personas)
- https://oreillyradar.substack.com/p/comprehension-debt-the-hidden-cost
- https://biggo.com/news/202509301913_AI_Code_Comprehension_Debt_Crisis (Peter Naur theory-building)
- https://virtuslab.com/blog/ai/cognitive-debt-the-code-nobody-understands
- https://dev.to/moksh/cognitive-debt-the-hidden-cost-of-letting-ai-write-your-code-5d5c
- https://amux.io/guides/cognitive-debt-ai-coding/
- https://www.augmentcode.com/guides/comprehension-debt-ai-code-review

**Tools/products**
- https://getmaestro.ai/blog/cognitive-debt-session-problem (Maestro)
- https://www.gitbook.com/blog/best-ai-documentation-tools · https://www.mintlify.com/library/best-code-documentation-tools
- https://arxiv.org/html/2510.24428v2 (CodeWiki + CodeWikiBench, github.com/FSoft-AI4Code/CodeWiki)
- https://kodesage.ai/blog/ai-documentation-tools-for-legacy-code (CodeSee, Tabnine, Codeium, Workik)
- https://archtocode.com/blog/from-source-code-to-architecture-diagram-top-tools-for-automated-code-mapping (ArchToCode, CodeScene, Understand, NDepend)
- https://dev.to/forgotten_areeb/code2flow-ai-visualizing-code-architecture-using-ai-24
- https://www.builder.io/blog/best-ai-tools-2026 (CodeRabbit, Greptile, Cursor Bugbot)
- https://www.augmentcode.com/tools/13-best-ai-coding-tools-for-complex-codebases
- https://blog.exceeds.ai/ai-code-readability-measurement/
- https://neurolaunch.com/cognitive-complexity-sonar/ · https://arxiv.org/pdf/2007.12520 (Cognitive Complexity validation)
- https://codemyspec.com/blog/architectural-decision-records (Archgate, AgDR)
- https://www.catio.tech/blog/architecture-decision-record · https://adolfi.dev/blog/ai-generated-adr · https://websiteinit.com/blog/architecture-decision-records-for-ai-agent-codebases
- https://www.metacto.com/blogs/leveraging-ai-for-system-design-and-architecture-decisions

**Hackathon projects/winners**
- https://www.linkedin.com/posts/shreyashs_microsoftbuildai-aiengineering-opensource-activity-7487805460725805056 (Provenant)
- https://devpost.com/software/graphdev (GraphDev)
- https://github.com/singh-yash129/CognitiveDebt-Technical-Debt-Intelligence-Agent
- https://devpost.com/software/codeancestory (CodeAncestry)
- https://www.linkedin.com/posts/swapnil-ambad-479605326_codeissance2026-hackathon-ai-activity-7497278017824587777 (DoomBot)
- https://github.com/Manasi200609/Mytrix
- https://github.laiyagushi.com/SRKRZ23/repomind (REPOMIND)
- https://github.com/Hacktown-BSB/Nexo
- https://devpost.com/software/clarum
- https://github.com/StarDust-Git-Code/sential.ai (SentinelAI)
- https://github.com/ranfarrr/amneai (amneAI)
- https://devpost.com/software/codeinsight-google-maps-for-software-systems
- https://devpost.com/software/repolens-1x7rfu (RepoLens)
- https://devpost.com/software/tessera-wfbvty · https://devpost.com/software/devpilot-ai-u423ob
- https://www.kaggle.com/competitions/vibecoding-agents-capstone-project/writeups/repository-intelligence-layer

*Note: several figures (17% comprehension drop, 91% review increase, 1.7x/2.74x defect ratios) come from vendor or survey sources with varying methodology; the strongest, peer-reviewed anchor is the Anthropic RCT and the Storey/UVic papers. Treat vendor-reported numbers as directional.*