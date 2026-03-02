"""
API routes for SmartShield AI.

Endpoints
---------
POST /api/v1/analyze        – analyze a text message or image
POST /api/v1/reply          – record that the recipient replied (resets unanswered streak)
DELETE /api/v1/session/{id} – explicitly expire a session (privacy control)
GET  /api/v1/health         – liveness check
"""

from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from app.models.behavioral_tracker import BehavioralTracker
from app.models.creep_score import compute_behavior_score, compute_creep_score
from app.models.image_analyzer import ImageAnalyzer
from app.models.text_analyzer import TextAnalyzer
from app.utils.explainer import build_reasons
from app.utils.privacy import SessionStore, hash_sender_id

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class TextAnalyzeRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4096, description="Text message to analyze")
    sender_id: str = Field(..., description="Sender identifier (will be hashed before storage)")
    session_id: str | None = Field(None, description="Session ID; auto-generated if omitted")
    has_reply: bool = Field(False, description="True if this message is a reply from the recipient")


class AnalyzeResponse(BaseModel):
    session_id: str
    creep_score: float
    disposition: str
    text_score: float
    image_score: float
    behavior_score: float
    reasons: list[str]
    categories: list[str]
    processing_time_ms: float


class ReplyRequest(BaseModel):
    session_id: str
    sender_id: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_components(request: Request) -> tuple[TextAnalyzer, ImageAnalyzer, BehavioralTracker, SessionStore]:
    return (
        request.app.state.text_analyzer,
        request.app.state.image_analyzer,
        request.app.state.behavioral_tracker,
        request.app.state.session_store,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/analyze/text", response_model=AnalyzeResponse)
async def analyze_text(body: TextAnalyzeRequest, request: Request) -> AnalyzeResponse:
    """Analyze a text message and return a Creep Score with XAI reasoning."""
    t0 = time.perf_counter()
    text_analyzer, _, behavioral_tracker, _ = _get_components(request)

    session_id = body.session_id or str(uuid.uuid4())
    sender_hash = hash_sender_id(body.sender_id)

    # 1. Text analysis
    text_result = text_analyzer.analyze(body.content)

    # 2. Behavioral tracking
    signals = behavioral_tracker.record_message(
        session_id=session_id,
        sender_hash=sender_hash,
        toxicity_score=text_result.score,
        keyword_alarm=text_result.keyword_alarm,
        has_reply=body.has_reply,
    )

    # 3. Compute scores
    behavior_score = compute_behavior_score(signals)
    score_result = compute_creep_score(
        text_score=text_result.score,
        image_score=0.0,
        behavior_score=behavior_score,
    )

    # 4. XAI reasons
    behavior_dict = {
        "flood_rate": signals.flood_rate,
        "unanswered_streak": signals.unanswered_streak,
        "odd_hour": signals.odd_hour,
        "escalation_rate": signals.escalation_rate,
        "keyword_alarm": signals.keyword_alarm,
        "total_messages": signals.total_messages,
        "messages_per_minute": signals.messages_per_minute,
    }
    reasons = build_reasons(
        text_score=text_result.score,
        text_categories=text_result.categories,
        image_score=0.0,
        image_categories=[],
        behavior=behavior_dict,
        creep_score=score_result.creep_score,
    )

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return AnalyzeResponse(
        session_id=session_id,
        creep_score=score_result.creep_score,
        disposition=score_result.disposition.value,
        text_score=score_result.text_score,
        image_score=score_result.image_score,
        behavior_score=score_result.behavior_score,
        reasons=reasons,
        categories=text_result.categories,
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post("/analyze/image", response_model=AnalyzeResponse)
async def analyze_image(
    request: Request,
    session_id: str = Form(...),
    sender_id: str = Form(...),
    file: UploadFile = File(...),
) -> AnalyzeResponse:
    """Analyze an uploaded image for NSFW content and return a Creep Score."""
    t0 = time.perf_counter()
    _, image_analyzer, behavioral_tracker, _ = _get_components(request)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    sender_hash = hash_sender_id(sender_id)
    image_bytes = await file.read()

    # 1. Image analysis
    image_result = image_analyzer.analyze_bytes(image_bytes, file.content_type)

    # 2. Behavioral tracking (image send counts as a message)
    signals = behavioral_tracker.record_message(
        session_id=session_id,
        sender_hash=sender_hash,
        toxicity_score=image_result.score,
        keyword_alarm=False,
    )

    # 3. Compute scores
    behavior_score = compute_behavior_score(signals)
    score_result = compute_creep_score(
        text_score=0.0,
        image_score=image_result.score,
        behavior_score=behavior_score,
    )

    # 4. XAI reasons
    behavior_dict = {
        "flood_rate": signals.flood_rate,
        "unanswered_streak": signals.unanswered_streak,
        "odd_hour": signals.odd_hour,
        "escalation_rate": signals.escalation_rate,
        "keyword_alarm": signals.keyword_alarm,
        "total_messages": signals.total_messages,
        "messages_per_minute": signals.messages_per_minute,
    }
    reasons = build_reasons(
        text_score=0.0,
        text_categories=[],
        image_score=image_result.score,
        image_categories=image_result.categories,
        behavior=behavior_dict,
        creep_score=score_result.creep_score,
    )

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return AnalyzeResponse(
        session_id=session_id,
        creep_score=score_result.creep_score,
        disposition=score_result.disposition.value,
        text_score=score_result.text_score,
        image_score=score_result.image_score,
        behavior_score=score_result.behavior_score,
        reasons=reasons,
        categories=image_result.categories,
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post("/reply")
async def record_reply(body: ReplyRequest, request: Request) -> dict:
    """Record that the recipient replied, resetting the unanswered message streak."""
    _, _, behavioral_tracker, _ = _get_components(request)
    sender_hash = hash_sender_id(body.sender_id)
    behavioral_tracker.record_reply(session_id=body.session_id, sender_hash=sender_hash)
    return {"status": "ok", "message": "Reply recorded; unanswered streak reset."}


@router.delete("/session/{session_id}")
async def delete_session(session_id: str, request: Request) -> dict:
    """Immediately expire/delete all data for a session (privacy control)."""
    _, _, _, session_store = _get_components(request)
    session_store.delete(session_id)
    return {"status": "ok", "message": f"Session '{session_id}' data deleted."}


@router.get("/health")
async def health() -> dict:
    """Liveness check."""
    return {"status": "ok", "service": "SmartShield AI"}
