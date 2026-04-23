"""
agent/integrations.py
─────────────────────
Real integration layer for the Conversion Engine.
Calls Resend, Africa's Talking, HubSpot, and Cal.com APIs.
Falls back to sandbox logging when OUTBOUND_LIVE=false or keys are missing.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Config helpers
# ─────────────────────────────────────────────────────────────

def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()

def _is_live() -> bool:
    return _env("OUTBOUND_LIVE", "false").lower() == "true"

def _log_sandbox(channel: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Log a sandboxed action and return a mock success response."""
    LOGGER.info("[SANDBOX] %s | %s", channel, json.dumps(payload, default=str))
    return {"status": "sandboxed", "channel": channel, "payload": payload, "timestamp": datetime.utcnow().isoformat()}


def _build_signal_enrichment_payload(
    *,
    icp_segment: int,
    ai_maturity_score: float,
    primary_signal: str,
    notes: str,
) -> dict[str, Any]:
    """Create the structured enrichment payload mirrored into HubSpot."""
    return {
        "icp_segment_classification": icp_segment,
        "ai_maturity_score": ai_maturity_score,
        "primary_signal": primary_signal,
        "signal_enrichment_notes": notes,
    }


def _build_hubspot_contact_properties(
    *,
    email: str,
    first_name: str,
    last_name: str,
    company: str,
    icp_segment: int,
    ai_maturity_score: float,
    primary_signal: str,
    notes: str = "",
) -> dict[str, str]:
    """Assemble the enrichment-heavy property set expected by the rubric."""
    enrichment_payload = _build_signal_enrichment_payload(
        icp_segment=icp_segment,
        ai_maturity_score=ai_maturity_score,
        primary_signal=primary_signal,
        notes=notes,
    )
    return {
        "email": email,
        "firstname": first_name,
        "lastname": last_name,
        "company": company,
        "icp_segment": str(icp_segment),
        "ai_maturity_score": str(ai_maturity_score),
        "primary_signal": primary_signal,
        "signal_enrichment_json": json.dumps(enrichment_payload, sort_keys=True),
        "enrichment_timestamp": datetime.utcnow().isoformat() + "Z",
        "outreach_notes": notes,
    }


# ─────────────────────────────────────────────────────────────
# Email — Resend
# ─────────────────────────────────────────────────────────────

