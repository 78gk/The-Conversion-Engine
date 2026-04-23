# AI Agent Handoff Document
**Project:** The Conversion Engine (Week 10)
**Updated:** 2026-04-23 21:00 EAT

---

## Where We Are Right Now

The production webhook backend is **live and verified**. All credentials are provisioned. Two of four webhook registrations are complete. The next unblocked task is running the real τ²-bench evaluation to improve pass@1 from 0.1333 → 0.40+.

---

## Completed This Session (2026-04-23)

### Credentials — all provisioned in local `.env` and Render env vars
| Var | Value / Status |
|---|---|
| `OPENROUTER_API_KEY` | ✅ Set (duplicate removed from .env) |
| `RESEND_API_KEY` | ✅ Set |
| `RESEND_FROM_EMAIL` | ✅ `onboarding@resend.dev` (valid Resend sandbox sender — no change needed) |
| `AT_USERNAME` / `AT_API_KEY` / `AT_SANDBOX` / `AT_SENDER_ID` | ✅ Set |
| `HUBSPOT_ACCESS_TOKEN` / `HUBSPOT_PORTAL_ID` / `HUBSPOT_OWNER_ID` | ✅ Set (owner ID: 91298335) |
| `CALCOM_API_KEY` / `CALCOM_EVENT_TYPE_ID` / `CALCOM_USERNAME` | ✅ Set (event ID: 5469048 "Discovery Call", username: kirubel-tewodros-d3sxbq) |
| `WEBHOOK_SECRET` | ✅ Generated (64-char hex in .env) |
| `STAFF_SINK_EMAIL` | ✅ `kirubel@10academy.org` |
| `OUTBOUND_LIVE` | ✅ `false` (kill-switch is on — keep it until live testing is confirmed) |

### Git / GitHub
- ✅ `.env` removed from git tracking (`git rm --cached`) — keys never reached GitHub
- ✅ `agent/requirements.txt` fixed: `africas-talking` → `africastalking`, `tau2-bench` PyPI line removed
- ✅ Branch renamed `master` → `main`, pushed to origin, GitHub default branch updated to `main`
- ⚠️ Remote `master` branch still exists on GitHub — delete with: `git push origin --delete master`

### Dependencies
- ✅ All packages installed in `.venv`: `uvicorn`, `fastapi`, `resend`, `africastalking`, `langfuse`, `litellm`, `openai`, `pandas`, `playwright`, `pyyaml`, `pydantic`
- Run server locally with: `.\.venv\Scripts\python -m uvicorn agent.webhook:app --reload --port 8000`

### Render Deployment
- ✅ **Live URL:** `https://conversion-engine-webhook-kirubel.onrender.com`
- ✅ Verified: `GET /health` returns `{"status":"ok","service":"conversion-engine-webhook"}`
- ✅ All 19 env vars set in Render dashboard
- ✅ Build command: `pip install -r agent/requirements.txt`
- ✅ Start command: `uvicorn agent.webhook:app --host 0.0.0.0 --port $PORT`
- ✅ Tracking `main` branch — auto-deploys on push
- ⚠️ 3 DUPLICATE services still running (waste free tier quota) — delete these:
  - `kirubel-ce-7887`
  - `kirubel-conversion-engine-webhook-7887`
  - `conversion-engine-webhook-kirubel78`

### Webhook Registrations
| Provider | Endpoint | Status | Notes |
|---|---|---|---|
| Cal.com | `/webhooks/calcom` | ✅ Registered | All booking events, WEBHOOK_SECRET set as signing secret |
| HubSpot | `/webhooks/hubspot` | ✅ Registered | Via Legacy App → Webhooks tab. Subscriptions: Contact created + Contact property changed (lifecyclestage). Committed. |
| Resend | `/webhooks/resend` | ❌ Not registered | See Step 1 below |
| Africa's Talking | `/webhooks/africas-talking` | ❌ Not registered | See Step 2 below |

---

## Immediate Next Steps (In Priority Order)

### Step 1 — Register Resend webhook (5 min)
1. Go to resend.com → **Webhooks** in left nav
2. Click **Add Endpoint**
3. URL: `https://conversion-engine-webhook-kirubel.onrender.com/webhooks/resend`
4. Events: `email.sent`, `email.bounced`, `email.opened`
5. Save — no signing secret needed

