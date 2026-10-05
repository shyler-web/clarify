# Nebius x NVIDIA Global AI Hackathon — Technical Stack Briefing

> Research by subagent (Task: Research Nebius and NVIDIA model stack). Date: 5 October 2026.
> Purpose: exact models, API usage, GPU options, and submission-gate steps.

**Deadline:** Oct 30, 2026 @ 10:00am PDT · Online, global · $50,000+ prizes (Grand Prize $20k cash + Jetson Orin Nano per track).

**Hard submission requirement (from Devpost):**
> "All submissions must run on either **Nebius Token Factory** or **Nebius AI Cloud** and use **at least one NVIDIA open source model**. Everything else is up to you."

Submission also needs: working demo URL, ≤3-min YouTube video with audio describing your use of Token Factory + NVIDIA models, public repo with an OSI license visible at top, README, and a writeup of how you used NVIDIA/Nebius tools.

## Token Factory — API + Models

**What it is:** Nebius Token Factory (rebrand of Nebius AI Studio, launched Nov 5 2025) is a fully-managed production inference platform built on Nebius AI Cloud 3.0 "Aether". Serves 60+ open-source models (DeepSeek, GPT-OSS, Llama, Nemotron, Qwen), OpenAI-compatible APIs, per-token pricing, public + dedicated endpoints, autoscaling, LoRA/full fine-tuning, zero-retention inference, 99.9% SLA.

**How to call it (OpenAI-compatible):**

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",   # note trailing /v1/
    api_key=os.environ.get("NEBIUS_API_KEY"),
)

resp = client.chat.completions.create(
    model="nvidia/nemotron-3-super-120b-a12b",
    messages=[{"role": "system", "content": "You are a helpful assistant"},
              {"role": "user", "content": "Explain this code: ..."}],
    temperature=0.6,
)
print(resp.to_json())
```

```bash
curl 'https://api.tokenfactory.nebius.com/v1/chat/completions' \
  -X POST -H 'Content-Type: application/json' -H 'Accept: */*' \
  -H "Authorization: Bearer $NEBIUS_API_KEY" \
  --data-binary '{"model":"nvidia/Nemotron-3_5-Lightning","messages":[{"role":"user","content":"Hello"}]}'
```

**Get your API key:** Token Factory console → **API keys** → Create → copy once (can't be reopened). List models with `GET https://api.tokenfactory.nebius.com/v1/models` (add `?verbose=true` for context window, quantization, rate limits). Machine-readable catalog: `GET https://tokenfactory.nebius.com/api/public/models_info` (or `model-catalog.md`).

**NVIDIA Nemotron models on Token Factory (public endpoints, per-token pricing):**

| Model | Model ID (use in API) | Total/active params | Context | Input $/1M | Output $/1M |
|---|---|---|---|---|---|
| **Nemotron 3.5 Lightning** | `nvidia/Nemotron-3_5-Lightning` | 30B / 3B | 1,024K | $0.06 | $0.24 |
| **Nemotron 3 Nano 30B A3B** | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | 30B / 3B | 262K | $0.06 | $0.24 |
| **Nemotron 3 Super 120b** | `nvidia/nemotron-3-super-120b-a12b` | 120B / 12B | 256K | $0.30 | $0.90 |
| **Nemotron 3 Ultra 550b** | `nvidia/Nemotron-3-Ultra-550b-a55b` | 550B / 55B | 1,024K | $1.00 | $3.00 |

Also in the family: Nano Omni (omni-modal), Nemotron-Parse, Nemotron-Nano-2-VL (multimodal). All hybrid Transformer–Mamba MoE, open weights/datasets/recipes.

**Dedicated endpoints:** `POST https://api.tokenfactory.nebius.com/v0/dedicated_endpoints` with `model_name`, `flavor_name`, `gpu_type`, `region`, `gpu_count`, `scaling {min_replicas, max_replicas}`. GPU enums: `gpu-l40s-d, gpu-l40s-a, gpu-h100-sxm, gpu-h200-sxm, gpu-b200-sxm, gpu-b200-sxm-a, gpu-b300-sxm`.

## Nebius AI Cloud — GPU Options & Pricing

