# Cognitive Debt: A Research Briefing

> Research compiled for the NVIDIA x Nebius Global AI Hackathon (2026).
> Date: 5 October 2026.

## Introduction

Cognitive debt is the fastest-rising concept in software engineering in 2026 — a term that captures a problem that has quietly existed for decades but that generative AI has transformed from a background nuisance into a first-order risk. Where "technical debt" describes problems *in the code*, cognitive debt describes problems *in the people*: the erosion of shared understanding about what a system does, why it does it, and who knows what. It is the growing gap between how much code a system contains and how much of it any human genuinely understands.

This briefing synthesizes current research, practitioner writing, and empirical studies to explain what cognitive debt is, where it comes from, how it is measured, how to reduce it, and why it matters specifically to anyone building maintainable AI applications and agents — including a software hackathon.

## 1. Definition, Origins, and Relationship to Other Debts

### What it is

Cognitive debt is commonly defined as **the accumulated gap between what a system actually is and what the team collectively understands it to be**. Margaret-Anne Storey, professor at the University of Victoria and the researcher most associated with formalizing the term, defines it precisely:

> "Cognitive debt is that understanding of what the system is doing and why, and who knows what across the team."

Technically, Storey frames it as a *team-level, project-level* property: the erosion of shared understanding and adequate mental models across a software system over time, manifesting as increasingly inadequate shared understanding for reasoning about and safely changing the system. It rests on a foundational idea from Peter Naur's 1985 paper **"Programming as Theory Building"**: a program is not its source code; it is the *theory* of the program that lives in the heads of developers — what the program does, how intentions are implemented, and how it can change. That theory is usually fragmented and distributed across the minds of many developers, so software health depends on *sufficient shared understanding*, not on any one person understanding everything.

### Who coined it and when

The term crystallized from **multiple independent directions in early 2026**, all reacting to AI-generated code outpacing human comprehension:

