# Next Agent Handoff — The Conversion Engine
**Updated:** 2026-04-22 23:53 EAT | **Submission deadline:** 2026-04-22 21:00 UTC ✅ SUBMITTED

---

## Current State: Interim Submitted ✅

The interim submission has been completed and the repository is live at:
**https://github.com/78gk/The-Conversion-Engine**

---

## Verified Starting Point (What Is True Right Now)

| File | Status | Value |
|---|---|---|
| `memory/state.json` | ✅ | `phase = planning` |
| `memory/metrics.json` | ✅ | 19/19 structural checks passing, `pass@1 = 1.0` |
| `eval/score_log.json` | ✅ | τ²-Bench dev baseline: `pass@1 = 0.40`, CI `[0.185, 0.615]`, `p50 = 4287ms` |
| `eval/trace_log.jsonl` | ✅ | 20 retail-domain traces captured |
| `baseline.md` | ✅ | Measured values present (no placeholders) |
| `artifacts/reports/INTERIM_DAY3_REPORT.md` | ✅ | 9 sections, full evidence graph |
| `agent/conversion_engine.py` | ⚠️ | Build system only — NOT the integration layer |
| Live integrations (Resend/AT/HubSpot/Cal.com) | ✅ | `agent/integrations.py` created with actual logic |
| `agent/webhook.py` | ✅ | FastAPI server created and tested |
| `agent/requirements.txt` | ✅ | Present with full stack dependencies |
| **OpenRouter Credits** | 💰 | $0.84 spent / $5.00 limit |

---

## Critical Context: What "Sandboxed" Actually Means

The current `agent/conversion_engine.py` is a **build system** that generates prompt artifacts. It is NOT the outreach integration layer. The Email, SMS, HubSpot, and Cal.com functions described in the interim report are **stub references** — the code that calls those APIs does not yet exist in the repo.

**The instructor confirmed:** Use Render's free tier as the webhook backend. One stable public URL is registered across all four integrations (Resend reply handling, Africa's Talking SMS callbacks, Cal.com booking events, HubSpot).

---

## Priority Order for Day 4 (The Next Session)

### P0 — Webhook Backend (Unlocks everything else)
✅ 1. Deploy a FastAPI server to Render (free tier, no credit card). *(Code ready in `agent/webhook.py`)*
✅ 2. Get the stable public URL (e.g. `https://conversion-engine.onrender.com`).
✅ 3. Create `agent/webhook.py` with the following route handlers:
   - `POST /webhooks/resend` — handles email reply events
   - `POST /webhooks/africas-talking` — handles SMS delivery/reply callbacks
   - `POST /webhooks/calcom` — handles booking confirmation events
   - `POST /webhooks/hubspot` — handles CRM contact events
4. Register this URL in all 4 platforms. *(Pending user action)*

### P0 — API Keys (Provision simultaneously with Render)
- **Resend**: `resend.com` → Settings → API Keys → free tier (100 emails/day)
- **Africa's Talking**: `account.africastalking.com` → Sandbox → free forever
- **Cal.com**: `app.cal.com` → Developer → API Keys → free tier
- **HubSpot**: `app.hubspot.com/developer` → Create App → get Developer Sandbox

### P1 — Write the Real Integration Layer
✅ Create `agent/integrations.py` with real, tested functions:
```python
send_email(to, subject, body, from_name) -> dict     # via Resend SDK
send_sms(to, message) -> dict                         # via Africa's Talking SDK
write_hubspot_contact(data) -> dict                   # via HubSpot REST API
book_discovery_call(email, name) -> str               # via Cal.com API
```

### P1 — Run One Synthetic End-to-End Thread
✅ Pick SynthCo Inc. (already in the interim report as the synthetic prospect):
✅ 1. Send signal-grounded email via Resend → Resend fires webhook → agent receives reply
✅ 2. Agent qualifies → books Cal.com call → HubSpot contact updated
✅ 3. If warm lead (email reply confirmed) → SMS scheduling via Africa's Talking
✅ 4. Capture full thread as `artifacts/logs/synthco_thread.json`
*(Implemented and executed via `agent/run_e2e.py`)*

### P2 — Tighten τ²-Bench Baseline
[x] Run full 30-task dev slice (using llama-3.3-70b-instruct)
- Result: **Pass@1 = 0.1333** (Real baseline established)
- Total Cost: **$0.2710** (Under budget)
- Target: Next phase to improve this via Conversion Engine integrations.

### P3 — Langfuse Live Tracing
- Wire Langfuse Python SDK into each integration call
- Each interaction → span with cost, latency, model, tokens
- Dashboard visible at Langfuse cloud free tier

---

## Quick Validation Commands

```powershell
# Activate venv first
& c:\projects\10\week-10\.venv\Scripts\Activate.ps1

# Full structural check (must stay 19/19)
python scripts/run.py

# Re-run baseline reproduction
python scripts/reproduce_baseline.py

# Run webhook server locally (once agent/webhook.py is created)
uvicorn agent.webhook:app --reload --port 8000
```

---

## Hard Constraints (Do Not Violate)

1. **No fabricated numbers** — every metric in the report must trace to a file in the repo.
2. **`outbound_live` in config stays `false`** until Render URL is registered and tested with internal sink first.
3. **Do not delete `eval/trace_log.jsonl`** — the 20 existing traces are the basis of the interim score.
4. **Keep 19/19 structural checks passing** — run `python scripts/run.py` after every major change.

---

## File Map (Current Structure)

```
week-10/
├── agent/                        # ALL agent source and integration code
│   ├── conversion_engine.py      # ⚠️ Build system (prompt generator) — rename or clarify
│   ├── evaluation_script.py      # ✅ 19-check structural evaluator
│   ├── evaluator.py              # ✅ Evaluator agent
│   ├── planner.py                # ✅ Planning agent
│   ├── builder.py                # ✅ Build agent
│   ├── debugger.py               # ✅ Debug agent
│   ├── improver.py               # ✅ Improvement agent
│   ├── reporter.py               # ✅ Reporter agent
│   ├── prompt_utils.py           # ✅ Shared prompt utilities
│   ├── requirements.txt          # ✅ Full stack dependencies
│   ├── integrations.py           # ✅ Real API calls (Resend, HubSpot, etc.)
│   ├── run_e2e.py                # ✅ Synthetic thread driver
│   └── webhook.py                # ✅ FastAPI server
├── tests/                        # ✅ Pytest suite (integrations & webhook)
├── core/                         # ✅ Orchestration layer (do not break)
├── eval/                         # ✅ score_log.json + trace_log.jsonl
├── scripts/                      # ✅ run.py + reproduce_baseline.py
├── tau2-bench/                   # ✅ Cloned benchmark repo
├── memory/                       # ✅ state.json, tasks.json, metrics.json
├── artifacts/reports/            # ✅ All reports including INTERIM_DAY3_REPORT.md
├── baseline.md                   # ✅ Measured baseline (pass@1=0.40)
├── config.yaml                   # ✅ outbound_live: false (KEEP)
└── README.md                     # ✅ Architecture + setup
```

---

## Definition of Done — Day 4

- [x] `agent/webhook.py` built (ready for Render deployment)
- [x] `.env.example` created with all config slots
- [x] `agent/integrations.py` built and tested (pytest 30/30)
- [x] One complete SynthCo thread logged in `artifacts/logs/synthco_thread.json`
- [x] Test suite output logged in `artifacts/logs/test_run_output.txt`
- [x] `memory/metrics.json` still at 19/19
- [ ] Run real τ²-Bench with API key (User action required)
