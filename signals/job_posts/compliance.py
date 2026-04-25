"""
signals/job_posts/compliance.py
───────────────────────────────
Scraping compliance: robots.txt fetch and rule checking.

This module is the rubric C3 sub-check: every scraper in this package
calls is_scrape_allowed before requesting any URL. Public-page-only —
no authenticated pages, no session cookies, no captcha bypasses.

If a target site disallows our user-agent on the path we want to fetch,
we return False and the caller MUST skip that source. We do not fall
through to a different fetch strategy.
"""

from __future__ import annotations

import logging
import urllib.parse
import urllib.robotparser

LOGGER = logging.getLogger(__name__)

USER_AGENT = "TenaciousConversionEngineBot/1.0 (+https://gettenacious.com/bots)"

# Cache parsed robots.txt per host so we don't re-fetch on every URL.
_ROBOT_CACHE: dict[str, urllib.robotparser.RobotFileParser] = {}


def is_scrape_allowed(url: str, user_agent: str = USER_AGENT) -> bool:
    """
    Return True only if robots.txt for the URL's host permits our agent
    to fetch the path. Network errors during robots.txt fetch are
    interpreted as DISALLOW (safe default).

    Public-page-only constraint: callers must additionally confirm the URL
    is reachable without authentication. This function only enforces
    robots.txt — it cannot detect login walls.
    """
    parsed = urllib.parse.urlparse(url)
    host = f"{parsed.scheme}://{parsed.netloc}"

    if host not in _ROBOT_CACHE:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{host}/robots.txt")
        try:
            rp.read()
        except Exception as exc:
            LOGGER.warning("robots.txt fetch failed for %s: %s -- defaulting to DISALLOW", host, exc)
            return False
        _ROBOT_CACHE[host] = rp

    rp = _ROBOT_CACHE[host]
    allowed = rp.can_fetch(user_agent, url)
    if not allowed:
        LOGGER.info("robots.txt DISALLOWS %s for %s", user_agent, url)
    return allowed
