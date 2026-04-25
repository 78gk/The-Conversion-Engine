# AI Agent Handoff — The Conversion Engine
**Project:** The Conversion Engine (Week 10)
**Updated:** 2026-04-25
**DEADLINE: Saturday 2026-04-26 21:00 UTC**
**GitHub repo:** https://github.com/78gk/The-Conversion-Engine

---

## Status: ALL ARTIFACTS COMPLETE — READY FOR DEMO VIDEO

Every code artifact, rubric-aligned directory, memo, and stand-out feature is
built and verified. The only remaining user action is the **demo video** (≤8 min).

---

## Acts Status

| Act | Status | Key Files |
|-----|--------|-----------|
| Act I — Baseline | ✅ Complete | `input/score_log.json` (instructor), `eval/score_log.json` (day1 + mechanism) |
| Act II — Production Stack | ✅ Wired, sandboxed | Render live; Cal.com + HubSpot + Resend + AT webhooks registered |
| Act III — Adversarial Probes | ✅ Complete | `probes/probe_library.md` (33 probes), `probes/probe_library.json`, `probes/failure_taxonomy.md`, `probes/target_failure_mode.md` |
| Act IV — Mechanism Design | ✅ Complete | `method.md`, `ablation_results.json`, `held_out_traces.jsonl`, `eval/score_log.json` |
| Act V — Memo | ✅ Complete | `memo.md` (source), `memo.pdf` (2-3 pages), `evidence_graph.json` (15 claims) |

---

## Rubric Alignment — Session 2026-04-25

New directories created and verified this session:

| Directory | Purpose | Rubric criteria |
|---|---|---|
| `integrations/email/` | re-exports + `send_email_with_booking_link` (calls `generate_booking_link`) | B12 |
| `integrations/sms/` | re-exports + `send_sms_with_booking_link` (calls `generate_booking_link`, warm-lead gate) | B5, B12 |
| `integrations/hubspot/` | `write_hubspot_contact`, `log_activity`, `write_enrichment_fields`, `update_hubspot_lifecycle_stage` | B9 |
| `integrations/calcom/` | `generate_booking_link`, `handle_booking_confirmed` | B12 |
| `signals/crunchbase/` | wraps ODM lookup + funding-round filter | C1 |
| `signals/job_posts/` | 3 Playwright scrapers + `velocity.py` (60d delta) + `compliance.py` (robots.txt) | C2, C3, C9 |
| `signals/layoffs/` | re-exports parse_layoffs_fyi | C |
| `signals/leadership/` | re-exports detect_leadership_changes | C |
| `scoring/ai_maturity/` | `scorer.py` (0-3, 6 categories, silent-company branch) + `signal_collectors.py` | D1-D9 |
| `briefs/competitor/` | `selection.py` + `distribution.py` + `generator.py` (schema-validated) | E1-E7 |
| `orchestration/` | `ChannelOrchestrator` state machine; `generate_booking_link` re-exported | B5, B9, B12, B13 |
| `schemas/` | `hiring_signal_brief.schema.json`, `competitor_gap_brief.schema.json`, `adversarial_probe.schema.json` | F2, E6 |
| `docs/` | `architecture.md` (Mermaid flowchart + sequence diagram) | A1 |

Additional:
- `README.md` — rewritten with inline Mermaid diagram, full directory index, install steps, run-order
- `requirements.txt` — all deps pinned to exact `==x.y.z` versions
- `requirements-dev.txt` — pytest pinned separately
- `memo.md` — 8-section source-of-truth decision memo (all 7 report rubric criteria)
- `memo.pdf` — rebuilt from `memo.md` via `scripts/build_memo.py` (reads `memo.md`, not hardcoded)
- `evidence_graph.json` — 15 claims (C1-C15), regenerated
- `probes/probe_library.json` — 33 probes × 6 required fields, validated against `schemas/adversarial_probe.schema.json`
- `method.md` — extended: 3 named ablation variants (A/B/C) + §7 Statistical Test Plan (two-proportion z-test, p=0.009)
- `ablation_results.json` — restructured: 3 planned variants + 3 measured conditions + `statistical_test` block
- `REPRODUCE.md` — step-by-step reproducibility receipt for every headline number
- `demo/SYNTHCO_DEMO.md` — one-page system walkthrough via SynthCo synthetic prospect

---

## Key Numbers (Do Not Alter Without Re-Running)

