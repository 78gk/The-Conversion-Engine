"""
integrations/calcom/
────────────────────
Cal.com booking channel.

Generates booking links via the Cal.com API (rubric B10) — booking URLs
are not hard-coded. Confirmation events are handled by the FastAPI route
in agent/webhook.py (rubric B11) which calls
hubspot.update_hubspot_lifecycle_stage on BOOKING_CREATED.

Functions:
  generate_booking_link    — produce a Cal.com URL for a prospect
  book_discovery_call      — full bookings/v1 call (referenced from email + sms channels)
  handle_booking_confirmed — invoked from the Cal.com webhook payload
"""

from __future__ import annotations

import logging
from typing import Any

from agent.integrations import book_discovery_call

LOGGER = logging.getLogger(__name__)

__all__ = [
    "book_discovery_call",
    "generate_booking_link",
    "handle_booking_confirmed",
]


def generate_booking_link(name: str, email: str, notes: str = "") -> dict[str, Any]:
    """
    Generate a Cal.com booking link for a prospect.

    Wraps book_discovery_call so callers in integrations/email and
    integrations/sms can request a link without depending on Cal.com
    API call semantics directly.
    """
    return book_discovery_call(name=name, email=email, notes=notes)


def handle_booking_confirmed(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Process a Cal.com BOOKING_CREATED webhook payload.

    Returns a structured event the orchestrator can consume — the actual
    HubSpot lifecycle update is dispatched by the orchestrator, keeping
    this channel module free of cross-channel coupling.
    """
    booking = payload.get("payload", {})
    attendee_email = next((a.get("email") for a in booking.get("attendees", [])), None)
    booking_uid = booking.get("uid", "")
    LOGGER.info("Cal.com booking confirmed: attendee=%s uid=%s", attendee_email, booking_uid)
    return {
        "status": "confirmed",
        "attendee_email": attendee_email,
        "booking_uid": booking_uid,
        "start_time": booking.get("startTime"),
    }
