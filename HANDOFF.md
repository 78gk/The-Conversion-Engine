# AI Agent Handoff Document
**Project:** The Conversion Engine (Week 10)
**Updated:** 2026-04-24
**DEADLINE: Saturday 2026-04-25 21:00 UTC — ~33 hours from now**

---

## Instructor Constraint Updates (2026-04-24)

| Constraint | Old | New |
|---|---|---|
| Run baseline benchmark | Required | **NOT required — instructor provides it** |
| Trials per task | 5 | **1 trial only** |
| Budget per trainee | ~$5 | **$10 allocated** |
| Reference baseline | Our run (0.1333) | **Instructor-provided (0.7267)** |

**Instructor baseline:** `input/score_log.json` and `input/trace_log.jsonl` (150 real traces)
**Our Day-1 baseline:** pass@1 = 0.1333 — kept as Delta A denominator for Act IV

---

## Current State (2026-04-24)

### Credentials
| Var | Status |
|---|---|
| `OPENROUTER_API_KEY` | ✅ New instructor key — `sk-or-v1-12d...90df` — $9.80 remaining |
| All other credentials | ✅ Set (Resend, AT, HubSpot, Cal.com) |
| `OUTBOUND_LIVE` | ✅ `false` — kill-switch on |

### Production Stack
| Integration | Status |
|---|---|
| Render webhook server | ✅ Live: `https://conversion-engine-webhook-kirubel.onrender.com` |
| Cal.com webhook | ✅ Registered |
| HubSpot webhook | ✅ Registered |
| Resend webhook | ❌ **NOT registered — 5 min task** |
| Africa's Talking webhook | ❌ **NOT registered — 5 min task** |

### Acts
| Act | Status |
|---|---|
| Act I — Baseline | ✅ Complete (instructor baseline + our day1 baseline both in `eval/`) |
| Act II — Production Stack | ✅ Wired, sandboxed. 2 webhooks pending. |
| Act III — Adversarial Probes | ✅ **COMPLETE** — 33 probes, taxonomy, target failure mode |
| Act IV — Mechanism Design | 🔄 In progress — method.md needed, eval pending |
| Act V — The Memo | ⏳ Pending Act IV results |

---

## Immediate Next Steps (Priority Order)

### P0 — Register 2 webhooks (10 min, user action)
1. **Resend:** resend.com → Webhooks → Add Endpoint → `https://conversion-engine-webhook-kirubel.onrender.com/webhooks/resend` → events: `email.sent`, `email.bounced`, `email.opened`
2. **Africa's Talking:** account.africastalking.com → SMS → Sandbox → Callback URLs → same base URL `/webhooks/africas-talking`

### P0 — Build method.md (Act IV mechanism)
File: `method.md`
Mechanism: Confidence-proportional phrasing gates on signal over-claiming
See: `probes/target_failure_mode.md` for full specification

### P0 — Run mechanism on held-out slice
Model: `openrouter/openai/gpt-4o-mini`
Command: `python scripts/reproduce_baseline.py` (after updating model in .env)
Budget: ~$0.60–$1.50 for 20 tasks × 1 trial
Target: pass@1 > 0.1333 with 95% CI separation (Delta A positive)
Update `eval/score_log.json` `mechanism-eval` entry with results

### P1 — Act V memo (method.md → memo.pdf)
Two pages. Every number traces to a file.
Template structure in `artifacts/reports/INTERIM_DAY3_REPORT.md` §7

### P1 — evidence_graph.json
Maps every numeric claim in memo.pdf to trace ID or source file.

### P2 — Demo video (max 8 min)
Required content: live email end-to-end, hiring signal brief generation, HubSpot populate, SMS scheduling, agent refusing to over-claim, τ²-bench score visible, probe walkthrough.

---

## Hard Constraints (Do Not Violate)
1. `OUTBOUND_LIVE=false` — flip to `true` ONLY for demo video with synthetic prospect
2. No fabricated Tenacious numbers — every claim traces to `eval/`, `input/`, or a public source
3. Do not delete `eval/trace_log.jsonl` — now contains instructor's 150 real traces
4. 19/19 structural checks must stay passing — run `python scripts/run.py` after any change
5. Do not commit `.env` — verify with `git ls-files | grep "^.env$"` before any push

## Budget
| Item | Amount |
|---|---|
| OpenRouter key balance | $9.80 |
| Mechanism eval (20 tasks × gpt-4o-mini) | ~$0.60–$1.50 |
| Buffer for retries / demo | ~$2.00 |
| **Remaining after all tasks** | **~$5.70–$6.70** |

---

## Key File Locations
| File | Purpose |
|---|---|
| `eval/score_log.json` | Baseline entries (instructor + day1 + mechanism pending) |
| `eval/trace_log.jsonl` | Instructor's 150 real traces |
| `input/score_log.json` | Instructor's original score log |
| `input/trace_log.jsonl` | Instructor's original trace log |
| `probes/probe_library.md` | 33 adversarial probes |
| `probes/failure_taxonomy.md` | 10-category taxonomy |
| `probes/target_failure_mode.md` | Signal over-claiming — business cost derivation |
| `method.md` | Act IV mechanism (to be created) |
| `ablation_results.json` | Act IV results (to be created) |
| `memo.pdf` | Act V — 2-page decision memo (to be created) |
| `evidence_graph.json` | Claim-to-source mapping (to be created) |

---

## Quick Commands
```bash
# Activate venv
.\.venv\Scripts\Activate.ps1

# Full structural check (must stay 19/19)
python scripts/run.py

# Test OpenRouter key
.\.venv\Scripts\python check_balance.py

# Run mechanism evaluation
python scripts/reproduce_baseline.py

# Run webhook server locally
.\.venv\Scripts\python -m uvicorn agent.webhook:app --reload --port 8000
```
