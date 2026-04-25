"""
signals/job_posts/linkedin_public.py
────────────────────────────────────
LinkedIn public company-jobs page scraper.

Public URL pattern: https://www.linkedin.com/jobs/{company-slug}-jobs
This URL is reachable WITHOUT a LinkedIn account; it serves the public
search view that anyone can browse. We do not log in, do not call the
LinkedIn private API, do not bypass the auth wall.

robots.txt compliance via signals.job_posts.compliance.is_scrape_allowed.
"""

from __future__ import annotations

import logging
import urllib.parse

from agent.enrichment import AI_KEYWORDS, SignalResult
from signals.job_posts.compliance import USER_AGENT, is_scrape_allowed

LOGGER = logging.getLogger(__name__)


async def scrape_linkedin_public(company_slug: str, max_pages: int = 1) -> SignalResult:
    """
    Scrape LinkedIn public jobs page for a company. Public pages only.

    This function does NOT and MUST NOT attempt LinkedIn auth or call any
    LinkedIn API endpoint requiring credentials.
    """
    url = f"https://www.linkedin.com/jobs/{urllib.parse.quote(company_slug)}-jobs"

    if not is_scrape_allowed(url):
        return SignalResult(
            signal="linkedin_public_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0, "skipped": "robots_txt_disallow"},
            confidence=0.0,
            source="linkedin_public",
        )

    try:
        from playwright.async_api import async_playwright  # type: ignore[import]
    except ImportError:
        return SignalResult(
            signal="linkedin_public_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0},
            confidence=0.0,
            source="linkedin_public",
        )

    titles: list[str] = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            ctx = await browser.new_context(user_agent=USER_AGENT)
            page = await ctx.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)

            # If LinkedIn redirects to a login wall, abort.
            if "/login" in page.url or "/authwall" in page.url:
                LOGGER.info("LinkedIn served auth wall for %s; abandoning scrape (public-only constraint)", url)
                await browser.close()
                return SignalResult(
                    signal="linkedin_public_jobs",
                    value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0, "skipped": "auth_wall"},
                    confidence=0.0,
                    source="linkedin_public",
                )

            page_titles = await page.eval_on_selector_all(
                "h3.base-search-card__title, .job-search-card__title",
                "els => els.map(e => e.innerText.trim()).filter(Boolean)",
            )
            titles.extend(page_titles)
            await browser.close()
    except Exception as exc:
        LOGGER.warning("LinkedIn public scrape failed for %s: %s", company_slug, exc)
        return SignalResult(
            signal="linkedin_public_jobs",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0, "error": str(exc)},
            confidence=0.2,
            source="linkedin_public",
        )

    open_roles = len(titles)
    ai_adj = sum(1 for t in titles if any(k in t.lower() for k in AI_KEYWORDS))
    ratio = round(ai_adj / open_roles, 3) if open_roles else 0.0
    return SignalResult(
        signal="linkedin_public_jobs",
        value={
            "open_roles": open_roles,
            "ai_adjacent_roles": ai_adj,
            "ai_role_ratio": ratio,
            "sample_titles": titles[:5],
        },
        confidence=min(0.85, 0.25 + open_roles / 30),
        source="linkedin_public",
    )
