# State Context
**Project:** The Conversion Engine (Week 10)
**Updated:** 2026-04-23 21:00 EAT

---

## Current Runtime State
- Workflow phase file: `memory/state.json` → phase = `reporting`
- Last full run: planning → building → evaluating → debugging → reporting
- Structural checks: 19/19 passing (`memory/metrics.json`)

---

## Production Stack Status

| Layer | Tool | Status | URL / Notes |
|---|---|---|---|
| Webhook server | FastAPI on Render (free) | ✅ LIVE | https://conversion-engine-webhook-kirubel.onrender.com |
| Email | Resend | ✅ Key provisioned | Webhook not yet registered |
| SMS | Africa's Talking sandbox | ✅ Key provisioned | Webhook not yet registered |
| CRM | HubSpot Legacy App | ✅ Key provisioned, webhook registered | Contact created + lifecyclestage change subscribed |
| Calendar | Cal.com | ✅ Key provisioned, webhook registered | Discovery Call event ID: 5469048 |
| LLM | OpenRouter | ✅ Active | $0.85 spent, ~$4.15 remaining of $5 cap |
| Observability | Langfuse | ⚠️ Project created, not yet wired | Pending Day 4 |

---

## τ²-Bench Baseline (Real, Measured)
- **Model:** `meta-llama/llama-3.3-70b-instruct` via OpenRouter
- **pass@1:** 0.1333 (4/30 tasks)
- **95% CI:** [0.053, 0.297]
- **Total cost:** $0.2710 (30 tasks × 1 trial)
- **Avg cost/task:** $0.009
- **Target:** pass@1 > 0.40
- **Recommended next model:** `openai/gpt-4o-mini` via OpenRouter

---

## Credential Status (Local `.env` + Render)
All credentials are provisioned and loaded into Render env vars. `.env` is gitignored and untracked. Summary:
- OpenRouter, Resend, Africa's Talking (sandbox), HubSpot (pat-eu1), Cal.com — all set
- WEBHOOK_SECRET: 64-char hex, matches what's registered in Cal.com
- OUTBOUND_LIVE: false (kill-switch active)
- STAFF_SINK_EMAIL: kirubel@10academy.org

---

## Git / Repo State
- **Branch:** `main` (renamed from master, pushed to origin)
- **Remote master:** still exists — pending deletion: `git push origin --delete master`
- **Last commit:** d5c8a74 "organizing setup" — clean (no .env, requirements.txt fixed)
- **.env:** untracked, gitignored, never pushed

---

## What Is Still NOT Done (Ordered by Priority)
1. ❌ Register Resend webhook at resend.com/webhooks
2. ❌ Register Africa's Talking callback at account.africastalking.com
3. ❌ Delete 3 duplicate Render services (kirubel-ce-7887, kirubel-conversion-engine-webhook-7887, conversion-engine-webhook-kirubel78)
4. ❌ Delete remote `master` branch: `git push origin --delete master`
5. ❌ Re-run τ²-bench with gpt-4o-mini (30 tasks × 5 trials) — **highest impact on final score**
6. ❌ Wire Langfuse per-trace spans
7. ❌ Days 5–7 deliverables (probes, mechanism design, final memo)

---

## Key Evidence Files
| File | Contents |
|---|---|
| `eval/score_log.json` | Real τ²-bench baseline (pass@1=0.1333) |
| `eval/trace_log.jsonl` | 20 traces (mix of real + simulated — see score_log status fields) |
| `baseline.md` | Measured baseline with real model/cost/CI data |
| `artifacts/reports/INTERIM_DAY3_REPORT.md` | Full 9-section interim report |
| `artifacts/logs/synthco_thread.json` | SynthCo synthetic prospect thread |
| `memory/metrics.json` | 19/19 structural checks |
| `agent/webhook.py` | FastAPI webhook server (deployed on Render) |
| `agent/integrations.py` | Real API integration layer (Resend, AT, HubSpot, Cal.com) |
| `agent/requirements.txt` | Fixed (africastalking, tau2-bench line removed) |
