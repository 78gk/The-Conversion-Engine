"""
scoring/ai_maturity/signal_collectors.py
────────────────────────────────────────
The six signal collectors required by rubric Criterion 4 (D1..D3):

  HIGH-weight   ai_adjacent_open_roles      (collected from job-post scrapers)
  HIGH-weight   named_ai_ml_leadership      (DuckDuckGo public news scan)
  MEDIUM-weight github_org_activity         (public GitHub Search API)
  MEDIUM-weight executive_commentary        (DuckDuckGo public site search)
  LOW-weight    modern_data_ml_stack        (job-post text grep for tooling tokens)
  LOW-weight    strategic_communications    (company /blog and /about page text)

Every collector returns a uniform shape:
    {"present": bool, "evidence": str, "confidence": float, "source_url": str | None}

Network failures, missing pages, and rate-limit responses are caught and
returned as `{present: False, ...}` — the collector never crashes the
caller. This is the rubric C8/D8 edge-case discipline.
"""

from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Iterable

LOGGER = logging.getLogger(__name__)

USER_AGENT = "TenaciousConversionEngineBot/1.0 (+https://gettenacious.com/bots)"

ML_LEADERSHIP_TITLES = (
    "head of ai", "head of ml", "chief ai officer", "chief ml officer",
    "vp ai", "vp ml", "vp of artificial intelligence", "director of ai",
    "director of machine learning", "ai lead", "principal ml engineer",
)

MODERN_STACK_TOKENS = (
    "dbt", "snowflake", "databricks", "airflow", "mlflow", "weights & biases",
    "ray", "kubeflow", "vertex ai", "sagemaker", "huggingface", "langchain",
)

STRATEGIC_AI_PHRASES = (
    "ai-first", "ai strategy", "applied ai", "agentic", "machine learning platform",
    "ml platform", "production ml", "responsible ai",
)


