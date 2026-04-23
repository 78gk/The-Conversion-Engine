"""tests/test_integrations.py
Tests for the agent/integrations.py layer.
All tests run in sandbox mode (OUTBOUND_LIVE=false) — no live API calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.integrations import (
    book_discovery_call,
    send_email,
    send_sms,
    write_hubspot_contact,
)


class TestSendEmail:
    def test_sandbox_returns_sandboxed_status(self):
        result = send_email(
            to="prospect@example.com",
            subject="Test Subject",
            body_html="<p>Hello</p>",
        )
        assert result["status"] == "sandboxed"
        assert result["channel"] == "resend_email"

    def test_sandbox_routes_to_staff_sink(self, monkeypatch):
        monkeypatch.setenv("STAFF_SINK_EMAIL", "sink@tenacious.test")
        result = send_email(
            to="prospect@example.com",
            subject="Test Subject",
            body_html="<p>Hello</p>",
        )
        assert "sink@tenacious.test" in str(result["payload"]["to"])

    def test_from_name_in_payload(self, monkeypatch):
        monkeypatch.setenv("RESEND_FROM_NAME", "My Name")
        result = send_email(
            to="p@example.com",
            subject="S",
            body_html="B",
        )
        assert "My Name" in result["payload"]["from"]

    def test_custom_from_name_override(self):
        result = send_email(
            to="p@example.com",
            subject="S",
            body_html="B",
            from_name="Override Name",
        )
        assert "Override Name" in result["payload"]["from"]

    def test_subject_preserved_in_payload(self):
        result = send_email(
            to="p@example.com",
            subject="Unique Subject 12345",
            body_html="B",
        )
        assert result["payload"]["subject"] == "Unique Subject 12345"

    def test_html_body_preserved(self):
        html = "<p>Rich content here</p>"
        result = send_email(to="p@example.com", subject="S", body_html=html)
        assert result["payload"]["html"] == html


class TestSendSms:
    def test_sandbox_returns_sandboxed_status(self):
        result = send_sms(to="+254700000001", message="Test message")
        assert result["status"] == "sandboxed"
        assert result["channel"] == "africas_talking_sms"

    def test_payload_contains_message(self):
        result = send_sms(to="+254700000001", message="Hello prospect")
        assert result["payload"]["message"] == "Hello prospect"

    def test_payload_contains_recipient(self):
        result = send_sms(to="+254700000002", message="Hi")
        assert result["payload"]["to"] == "+254700000002"

    def test_sandbox_flag_in_payload(self, monkeypatch):
        monkeypatch.setenv("AT_SANDBOX", "true")
        result = send_sms(to="+254700000001", message="Test")
        assert result["payload"]["sandbox"] is True


class TestWriteHubspotContact:
    def test_sandbox_returns_sandboxed_status(self):
        result = write_hubspot_contact(
            email="alex@synthco.test",
            first_name="Alex",
            last_name="Rivera",
            company="SynthCo Inc.",
            icp_segment=3,
            ai_maturity_score=2.0,
            primary_signal="New CTO",
        )
        assert result["status"] == "sandboxed"
        assert result["channel"] == "hubspot_contact_write"

    def test_properties_in_payload(self):
        result = write_hubspot_contact(
            email="test@company.test",
            first_name="John",
            last_name="Doe",
            company="AcmeCo",
            icp_segment=2,
            ai_maturity_score=1.5,
            primary_signal="Funding signal",
        )
        props = result["payload"]["properties"]
        assert props["email"] == "test@company.test"
        assert props["icp_segment"] == "2"
        assert props["ai_maturity_score"] == "1.5"

    def test_enrichment_timestamp_present(self):
        result = write_hubspot_contact(
            email="ts@test.com",
            first_name="A",
            last_name="B",
            company="C",
            icp_segment=1,
            ai_maturity_score=1.0,
            primary_signal="test",
        )
        props = result["payload"]["properties"]
        assert "enrichment_timestamp" in props
        assert props["enrichment_timestamp"].endswith("Z")


class TestBookDiscoveryCall:
    def test_sandbox_returns_sandboxed_status(self):
        result = book_discovery_call(
            name="Alex Rivera",
            email="alex@synthco.test",
            notes="ICP Segment 3",
        )
        assert result["status"] == "sandboxed"
        assert result["channel"] == "calcom_booking"

    def test_mock_booking_url_present_in_sandbox(self):
        result = book_discovery_call(
            name="Test User",
            email="test@example.com",
        )
        assert "mock_booking_url" in result["payload"]
        assert "test@example.com" in result["payload"]["mock_booking_url"]

    def test_name_and_email_in_payload(self):
        result = book_discovery_call(
            name="Jane Smith",
            email="jane@test.com",
            notes="Important prospect",
        )
        payload = result["payload"]
        assert payload["name"] == "Jane Smith"
        assert payload["email"] == "jane@test.com"
        assert payload["notes"] == "Important prospect"