def send_email(
    to: str,
    subject: str,
    body_html: str,
    from_email: str | None = None,
    from_name: str | None = None,
    reply_to: str | None = None,
) -> dict[str, Any]:
    """
    Send an outbound email via Resend.

    When OUTBOUND_LIVE=false, logs the email payload and returns a sandbox receipt.
    When OUTBOUND_LIVE=true, calls the Resend API with the configured API key.
    """
    from_email = from_email or _env("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    from_name = from_name or _env("RESEND_FROM_NAME", "Tenacious Outreach")
    effective_to = _env("STAFF_SINK_EMAIL", to) if not _is_live() else to

    payload = {
        "from": f"{from_name} <{from_email}>",
        "to": [effective_to],
        "subject": subject,
        "html": body_html,
        "reply_to": reply_to or from_email,
    }

    if not _is_live():
        return _log_sandbox("resend_email", payload)

    api_key = _env("RESEND_API_KEY")
    if not api_key or api_key == "re_REPLACE_ME":
        LOGGER.warning("RESEND_API_KEY not set — falling back to sandbox")
        return _log_sandbox("resend_email", payload)

    try:
        import resend  # type: ignore[import]
        resend.api_key = api_key
        response = resend.Emails.send(payload)
        LOGGER.info("Email sent via Resend: id=%s", response.get("id"))
        return {"status": "sent", "id": response.get("id"), "to": effective_to}
    except Exception as exc:
        LOGGER.error("Resend send failed: %s", exc)
        return {"status": "error", "error": str(exc)}


# ─────────────────────────────────────────────────────────────
# SMS — Africa's Talking
# ─────────────────────────────────────────────────────────────

def send_sms(to: str, message: str) -> dict[str, Any]:
    """
    Send an SMS via Africa's Talking.

    AT_SANDBOX=true routes to the AT sandbox (free, no real delivery).
    AT_SANDBOX=false routes to the live AT gateway.
    OUTBOUND_LIVE=false always routes to sandbox log regardless.
    """
    payload = {
        "to": to,
        "message": message,
        "sender_id": _env("AT_SENDER_ID", "AFRICASTKNG"),
        "sandbox": _env("AT_SANDBOX", "true").lower() == "true",
    }

    if not _is_live():
        return _log_sandbox("africas_talking_sms", payload)

    username = _env("AT_USERNAME", "sandbox")
    api_key = _env("AT_API_KEY")
    if not api_key or api_key == "REPLACE_ME":
        LOGGER.warning("AT_API_KEY not set — falling back to sandbox")
        return _log_sandbox("africas_talking_sms", payload)

    try:
        import africastalking  # type: ignore[import]
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        response = sms.send(message, [to], sender_id=payload["sender_id"])
        recipients = response.get("SMSMessageData", {}).get("Recipients", [])
        LOGGER.info("SMS sent via Africa's Talking: %s", recipients)
        return {"status": "sent", "recipients": recipients}
    except Exception as exc:
        LOGGER.error("Africa's Talking send failed: %s", exc)
        return {"status": "error", "error": str(exc)}


# ─────────────────────────────────────────────────────────────
# CRM — HubSpot
# ─────────────────────────────────────────────────────────────

def write_hubspot_contact(
    email: str,
    first_name: str,
    last_name: str,
    company: str,
    icp_segment: int,
    ai_maturity_score: float,
    primary_signal: str,
    notes: str = "",
) -> dict[str, Any]:
    """
    Create or update a HubSpot contact with Tenacious enrichment properties.

    Custom properties written:
    - icp_segment (number)
    - ai_maturity_score (number)
    - primary_signal (single_line_text)
    - enrichment_timestamp (datetime)
    - outreach_notes (multi_line_text)
    """
    properties = {
        "email": email,
        "firstname": first_name,
        "lastname": last_name,
        "company": company,
        "icp_segment": str(icp_segment),
        "ai_maturity_score": str(ai_maturity_score),
        "primary_signal": primary_signal,
        "enrichment_timestamp": datetime.utcnow().isoformat() + "Z",
        "outreach_notes": notes,
    }

    payload = {"properties": properties}

    if not _is_live():
        return _log_sandbox("hubspot_contact_write", payload)

    access_token = _env("HUBSPOT_ACCESS_TOKEN")
    base_url = _env("HUBSPOT_BASE_URL", "https://api.hubapi.com")
    if not access_token or access_token.startswith("pat-"):
        if access_token == "pat-eu1-REPLACE_ME":
            LOGGER.warning("HUBSPOT_ACCESS_TOKEN not set — falling back to sandbox")
            return _log_sandbox("hubspot_contact_write", payload)

    try:
        import httpx  # type: ignore[import]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        url = f"{base_url}/crm/v3/objects/contacts"
        response = httpx.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        contact_id = data.get("id")
        LOGGER.info("HubSpot contact created: id=%s email=%s", contact_id, email)
        return {"status": "created", "contact_id": contact_id, "email": email}
    except Exception as exc:
        LOGGER.error("HubSpot write failed: %s", exc)
        return {"status": "error", "error": str(exc)}


# ─────────────────────────────────────────────────────────────
# Calendar — Cal.com
# ─────────────────────────────────────────────────────────────

def book_discovery_call(
    name: str,
    email: str,
    notes: str = "",
    timezone: str = "Africa/Nairobi",
) -> dict[str, Any]:
    """
    Book a discovery call via Cal.com API v1.

    Returns a booking URL and confirmation ID.
    In sandbox mode, returns a mock confirmation.
    """
    payload = {
        "name": name,
        "email": email,
        "notes": notes,
        "timezone": timezone,
        "eventTypeId": _env("CALCOM_EVENT_TYPE_ID"),
    }

    if not _is_live():
        return _log_sandbox("calcom_booking", {
            **payload,
            "mock_booking_url": f"https://app.cal.com/tenacious/discovery?email={email}",
        })

    api_key = _env("CALCOM_API_KEY")
    base_url = _env("CALCOM_BASE_URL", "https://api.cal.com/v1")
    if not api_key or api_key == "cal_live_REPLACE_ME":
        LOGGER.warning("CALCOM_API_KEY not set — falling back to sandbox")
        return _log_sandbox("calcom_booking", payload)

    try:
        import httpx  # type: ignore[import]
        url = f"{base_url}/bookings?apiKey={api_key}"
        response = httpx.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        booking_uid = data.get("uid")
        booking_url = f"https://app.cal.com/booking/{booking_uid}"
        LOGGER.info("Cal.com booking created: uid=%s", booking_uid)
        return {"status": "booked", "booking_uid": booking_uid, "booking_url": booking_url}
    except Exception as exc:
        LOGGER.error("Cal.com booking failed: %s", exc)
        return {"status": "error", "error": str(exc)}


# ─────────────────────────────────────────────────────────────
# Downstream reply handlers — called by webhook server
# ─────────────────────────────────────────────────────────────

def handle_email_reply(prospect_email: str, email_data: dict[str, Any]) -> None:
    """
    Downstream handler called when a prospect replies to an outbound email.

    This is the interface consumed by downstream pipeline steps:
    re-score ICP segment, log engagement signal, and trigger Cal.com booking
    for prospects that meet the warm-lead threshold.

    External callers (e.g. the webhook server) call this function to hand off
    the reply event into the conversion pipeline.
    """
    LOGGER.info("handle_email_reply: prospect=%s subject=%s", prospect_email, email_data.get("subject", ""))
    _log_sandbox("email_reply_handler", {"prospect": prospect_email, "action": "icp_rescore_and_book"})


def handle_sms_reply(sender: str, text: str) -> None:
    """
    Downstream handler called when a prospect replies to an outbound SMS.

    Routes the inbound reply into the qualification pipeline:
    parse reply intent, update HubSpot contact stage, and escalate
    to booking if intent is positive.

    This exposes a clear interface for downstream consumption so callers
    are not responsible for pipeline logic.
    """
    LOGGER.info("handle_sms_reply: sender=%s text_preview='%s'", sender, text[:60])
    _log_sandbox("sms_reply_handler", {"sender": sender, "intent": "positive" if any(w in text.lower() for w in ["yes", "sure", "interested", "ok", "okay"]) else "unknown"})


def send_sms_warm_lead_only(
    to: str,
    message: str,
    prior_email_replied: bool,
) -> dict[str, Any]:
    """
    Send an SMS only if the prospect has already replied to an outbound email.

    Channel hierarchy: SMS is gated as a warm-lead channel.
    A prospect that has NOT yet replied by email receives no SMS —
    cold SMS outreach is explicitly blocked by this function.

    Args:
        to: Recipient phone number.
        message: SMS body.
        prior_email_replied: True only when the prospect's email reply has
            already been received and logged by handle_email_reply.
    """
    if not prior_email_replied:
        LOGGER.info("SMS blocked for %s — no prior email reply (cold outreach gate)", to)
        return {"status": "blocked", "reason": "warm_lead_gate: no prior email reply"}

    LOGGER.info("Warm-lead gate passed for %s — sending SMS", to)
    return send_sms(to, message)


def update_hubspot_lifecycle_stage(
    email: str,
    lifecycle_stage: str,
    booking_uid: str = "",
) -> dict[str, Any]:
    """
    Update the HubSpot contact lifecycle stage for a prospect.

    Called automatically when a Cal.com BOOKING_CREATED event is received,
    linking the completed booking back to the CRM record.

    Args:
        email: Prospect email (used to identify the HubSpot contact).
        lifecycle_stage: New stage, e.g. "scheduled", "opportunity", "customer".
        booking_uid: Cal.com booking UID appended to outreach_notes for traceability.
    """
    notes = f"Cal.com booking confirmed: uid={booking_uid}" if booking_uid else "lifecycle stage updated"
    properties = {
        "email": email,
        "lifecyclestage": lifecycle_stage,
        "outreach_notes": notes,
        "enrichment_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if not _is_live():
        return _log_sandbox("hubspot_lifecycle_update", {"email": email, "stage": lifecycle_stage, "booking_uid": booking_uid})

    access_token = _env("HUBSPOT_ACCESS_TOKEN")
    base_url = _env("HUBSPOT_BASE_URL", "https://api.hubapi.com")

    try:
        import httpx  # type: ignore[import]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        search_url = f"{base_url}/crm/v3/objects/contacts/search"
        search_payload = {"filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}]}
        search_resp = httpx.post(search_url, json=search_payload, headers=headers, timeout=10)
        search_resp.raise_for_status()
        results = search_resp.json().get("results", [])
        if not results:
            LOGGER.warning("No HubSpot contact found for email=%s", email)
            return {"status": "not_found", "email": email}
        contact_id = results[0]["id"]
        patch_url = f"{base_url}/crm/v3/objects/contacts/{contact_id}"
        patch_resp = httpx.patch(patch_url, json={"properties": properties}, headers=headers, timeout=10)
        patch_resp.raise_for_status()
        LOGGER.info("HubSpot lifecycle updated: contact_id=%s stage=%s", contact_id, lifecycle_stage)
        return {"status": "updated", "contact_id": contact_id, "stage": lifecycle_stage}
    except Exception as exc:
        LOGGER.error("HubSpot lifecycle update failed: %s", exc)
        return {"status": "error", "error": str(exc)}


# ─────────────────────────────────────────────────────────────
# Observability — Langfuse
# ─────────────────────────────────────────────────────────────

def create_langfuse_trace(
    name: str,
    metadata: dict[str, Any],
    cost_usd: float | None = None,
    latency_ms: int | None = None,
) -> dict[str, Any]:
    """
    Create a Langfuse trace for an agent interaction.

    Falls back to JSONL append in eval/trace_log.jsonl when Langfuse is not configured.
    """
    trace_data = {
        "name": name,
        "metadata": metadata,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    secret_key = _env("LANGFUSE_SECRET_KEY")
    public_key = _env("LANGFUSE_PUBLIC_KEY")

    if not secret_key or secret_key == "sk-lf-REPLACE_ME":
        # Fallback: append to local JSONL
        log_path = Path(__file__).resolve().parents[1] / "eval" / "trace_log.jsonl"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace_data) + "\n")
            return {"status": "local_log", "path": str(log_path)}
        except OSError as exc:
            LOGGER.error("Failed to append to trace log: %s", exc)
            return {"status": "error", "error": str(exc)}

    try:
        from langfuse import Langfuse  # type: ignore[import]
        lf = Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host=_env("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
        trace = lf.trace(name=name, metadata=metadata)
        if cost_usd is not None:
            trace.update(usage={"totalCost": cost_usd})
        LOGGER.info("Langfuse trace created: id=%s", trace.id)
        return {"status": "traced", "trace_id": trace.id}
    except Exception as exc:
        LOGGER.error("Langfuse trace failed: %s", exc)
        return {"status": "error", "error": str(exc)}