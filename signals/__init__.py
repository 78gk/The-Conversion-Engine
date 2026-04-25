"""
signals/
────────
Per-source signal collection packages.

Each subpackage corresponds to one of the four hiring signals plus the
compliance and velocity helpers shared across job-post sources.

Packages:
  crunchbase/   — Crunchbase ODM lookup with funding-round filter
  job_posts/    — BuiltIn + Wellfound + LinkedIn public scrapers, robots.txt compliance, 60-day delta
  layoffs/      — layoffs.fyi CSV parser
  leadership/   — public-source leadership-change detection
"""
