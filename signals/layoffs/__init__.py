"""
signals/layoffs/
────────────────
layoffs.fyi CSV parser. Re-exports the working module in
agent.enrichment which downloads and parses the public CSV at
https://layoffs.fyi/layoffs_data.csv with a 365-day lookback window
(rubric default).

Edge cases handled at agent.enrichment.parse_layoffs_fyi:
  - CSV missing -> downloads on first call
  - Download failure -> returns confidence=0.0, empty events
  - No matches -> confidence=0.5 with empty event list (low-confidence absence)
"""

from agent.enrichment import parse_layoffs_fyi

__all__ = ["parse_layoffs_fyi"]