- **Margaret-Anne Storey** formalized *cognitive debt* and its companion *intent debt* in the arXiv paper **"From Technical Debt to Cognitive and Intent Debt"** (arXiv:2603.22106, published March 23, 2026), and popularized it in a February 2026 blog post and ICSE Technical Debt keynote.
- **Addy Osmani** (Google Chrome) independently coined the closely related term **"comprehension debt"** in a March 2026 post (later an O'Reilly Radar piece, April 2026): *"The growing gap between the volume of code in a system and how much of it any human being genuinely understands."*
- **John V Willshire** used "cognitive debt" earlier (April 2025) in a broader sense — "where you forgo the thinking in order just to get the answers, but have no real idea of why the answers are what they are" — largely in the context of LLMs at scale.
- An earlier meaning also exists in neuroscience/HCI: reductions in neural engagement during AI-assisted work (e.g., a 2024 Kosmyna et al. EEG study).

The concept is explicitly modeled on **Ward Cunningham's "technical debt"** (coined at OOPSLA 1992), and the debt metaphor intentionally parallels financial debt: borrowing lets you move fast now, but interest accrues until you pay it back.

### How it relates to (but differs from) technical debt and design debt

| | **Technical debt** | **Cognitive debt** | **Intent debt** |
|---|---|---|---|
| **Lives in** | The code | The people | The artifacts/knowledge |
| **Definition** | Implementation decisions that compromise future changeability | Erosion of shared understanding across a team | Absence of externalized goals, constraints, rationale |
| **Limits** | How systems can change | How teams can reason about change | Whether the system reflects what we meant to build |
| **Visibility** | High — surfaces via slow builds, failing tests, churn | Low — invisible, breeds false confidence | Low — missing docs and rationale |
| **Announces itself** | Yes, through friction | No | No |

Storey's **Triple Debt Model** is the cleanest current framing: technical debt lives in code, cognitive debt lives in people, and **intent debt** lives in artifacts (the missing rationale/constraints that both humans and AI agents need). This is often presented as the "three layers of software system health."

The key distinction: **clean, well-tested code can still carry massive cognitive debt** if no one can explain why it exists or safely change it. Technical debt makes systems harder to *change*; cognitive debt makes systems harder to *understand*; intent debt makes it hard to know what the system is *for*. "Design debt" is essentially a synonym for the code-side debt (technical debt's cousin), so the meaningful comparison is cognitive debt vs. the code-focus of technical/design debt. The three debts are **not independent** — they reinforce each other: intent debt causes cognitive debt (no documented purpose → no mental model), cognitive debt causes technical debt (misunderstanding → poor implementations), and technical debt amplifies cognitive debt (messy code is harder to reason about).

## 2. Causes: How Cognitive Debt Accumulates

Cognitive debt accumulates when *output velocity exceeds comprehension velocity* — when the team ships code faster than it can build and maintain mental models. Key causes:

**Engineering causes**
- **AI-generated code accepted without review.** A coding agent can produce 200 lines in 30 seconds; reading and building a mental model of them takes far longer. Most developers run tests, see green, and move on. This is the "generation–comprehension gap."
- **Passive delegation / "cognitive surrender."** Drawing on Kahneman's System 1/System 2, researchers Shaw & Nave describe *cognitive surrender*: adopting AI outputs with minimal scrutiny, bypassing both intuition and deliberation. This is distinct from healthy *cognitive offloading* (delegating syntax/boilerplate you already understand). Surrender *inflates confidence even when the AI is wrong*, which is why the debt stays invisible until it's too late.
- **Code volume + duplication.** GitClear's analysis of 211 million changed lines found code duplication rose ~8x in 2024, refactoring collapsed from ~25% to <10% of changed lines, and early churn nearly doubled.
- **Hidden state and complexity.** Deep nesting, tangled control flow, abrupt logic shifts, and unreadable abstractions raise the mental effort to understand code (the subject of the cognitive complexity metric).
- **Undocumented / poorly-documented systems** and unrecorded decision rationale (ADR debt / intent debt).

**Product and organizational causes**
- **Context switching** between prompt-crafting and code editing; METR identified switching overhead as a principal cause of measured slowdowns.
- **Reviewer bottleneck inversion.** A junior can now generate code faster than a senior can critically audit it. Review depth gets sacrificed for throughput, so "reviewed = understood" no longer holds.
- **Knowledge concentration and attrition.** Tacit knowledge walks out the door when the people who built the system leave; AI-assisted development can short-circuit the replenishment mechanism, so new engineers never form the intuition.
- **Incentive structures.** Organizations measure observable output (velocity, story points, features shipped), not comprehension. The incentive system selects for behaviors that accelerate debt accumulation.
- **Key-person dependency / bus factor.** Knowledge concentrates in individuals who rotate or leave.

## 3. Costs and Consequences

**On comprehension (the measured, most-cited evidence)**
- **Anthropic study (Shen & Tamkin, arXiv:2601.20245):** In a randomized controlled trial, junior programmers who used an AI assistant scored **50%** on a comprehension quiz of code they'd just written, vs. **67%** for the no-AI control — a 17-point gap. Developers who *delegated* ("write this") scored <40%; those who used AI as a *conceptual tutor* ("why does this work?") scored >65%.
- **MIT Media Lab (EEG, June 2025):** Brain connectivity and memory retention scaled downward as tool support increased; LLM users showed weaker neural engagement and reduced ownership of output — "cognitive disengagement."
- **Epistemic debt experiment (Sankaranarayanan, arXiv:2602.20206):** Under a 30-minute AI-blackout maintenance task, the unrestricted-AI group had a **77% failure rate** vs. **39%** for a group forced to explain AI code before integrating it (the "Explanation Gate"). Developers became "fragile experts" — fast at building, unable to maintain/debug.

**On productivity**
- **METR study:** Experienced open-source developers on large codebases were **19% slower** with AI assistance, yet believed AI had sped them up by ~20% — a large perception–reality gap. A follow-up showed real gains only after sustained exposure.

**On organizations**
- **Velocity illusion:** Cognitive debt is invisible to velocity metrics (DORA, story points, build times). It surfaces only as *lagging* indicators — longer MTTR, rising change-failure rate, delayed onboarding — months after the cause.
- **Onboarding** slows because new hires inherit systems no one can fully explain; teams may need longer onboarding windows.
- **Bug rates and incident severity** rise because on-call engineers debug "a black box written by a black box."
- **Burnout:** A distinct pattern of "high output + low confidence" — executing without grasping one's own output.
- **Strategic erosion:** Organizations "trade their pipeline of future Staff Engineers for this quarter's feature delivery" — juniors never form the scar tissue and intuition that create senior architects.

## 4. Measurement: Frameworks, Metrics, and Heuristics

**Static code metrics (for the code, a partial proxy)**
- **Cognitive complexity (SonarSource/SonarQube):** a metric quantifying the mental effort to read and understand code. Unlike cyclomatic complexity (which counts execution paths), it accounts for nesting depth, control flow, break/goto, and readability constructs. Automated via SonarQube/static analysis. *Caveat:* a 2023 neuroscience study (Hao et al.) found even these metrics deviate considerably from programmers' actual brain-measured comprehension.
- **Cyclomatic complexity** (V(g)): counts linearly independent paths — related but not the same.
- **Code churn, duplication ratio, refactoring ratio:** GitClear-style signals consistent with comprehension loss.

**Subjective workload measurement**
- **NASA-TLX (Task Load Index):** the gold-standard subjective workload questionnaire (developed by Sandra Hart at NASA Ames in the 1980s, now an iOS app), measuring mental demand, effort, frustration, etc. Useful for measuring *cognitive load* on tasks, distinct from measuring *debt* accumulated in a system.

**Team-level / debt-specific heuristics (from Storey's work and practitioners)**
- **Architecture whiteboard audit:** Ask several engineers to independently draw the system's architecture; where diagrams diverge, cognitive debt has accumulated.
- **Code explanation walk:** Ask the author of an AI-generated function (older than 2 weeks) to explain it without looking; track whether they can recover the reasoning.
- **Debugging dry run:** Give an engineer a bug in unfamiliar AI-generated code, with AI access removed, for 20 minutes; observe whether they can hypothesize and test independently.
- **Review-quality sampling:** Count PR comments that engage with *logic* vs. "LGTM"/test-pass confirmation; a declining logic-engagement ratio is an early signal.
- **The "can you explain what this does?" test** shifted to be the primary review question.
- **Comprehension quizzes / evaluation gates** (as in the Anthropic and epistemic-debt studies) to measure team understanding directly.
- Storey's paper frames diagnosis by separating *technical* (code), *cognitive* (people), and *intent* (artifacts) debt, so each can be assessed and mitigated separately.

**Important caveat from the research:** "Organizations cannot optimize for what they cannot measure." The core problem is that comprehension is not legible to standard dashboards, so incentive structures default to rewarding velocity.

## 5. Reduction and Mitigation: Paying Down Cognitive Debt

**Individual practices**
- **Apply the "Explanation Gate."** Before integrating any AI-generated code, explain it back — why it works this way and what would break if a part changed. This single intervention cut the maintenance failure rate from 77% to 39% with no measurable productivity cost.
- **Attempt first, then consult.** Work 15–30 minutes independently before opening the AI; the "productive struggle" is where schema formation happens.
- **Ask "why?" more than "write this."** Conceptual-inquiry prompting produces comprehension matching or exceeding no-AI groups.
- **Schedule no-AI days** to calibrate actual skill level against AI-inflated confidence.
- **Design before you generate.** Engage the AI in architecture/tradeoffs first so code generation fills an architecture you understand.

**Team and engineering practices**
- **Slow down deliberately** and use the practices Kent Beck calls "make the hard change easy": **pair programming, refactoring, and test-driven development** (recommended at a Martin Fowler / Thoughtworks retreat). TDD, refactoring, and code review are also the established, validated ways to manage *technical* debt.
- **Rebuild shared understanding** through pair work, rotating reviewers, and reviews focused on comprehension, not just correctness.
- **Document intent.** Capture decisions as Architecture Decision Records (ADRs) and externalized rationale to pay down *intent* debt, which directly prevents cognitive debt.
- **Modularize and reduce state.** Break systems into cohesive modules with explicit, enforced boundaries (fewer layers, less hidden state, smaller blast radius), which reduces the mental model each change requires.
- **Reduce context switching** and protect deep-work/flow time.
- **Audit quarterly** using the whiteboard / explanation-walk / dry-run exercises above.

## 6. Cognitive Debt and Maintainable AI Applications (Including a Hackathon)

Cognitive debt thinking maps directly onto building AI applications and agents — arguably more than for any other software category, because agents generate ambiguity and hidden behavior by nature.

**The core problem in AI apps**
- Agents produce **opaque, stateful, non-deterministic** behavior (LLM drift, tool-selection ambiguity, cascading failures, token explosions, context-window overflow). When no human understands the orchestration, the system becomes a black box that is nearly impossible to debug, govern, or extend.
- The classic failure mode is the **single-file agent monolith**: prompt, tool registry, agent loop, routes, DB session, and LLM client all in one `main.py` that "shipped," then grew to 900 lines where every change is a merge conflict. This is cognitive debt concretized.

**Engineering principles for agent codebases (that keep human and agent comprehension feasible)**
- **Modularity with enforced boundaries.** The 4-layer pattern (Routes → Services → Domain → Infrastructure) with one-directional dependency rules, enforced by a linter in CI (e.g., `import-linter`). Domain holds pure prompts/schemas/tool definitions with zero I/O; Services own the agent loop; Infrastructure handles the LLM client, DB, observability. This makes each change local and each layer testable.
- **"Maintainable codebase for AI coding agents" properties** (locality, small blast radius, boundary integrity, navigability, narrow rebuild/test scope): let an unfamiliar agent (or human) find the right context, make a narrow change, and verify it without loading the whole system into working memory.
- **KISS and flat, function-driven designs.** Avoid over-engineering and deep indirection; each layer of complexity adds ambiguity and token cost. Anthropic's guidance: *start simple with single-purpose agents*, and use multi-agent systems only when a genuinely single-purpose agent can't work (multi-agent uses ~10–15x more tokens).
- **Single-responsibility, single-tool agents** reduce tool-selection noise and make behavior predictable.
- **Externalized prompt management** (prompts as versioned configuration, not buried in code) — this is intent-debt discipline applied to agents.
- **Observability and tracing** of agent decision patterns and tool calls — without it, debugging emergent multi-agent behavior is nearly impossible.
- **Keep a "table of contents," not an encyclopedia** — treat files like `AGENTS.md` as navigability maps so both humans and coding agents can orient quickly (progressive disclosure of context).

**For a hackathon specifically**
- The tension is acute: you want speed to demo something impressive, but you will likely hand it off (or return to it later). The research offers a pragmatic dial rather than a zero-tolerance rule: **strategic cognitive debt is rational** (like a mortgage) *if* you have a plan to pay it back — a "good down payment" of knowing what you want to build, plus time later to read/understand the code. The danger is *reckless* debt: generating the wrong thing and then spending time learning the wrong thing, with no repayment plan.
- Practical hacks: use the **Explanation Gate** (even a 30-second self-explanation), keep the codebase modular from day one (a few hard boundaries, not a giant `main.py`), externalize your prompt/config so intent survives, enforce one-directional imports, and add minimal observability/tracing so behavior is legible. These cost little during a sprint but prevent the "can't change anything on day two" wall.

## Summary

Cognitive debt is the erosion of shared human understanding of a software system — distinct from and more dangerous than technical debt because it lives in people, is invisible to velocity metrics, and compounds as AI generates code faster than teams can comprehend it. Formalized in early 2026 by Margaret-Anne Storey (and independently as "comprehension debt" by Addy Osmani), it is built on Peter Naur's insight that a program is really a theory in developers' heads. Empirical studies show measurable comprehension drops (Anthropic: 50% vs 67%), productivity paradoxes (METR: 19% slower but felt faster), and failure spikes without scaffolding (77% vs 39%). It is caused by passive delegation, unreviewed AI output, undocumented rationale, hidden state, and context switching; it costs teams velocity, onboarding speed, and incident resilience. It can be partially measured via cognitive-complexity metrics, NASA-TLX, and team-level heuristics like architecture whiteboards and explanation walks — but the fundamental measurement gap remains. Mitigation centers on slowing down deliberately: explanation gates, pair programming, refactoring, TDD, documentation of intent, and modularization. For AI applications and agents — including in a hackathon — the same principles apply with extra force: enforce modular boundaries, externalize prompts and decisions, keep blast radius small, and maintain observability, so that both humans and agents can actually understand and safely change what was built.

## Sources

**Origin & definitions**
- Margaret-Anne Storey, "From Technical Debt to Cognitive and Intent Debt: Rethinking Software Health in the Age of AI" (arXiv:2603.22106) — https://arxiv.org/abs/2603.22106 and PDF https://arxiv.org/pdf/2603.22106
- Margaret-Anne Storey, "How Generative and Agentic AI Shift Concern from Technical Debt to Cognitive Debt" (blog, Feb 2026) — https://margaretstorey.com/blog/2026/02/09/cognitive-debt/
- Addy Osmani, "Comprehension Debt: The Hidden Cost of AI-Generated Code" (O'Reilly Radar) — https://www.oreilly.com/radar/comprehension-debt-the-hidden-cost-of-ai-generated-code/ and https://addyosmani.com/blog/comprehension-debt/
- John V Willshire, "What is Cognitive Debt?" — https://medium.com/@willsh/what-is-cognitive-debt-5182e4a4fa98
- Martin Fowler, "Fragments: April 2" (Triple Debt Model) — https://martinfowler.com/fragments/2026-04-02.html
- Simon Willison, "How Generative and Agentic AI Shift Concern from Technical Debt to Cognitive Debt" — https://simonwillison.net/2026/Feb/15/cognitive-debt
- Smilodon Software, "Cognitive Debt" — https://smilodon.co/blog/cognitive-debt
- OLS Consulting, "Cognitive Debt in Software Engineering: Definitions, Measurement, Impact, and Remediation" — https://olsconsulting.co/field-notes/cognitive-debt-definitions

**Technical debt background**
- Wikipedia, "Technical debt" (Ward Cunningham, OOPSLA 1992) — https://en.wikipedia.org/wiki/Design_debt
- P. Kruchten, "Technical Debt" — https://philippe.kruchten.com/wp-content/uploads/2012/08/kruchten-120821-techdebt.pdf
- Software Engineering Institute, "Managing Technical Debt: A Research Agenda" — https://www.sei.cmu.edu/library/file_redirect/2011_019_001_28828.pdf/

**Empirical studies**
- Shen & Tamkin (Anthropic), "AI and Comprehension" (arXiv:2601.20245) — https://arxiv.org/abs/2601.20245 (summarized in DevToolLab)
- Sreecharan Sankaranarayanan, "Epistemic Debt" (arXiv:2602.20206) — https://arxiv.org/abs/2602.20206
- MIT Media Lab, "Your Brain on ChatGPT" — https://www.media.mit.edu/publications/your-brain-on-chatgpt/
- METR, "Early 2025 AI-Experienced OS Dev Study" — https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
- GitClear, "AI Assistant Code Quality 2025 Research" — https://www.gitclear.com/ai_assistant_code_quality_2025_research
- Hao et al., "On the accuracy of code complexity metrics: A neuroscience..." — https://pmc.ncbi.nlm.nih.gov/articles/PMC9942489
- Stack Overflow Developer Survey 2025 — https://survey.stackoverflow.co/2025

**Measurement**
- SonarSource, "Cognitive Complexity: A New Way of Measuring Understandability" — https://www.sonarsource.com/docs/CognitiveComplexity.pdf
- Sonar Community, "How to use Cognitive Complexity?" — https://community.sonarsource.com/t/how-to-use-cognitive-complexity/1894
- NASA Task Load Index (TLX) — https://www.nasa.gov/human-systems-integration-division/nasa-task-load-index-tlx
- getdx, "How cognitive complexity creates hidden friction" — https://getdx.com/blog/cognitive-complexity

**AI/agent engineering & hackathon relevance**
- Anthropic, "Building Effective AI Agents: Architecture Patterns and Implementation Frameworks" — https://resources.anthropic.com/hubfs/Building%20Effective%20AI%20Agents-%20Architecture%20Patterns%20and%20Implementation%20Frameworks.pdf
- Jan-Gerke Salomon, "How to Design a Maintainable Codebase for AI Coding Agents" — https://maintainable.software/agentic-engineering-part-2-agentic-codebase-principles/
- A. Aleryani, "Modular Architectures for Agentic AI: The 4-Layer Cut" — https://www.learnwithparam.com/blog/modular-architectures-agentic-ai-maintainable-production
- "A Practical Guide for Designing, Developing, and Deploying Production-Grade Agentic AI Workflows" (arXiv:2512.08769) — https://arxiv.org/abs/2512.08769
- Vectorize, "Designing Agentic AI Systems, Part 2: Modularity" — https://vectorize.io/blog/designing-agentic-ai-systems-part-2-modularity
- falila, "AI Agent Engineering Playbook" — https://github.com/falila/ai-agent-engineering-playbook/blob/main/README.md

**Practitioner syntheses**
- DevToolLab, "What Is Cognitive Debt? How AI Coding Tools Are Silently Eroding Developer Skills" — https://devtoollab.com/blog/cognitive-debt-ai-coding
- rockoder, "Cognitive Debt: When Velocity Exceeds Comprehension" — https://www.rockoder.com/beyondthecode/cognitive-debt-when-velocity-exceeds-comprehension/
- AI CERTs, "Cognitive Debt: The Hidden Cost of AI Coding" — https://www.aicerts.ai/news/cognitive-debt-the-hidden-cost-of-ai-coding/
- getdx, "Cognitive debt: The hidden risk in AI-driven software development" — https://getdx.com/blog/cognitive-debt-the-hidden-risk-in-ai-driven-software-development
- Aviator, "The Hidden Cost of AI-Generated Code: Cognitive Debt" (podcast with Margaret-Anne Storey) — https://www.aviator.co/podcast/cognitive-debt-ai-code-margaret-anne-storey