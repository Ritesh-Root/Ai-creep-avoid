"""Tests for ImageAnalyzer (mock mode, no model download required)."""

import os
os.environ["USE_MOCK_MODELS"] = "true"

import io
import pytest
from PIL import Image
from app.models.image_analyzer import ImageAnalyzer


@pytest.fixture(scope="module")
def analyzer():
    return ImageAnalyzer()


def _make_image_bytes(color: tuple, size: tuple = (100, 100)) -> bytes:
    """Helper: create a solid-color PNG image as bytes."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_empty_bytes_zero_score(analyzer):
    result = analyzer.analyze_bytes(b"")
    assert result.score == 0.0


def test_invalid_bytes_zero_score(analyzer):
    result = analyzer.analyze_bytes(b"not an image")
    assert result.score == 0.0


def test_blue_image_low_score(analyzer):
    # Blue image has very few skin-tone pixels → low score
    blue_bytes = _make_image_bytes((0, 0, 200))
    result = analyzer.analyze_bytes(blue_bytes)
    assert result.score < 0.30, "Blue image should have a low NSFW score"


def test_result_has_expected_fields(analyzer):
    blue_bytes = _make_image_bytes((0, 100, 200))
    result = analyzer.analyze_bytes(blue_bytes)
    assert isinstance(result.score, float)
    assert isinstance(result.categories, list)
    assert isinstance(result.raw_labels, dict)


def test_score_between_zero_and_one(analyzer):
    img_bytes = _make_image_bytes((180, 120, 90))
    result = analyzer.analyze_bytes(img_bytes)
    assert 0.0 <= result.score <= 1.0
