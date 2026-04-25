"""
signals/job_posts/wellfound_scraper.py
──────────────────────────────────────
Wellfound (formerly AngelList Talent) public company-jobs page scraper.

Public URL pattern: https://wellfound.com/company/{slug}/jobs
No login required for the public-jobs view. robots.txt compliance via
signals.job_posts.compliance.is_scrape_allowed.
"""

from __future__ import annotations

import logging
import urllib.parse

from agent.enrichment import AI_KEYWORDS, SignalResult
from signals.job_posts.compliance import USER_AGENT, is_scrape_allowed

LOGGER = logging.getLogger(__name__)


async def scrape_wellfound(company_slug: str, max_pages: int = 1) -> SignalResult:
    """Scrape Wellfound public job listings for a company."""
    url = f"https://wellfound.com/company/{urllib.parse.quote(company_slug)}/jobs"

    if not is_scrape_allowed(url):
        return SignalResult(
            signal="wellfound_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0, "skipped": "robots_txt_disallow"},
            confidence=0.0,
            source="wellfound_public",
        )

    try:
        from playwright.async_api import async_playwright  # type: ignore[import]
    except ImportError:
        return SignalResult(
            signal="wellfound_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0},
            confidence=0.0,
            source="wellfound_public",
        )

    titles: list[str] = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            ctx = await browser.new_context(user_agent=USER_AGENT)
            page = await ctx.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            for _ in range(max_pages):
                page_titles = await page.eval_on_selector_all(
                    "[data-test='JobSearchResultItem'] h2, h3.job-title",
                    "els => els.map(e => e.innerText.trim()).filter(Boolean)",
                )
                titles.extend(page_titles)
                break  # Wellfound uses infinite scroll; one page sample is sufficient for ratio
            await browser.close()
    except Exception as exc:
        LOGGER.warning("Wellfound scrape failed for %s: %s", company_slug, exc)
        return SignalResult(
            signal="wellfound_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0, "error": str(exc)},
            confidence=0.2,
            source="wellfound_public",
        )

    open_roles = len(titles)
    ai_adj = sum(1 for t in titles if any(k in t.lower() for k in AI_KEYWORDS))
    ratio = round(ai_adj / open_roles, 3) if open_roles else 0.0
    return SignalResult(
        signal="wellfound_jobs",
        value={
            "open_roles": open_roles,
            "ai_adjacent_roles": ai_adj,
            "ai_role_ratio": ratio,
            "sample_titles": titles[:5],
        },
        confidence=min(0.85, 0.25 + open_roles / 30),
        source="wellfound_public",
    )
