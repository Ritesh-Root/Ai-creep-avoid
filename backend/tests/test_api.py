"""Integration tests for the FastAPI routes (mock models, no GPU needed)."""

import os
os.environ["USE_MOCK_MODELS"] = "true"

import io
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from PIL import Image

from app.main import app


@pytest_asyncio.fixture(scope="module")
async def client():
    from app.models.text_analyzer import TextAnalyzer
    from app.models.image_analyzer import ImageAnalyzer
    from app.models.behavioral_tracker import BehavioralTracker
    from app.utils.privacy import SessionStore

    # Manually initialize app state (lifespan is not triggered by ASGITransport in tests)
    session_store = SessionStore()
    app.state.text_analyzer = TextAnalyzer()
    app.state.image_analyzer = ImageAnalyzer()
    app.state.session_store = session_store
    app.state.behavioral_tracker = BehavioralTracker(session_store=session_store)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.state.session_store.clear_all()


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_analyze_text_clean_message(client):
    payload = {
        "content": "Hey! How are you doing today?",
        "sender_id": "user1",
        "session_id": "sess_test_1",
    }
    response = await client.post("/api/v1/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "creep_score" in data
    assert "disposition" in data
    assert data["creep_score"] < 0.50
    assert data["disposition"] in ("ALLOW", "WARN")


@pytest.mark.asyncio
async def test_analyze_text_threatening_message(client):
    payload = {
        "content": "I know where you live and you'll regret this",
        "sender_id": "user_bad",
        "session_id": "sess_test_2",
    }
    response = await client.post("/api/v1/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["creep_score"] >= 0.40
    assert data["disposition"] in ("WARN", "BLUR", "BLOCK")
    assert len(data["reasons"]) > 0


@pytest.mark.asyncio
async def test_analyze_text_returns_session_id(client):
    payload = {
        "content": "Hello",
        "sender_id": "user2",
    }
    response = await client.post("/api/v1/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


@pytest.mark.asyncio
async def test_analyze_text_flood_behavior(client):
    """Sending many rapid messages should raise the behavior score."""
    session_id = "sess_flood_test"
    last_score = 0.0
    for i in range(8):
        payload = {
            "content": "Hey",
            "sender_id": "flood_user",
            "session_id": session_id,
        }
        response = await client.post("/api/v1/analyze/text", json=payload)
        assert response.status_code == 200
        last_score = response.json()["behavior_score"]
    assert last_score > 0.0, "Flood behavior should raise behavior score"


@pytest.mark.asyncio
async def test_analyze_image_blue(client):
    """A plain blue image should get a low NSFW score."""
    img = Image.new("RGB", (100, 100), color=(0, 0, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = await client.post(
        "/api/v1/analyze/image",
        data={"session_id": "sess_img_1", "sender_id": "img_user"},
        files={"file": ("test.jpg", buf, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["image_score"] < 0.40


@pytest.mark.asyncio
async def test_analyze_image_invalid_file_type(client):
    response = await client.post(
        "/api/v1/analyze/image",
        data={"session_id": "sess_img_2", "sender_id": "img_user2"},
        files={"file": ("test.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_record_reply(client):
    response = await client.post(
        "/api/v1/reply",
        json={"session_id": "sess_reply_1", "sender_id": "reply_user"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_delete_session(client):
    response = await client.delete("/api/v1/session/sess_to_delete")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_processing_time_present(client):
    payload = {
        "content": "Hello world",
        "sender_id": "timer_user",
        "session_id": "sess_timer",
    }
    response = await client.post("/api/v1/analyze/text", json=payload)
    data = response.json()
    assert "processing_time_ms" in data
    assert data["processing_time_ms"] >= 0
