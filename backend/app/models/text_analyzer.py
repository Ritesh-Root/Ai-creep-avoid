"""
Text analyzer – wraps HuggingFace toxic-bert (or a mock for fast startup).

Primary model: unitary/toxic-bert
  Labels: toxic, severe_toxic, obscene, threat, insult, identity_hate

The model is loaded once at startup and reused across all requests.
If USE_MOCK_MODELS=true is set in the environment, a lightweight mock
is used so the server starts instantly (useful for demos without GPU).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

_MOCK = os.getenv("USE_MOCK_MODELS", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Keyword alarm list (fast, zero-cost pre-filter)
# ---------------------------------------------------------------------------
_THREAT_KEYWORDS: frozenset[str] = frozenset(
    {
        "kill", "murder", "stab", "shoot", "rape", "i know where you live",
        "i'll find you", "you'll regret", "watch your back", "i'm watching",
        "come outside", "i'll hurt", "you're dead", "die", "hurt you",
    }
)


@dataclass
class TextAnalysisResult:
    score: float
    categories: list[str] = field(default_factory=list)
    keyword_alarm: bool = False
    raw_labels: dict[str, float] = field(default_factory=dict)


class TextAnalyzer:
    """Wraps the toxic-bert classifier with a simple interface."""

    def __init__(self) -> None:
        if _MOCK:
            self._pipeline = None
        else:
            self._pipeline = self._load_pipeline()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, text: str) -> TextAnalysisResult:
        """Return a TextAnalysisResult for *text*."""
        if not text or not text.strip():
            return TextAnalysisResult(score=0.0)

        keyword_alarm = self._check_keywords(text)

        if self._pipeline is None:
            # Mock mode: use keyword heuristic only
            return self._mock_analyze(text, keyword_alarm)

        return self._model_analyze(text, keyword_alarm)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_keywords(self, text: str) -> bool:
        lower = text.lower()
        return any(kw in lower for kw in _THREAT_KEYWORDS)

    def _load_pipeline(self):
        try:
            from transformers import pipeline as hf_pipeline
            return hf_pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                top_k=None,
                truncation=True,
                max_length=512,
            )
        except Exception:
            return None

    def _model_analyze(self, text: str, keyword_alarm: bool) -> TextAnalysisResult:
        try:
            results = self._pipeline(text)
            # results is a list of lists: [[{label, score}, ...]]
            label_scores: dict[str, float] = {}
            if results and isinstance(results[0], list):
                for item in results[0]:
                    label_scores[item["label"].lower()] = item["score"]
            elif results and isinstance(results[0], dict):
                for item in results:
                    label_scores[item["label"].lower()] = item["score"]

            toxic_score = label_scores.get("toxic", 0.0)
            categories = [
                lbl
                for lbl, sc in label_scores.items()
                if sc >= 0.5 and lbl != "toxic"
            ]
            if toxic_score >= 0.5 and "toxic" not in categories:
                categories.insert(0, "toxic")

            # Boost score if keyword matched
            final_score = min(toxic_score + (0.20 if keyword_alarm else 0.0), 1.0)
            return TextAnalysisResult(
                score=final_score,
                categories=categories,
                keyword_alarm=keyword_alarm,
                raw_labels=label_scores,
            )
        except Exception:
            return self._mock_analyze(text, keyword_alarm)

    def _mock_analyze(self, text: str, keyword_alarm: bool) -> TextAnalysisResult:
        """Heuristic-only analysis used when the model is unavailable."""
        lower = text.lower()

        score = 0.0
        categories: list[str] = []

        if keyword_alarm:
            score = max(score, 0.85)
            categories.append("threat")

        obscene_words = {"fuck", "bitch", "asshole", "bastard", "damn"}
        words = set(lower.split())
        if any(w in words for w in obscene_words):
            score = max(score, 0.70)
            categories.append("obscene")

        sexual_words = {"sex", "nude", "naked", "porn", "sexy", "horny"}
        if any(w in words for w in sexual_words):
            score = max(score, 0.65)
            categories.append("sexual")

        insult_words = {"idiot", "stupid", "moron", "loser", "ugly", "fat"}
        if any(w in words for w in insult_words):
            score = max(score, 0.55)
            categories.append("insult")

        return TextAnalysisResult(
            score=score,
            categories=categories,
            keyword_alarm=keyword_alarm,
            raw_labels={},
        )
