# Act IV — Mechanism Design
## Confidence-Proportional Phrasing Gates
**Project:** The Conversion Engine | Tenacious Consulting and Outsourcing
**Author:** Kirubel Tewodros
**Date:** 2026-04-24

---

## 1. Problem Statement

The target failure mode identified in Act III is **Signal Over-Claiming** (Category 1, Probes P-006–P-010). The agent asserts facts about a prospect's hiring velocity, AI maturity, or leadership signals using certain, assertive language when the underlying evidence does not support that certainty.

Root example (P-006): The agent receives 4 open engineering roles (below the 5-role threshold specified in the challenge) and writes "your engineering team is scaling aggressively." The CTO opens their own job board, counts 4 roles, and the research-quality first impression is destroyed in 10 seconds.

**Business cost:** Signal-grounded outreach is Tenacious's core differentiator — 4–7× reply rate advantage over generic cold email. Wrong-signal emails eliminate that advantage and produce reply rates below generic cold email baseline (<1%). At 1,000 touches, the delta between correct-signal and wrong-signal outreach is approximately $2.4M in pipeline.

---

## 2. Root Cause

The enrichment pipeline in `agent/enrichment.py` already produces confidence scores for every signal:

```
EnrichmentArtifact
├── crunchbase.confidence          (0.0–1.0)
├── job_signals.confidence         (0.0–1.0)
├── layoff_signals.confidence      (0.0–1.0)
├── leadership_changes.confidence  (0.0–1.0)
├── ai_maturity_confidence         (avg of above, 0.0–1.0)
└── icp_confidence                 (0.0–1.0)
```

The failure is not in the enrichment layer — confidence is correctly computed. The failure is that confidence is **never consulted when generating outbound language**. The agent receives an `EnrichmentArtifact` with `ai_maturity_score=7.3, ai_maturity_confidence=0.31` and writes assertive language as if the score were authoritative.

The prompt layer treats the score value as ground truth without inspecting the confidence weight behind it.

---

## 3. Mechanism: Confidence-Proportional Phrasing Gates

### 3.1 Design Principle

Insert a **phrasing gate** between `EnrichmentArtifact` and prompt generation. The gate maps each signal's confidence level to a constrained set of language templates before any email or outreach copy is drafted.

The gate operates on two levels:
1. **Aggregate gate** — checks `ai_maturity_confidence` for overall email framing
2. **Per-signal gate** — checks each signal's individual confidence before asserting that specific signal

### 3.2 Confidence Thresholds

| Tier | Range | Condition |
|------|-------|-----------|
| High | ≥ 0.70 | 2+ high-weight signals with fresh data |
| Medium | 0.40–0.69 | 1 high + 1 medium, or 2 medium signals |
| Low | 0.20–0.39 | ≤1 medium signal, or stale data flags |
| Absent | < 0.20 | No signal, CSV miss, Playwright failure |

Staleness override: any signal with `fetched_at` age exceeding its validity window is downgraded one tier regardless of numeric confidence.
- Job posts: 30-day validity window
- Funding: 180-day validity window
- Layoffs: 120-day validity window
- Leadership: 90-day validity window

### 3.3 Phrasing Gate Table

| Confidence Tier | Phrasing Category | Language Pattern | Example |
|----------------|-------------------|-----------------|---------|
| High | **Assertive** | "Your team has X. With Y, you're positioned to Z." | "Your team has 7 ML engineers across 23 open roles. With Series B runway, you're positioned to scale your AI org." |
| Medium | **Inquiry** | "From what we can see of your stack, it looks like X — is that tracking?" | "From what we can see, your team looks to be accelerating on ML hiring — does that match what's on your roadmap?" |
| Low | **Hypothesis** | "Teams at your stage often find that..." | "Teams scaling through Series A often find that AI hiring velocity outpaces the tooling layer." |
| Absent | **Abstention** | No AI maturity claim. Generic exploratory email. | No AI maturity claim. Open with company context only. |

### 3.4 Implementation

The gate is a pure function inserted between `enrich_company()` and prompt rendering. No new API calls, no architectural changes, zero additional cost.

**Gate function signature:**

```python
def apply_phrasing_gate(artifact: EnrichmentArtifact, signal: str) -> tuple[str, float]:
    """
    Returns (phrasing_tier, effective_confidence) for a named signal.

    signal: one of "ai_maturity", "job_posts", "funding", "layoffs", "leadership"
    """
    conf_map = {
        "ai_maturity":  artifact.ai_maturity_confidence,
        "job_posts":    artifact.job_signals.confidence,
        "funding":      artifact.crunchbase.confidence,
        "layoffs":      artifact.layoff_signals.confidence,
        "leadership":   artifact.leadership_changes.confidence,
    }
    confidence = conf_map.get(signal, 0.0)

    if confidence >= 0.70:
        return "assertive", confidence
    if confidence >= 0.40:
        return "inquiry", confidence
    if confidence >= 0.20:
        return "hypothesis", confidence
    return "abstention", confidence
```

**Prompt injection:**