Raw GPU VMs and multi-node clusters. Price per GPU-hour, on-demand:

| Platform ID | GPU | VRAM | On-demand $/GPU-hr | Preemptible | Presets | Regions |
|---|---|---|---|---|---|---|
| `gpu-l40s-a` | L40S (Xeon Gold 6338) | 48 GB | **$1.35** | $0.65 | `1gpu-8vcpu-32gb` ... `1gpu-40vcpu-160gb` | `eu-north1` |
| `gpu-l40s-d` | L40S (AMD EPYC 9654) | 48 GB | $1.35 | $0.65 | up to `4gpu-192vcpu-1152gb` | `eu-north1` |
| `gpu-h100-sxm` | H100 NVLink | 80 GB | **$3.85** | $2.15 | `1gpu-16vcpu-200gb`, `8gpu-128vcpu-1600gb` | `eu-north1` |
| `gpu-h200-sxm` | H200 NVLink | 141 GB | **$4.50** | $2.45 | `1gpu-16vcpu-200gb`, `8gpu-128vcpu-1600gb` | `eu-north1`, `eu-west1`, `us-central1` |
| `gpu-b200-sxm` | B200 | 180 GB | $7.15 | ~$0.99 | `8gpu-160vcpu-1792gb` | `us-central1` |
| `gpu-b300-sxm` | B300 (HGX) | 288 GB | $7.85 | ~$0.99 | `8gpu-192vcpu-2768gb` | `uk-south1` |

Pricing notes: billed per second (30 min = half hourly). vCPU/RAM billed separately (e.g., L40S: $0.012/vCPU-hr + $0.0032/GiB-hr). Stop VMs to stop billing. Commitment discounts up to 35% on multi-month reservations. Preemptible H100/H200 from $0.79–0.90/GPU-hr.

**Caution:** the **Nebius AI Cloud free-trial program was suspended as of July 13, 2026** — for the hackathon budget primarily on **Token Factory credits** rather than a free AI Cloud trial.

## Recommended NVIDIA Models for a Code-Understanding Agent

Prioritize the Nemotron line on Token Factory (all agent-ready: tool calling, long context, instruction following):

- **Nemotron 3 Super 120b ($0.30/$0.90)** — *best all-rounder for the core agent.* NVIDIA reports 60.47 SWE-Bench (OpenHands), 96.30 RULER @256K, strong code generation/analysis, multi-agent orchestration, long-context reasoning, 1M-token support. Sweet spot for quality-vs-cost.
- **Nemotron 3 Ultra 550b ($1.00/$3.00)** — *best reasoning/agent ceiling.* 87.0 GPQA, **70.7 SWE-Bench Verified**, 56.4 Terminal-Bench 2.1. For hard planning/architecture; expensive, route only complex queries.
- **Nemotron 3.5 Lightning & Nano 30B ($0.06/$0.24)** — *fast/cheap everyday calls.* 3B active; strong agentic reasoning, tool use (Nano: 53.8 BFCL v4, 99.2 AIME25 w/ tools), instruction following (Lightning: 71.88 IFBench). For retrieval, summarization, quick code edits, high-volume steps.
- **Nemotron-Nano-2-VL / Nano Omni** — multimodal (reading screenshots, diagrams in docs).
- **Embeddings:** NVIDIA's open embedding family not explicitly confirmed in the current public Token Factory catalog; catalog does list embedding/rerank models like **Qwen3-Embedding-8B** and rerankers. Run semantic retrieval on Token Factory's embedding endpoint (check `/v1/models`); keep the **NVIDIA text model as the "at least one NVIDIA open-source model"** to satisfy the requirement. Verify current availability before locking the stack.

Recommended routing for a code-understanding agent: **Super** for reasoning/code gen → **Lightning/Nano** for fast tool-call/retrieval/summary → **embedding model** for retrieval → **Ultra** only for final hard architectural decisions.

## Exact Steps to Meet Submission Requirements

