"""
signals/leadership/
───────────────────
Leadership-change detection from public sources.

Re-exports the working detector in agent.enrichment which combines:
  - Crunchbase ODM growth-stage flags (Series A/B/Seed)
  - DuckDuckGo Instant Answer API news scan for executive title
    + change-keyword pairings (no auth, no scraping behind login)

Edge cases:
  - No match -> confidence=0.25, change_count=0
  - News API failure -> falls back to ODM-only flag
"""

from agent.enrichment import detect_leadership_changes

__all__ = ["detect_leadership_changes"]
