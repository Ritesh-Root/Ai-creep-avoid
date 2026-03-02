"""Tests for the scoring engine."""

import pytest

from backend.scoring import (
    W_BEHAVIOR,
    W_IMAGE,
    W_TEXT,
    build_reason,
    calculate_behavioral_penalty,
    calculate_creep_score,
    determine_action,
)


class TestBehavioralPenalty:
    def test_zero_unanswered(self):
        assert calculate_behavioral_penalty(0) == 0.0

    def test_five_unanswered(self):
        assert calculate_behavioral_penalty(5) == pytest.approx(0.5)

    def test_ten_unanswered(self):
        assert calculate_behavioral_penalty(10) == pytest.approx(1.0)

    def test_exceeds_ten_capped(self):
        assert calculate_behavioral_penalty(20) == pytest.approx(1.0)

    def test_one_unanswered(self):
        assert calculate_behavioral_penalty(1) == pytest.approx(0.1)


class TestCreepScore:
    def test_all_zeros(self):
        assert calculate_creep_score(0.0, 0.0, 0.0) == pytest.approx(0.0)

    def test_all_ones(self):
        # With behavioral amplification, score would exceed 1.0 but is clamped
        assert calculate_creep_score(1.0, 1.0, 1.0) == pytest.approx(1.0)

    def test_text_only(self):
        assert calculate_creep_score(text_toxicity=0.8) == pytest.approx(W_TEXT * 0.8)

    def test_image_only(self):
        assert calculate_creep_score(image_nsfw=0.9) == pytest.approx(W_IMAGE * 0.9)

    def test_behavior_only(self):
        assert calculate_creep_score(behavioral_penalty=0.5) == pytest.approx(
            W_BEHAVIOR * 0.5
        )

    def test_behavioral_amplification(self):
        """When behavioral penalty exceeds 0.5, flooding boost kicks in."""
        # B=0.8: base = 0.20*0.8 = 0.16, boost = (0.8-0.5)*1.0 = 0.30
        score = calculate_creep_score(behavioral_penalty=0.8)
        assert score == pytest.approx(W_BEHAVIOR * 0.8 + 0.3)

    def test_flooding_triggers_blur(self):
        """8+ unanswered messages should trigger blur action."""
        score = calculate_creep_score(behavioral_penalty=0.8)
        assert determine_action(score) == "blur"

    def test_flooding_triggers_block(self):
        """10+ unanswered messages should trigger block action."""
        score = calculate_creep_score(behavioral_penalty=1.0)
        assert determine_action(score) == "block"

    def test_clamped_to_one(self):
        # Even with extreme inputs, score stays <= 1.0
        score = calculate_creep_score(1.0, 1.0, 1.0)
        assert score <= 1.0

    def test_clamped_to_zero(self):
        score = calculate_creep_score(0.0, 0.0, 0.0)
        assert score >= 0.0


class TestDetermineAction:
    def test_allow(self):
        assert determine_action(0.0) == "allow"
        assert determine_action(0.39) == "allow"

    def test_blur(self):
        assert determine_action(0.4) == "blur"
        assert determine_action(0.69) == "blur"

    def test_block(self):
        assert determine_action(0.7) == "block"
        assert determine_action(1.0) == "block"


class TestBuildReason:
    def test_allow_reason(self):
        reason = build_reason("allow")
        assert "safe" in reason.lower()

    def test_block_with_text_toxicity(self):
        reason = build_reason("block", text_toxicity=0.92)
        assert "Blocked" in reason
        assert "toxic" in reason.lower()

    def test_blur_with_nsfw(self):
        reason = build_reason("blur", image_nsfw=0.85)
        assert "Filtered" in reason
        assert "NSFW" in reason

    def test_behavioral_flooding(self):
        reason = build_reason(
            "block", behavioral_penalty=0.8, unanswered_count=8
        )
        assert "flooding" in reason.lower()

    def test_combined_reasons(self):
        reason = build_reason(
            "block",
            text_toxicity=0.9,
            image_nsfw=0.8,
            behavioral_penalty=0.5,
            unanswered_count=5,
        )
        assert "toxic" in reason.lower()
        assert "NSFW" in reason
        assert "flooding" in reason.lower()