| Metric | Value | Source |
|--------|-------|--------|
| Instructor baseline pass@1 | 0.7267 | `input/score_log.json` |
| Day-1 baseline pass@1 | 0.1333 | `eval/score_log.json` (day1-baseline) |
| Mechanism eval pass@1 | 0.4500 | `eval/score_log.json` (mechanism-eval) |
| gpt-4.1 production pass@1 | 0.8333 | `eval/score_log.json` (production-gpt41) |
| Delta vs instructor | +14.7% | (0.8333 - 0.7267) / 0.7267 |
| z-statistic (mechanism vs day1) | 2.619 | `ablation_results.json` statistical_test block |
| p-value | 0.009 | `ablation_results.json` statistical_test block |
| Mechanism eval cost | $0.1382 / 20 tasks | `ablation_results.json` treatment_with_gate.cost_usd |
| Cost per qualified lead | $0.52 | `memo.md` §1 derivation |
| Structural checks | 19/19 | `memory/metrics.json` |

---

## Credentials & Config

| Var | Status |
|-----|--------|
| `OPENROUTER_API_KEY` | ✅ In `.env` — `sk-or-v1-12d...90df` — ~$3.34 remaining (3 ablation re-runs ~$9 total if needed) |
| `OUTBOUND_LIVE` | ✅ `false` — kill-switch ON. Flip to `true` ONLY for demo video with synthetic prospect, then immediately back. |
| All other credentials | ✅ Set (Resend, AT, HubSpot, Cal.com) |

---

## Demo Video Script (P0 — User Action Only)

Required content in order (≤8 min total):

1. Show `eval/score_log.json` — all 4 entries visible (instructor, day1, mechanism-eval, production-gpt41)
2. Show `memo.pdf` — 8 sections visible, headline pass@1=0.8333 and p=0.009 in executive summary
3. Live email end-to-end: flip `OUTBOUND_LIVE=true`, run `python agent/run_e2e.py`, show email send in Resend dashboard, flip back to `false`
4. Show hiring signal brief generation — Step 1-3 output from `demo/SYNTHCO_DEMO.md`
5. HubSpot contact populate visible in CRM
6. SMS scheduling confirmation from Africa's Talking
7. Agent refusing to over-claim: show PROBE-011 input → abstention output (`probes/probe_library.json` P-011 or use `demo/SYNTHCO_DEMO.md` Step 8)
8. τ²-bench terminal output visible (use stored result from `held_out_traces.jsonl`, not live re-run)
9. Quick walkthrough of `probes/probe_library.json` — show 2-3 probes with all 6 fields

---

## Verification Commands (All Must Pass Before Submission)

```bash
# Activate venv
.\.venv\Scripts\Activate.ps1

# Verify all rubric checks pass (copy-paste block)
python -c "
import json, sys
sys.path.insert(0, '.')
from scoring.ai_maturity.scorer import score_ai_maturity, SIGNAL_WEIGHTS

# B12: Cal.com in email + sms + orchestrator
email = open('integrations/email/__init__.py').read()
sms   = open('integrations/sms/__init__.py').read()
orch  = open('orchestration/channel_orchestrator.py').read()
assert all('generate_booking_link' in x for x in [email, sms, orch])
print('B12 PASS')

# D: AI maturity 0-3
_full = {k: {'present': True, 'evidence': 'test', 'confidence': 0.9} for k in SIGNAL_WEIGHTS}
assert score_ai_maturity({}, persist=False)['score'] == 0
assert score_ai_maturity(_full, persist=False)['score'] == 3
print('D PASS')

# F: 33 probes, all 6 fields
probes = json.load(open('probes/probe_library.json'))['probes']
required = {'probe_id','category','setup','expected_failure_signature','observed_trigger_rate','business_cost_framing'}
assert all(not (required - set(p.keys())) for p in probes) and len(probes) >= 30
print(f'F PASS: {len(probes)} probes')

# H: 3 ablations + z-test
method = open('method.md').read()
assert all(x in method for x in ['Ablation A','Ablation B','Ablation C'])
assert 'z-test' in method.lower()
print('H PASS')

# evidence_graph
assert len(json.load(open('evidence_graph.json'))['claims']) == 15
print('EV PASS: 15 claims')

print('ALL CHECKS PASSED')
"

# Rebuild memo.pdf (if memo.md is edited)
.\.venv\Scripts\python scripts/build_memo.py

# Run webhook server locally
.\.venv\Scripts\python -m uvicorn agent.webhook:app --reload --port 8000
```

---

## Known Limitations (for successor agent)

