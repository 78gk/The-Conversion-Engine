# REPORT_RUBRIC.md

> **Purpose:** This file is the canonical grading rubric for AI agents reviewing the final report before submission. Agents must evaluate each criterion, assign a score, identify gaps, and iteratively improve the report until every criterion reaches its **maximum score**. Do not submit until all seven criteria reach their maximum points.

---

## How to Use This Rubric (Agent Instructions)

```
FOR EACH criterion in this rubric:
  1. READ every sub-check listed under the criterion
  2. READ the relevant section(s) of the final report carefully
  3. ASSIGN the matching score tier (0, 2/3, 6/9, or 10/15)
  4. LIST every missing or incomplete item as a concrete TODO
  5. REWRITE or EXPAND the relevant report section to address each TODO
  6. RE-EVALUATE after each change to confirm the score moved up
REPEAT until all seven criteria reach maximum points
THEN output a final scorecard with direct quote citations for each criterion
```

---

## Scoring Tiers (Global Reference)

| Label | Description |
|-------|-------------|
| **Mastered** | Full points — all sub-checks satisfied with specificity and honesty |
| **Competent** | Partial points — core elements present but one named element missing |
| **Developing** | Minimal points — fundamental elements absent or too vague to act on |
| **Unsatisfactory** | Zero points — criterion not addressed or actively contradicted |

---

## Maximum Points by Criterion

| # | Criterion | Max Points |
|---|-----------|-----------|
| 1 | Executive Decision Framing | 10 |
| 2 | Cost per Qualified Lead Derivation | 10 |
| 3 | Stalled-thread Rate Delta | 10 |
| 4 | Competitive-gap Outbound Reply-rate Delta | 10 |
| 5 | Pilot Scope Specificity | 15 |
| 6 | Public-signal Lossiness of AI Maturity Scoring | 10 |
| 7 | Honest Unresolved Failure from the Mechanism | 10 |
| | **TOTAL** | **75** |

---

## Criterion 1 — Executive Decision Framing

**What is being evaluated:** Whether the memo opens with a clear, decision-oriented headline that a busy CEO or CFO could act on in thirty seconds.

### Sub-Checks (all must pass for 10 pts)

| ID | Sub-Check | Pass Condition |
|----|-----------|----------------|
| A1 | Executive Summary exists | A summary of **roughly three sentences** appears at or before the first section break |
| A2 | Names the build | The summary states what was built (the system, agent, or pipeline name) |
| A3 | Headline number in context | A headline performance number is given **with a baseline or manual process comparison** (not a bare number) |
| A4 | Specific recommendation with parameters | Recommendation is binary or specific — includes named segment, scope, budget, or named conditions. Not "continue to evaluate" or "consider a pilot" |
| A5 | Executive register | Reads as a memo to executives — no research exposition, no passive hedging, no filler sentences |

### Score Tiers

#### ✅ Mastered — 10 pts
Tight three-sentence summary that:
- Names the build
- Gives a headline number **in context** (against a baseline or manual process)
- States a specific recommendation with parameters

**Example of Mastered:**
> *"We built an AI-powered outbound pipeline that reduced stalled-thread rate from 35% to 11% against synthetic prospects. Signal-grounded outreach delivered a 14-point reply-rate lift over generic sequences (18% vs. 4%) at $3.20 per qualified lead. Recommendation: run a 30-day Segment 2 pilot at 150 leads per week on a $1,200 weekly budget, with a success threshold of 12% reply rate on signal-grounded outreach."*

#### ⚠️ Competent — 6 pts
Three-sentence summary with a recommendation, but **one of the following is missing:**
- Recommendation is soft ("consider a pilot") without specifying scope
- Headline number asserted without context (e.g., "pass@1 of 0.58" with no comparison)

#### 🔴 Developing — 2 pts
**One or more of the following:**
- No concrete recommendation
- Written as research exposition without a decision framing
- Summary exceeds three sentences with meaningful content lost in filler
- Missing decision orientation, brevity, or executive register

#### ⛔ Unsatisfactory — 0 pts
No executive summary, or the recommendation is buried beyond the first section.

