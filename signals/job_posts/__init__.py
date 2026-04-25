"""
signals/job_posts/
──────────────────
Public job-post scraping across BuiltIn, Wellfound, and LinkedIn public
listing pages, plus robots.txt compliance and 60-day velocity delta
(rubric sub-checks C2, C3, C9).

All scrapers are public-page-only. Authenticated pages, login flows,
and captcha bypasses are explicitly out of scope — see compliance.py.

Modules:
  builtin_scraper    — BuiltIn public company-jobs page
  wellfound_scraper  — Wellfound (formerly AngelList Talent) public page
  linkedin_public    — LinkedIn public company-jobs page (no login)
  velocity           — 60-day delta from snapshot store
  compliance         — robots.txt fetch + check before any scrape
"""

from __future__ import annotations

from agent.enrichment import scrape_job_posts as scrape_indeed

from signals.job_posts.builtin_scraper import scrape_builtin
from signals.job_posts.compliance import is_scrape_allowed
from signals.job_posts.linkedin_public import scrape_linkedin_public
from signals.job_posts.velocity import compute_velocity_60d
from signals.job_posts.wellfound_scraper import scrape_wellfound

__all__ = [
    "scrape_indeed",
    "scrape_builtin",
    "scrape_wellfound",
    "scrape_linkedin_public",
    "is_scrape_allowed",
    "compute_velocity_60d",
]
