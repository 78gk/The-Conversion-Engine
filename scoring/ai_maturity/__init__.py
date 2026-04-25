"""
scoring/ai_maturity/
────────────────────
AI maturity scoring subsystem (rubric Criterion 4).

The score is an integer in {0, 1, 2, 3} per the canonical
schemas/hiring_signal_brief.schema.json definition:
  0 = no signal
  1 = thin signal: stack present but no AI roles or leadership
  2 = active build: AI-adjacent roles open, no named AI leadership
  3 = mature function: named AI/ML leadership + open roles + public commentary

Six input categories with tiered weights:
  HIGH  (weight 3): ai_adjacent_open_roles, named_ai_ml_leadership
  MEDIUM (weight 2): github_org_activity, executive_commentary
  LOW   (weight 1): modern_data_ml_stack, strategic_communications

Public exports:
  score_ai_maturity   — the scoring function (returns integer 0..3 + rationale)
  collect_signals     — a one-call collector that runs all six collectors
"""

from scoring.ai_maturity.scorer import score_ai_maturity
from scoring.ai_maturity.signal_collectors import collect_signals

__all__ = ["score_ai_maturity", "collect_signals"]