### Agent TODO Template
```
[ ] A1: Ensure executive summary appears in the first section, ≤3 sentences with no filler
[ ] A2: Name the build explicitly in sentence 1
[ ] A3: State the headline number AND its baseline/manual-process comparison in sentence 2
[ ] A4: Make the recommendation binary or parameterized in sentence 3
      (segment name + lead volume + budget + named conditions)
[ ] A5: Read the summary aloud — would a CFO act on it in 30 seconds? Revise if not
```

---

## Criterion 2 — Cost per Qualified Lead Derivation

**What is being evaluated:** Whether the memo derives cost per qualified lead from its inputs rather than asserting a single number. Covers the visible derivation and definitional clarity in the memo only.

### Sub-Checks (all must pass for 10 pts)

| ID | Sub-Check | Pass Condition |
|----|-----------|----------------|
| B1 | Dollar figure stated | Cost per qualified lead expressed as a dollar figure (e.g., $3.20) |
| B2 | Qualification definition stated | "Qualified lead" is explicitly defined or recoverable from surrounding text — not just implied |
| B3 | LLM spend itemized | LLM cost component broken out separately |
| B4 | Rig/infrastructure usage itemized | Compute or rig cost component broken out separately |
| B5 | Any enrichment API costs itemized | Additional API costs (Crunchbase, scraping, etc.) included or explicitly noted as zero |
| B6 | Derivation shown | Arithmetic from inputs to final cost per lead is visible (not just inputs listed separately from the conclusion) |
| B7 | Number compared against a target | Final number compared against either the challenge cost envelope or an implicit manual process cost |

### Score Tiers

#### ✅ Mastered — 10 pts
- Clear qualification definition
- All cost inputs itemized (LLM + rig + enrichment APIs)
- Derivation shown (arithmetic visible)
- Final number compared against a target

**Example of Mastered:**
> *"A 'qualified lead' is a prospect who replied to at least one outbound sequence and did not immediately unsubscribe. Total cost for 312 leads: LLM calls $48.20, compute (rig) $18.40, Crunchbase enrichment $6.00 = $72.60 total. Qualified leads: 22. Cost per qualified lead: $72.60 ÷ 22 = $3.30, compared to an estimated $8–12 manual research-and-touch cost per lead."*

#### ⚠️ Competent — 6 pts
Inputs shown and qualification definition given, but **one of the following is missing:**
- Definition is loose ("leads that look promising")
- One input category absent (LLM cost shown, rig usage ignored)

#### 🔴 Developing — 2 pts
**One or more of the following:**
- Dollar figure asserted with zero breakdown of inputs
- "Qualified lead" undefined — number could mean cost per email, per contact, or per booking
- Input decomposition or definitional clarity absent

#### ⛔ Unsatisfactory — 0 pts
No cost per lead number, or a number with no derivation of any kind.

### Agent TODO Template
```
[ ] B1: State cost per qualified lead as a dollar figure
[ ] B2: Define "qualified lead" explicitly (e.g., "replied and did not unsubscribe within 72 hours")
[ ] B3: Break out LLM spend as a separate line item with dollar amount
[ ] B4: Break out rig/compute cost as a separate line item with dollar amount
[ ] B5: Break out enrichment API costs OR explicitly state $0 with rationale
[ ] B6: Show arithmetic: sum of inputs ÷ qualified lead count = cost per lead
[ ] B7: Compare final number against challenge cost envelope or manual process cost estimate
```

---

## Criterion 3 — Stalled-thread Rate Delta

**What is being evaluated:** Whether the memo honestly compares its stalled-thread rate to the 30–40% manual baseline, with the math visible.

### Sub-Checks (all must pass for 10 pts)

| ID | Sub-Check | Pass Condition |
|----|-----------|----------------|
| C1 | "Stalled" is defined in this system's context | Definition states the threshold (e.g., "no outbound action within N hours after an inbound reply") |
| C2 | System's measured rate reported | An actual measured stalled-thread rate reported (not projected or claimed) |
| C3 | Comparison to 30–40% baseline shown | The system rate is explicitly compared against the 30–40% manual baseline |
| C4 | Math visible | The arithmetic from raw counts to the rate percentage is shown or clearly recoverable |
| C5 | Synthetic prospect caveat acknowledged | Memo acknowledges that measurement was over synthetic prospects and may not transfer directly to production |

### Score Tiers

