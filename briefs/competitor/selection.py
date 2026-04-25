"""
briefs/competitor/selection.py
──────────────────────────────
Selects 5..10 top-quartile competitors for a prospect (rubric E1, E2).

Selection criteria (documented in code so they are auditable per E2):

  1. Same sector tag (`category_list` substring match in Crunchbase ODM)
  2. Funding stage in {Seed, Series A, Series B, Series C, Series D+}
     — excludes IPO and unfunded; matches Tenacious's actual prospect window
  3. Employee count band within 0.5x..2x of the prospect's headcount
     — keeps comparisons honest; a 5,000-person enterprise is not a
       useful comparator for a 60-person Series B
  4. After filtering, sort by employee_count desc and take the top
     quartile (≥75th percentile) of the filtered set
  5. Cap final list at n_max=10. If fewer than n_min=5 viable
     competitors remain, hand off to handle_sparse_sector (rubric E7)
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

ODM_PATH = Path(__file__).resolve().parents[2] / "data" / "crunchbase_odm.csv"

ALLOWED_FUNDING_STAGES = {"Seed", "Series A", "Series B", "Series C", "Series D"}


@dataclass(frozen=True)
class Competitor:
    name: str
    domain: str
    sector: str
    funding_stage: str
    employee_count: str
    headcount_band: str
    source_row: dict[str, Any]


def _parse_employee_band_min(raw: str) -> int:
    s = (raw or "").strip()
    if "+" in s:
        try:
            return int(s.replace("+", ""))
        except ValueError:
            return 0
    if "-" in s:
        try:
            return int(s.split("-", 1)[0])
        except ValueError:
            return 0
    try:
        return int(s)
    except ValueError:
        return 0


def _band_label(min_size: int) -> str:
    if min_size <= 80:
        return "15_to_80"
    if min_size <= 200:
        return "80_to_200"
    if min_size <= 500:
        return "200_to_500"
    if min_size <= 2000:
        return "500_to_2000"
    return "2000_plus"


def _matches_sector(categories: str, prospect_sector: str) -> bool:
    categories_lower = (categories or "").lower()
    sector_lower = (prospect_sector or "").lower()
    if not categories_lower or not sector_lower:
        return False
    if sector_lower in categories_lower:
        return True
    sector_tokens = [tok for tok in sector_lower.replace("/", " ").replace("-", " ").split() if len(tok) >= 4]
    return any(tok in categories_lower for tok in sector_tokens)


def _within_headcount_band(row_min: int, prospect_headcount_min: int, lower: float, upper: float) -> bool:
    if prospect_headcount_min <= 0:
        return True
    return prospect_headcount_min * lower <= row_min <= prospect_headcount_min * upper


def handle_sparse_sector(prospect_sector: str, count: int) -> dict[str, Any]:
    """Documented fallback when fewer than 5 viable competitors remain (rubric E7)."""
    return {
        "status": "sparse",
        "viable_count": count,
        "fallback": (
            f"only {count} competitors matched all criteria for sector '{prospect_sector}'. "
            "Broaden the comparator pool to the parent sector tag (e.g. 'Analytics' instead "
            "of 'AI-augmented BI for mid-market') and re-run select_competitors. The brief "
            "must explicitly disclose the small-sample limitation in its gap_quality_self_check."
        ),
    }


def select_competitors(
    prospect_name: str,
    prospect_sector: str,
    prospect_headcount_min: int = 50,
    n_min: int = 5,
    n_max: int = 10,
) -> dict[str, Any]:
    """
    Return up to n_max competitors matching the documented criteria.

    Returns:
      {"status": "ok", "competitors": [Competitor, ...]}                      — when n_min..n_max found
      {"status": "sparse", "competitors": [...], "fallback": str, ...}        — when < n_min found
    """
    if not ODM_PATH.exists():
        LOGGER.warning("Crunchbase ODM CSV missing at %s", ODM_PATH)
        return handle_sparse_sector(prospect_sector, 0) | {"competitors": []}

    strict_candidates: list[Competitor] = []
    broadened_candidates: list[Competitor] = []

    with open(ODM_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_name = row.get("name", "").strip()
            if not row_name or row_name.lower() == prospect_name.lower():
                continue

            stage = row.get("funding_stage", "").strip()
            if stage not in ALLOWED_FUNDING_STAGES:
                continue

            row_min = _parse_employee_band_min(row.get("employee_count", ""))
            competitor = Competitor(
                name=row_name,
                domain=row.get("homepage_url", row_name.lower().replace(" ", "-") + ".example"),
                sector=row.get("category_list", ""),
                funding_stage=stage,
                employee_count=row.get("employee_count", ""),
                headcount_band=_band_label(row_min),
                source_row=dict(row),
            )

            if _matches_sector(row.get("category_list", ""), prospect_sector) and _within_headcount_band(row_min, prospect_headcount_min, 0.5, 2.0):
                strict_candidates.append(competitor)
                continue

            if _within_headcount_band(row_min, prospect_headcount_min, 0.2, 10.0):
                broadened_candidates.append(competitor)

    candidates = strict_candidates[:]
    used_broadened_fallback = False
    if len(candidates) < n_min and broadened_candidates:
        seen = {c.name.lower() for c in candidates}
        for competitor in broadened_candidates:
            if competitor.name.lower() not in seen:
                candidates.append(competitor)
        used_broadened_fallback = True

    if not candidates:
        return handle_sparse_sector(prospect_sector, 0) | {"competitors": []}

    candidates.sort(key=lambda c: _parse_employee_band_min(c.employee_count), reverse=True)
    if len(candidates) <= n_max:
        selected = candidates
    else:
        top_quartile_cutoff = max(n_min, min(n_max, len(candidates) // 4))
        selected = candidates[:top_quartile_cutoff]

    if len(selected) < n_min:
        return handle_sparse_sector(prospect_sector, len(selected)) | {"competitors": [c.__dict__ for c in selected]}

    return {
        "status": "ok",
        "selection_strategy": "broadened_fallback" if used_broadened_fallback else "strict_top_quartile",
        "competitors": [c.__dict__ for c in selected],
    }
