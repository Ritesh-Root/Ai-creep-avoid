"""
SmartShield AI – FastAPI application entry point.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.models.text_analyzer import TextAnalyzer
from app.models.image_analyzer import ImageAnalyzer
from app.models.behavioral_tracker import BehavioralTracker
from app.utils.privacy import SessionStore


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Load models once at startup and share via app.state."""
    application.state.text_analyzer = TextAnalyzer()
    application.state.image_analyzer = ImageAnalyzer()
    application.state.session_store = SessionStore()
    application.state.behavioral_tracker = BehavioralTracker(
        session_store=application.state.session_store
    )
    yield
    # Cleanup: clear in-memory sessions on shutdown
    application.state.session_store.clear_all()


app = FastAPI(
    title="SmartShield AI",
    description=(
        "Digital Boundary Enforcement System – real-time detection of toxic text, "
        "NSFW images, and aggressive behavioral patterns with explainable AI."
    ),
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

app.include_router(router, prefix="/api/v1")