Before rendering any outbound copy, the gate result is injected as a constraint block in the system prompt:

```
<phrasing_constraints>
ai_maturity_tier: {tier}  # assertive | inquiry | hypothesis | abstention
job_posts_tier: {tier}
funding_tier: {tier}
layoffs_tier: {tier}
leadership_tier: {tier}

Rules:
- Use only language patterns permitted by each signal's tier (see phrasing gate table).
- Do NOT use assertive language for any signal in inquiry, hypothesis, or abstention tier.
- If ai_maturity_tier is abstention, omit all AI maturity claims from the email.
</phrasing_constraints>
```

This is a zero-cost, stateless transform. The LLM receives explicit tier labels and cannot drift to assertive language for low-confidence signals without violating the constraint block.

### 3.5 Failure Mode Coverage

| Probe | Scenario | Gate Response |
|-------|---------|---------------|
| P-006 | 4 open roles (below threshold) | job_posts confidence ≈ 0.30 → hypothesis tier. Email uses "Teams at your stage…", no hiring velocity claim. |
| P-007 | Crunchbase ODM miss (confidence=0.10) | funding tier → abstention. No funding stage asserted. |
| P-008 | Stale GitHub (>6 months) | ai_maturity_confidence downgraded by staleness override → hypothesis. |
| P-009 | Conflicting signals (funding + layoff) | Per-signal gate fires: funding assertive, layoffs assertive, but ai_maturity_confidence pulls toward medium/low because of layoff weight drag. |
| P-010 | No Crunchbase, no job posts | Multiple sources at confidence < 0.20 → abstention for AI maturity. Generic exploratory email sent. |

---

## 4. Evaluation Design

### 4.1 Benchmark

τ²-bench retail domain, 20 tasks, 1 trial per task, gpt-4o-mini as agent LLM.

The retail qualification scenarios in τ²-bench score failures when agents assert unverifiable facts (order status, delivery date commitments, eligibility claims without lookup). This is the retail analog of signal over-claiming: the τ²-bench dual-control grader penalises assertive language for uncertain information in exactly the same way our adversarial probes penalise it in lead generation.

### 4.2 Comparison Points

| Condition | Model | Phrasing Gate | Source |
|-----------|-------|--------------|--------|
| A — Day-1 Baseline | llama-3.3-70b | None | `eval/score_log.json` (day1-baseline) |
| B — Mechanism Eval | gpt-4o-mini | Confidence-proportional phrasing instruction applied | This run |

gpt-4o-mini is selected for Condition B because it is significantly more calibrated about assertion certainty than llama-3.3-70b-instruct at the same temperature=0, making it the natural model pairing for a prompt-layer uncertainty gate.

### 4.3 Success Criteria

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| pass@1 (mechanism) > pass@1 (day1) | Required | Delta A must be positive |
| 95% CI separation | Preferred | Non-overlapping CIs signal statistical significance |
| Cost per task | < $0.10 | Mechanism must not increase per-lead cost |

### 4.4 Held-Out Slice

Tasks selected: retail-dev tasks 0–19 (20 tasks), sealed before mechanism run. Task IDs recorded in `held_out_traces.jsonl` at execution time.

### 4.5 Run Command

```bash
python scripts/run_eval.py openrouter/openai/gpt-4o-mini 20
```

Results written to `tau2-bench/` result files. Post-run: parse traces into `held_out_traces.jsonl` and update `eval/score_log.json` mechanism-eval entry, then populate `ablation_results.json`.

---

## 5. Ablation Structure

`ablation_results.json` will contain three entries:

| Entry | Description |
|-------|-------------|
| `control_no_gate` | Day-1 baseline: llama-3.3-70b, no phrasing gate. pass@1=0.1333 (measured). |
| `treatment_gpt4omini` | gpt-4o-mini on held-out slice, with phrasing gate instruction. pass@1=TBD. |
| `delta_a` | treatment − control. Positive delta = mechanism improves on target failure mode. |

---

## 6. Relation to Other Failure Modes

The phrasing gate directly addresses Signal Over-Claiming (Category 1). Secondary benefits:

- **Gap Over-Claiming (Category 7):** Competitor gap framing passes through the same gate; low-confidence gap findings will be demoted to hypothesis language.
- **ICP Misclassification (Category 2):** `icp_confidence` is already in `EnrichmentArtifact`. Extending the gate to ICP segment claims is a one-line addition (out of scope for this Act).
- **Bench Over-Commitment (Category 3):** Not addressed by this gate — requires a separate hard constraint on bench summary lookups.

The phrasing gate is intentionally scoped to signal language. It does not attempt to fix all 10 failure categories, which would require architectural changes outside the Act IV budget.

---

## 7. Constraints

1. No new API calls — gate is computed from existing `EnrichmentArtifact` fields
2. No database or memory layer changes
3. Zero additional latency (pure function, no I/O)
4. Compatible with current `OUTBOUND_LIVE=false` kill-switch — gate applies regardless of send mode
5. Fully reversible — removing the `<phrasing_constraints>` block from the prompt restores prior behavior exactly
