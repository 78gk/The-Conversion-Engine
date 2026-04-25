"""
briefs/competitor/distribution.py
─────────────────────────────────
Compute the prospect's position in the sector AI-maturity distribution
(rubric E4).
"""

from __future__ import annotations

from statistics import median
from typing import Any


def compute_distribution_position(
    prospect_score: int,
    competitor_scores: list[int],
) -> dict[str, Any]:
    """
    Where does the prospect sit relative to the competitor distribution?

    Returns:
      {
        "rank":                     int  (1 = highest score),
        "above":                    int  (count of competitors strictly higher than prospect),
        "below":                    int  (count of competitors strictly lower than prospect),
        "ties":                     int,
        "percentile":               int  (rough rank-based percentile, 0..100),
        "median_competitor_score":  float,
        "max_competitor_score":     int,
        "min_competitor_score":     int,
      }
    """
    if not competitor_scores:
        return {
            "rank": 1,
            "above": 0,
            "below": 0,
            "ties": 0,
            "percentile": 100,
            "median_competitor_score": 0.0,
            "max_competitor_score": 0,
            "min_competitor_score": 0,
            "note": "no competitor scores supplied",
        }

    above = sum(1 for s in competitor_scores if s > prospect_score)
    below = sum(1 for s in competitor_scores if s < prospect_score)
    ties = sum(1 for s in competitor_scores if s == prospect_score)
    rank = above + 1
    n = len(competitor_scores) + 1  # include the prospect in the rank denominator
    percentile = int(round(100 * (n - rank) / n))

    return {
        "rank": rank,
        "above": above,
        "below": below,
        "ties": ties,
        "percentile": percentile,
        "median_competitor_score": float(median(competitor_scores)),
        "max_competitor_score": max(competitor_scores),
        "min_competitor_score": min(competitor_scores),
    }
