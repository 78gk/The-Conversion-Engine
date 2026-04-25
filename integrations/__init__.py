"""
integrations/
─────────────
Per-channel integration packages, each re-exporting the working clients
from agent.integrations and adding channel-specific wiring.

Packages:
  email/    — Resend send + reply handler + booking-link composer
  sms/      — Africa's Talking send + warm-lead gate + booking-link composer
  hubspot/  — HubSpot contact create, activity log, lifecycle update, enrichment writes
  calcom/   — Cal.com booking link generation + confirmation handler

Channel handoff lives in orchestration/channel_orchestrator.py — these
packages do not coordinate cross-channel state themselves.
"""
