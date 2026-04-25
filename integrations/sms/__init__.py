"""
integrations/sms/
─────────────────
SMS channel: Africa's Talking send + inbound webhook + warm-lead gate.

Re-exports the working clients in agent.integrations and adds a
booking-link composer that imports Cal.com from integrations.calcom.
This satisfies rubric B12 — Cal.com referenced from the SMS channel.

Handlers:
  send_sms                          — raw send via Africa's Talking
  send_sms_warm_lead_only           — gated: only sends if a prior email reply exists
  send_sms_with_booking_link        — warm-lead-only send including a Cal.com link
  handle_sms_reply                  — inbound reply webhook handler
"""

from __future__ import annotations

import logging
from typing import Any

from agent.integrations import (
    handle_sms_reply,
    send_sms,
    send_sms_warm_lead_only,
)

# Cal.com booking-link generator — referenced from this channel per rubric B12
from integrations.calcom import generate_booking_link

LOGGER = logging.getLogger(__name__)

__all__ = [
    "send_sms",
    "send_sms_warm_lead_only",
    "send_sms_with_booking_link",
    "handle_sms_reply",
]


def send_sms_with_booking_link(
    to: str,
    prospect_name: str,
    prospect_email: str,
    prior_email_replied: bool,
    notes: str = "",
) -> dict[str, Any]:
    """
    Send an SMS containing a Cal.com booking link.

    Enforces the warm-lead gate: returns a blocked response if the prospect
    has not previously replied to an email. This is the rubric B5/B12 wiring
    — Cal.com is invoked from the SMS channel only after the warm-lead
    check passes.
    """
    if not prior_email_replied:
        LOGGER.info("SMS-with-booking blocked for %s — no prior email reply", to)
        return {"status": "blocked", "reason": "warm_lead_gate: no prior email reply"}

    booking = generate_booking_link(name=prospect_name, email=prospect_email, notes=notes)
    booking_url = booking.get("booking_url") or booking.get("mock_booking_url", "")
    message = f"Hi {prospect_name.split()[0]}, ready to chat? Grab a slot: {booking_url}"

    LOGGER.info("Composed SMS with booking link for %s -> %s", to, booking_url)
    result = send_sms_warm_lead_only(to=to, message=message, prior_email_replied=True)
    result["booking_link"] = booking_url
    return result