### Step 2 — Register Africa's Talking webhook (5 min)
1. Go to account.africastalking.com → **SMS** (sandbox) → **Callback URLs**
2. **Delivery Reports URL:** `https://conversion-engine-webhook-kirubel.onrender.com/webhooks/africas-talking`
3. **Incoming Messages URL:** same URL
4. Save

### Step 3 — Cleanup (5 min)
- Delete 3 extra Render services (kirubel-ce-7887, kirubel-conversion-engine-webhook-7887, conversion-engine-webhook-kirubel78) via Render dashboard → Settings → Delete or suspend
- Delete remote master: `git push origin --delete master`

### Step 4 — Run real τ²-bench evaluation (HIGHEST IMPACT)
Current baseline: **pass@1 = 0.1333** (4/30 tasks, llama-3.3-70b-instruct, $0.27 total)
Target: **pass@1 > 0.40** (the published ceiling for retail domain)

**Recommended model:** `openai/gpt-4o-mini` via OpenRouter — stronger tool-use than llama-70b, ~$0.30-$0.60 for 30×1 run, ~$1.50-$3.00 for 30×5 run.

Change in `.env`:
```
AGENT_LLM_MODEL=openrouter/openai/gpt-4o-mini
USER_LLM_MODEL=openrouter/mistralai/mistral-7b-instruct:free
```

Run: `python scripts/reproduce_baseline.py`

**Budget status:** ~$0.85 spent of ~$5.00 limit → ~$4.15 remaining. A 30×5 run with gpt-4o-mini costs ~$1.50-$3.00. Stay within budget.

---

## OpenRouter Budget
- Total spent: **$0.85**
- Weekly limit: **$10.85** (resets weekly)
- Remaining this week: **~$10.57**
- User-stated cap: **$5.00 total**
- Remaining vs user cap: **~$4.15**
- Spend rate this session: $0.28

---

## Hard Constraints (Do Not Violate)
1. **`OUTBOUND_LIVE=false`** in both local `.env` and Render — all outbound routes to staff sink. Only flip to `true` when live prospect contact is explicitly authorized.
2. **No fabricated numbers** — every metric in any report must trace to a file in the repo.
3. **Do not delete `eval/trace_log.jsonl`** — 20 existing traces are the interim submission basis.
4. **Keep 19/19 structural checks passing** — run `python scripts/run.py` after any major change.
5. **HubSpot app must stay as Private/Legacy app** — do not create a Public App.
6. **Do not commit `.env`** — it is gitignored and untracked. Verify with `git ls-files | grep .env` before any push (should return nothing).

---

## Key URLs
| Resource | URL |
|---|---|
| Render webhook server | https://conversion-engine-webhook-kirubel.onrender.com |
| GitHub repo | https://github.com/78gk/The-Conversion-Engine |
| Cal.com account | app.cal.com (username: kirubel-tewodros-d3sxbq) |
| HubSpot CRM | app-eu1.hubspot.com (portal: 148335210) |

---

## Days 5–7 Plan (from INTERIM_DAY3_REPORT.md §7)
| Day | Work | Outcome |
|---|---|---|
| Day 5 | Live crawl ≤200 company job posts (Playwright) | Real velocity signal replacing frozen snapshot |
| Day 5 | Full Crunchbase ODM enrichment sweep | Market-space candidate cell identification |
| Day 5–6 | Act III: 30+ adversarial probes | `probes/probe_library.md` |
| Day 6 | Act IV: Mechanism design (confidence-aware phrasing) | `method.md`, `ablation_results.json` |
| Day 7 | Act V memo (2 pages PDF) | `memo.pdf`, `evidence_graph.json` |

---

## Quick Validation Commands
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Full structural check (must stay 19/19)
python scripts/run.py

# Run baseline (30-task tau2-bench dev slice)
python scripts/reproduce_baseline.py

# Run webhook server locally
.\.venv\Scripts\python -m uvicorn agent.webhook:app --reload --port 8000

# Check OpenRouter balance
.\.venv\Scripts\python check_balance.py
```
