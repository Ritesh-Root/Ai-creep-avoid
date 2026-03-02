"""
Image analyzer – detects NSFW / sexually explicit content in uploaded images.

Primary model: Falconsai/nsfw_image_detection  (HuggingFace)
  Labels: normal, nsfw

Falls back to a lightweight pixel-heuristic when USE_MOCK_MODELS=true or
when the model cannot be loaded (e.g., no internet in offline hackathon env).
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass, field

_MOCK = os.getenv("USE_MOCK_MODELS", "false").lower() == "true"


@dataclass
class ImageAnalysisResult:
    score: float
    categories: list[str] = field(default_factory=list)
    raw_labels: dict[str, float] = field(default_factory=dict)


class ImageAnalyzer:
    """Wraps the NSFW image classifier with a simple interface."""

    def __init__(self) -> None:
        if _MOCK:
            self._pipeline = None
        else:
            self._pipeline = self._load_pipeline()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_bytes(self, image_bytes: bytes, content_type: str = "image/jpeg") -> ImageAnalysisResult:
        """Classify raw image bytes.  Returns an ImageAnalysisResult."""
        if not image_bytes:
            return ImageAnalysisResult(score=0.0)

        try:
            from PIL import Image
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception:
            return ImageAnalysisResult(score=0.0)

        if self._pipeline is None:
            return self._mock_analyze(image)

        return self._model_analyze(image)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_pipeline(self):
        try:
            from transformers import pipeline as hf_pipeline
            return hf_pipeline(
                "image-classification",
                model="Falconsai/nsfw_image_detection",
            )
        except Exception:
            return None

    def _model_analyze(self, image) -> ImageAnalysisResult:
        try:
            results = self._pipeline(image)
            label_scores: dict[str, float] = {r["label"].lower(): r["score"] for r in results}
            nsfw_score = label_scores.get("nsfw", 0.0)
            categories = ["nsfw"] if nsfw_score >= 0.5 else []
            return ImageAnalysisResult(
                score=nsfw_score,
                categories=categories,
                raw_labels=label_scores,
            )
        except Exception:
            return self._mock_analyze(image)

    def _mock_analyze(self, image) -> ImageAnalysisResult:
        """
        Minimal heuristic: examine average skin-tone pixel ratio.
        This is intentionally simple – for demo / offline use only.
        """
        try:
            import numpy as np
            arr = np.array(image.resize((64, 64)))
            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            # Broad skin-tone heuristic (Fitzpatrick scale approximation)
            skin_mask = (
                (r > 60) & (r < 255) &
                (g > 40) & (g < 220) &
                (b > 20) & (b < 195) &
                (r > g) & (r > b) &
                ((r.astype(int) - g.astype(int)) > 10)
            )
            skin_ratio = float(skin_mask.sum()) / (64 * 64)
            # High skin ratio is a weak signal; cap at 0.6 for mock
            score = min(skin_ratio * 1.5, 0.60)
            categories = ["potential_nsfw"] if score >= 0.30 else []
            return ImageAnalysisResult(score=score, categories=categories, raw_labels={})
        except Exception:
            return ImageAnalysisResult(score=0.0)
