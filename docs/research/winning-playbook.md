# AI Hackathon Winning Playbook — NVIDIA x Nebius Global AI Hackathon (2026)

> Research by subagent (Task: Research winning AI hackathon projects). Date: 5 October 2026.
> Purpose: track-by-track guidance, winning patterns, judging criteria, and sponsor-tech fit.

## Track-by-track guidance

**The universal gate:** *Every* submission must (1) run on **Nebius Token Factory** or **Nebius AI Cloud**, and (2) use **at least one NVIDIA open-source model** (Nemotron, GR00T, Cosmos, or Sonic). "Runs on Token Factory" = a **runtime call to the Token Factory inference API** (OpenAI-compatible chat completions). This is a hard pass/fail gate, not a preference.

| Track | Baseline (just ok) | Winning bar (judges' own words) |
|---|---|---|
| **1. Coding & Agentic Engineering** — coding agents & developer tools that write, run, and **test code in Token Factory Sandboxes** | A code-completion wrapper | "An agent that **plans, writes, tests, and iterates on a real repo with minimal human input**" |
| **2. Best Apps & Agents** — any app/agent someone would actually use | A single API call demo | "A **multi-step autonomous workflow that chains tools end to end**" |
| **3. Personal AI** — always-on private assistant, persistent memory, data under your control | A chatbot with a system prompt | "An assistant that **remembers context across sessions and takes real action on your behalf**" |
| **4. Physical AI** — robotics / IoT / on-device intelligence | A scripted demo | "**Hardware reacting live to real-world input**" |

**Prize structure (official):**
- **Overall:** Grand Prize **$20,000 cash** · 2nd **$10,000** · 3rd **$6,000**
- **Track winners:** each of the 4 tracks gets an **NVIDIA Jetson Orin Nano** (hardware, not cash)
- **Bonus — Best Use of Tavily: $3,000 cash** (requires a *functional, runtime call* to the Tavily API as part of the solution)
- **20 City Winner Awards** ($500 each) — only for attending an in-person *Builders & Brews* event
- **10 Most Valuable Feedback** ($100 + swag)

**Multiple-prize rule:** a project wins **one Overall award OR one Track award, plus one Bonus award**. Realistic best case for a remote entrant = cash Grand Prize + the $3k Tavily bonus. ~17,800 registered by early Oct 2026, but the narrow technical gate means the *completed* field is far smaller — finishing is the competitive edge.

## Winning project patterns

**Pattern 1 — "Real repo autonomy," not wrappers.** Depth over surface: an agent that closes a loop on real artifacts (plan → write → test → iterate) beats a chat wrapper. The Nebius organizers repeat this verbatim.

**Pattern 2 — multi-agent orchestration.** Grand-prize winners orchestrate multiple specialist agents over one coordinated workflow, not a single LLM call.
- **RiskWise** (Microsoft AI Agents Hackathon 2025, Best Overall, $20k): supply-chain risk analysis, multi-agent (Semantic Kernel, Azure AI Agent Service, Python + Next.js, SQL).
- **SalesShortcut** (Google ADK Hackathon 2025, Grand Prize): multi-agent SDR doing lead gen → research → proposal → outreach.
- **Apollo Deep-Research Meta-Agent** (Microsoft 2025, Best C#): meta-agent decomposing a query into sub-agents.
- **Deptheon** (Agents in the Loop 2025, 1st): tool-based agent chaining web research → **live phone calls** → email across 3,000+ APIs for hours unattended.

**Pattern 3 — an MCP server / dev-tool that makes an *agent* better.** 2025 developer-tooling winners were often **MCP servers** giving agents accurate, grounded tooling.
- **baseline-mcp** (Google Baseline Tooling Hackathon, 2nd): MCP server giving agents accurate web-compat data — praised for "steering agents towards generating more modern code."
- **PulseAI** (TreeHacks 2025): custom **MCP tool** feeding browser context into a coding assistant.
- **Agentic Software Factory** (Microsoft 2025): mini-factory of coding/research/testing agents with human-in-the-loop.

**Pattern 4 — grounded, non-obvious real-world problems.** Winners tie agents to a credible, specific audience and problem, and ground outputs in real data (Bing grounding, vector DBs, SQL) rather than raw generation.

**Pattern 5 — sponsorship-surface, demonstrated not claimed.** Winners explicitly integrate and *demonstrate* the sponsor stack and call it out in the video/repo.

## Judging criteria (Devpost-style)

**Nebius-specific two-stage judging (published in Official Rules):**

**Stage 1 — Pass/fail gate:** baseline viability + genuine fit with theme/track ("not a superficial rebrand of an unrelated idea").

**Stage 2 — Four equally weighted criteria, scored 1–5:**
1. **Technological Implementation** — how well it's built *and* how effectively it uses Nebius Token Factory/AI Cloud + the NVIDIA model (deep use of the required stack scores higher than incidental use).
2. **Design** — "a complete, coherent product experience, not just a technical proof of concept."
3. **Potential Impact** — a credible, *specific* case for solving a real problem for a real audience, backed by the demo.
4. **Quality of the Idea** — creative, non-obvious use of the required stack + genuine understanding of the problem space.

**Submission deliverables (mandatory, all judged):**
- Working demo URL (not required for Physical AI only)
- **≤3-min YouTube demo video** (must show it functioning + explain your use of Token Factory + NVIDIA model)
- **Public repo** (GitHub/GitLab/Bitbucket) with a **visible open-source license** (Apache 2.0/MIT/MPL-2.0) and a README with setup + run instructions
- Project description (what, why, how)
- **Required written feedback** on Nebius Token Factory, AI Cloud, NVIDIA tools (feeds "Most Valuable Feedback" award, part of every submission)
- If pre-existing, explanation of what was *significantly updated* during the submission window

**General Devpost norms:** judges weight **working demo > idea alone**, innovation, technical difficulty, real problem/specific audience, polish, depth of sponsor-tech use, and the video pitch. Judges may judge solely from description + video + repo — the video and README must carry the argument.

## Satisfying the sponsor-tech requirement & fit for a cognitive-debt tool

**What satisfies it (from Official Rules):** the project must "**make a runtime call to the Token Factory inference API**, or be deployed/run using Nebius AI Cloud compute (Serverless Jobs, Serverless Endpoints, or DevPods)" **AND** use **≥1 NVIDIA open-source model**. Concretely: backend hits an OpenAI-compatible endpoint like `base_url = https://api.studio.nebius.ai/v1` with `model = "nvidia/nemotron-3-super-120b-a12b"` at runtime. Tavily bonus requires a **live Tavily API call** in the running app.

**Model routing tip:** use **Nemotron 3 Ultra** for hard reasoning, **Nano/Super** for fast high-volume calls — keeps the app responsive and "credits stretch further." Demonstrating deliberate model selection is itself a "Technological Implementation" / "Quality of Idea" plus.

**Budget reality:** **$25** Token Factory credits via code `NEBIUS-DEVPOST-GLOBAL26`, plus **another $25** (plus Tavily + Nebius Academy credits) via the Nebius Builders Program. ~**$50** total — design for token efficiency.

**Does a cognitive-debt tool fit? Yes, strongly.**
- Maps naturally to **Coding & Agentic Engineering** (developer tooling), which organizers want "pushed past the basics."
- Winning pattern = a grounded dev tool that augments agents/developers with *accurate understanding of a real codebase* — exactly what cognitive-debt tools do (matches MCP-server winners like `baseline-mcp` and `PulseAI`).
- Nemotron is a strong fit (open, coding-capable, served on Token Factory): a "serious reasoning" model for deep code analysis + fast cheap models for classification, showing deliberate credit-efficient routing.
- To maximize the **Tavily bonus**, make the tool do runtime web research (resolve deprecated API/pattern by pulling current docs via Tavily).
- To win the *track* (Jetson) enter under Coding & Agentic Engineering; to win *cash* aim for the Overall Grand Prize (max one overall **or** one track, so target Overall + Tavily bonus).

## Source URLs

**Primary (official)**
- https://nebiusglobalaihackathon.devpost.com/
- https://nebiusglobalaihackathon.devpost.com/rules
- "Here's how judging works": https://nebiusglobalaihackathon.devpost.com/updates/46204-here-s-how-judging-works
- Kickoff tips: https://nebiusglobalaihackathon.devpost.com/updates/46203-kickoff-tips
- All updates: https://nebiusglobalaihackathon.devpost.com/updates
- Token Factory × Nemotron: https://nebius.com/services/token-factory/nemotron

**Verification / secondary**
- https://jobopportunity.info/opportunity/nebius-x-nvidia-global-ai-hackathon-2026
- https://tierones.io/opportunities/nebius-nvidia-ai-2026
- https://internshala.com/competitions/nebius-x-nvidia-global-ai-hackathon-2026

**Comparable winning-project examples**
- https://microsoft.github.io/AI_Agents_Hackathon/winners/ · https://techcommunity.microsoft.com/blog/azuredevcommunityblog/ai-agents-hackathon-2025-%E2%80%93-category-winners-showcase/4415088
- https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights
- https://web.dev/blog/baseline-hackathon-2025-winners
- https://devpost.com/software/deptheon-ai
- https://github.com/ekang7/PulseAI
- https://github.com/yli12313/AI-Agents-Hackathon-2025 (RedBot sponsor-integration pattern)
- https://huggingface.co/blog/kikikita/immersia-ai-games (LLMGameHub)