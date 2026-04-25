# Progress Update Script — The Conversion Engine
**Day 3 Standup | 2026-04-23 | Presenter: Kirubel**
**Tone:** Confident, precise, honest. Not overselling. Not underselling.

---

## OPENING (30 seconds)

> "Good morning. I'm Kirubel, and I'm presenting for The Conversion Engine — our automated lead generation and conversion system for Tenacious Consulting.

> We hit the interim deadline last night. The repository is live at github.com/78gk/The-Conversion-Engine and the interim report is in there. I want to walk you through what we actually built, what the numbers mean, and where we're headed."

---

## SECTION 1: WHAT WE BUILT (60 seconds)

> "The core idea is simple: Tenacious's salespeople spend most of their day doing research that a well-designed agent can do in seconds. Find a company, check their funding, check their hiring velocity, detect if there's a new CTO, score their AI maturity, then write a personalised email based on exactly those signals.

> We built a 6-phase agentic loop: Plan → Build → Evaluate → Debug → Improve → Report. Every phase is independently restartable from a state file, which means if something breaks mid-run, you don't lose everything.

> The signal enrichment pipeline checks five sources: Crunchbase for funding, job boards for hiring velocity, layoffs.fyi for disqualification signals, public sources for leadership changes, and a custom scoring model for AI maturity on a 0-to-3 scale.

> The output is a hiring signal brief and a competitor gap brief for each prospect — the information a Tenacious salesperson would normally spend two hours collecting."

---

## SECTION 2: THE BENCHMARK FRAMEWORK (60 seconds)

> "Now, the benchmark. The challenge requires τ²-Bench — an academic benchmark from Sierra Research that evaluates AI agents in real-world customer service conversations. It has a published retail leaderboard with a ceiling of about 42%.

> We have the harness cloned and the measurement pipeline in place. The score log, trace log, and baseline file are all structured to receive the real results. What we do NOT have yet is a live LLM API key wired through the τ²-bench CLI — which is what actually runs the tasks against a real model.

> The simulated run we did to validate the evidence pipeline structure showed the framework works end-to-end. But I want to be clear: we have not claimed a real pass@1 score. The score log explicitly marks the benchmark entry as pending a real run. That run is the first thing we do this morning.

> What IS a real measurement: the structural integrity of the repository. 19 out of 19 automated checks pass. That's not a simulated number — that's the actual evaluator running against the actual files."

---

## SECTION 3: THE PRODUCTION STACK (45 seconds)

> "For the production stack — email via Resend, SMS via Africa's Talking, CRM via HubSpot, and booking via Cal.com — we're in sandboxed mode for the interim. All the integration points are wired and the functions exist, but we haven't provisioned the live API credentials yet.

> The reason is straightforward: standing up a live outbound email pipeline in one afternoon without a public webhook server means you have no way to receive replies, which means you have no end-to-end thread. You just have a sender with no ears.

> Our instructor confirmed exactly what we needed yesterday: use Render's free tier for the webhook backend. One stable public URL, registered across all four platforms. That's Day 4 — Render deployed, API keys provisioned, one real end-to-end thread with our synthetic prospect, SynthCo Inc."

---

## SECTION 4: WHAT'S HONEST (30 seconds)

> "What's not done: the live integrations, the adversarial probe library, and the mechanism design paper. Those are Acts III and IV — due Saturday.

> I'm not going to dress those up. The framework for all of them exists. The hard architectural decisions are made. The webhook server is the unlock — once that's deployed tomorrow morning, the rest follows in sequence.

> The structural integrity is solid: 19 out of 19 automated checks pass. The codebase is clean. The evidence is non-fabricated and every number in the report traces back to a file in the repository."

---

## SECTION 5: THE PLAN (30 seconds)

> "Day 4: Render deployment, live API keys, real end-to-end thread.
> Day 5: Full τ²-Bench run with 5 trials, Langfuse observability, enrichment sweep.
> Day 5–6: 30+ adversarial probes — Tenacious-specific failure modes.
> Day 6: Mechanism design, ablation testing.
> Day 7: The two-page decision memo.

> The goal is the same one the brief sets out: a system trustworthy enough that the Tenacious CEO would point it at live revenue. We're building toward that bar."

---

## CLOSING (15 seconds)

> "That's the update. Repository is public, report is comprehensive, numbers are real. Happy to take questions."

---

## ANTICIPATED QUESTIONS — PRE-PREPARED ANSWERS

**Q: "Where is your actual pass@1 score?"**
> "We don't have one yet — and we're not claiming one. The score log explicitly marks the τ²-bench entry as pending a real run. What we have is the measurement framework: harness cloned, score log structured, trace log structured. The real run is this morning, Day 4. The spec says the baseline is due by the final submission Saturday — the interim deadline covered Acts I framework and Act II framework, not the sealed results."

**Q: "Why didn't you run the benchmark before the interim?"**
> "Running τ²-bench against a real model requires a live API key routed through the τ²-bench CLI, and the `uv` package manager which wasn't available in our environment at the time. Critically: the spec says 'fabricated Tenacious numbers are a disqualifying violation.' Claiming a pass@1 from a random number generator would have been that violation. We chose to mark it honestly as pending rather than fabricate a result."

**Q: "Why didn't you have live email working for the interim?"**
> "Standing up a live outbound pipeline responsibly requires a webhook server to receive replies — otherwise you're sending into a void with no way to qualify responses. The instructor confirmed Render as the solution yesterday. We prioritised getting the framework, evidence, and report right over sending a single real email with no reply handling."

**Q: "What does 'sandboxed mode' actually mean?"**
> "It means all outbound routes to an internal sink instead of real prospect inboxes. The code path is identical — the only difference is the `outbound_live` flag in config.yaml is set to false. Flip that to true once the Render webhook URL is registered, and the system is live."

**Q: "What is the actual value delivered to Tenacious right now?"**
> "Right now: the enrichment framework, the ICP classifier, and the hiring signal brief. Those alone replace 2–3 hours of manual research per prospect. The automation of the outreach and booking loop is what gets delivered by Saturday."

**Q: "Can the system over-claim signals it isn't confident about?"**
> "No — that's a hard design constraint. The ICP classifier has an abstention mode: if confidence is below threshold, the agent sends a generic exploratory email instead of a wrong-segment pitch. The AI maturity scorer outputs a confidence level alongside the score, and the prompt templates are built to hedge language proportionally. The challenge spec calls this out explicitly and the graders check for it."

---

## NOTES FOR PRESENTER

- **Focus on the framework** — explain that you built the research and enrichment system first.
- **The word "sandboxed" will get a question** — use the pre-prepared answer above, don't get defensive.
- **If asked about team** — this is a solo submission from Kirubel; be clear and confident about that.
- **Slide suggestion:** One slide per section (5 slides total). No bullet dumps. One metric per slide, big font.
- **Time target:** 4 minutes for the main script, 2 minutes for Q&A. Total: 6 minutes.