#### ✅ Mastered — 10 pts
- Stall definition stated
- System measurement reported
- Comparison to 30–40% baseline shown
- Memo acknowledges the synthetic prospect caveat or other transfer risks

**Example of Mastered:**
> *"We define a stalled thread as any inbound reply receiving no outbound follow-up within 4 hours. Across 87 synthetic prospect interactions, 10 threads stalled — an 11.5% stall rate, compared to the 30–40% manual baseline. Note: this measurement was conducted over synthetic prospects; real-prospect responsiveness and edge-case variety may shift this rate in production."*

#### ⚠️ Competent — 6 pts
System's stalled-thread rate reported with a defined threshold, compared to the 30–40% baseline, but **the following is missing:**
- No honest caveat about synthetic prospect conditions

#### 🔴 Developing — 2 pts
**One or more of the following:**
- Number claimed without any definition of "stalled" in this system's context
- Comparison to the 30–40% baseline with no evidence of measurement ("our system will reduce stalls")
- Stall definition or measured evidence absent

#### ⛔ Unsatisfactory — 0 pts
No mention of stalled-thread rate or speed-to-lead metric of any kind.

### Agent TODO Template
```
[ ] C1: Define "stalled thread" explicitly with the hour threshold (e.g., "no follow-up within 4 hours of inbound reply")
[ ] C2: Report the actually measured stall rate (threads stalled ÷ total threads with inbound reply = X%)
[ ] C3: Compare system rate to 30–40% manual baseline explicitly
[ ] C4: Show the arithmetic (e.g., "10 stalled of 87 threads = 11.5%")
[ ] C5: Add honest caveat: "measured over synthetic prospects; production transfer risk acknowledged"
```

---

## Criterion 4 — Competitive-gap Outbound Reply-rate Delta

**What is being evaluated:** Whether the memo compares reply rates between research-grounded outbound and generic outbound, with a methodology that isolates the variable being tested. Covers how the comparison is presented and caveated in the memo.

### Sub-Checks (all must pass for 10 pts)

| ID | Sub-Check | Pass Condition |
|----|-----------|----------------|
| D1 | Two variants defined | Signal-grounded variant and generic variant are both explicitly named and described |
| D2 | Assignment method stated | How prospects were placed into each variant is described (prevents confound ambiguity) |
| D3 | Reply rates reported for both | Both variants have a reply rate stated |
| D4 | Sample size or interaction count given | Context for each variant's rate (e.g., "8 of 44" not just "18%") |
| D5 | Delta stated in percentage points | Delta expressed as percentage points, not only in relative terms ("2× better" insufficient alone) |
| D6 | Statistical honesty — small sample caveat | If sample is small (< ~100 per arm), memo flags the limitation and treats delta as suggestive, not conclusive |

### Score Tiers

#### ✅ Mastered — 10 pts
- Both variants defined with assignment method
- Reply rates reported with sample size
- Delta quantified in percentage points
- Either the sample supports the claim OR the memo flags the small-sample limitation and treats the delta as suggestive

**Example of Mastered:**
> *"Prospects were assigned alternately — odd-numbered to signal-grounded, even-numbered to generic outreach. Signal-grounded: 8 replies of 44 interactions (18.2%). Generic: 2 replies of 46 interactions (4.3%). Delta: +13.9 percentage points. Sample is small; this should be treated as directionally suggestive pending a larger pilot."*

#### ⚠️ Competent — 6 pts
Both reply rates given with sample context, delta in percentage points stated, but:
- Sample is small enough to be meaningless (e.g., 2/20 vs. 1/20) and this limitation is **not acknowledged**

#### 🔴 Developing — 2 pts
**One or more of the following:**
- Only one variant's reply rate reported
- Both reported but assignment method absent
- Comparison itself or experimental setup missing

#### ⛔ Unsatisfactory — 0 pts
No reply-rate comparison between variants.

### Agent TODO Template
```
[ ] D1: Name and describe both variants (signal-grounded vs. generic)
[ ] D2: State how prospects were assigned to each variant (alternating, random, cohort-based)
[ ] D3: Report reply rate for BOTH variants
[ ] D4: Include raw counts alongside percentages (e.g., "8 of 44" not just "18%")
[ ] D5: Express delta in percentage points explicitly (not only relative terms)
[ ] D6: If n < 100 per arm, add: "Small sample — treat as directionally suggestive, not conclusive"
```

