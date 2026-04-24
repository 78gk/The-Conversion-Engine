# Baseline — The Conversion Engine

## Reference Baseline (Program-Provided)

| Metric | Value | Source |
|---|---|---|
| pass@1 | **0.7267** | `input/score_log.json` |
| 95% CI | [0.6504, 0.7917] | `input/score_log.json` |
| Trials per task | 5 | `input/score_log.json` |
| Total simulations | 150 (30 tasks × 5) | `input/score_log.json` |
| Avg agent cost | $0.0199 / task | `input/score_log.json` |
| p50 latency | 105.95s | `input/score_log.json` |
| p95 latency | 551.65s | `input/score_log.json` |

Provided by program staff per instructor update (2026-04-24). All trainees work from this same reference baseline. Raw traces: `input/trace_log.jsonl` (150 entries).

## Our Day-1 Baseline (Act I)

| Metric | Value | Source |
|---|---|---|
| pass@1 | **0.1333** | `eval/score_log.json` → `day1-baseline` |
| 95% CI | [0.053, 0.297] | Wilson interval at α=0.05 |
| Model | `meta-llama/llama-3.3-70b-instruct` | `eval/score_log.json` |
| Trials per task | 1 | `eval/score_log.json` |
| Total tasks | 30 | `eval/score_log.json` |
| Cost per run | $0.2710 | `eval/score_log.json` |
| p50 latency | 4,287ms | `eval/score_log.json` |

This is our own reproduction run used as the **Delta A denominator** for Act IV mechanism evaluation. A weak model (llama-3.3-70b) on 1 trial — the mechanism targets improvement above this bar.

## Delta Targets (Act IV)

| Delta | Formula | Required |
|---|---|---|
| Delta A | mechanism_pass@1 − 0.1333 | Must be positive, p < 0.05 |
| Delta B | mechanism_pass@1 − automated_opt_baseline | Report honestly; underperformance explained |
| Delta C | mechanism_pass@1 − 0.7267 | Informational only |

## Unexpected Behavior (Day-1 Run)

llama-3.3-70b-instruct failed most multi-tool-call tasks — the model frequently resolved the user message without completing the required tool sequence. Single-step tasks passed at a higher rate. This is a model capability ceiling, not a harness issue. Switching to gpt-4o-mini is expected to close the gap substantially.
