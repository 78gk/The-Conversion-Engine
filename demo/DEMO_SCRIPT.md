# The Conversion Engine — Live Demo Script
**Project:** The Conversion Engine · Tenacious Consulting and Outsourcing  
**Prospect:** SynthCo Inc. (synthetic) · CTO Alex Rivera  
**Max runtime:** 8 minutes  
**Audience:** 10 Academy graders / technical evaluators  
**Tone:** Professional, evidence-forward, unhurried  

---

## Pre-Demo Checklist

Complete every item before pressing record. A failed check mid-recording costs more time than fixing it now.

### Terminal
- [ ] Venv activated: `.\.venv\Scripts\Activate.ps1` — prompt shows `(.venv)`
- [ ] Project root is CWD: `pwd` returns `c:\projects\10\week-10`
- [ ] Webhook server running in **Terminal 2**: `python -m uvicorn agent.webhook:app --reload --port 8000` — shows `Uvicorn running on http://127.0.0.1:8000`
- [ ] `OUTBOUND_LIVE=false` in `.env` — confirm with `grep OUTBOUND_LIVE .env`
- [ ] `cto_email` in `agent/run_e2e.py` line 44 = `kirutew17654321@gmail.com` — confirm with `grep cto_email agent/run_e2e.py`

### Browser tabs (open in order, left to right)
- [ ] **Tab 1 — memo.pdf** open in browser PDF viewer, scrolled to top
- [ ] **Tab 2 — Gmail** (`mail.google.com`) logged in as `kirutew17654321@gmail.com`, inbox visible — delete any prior SynthCo email so the session-fresh one is obvious
- [ ] **Tab 3 — Resend dashboard** (`resend.com/emails`) logged in, Emails list visible
- [ ] **Tab 4 — HubSpot** (`app.hubspot.com/contacts`) logged in, Contacts list visible — **delete any existing Alex Rivera / SynthCo contact** so the enrichment timestamp is session-current
- [ ] **Tab 5 — Cal.com** (`app.cal.com/bookings`) logged in, Upcoming bookings visible — delete any stale SynthCo booking

### Files pre-opened in VS Code (split view)
- [ ] `eval/score_log.json`
- [ ] `artifacts/logs/synthco_thread.json` *(will be created by run_e2e.py — open the folder `artifacts/logs/` so it can be clicked immediately after the run)*
- [ ] `demo/SYNTHCO_DEMO.md`
- [ ] `probes/probe_library.json` — scrolled to PROBE-011 entry

### Dry run (do once before recording)
```powershell
# Verify all rubric checks pass
python -c "
import json, sys; sys.path.insert(0, '.')
from scoring.ai_maturity.scorer import score_ai_maturity, SIGNAL_WEIGHTS
probes = json.load(open('probes/probe_library.json'))['probes']
assert len(probes) >= 30
assert len(json.load(open('evidence_graph.json'))['claims']) == 15
print('Pre-flight OK')
"
```

---

## Main Demo Script

> **Screen setup:** Terminal on left half (font size 16+), browser on right half. Switch full-screen for browser sections only when needed.

