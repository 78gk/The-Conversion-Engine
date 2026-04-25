"""
briefs/competitor/
──────────────────
Competitor gap brief generator (rubric Criterion 5).

The brief takes a prospect, finds 5..10 sector competitors via the same
selection criteria, scores each competitor with the AI maturity scoring
function used on the prospect (rubric E3), computes the prospect's
distribution position, and extracts 2..3 specific gap practices with
named-entity public-signal evidence (rubric E5).

Public exports:
  select_competitors                — 5..10 competitor selection with documented criteria
  compute_distribution_position     — prospect's percentile position vs competitors
  generate_competitor_gap_brief     — full schema-conformant brief
"""

from briefs.competitor.distribution import compute_distribution_position
from briefs.competitor.generator import generate_competitor_gap_brief
from briefs.competitor.selection import select_competitors

__all__ = [
    "select_competitors",
    "compute_distribution_position",
    "generate_competitor_gap_brief",
]
