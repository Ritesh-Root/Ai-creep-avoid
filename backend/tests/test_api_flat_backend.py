"""Tests for the FastAPI endpoints."""

import io

import pytest
from fastapi.testclient import TestClient

from backend.main import app, tracker


@pytest.fixture(autouse=True)
def _reset_tracker():
    """Reset the behavioral tracker between tests."""
    tracker._counters.clear()
    yield
    tracker._counters.clear()


client = TestClient(app)


class TestHealthCheck:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


class TestAnalyzeText:
    def test_safe_message(self):
        resp = client.post(
            "/analyze/text",
            json={"sender_id": "u1", "receiver_id": "u2", "text": "Hello, how are you?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert 0.0 <= data["creep_score"] <= 1.0
        assert data["action"] in ("allow", "blur", "block")
        assert "reason" in data

    def test_response_includes_behavioral_penalty(self):
        # Send multiple messages to accumulate behavioral penalty
        for _ in range(5):
            resp = client.post(
                "/analyze/text",
                json={"sender_id": "u1", "receiver_id": "u2", "text": "hey"},
            )
        data = resp.json()
        assert data["behavioral_penalty"] > 0.0

    def test_creep_score_increases_with_flooding(self):
        """Sending many unanswered messages should increase the creep score."""
        scores = []
        for i in range(12):
            resp = client.post(
                "/analyze/text",
                json={"sender_id": "u1", "receiver_id": "u2", "text": "hi"},
            )
            scores.append(resp.json()["creep_score"])
        # Score should generally increase
        assert scores[-1] >= scores[0]

    def test_missing_fields_returns_422(self):
        resp = client.post("/analyze/text", json={"sender_id": "u1"})
        assert resp.status_code == 422


class TestAnalyzeImage:
    def test_upload_image(self):
        # Create a minimal valid PNG image
        from PIL import Image

        img = Image.new("RGB", (10, 10), color="red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        resp = client.post(
            "/analyze/image",
            data={"sender_id": "u1", "receiver_id": "u2"},
            files={"file": ("test.png", buf, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert 0.0 <= data["creep_score"] <= 1.0
        assert data["action"] in ("allow", "blur", "block")


class TestReply:
    def test_reply_resets_counter(self):
        # Build up a count
        for _ in range(5):
            client.post(
                "/analyze/text",
                json={"sender_id": "u1", "receiver_id": "u2", "text": "hey"},
            )

        # Record a reply
        resp = client.post(
            "/reply",
            json={"sender_id": "u1", "receiver_id": "u2"},
        )
        assert resp.status_code == 200

        # Next message should show lower behavioral penalty
        resp = client.post(
            "/analyze/text",
            json={"sender_id": "u1", "receiver_id": "u2", "text": "hey again"},
        )
        data = resp.json()
        assert data["behavioral_penalty"] <= 0.1


class TestReset:
    def test_reset_tracking(self):
        for _ in range(5):
            client.post(
                "/analyze/text",
                json={"sender_id": "u1", "receiver_id": "u2", "text": "hey"},
            )

        resp = client.post(
            "/reset",
            json={"sender_id": "u1", "receiver_id": "u2"},
        )
        assert resp.status_code == 200

        resp = client.post(
            "/analyze/text",
            json={"sender_id": "u1", "receiver_id": "u2", "text": "hello"},
        )
        data = resp.json()
        assert data["behavioral_penalty"] <= 0.1
