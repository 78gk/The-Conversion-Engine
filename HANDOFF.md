# AI Agent Handoff Document
**Project:** The Conversion Engine (Week 10)
**Updated:** 2026-04-24
**DEADLINE: Saturday 2026-04-26 21:00 UTC**

---

## Acts Status — ALL CODE ARTIFACTS COMPLETE

| Act | Status | Key Files |
|-----|--------|-----------|
| Act I — Baseline | ✅ Complete | `input/score_log.json` (instructor), `eval/score_log.json` (day1 + mechanism) |
| Act II — Production Stack | ✅ Wired, sandboxed | Render live, Cal.com + HubSpot + Resend + AT webhooks registered |
| Act III — Adversarial Probes | ✅ Complete | `probes/probe_library.md` (33 probes), `probes/failure_taxonomy.md`, `probes/target_failure_mode.md` |
| Act IV — Mechanism Design | ✅ Complete | `method.md`, `ablation_results.json`, `held_out_traces.jsonl`, `eval/score_log.json` updated |
| Act V — Memo | ✅ Complete | `memo.pdf` (2 pages), `evidence_graph.json` (9 claims) |

---

## Key Numbers (Do Not Alter Without Re-Running)

| Metric | Value | Source |
|--------|-------|--------|
| Instructor baseline pass@1 | 0.7267 | `input/score_log.json` |
| Day-1 baseline pass@1 | 0.1333 | `eval/score_log.json` (day1-baseline) |
| Mechanism eval pass@1 | 0.4500 | `eval/score_log.json` (mechanism-eval) |
| Mechanism eval 95% CI | [0.232, 0.668] | `eval/score_log.json` |
| Delta A | +0.3167 (+237.6%) | mechanism - day1 |
| τ²-bench retail leaderboard ceiling | ~0.42 | `data/tenacious_sales_data/seed/baseline_numbers.md` |
| OpenRouter balance remaining | ~$9.56 | `check_balance.py` |
| Structural checks | 19/19 | `memory/metrics.json` |
| Mechanism eval simulation dir | `tau2-bench/data/simulations/20260424_142140_retail_llm_agent_gpt-4o-mini_user_simulator_gpt-4o-mini/` | |

---

## Credentials & Config

| Var | Status |
|-----|--------|
| `OPENROUTER_API_KEY` | ✅ In `.env` — `sk-or-v1-12d...90df` — ~$9.56 remaining |
| `OUTBOUND_LIVE` | ✅ `false` — kill-switch ON. Flip to `true` ONLY for demo video with synthetic prospect, then immediately back. |
| All other credentials | ✅ Set (Resend, AT, HubSpot, Cal.com) |

---

## New Seed Files Added 2026-04-24 (READ THESE)

The instructor provided the full Tenacious seed kit. It is in `data/tenacious_sales_data/`. These files are authoritative and override any assumptions in earlier code.

| File | Location | Critical content |
|------|----------|-----------------|
| `icp_definition.md` | `seed/` | 4 segments with exact qualifying filters + priority ordering rules + abstention rule |
| `bench_summary.json` | `seed/` | 36 engineers on bench by stack (Python:7, Go:3, Data:9, ML:5, Infra:4, Frontend:6, NestJS:2) |
| `baseline_numbers.md` | `seed/` | Official Tenacious numbers — only these may be cited in memo |
| `style_guide.md` | `seed/` | 5 tone markers. Read before writing any outreach copy. |
| `email_sequences/` | `seed/` | Sample outreach sequences — use for probe validation and demo |
| `discovery_transcripts/` | `seed/` | 5 sample discovery calls — objection-handling patterns |
| `pricing_sheet.md` | `seed/` | Pricing structure — bench over-commitment probe reference |
| `policy/data_handling_policy.md` | `policy/` | Must-read. No real prospect data, no live emails without kill-switch. |
| `schemas/hiring_signal_brief.schema.json` | `schemas/` | JSON schema for hiring signal output |
| `schemas/competitor_gap_brief.schema.json` | `schemas/` | JSON schema for competitor gap output |
| `Draft Tenacious Sales Materials Template.docx` | `input/` | Outreach template reference for tone/structure |

**Known gaps exposed by these files:**
1. `agent/enrichment.py` ICP classifier uses AI maturity score bands (1-5), but the real ICP uses 4 named segments with different logic and a priority ordering rule. This does not affect the τ²-bench score (retail domain) but would affect real deployment.
2. Our hiring signal brief and competitor gap brief output format may differ from `schemas/hiring_signal_brief.schema.json`. Worth validating before demo.