---

## Criterion 5 — Pilot Scope Specificity

**What is being evaluated:** Whether the pilot recommendation names a specific segment, a specific lead volume, a specific weekly budget, and a specific measurable success criterion.

> ⚠️ **This criterion is worth 15 points — weight accordingly.**

### Sub-Checks (all must pass for 15 pts)

| ID | Sub-Check | Pass Condition |
|----|-----------|----------------|
| E1 | Named segment | One specific segment named (e.g., "Segment 2: Series B SaaS companies with 3+ AI-adjacent job posts") — not "the most promising segment" |
| E2 | Segment choice justified | Segment choice is argued against the memo's own findings, not selected arbitrarily |
| E3 | Lead volume stated | A specific lead volume stated (e.g., "150 leads per week") |
| E4 | Budget stated | A weekly or total budget stated (e.g., "$1,200 per week") |
| E5 | Success criterion has a number | Success criterion includes a specific threshold (e.g., "12% reply rate") |
| E6 | Success criterion has a metric definition | The metric being measured is defined (not just "improved conversion") |
| E7 | Success criterion has a timeframe | 30-day or specific measurement window stated |

### Score Tiers

#### ✅ Mastered — 15 pts
All four elements present and specific:
- Named segment with justification from memo findings
- Lead volume
- Budget
- Success criterion with number + metric definition + 30-day window

**Example of Mastered:**
> *"Recommended pilot: Segment 2 (Series B SaaS companies in the AI/data infrastructure space with AI maturity score ≥ 2 and 3+ open AI-adjacent roles in the past 60 days). This segment showed the highest reply-rate delta in our test runs and aligns with Tenacious's highest ACV band. Run 150 leads per week over 30 days at a $1,200 weekly budget ($8.00 per lead). Success criterion: ≥12% reply rate on signal-grounded outreach measured at Day 30, with ≤$5.00 cost per qualified lead."*

#### ⚠️ Competent — 9 pts
Segment, volume, and budget named, but **the success criterion is missing one of:**
- A specific threshold number
- A metric definition
- A timeframe

#### 🔴 Developing — 3 pts
Pilot named but **three or more of the four elements** (segment, volume, budget, success criterion) are missing or vague.

#### ⛔ Unsatisfactory — 0 pts
No pilot recommendation, or a recommendation at the level of "run a pilot" with no parameters.

### Agent TODO Template
```
[ ] E1: Name one specific segment (not generic — include defining characteristics)
[ ] E2: Justify segment choice by citing findings from elsewhere in the memo
[ ] E3: State a specific lead volume (e.g., "150 leads per week")
[ ] E4: State a weekly or total budget with dollar amount
[ ] E5: Add a numeric threshold to the success criterion (e.g., "≥12% reply rate")
[ ] E6: Define the metric being measured (e.g., "reply rate = any non-bounce reply within 7 days")
[ ] E7: Set a 30-day measurement window explicitly
```

---

## Criterion 6 — Public-signal Lossiness of AI Maturity Scoring

**What is being evaluated:** Whether the memo acknowledges and characterizes the known false positive and false negative modes of AI maturity scoring with concrete archetypes.

### Sub-Checks (all must pass for 10 pts)

| ID | Sub-Check | Pass Condition |
|----|-----------|----------------|
| F1 | False positive mode named with concrete archetype | At least one named false positive (a company scoring high for the wrong reasons), with a concrete company type or scenario |
| F2 | False positive — agent's wrong action spelled out | What the agent does wrong in this case is explicit (e.g., "pitches Segment 4 positioning to a company that is just noisy") |
| F3 | False positive — business impact tied to Tenacious mechanics | Business impact expressed in terms of brand, segment mismatch, wasted touch, or dollar equivalent |
| F4 | False negative mode named with concrete archetype | At least one named false negative (a company scoring low while actually AI-mature), with a concrete company type or scenario |
| F5 | False negative — agent's wrong action spelled out | What the agent does wrong in this case is explicit |
| F6 | False negative — business impact tied to Tenacious mechanics | Business impact expressed in Tenacious-specific terms |

### Score Tiers

