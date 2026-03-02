"""
Creep Score engine.

Aggregates text, image, and behavioral sub-scores into a single
Creep Score (0–1) and maps it to an actionable disposition.

Formula
-------
raw_score = (
    0.40 * text_score
  + 0.35 * image_score
  + 0.25 * behavior_score
)
creep_score = clamp(raw_score, 0.0, 1.0)

behavior_score = clamp(
    flood_rate           * 0.25
  + unanswered_score     * 0.35
  + odd_hour_penalty              (flat +0.15)
  + escalation_rate      * 0.20
  + keyword_alarm_bonus           (flat +0.30)
)

Disposition thresholds (configurable via environment):
  ALLOW : 0.00 – 0.39
  WARN  : 0.40 – 0.59
  BLUR  : 0.60 – 0.79
  BLOCK : 0.80 – 1.00
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.behavioral_tracker import BehaviorSignals

# ---------------------------------------------------------------------------
# Configurable thresholds (can be overridden via environment variables)
# ---------------------------------------------------------------------------
WARN_THRESHOLD = float(os.getenv("WARN_THRESHOLD", "0.40"))
BLUR_THRESHOLD = float(os.getenv("BLUR_THRESHOLD", "0.60"))
BLOCK_THRESHOLD = float(os.getenv("BLOCK_THRESHOLD", "0.80"))

# Sub-score weights (must sum to 1.0)
_W_TEXT = 0.40
_W_IMAGE = 0.35
_W_BEHAVIOR = 0.25

# Behavioral component weights (need not sum to 1.0; result is clamped)
_BW_FLOOD = 0.25
_BW_UNANSWERED = 0.35
_BW_ODD_HOUR = 0.15        # flat bonus
_BW_ESCALATION = 0.20
_BW_KEYWORD = 0.30         # flat bonus


class Disposition(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLUR = "BLUR"
    BLOCK = "BLOCK"


@dataclass
class CreepScoreResult:
    creep_score: float
    disposition: Disposition
    text_score: float
    image_score: float
    behavior_score: float


def compute_behavior_score(signals: "BehaviorSignals") -> float:
    """Convert BehaviorSignals into a 0–1 behavior sub-score."""
    score = (
        signals.flood_rate * _BW_FLOOD
        + signals.unanswered_score * _BW_UNANSWERED
        + (_BW_ODD_HOUR if signals.odd_hour else 0.0)
        + signals.escalation_rate * _BW_ESCALATION
        + (_BW_KEYWORD if signals.keyword_alarm else 0.0)
    )
    return float(min(max(score, 0.0), 1.0))


def compute_creep_score(
    text_score: float,
    image_score: float,
    behavior_score: float,
) -> CreepScoreResult:
    """Aggregate sub-scores and return a CreepScoreResult."""
    raw = (
        _W_TEXT * text_score
        + _W_IMAGE * image_score
        + _W_BEHAVIOR * behavior_score
    )
    creep_score = round(float(min(max(raw, 0.0), 1.0)), 4)

    if creep_score >= BLOCK_THRESHOLD:
        disposition = Disposition.BLOCK
    elif creep_score >= BLUR_THRESHOLD:
        disposition = Disposition.BLUR
    elif creep_score >= WARN_THRESHOLD:
        disposition = Disposition.WARN
    else:
        disposition = Disposition.ALLOW

    return CreepScoreResult(
        creep_score=creep_score,
        disposition=disposition,
        text_score=round(text_score, 4),
        image_score=round(image_score, 4),
        behavior_score=round(behavior_score, 4),
    )