1. **Get Token Factory credits (essential — AI Cloud free trial suspended):**
   - Fill the [promo form](https://nebius.com/promo-code) with activation code **`NEBIUS-DEVPOST-GLOBAL26`** → **$25**.
   - Join the [Nebius Builders Program](https://dev.nebius.com/builders) → another **$25** (Token Factory + Tavily + Academy) plus office hours.
   - Optional extra credits at an in-person Builders & Brews meetup.
2. **Create an API key** in Token Factory console; put in `NEBIUS_API_KEY`.
3. **Build your app to call Token Factory** via the OpenAI-compatible API with at least one `nvidia/*` model ID (e.g., `nvidia/nemotron-3-super-120b-a12b`). This alone satisfies "run on Token Factory **and** use at least one NVIDIA open-source model."
4. **(Recommended) Deploy on Nebius:** Best Apps & Agents and Personal AI tracks encourage Nebius **Serverless Endpoints** (serving) and **Serverless Jobs** (background/async); Coding track mentions Token Factory Sandboxes. Use if convenient — not strictly required.
5. **Demonstrate it:** working demo URL + ≤3-min YouTube video (audio: how you used Token Factory + NVIDIA models).
6. **Publish the repo:** public GitHub with OSI license (Apache-2.0/MIT/MPL-2.0) visible at top, README with setup/run instructions and a section highlighting your NVIDIA model + Token Factory use.
7. **Pick a track** and submit a project description.

## Integration Options for a FastAPI / uv App

- **OpenAI-compatible API:** point the `openai` Python SDK at `base_url="https://api.tokenfactory.nebius.com/v1/"`. Endpoints: `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, `/v1/models`, `/v0/dedicated_endpoints`. Standard sampling params + streaming supported.
- **Python SDK / packages:** `openai` (primary), `langchain-nebius` (pip) for LangChain/LangGraph Deep Agents + embeddings + semantic retrieval on Token Factory; Tavily for agentic web search; `.venv` via `uv`.
- **Other:** REST with `curl`; official Nebius CLI for AI Cloud provisioning; K8s/OpenStack-style APIs for AI Cloud compute.

**Minimal FastAPI example:**

```python
import os
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/",
                api_key=os.environ["NEBIUS_API_KEY"])

@app.post("/analyze")
def analyze(code: str):
    r = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[{"role": "user", "content": f"Analyze this code:\n{code}"}])
    return {"result": r.choices[0].message.content}
```

Run with `uv run fastapi dev app.py` (or `uvicorn app:app`).

## Source URLs

- Hackathon home / rules / tracks / prizes: https://nebiusglobalaihackathon.devpost.com/
- Resources & credit codes: https://nebiusglobalaihackathon.devpost.com/resources
- Dev.nebius (builders hub): https://dev.nebius.com
- Token Factory Nemotron landing + OpenAI API example: https://nebius.com/services/token-factory/nemotron
- Nemotron models on Token Factory (pricing, benchmarks): https://nebius.com/services/token-factory/models/nvidia-nemotron-models-inference
- Token Factory model catalog (machine-readable): https://tokenfactory.nebius.com/model-catalog.md
- Token Factory API reference: https://docs.tokenfactory.nebius.com/api-reference/introduction
- Token Factory launch press release: https://nebius.com/newsroom/nebius-launches-nebius-token-factory-to-deliver-production-ai-inference-at-scale
- Nemotron 3 Super on Token Factory: https://nebius.com/blog/posts/nemotron3-super-now-available
- LangChain Deep Agents (`langchain-nebius`): https://nebius.com/blog/posts/nebius-and-langchain-partner-to-power-production-grade-ai-agents-on-open-models
- AI Cloud GPU instance types/presets: https://docs.nebius.com/compute/virtual-machines/types
- AI Cloud compute pricing: https://docs.nebius.com/compute/resources/pricing
- AI Cloud GPU pricing: https://nebius.com/prices
- AI Cloud free trial status (suspended Jul 13 2026): https://docs.nebius.com/signup-billing/free-trial
- Promo code redemption: https://docs.nebius.com/signup-billing/payments/promo-codes

**Caveat:** model availability and prices on Token Factory change frequently (the catalog is the source of truth). Re-run `GET https://api.tokenfactory.nebius.com/v1/models?verbose=true` and check the model-catalog to confirm the exact `nvidia/*` model IDs and embedding-model availability before you scope the build.