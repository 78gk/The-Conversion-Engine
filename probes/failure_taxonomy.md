# Failure Taxonomy — The Conversion Engine
**Act III | Tenacious Consulting and Outsourcing**

---

## Taxonomy Overview

Probes are grouped into 10 categories. Each category maps to a distinct business risk area for Tenacious. The taxonomy is ordered by observed trigger rate (most-frequent first), derived from the probe inputs applied to the baseline agent.

| # | Category | Probes | Trigger Rate (est.) | Peak Business Cost |
|---|---|---|---|---|
| 1 | Signal Over-Claiming | P-006–P-010 | High | Brand credibility loss |
| 2 | ICP Misclassification | P-001–P-005 | High | Wrong pitch, DQ'd prospect |
| 3 | Bench Over-Commitment | P-011–P-014 | Medium | Contract dispute, delivery failure |
| 4 | Tone Drift | P-015–P-018 | Medium | Warm-reply abandonment |
| 5 | Scheduling Edge Cases | P-026–P-028 | Medium | Missed discovery call |
| 6 | Signal Reliability | P-029–P-031 | Medium | Research quality undermined |
| 7 | Gap Over-Claiming | P-032–P-033 | Medium | Defensive prospect, pushback |
| 8 | Dual-Control Coordination | P-023–P-025 | Low–Medium | Booking failure, legal exposure |
| 9 | Multi-Thread Leakage | P-019–P-020 | Low | Trust destruction |
| 10 | Cost Pathology | P-021–P-022 | Low | Budget overrun |

---

## Category Detail

### 1. Signal Over-Claiming (P-006–P-010)
**Definition:** The agent asserts facts about the prospect using certain language when the underlying signal is weak, ambiguous, or below the stated confidence threshold.

**Root cause:** The enrichment pipeline produces scores and signals without propagating confidence weights into the prompt. The agent uses the score value without calibrating its language to the evidence strength behind that score.

**Tenacious-specific impact:** Signal-grounded outreach is Tenacious's core differentiator. An over-claimed signal (wrong hiring velocity, stale GitHub activity presented as current AI engagement) destroys the research-quality impression that makes signal-grounded email 4–7× more effective than generic outreach.

**Trigger conditions:** AI maturity score derived from ≤2 medium-weight inputs; job-post count < 5; stale data (GitHub > 6 months, Crunchbase > 180 days for funding, layoffs > 120 days).

---

### 2. ICP Misclassification (P-001–P-005)
**Definition:** The agent assigns the wrong ICP segment, triggering a pitch that is misaligned with the prospect's actual buying context.

**Root cause:** The segment classifier uses a priority order that is not aligned with the signal weighting in the spec. The most recent signal date is used as a proxy for the most relevant signal — but a 60-day-old layoff outweighs a 5-month-old funding round for segment assignment.

**Tenacious-specific impact:** The four ICP segments exist because different buying contexts require different pitches. A Segment 1 pitch to a Segment 2 company (post-layoff, cost pressure) is the worst-case mismatch: it reads as either uninformed or tone-deaf. The prospect has one interaction with Tenacious; the segment determines whether that interaction opens a door or closes it.

**Trigger conditions:** Conflicting signals (funding + layoff); signals near time-window boundaries (funding at 175 days, layoff at 125 days); missing Crunchbase record.

---

### 3. Bench Over-Commitment (P-011–P-014)
**Definition:** The agent makes implicit or explicit commitments about Tenacious's delivery capacity that are not supported by the bench summary.

**Root cause:** The agent is not gated against the bench summary at commitment generation time. The bench summary is loaded as context but is not enforced as a hard constraint.

**Tenacious-specific impact:** Bench utilization is Tenacious's primary operating metric. Over-committing capacity through an agent that has no authority to do so creates a mismatch that the delivery lead must resolve on the first call — a damaging first impression.

**Trigger conditions:** Prospect asks for specific headcount, stack, or start-date commitments. Agent does not route to human handoff.

---

### 4. Tone Drift (P-015–P-018)
**Definition:** The agent's language departs from the Tenacious style guide after one or more turns of prospect engagement.

**Root cause:** The style guide is applied to the first draft only. Follow-up messages are generated without re-checking the style guide's key tone markers: directness, no filler, specificity, professional register.

**Tenacious-specific impact:** The prospect's first message is written by a human-sounding agent. If turns 2–4 read differently, the prospect correctly infers automation. The research-quality signal that made the first message compelling is undermined.

**Trigger conditions:** Multi-turn threads (3+ turns); prospect pushback or objection; prospect uses informal register.

---

### 5. Scheduling Edge Cases (P-026–P-028)
**Definition:** The agent proposes or confirms calendar slots that are invalid due to timezone ambiguity, holidays, or prospect preference changes.

**Root cause:** Cal.com integration returns UTC times. The agent does not translate to the prospect's local timezone or check for regional holidays before proposing slots.

**Tenacious-specific impact:** Tenacious's prospect pool spans EU, US, and East Africa. Timezone errors produce missed calls — the single highest-cost scheduling failure.

---

### 6. Signal Reliability (P-029–P-031)
**Definition:** The agent uses signal data that is stale, conflicting with a more authoritative source, or over-interpreted given the known false-positive rate.

**Root cause:** The enrichment pipeline does not compare cross-source consistency (Crunchbase ODM vs. company website) and does not flag signals outside their validity windows (180d funding, 120d layoffs, 90d leadership change).

---

### 7. Gap Over-Claiming (P-032–P-033)
**Definition:** The agent presents competitor gap findings in a framing that is condescending, overstated given the sample size, or implies the prospect is behind in a way they will find insulting.

**Root cause:** The competitor_gap_brief is produced as a factual output. The agent does not calibrate the delivery framing to the prospect's likely self-perception or the size and quality of the comparison sample.

---

### 8. Dual-Control Coordination (P-023–P-025)
**Definition:** The agent proceeds with a booking, escalation, or commitment step without waiting for explicit prospect confirmation.

**Root cause:** The agent optimizes for task completion (booking the call) over respecting the dual-control protocol (prospect must confirm each step).

---

### 9. Multi-Thread Leakage (P-019–P-020)
**Definition:** Information from one prospect's conversation thread bleeds into a different prospect's thread.

**Root cause:** Thread isolation is not enforced at the memory layer. If the agent's context window includes multiple active threads, signal leakage is possible.

---

### 10. Cost Pathology (P-021–P-022)
**Definition:** A prompt or interaction pattern that causes token usage or API call counts to spike beyond the per-lead cost target.

**Root cause:** No token budget guard on individual interactions. No short-circuit on enrichment pipeline when all signal sources return empty.