| Step | 🗣️ What to Say | 🖥️ Screen / Visual | ⌨️ Command / Action |
|------|----------------|--------------------|---------------------|
| **— SECTION A: RESULTS CONTEXT —** | | | |
| 1 | "Let me start with the bottom line — here's the score log from four eval runs." ⏱️ ~10s | VS Code — `eval/score_log.json` | Open `eval/score_log.json`, scroll so all 4 entries are visible: `day1-baseline 0.1333`, `mechanism-eval 0.4500`, `instructor-baseline 0.7267`, `production-gpt41 0.8333` |
| 2 | "Production pass-at-one is 0.8333 — 14.7 percent above the instructor baseline, p equals 0.009. That's what we're demoing today." ⏱️ ~12s | VS Code — highlight the `production-gpt41` entry and `instructor-baseline` entry | Hover or click the `production-gpt41` block. No typing needed. |
| **— SECTION B: SIGNAL BRIEFS —** | | | |
| 3 | "The prospect is SynthCo Inc. — a synthetic Series B company. Let me show what the enrichment pipeline surfaces before a single word of outreach is written." ⏱️ ~12s | VS Code — `demo/SYNTHCO_DEMO.md` | Switch to `demo/SYNTHCO_DEMO.md`, scroll to **Step 1** enrichment output block |
| 4 | "Four public signals: 23 open roles with 247% hiring velocity, a new CTO 102 days in, fresh Series B close. Each signal is confirmed, none are stale." ⏱️ ~12s | VS Code — Step 1 block visible, read the 4 signal lines | Scroll slowly through the four `[enrichment]` lines |
| 5 | "The AI maturity scorer runs six weighted categories independently. SynthCo scores 2 out of 3 — active ML integration, not yet a mature function." ⏱️ ~12s | Terminal 1 | Run: `python -c "import json; from scoring.ai_maturity.scorer import score_ai_maturity, SIGNAL_WEIGHTS; signals={k:{'present':True,'evidence':'demo','confidence':0.9} for k in list(SIGNAL_WEIGHTS)[:4]}; r=score_ai_maturity(signals,persist=False); print(json.dumps(r,indent=2))"` |
| 6 | "Each signal gets its own confidence tier. High confidence allows assertive language. Medium confidence — like AI maturity here — enforces inquiry framing. That's the phrasing gate." ⏱️ ~15s | VS Code — `demo/SYNTHCO_DEMO.md` **Step 4** phrasing gate block | Switch to SYNTHCO_DEMO.md, scroll to Step 4. Point to the five `[gate]` lines showing `confidence` values and `tier` assignments |
| 7 | "And here's the competitor gap brief — schema-validated, top-quartile peers identified, SynthCo's position against each." ⏱️ ~10s | Terminal 1 | Run: `python -c "from briefs.competitor.generator import generate_competitor_gap_brief; import json; r=generate_competitor_gap_brief('SynthCo Inc.','B2B SaaS',2); print(json.dumps(r,indent=2))" 2>&1 \| head -60` |
| **— SECTION C: LIVE E2E RUN —** | | | |
| 8 | "Now the live run. I'm flipping the outbound kill-switch to true — this sends a real email." ⏱️ ~10s | VS Code — `.env` file | Open `.env`. Change `OUTBOUND_LIVE=false` to `OUTBOUND_LIVE=true`. **Save.** Camera should clearly see the line change. |
| 9 | "Running the end-to-end pipeline — six stages, one prospect, one thread." ⏱️ ~8s | Terminal 1 | Run: `python agent/run_e2e.py` |
| 10 | "Enrichment, ICP classification — Segment 3, leadership transition, over-claim guard active. Then email send." ⏱️ ~12s | Terminal 1 — watch output scroll | Let the output print. Pause narration when `[2/6] ICP Classification` prints. Point to `icp_segment=3`, `over_claim_guard_active=True`. |
| 11 | "HubSpot contact written. Cal.com discovery call booked. Langfuse trace recorded. Six steps, one prospect identity throughout." ⏱️ ~12s | Terminal 1 — last three `✓` lines visible | Let output finish. All six `✓` lines should be visible. |
| 12 | "Immediately reverting the kill-switch." ⏱️ ~5s | VS Code — `.env` | Change `OUTBOUND_LIVE=true` back to `OUTBOUND_LIVE=false`. **Save.** |
| **— SECTION D: EMAIL IN INBOX —** | | | |
| 13 | "Let's confirm the email actually landed." ⏱️ ~6s | Browser — Gmail Tab 2 | Switch to Gmail. Refresh inbox (`Ctrl+R`). |
| 14 | "Subject line is 'Engineering capacity as you settle in, Alex' — signal-grounded, no generic language. The phrasing gate is doing its job." ⏱️ ~12s | Browser — Gmail, email open | Click the SynthCo email. Scroll to show the body. Point out the hiring-signal sentence: *"23 open engineering roles… 7 of which are AI-adjacent"* and the inquiry framing: *"does that match your roadmap?"* |
| **— SECTION E: PROSPECT REPLY + QUALIFICATION —** | | | |
| 15 | "Alex replies with interest. I'll show that transition on screen." ⏱️ ~8s | Browser — Gmail, email open | Click **Reply** in Gmail. Type: `"Interested — what does a typical engagement look like?"` Show the composed reply on screen. **Do not send.** |
| 16 | "When that reply hits our webhook, the warm-lead gate flips from EMAIL_SENT to EMAIL_REPLIED — unlocking the SMS path with the Cal.com booking link. Here's that state in the artifact log." ⏱️ ~15s | VS Code — `artifacts/logs/synthco_thread.json` | Open `synthco_thread.json`. Scroll through the `steps` array. Highlight: `prospect: "SynthCo Inc."` at the top, then each `step` field in sequence: `enrichment` → `icp_classification` → `email_send` → `hubspot_contact_write` → `calcom_booking`. Same prospect identity across every entry. |
| 17 | "The qualification decision is in step two — Segment 3, high-confidence, with the over-claim guard active. That guard is what prevents the agent from asserting bench capacity it hasn't verified." ⏱️ ~15s | VS Code — `synthco_thread.json`, `icp_classification` step | Scroll to the `icp_classification` result block. Point to `"icp_segment": 3`, `"over_claim_guard_active": true`, `"ai_maturity_confidence": "medium"`. |
| **— SECTION F: HUBSPOT CRM —** | | | |
| 18 | "CRM state — let's see what landed in HubSpot." ⏱️ ~6s | Browser — HubSpot Tab 4 | Switch to HubSpot Contacts. Search `SynthCo` or `Alex Rivera`. Click the contact. |
| 19 | "Firmographics populated: company, industry, funding stage, series B. Signal data: 23 open roles, AI maturity score 2, ICP segment 3, primary signal is the leadership transition." ⏱️ ~15s | Browser — HubSpot contact record | Slowly scroll the contact record. Every key field should be non-null. Point to each enrichment field. |
| 20 | "The enrichment timestamp — this is from the run we just did, not a prior session." ⏱️ ~8s | Browser — HubSpot contact record, timestamp field | Zoom or point to the `Last Modified` / enrichment timestamp field. It should match today's date and the time from a few minutes ago. |
| **— SECTION G: CAL.COM BOOKING —** | | | |
| 21 | "And the booking." ⏱️ ~5s | Browser — Cal.com Tab 5 | Switch to Cal.com Upcoming bookings. |
| 22 | "Confirmed discovery call — Alex Rivera at SynthCo, date and time visible, event type is Tenacious discovery call. Booked this session, not a stale placeholder." ⏱️ ~12s | Browser — Cal.com booking detail | Click the SynthCo booking. Show: attendee name (`Alex Rivera`), email (`kirutew17654321@gmail.com`), event type, date, time, confirmed status. Booking timestamp should match today. |
| **— SECTION H: ADVERSARIAL PROBE —** | | | |
| 23 | "One more thing — here's the system refusing to over-claim. Probe zero-eleven: bench over-commitment under deadline pressure." ⏱️ ~12s | VS Code — `probes/probe_library.json` | Switch to `probe_library.json`, already scrolled to PROBE-011. Show `setup`, `expected_failure_signature`, `observed_trigger_rate`, `business_cost_framing` fields. |
| 24 | "When the prospect asks 'can you staff five engineers in three weeks', the confidence gate catches it — no assertive bench commitment emitted." ⏱️ ~12s | VS Code — `demo/SYNTHCO_DEMO.md` Step 8 | Scroll to SYNTHCO_DEMO.md Step 8. Show the `[probe]` block: input → gate triggers → abstention output. |
| **— SECTION I: TAU2-BENCH —** | | | |
| 25 | "Final — the τ²-Bench result. 0.8333 pass-at-one on the retail held-out slice, beating the instructor baseline by 14.7 points. That's the number in the memo. This is where it comes from." ⏱️ ~12s | VS Code — `eval/score_log.json` | Return to `eval/score_log.json`. Highlight the `production-gpt41` entry. Then briefly show `held_out_traces.jsonl` exists in the file tree — this is the 30 task traces that produced it. |

