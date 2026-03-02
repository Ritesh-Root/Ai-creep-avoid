"""
Behavioral pattern tracker.

Tracks per-session, per-sender signals entirely in RAM using SessionStore.
No data is ever written to disk.

Tracked signals
---------------
- messages_per_minute  : rolling 60-second message count
- unanswered_streak    : consecutive messages without a reply
- odd_hour             : message sent between 00:00 and 05:00 local time
- escalation_rate      : rising toxicity across recent message window
- keyword_alarm        : forwarded from TextAnalysisResult
- total_messages       : lifetime message count in this session
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.utils.privacy import SessionStore


# Number of recent toxicity scores to track for escalation detection
_ESCALATION_WINDOW = 5


@dataclass
class BehaviorSignals:
    flood_rate: float          # 0–1; derived from messages_per_minute
    unanswered_streak: int     # raw count
    unanswered_score: float    # 0–1 normalised
    odd_hour: bool
    escalation_rate: float     # 0–1
    keyword_alarm: bool
    total_messages: int
    messages_per_minute: float


class BehavioralTracker:
    """Records and scores behavioral patterns per (session_id, sender_hash)."""

    def __init__(self, session_store: "SessionStore") -> None:
        self._store = session_store

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_message(
        self,
        *,
        session_id: str,
        sender_hash: str,
        toxicity_score: float,
        keyword_alarm: bool,
        has_reply: bool = False,
    ) -> BehaviorSignals:
        """Record a new message and return current behavioral signals."""
        key = f"{session_id}:{sender_hash}"
        now = time.time()
        state = self._store.get(key) or self._default_state()

        # ---- Update message timestamps for flood detection ----------------
        state["timestamps"].append(now)
        # Keep only the last 60 seconds of timestamps
        state["timestamps"] = [t for t in state["timestamps"] if now - t <= 60]
        messages_per_minute = float(len(state["timestamps"]))
        flood_rate = min(messages_per_minute / 10.0, 1.0)

        # ---- Unanswered streak --------------------------------------------
        if has_reply:
            state["unanswered_streak"] = 0
        else:
            state["unanswered_streak"] = state.get("unanswered_streak", 0) + 1
        unanswered_streak = state["unanswered_streak"]
        unanswered_score = min(unanswered_streak / 15.0, 1.0)

        # ---- Odd-hour detection (UTC) -------------------------------------
        hour = datetime.now(tz=timezone.utc).hour
        odd_hour = 0 <= hour < 5

        # ---- Escalation rate over recent window --------------------------
        state.setdefault("toxicity_window", [])
        state["toxicity_window"].append(toxicity_score)
        if len(state["toxicity_window"]) > _ESCALATION_WINDOW:
            state["toxicity_window"] = state["toxicity_window"][-_ESCALATION_WINDOW:]
        escalation_rate = self._compute_escalation(state["toxicity_window"])

        # ---- Keyword alarm (forwarded from text analyzer) ----------------
        state["keyword_alarm"] = state.get("keyword_alarm", False) or keyword_alarm

        # ---- Total message count -----------------------------------------
        state["total_messages"] = state.get("total_messages", 0) + 1

        self._store.set(key, state)

        return BehaviorSignals(
            flood_rate=flood_rate,
            unanswered_streak=unanswered_streak,
            unanswered_score=unanswered_score,
            odd_hour=odd_hour,
            escalation_rate=escalation_rate,
            keyword_alarm=state["keyword_alarm"],
            total_messages=state["total_messages"],
            messages_per_minute=messages_per_minute,
        )

    def record_reply(self, *, session_id: str, sender_hash: str) -> None:
        """Mark that the recipient replied to *sender_hash*, resetting their streak."""
        key = f"{session_id}:{sender_hash}"
        state = self._store.get(key) or self._default_state()
        state["unanswered_streak"] = 0
        self._store.set(key, state)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _default_state() -> dict:
        return {
            "timestamps": [],
            "unanswered_streak": 0,
            "toxicity_window": [],
            "keyword_alarm": False,
            "total_messages": 0,
        }

    @staticmethod
    def _compute_escalation(window: list[float]) -> float:
        """Return a 0–1 escalation rate based on the slope of recent toxicity scores."""
        if len(window) < 2:
            return 0.0
        mid = len(window) // 2
        if mid == 0:
            return 0.0
        first_half_avg = sum(window[:mid]) / mid
        second_half_avg = sum(window[mid:]) / len(window[mid:])
        delta = second_half_avg - first_half_avg
        # Normalise: a delta of 0.5 → escalation_rate of 1.0
        return min(max(delta * 2.0, 0.0), 1.0)
