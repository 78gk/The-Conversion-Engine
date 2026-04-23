"""
agent/webhook.py
────────────────
FastAPI webhook server for the Conversion Engine.
Receives callbacks from Resend, Africa's Talking, Cal.com, and HubSpot.

Deploy to Render:
  - Build command: pip install -r agent/requirements.txt
  - Start command: uvicorn agent.webhook:app --host 0.0.0.0 --port $PORT

Run locally:
  uvicorn agent.webhook:app --reload --port 8000

Webhook URLs to register (replace with your Render URL):
  Resend reply handler:       POST https://<render-url>/webhooks/resend
  Africa's Talking callback:  POST https://<render-url>/webhooks/africas-talking
  Cal.com booking event:      POST https://<render-url>/webhooks/calcom
  HubSpot contact event:      POST https://<render-url>/webhooks/hubspot
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

# Downstream handlers — called when inbound events require pipeline action
from agent.integrations import (
    handle_email_reply,
    handle_sms_reply,
    update_hubspot_lifecycle_stage,
)

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

app = FastAPI(
    title="Conversion Engine Webhook Server",
    description="Receives callbacks from Resend, Africa's Talking, Cal.com, and HubSpot.",
    version="1.0.0",
)

# Path for persisting incoming webhook events
EVENTS_LOG = Path(__file__).resolve().parents[1] / "artifacts" / "logs" / "webhook_events.jsonl"


def _log_event(source: str, event_type: str, data: dict[str, Any]) -> None:
    """Append a received webhook event to the events log."""
    entry = {
        "source": source,
        "event_type": event_type,
        "received_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }
    try:
        EVENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(EVENTS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as exc:
        LOGGER.error("Failed to log webhook event: %s", exc)


def _verify_hmac(payload: bytes, signature: str, secret: str) -> bool:
    """Verify an HMAC-SHA256 webhook signature."""
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.lstrip("sha256="))


# ─────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health_check() -> JSONResponse:
    """Render pings this every 30 seconds to keep the service alive."""
    return JSONResponse({"status": "ok", "service": "conversion-engine-webhook", "timestamp": datetime.utcnow().isoformat()})


@app.get("/", tags=["system"])
async def root() -> JSONResponse:
    return JSONResponse({"service": "The Conversion Engine Webhook Server", "version": "1.0.0"})


# ─────────────────────────────────────────────────────────────
# Resend — email reply events
# ─────────────────────────────────────────────────────────────

@app.post("/webhooks/resend", tags=["webhooks"])
async def resend_webhook(request: Request) -> JSONResponse:
    """
    Receives email events from Resend.
    Event types handled: email.opened, email.clicked, email.replied, email.bounced

    Register at: resend.com/webhooks → add endpoint → select events
    """
    try:
        payload = await request.json()
    except Exception:
        LOGGER.warning("Resend webhook: malformed JSON payload received")
        return JSONResponse({"status": "error", "reason": "malformed_payload"}, status_code=400)

    event_type = payload.get("type", "unknown")
    email_data = payload.get("data", {})
    LOGGER.info("Resend event received: type=%s to=%s", event_type, email_data.get("to"))
    _log_event("resend", event_type, payload)

    if event_type == "email.replied":
        prospect_email = email_data.get("from", "unknown")
        LOGGER.info("Email reply from prospect: %s — triggering qualification", prospect_email)
        handle_email_reply(prospect_email, email_data)
        return JSONResponse({"status": "reply_received", "prospect": prospect_email})

    if event_type == "email.bounced":
        LOGGER.warning("Email bounced: %s", email_data.get("to"))
        return JSONResponse({"status": "bounce_logged"})

    return JSONResponse({"status": "event_logged", "event_type": event_type})


# ─────────────────────────────────────────────────────────────
# Africa's Talking — SMS delivery and reply callbacks
# ─────────────────────────────────────────────────────────────

@app.post("/webhooks/africas-talking", tags=["webhooks"])
async def africas_talking_webhook(request: Request) -> JSONResponse:
    """
    Receives SMS delivery receipts and inbound reply messages from Africa's Talking.

    Register at: account.africastalking.com → SMS → Callback URL
    Two types:
    - Delivery report: fired when SMS is delivered to the handset
    - Inbound message: fired when a prospect replies to an SMS
    """
    form = await request.form()
    payload = dict(form)
    event_type = "sms.inbound" if "text" in payload else "sms.delivery"

    LOGGER.info("Africa's Talking event: type=%s from=%s", event_type, payload.get("from"))
    _log_event("africas_talking", event_type, payload)

    if event_type == "sms.inbound":
        sender = payload.get("from", "")
        text = payload.get("text", "")
        LOGGER.info("SMS reply from %s: '%s' — routing to qualification handler", sender, text[:80])
        handle_sms_reply(sender, text)
        return JSONResponse({"status": "inbound_routed", "from": sender})

    delivery_status = payload.get("status", "")
    LOGGER.info("SMS delivery status: %s for %s", delivery_status, payload.get("to"))
    return JSONResponse({"status": "delivery_logged", "delivery_status": delivery_status})


# ─────────────────────────────────────────────────────────────
# Cal.com — booking events
# ─────────────────────────────────────────────────────────────

@app.post("/webhooks/calcom", tags=["webhooks"])
async def calcom_webhook(
    request: Request,
    x_cal_signature_256: str = Header(default=""),
) -> JSONResponse:
    """
    Receives booking events from Cal.com.
    Event types: BOOKING_CREATED, BOOKING_RESCHEDULED, BOOKING_CANCELLED

    Register at: app.cal.com/settings/developer/webhooks
    Set signing secret to match WEBHOOK_SECRET in .env
    """
    body = await request.body()
    secret = os.environ.get("WEBHOOK_SECRET", "")

    if secret and x_cal_signature_256:
        if not _verify_hmac(body, x_cal_signature_256, secret):
            LOGGER.warning("Cal.com webhook signature verification failed")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    payload = json.loads(body)
    trigger = payload.get("triggerEvent", "unknown")
    booking = payload.get("payload", {})
    attendee_email = next(
        (a.get("email") for a in booking.get("attendees", [])), None
    )

    LOGGER.info("Cal.com event: trigger=%s attendee=%s", trigger, attendee_email)
    _log_event("calcom", trigger, payload)

    if trigger == "BOOKING_CREATED":
        booking_uid = booking.get("uid", "")
        LOGGER.info("Discovery call booked for %s at %s", attendee_email, booking.get("startTime"))
        if attendee_email:
            update_hubspot_lifecycle_stage(attendee_email, "scheduled", booking_uid)
        return JSONResponse({"status": "booking_confirmed", "attendee": attendee_email})

    if trigger == "BOOKING_CANCELLED":
        LOGGER.info("Booking cancelled for %s", attendee_email)
        return JSONResponse({"status": "cancellation_logged"})

    return JSONResponse({"status": "event_logged", "trigger": trigger})


# ─────────────────────────────────────────────────────────────
# HubSpot — CRM contact events
# ─────────────────────────────────────────────────────────────

@app.post("/webhooks/hubspot", tags=["webhooks"])
async def hubspot_webhook(request: Request) -> JSONResponse:
    """
    Receives contact lifecycle and property-change events from HubSpot.

    Register at: app.hubspot.com/developer → Webhooks → Create subscription
    Subscriptions: contact.propertyChange, contact.creation
    """
    body = await request.body()
    events = await request.json()

    if not isinstance(events, list):
        events = [events]

    for event in events:
        event_type = event.get("subscriptionType", "unknown")
        contact_id = event.get("objectId")
        LOGGER.info("HubSpot event: type=%s contact_id=%s", event_type, contact_id)
        _log_event("hubspot", event_type, event)

    return JSONResponse({"status": "events_logged", "count": len(events)})


# ─────────────────────────────────────────────────────────────
# Local dev entrypoint
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("WEBHOOK_PORT", 8000))
    uvicorn.run("agent.webhook:app", host="0.0.0.0", port=port, reload=True)
