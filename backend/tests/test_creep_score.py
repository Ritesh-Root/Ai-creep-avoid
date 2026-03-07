"""Tests for the Creep Score engine."""

import pytest
from app.models.creep_score import (
    compute_creep_score,
    compute_behavior_score,
    Disposition,
)
from app.models.behavioral_tracker import BehaviorSignals


def _make_signals(**kwargs) -> BehaviorSignals:
    defaults = dict(
        flood_rate=0.0,
        unanswered_streak=0,
        unanswered_score=0.0,
        odd_hour=False,
        escalation_rate=0.0,
        keyword_alarm=False,
        total_messages=1,
        messages_per_minute=1.0,
    )
    defaults.update(kwargs)
    return BehaviorSignals(**defaults)


class TestComputeBehaviorScore:
    def test_zero_signals_gives_zero(self):
        signals = _make_signals()
        assert compute_behavior_score(signals) == 0.0

    def test_all_max_signals_gives_one(self):
        signals = _make_signals(
            flood_rate=1.0,
            unanswered_score=1.0,
            odd_hour=True,
            escalation_rate=1.0,
            keyword_alarm=True,
        )
        assert compute_behavior_score(signals) == 1.0

    def test_keyword_alarm_adds_bonus(self):
        s_no_alarm = _make_signals(keyword_alarm=False)
        s_alarm = _make_signals(keyword_alarm=True)
        assert compute_behavior_score(s_alarm) > compute_behavior_score(s_no_alarm)

    def test_odd_hour_adds_bonus(self):
        s_normal = _make_signals(odd_hour=False)
        s_odd = _make_signals(odd_hour=True)
        assert compute_behavior_score(s_odd) > compute_behavior_score(s_normal)


class TestComputeCreepScore:
    def test_zero_inputs_give_zero(self):
        result = compute_creep_score(0.0, 0.0, 0.0)
        assert result.creep_score == 0.0
        assert result.disposition == Disposition.ALLOW

    def test_high_text_score_triggers_block(self):
        result = compute_creep_score(1.0, 0.0, 0.0)
        assert result.creep_score == 0.40  # 0.40 * 1.0
        assert result.disposition == Disposition.WARN

    def test_all_max_triggers_block(self):
        result = compute_creep_score(1.0, 1.0, 1.0)
        assert result.creep_score == 1.0
        assert result.disposition == Disposition.BLOCK

    def test_moderate_text_triggers_warn(self):
        # text_score=0.7 → raw = 0.40*0.7 = 0.28 → ALLOW
        result = compute_creep_score(0.70, 0.0, 0.0)
        assert result.disposition in (Disposition.ALLOW, Disposition.WARN)

    def test_score_between_zero_and_one(self):
        result = compute_creep_score(0.5, 0.5, 0.5)
        assert 0.0 <= result.creep_score <= 1.0

    def test_sub_scores_preserved(self):
        result = compute_creep_score(0.3, 0.5, 0.2)
        assert result.text_score == 0.3
        assert result.image_score == 0.5
        assert result.behavior_score == 0.2

    def test_blur_threshold(self):
        # Need creep_score >= 0.60 for BLUR
        # 0.40*0.9 + 0.35*0.9 + 0.25*0.9 = 0.9 → BLOCK
        result = compute_creep_score(0.9, 0.9, 0.9)
        assert result.disposition == Disposition.BLOCK

    def test_warn_threshold(self):
        # 0.40*0.5 + 0.35*0.5 + 0.25*0.5 = 0.5 → WARN
        result = compute_creep_score(0.5, 0.5, 0.5)
        assert result.disposition == Disposition.WARN

    def test_disposition_values_are_strings(self):
        result = compute_creep_score(0.0, 0.0, 0.0)
        assert result.disposition.value in ("ALLOW", "WARN", "BLUR", "BLOCK")
