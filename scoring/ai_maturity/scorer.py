"""
scoring/ai_maturity/scorer.py
─────────────────────────────
The AI maturity scoring function.

Returns an integer score in {0, 1, 2, 3}, separate confidence float,
per-signal justifications, and explicit silent-company handling.
Persists rationale to eval/scoring_rationales/{prospect}.json so the
score is auditable alongside the brief (rubric D9).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

# Tiered signal weights — see scoring/ai_maturity/__init__.py for the rubric mapping
SIGNAL_WEIGHTS: dict[str, int] = {
    "ai_adjacent_open_roles":   3,   # HIGH
    "named_ai_ml_leadership":   3,   # HIGH
    "github_org_activity":      2,   # MEDIUM
    "executive_commentary":     2,   # MEDIUM
    "modern_data_ml_stack":     1,   # LOW
    "strategic_communications": 1,   # LOW
}

# Score buckets — total weighted points -> 0..3 integer score
# Max possible = 3+3+2+2+1+1 = 12. Tier cutoffs chosen so that:
#   3 (mature)    requires at least one HIGH + medium signal stack
#   2 (active)    requires either HIGH + LOW or 2 MEDIUM
#   1 (thin)      requires at least one LOW signal
#   0 (silent)    no signals present
SCORE_BUCKETS = [
    (8, 3),   # >=8 weighted -> mature
    (5, 2),   # 5..7 -> active
    (2, 1),   # 2..4 -> thin
    (0, 0),   # 0..1 -> silent / no signal
]

RATIONALE_DIR = Path(__file__).resolve().parents[2] / "eval" / "scoring_rationales"


def _bucket(weighted_total: int) -> int:
    for threshold, bucket in SCORE_BUCKETS:
        if weighted_total >= threshold:
            return bucket
    return 0


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "unknown"


def score_ai_maturity(
    signals: dict[str, dict[str, Any]],
    prospect: str = "unknown",
    persist: bool = True,
) -> dict[str, Any]:
    """
    Score AI maturity from a bundle of six signal collector outputs.

    signals: a dict keyed by the names in SIGNAL_WEIGHTS. Each value is a
             dict from the corresponding collector with shape
                {"present": bool, "evidence": str, "confidence": float, "source_url": str | None}

    Returns:
      {
        "score":            int in {0,1,2,3},
        "confidence":       float in [0.0, 1.0]   (separate from score, rubric D7),
        "weighted_total":   int,
        "justifications":   {signal_name: rationale_text, ...},
        "silent_company":   bool                  (rubric D8),
        "note":             str | None,           (only when silent_company True)
        "computed_at":      ISO8601 UTC,
      }

    Side effect (when persist=True): writes the result to
      eval/scoring_rationales/{prospect-slug}.json (rubric D9 — rationale persisted).
    """
    weighted_total = 0
    justifications: dict[str, str] = {}
    confidences: list[float] = []
    presence_count = 0

    for name, weight in SIGNAL_WEIGHTS.items():
        sig = signals.get(name) or {"present": False, "evidence": "no signal collected", "confidence": 0.0}
        present = bool(sig.get("present"))
        evidence = str(sig.get("evidence", ""))
        sig_conf = float(sig.get("confidence", 0.0))
        confidences.append(sig_conf)

        if present:
            weighted_total += weight
            presence_count += 1
            justifications[name] = f"present (weight={weight}): {evidence}"
        else:
            justifications[name] = f"absent (weight={weight}): {evidence or 'no signal'}"

    # Silent-company branch (rubric D8) — explicit handling of zero-signal companies
    if presence_count == 0:
        result = {
            "score": 0,
            "confidence": 0.0,
            "weighted_total": 0,
            "justifications": justifications,
            "silent_company": True,
            "note": (
                "Absence of public signal is not proof of absence. Quietly sophisticated "
                "companies often score zero here (proprietary stacks, no public GitHub, "
                "minimal exec commentary). Treat the score as low confidence and prefer "
                "abstention over a Segment 1 introductory pitch."
            ),
            "computed_at": datetime.utcnow().isoformat() + "Z",
        }
    else:
        score = _bucket(weighted_total)
        # Confidence is the average of present-signal confidences, weighted by tier
        present_confs = [
            float(signals[n].get("confidence", 0.0)) * SIGNAL_WEIGHTS[n]
            for n in SIGNAL_WEIGHTS
            if signals.get(n, {}).get("present")
        ]
        avg_conf = round(sum(present_confs) / sum(SIGNAL_WEIGHTS[n] for n in SIGNAL_WEIGHTS if signals.get(n, {}).get("present")), 3) if present_confs else 0.0
        result = {
            "score": score,
            "confidence": avg_conf,
            "weighted_total": weighted_total,
            "justifications": justifications,
            "silent_company": False,
            "note": None,
            "computed_at": datetime.utcnow().isoformat() + "Z",
        }

    # Persist rationale alongside the brief (rubric D9)
    if persist:
        try:
            RATIONALE_DIR.mkdir(parents=True, exist_ok=True)
            out_path = RATIONALE_DIR / f"{_slugify(prospect)}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"prospect": prospect, **result}, f, indent=2)
            LOGGER.info("Persisted AI maturity rationale: %s", out_path)
        except OSError as exc:
            LOGGER.warning("Could not persist rationale for %s: %s", prospect, exc)

    return result
