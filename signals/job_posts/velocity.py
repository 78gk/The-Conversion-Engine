"""
signals/job_posts/velocity.py
─────────────────────────────
60-day hiring-velocity delta (rubric C9).

Velocity is computed as the change in the company's open-role count over
a 60-day window — not the absolute count of currently-open roles.

Snapshots are persisted as JSONL to data/job_post_snapshots.jsonl. Each
line is one snapshot:
    {"company": str, "open_roles": int, "captured_at": ISO8601 UTC}

The first time a company is scraped, only "today" is recorded and the
velocity_label is "insufficient_signal" (the schema's allowed value when
no 60-day-prior snapshot exists). On subsequent calls, the most recent
snapshot at least 50 days old is used as the baseline.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

SNAPSHOT_PATH = Path(__file__).resolve().parents[2] / "data" / "job_post_snapshots.jsonl"


def _read_snapshots(company: str) -> list[dict[str, Any]]:
    if not SNAPSHOT_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    with open(SNAPSHOT_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("company", "").lower() == company.lower():
                rows.append(row)
    return rows


def _append_snapshot(company: str, open_roles: int) -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "company": company,
        "open_roles": int(open_roles),
        "captured_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(SNAPSHOT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _label_for_delta(today: int, prior: int) -> str:
    """Map the today-vs-prior counts to the schema's velocity_label enum."""
    if prior <= 0:
        return "insufficient_signal" if today == 0 else "increased_modestly"
    ratio = today / prior
    if ratio >= 3.0:
        return "tripled_or_more"
    if ratio >= 2.0:
        return "doubled"
    if ratio > 1.1:
        return "increased_modestly"
    if ratio < 0.9:
        return "declined"
    return "flat"


def compute_velocity_60d(company: str, today_count: int) -> dict[str, Any]:
    """
    Return a hiring_velocity dict matching the
    schemas/hiring_signal_brief.schema.json -> hiring_velocity block.

    Computes the delta over a 60-day window:
      open_roles_today      — the count just scraped (passed in)
      open_roles_60_days_ago — most recent snapshot at least 50 days old
      velocity_label         — categorical label from _label_for_delta
      signal_confidence      — 0.0 when no prior snapshot, otherwise tier-mapped

    Side effect: persists today's snapshot to data/job_post_snapshots.jsonl.
    """
    snapshots = _read_snapshots(company)
    cutoff_low = datetime.utcnow() - timedelta(days=70)
    cutoff_high = datetime.utcnow() - timedelta(days=50)

    prior_snapshot = None
    for snap in sorted(snapshots, key=lambda r: r.get("captured_at", "")):
        try:
            captured_at = datetime.fromisoformat(snap["captured_at"].rstrip("Z"))
        except (ValueError, KeyError):
            continue
        if cutoff_low <= captured_at <= cutoff_high:
            prior_snapshot = snap
            # do not break — prefer the most recent within the window

    _append_snapshot(company, today_count)

    if prior_snapshot is None:
        LOGGER.info("No 60-day-prior snapshot for %s; first capture stored", company)
        return {
            "open_roles_today": int(today_count),
            "open_roles_60_days_ago": 0,
            "velocity_label": "insufficient_signal",
            "signal_confidence": 0.0,
            "sources": [],
            "note": "first capture; 60-day baseline not yet available",
        }

    prior_count = int(prior_snapshot["open_roles"])
    label = _label_for_delta(today_count, prior_count)
    return {
        "open_roles_today": int(today_count),
        "open_roles_60_days_ago": prior_count,
        "velocity_label": label,
        "signal_confidence": 0.7 if prior_count >= 5 else 0.4,
        "sources": ["builtin", "wellfound", "linkedin_public", "company_careers_page"],
        "captured_at_prior": prior_snapshot.get("captured_at"),
    }
