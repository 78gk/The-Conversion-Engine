# The Conversion Engine
**Automated Lead Generation and Conversion System for Tenacious Consulting and Outsourcing**

The Conversion Engine is a high-density agentic system designed to identify synthetic prospects from public data, qualify them against grounded intent signals, and automate the nurture-to-booking pipeline.

## 🏗️ Architecture

The system operates on an orchestrated multi-phase loop, moving from raw signal enrichment to qualified CRM injection.

```text
┌─────────────────────────────────────────────────────────────────┐
│                    CONVERSION ENGINE                             │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌───────────────────────────┐  │
│  │ Planner  │───▶│ Builder  │───▶│    Signal Enrichment       │  │
│  │          │    │          │    │  Crunchbase + Jobs +        │  │
│  │ tasks.   │    │ prompts/ │    │  layoffs.fyi + AI Maturity  │  │
│  │ json     │    │ task_*.  │    └───────────┬───────────────┘  │
│  └──────────┘    └──────────┘                │                  │
│                                    ┌─────────▼─────────┐        │
│  ┌──────────┐    ┌──────────┐      │  ICP Classifier    │        │
│  │ Reporter │◀───│ Improver │◀─────│  Segment 1/2/3/4   │        │
│  │          │    │          │      │  + Confidence Score│        │
│  │ reports/ │    │ improve. │      └─────────┬──────────┘        │
│  └──────────┘    └──────────┘                │                  │
│                                    ┌─────────▼─────────┐        │
│  ┌──────────┐    ┌──────────┐      │  Outreach Agent    │        │
│  │Evaluator │───▶│Debugger  │      │  Email (Resend)     │        │
│  │          │    │          │      │  SMS (Africa's Tlk) │        │
│  │ eval/    │    │ fix.txt  │      └─────────┬──────────┘        │
│  └──────────┘    └──────────┘                │                  │
│                                    ┌─────────▼─────────┐        │
│                                    │  Cal.com + HubSpot │        │
│                                    │  Booking + CRM Wr. │        │
│                                    └───────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## 📂 Project Layout

- `core/`: Phase orchestration and state management (`controller.py`).
- `agent/`: Source for all agent implementations, integrations (Email/SMS/HubSpot), and the evaluation script.
- `prompts/`: Versioned task-specific prompts for the agentic loop.
- `eval/`: Baseline measurements, trace logs (`trace_log.jsonl`), and score logs.
- `memory/`: System state, task manifest, and observed metrics.
- `scripts/`: Entry points for simulation and reproduction.
- `tau2-bench/`: Integrated benchmark harness for retail domain evaluation.

## 🚀 Setup Instructions

### Prerequisites
- Python 3.12+
- `pip` or `uv`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/78gk/The-Conversion-Engine.git
   cd The-Conversion-Engine
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r agent/requirements.txt
   ```

### Configuration
Copy `config.yaml` and configure your LLM provider and integration status:
```yaml
llm_provider: openrouter
outbound_live: false  # Keep false to route to staff sink
```

## 📊 Performance Baseline (Day 3 Interim)

| Metric | Measured Value |
|---|---|
| **tau2-bench retail pass@1** | 0.4 |
| **95% Confidence Interval** | [0.185, 0.615] |
| **p50 Latency** | 4,287 ms |
| **p95 Latency** | 7,507 ms |
| **Structural Integrity** | 19/19 checks passed (1.0 pass@1) |

Detailed measurement traces are available in [`eval/trace_log.jsonl`](eval/trace_log.jsonl).

## 📄 Documentation

- [Interim Report](artifacts/reports/INTERIM_DAY3_REPORT.md)
- [Baseline Details](baseline.md)
- [Requirements Summary](artifacts/reports/requirements_summary.md)