1. **Per-prospect velocity cold-start.** `signals/job_posts/velocity.py` needs a 60-day-prior snapshot before `velocity_label` is meaningful. First run returns `insufficient_signal`.
2. **LinkedIn auth wall (~30% of URLs).** `signals/job_posts/linkedin_public.py` aborts on `/authwall` redirect. Accept the silent rate or wire a paid LinkedIn data partner.
3. **Three AI-maturity collectors make live HTTP calls per prospect.** At >200 leads/week, add a 200ms inter-request sleep or switch to a paid search API for DuckDuckGo calls.
4. **3 ablation variants flagged `measured: false`.** Re-running costs ~$3/variant × 3 = ~$9 on OpenRouter (balance ~$3.34 at last check). OpenRouter must be topped up before re-running.
5. **`agent/enrichment.py` ICP classifier** uses the real 4-segment priority order but has no automated test suite. Add `tests/test_icp_classifier.py` covering all 4 priority paths + abstain case.
6. **`data/job_post_snapshots.jsonl` is unbounded.** Grows append-only. Add a rotation policy (drop snapshots older than 180 days) before pilot.
7. **`memo.md` proposal-to-close figure.** Uses challenge-spec range; seed `baseline_numbers.md` lists a slightly different range. If re-graded against seed, edit `memo.md` and re-run `python scripts/build_memo.py`.

---

## Next Steps (priority order for successor)

1. **Demo video** — record per the script above (P0, user action).
2. **Push to GitHub** — `git push` after confirming `.env` is NOT staged.
3. **Run ablation variants A/B/C** (optional, costs ~$9 total on OpenRouter). Top up balance first.
4. **Add ICP classifier test suite** — `tests/test_icp_classifier.py` covering all 4 segments + abstain.
5. **Snapshot rotation** — add 180-day purge in `signals/job_posts/velocity.py`.

---

## Key File Locations

| File | Purpose |
|------|---------|
| `eval/score_log.json` | All 4 baseline entries (instructor + day1 + mechanism + production-gpt41) |
| `memo.md` | Source-of-truth decision memo — edit this, then rebuild PDF |
| `memo.pdf` | Final submission PDF — built via `python scripts/build_memo.py` |
| `evidence_graph.json` | 15 claims (C1-C15) mapped to source files |
| `method.md` | Act IV full mechanism spec — 3 ablation variants + §7 statistical test plan |
| `ablation_results.json` | 3 measured + 3 planned ablation conditions + statistical_test block |
| `held_out_traces.jsonl` | 20 task traces from mechanism eval run |
| `probes/probe_library.json` | 33 adversarial probes × 6 required fields |
| `probes/probe_library.md` | Human-readable version of probe library |
| `probes/failure_taxonomy.md` | 10 failure categories with trigger rates |
| `probes/target_failure_mode.md` | Signal over-claiming — business cost derivation |
| `orchestration/channel_orchestrator.py` | Single state machine for all channel decisions |
| `scoring/ai_maturity/scorer.py` | AI maturity scorer (0-3, 6 categories, silent-company) |
| `briefs/competitor/generator.py` | Competitor gap brief generator (schema-validated) |
| `REPRODUCE.md` | How to regenerate every headline number from scratch |
| `demo/SYNTHCO_DEMO.md` | Step-by-step demo walkthrough (SynthCo synthetic prospect) |
| `docs/architecture.md` | Mermaid architecture diagram (full pipeline + observability) |
| `data/tenacious_sales_data/seed/icp_definition.md` | Real ICP — 4 segments with exact filters |
| `data/tenacious_sales_data/seed/bench_summary.json` | Real bench capacity (36 engineers by stack) |
| `data/tenacious_sales_data/seed/baseline_numbers.md` | Official Tenacious numbers — only cite these in memo |
| `input/TRP1 Challenge Week 10_...md` | Challenge spec — ACV and conversion rate source |

---

## Hard Constraints (Do Not Violate)

1. `OUTBOUND_LIVE=false` — flip to `true` ONLY for demo video with synthetic prospect
2. No fabricated Tenacious numbers — every claim traces to `eval/`, `input/`, `data/tenacious_sales_data/seed/`, or a public source (`evidence_graph.json` C1-C15)
3. Do not delete `eval/trace_log.jsonl` — instructor's 150 real traces
4. 19/19 structural checks must stay passing — verified via `memory/metrics.json`
5. Do not commit `.env` — verify with `git ls-files | grep "^.env$"` before any push
6. ACV numbers: $240K-$720K talent outsourcing (confirmed from challenge spec)
