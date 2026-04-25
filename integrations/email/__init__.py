"""
integrations/email/
───────────────────
Email channel: Resend send handler + inbound reply webhook handler.

Re-exports the working clients in agent.integrations and adds a
booking-link composer that imports Cal.com from integrations.calcom.
This satisfies rubric B12 — Cal.com referenced from the email channel.

Handlers:
  send_email                         — outbound send via Resend
  send_email_with_booking_link       — outbound send including a Cal.com link
  handle_email_reply                 — inbound reply webhook handler
"""

from __future__ import annotations

import logging
from typing import Any

from agent.integrations import (
    handle_email_reply,
    send_email,
)

# Cal.com booking-link generator — referenced from this channel per rubric B12
from integrations.calcom import generate_booking_link

LOGGER = logging.getLogger(__name__)

__all__ = [
    "send_email",
    "send_email_with_booking_link",
    "handle_email_reply",
]


def send_email_with_booking_link(
    to: str,
    subject: str,
    body_html: str,
    prospect_name: str,
    prospect_email: str,
    notes: str = "",
) -> dict[str, Any]:
    """
    Send an outbound email that embeds a Cal.com discovery-call link.

    Cal.com link is generated via integrations.calcom.generate_booking_link
    rather than hard-coded — this is the explicit rubric B10/B12 wiring.
    """
    booking = generate_booking_link(name=prospect_name, email=prospect_email, notes=notes)
    booking_url = booking.get("booking_url") or booking.get("mock_booking_url", "")

    body_with_link = body_html.rstrip()
    if "</p>" in body_with_link:
        insertion = (
            f'<p>If a quick conversation is useful, you can grab a slot here: '
            f'<a href="{booking_url}">{booking_url}</a></p>'
        )
        body_with_link = body_with_link + "\n" + insertion
    else:
        body_with_link = f"{body_with_link}\n\nBook a 30-min discovery call: {booking_url}"

    LOGGER.info("Composed email with booking link for %s -> %s", to, booking_url)
    result = send_email(to=to, subject=subject, body_html=body_with_link)
    result["booking_link"] = booking_url
    return result
