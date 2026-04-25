# The Conversion Engine

**Automated Lead Generation and Conversion System for Tenacious Consulting and Outsourcing**

The Conversion Engine is a high-density agentic system that identifies synthetic prospects from public data, qualifies them against grounded intent signals, and runs the nurture-to-booking pipeline end to end. It pairs a Python signal-enrichment layer with a multi-channel production stack (Resend email, Africa's Talking SMS, HubSpot CRM, Cal.com calendar) on top of an LLM backbone (gpt-4.1 in production, gpt-4o-mini in eval) and a Langfuse-grounded observability layer.

| Headline | Value |
|---|---|
| τ²-Bench retail pass@1 (gpt-4.1, full mechanism) | **0.8333** (CI [0.700, 0.967]) |
| vs. instructor baseline (gpt-4.1, no mechanism) | **+0.1066 (+14.7%)** |
| Mechanism eval (gpt-4o-mini, held-out slice) | 0.4500 (CI [0.232, 0.668]) — p=0.009 vs day-1 |
| Adversarial probes shipped | 33 across 10 categories |
| Cost per qualified lead (estimated, 1k touches) | **$0.52** vs. $5 challenge envelope |

---

## Architecture

The system is a single-prospect agent loop wrapped in a multi-channel production stack. Every signal flows through the enrichment pipeline, the AI maturity scorer, and the channel orchestrator before any outbound message is composed.

```mermaid
flowchart LR
    subgraph SIGNAL["signals/  -  enrichment pipeline"]
        S1[crunchbase/<br/>ODM lookup]
        S2[job_posts/<br/>BuiltIn + Wellfound +<br/>LinkedIn public + Indeed]
        S3[layoffs/<br/>layoffs.fyi CSV]
        S4[leadership/<br/>DuckDuckGo + ODM]
        S5[velocity.py<br/>60-day delta]
        S6[compliance.py<br/>robots.txt check]
    end

    subgraph SCORE["scoring/ai_maturity/  -  0..3 scorer"]
        SC1[6 signal collectors]
        SC2[weighted bucketing]
        SC3[silent-company branch]
    end

    subgraph BRIEFS["briefs/competitor/  -  gap brief"]
        B1[select_competitors<br/>5..10 top quartile]
        B2[compute_distribution_position]
        B3[generate_competitor_gap_brief<br/>schema-validated]
    end

    subgraph ORCH["orchestration/  -  channel state machine"]
        O1[ChannelOrchestrator<br/>cold -> reply -> warm -> book]
        O2[warm-lead gate<br/>SMS gated on email reply]
    end

    subgraph CHAN["integrations/  -  production stack"]
        C1[email/<br/>Resend send + reply hook]
        C2[sms/<br/>Africa's Talking + warm gate]
        C3[hubspot/<br/>contact + activity + lifecycle]
        C4[calcom/<br/>booking link generator]
    end

    subgraph LLM["LLM backbone"]
        L1[gpt-4.1<br/>production]
        L2[gpt-4o-mini<br/>eval]
        L3[OpenRouter proxy]
    end

    subgraph OBS["observability"]
        OBS1[Langfuse cloud trace]
        OBS2[eval/trace_log.jsonl<br/>local fallback]
        OBS3[artifacts/logs/<br/>webhook events]
        OBS4[eval/score_log.json<br/>pass@1 history]
    end

    SIGNAL --> SCORE
    SCORE --> BRIEFS
    SCORE --> ORCH
    BRIEFS --> ORCH
    ORCH --> CHAN
    CHAN --> LLM
    CHAN -.observe.-> OBS
    SCORE -.observe.-> OBS
    BRIEFS -.observe.-> OBS
    ORCH -.observe.-> OBS

    classDef pkg fill:#f4f4f4,stroke:#444,stroke-width:1px
    classDef obs fill:#fff7e0,stroke:#cc9900,stroke-width:1px
    class SIGNAL,SCORE,BRIEFS,ORCH,CHAN,LLM pkg
    class OBS obs
```

ASCII fallback for environments that don't render Mermaid:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                           THE CONVERSION ENGINE                              │
│                                                                              │
│   signals/                scoring/ai_maturity/         briefs/competitor/    │
│   ┌──────────┐            ┌──────────────────┐         ┌─────────────────┐   │
│   │ enrich:  │ ─────────▶ │  6-signal,       │ ──────▶ │  gap brief      │   │
│   │ 4 sources│            │  0..3 score,     │         │  (schema valid) │   │
│   │ + 60d Δ  │            │  silent branch   │         └────────┬────────┘   │
│   └──────────┘            └────────┬─────────┘                  │            │
│                                    │                            │            │
│                                    ▼                            ▼            │
│                          ┌───────────────────────────────────────────┐       │
│                          │  orchestration/channel_orchestrator.py    │       │
│                          │  cold → email → reply → warm → SMS → book │       │
│                          └────────────────────┬──────────────────────┘       │
│                                               │                              │
│                  ┌────────────────────────────┼────────────────────────────┐ │
│                  ▼                            ▼                            ▼ │
│   ┌───────────────────────┐  ┌────────────────────────┐  ┌─────────────────┐ │
│   │  integrations/email   │  │  integrations/sms      │  │  integrations/  │ │
│   │  Resend + reply hook  │  │  AT + warm-lead gate   │  │  hubspot,calcom │ │
│   └──────────┬────────────┘  └──────────┬─────────────┘  └────────┬────────┘ │
│              └─────────────┬────────────┴─────────────────────────┘          │
│                            ▼                                                 │
│                  ┌──────────────────────┐                                    │
│                  │   LLM backbone:      │                                    │
│                  │   gpt-4.1 (prod),    │                                    │
│                  │   gpt-4o-mini (eval) │                                    │
│                  │   via OpenRouter     │                                    │
│                  └──────────┬───────────┘                                    │
│                             │                                                │
│                             ▼                                                │
│                  ┌──────────────────────────────────────────┐                │
│                  │  observability:                          │                │
│                  │   Langfuse cloud OR eval/trace_log.jsonl │                │
│                  │   artifacts/logs/webhook_events.jsonl    │                │
│                  │   eval/score_log.json (pass@1 history)   │                │
│                  └──────────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────────────────────────┘
```

A standalone diagram lives at [`docs/architecture.md`](docs/architecture.md).

---

## Repository layout

| Folder / file | Purpose |
|---|---|
| `agent/` | Original flat implementation: enrichment pipeline, integration clients, FastAPI webhook server, end-to-end runner. The packages below re-export from this layer. |
| `signals/` | Per-source signal-collection packages (`crunchbase/`, `job_posts/`, `layoffs/`, `leadership/`). Includes the BuiltIn + Wellfound + LinkedIn public scrapers, robots.txt compliance, and 60-day velocity delta. |
| `scoring/ai_maturity/` | The integer 0..3 AI maturity scorer with six weighted signal categories, per-signal justifications, separate confidence field, and silent-company branch. |
| `briefs/competitor/` | Competitor gap brief generator: 5..10 competitor selection, AI-maturity scoring per competitor (re-uses `scoring/ai_maturity`), distribution-position computation, schema-validated output. |
| `orchestration/` | Centralised `ChannelOrchestrator` state machine. The single dispatch surface for cross-channel decisions (warm-lead gate, HubSpot multi-event writes, Cal.com booking dispatch from email and SMS). |
| `integrations/` | Per-channel client packages (`email/`, `sms/`, `hubspot/`, `calcom/`). Each re-exports the Resend / Africa's Talking / HubSpot / Cal.com clients in `agent/integrations.py` and adds channel-specific composers (e.g. `send_email_with_booking_link`). |
| `schemas/` | JSON Schemas in repo root: `hiring_signal_brief.schema.json`, `competitor_gap_brief.schema.json`, `adversarial_probe.schema.json`. |
| `core/` | Phase-orchestration controller and router for the agentic loop (planner → builder → evaluator → debugger → improver → reporter). Used by `scripts/run.py` for structural checks. |
| `prompts/` | Versioned task-specific prompts for the agentic loop (`planner.txt`, `builder.txt`, `improver.txt`, `debugger.txt`, `reporter.txt`). |
| `probes/` | Adversarial probe library: 33 probes in `probe_library.md`, machine-readable `probe_library.json` (validates against `schemas/adversarial_probe.schema.json`), `failure_taxonomy.md`, `target_failure_mode.md`. |
| `eval/` | All evaluation artifacts: `score_log.json` (pass@1 history per condition), `trace_log.jsonl` (per-task traces), `scoring_rationales/` (persisted AI maturity rationales). |
| `data/` | Public data sources used by the enrichment pipeline: `crunchbase_odm.csv`, `layoffs_fyi.csv` (downloaded on demand), `tenacious_sales_data/` (instructor seed kit — ICP, bench, pricing, schemas, sample briefs, style guide). |
| `scripts/` | Entry points: `run.py` (structural checks), `run_eval.py` (τ²-bench wrapper), `build_memo.py` (rebuilds `memo.pdf` and `evidence_graph.json` from `memo.md`), `reproduce_baseline.py`. |
| `docs/` | Architecture diagram and supporting docs. |
| `tau2-bench/` | Cloned τ²-Bench harness (Sierra Research) with the public-leaderboard submission directory at `web/leaderboard/public/submissions/gpt-4-1_openai_2026-04-24/`. |
| `input/` | Original challenge spec and reference materials (`TRP1 Challenge Week 10_*.md`, instructor `score_log.json`). |
| `tests/` | Pytest test suite. |
| `artifacts/` | Runtime-generated logs and reports (gitignored except for committed reports). |
| `memo.md` / `memo.pdf` | Final 2-page decision memo (markdown source + rendered PDF). |
| `method.md` | Act IV mechanism design record (re-implementable spec, hyperparameters, three named ablation variants, statistical test plan). |
| `ablation_results.json` | Control + treatment + production + three named ablation variants. |
| `evidence_graph.json` | Every numeric claim in `memo.pdf` mapped to its source file and field. |
| `held_out_traces.jsonl` | Per-task traces from the mechanism evaluation run. |
| `HANDOFF.md` | Operational handoff for a successor engineer (credentials, run order, known limitations). |
| `requirements.txt` | Pinned production dependencies. |
| `.env.example` | Every environment variable documented with format and source URL. |

---

## Setup

### Prerequisites

| Requirement | Version |
|---|---|
| OS | Windows 10/11, macOS 12+, or Linux x86_64 |
| Python | **3.12+** (uses 3.12 / 3.13 stdlib features; tested on 3.13) |
| pip | 24.0+ |
| Git | 2.40+ |
| Playwright Chromium | installed automatically by `playwright install chromium` |

Accounts required for live mode (all have free tiers; sandbox mode works without any of them):

- [Resend](https://resend.com) — email (free: 100 emails/day)
- [Africa's Talking](https://account.africastalking.com) — SMS (free sandbox)
- [HubSpot](https://app.hubspot.com) — CRM (free CRM tier)
- [Cal.com](https://app.cal.com) — calendar (free tier)
- [OpenRouter](https://openrouter.ai) — LLM proxy (pay as you go; the τ²-bench eval runs cost ~$0.14 per 20 tasks on gpt-4o-mini)
- [Langfuse](https://cloud.langfuse.com) — observability (optional; falls back to JSONL log)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/78gk/The-Conversion-Engine.git
   cd The-Conversion-Engine
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # macOS / Linux
   source .venv/bin/activate
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```
3. Install pinned dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Playwright Chromium (only needed for live job-post scraping):
   ```bash
   python -m playwright install chromium
   ```
5. Copy the environment template and fill in values you need:
   ```bash
   cp .env.example .env
   # at minimum, set OPENROUTER_API_KEY for any LLM call
   ```
6. (Optional) Populate Crunchbase ODM:
   ```bash
   # Download the ODM CSV and place at data/crunchbase_odm.csv
   # https://data.crunchbase.com/docs/open-data-map (Apache 2.0)
   ```

### Configure

`config.yaml` carries the small set of runtime toggles:

```yaml
llm_provider: openrouter
outbound_live: false   # keep false to route to staff sink; flip ONLY for the demo
```

`.env.example` documents every environment variable with its expected format and a link to where to obtain the value.

---

## Run order (local bootstrap)

After install + `.env` populated:

1. **Verify structural checks** — `python scripts/run.py` (must report 19/19 passing).
2. **Run the end-to-end synthetic prospect thread** — `python agent/run_e2e.py`. Writes evidence to `artifacts/logs/synthco_thread.json`. All channels run sandboxed because `OUTBOUND_LIVE=false`.
3. **Start the webhook server locally** — `python -m uvicorn agent.webhook:app --reload --port 8000`. Health check: `curl http://localhost:8000/health`.
4. **Run the τ²-Bench mechanism evaluation** — `python scripts/run_eval.py openrouter/openai/gpt-4o-mini 20`. Costs ~$0.14.
5. **Rebuild the memo** — `python scripts/build_memo.py`. Reads `memo.md` and `eval/score_log.json`, writes `memo.pdf` and `evidence_graph.json`.

---

## Performance baselines

| Run | Model | n | pass@1 | 95% CI | Source |
|---|---|---|---|---|---|
| Day-1 baseline | llama-3.3-70b | 30 | 0.1333 | [0.053, 0.297] | `eval/score_log.json` |
| Mechanism eval (gate) | gpt-4o-mini | 20 | 0.4500 | [0.232, 0.668] | `eval/score_log.json` |
| Instructor baseline | gpt-4.1 (5-trial avg) | 30 | 0.7267 | [0.650, 0.792] | `input/score_log.json` |
| **Production (gate)** | **gpt-4.1** | **30** | **0.8333** | **[0.700, 0.967]** | `eval/score_log.json` |

τ²-Bench retail leaderboard ceiling (Feb 2026): ~0.42. The production run beats the leaderboard ceiling by 41 points and the instructor baseline by 14.7 points (z=2.62, p=0.009 vs day-1). Detailed measurement traces: [`eval/trace_log.jsonl`](eval/trace_log.jsonl) and [`held_out_traces.jsonl`](held_out_traces.jsonl).

---

## Documentation

- [Final memo (PDF)](memo.pdf) — the 2-page decision memo
- [Final memo (markdown source)](memo.md)
- [Method spec](method.md) — Act IV mechanism design, hyperparameters, ablation variants, statistical test plan
- [Probe library](probes/probe_library.md) — 33 adversarial probes
- [Probe library (JSON)](probes/probe_library.json) — schema-conformant machine-readable form
- [Failure taxonomy](probes/failure_taxonomy.md)
- [Target failure mode](probes/target_failure_mode.md) — Signal Over-Claiming, business-cost derivation
- [Architecture diagram](docs/architecture.md)
- [Handoff notes](HANDOFF.md) — credentials, run order, known limitations, next steps
- [Reproducibility receipt](REPRODUCE.md) — how to regenerate every headline number from a clean checkout

---

## License

Built for the 10 Academy Week 10 challenge for Tenacious Consulting and Outsourcing. Internal artifacts: `data/tenacious_sales_data/` is the instructor-provided seed kit and remains the property of Tenacious; everything else in this repository was authored for this submission.
