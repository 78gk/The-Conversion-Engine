"""
orchestration/
──────────────
Centralized channel-handoff state machine (rubric B13).

All cross-channel decisions — when to send an SMS, when to write to
HubSpot, when to book a Cal.com slot — live here. Channel modules
(integrations.email, integrations.sms, integrations.hubspot,
integrations.calcom) call out to their underlying APIs but never
coordinate with each other directly. The orchestrator is the single
point of cross-channel state.
"""

from orchestration.channel_orchestrator import ChannelOrchestrator, ChannelEvent

__all__ = ["ChannelOrchestrator", "ChannelEvent"]