#### ✅ Mastered — 10 pts
Both directions named with concrete archetypes. Agent's wrong action spelled out for each. Business impact tied to Tenacious's pitch mechanics (brand, segment mismatch, wasted touch).

**Example of Mastered:**
> *"False positive: a 'loud but shallow' company — large public GitHub presence, frequent AI conference speaking, but no actual production ML workloads. Our scorer rates them a 3; the agent pitches our highest-tier AI transformation offering. The business impact: brand damage with a technically sophisticated audience that immediately recognizes the pitch as misaligned — equivalent to a wasted senior touch in the $80K–120K ACV band. False negative: a 'quietly sophisticated' company — no public GitHub, minimal executive commentary, but running a proprietary ML platform internally. Our scorer rates them a 0; the agent sends Segment 1 introductory copy. The business impact: we under-pitch to a buyer who is ready for Segment 4 engagement, ceding that ACV to a competitor who conducted deeper discovery."*

#### ⚠️ Competent — 6 pts
Both directions named with concrete archetypes, but **business impact is absent or generic:**
- "bad outreach" or "could damage the brand" without segment-specific or dollar-specific framing

#### 🔴 Developing — 2 pts
**One or more of the following:**
- Errors mentioned abstractly without distinguishing false positive from false negative
- Only one direction discussed

#### ⛔ Unsatisfactory — 0 pts
No discussion of scoring errors, or a generic "all models have errors" acknowledgment.

### Agent TODO Template
```
[ ] F1: Name a concrete false positive archetype (e.g., "loud but shallow" — public AI noise, no production ML)
[ ] F2: State what the agent does wrong for the false positive case specifically
[ ] F3: Express business impact in Tenacious terms: brand, segment mismatch, ACV band, wasted touch
[ ] F4: Name a concrete false negative archetype (e.g., "quietly sophisticated" — proprietary stack, no public signal)
[ ] F5: State what the agent does wrong for the false negative case specifically
[ ] F6: Express business impact in Tenacious terms for the false negative case
```

---

## Criterion 7 — Honest Unresolved Failure from the Mechanism

**What is being evaluated:** Whether the memo names a specific failure that the built mechanism did not resolve, including the business impact of deploying anyway.

### Sub-Checks (all must pass for 10 pts)

| ID | Sub-Check | Pass Condition |
|----|-----------|----------------|
| G1 | Specific failure named | One specific failure named — not "the system sometimes makes mistakes" |
| G2 | Triggering conditions stated | The conditions that cause the failure are described (not just the failure type) |
| G3 | Probe category identified | Failure is tied to an identifiable probe category (e.g., signal over-claiming under defensive replies, bench over-commitment under pressure, tone drift after multiple turns) |
| G4 | Honest admission mechanism did not resolve it | Explicit statement that the built mechanism did not fix this failure — not hedged as "may sometimes" |
| G5 | Business impact quantified or segment-specific | Business impact stated in the memo's own unit economics terms — segment, ACV band, stall rate, or dollar estimate per N leads |

### Score Tiers

#### ✅ Mastered — 10 pts
- Specific failure with triggering conditions
- Honest admission that the mechanism did not resolve it
- Business impact expressed in the memo's own unit economics terms

**Example of Mastered:**
> *"The mechanism did not resolve bench over-commitment under pressure. When a prospect directly asks whether Tenacious can place a full AI engineering team within 30 days, the agent responds with affirmative language in approximately 3% of Segment 2 conversations — even when bench capacity data is absent from the context window. This failure category (PROBE-011: bench over-commitment under deadline pressure) was not resolved by the confidence-gating mechanism; the gate triggers on factual uncertainty but not on scoped delivery claims. Deployed at 150 leads per week against Segment 2, this represents roughly 4–5 conversations per week where the agent makes an unverifiable commitment — estimated at $X in remediation cost or goodwill damage per incident in the $80K–120K ACV band."*

#### ⚠️ Competent — 6 pts
Specific failure named with triggering conditions, but **business impact is generic:**
- "could damage the brand" without segment, ACV, or stall-rate framing

#### 🔴 Developing — 2 pts
**One or more of the following:**
- Failure mentioned vaguely ("the agent occasionally drifts")
- Triggering conditions not identified
- Business impact absent

