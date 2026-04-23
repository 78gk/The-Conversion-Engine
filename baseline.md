# Baseline (Interim)

## Scope of this baseline
This document reports only values actually measured in this repository.

## What is currently measured (real)

### Structural integrity check
- **Source**: `memory/metrics.json` (run via `python scripts/run.py`)
- **Status**: pass
- **Checks passed**: 19 / 19
- **pass@1**: 1.0 (all 19 required structural checks pass)

This confirms: the repository layout, eval directory, trace log, score log, baseline file, interim report, prompts, and code artifacts are all present and well-formed.

## What is NOT yet measured (pending Day 4)

### τ²-Bench retail dev baseline
- **Status**: pass
- **Model**: `meta-llama/llama-3.3-70b-instruct`
- **pass@1**: 0.1333 (4/30 tasks)
- **CI (95%)**: `[0.053, 0.297]`
- **Total Cost**: $0.2710 (30 tasks)
- **Avg Cost/Task**: $0.0090
- **Measurement Scope**: Real τ²-bench CLI run on `retail` domain dev slice.
- **Timestamp**: 2026-04-23 15:37:02

## Next measurement steps
1. Deploy real integration layer (Resend, HubSpot, Cal.com)
2. Run comparative benchmark with adaptive context injection (Conversion Engine logic)
3. Target: Improved pass@1 > 0.40 using task-specific memory retrieval.

