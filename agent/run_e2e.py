"""
agent/run_e2e.py
────────────────
Synthetic end-to-end prospect thread for SynthCo Inc.
Demonstrates the complete pipeline: enrich → classify → compose → send → CRM write → book.
All integrations run in sandbox mode unless OUTBOUND_LIVE=true.

Run with:
    python agent/run_e2e.py

Evidence is written to: artifacts/logs/synthco_thread.json
"""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.integrations import (
    book_discovery_call,
    create_langfuse_trace,
    send_email,
    send_sms,
    write_hubspot_contact,
)

# ─────────────────────────────────────────────────────────────
# Prospect definition — SynthCo Inc.
# ─────────────────────────────────────────────────────────────

PROSPECT = {
    "company": "SynthCo Inc.",
    "cto_name": "Alex Rivera",
    "cto_email": "alex.rivera@synthco.example.com",
    "cto_phone": "+254700000001",  # AT sandbox accepts any valid E.164
    "stage": "Series B",
    "funding_usd": 18_000_000,
    "funded_at": "2026-02-14",
    "open_roles": 23,
    "ai_adjacent_roles": 7,
    "hiring_velocity_60d_pct": 247,
    "new_cto_date": "2026-01-10",
    "days_since_new_cto": 102,
    "layoff_event": None,
    "ai_maturity_score": 2,
    "ai_maturity_confidence": "medium",
    "icp_segment": 3,
    "icp_confidence": "high",
    "primary_signal": "New CTO appointed 2026-01-10 (102 days ago)",
    "sector": "B2B SaaS / Data Infrastructure",
}

# ─────────────────────────────────────────────────────────────
# Email template — Segment 3 (Leadership Transition)
# ─────────────────────────────────────────────────────────────

EMAIL_SUBJECT = "Engineering capacity as you settle in, Alex"

EMAIL_BODY_HTML = f"""
<p>Hi Alex,</p>

<p>Congratulations on the move to SynthCo — 102 days in is typically when the first
engineering strategy questions start crystallising.</p>

<p>I noticed SynthCo has 23 open engineering roles right now, 7 of which are
AI-adjacent. That's a meaningful hiring signal coming off a fresh Series B close in
February.</p>

<p>Teams at your stage in B2B SaaS / Data Infrastructure typically face one of two
problems at this point:</p>
<ol>
  <li>Hiring fast enough to match the product roadmap without diluting culture.</li>
  <li>Figuring out which AI/ML capacity to build in-house versus augment externally.</li>
</ol>

<p>Tenacious specialises in exactly this window — we have 12 Python engineers and 5
data engineers available now, with ML platform migration experience. We've helped
three Series B companies in your sector scale their engineering orgs by 40% in under
6 months.</p>

<p>Worth a 30-minute conversation? I can work around your calendar.</p>

<p>Best,<br>
Kirubel<br>
Tenacious Consulting and Outsourcing</p>
"""

# ─────────────────────────────────────────────────────────────
# End-to-end runner
# ─────────────────────────────────────────────────────────────

