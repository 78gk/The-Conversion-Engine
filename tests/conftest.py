"""tests/conftest.py — Shared fixtures for the Conversion Engine test suite."""

from __future__ import annotations

import os
import pytest

@pytest.fixture(autouse=True)
def sandbox_env(monkeypatch):
    """Force sandbox mode for all tests — prevents any live API calls."""
    monkeypatch.setenv("OUTBOUND_LIVE", "false")
    monkeypatch.setenv("AT_SANDBOX", "true")
    monkeypatch.setenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    monkeypatch.setenv("RESEND_FROM_NAME", "Test Sender")
    monkeypatch.setenv("STAFF_SINK_EMAIL", "test-sink@tenacious.test")
