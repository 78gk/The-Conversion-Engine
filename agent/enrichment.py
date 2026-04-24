"""
agent/enrichment.py
───────────────────
Signal Enrichment Pipeline for the Conversion Engine.

Four signal sources:
  1. Crunchbase ODM   — company funding/category lookup from Open Data Map CSV
  2. Job-post scraping — Playwright scraper for public Indeed listings (no login)
  3. Layoffs.fyi      — CSV parser for recent workforce-reduction events
  4. Leadership       — C-suite change detection via public news (no login)

All signals are merged into an EnrichmentArtifact dataclass with per-signal
confidence scores (0.0–1.0).

Usage:
    from agent.enrichment import enrich_company
    artifact = enrich_company("Acme Corp")
    print(artifact.to_json())
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ODM_CSV = DATA_DIR / "crunchbase_odm.csv"
LAYOFFS_CSV = DATA_DIR / "layoffs_fyi.csv"


# ─────────────────────────────────────────────────────────────
# Data models
# ─────────────────────────────────────────────────────────────

@dataclass
class SignalResult:
    """A single enrichment signal with its confidence score."""
    signal: str
    value: Any
    confidence: float       # 0.0 – 1.0
    source: str
    fetched_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class EnrichmentArtifact:
    """Structured output of the full enrichment pipeline for one prospect company."""
    company: str
    crunchbase: SignalResult
    job_signals: SignalResult
    layoff_signals: SignalResult
    leadership_changes: SignalResult
    ai_maturity_score: float
    ai_maturity_confidence: float
    icp_segment: int
    icp_confidence: float
    icp_segment_name: str = ""
    enriched_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


# ─────────────────────────────────────────────────────────────
# Signal 1 — Crunchbase ODM lookup
# ─────────────────────────────────────────────────────────────

def lookup_crunchbase_odm(company_name: str) -> SignalResult:
    """
    Look up a company in the Crunchbase Open Data Map CSV.

    The ODM is a free dataset published by Crunchbase containing company
    metadata: funding stage, category, employee count, city, country.

    Download the dataset from https://data.crunchbase.com/docs/open-data-map
    and place it at data/crunchbase_odm.csv with columns:
      name, funding_stage, category_list, employee_count, city, country_code, founded_on
    """
    if not ODM_CSV.exists():
        LOGGER.warning("Crunchbase ODM CSV not found at %s — returning zero-confidence signal", ODM_CSV)
        return SignalResult(
            signal="crunchbase_odm",
            value={"funding_stage": "unknown", "category": "unknown"},
            confidence=0.0,
            source="crunchbase_odm_csv",
        )

    name_lower = company_name.lower().strip()
    best_row: dict | None = None
    best_score = 0.0

    with open(ODM_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_name = row.get("name", "").lower().strip()
            if row_name == name_lower:
                best_row = row
                best_score = 1.0
                break
            if name_lower in row_name or row_name in name_lower:
                candidate_score = len(row_name) / max(len(name_lower), 1)
                if candidate_score > best_score:
                    best_row = row
                    best_score = min(0.75, candidate_score)

    if best_row is None:
        return SignalResult(
            signal="crunchbase_odm",
            value={"funding_stage": "unknown", "category": "unknown"},
            confidence=0.1,
            source="crunchbase_odm_csv",
        )

    return SignalResult(
        signal="crunchbase_odm",
        value={
            "funding_stage": best_row.get("funding_stage", "unknown"),
            "category": best_row.get("category_list", ""),
            "employee_count": best_row.get("employee_count", ""),
            "city": best_row.get("city", ""),
            "country": best_row.get("country_code", ""),
            "founded_on": best_row.get("founded_on", ""),
        },
        confidence=best_score,
        source="crunchbase_odm_csv",
    )


# ─────────────────────────────────────────────────────────────
# Signal 2 — Job-post scraping via Playwright
# ─────────────────────────────────────────────────────────────

AI_KEYWORDS = {
    "machine learning", "artificial intelligence", "nlp", "data science",
    "llm", "deep learning", "mlops", "computer vision", "generative ai",
    "ml engineer", "ai engineer", "data engineer", "prompt engineer",
}


async def scrape_job_posts(company_name: str, max_pages: int = 2) -> SignalResult:
    """
    Scrape public job listings for a company from Indeed.

    Uses Playwright to render public search result pages.
    No login forms, no session cookies, no captcha-bypass code are used.
    Only publicly accessible URLs are fetched.
    """
    try:
        from playwright.async_api import async_playwright  # type: ignore[import]
    except ImportError:
        LOGGER.warning("playwright not installed — returning stub job signal")
        return SignalResult(
            signal="job_posts",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0},
            confidence=0.0,
            source="indeed_playwright",
        )

    search_url = (
        "https://www.indeed.com/jobs"
        f"?q={urllib.parse.quote(company_name + ' engineer')}"
        "&l=&fromage=30"
    )
    all_titles: list[str] = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)

            for _ in range(max_pages):
                titles = await page.eval_on_selector_all(
                    "h2.jobTitle span, [data-testid='jobTitle'] span",
                    "els => els.map(e => e.innerText.trim()).filter(Boolean)",
                )
                all_titles.extend(titles)
                next_btn = await page.query_selector('[data-testid="pagination-page-next"]')
                if next_btn is None:
                    break
                await next_btn.click()
                await page.wait_for_load_state("domcontentloaded", timeout=10000)

            await browser.close()

    except Exception as exc:
        LOGGER.warning("Playwright job scraping failed for %s: %s", company_name, exc)
        return SignalResult(
            signal="job_posts",
            value={"open_roles": 0, "ai_adjacent_roles": 0, "ai_role_ratio": 0.0, "error": str(exc)},
            confidence=0.2,
            source="indeed_playwright",
        )

    open_roles = len(all_titles)
    ai_adjacent = sum(1 for t in all_titles if any(kw in t.lower() for kw in AI_KEYWORDS))
    ai_ratio = round(ai_adjacent / open_roles, 3) if open_roles else 0.0
    confidence = min(0.95, 0.3 + open_roles / 30)

    return SignalResult(
        signal="job_posts",
        value={
            "open_roles": open_roles,
            "ai_adjacent_roles": ai_adjacent,
            "ai_role_ratio": ai_ratio,
            "sample_titles": all_titles[:5],
        },
        confidence=confidence,
        source="indeed_playwright",
    )


# ─────────────────────────────────────────────────────────────
# Signal 3 — Layoffs.fyi CSV parsing
# ─────────────────────────────────────────────────────────────

def parse_layoffs_fyi(company_name: str, lookback_days: int = 365) -> SignalResult:
    """
    Parse the Layoffs.fyi dataset for recent workforce-reduction events.

    Loads from data/layoffs_fyi.csv (downloaded automatically on first run).

    Layoffs.fyi CSV columns:
      Company, Location_HQ, Industry, Laid_Off_Count, Date,
      Funds_Raised, Stage, Date_Added, Country, Percentage
    """
    if not LAYOFFS_CSV.exists():
        _download_layoffs_csv()

    if not LAYOFFS_CSV.exists():
        return SignalResult(
            signal="layoffs_fyi",
            value={"layoff_events": [], "total_laid_off": 0, "event_count": 0},
            confidence=0.0,
            source="layoffs_fyi_csv",
        )

    name_lower = company_name.lower().strip()
    cutoff = datetime.utcnow() - timedelta(days=lookback_days)
    events: list[dict] = []

    with open(LAYOFFS_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_company = row.get("Company", "").lower().strip()
            if name_lower not in row_company and row_company not in name_lower:
                continue
            raw_date = row.get("Date", "").strip()
            event_date = _parse_date(raw_date)
            if event_date is None or event_date < cutoff:
                continue
            events.append({
                "date": raw_date,
                "laid_off_count": row.get("Laid_Off_Count", ""),
                "percentage": row.get("Percentage", ""),
                "stage": row.get("Stage", ""),
                "location": row.get("Location_HQ", ""),
            })

    total_laid_off = 0
    for e in events:
        try:
            total_laid_off += int(str(e["laid_off_count"]).replace(",", "").strip() or "0")
        except (ValueError, TypeError):
            pass

    return SignalResult(
        signal="layoffs_fyi",
        value={
            "layoff_events": events,
            "total_laid_off": total_laid_off,
            "event_count": len(events),
        },
        confidence=0.9 if events else 0.5,
        source="layoffs_fyi_csv",
    )


def _parse_date(raw: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _download_layoffs_csv() -> None:
    """Download the Layoffs.fyi public CSV export to data/layoffs_fyi.csv."""
    url = "https://layoffs.fyi/layoffs_data.csv"
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (enrichment-bot/1.0)"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
        with open(LAYOFFS_CSV, "wb") as f:
            f.write(content)
        LOGGER.info("Downloaded layoffs.fyi CSV (%d bytes)", len(content))
    except Exception as exc:
        LOGGER.warning("Could not download layoffs.fyi CSV: %s", exc)


# ─────────────────────────────────────────────────────────────
# Signal 4 — Leadership change detection
# ─────────────────────────────────────────────────────────────

_EXEC_TITLES = ["cto", "ceo", "coo", "cfo", "vp engineering", "head of ai", "chief ai officer", "president"]
_CHANGE_WORDS = ["appoint", "hire", "join", "named", "promot", "resign", "depart", "step down", "new"]


def detect_leadership_changes(company_name: str, lookback_days: int = 180) -> SignalResult:
    """
    Detect recent C-suite leadership changes for a prospect company.

    Detection strategy:
      1. Crunchbase ODM: flags early-stage companies with recent founding teams.
      2. Public news scan via DuckDuckGo Instant Answer API (no login required).

    Returns a list of detected changes with source snippets and confidence scores.
    """
    changes: list[dict] = []

    # Strategy 1: cross-reference ODM for founding/growth-stage signals
    odm = lookup_crunchbase_odm(company_name)
    if isinstance(odm.value, dict) and odm.confidence > 0.5:
        stage = odm.value.get("funding_stage", "")
        if stage in ("Series A", "Series B", "Seed"):
            changes.append({
                "type": "growth_stage_flag",
                "detail": f"{stage} company — elevated probability of recent leadership changes",
                "confidence": 0.35,
            })

    # Strategy 2: public news scan (no login, no scraping of authenticated pages)
    try:
        news_hits = _scan_duckduckgo_news(company_name)
        changes.extend(news_hits)
    except Exception as exc:
        LOGGER.warning("News leadership scan failed for %s: %s", company_name, exc)

    confidence = min(0.9, 0.25 + 0.2 * len(changes))

    return SignalResult(
        signal="leadership_changes",
        value={
            "changes_detected": changes,
            "change_count": len(changes),
            "lookback_days": lookback_days,
        },
        confidence=confidence,
        source="crunchbase_odm_and_duckduckgo_news",
    )


def _scan_duckduckgo_news(company_name: str) -> list[dict]:
    """
    Query the DuckDuckGo Instant Answer API for leadership change mentions.
    Public API — no authentication, no login, no captcha required.
    """
    query = f'"{company_name}" new CTO CEO COO CFO appointed hired joined'
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (enrichment-bot/1.0)"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    results = []
    abstract = data.get("AbstractText", "")
    if abstract:
        abstract_lower = abstract.lower()
        if any(t in abstract_lower for t in _EXEC_TITLES) and any(w in abstract_lower for w in _CHANGE_WORDS):
            results.append({
                "type": "news_abstract",
                "source_url": data.get("AbstractURL", ""),
                "snippet": abstract[:300],
                "confidence": 0.65,
            })

    for topic in data.get("RelatedTopics", [])[:5]:
        text = topic.get("Text", "").lower()
        if any(t in text for t in _EXEC_TITLES) and any(w in text for w in _CHANGE_WORDS):
            results.append({
                "type": "related_topic",
                "snippet": topic.get("Text", "")[:200],
                "confidence": 0.45,
            })

    return results


# ─────────────────────────────────────────────────────────────
# Scoring functions
# ─────────────────────────────────────────────────────────────

_FUNDING_SCORE: dict[str, float] = {
    "Series C": 3.0, "Series D": 3.0, "Series E": 3.0, "Growth": 3.0,
    "IPO": 3.0, "Series B": 2.5, "Series A": 2.0, "Seed": 1.0,
}


def compute_ai_maturity_score(
    job_signal: SignalResult,
    crunchbase_signal: SignalResult,
    layoff_signal: SignalResult,
    leadership_signal: SignalResult,
) -> tuple[float, float]:
    """
    Compute an AI maturity score (0–10) and confidence from the four signals.

    Weights:
      40% — AI role ratio (job posts signal)
      30% — Funding stage (Crunchbase ODM — proxy for budget)
      20% — Workforce stability (no recent layoffs)
      10% — Leadership change urgency
    """
    parts: list[tuple[float, float]] = []

    job_val = job_signal.value if isinstance(job_signal.value, dict) else {}
    ai_ratio = float(job_val.get("ai_role_ratio", 0.0))
    parts.append((min(4.0, ai_ratio * 10), job_signal.confidence))

    cb_val = crunchbase_signal.value if isinstance(crunchbase_signal.value, dict) else {}
    funding = cb_val.get("funding_stage", "")
    parts.append((_FUNDING_SCORE.get(funding, 1.5), crunchbase_signal.confidence))

    layoff_val = layoff_signal.value if isinstance(layoff_signal.value, dict) else {}
    events = int(layoff_val.get("event_count", 0))
    parts.append((max(0.0, 2.0 - events * 0.5), layoff_signal.confidence))

    lead_val = leadership_signal.value if isinstance(leadership_signal.value, dict) else {}
    changes = int(lead_val.get("change_count", 0))
    parts.append((min(1.0, changes * 0.5), leadership_signal.confidence))

    raw_score = sum(s for s, _ in parts)
    avg_confidence = sum(c for _, c in parts) / len(parts)

    return round(min(10.0, max(0.0, raw_score)), 2), round(avg_confidence, 3)


def compute_icp_segment(ai_score: float) -> tuple[int, float]:
    """Map AI maturity score to ICP segment (1=highest intent, 5=lowest)."""
    if ai_score >= 8.0:
        return 1, 0.90
    if ai_score >= 6.0:
        return 2, 0.80
    if ai_score >= 4.0:
        return 3, 0.70
    if ai_score >= 2.0:
        return 4, 0.60
    return 5, 0.50


def _parse_headcount(employee_count_str: str) -> tuple[int, int]:
    """Parse '11-50' style employee count into (min, max). Returns (0, 0) on failure."""
    s = str(employee_count_str).strip()
    if "+" in s:
        try:
            return int(s.replace("+", "")), 999_999
        except ValueError:
            return 0, 0
    if "-" in s:
        parts = s.split("-", 1)
        try:
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            return 0, 0
    try:
        v = int(s)
        return v, v
    except ValueError:
        return 0, 0


def _days_since_most_recent_layoff(layoff_value: dict) -> int:
    """Return days since the most recent layoff event, or 999 if none recorded."""
    events = layoff_value.get("layoff_events", [])
    if not events:
        return 999
    now = datetime.utcnow()
    min_days = 999
    for evt in events:
        parsed = _parse_date(evt.get("date", ""))
        if parsed is not None:
            min_days = min(min_days, (now - parsed).days)
    return min_days


def classify_icp_segment_name(artifact: EnrichmentArtifact) -> tuple[str, float]:
    """
    Classify a prospect into one of the 4 Tenacious ICP segments using the
    priority ordering defined in data/tenacious_sales_data/seed/icp_definition.md.

    Priority order (first match wins):
      1. Layoff ≤120d + Series A/B funding          → Segment 2 (cost pressure dominates)
      2. Leadership change + headcount 50–500        → Segment 3 (transition window)
      3. AI score ≥4.0 + capability-gap job signals  → Segment 4 (specialised gap)
      4. Series A/B funding + headcount ≤80 + 5+ roles → Segment 1 (fresh-funded startup)
      5. No match                                    → abstain

    Returns (segment_name, confidence).
    """
    crunch = artifact.crunchbase.value if isinstance(artifact.crunchbase.value, dict) else {}
    jobs = artifact.job_signals.value if isinstance(artifact.job_signals.value, dict) else {}
    layoff = artifact.layoff_signals.value if isinstance(artifact.layoff_signals.value, dict) else {}
    leadership = artifact.leadership_changes.value if isinstance(artifact.leadership_changes.value, dict) else {}

    funding_stage = crunch.get("funding_stage", "")
    open_roles = int(jobs.get("open_roles", 0) or 0)
    ai_adjacent = int(jobs.get("ai_adjacent_roles", 0) or 0)
    layoff_event_count = int(layoff.get("event_count", 0) or 0)
    leadership_change_count = int(leadership.get("change_count", 0) or 0)

    hc_min, _ = _parse_headcount(crunch.get("employee_count", ""))
    days_since_layoff = _days_since_most_recent_layoff(layoff)
    series_ab = funding_stage in ("Series A", "Series B")

    # Priority 1 — layoff in last 120d + fresh Series A/B → cost-pressure window
    if layoff_event_count > 0 and days_since_layoff <= 120 and series_ab:
        return "Segment 2 — Mid-market platforms restructuring cost", min(0.85, artifact.layoff_signals.confidence)

    # Priority 2 — leadership change + right-size headcount → transition window
    if leadership_change_count > 0 and (hc_min == 0 or 50 <= hc_min <= 500):
        return "Segment 3 — Engineering-leadership transitions", min(0.80, artifact.leadership_changes.confidence)

    # Priority 3 — AI score ≥4.0 (≈ readiness 2/3) + repeated niche role signals → capability gap
    if artifact.ai_maturity_score >= 4.0 and open_roles >= 3 and ai_adjacent >= 1:
        return "Segment 4 — Specialized capability gaps", min(0.70, artifact.ai_maturity_confidence)

    # Priority 4 — fresh Series A/B + startup headcount + 5+ open roles → funded startup
    if series_ab and open_roles >= 5 and (hc_min == 0 or hc_min <= 80):
        return "Segment 1 — Recently-funded Series A/B startups", min(0.85, artifact.crunchbase.confidence)

    return "abstain", 0.30


# ─────────────────────────────────────────────────────────────
# Pipeline entrypoint
# ─────────────────────────────────────────────────────────────

def enrich_company(company_name: str) -> EnrichmentArtifact:
    """
    Run the full four-signal enrichment pipeline for a prospect company.

    Collects all signals, merges them into an EnrichmentArtifact with
    per-signal confidence scores, and computes AI maturity score and ICP segment.
    """
    LOGGER.info("Starting enrichment pipeline for: %s", company_name)

    crunchbase = lookup_crunchbase_odm(company_name)
    LOGGER.info("  [1/4] Crunchbase: confidence=%.2f stage=%s",
                crunchbase.confidence,
                crunchbase.value.get("funding_stage") if isinstance(crunchbase.value, dict) else "?")

    try:
        job_signals = asyncio.run(scrape_job_posts(company_name))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        job_signals = loop.run_until_complete(scrape_job_posts(company_name))
    LOGGER.info("  [2/4] Job posts: confidence=%.2f open_roles=%s",
                job_signals.confidence,
                job_signals.value.get("open_roles") if isinstance(job_signals.value, dict) else "?")

    layoff = parse_layoffs_fyi(company_name)
    LOGGER.info("  [3/4] Layoffs.fyi: confidence=%.2f events=%s",
                layoff.confidence,
                layoff.value.get("event_count") if isinstance(layoff.value, dict) else "?")

    leadership = detect_leadership_changes(company_name)
    LOGGER.info("  [4/4] Leadership: confidence=%.2f changes=%s",
                leadership.confidence,
                leadership.value.get("change_count") if isinstance(leadership.value, dict) else "?")

    ai_score, ai_conf = compute_ai_maturity_score(job_signals, crunchbase, layoff, leadership)
    icp_seg, icp_conf = compute_icp_segment(ai_score)

    artifact = EnrichmentArtifact(
        company=company_name,
        crunchbase=crunchbase,
        job_signals=job_signals,
        layoff_signals=layoff,
        leadership_changes=leadership,
        ai_maturity_score=ai_score,
        ai_maturity_confidence=ai_conf,
        icp_segment=icp_seg,
        icp_confidence=icp_conf,
    )

    seg_name, _ = classify_icp_segment_name(artifact)
    artifact.icp_segment_name = seg_name

    LOGGER.info("Enrichment complete: %s | ai_score=%.2f icp_seg=%d seg=%s conf=%.2f",
                company_name, ai_score, icp_seg, seg_name, icp_conf)
    return artifact
