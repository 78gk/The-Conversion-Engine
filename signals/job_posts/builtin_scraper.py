"""
signals/job_posts/builtin_scraper.py
────────────────────────────────────
BuiltIn (builtin.com) public company-jobs page scraper.

Public URL pattern: https://builtin.com/company/{slug}/jobs
No login required. We respect robots.txt via signals.job_posts.compliance.

Returns a SignalResult with the same shape as agent.enrichment.scrape_job_posts.
"""

from __future__ import annotations

import logging
import urllib.parse

from agent.enrichment import AI_KEYWORDS, SignalResult
from signals.job_posts.compliance import USER_AGENT, is_scrape_allowed

LOGGER = logging.getLogger(__name__)


async def scrape_builtin(company_slug: str, max_pages: int = 2) -> SignalResult:
    """
    Scrape BuiltIn public job listings for a company.

    company_slug: the kebab-case slug used in the BuiltIn URL
                  (e.g. "tenacious" for builtin.com/company/tenacious/jobs)
    """
    url = f"https://builtin.com/company/{urllib.parse.quote(company_slug)}/jobs"

    if not is_scrape_allowed(url):
        return SignalResult(
            signal="builtin_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0, "skipped": "robots_txt_disallow"},
            confidence=0.0,
            source="builtin_public",
        )

    try:
        from playwright.async_api import async_playwright  # type: ignore[import]
    except ImportError:
        LOGGER.warning("playwright not installed -- returning stub builtin signal")
        return SignalResult(
            signal="builtin_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0},
            confidence=0.0,
            source="builtin_public",
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
                    "h2.job-card__title, [data-testid='job-title']",
                    "els => els.map(e => e.innerText.trim()).filter(Boolean)",
                )
                titles.extend(page_titles)
                next_btn = await page.query_selector('a[rel="next"]')
                if next_btn is None:
                    break
                await next_btn.click()
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            await browser.close()
    except Exception as exc:
        LOGGER.warning("BuiltIn scrape failed for %s: %s", company_slug, exc)
        return SignalResult(
            signal="builtin_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0, "error": str(exc)},
            confidence=0.2,
            source="builtin_public",
        )

    open_roles = len(titles)
    ai_adj = sum(1 for t in titles if any(k in t.lower() for k in AI_KEYWORDS))
    ratio = round(ai_adj / open_roles, 3) if open_roles else 0.0
    return SignalResult(
        signal="builtin_jobs",
        value={
            "open_roles": open_roles,
            "ai_adjacent_roles": ai_adj,
            "ai_role_ratio": ratio,
            "sample_titles": titles[:5],
        },
        confidence=min(0.9, 0.3 + open_roles / 30),
        source="builtin_public",
    )
