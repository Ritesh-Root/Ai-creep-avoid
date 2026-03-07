"""Tests for TextAnalyzer (mock mode, no model download required)."""

import os
os.environ["USE_MOCK_MODELS"] = "true"

import pytest
from app.models.text_analyzer import TextAnalyzer


@pytest.fixture(scope="module")
def analyzer():
    return TextAnalyzer()


def test_clean_message_low_score(analyzer):
    result = analyzer.analyze("Hey! How are you doing today?")
    assert result.score < 0.40, "Clean message should have a low toxicity score"


def test_empty_message_zero_score(analyzer):
    result = analyzer.analyze("")
    assert result.score == 0.0


def test_whitespace_message_zero_score(analyzer):
    result = analyzer.analyze("   ")
    assert result.score == 0.0


def test_threat_keyword_triggers_alarm(analyzer):
    result = analyzer.analyze("I know where you live and you'll regret this")
    assert result.keyword_alarm is True
    assert result.score >= 0.80, "Threat keyword should produce high score"
    assert "threat" in result.categories


def test_obscene_language_flagged(analyzer):
    result = analyzer.analyze("You stupid asshole")
    assert result.score >= 0.55


def test_sexual_language_flagged(analyzer):
    result = analyzer.analyze("Send me nude photos")
    assert result.score >= 0.55
    assert "sexual" in result.categories


def test_categories_returned_as_list(analyzer):
    result = analyzer.analyze("You idiot loser")
    assert isinstance(result.categories, list)


def test_raw_labels_empty_in_mock(analyzer):
    result = analyzer.analyze("Hello there")
    assert isinstance(result.raw_labels, dict)
