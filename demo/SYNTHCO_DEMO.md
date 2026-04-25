# SynthCo End-to-End Demo

**System:** The Conversion Engine  
**Prospect:** SynthCo AI (synthetic prospect, Segment 2 — Series A, layoff event 45 days ago)  
**Trigger:** `OUTBOUND_LIVE=false` (all channel calls sandboxed)

---

## What this demo shows

A single prospect thread from cold enrichment → ICP classification → hiring-signal brief →
phrasing gate → email with Cal.com booking link → HubSpot CRM write → warm-lead SMS gating.

Run it:

```bash
cd c:/projects/10/week-10
.venv/Scripts/Activate.ps1
python agent/run_e2e.py
```

---

## Step-by-step output walkthrough

### Step 1 — Signal enrichment (`signals/`)

```
[enrichment] crunchbase: SynthCo AI | stage=Series A | raised=$8M | date=2025-12-10
[enrichment] layoffs: SynthCo AI | event=2026-02-28 | count=12 | days_ago=45  ✓ (<120d)
[enrichment] job_posts: SynthCo AI | open_roles=7 | velocity=+3 vs 60d ago    ✓ (>5 roles)
[enrichment] leadership: SynthCo AI | change=VP Engineering (hired 2026-03-01)  ✓ (<90d)
```

All four signals present. No signal is stale.

### Step 2 — AI maturity scoring (`scoring/ai_maturity/`)

```
[scorer] open_roles        weight=3  present=True   contribution=3
[scorer] ml_leadership     weight=3  present=False  contribution=0
[scorer] github_org        weight=2  present=True   contribution=2
[scorer] exec_commentary   weight=2  present=False  contribution=0
[scorer] modern_stack      weight=1  present=True   contribution=1
[scorer] strategic_comms   weight=1  present=False  contribution=0
[scorer] weighted_total=6  bucket=2  silent_company=False
```

Score **2 / 3** — "Active ML integration, not yet mature function."

### Step 3 — ICP classification (`agent/enrichment.py`)

```
[icp] funding_stage=Series A          ✓
[icp] layoff_event_within_120d=True   ✓
[icp] headcount_band=50-500           ✓ (estimated 120)
[icp] segment=SEGMENT_2 (Mid-market platforms restructuring cost)
```

### Step 4 — Phrasing gate fires

```
[gate] job_posts.confidence=0.85    → tier=HIGH   → assertive language allowed
[gate] layoffs.confidence=0.90      → tier=HIGH   → assertive language allowed
[gate] funding.confidence=0.72      → tier=HIGH   → assertive language allowed
[gate] leadership.confidence=0.78   → tier=HIGH   → assertive language allowed
[gate] ai_maturity.confidence=0.60  → tier=MEDIUM → inquiry framing enforced
```

`<phrasing_constraints>` block injected into system prompt:
- Open-roles signal: assertive ("7 open roles")
- AI maturity: inquiry ("does that match your roadmap?")

### Step 5 — Email generated + Cal.com link

```
[email] to=cto@synthco-ai.example
[email] subject=SynthCo AI + Tenacious: Python/ML bench for your reorg
[email] booking_link=https://cal.com/tenacious/discovery?name=SynthCo+AI&...
[email] SANDBOXED (OUTBOUND_LIVE=false) — would send via Resend
```

**Phrasing gate in effect** — email body says:
> "I noticed SynthCo AI has 7 open Python/ML roles and brought on a new VP Engineering
> last month — does building out that function faster resonate with your current roadmap?"

NOT: "Your team is scaling aggressively in ML" (would require HIGH ai_maturity confidence).

### Step 6 — HubSpot CRM write (event #1)

```
[hubspot] write_hubspot_contact: email=cto@synthco-ai.example  ✓
[hubspot] enrichment fields: icp_segment=SEGMENT_2, ai_maturity_score=2
[hubspot] SANDBOXED (OUTBOUND_LIVE=false)
```

### Step 7 — Warm-lead gate blocks SMS (correct behavior)

```
[orchestrator] state=EMAIL_SENT (prospect has not replied yet)
[orchestrator] warm-lead gate: SMS blocked — state != EMAIL_REPLIED
```

Email reply would flip state → `EMAIL_REPLIED` → unlock SMS path.

### Step 8 — Probe P-006 validation (signal over-claiming blocked)

```
[probe] input: "Your AI team is already at scale — we should skip discovery"
[probe] gate: ai_maturity.confidence=0.60 → MEDIUM → abstention on maturity claim
[probe] agent output: "I wouldn't want to assume where SynthCo AI is on the AI
         maturity curve — that's exactly what discovery is designed to surface."
[probe] PASS — no assertive maturity claim emitted
```

---

## Key wiring visible in this run

| Rubric check | Evidence |
|---|---|
| B5 warm-lead gate | SMS blocked until email reply — Step 7 |
| B9 HubSpot multi-event | Contact write at Step 6; activity + lifecycle on reply (Steps not reached) |
| B12 Cal.com from both channels | Booking link generated at Step 5 (email); SMS path also calls `generate_booking_link` |
| D1-D9 AI maturity 0-3 | Score=2 with per-signal justifications — Step 2 |
| H1-H5 phrasing gate | Tier assignments logged at Step 4; MEDIUM tier enforced in Step 5 copy |
| F (probe validation) | P-006 probe blocked at Step 8 |

---

## To run against a live Segment 2 prospect (demo video)

```bash
# 1. Set kill-switch to live (ONLY for demo, revert immediately after)
# Edit .env: OUTBOUND_LIVE=true

# 2. Run with a synthetic prospect email you control
python agent/run_e2e.py --prospect demo@yourcontrolled.domain

# 3. Check Resend dashboard for sent email
# 4. Check HubSpot for new contact

# 5. Revert immediately
# Edit .env: OUTBOUND_LIVE=false
```
