"""Tests for BehavioralTracker."""

import pytest
from app.utils.privacy import SessionStore
from app.models.behavioral_tracker import BehavioralTracker


@pytest.fixture
def tracker():
    store = SessionStore(ttl_seconds=60)
    return BehavioralTracker(session_store=store)


def test_first_message_creates_session(tracker):
    signals = tracker.record_message(
        session_id="s1", sender_hash="h1",
        toxicity_score=0.1, keyword_alarm=False
    )
    assert signals.total_messages == 1
    assert signals.unanswered_streak == 1


def test_unanswered_streak_increments(tracker):
    for i in range(5):
        signals = tracker.record_message(
            session_id="s2", sender_hash="h2",
            toxicity_score=0.1, keyword_alarm=False
        )
    assert signals.unanswered_streak == 5


def test_reply_resets_streak(tracker):
    for _ in range(3):
        tracker.record_message(
            session_id="s3", sender_hash="h3",
            toxicity_score=0.1, keyword_alarm=False
        )
    tracker.record_reply(session_id="s3", sender_hash="h3")
    signals = tracker.record_message(
        session_id="s3", sender_hash="h3",
        toxicity_score=0.1, keyword_alarm=False
    )
    assert signals.unanswered_streak == 1


def test_keyword_alarm_persists(tracker):
    tracker.record_message(
        session_id="s4", sender_hash="h4",
        toxicity_score=0.9, keyword_alarm=True
    )
    signals = tracker.record_message(
        session_id="s4", sender_hash="h4",
        toxicity_score=0.1, keyword_alarm=False
    )
    assert signals.keyword_alarm is True


def test_flood_rate_increases_with_rapid_messages(tracker):
    for _ in range(12):
        signals = tracker.record_message(
            session_id="s5", sender_hash="h5",
            toxicity_score=0.1, keyword_alarm=False
        )
    # 12 messages in under a second → flood_rate should be at max (1.0)
    assert signals.flood_rate == 1.0


def test_escalation_rate_for_rising_toxicity(tracker):
    low_scores = [0.1, 0.1, 0.15]
    high_scores = [0.7, 0.8, 0.9]
    for score in low_scores + high_scores:
        signals = tracker.record_message(
            session_id="s6", sender_hash="h6",
            toxicity_score=score, keyword_alarm=False
        )
    assert signals.escalation_rate > 0.0


def test_different_senders_tracked_independently(tracker):
    tracker.record_message(
        session_id="s7", sender_hash="hA",
        toxicity_score=0.1, keyword_alarm=True
    )
    signals_b = tracker.record_message(
        session_id="s7", sender_hash="hB",
        toxicity_score=0.1, keyword_alarm=False
    )
    assert signals_b.keyword_alarm is False
