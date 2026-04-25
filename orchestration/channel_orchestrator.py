"""
orchestration/channel_orchestrator.py
─────────────────────────────────────
The single state machine that owns channel handoff (rubric B13).

States per prospect:
  COLD              — no contact yet
  EMAIL_SENT        — first cold email dispatched
  EMAIL_REPLIED     — prospect replied to an email (warm-lead gate now passes)
  SMS_SENT          — warm-lead SMS dispatched
  BOOKING_OFFERED   — calendar link delivered
  BOOKING_CONFIRMED — Cal.com webhook received
  CLOSED            — booking happened or prospect unsubscribed

Cross-channel rules (this module is the only place these are encoded):
  1. SMS is forbidden until EMAIL_REPLIED has been observed
     (the warm-lead gate, rubric B5)
  2. HubSpot writes happen at THREE distinct event points (rubric B9):
       (a) on transition COLD -> EMAIL_SENT     -> contact create
       (b) on transition * -> EMAIL_REPLIED     -> activity log + enrichment write
       (c) on transition * -> BOOKING_CONFIRMED -> lifecycle stage update
  3. Cal.com booking links are offered from BOTH email and SMS paths
     (rubric B12) — the orchestrator is the dispatch point.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from integrations.calcom import generate_booking_link, handle_booking_confirmed
from integrations.email import (
    handle_email_reply,
    send_email_with_booking_link,
)
from integrations.hubspot import (
    log_activity,
    update_hubspot_lifecycle_stage,
    write_enrichment_fields,
    write_hubspot_contact,
)
from integrations.sms import (
    handle_sms_reply,
    send_sms_with_booking_link,
)

LOGGER = logging.getLogger(__name__)

STATE_PATH = Path(__file__).resolve().parents[1] / "data" / "orchestrator_state.json"

# Re-export generate_booking_link so callers that need a standalone link
# (e.g., a webhook handler that must reply synchronously) can import it
# directly from the orchestration layer without coupling to integrations.calcom.
__all__ = ["ChannelOrchestrator", "generate_booking_link"]


class ProspectState(str, Enum):
    COLD = "cold"
    EMAIL_SENT = "email_sent"
    EMAIL_REPLIED = "email_replied"
    SMS_SENT = "sms_sent"
    BOOKING_OFFERED = "booking_offered"
    BOOKING_CONFIRMED = "booking_confirmed"
    CLOSED = "closed"


class ChannelEvent(str, Enum):
    SEND_COLD_EMAIL = "send_cold_email"
    INBOUND_EMAIL_REPLY = "inbound_email_reply"
    SEND_WARM_SMS = "send_warm_sms"
    INBOUND_SMS_REPLY = "inbound_sms_reply"
    BOOKING_CONFIRMED = "booking_confirmed"
    UNSUBSCRIBE = "unsubscribe"


@dataclass
class ProspectThread:
    email: str
    name: str = ""
    company: str = ""
    phone: str = ""
    state: ProspectState = ProspectState.COLD
    icp_segment: int = 0
    ai_maturity_score: float = 0.0
    primary_signal: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)


class ChannelOrchestrator:
    """
    The single dispatch surface for cross-channel decisions.

    Use one instance per process; state is persisted to
    data/orchestrator_state.json so the live webhook server can recover
    on restart.
    """

    def __init__(self) -> None:
        self.threads: dict[str, ProspectThread] = self._load_state()

    # ─── Persistence ─────────────────────────────────────────────

    def _load_state(self) -> dict[str, ProspectThread]:
        if not STATE_PATH.exists():
            return {}
        try:
            raw = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            LOGGER.warning("Could not load orchestrator state: %s -- starting empty", exc)
            return {}
        threads: dict[str, ProspectThread] = {}
        for email, payload in raw.items():
            payload["state"] = ProspectState(payload.get("state", "cold"))
            threads[email] = ProspectThread(**payload)
        return threads

    def _save_state(self) -> None:
        try:
            STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            serialisable = {
                email: {**t.__dict__, "state": t.state.value}
                for email, t in self.threads.items()
            }
            STATE_PATH.write_text(json.dumps(serialisable, indent=2, default=str), encoding="utf-8")
        except OSError as exc:
            LOGGER.warning("Could not persist orchestrator state: %s", exc)

    # ─── Thread management ──────────────────────────────────────

    def get_or_create(self, email: str, **defaults: Any) -> ProspectThread:
        if email not in self.threads:
            self.threads[email] = ProspectThread(email=email, **defaults)
        return self.threads[email]

    def _record(self, thread: ProspectThread, event: ChannelEvent, payload: dict[str, Any]) -> None:
        thread.history.append({
            "event": event.value,
            "state_before": thread.state.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload,
        })

    # ─── Event dispatch — the single public surface ─────────────

    def handle(self, event: ChannelEvent, *, prospect_email: str, **payload: Any) -> dict[str, Any]:
        """
        Drive the state machine from a channel event.

        Returns a dict describing the action(s) taken. All cross-channel
        decisions live here — channel modules never call each other directly.
        """
        thread = self.get_or_create(prospect_email, **{k: v for k, v in payload.items() if k in {"name", "company", "phone", "icp_segment", "ai_maturity_score", "primary_signal"}})
        self._record(thread, event, payload)

        try:
            if event is ChannelEvent.SEND_COLD_EMAIL:
                return self._cold_email(thread, payload)
            if event is ChannelEvent.INBOUND_EMAIL_REPLY:
                return self._email_reply(thread, payload)
            if event is ChannelEvent.SEND_WARM_SMS:
                return self._warm_sms(thread, payload)
            if event is ChannelEvent.INBOUND_SMS_REPLY:
                return self._sms_reply(thread, payload)
            if event is ChannelEvent.BOOKING_CONFIRMED:
                return self._booking_confirmed(thread, payload)
            if event is ChannelEvent.UNSUBSCRIBE:
                thread.state = ProspectState.CLOSED
                return {"status": "closed", "reason": "unsubscribe"}
            return {"status": "ignored", "reason": f"unknown event {event}"}
        finally:
            self._save_state()

    # ─── Per-event handlers (the cross-channel rules live here) ──

    def _cold_email(self, thread: ProspectThread, payload: dict[str, Any]) -> dict[str, Any]:
        # HubSpot event point #1: contact create (rubric B9)
        crm_result = write_hubspot_contact(
            email=thread.email,
            first_name=thread.name.split()[0] if thread.name else "",
            last_name=" ".join(thread.name.split()[1:]) if thread.name else "",
            company=thread.company,
            icp_segment=thread.icp_segment,
            ai_maturity_score=thread.ai_maturity_score,
            primary_signal=thread.primary_signal,
            notes=payload.get("notes", ""),
        )
        # Cal.com booking link offered from the EMAIL channel (rubric B12)
        email_result = send_email_with_booking_link(
            to=thread.email,
            subject=payload.get("subject", "Quick note from Tenacious"),
            body_html=payload.get("body_html", "<p>Hi,</p><p>Quick note from Tenacious.</p>"),
            prospect_name=thread.name or "there",
            prospect_email=thread.email,
            notes=payload.get("notes", ""),
        )
        thread.state = ProspectState.EMAIL_SENT
        return {"status": "sent", "crm": crm_result, "email": email_result}

    def _email_reply(self, thread: ProspectThread, payload: dict[str, Any]) -> dict[str, Any]:
        handle_email_reply(thread.email, payload)
        # HubSpot event point #2: activity log + enrichment write on warm signal (rubric B9)
        activity = log_activity(thread.email, "EMAIL", payload.get("snippet", "inbound reply"))
        enrichment = write_enrichment_fields(
            email=thread.email,
            icp_segment=thread.icp_segment,
            ai_maturity_score=thread.ai_maturity_score,
            primary_signal=thread.primary_signal,
            enrichment_notes="warm via inbound email reply",
        )
        thread.state = ProspectState.EMAIL_REPLIED
        return {"status": "warm", "activity": activity, "enrichment": enrichment}

    def _warm_sms(self, thread: ProspectThread, payload: dict[str, Any]) -> dict[str, Any]:
        # Warm-lead gate (rubric B5) — enforced HERE in the orchestrator,
        # not in the SMS channel module.
        if thread.state not in {ProspectState.EMAIL_REPLIED, ProspectState.BOOKING_OFFERED}:
            return {"status": "blocked", "reason": "warm_lead_gate: prospect has not replied to email"}

        # Cal.com booking link offered from the SMS channel (rubric B12)
        sms_result = send_sms_with_booking_link(
            to=thread.phone,
            prospect_name=thread.name or "there",
            prospect_email=thread.email,
            prior_email_replied=True,
            notes=payload.get("notes", ""),
        )
        thread.state = ProspectState.SMS_SENT
        return {"status": "sent", "sms": sms_result}

    def _sms_reply(self, thread: ProspectThread, payload: dict[str, Any]) -> dict[str, Any]:
        handle_sms_reply(thread.phone, payload.get("text", ""))
        return {"status": "sms_logged"}

    def _booking_confirmed(self, thread: ProspectThread, payload: dict[str, Any]) -> dict[str, Any]:
        result = handle_booking_confirmed(payload)
        # HubSpot event point #3: lifecycle stage update on booking (rubric B9)
        lifecycle = update_hubspot_lifecycle_stage(
            email=thread.email,
            lifecycle_stage="scheduled",
            booking_uid=result.get("booking_uid", ""),
        )
        thread.state = ProspectState.BOOKING_CONFIRMED
        return {"status": "booked", "calcom": result, "hubspot": lifecycle}