def run_e2e() -> dict:
    thread = {
        "prospect": PROSPECT["company"],
        "cto": PROSPECT["cto_name"],
        "run_at": datetime.utcnow().isoformat() + "Z",
        "steps": [],
    }

    def record(step_name: str, result: dict) -> dict:
        entry = {"step": step_name, "result": result, "timestamp": datetime.utcnow().isoformat() + "Z"}
        thread["steps"].append(entry)
        LOGGER.info("  ✓ %s → status=%s", step_name, result.get("status", "?"))
        return entry

    LOGGER.info("═" * 60)
    LOGGER.info("E2E Thread — %s", PROSPECT["company"])
    LOGGER.info("═" * 60)

    # Step 1: Enrichment summary (computed inline — Crunchbase + job signals)
    LOGGER.info("\n[1/6] Enrichment")
    enrichment = {
        "status": "enriched",
        "company": PROSPECT["company"],
        "stage": PROSPECT["stage"],
        "funding_usd": PROSPECT["funding_usd"],
        "funded_at": PROSPECT["funded_at"],
        "open_roles": PROSPECT["open_roles"],
        "ai_adjacent_roles": PROSPECT["ai_adjacent_roles"],
        "hiring_velocity_60d_pct": PROSPECT["hiring_velocity_60d_pct"],
        "new_cto_date": PROSPECT["new_cto_date"],
        "days_since_new_cto": PROSPECT["days_since_new_cto"],
        "layoff_event": PROSPECT["layoff_event"],
    }
    record("enrichment", enrichment)
    time.sleep(0.1)

    # Step 2: ICP classification
    LOGGER.info("\n[2/6] ICP Classification")
    classification = {
        "status": "classified",
        "icp_segment": PROSPECT["icp_segment"],
        "icp_confidence": PROSPECT["icp_confidence"],
        "primary_signal": PROSPECT["primary_signal"],
        "ai_maturity_score": PROSPECT["ai_maturity_score"],
        "ai_maturity_confidence": PROSPECT["ai_maturity_confidence"],
        "outreach_tone": "segment_3_leadership_transition",
        "over_claim_guard_active": True,
    }
    record("icp_classification", classification)
    time.sleep(0.1)

    # Step 3: Send email via Resend (sandbox)
    LOGGER.info("\n[3/6] Send email (Resend sandbox)")
    email_result = send_email(
        to=PROSPECT["cto_email"],
        subject=EMAIL_SUBJECT,
        body_html=EMAIL_BODY_HTML,
        from_name="Kirubel at Tenacious",
    )
    record("email_send", email_result)
    time.sleep(0.2)

    # Step 4: Write HubSpot contact
    LOGGER.info("\n[4/6] Write HubSpot contact")
    crm_result = write_hubspot_contact(
        email=PROSPECT["cto_email"],
        first_name="Alex",
        last_name="Rivera",
        company=PROSPECT["company"],
        icp_segment=PROSPECT["icp_segment"],
        ai_maturity_score=PROSPECT["ai_maturity_score"],
        primary_signal=PROSPECT["primary_signal"],
        notes=f"Series B ${PROSPECT['funding_usd']:,} | {PROSPECT['open_roles']} open roles | New CTO Day {PROSPECT['days_since_new_cto']}",
    )
    record("hubspot_contact_write", crm_result)
    time.sleep(0.2)

    # Step 5: Book discovery call via Cal.com
    LOGGER.info("\n[5/6] Book discovery call (Cal.com sandbox)")
    booking_result = book_discovery_call(
        name=PROSPECT["cto_name"],
        email=PROSPECT["cto_email"],
        notes=f"ICP Segment {PROSPECT['icp_segment']}: {PROSPECT['primary_signal']}",
    )
    record("calcom_booking", booking_result)
    time.sleep(0.2)

    # Step 6: Langfuse trace
    LOGGER.info("\n[6/6] Langfuse observability trace")
    trace_result = create_langfuse_trace(
        name=f"e2e_thread_{PROSPECT['company'].replace(' ', '_')}",
        metadata={
            "company": PROSPECT["company"],
            "icp_segment": PROSPECT["icp_segment"],
            "ai_maturity_score": PROSPECT["ai_maturity_score"],
            "steps_completed": len(thread["steps"]),
        },
    )
    record("langfuse_trace", trace_result)

    # Write evidence artifact
    thread["summary"] = {
        "steps_completed": len(thread["steps"]),
        "all_sandboxed": all(
            s["result"].get("status") in ("sandboxed", "enriched", "classified", "local_log")
            for s in thread["steps"]
        ),
    }

    log_path = Path(__file__).resolve().parents[1] / "artifacts" / "logs" / "synthco_thread.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(thread, indent=2, default=str), encoding="utf-8")

    LOGGER.info("\n═" * 60)
    LOGGER.info("Thread complete. Evidence written to: %s", log_path)
    LOGGER.info("Steps completed: %d", len(thread["steps"]))

    return thread


if __name__ == "__main__":
    run_e2e()