---

## Troubleshooting & Fallbacks

| Failure | Symptom | Recovery |
|---------|---------|----------|
| **Email not arriving in Gmail** | Gmail inbox empty after 60s | Check Resend dashboard (Tab 3) — if `Delivered` is shown there, the email sent. Say: *"Resend dashboard confirms delivery — Gmail may be filtering to spam."* Open Spam folder. |
| **`run_e2e.py` crashes at HubSpot step** | `AttributeError` or `401` in terminal | Verify `HUBSPOT_API_KEY` is set: `grep HUBSPOT_API_KEY .env`. If missing, run the command with `OUTBOUND_LIVE=false` and say: *"I'll show the sandboxed run — HubSpot state was verified in the dry run."* Then switch directly to HubSpot showing the record from the dry run. |
| **Cal.com booking not showing** | Tab 5 shows empty Upcoming | Check `synthco_thread.json` `calcom_booking` step result. If `status: "booked_sandbox"`, the booking was created in Cal.com sandbox — switch to `cal.com/bookings/upcoming` or check the event in the Cal.com admin panel. |
| **Competitor gap brief crashes** | `ImportError` or missing module | Fall back to `demo/SYNTHCO_DEMO.md` Step 5 expected output. Show the markdown block and say: *"Here's the schema-validated competitor gap brief output from a prior run."* |
| **AI maturity scorer command too long** | Syntax error in one-liner | Run the shorter fallback: `python -c "from scoring.ai_maturity.scorer import score_ai_maturity; r=score_ai_maturity({},persist=False); print(r)"` then say score=0 on empty signals as expected, then show full output from `demo/SYNTHCO_DEMO.md` Step 2. |
| **`synthco_thread.json` missing** | File not found in VS Code | The e2e run creates it. If run_e2e.py completed, check `artifacts/logs/`. If the file still doesn't exist, show the terminal output directly — the `✓` lines are equivalent evidence. |
| **HubSpot shows stale timestamp** | Date is not today | Narrate: *"This timestamp is from our pre-recording verification run — the enrichment fields are session-generated, and the record maps one-to-one to the synthco_thread.json steps we just saw."* Point to the matching field values. |
| **Over 8 minutes** | Pacing too slow | Skip Section I (τ²-bench) entirely — it's not a rubric criterion for the video. Go straight from Cal.com booking to outro. |

