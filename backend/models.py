"""Pydantic models for SmartShield AI API."""

from pydantic import BaseModel, Field
from typing import Optional


class TextAnalysisRequest(BaseModel):
    """Request model for text message analysis."""
    sender_id: str = Field(..., description="Unique identifier for the sender")
    receiver_id: str = Field(..., description="Unique identifier for the receiver")
    text: str = Field(..., description="Text message content to analyze")


class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis (metadata only, image sent as file)."""
    sender_id: str = Field(..., description="Unique identifier for the sender")
    receiver_id: str = Field(..., description="Unique identifier for the receiver")


class AnalysisResponse(BaseModel):
    """Response model returned after content analysis."""
    creep_score: float = Field(..., ge=0.0, le=1.0, description="Aggregate creep score from 0 to 1")
    action: str = Field(..., description="Action to take: allow, blur, or block")
    reason: str = Field(..., description="Explainable AI reasoning for the decision")
    text_toxicity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Text toxicity probability")
    image_nsfw: Optional[float] = Field(None, ge=0.0, le=1.0, description="Image NSFW probability")
    behavioral_penalty: float = Field(0.0, ge=0.0, le=1.0, description="Behavioral penalty score")


class ResetRequest(BaseModel):
    """Request model for resetting behavioral tracking between two users."""
    sender_id: str
    receiver_id: str