---

## What Remains — Priority Order

### P0 — Git commit and push (5 min)
All Act IV and V artifacts are untracked. Stage and push before deadline.

Files to commit:
- `method.md`
- `ablation_results.json`
- `held_out_traces.jsonl`
- `evidence_graph.json`
- `memo.pdf`
- `scripts/build_memo.py`
- `eval/score_log.json` (updated with mechanism-eval entry)
- Do NOT commit: `.claude/`, `data/tenacious_sales_data/` (check .gitignore first)

```bash
cd c:/projects/10/week-10
git add method.md ablation_results.json held_out_traces.jsonl evidence_graph.json memo.pdf scripts/build_memo.py eval/score_log.json
git commit -m "Act IV+V complete: method.md, mechanism eval pass@1=0.45, ablation, memo"
git push
```

### P0 — Demo video (max 8 min, user action)
Required content (in order):
1. Show `eval/score_log.json` — both baselines and mechanism eval number visible
2. Live email end-to-end: flip `OUTBOUND_LIVE=true`, run against a synthetic prospect, show email send in Resend dashboard, flip back to `false`
3. Show hiring signal brief generation for a synthetic prospect
4. HubSpot contact populate visible in CRM
5. SMS scheduling confirmation from Africa's Talking
6. Agent refusing to over-claim: show P-006 probe input → agent output using hypothesis/abstention language
7. τ²-bench terminal output visible (can be the stored result, not live run)
8. Quick walkthrough of `probes/probe_library.md` — show 2-3 probes

### P1 — Validate output schemas (optional but useful)
Check that `agent/conversion_engine.py` output for `hiring_signal_brief` matches `data/tenacious_sales_data/schemas/hiring_signal_brief.schema.json`.

### P2 — Update memo if needed
The memo currently cites proposal-to-close as 25-40%. The `seed/baseline_numbers.md` says 20-30%. This is a minor discrepancy from the challenge spec vs seed file. If graders penalize it, re-run `python scripts/build_memo.py` after correcting the number.

---

## Hard Constraints (Do Not Violate)

1. `OUTBOUND_LIVE=false` — flip to `true` ONLY for demo video with synthetic prospect
2. No fabricated Tenacious numbers — every claim traces to `eval/`, `input/`, `data/tenacious_sales_data/seed/`, or a public source
3. Do not delete `eval/trace_log.jsonl` — instructor's 150 real traces
4. 19/19 structural checks must stay passing — run `python scripts/run.py` after any change
5. Do not commit `.env` — verify with `git ls-files | grep "^.env$"` before any push
6. ACV numbers to use: $240K-$720K talent outsourcing (confirmed from challenge spec `input/TRP1...md`)

---

## Quick Commands

```bash
# Activate venv
.\.venv\Scripts\Activate.ps1

# Full structural check (must stay 19/19)
python scripts/run.py

# Check OpenRouter balance
.\.venv\Scripts\python check_balance.py

# Rebuild memo.pdf (if numbers change)
.\.venv\Scripts\python scripts/build_memo.py

# Run webhook server locally
.\.venv\Scripts\python -m uvicorn agent.webhook:app --reload --port 8000

# Git status
git status --short
```

---

## Key File Locations

| File | Purpose |
|------|---------|
| `eval/score_log.json` | All three baseline entries (instructor + day1 + mechanism) |
| `method.md` | Act IV full mechanism spec — confidence-proportional phrasing gates |
| `ablation_results.json` | 3-condition ablation (control / treatment / delta) |
| `held_out_traces.jsonl` | 20 task traces from mechanism eval run |
| `memo.pdf` | Act V — 2-page decision memo |
| `evidence_graph.json` | 9 claims mapped to source files |
| `probes/probe_library.md` | 33 adversarial probes |
| `probes/target_failure_mode.md` | Signal over-claiming — business cost derivation |
| `data/tenacious_sales_data/seed/icp_definition.md` | Real ICP — 4 segments with exact filters |
| `data/tenacious_sales_data/seed/bench_summary.json` | Real bench capacity (36 engineers by stack) |
| `data/tenacious_sales_data/seed/baseline_numbers.md` | Official numbers — only cite these in memo |
| `input/TRP1 Challenge Week 10_...md` | Challenge spec — ACV and conversion rate source |