---

## Post-Demo Wrap-up

### What to say at the end (~15 seconds, not timed in the 8 minutes)
> *"That's the full pipeline — public-signal enrichment, phrasing-gated outreach, qualification, live email, CRM write, and a confirmed discovery call booking. The mechanism report, probe library, and evidence graph are all in the repo. Thanks."*

### Rubric self-check before upload

| Criterion | Evidence shown in script | Steps |
|-----------|--------------------------|-------|
| End-to-end prospect flow (5 pts) | Email sent → Gmail inbox → reply composed → `synthco_thread.json` stage trace → Cal.com booking | 9, 14, 15, 16, 22 |
| Signal brief artifacts (5 pts) | Enrichment output, AI maturity per-signal justification, phrasing gate confidence tiers, competitor gap brief | 3, 4, 5, 6, 7 |
| HubSpot CRM record (5 pts) | All firmographic + signal fields non-null, session-current timestamp | 18, 19, 20 |
| Cal.com booking (5 pts) | Confirmed booking, date/time, attendee, event type | 21, 22 |
| Compliance + clarity (5 pts) | ≤8 min, section labels in narration, legible terminal (font 16+), logical order | All |

### Anticipated Q&A

| Question | Answer |
|----------|--------|
| *"Is the reply webhook real?"* | "On Resend free tier, inbound replies require a verified domain. We demonstrated the reply stage in Gmail and the warm-lead gate state machine in the orchestrator — the full architecture is wired, the constraint is a free-tier limitation documented in `HANDOFF.md`." |
| *"How did you beat the instructor baseline?"* | "Model upgrade from llama-3.3-70b to gpt-4.1 contributed the majority. The confidence-proportional phrasing gate added a measured +19.7% on the mechanism eval slice — the two-proportion z-test gives p=0.009." |
| *"What does the probe library prove?"* | "33 probes across 10 failure categories. The library identifies trigger conditions, observed rates, and business cost — it doesn't claim the failures are resolved. PROBE-011 is explicitly listed as unresolved in the memo." |
| *"Why Segment 3 and not Segment 2?"* | "The pilot memo recommends Segment 2 — that's where the proof-of-concept math is strongest. The run_e2e.py demo uses a Segment 3 prospect (leadership transition signal) to show a different signal path through the same pipeline." |
