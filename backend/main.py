"""SmartShield AI – FastAPI Backend.

A proactive, privacy-first digital boundary enforcement system.
Analyzes text messages and images for toxicity, NSFW content,
and stalking-like behavioral patterns, producing a dynamic Creep Score.
"""

import io
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.behavior import BehaviorTracker
from backend.models import AnalysisResponse, ResetRequest, TextAnalysisRequest
from backend.scoring import (
    build_reason,
    calculate_behavioral_penalty,
    calculate_creep_score,
    determine_action,
)

# ---------------------------------------------------------------------------
# Optional ML model loading – gracefully degrades if models unavailable
# ---------------------------------------------------------------------------
text_classifier = None
image_classifier = None


def _load_models() -> None:
    """Attempt to load Hugging Face models. Skip if unavailable."""
    global text_classifier, image_classifier
    try:
        from transformers import pipeline

        model_name = os.getenv(
            "SMARTSHIELD_TEXT_MODEL", "unitary/toxic-bert"
        )
        text_classifier = pipeline("text-classification", model=model_name)
    except Exception:
        text_classifier = None

    try:
        from transformers import pipeline

        image_model = os.getenv(
            "SMARTSHIELD_IMAGE_MODEL", "Falconsai/nsfw_image_detection"
        )
        image_classifier = pipeline("image-classification", model=image_model)
    except Exception:
        image_classifier = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models on startup."""
    _load_models()
    yield


app = FastAPI(
    title="SmartShield AI",
    description="AI-Based Creep Filtration & Digital Boundary Enforcement System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory behavioral tracker (would be Redis in production)
tracker = BehaviorTracker()


def _predict_text_toxicity(text: str) -> float:
    """Run text through the toxicity model and return a probability."""
    if text_classifier is None:
        return 0.0
    try:
        results = text_classifier(text, truncation=True)
        if results:
            result = results[0]
            label = result.get("label", "").lower()
            score = result.get("score", 0.0)
            if "toxic" in label:
                return float(score)
            return 1.0 - float(score)
    except Exception:
        pass
    return 0.0


def _predict_image_nsfw(image_bytes: bytes) -> float:
    """Run image through the NSFW classifier and return a probability."""
    if image_classifier is None:
        return 0.0
    try:
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = image_classifier(image)
        if results:
            for result in results:
                label = result.get("label", "").lower()
                if "nsfw" in label:
                    return float(result.get("score", 0.0))
            # If no explicit NSFW label, return complement of safe score
            result = results[0]
            label = result.get("label", "").lower()
            score = result.get("score", 0.0)
            if "normal" in label or "safe" in label or "sfw" in label:
                return 1.0 - float(score)
    except Exception:
        pass
    return 0.0


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "text_model_loaded": text_classifier is not None,
        "image_model_loaded": image_classifier is not None,
    }


@app.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """Analyze a text message for toxicity and behavioral patterns.

    Process:
    1. Run text through toxicity model
    2. Update behavioral counter (unanswered messages)
    3. Calculate aggregate Creep Score
    4. Return action and explainable reasoning
    """
    # Record the message and get unanswered count
    unanswered = tracker.record_message(request.sender_id, request.receiver_id)

    # Predict text toxicity
    text_score = _predict_text_toxicity(request.text)

    # Calculate behavioral penalty
    b_penalty = calculate_behavioral_penalty(unanswered)

    # Calculate aggregate creep score (no image in text-only analysis)
    creep = calculate_creep_score(
        text_toxicity=text_score,
        image_nsfw=0.0,
        behavioral_penalty=b_penalty,
    )

    action = determine_action(creep)
    reason = build_reason(
        action=action,
        text_toxicity=text_score,
        behavioral_penalty=b_penalty,
        unanswered_count=unanswered,
    )

    return AnalysisResponse(
        creep_score=round(creep, 4),
        action=action,
        reason=reason,
        text_toxicity=round(text_score, 4),
        image_nsfw=None,
        behavioral_penalty=round(b_penalty, 4),
    )


@app.post("/analyze/image", response_model=AnalysisResponse)
async def analyze_image(
    sender_id: str = Form(...),
    receiver_id: str = Form(...),
    file: UploadFile = File(...),
    text: Optional[str] = Form(None),
):
    """Analyze an uploaded image (and optional text) for NSFW content.

    Process:
    1. Run image through NSFW classifier
    2. Optionally run accompanying text through toxicity model
    3. Update behavioral counter
    4. Calculate aggregate Creep Score
    5. Return action and explainable reasoning
    """
    image_bytes = await file.read()

    unanswered = tracker.record_message(sender_id, receiver_id)

    image_score = _predict_image_nsfw(image_bytes)
    text_score = _predict_text_toxicity(text) if text else 0.0
    b_penalty = calculate_behavioral_penalty(unanswered)

    creep = calculate_creep_score(
        text_toxicity=text_score,
        image_nsfw=image_score,
        behavioral_penalty=b_penalty,
    )

    action = determine_action(creep)
    reason = build_reason(
        action=action,
        text_toxicity=text_score,
        image_nsfw=image_score,
        behavioral_penalty=b_penalty,
        unanswered_count=unanswered,
    )

    return AnalysisResponse(
        creep_score=round(creep, 4),
        action=action,
        reason=reason,
        text_toxicity=round(text_score, 4) if text else None,
        image_nsfw=round(image_score, 4),
        behavioral_penalty=round(b_penalty, 4),
    )


@app.post("/reply")
async def record_reply(request: ResetRequest):
    """Record that a receiver replied, resetting the behavioral counter.

    This resets the unanswered message counter between the pair,
    reflecting that the conversation is now two-way.
    """
    tracker.record_reply(request.sender_id, request.receiver_id)
    return {"status": "ok", "message": "Behavioral counter reset."}


@app.post("/reset")
async def reset_tracking(request: ResetRequest):
    """Reset behavioral tracking between two users (for demo/testing)."""
    tracker.reset(request.sender_id, request.receiver_id)
    return {"status": "ok", "message": "Tracking reset."}
