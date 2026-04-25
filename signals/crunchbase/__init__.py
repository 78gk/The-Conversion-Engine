"""
signals/crunchbase/
───────────────────
Crunchbase ODM lookup with funding-round filter applied (rubric C1).

The Crunchbase Open Data Map (Apache 2.0, https://data.crunchbase.com)
ships a CSV containing company name, funding stage, category, employee
count, city, country. We never call the paid Crunchbase API.

Functions:
  lookup_crunchbase_odm     — re-export of the working ODM lookup
  filter_by_funding_round   — explicit funding-round filter (rubric C1 sub-check)
"""

from __future__ import annotations

from typing import Iterable

from agent.enrichment import SignalResult, lookup_crunchbase_odm

__all__ = [
    "lookup_crunchbase_odm",
    "filter_by_funding_round",
]


def filter_by_funding_round(
    rows: Iterable[dict],
    allowed_stages: tuple[str, ...] = ("Seed", "Series A", "Series B", "Series C"),
) -> list[dict]:
    """
    Apply the funding-round filter to a list of Crunchbase ODM rows.

    Default kept narrow to the segments Tenacious actively pitches into
    (Seed -> Series C). Extending requires changing the tuple — explicit
    by design so the filter is auditable.
    """
    return [r for r in rows if r.get("funding_stage", "") in allowed_stages]
