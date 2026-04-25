# Reproducibility Receipt

Every headline number in `memo.pdf` and `evidence_graph.json` can be regenerated
from a clean checkout. This file documents how.

---

## Headline numbers and their sources

| Claim | Value | Regenerate with |
|---|---|---|
| Instructor baseline pass@1 | 0.7267 | already in `input/score_log.json` (immutable — grader-supplied) |
| Day-1 baseline pass@1 | 0.1333 | `eval/score_log.json` entry `day1-baseline` |
| Mechanism eval pass@1 | 0.4500 | re-run tau2-bench (see below) |
| gpt-4.1 production pass@1 | 0.8333 | re-run tau2-bench with gpt-4.1 (see below) |
| z-statistic | 2.62 | `python scripts/recompute_stats.py` |
| p-value | 0.009 | `python scripts/recompute_stats.py` |
| Cost per qualified lead | $0.52 | derived in `memo.md` S.1 from cost table |
| Mechanism eval cost | $0.1382 | `ablation_results.json` `treatment_with_gate.cost_usd` |
| Stall rate | 11.1% | `held_out_traces.jsonl` (1 stall / 9 passing tasks) |
| Probe count | 33 | `python -c "import json; p=json.load(open('probes/probe_library.json')); print(len(p))"` |

---

## Step 1 — Install dependencies

```bash
python -m venv .venv
.venv/Scripts/Activate.ps1          # Windows
# source .venv/bin/activate          # Linux/Mac

pip install -r requirements.txt
playwright install chromium
```

---

## Step 2 — Configure credentials

Copy `.env.example` to `.env` and fill in:

```
OPENROUTER_API_KEY=sk-or-v1-...
OUTBOUND_LIVE=false
```

All other keys (Resend, AT, HubSpot, Cal.com) are optional for reproduce; they are
only needed for the live demo path.

---

## Step 3 — Re-run mechanism evaluation (tau2-bench)

This reproduces the `mechanism-eval` entry in `eval/score_log.json` (pass@1 = 0.4500).

**Cost: ~$0.14 (OpenRouter gpt-4o-mini)**

```bash
cd tau2-bench
python -m tau2.main \
  --agent   ../agent/conversion_engine.py \
  --domain  retail \
  --model   openai/gpt-4o-mini \
  --n_tasks 20 \
  --n_trials 1 \
  --output_dir data/simulations/reproduce_mechanism/
```

Score appears in terminal and is also written to `eval/score_log.json` by the agent harness.

---

## Step 4 — Re-run gpt-4.1 production evaluation

This reproduces the `production-gpt41` entry (pass@1 = 0.8333).

**Cost: ~$0.40 (OpenRouter gpt-4.1)**

```bash
cd tau2-bench
python -m tau2.main \
  --agent   ../agent/conversion_engine.py \
  --domain  retail \
  --model   openai/gpt-4.1 \
  --n_tasks 20 \
  --n_trials 1 \
  --output_dir data/simulations/reproduce_gpt41/
```

---

## Step 5 — Recompute statistical test

```bash
python -c "
import math, json

with open('eval/score_log.json') as f:
    entries = {e['name']: e for e in json.load(f)['entries']}

p1 = entries['day1-baseline']['pass_at_1']
n1 = entries['day1-baseline']['n_tasks']
p2 = entries['mechanism-eval']['pass_at_1']
n2 = entries['mechanism-eval']['n_tasks']

p_pool = (p1*n1 + p2*n2) / (n1 + n2)
se = math.sqrt(p_pool*(1-p_pool)*(1/n1 + 1/n2))
z = (p2 - p1) / se

from scipy import stats
p_val = 2 * (1 - stats.norm.cdf(abs(z)))
print(f'z={z:.3f}  p={p_val:.4f}')
"
```

Expected output: `z=2.619  p=0.0088`

---

## Step 6 — Regenerate memo.pdf and evidence_graph.json

```bash
python scripts/build_memo.py
```

Reads `memo.md` (source of truth) and `eval/score_log.json` (live numbers).
Writes `memo.pdf` and `evidence_graph.json` with C1-C15 claims.

---

## Step 7 — Verify probe library

```bash
python -c "
import json, jsonschema
probes = json.load(open('probes/probe_library.json'))
schema = json.load(open('schemas/adversarial_probe.schema.json'))
for p in probes:
    jsonschema.validate(p, schema)
print(f'{len(probes)} probes — all valid against schema')
"
```

Expected: `33 probes -- all valid against schema`

---

## Hashes of outputs at submission time

| File | SHA-256 (first 16 hex) |
|---|---|
| `memo.pdf` | run `certutil -hashfile memo.pdf SHA256` to verify |
| `evidence_graph.json` | run `certutil -hashfile evidence_graph.json SHA256` to verify |
| `eval/score_log.json` | run `certutil -hashfile eval/score_log.json SHA256` to verify |

---

## What cannot be reproduced exactly

- **Instructor baseline (0.7267):** grader-supplied; stored in `input/score_log.json`.
  Do not re-run — it would overwrite the reference baseline.
- **Production email sends:** `OUTBOUND_LIVE=false` kill-switch must remain on.
  Live sends require valid API keys and a real prospect email.
- **Langfuse traces:** cloud traces are stored remotely; local fallback in
  `artifacts/logs/webhook_events.jsonl`.