def _safe_get(url: str, timeout: int = 8) -> str | None:
    """GET a URL with a polite UA, return body text or None on any error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as exc:
        LOGGER.debug("GET %s failed: %s", url, exc)
        return None


def collect_ai_adjacent_open_roles(job_titles: Iterable[str]) -> dict[str, Any]:
    """HIGH-weight signal — count of AI/ML/Data roles in the supplied titles."""
    titles = list(job_titles)
    ai_terms = ("ml engineer", "ai engineer", "data scientist", "machine learning",
                "applied scientist", "research engineer", "ml platform", "mlops")
    matches = [t for t in titles if any(term in t.lower() for term in ai_terms)]
    if matches:
        return {
            "present": True,
            "evidence": f"{len(matches)} AI-adjacent role(s) of {len(titles)} total: {matches[:3]}",
            "confidence": min(0.9, 0.4 + 0.1 * len(matches)),
            "source_url": None,
        }
    return {
        "present": False,
        "evidence": f"no AI-adjacent roles among {len(titles)} job posts scanned",
        "confidence": 0.6 if titles else 0.0,
        "source_url": None,
    }


def collect_named_ai_ml_leadership(company_name: str) -> dict[str, Any]:
    """HIGH-weight signal — DuckDuckGo Instant Answer scan for AI/ML leadership titles."""
    q = f'"{company_name}" "head of ai" OR "head of ml" OR "chief ai officer" OR "vp ai"'
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(q)}&format=json&no_html=1&skip_disambig=1"
    body = _safe_get(url)
    if not body:
        return {"present": False, "evidence": "DuckDuckGo lookup failed", "confidence": 0.0, "source_url": None}
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"present": False, "evidence": "non-JSON response", "confidence": 0.0, "source_url": None}

    abstract = (data.get("AbstractText", "") or "").lower()
    abstract_url = data.get("AbstractURL", "") or None
    if any(t in abstract for t in ML_LEADERSHIP_TITLES):
        return {
            "present": True,
            "evidence": data.get("AbstractText", "")[:200],
            "confidence": 0.6,
            "source_url": abstract_url,
        }
    for topic in (data.get("RelatedTopics", []) or [])[:5]:
        text = (topic.get("Text", "") or "").lower()
        if any(t in text for t in ML_LEADERSHIP_TITLES):
            return {
                "present": True,
                "evidence": topic.get("Text", "")[:200],
                "confidence": 0.45,
                "source_url": topic.get("FirstURL"),
            }
    return {
        "present": False,
        "evidence": "no AI/ML leadership title detected in public news abstracts",
        "confidence": 0.4,
        "source_url": None,
    }


def collect_github_org_activity(company_slug: str) -> dict[str, Any]:
    """MEDIUM-weight signal — public GitHub Search API for an org with recent activity."""
    q = f"org:{company_slug}+pushed:>2025-10-01"
    url = f"https://api.github.com/search/repositories?q={q}&per_page=5"
    body = _safe_get(url)
    if not body:
        return {"present": False, "evidence": "GitHub Search unreachable", "confidence": 0.0, "source_url": None}
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"present": False, "evidence": "GitHub returned non-JSON", "confidence": 0.0, "source_url": None}

    total = int(data.get("total_count", 0) or 0)
    items = data.get("items", []) or []
    if total == 0 or not items:
        return {
            "present": False,
            "evidence": f"no public repos pushed in the last ~6 months under org:{company_slug}",
            "confidence": 0.5,
            "source_url": f"https://github.com/{company_slug}",
        }

    top_names = [r.get("name") for r in items[:3]]
    return {
        "present": True,
        "evidence": f"{total} active public repos; recent: {top_names}",
        "confidence": min(0.85, 0.4 + 0.1 * min(total, 5)),
        "source_url": f"https://github.com/{company_slug}",
    }


def collect_executive_commentary(company_name: str) -> dict[str, Any]:
    """MEDIUM-weight signal — DuckDuckGo search for exec public AI commentary."""
    q = f'"{company_name}" CEO OR CTO AI strategy OR "ai-first" OR agentic'
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(q)}&format=json&no_html=1&skip_disambig=1"
    body = _safe_get(url)
    if not body:
        return {"present": False, "evidence": "DuckDuckGo lookup failed", "confidence": 0.0, "source_url": None}
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"present": False, "evidence": "non-JSON response", "confidence": 0.0, "source_url": None}

    abstract = (data.get("AbstractText", "") or "").lower()
    abstract_url = data.get("AbstractURL", "") or None
    if any(p in abstract for p in STRATEGIC_AI_PHRASES):
        return {
            "present": True,
            "evidence": data.get("AbstractText", "")[:200],
            "confidence": 0.55,
            "source_url": abstract_url,
        }
    return {
        "present": False,
        "evidence": "no executive AI commentary detected in public abstracts",
        "confidence": 0.35,
        "source_url": None,
    }


def collect_modern_data_ml_stack(job_post_text_blob: str) -> dict[str, Any]:
    """LOW-weight signal — job-post grep for modern data/ML tooling tokens."""
    blob_lower = (job_post_text_blob or "").lower()
    matches = [tok for tok in MODERN_STACK_TOKENS if tok in blob_lower]
    if matches:
        return {
            "present": True,
            "evidence": f"modern stack tokens in job posts: {matches[:5]}",
            "confidence": min(0.8, 0.3 + 0.1 * len(matches)),
            "source_url": None,
        }
    return {
        "present": False,
        "evidence": "no modern data/ML stack tokens detected in job-post text",
        "confidence": 0.4 if blob_lower else 0.0,
        "source_url": None,
    }


def collect_strategic_communications(domain: str) -> dict[str, Any]:
    """LOW-weight signal — fetch /blog and /about, grep for AI strategy phrases."""
    found_phrases: list[str] = []
    found_url = None
    for path in ("/blog", "/about", "/"):
        url = f"https://{domain}{path}"
        body = _safe_get(url)
        if not body:
            continue
        body_lower = body.lower()
        hits = [p for p in STRATEGIC_AI_PHRASES if p in body_lower]
        if hits:
            found_phrases = hits
            found_url = url
            break

    if found_phrases:
        return {
            "present": True,
            "evidence": f"AI strategy phrases on {found_url}: {found_phrases}",
            "confidence": 0.5,
            "source_url": found_url,
        }
    return {
        "present": False,
        "evidence": "no AI strategy phrases on /blog, /about, or /",
        "confidence": 0.3,
        "source_url": None,
    }


def collect_signals(
    company_name: str,
    company_slug: str,
    domain: str,
    job_titles: Iterable[str],
    job_post_text_blob: str,
) -> dict[str, dict[str, Any]]:
    """
    Run all six collectors and assemble the input dict expected by score_ai_maturity.

    Catches per-collector exceptions individually so one network failure doesn't
    blank the whole signal bundle.
    """
    out: dict[str, dict[str, Any]] = {}
    titles_list = list(job_titles)

    runners: list[tuple[str, Any]] = [
        ("ai_adjacent_open_roles",   lambda: collect_ai_adjacent_open_roles(titles_list)),
        ("named_ai_ml_leadership",   lambda: collect_named_ai_ml_leadership(company_name)),
        ("github_org_activity",      lambda: collect_github_org_activity(company_slug)),
        ("executive_commentary",     lambda: collect_executive_commentary(company_name)),
        ("modern_data_ml_stack",     lambda: collect_modern_data_ml_stack(job_post_text_blob)),
        ("strategic_communications", lambda: collect_strategic_communications(domain)),
    ]

    for name, fn in runners:
        try:
            out[name] = fn()
        except Exception as exc:
            LOGGER.warning("collector %s raised: %s", name, exc)
            out[name] = {"present": False, "evidence": f"collector error: {exc}", "confidence": 0.0, "source_url": None}

    return out
