"""tests/test_webhook.py
Tests for the FastAPI webhook server (agent/webhook.py).
Uses FastAPI's TestClient — no real HTTP server needed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from agent.webhook import app

client = TestClient(app)


class TestHealthCheck:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_includes_service_name(self):
        response = client.get("/health")
        assert "conversion-engine" in response.json()["service"]

    def test_health_includes_timestamp(self):
        response = client.get("/health")
        assert "timestamp" in response.json()

    def test_root_returns_version(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "version" in response.json()


class TestResendWebhook:
    def test_email_opened_event_logged(self):
        payload = {
            "type": "email.opened",
            "data": {"to": ["prospect@example.com"], "from": "sender@tenacious.co"},
        }
        response = client.post("/webhooks/resend", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "event_logged"

    def test_email_replied_triggers_reply_received(self):
        payload = {
            "type": "email.replied",
            "data": {
                "to": ["outreach@tenacious.co"],
                "from": "alex@synthco.example.com",
            },
        }
        response = client.post("/webhooks/resend", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "reply_received"
        assert "alex@synthco.example.com" in response.json()["prospect"]

    def test_email_bounced_logs_bounce(self):
        payload = {
            "type": "email.bounced",
            "data": {"to": ["invalid@nonexistent.example"]},
        }
        response = client.post("/webhooks/resend", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "bounce_logged"

    def test_unknown_event_type_logged(self):
        payload = {"type": "email.complained", "data": {}}
        response = client.post("/webhooks/resend", json=payload)
        assert response.status_code == 200
        assert "event_logged" in response.json()["status"]


class TestAfricasTalkingWebhook:
    def test_sms_inbound_logged(self):
        form_data = {
            "from": "+254700000001",
            "to": "+254700000002",
            "text": "Yes I am interested",
            "date": "2026-04-23 13:00:00",
        }
        response = client.post(
            "/webhooks/africas-talking",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "inbound_logged"
        assert "+254700000001" in response.json()["from"]

    def test_sms_delivery_report_logged(self):
        form_data = {
            "to": "+254700000001",
            "status": "Success",
            "networkCode": "63902",
            "cost": "KES 1.0000",
        }
        response = client.post(
            "/webhooks/africas-talking",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "delivery_logged"


class TestCalcomWebhook:
    def test_booking_created_logged(self):
        payload = {
            "triggerEvent": "BOOKING_CREATED",
            "payload": {
                "startTime": "2026-04-25T10:00:00Z",
                "attendees": [{"email": "alex@synthco.example.com", "name": "Alex Rivera"}],
            },
        }
        response = client.post("/webhooks/calcom", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "booking_logged"
        assert "alex@synthco.example.com" in response.json()["attendee"]

    def test_booking_cancelled_logged(self):
        payload = {
            "triggerEvent": "BOOKING_CANCELLED",
            "payload": {
                "attendees": [{"email": "alex@synthco.example.com"}],
            },
        }
        response = client.post("/webhooks/calcom", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "cancellation_logged"


class TestHubspotWebhook:
    def test_single_event_processed(self):
        payload = [
            {
                "subscriptionType": "contact.propertyChange",
                "objectId": 12345,
                "propertyName": "email",
                "propertyValue": "alex@synthco.example.com",
            }
        ]
        response = client.post("/webhooks/hubspot", json=payload)
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_multiple_events_processed(self):
        payload = [
            {"subscriptionType": "contact.creation", "objectId": 1},
            {"subscriptionType": "contact.propertyChange", "objectId": 2},
        ]
        response = client.post("/webhooks/hubspot", json=payload)
        assert response.status_code == 200
        assert response.json()["count"] == 2