#### ⛔ Unsatisfactory — 0 pts
No unresolved failure disclosed, or an "everything works" framing that contradicts the rest of the skeptic's appendix.

### Agent TODO Template
```
[ ] G1: Name one specific failure (not a category — a specific behavior)
[ ] G2: State the triggering conditions (what input or context causes this failure)
[ ] G3: Tie the failure to a named probe category from the adversarial probe library
[ ] G4: Add explicit statement: "The [mechanism name] did not resolve this failure because [reason]"
[ ] G5: Quantify business impact: frequency per N leads × segment ACV band × remediation cost
      OR tie to stall rate or conversion rate impact with visible arithmetic
```

---

## Final Scorecard Template (Agent Output)

> Fill this out after each evaluation pass. Target: all criteria at maximum before submission.

```markdown
# Pre-Submission Report Scorecard

| # | Criterion | Max | Score | Missing Items |
|---|-----------|-----|-------|---------------|
| 1 | Executive Decision Framing | 10 | /10 | |
| 2 | Cost per Qualified Lead Derivation | 10 | /10 | |
| 3 | Stalled-thread Rate Delta | 10 | /10 | |
| 4 | Competitive-gap Outbound Reply-rate Delta | 10 | /10 | |
| 5 | Pilot Scope Specificity | 15 | /15 | |
| 6 | Public-signal Lossiness of AI Maturity Scoring | 10 | /10 | |
| 7 | Honest Unresolved Failure from the Mechanism | 10 | /10 | |
| | **TOTAL** | **75** | **/75** | |

## Evidence Citations
> Direct quotes from the report supporting each score

- Criterion 1 (A1–A5): "[quote]" — location: [section/paragraph]
- Criterion 2 (B1–B7): "[quote]" — location: [section/paragraph]
- Criterion 3 (C1–C5): "[quote]" — location: [section/paragraph]
- Criterion 4 (D1–D6): "[quote]" — location: [section/paragraph]
- Criterion 5 (E1–E7): "[quote]" — location: [section/paragraph]
- Criterion 6 (F1–F6): "[quote]" — location: [section/paragraph]
- Criterion 7 (G1–G5): "[quote]" — location: [section/paragraph]

## Remaining TODOs Before Resubmission
1. 
2. 
3. 

## Ready for Submission?
[ ] All criteria at maximum points
[ ] Total = 75/75
[ ] All TODOs cleared
[ ] No "everything works" framing anywhere in the report
[ ] No uncontextualized numbers (every metric has a baseline or caveat)
```

---

## Agent Iteration Protocol

```
WHILE total_score < 75:
  FOR criterion IN criteria:
    score = evaluate(criterion, report)
    IF score < max_score(criterion):
      todos = identify_missing_sub_checks(criterion)
      FOR todo IN todos:
        rewrite_report_section(todo)
      re_score = evaluate(criterion, report)
      ASSERT re_score > score  # verify improvement

  IF no_progress_made_in_full_pass:
    ESCALATE "Manual review required — blocked on: [specific sub-check ID and reason]"

OUTPUT final_scorecard(
  scores=per_criterion_scores,
  citations=direct_quote_evidence,
  total=sum(scores)
)

ASSERT total == 75 before marking report as ready for submission
```

---

## Common Failure Patterns to Avoid

| Pattern | Criterion Affected | Why It Fails |
|---------|-------------------|--------------|
| Asserting a number without showing arithmetic | 2, 3, 7 | Graders cannot verify the derivation |
| "Consider running a pilot" with no parameters | 1, 5 | Not actionable — executives cannot execute a vague instruction |
| Relative-only comparisons ("2× better") | 4 | Cannot assess magnitude without percentage point delta |
| "All models have limitations" acknowledgment | 6, 7 | Generic — does not name the specific failure shape |
| No synthetic prospect caveat on stall rate | 3 | Overstates production readiness |
| Segment described as "most promising" | 5 | Not named — not executable |
| Business impact as "brand damage" only | 6, 7 | Not tied to Tenacious unit economics — not actionable |
| Executive summary > 3 sentences | 1 | Loses executive register; buries the decision |

---

*This rubric is the source of truth for report grading. A criterion is only at maximum points when **every** sub-check passes — not when the majority pass. When in doubt, re-read the sub-check pass conditions and compare them against a direct quote from the report.*