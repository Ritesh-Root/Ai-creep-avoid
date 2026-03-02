"""
Explainable AI (XAI) reasoning module.

Translates raw scores and signals into human-readable explanations
that are returned to the client with every analysis response.
"""

from __future__ import annotations

from typing import Any


def build_reasons(
    *,
    text_score: float,
    text_categories: list[str],
    image_score: float,
    image_categories: list[str],
    behavior: dict[str, Any],
    creep_score: float,
) -> list[str]:
    """Return a list of human-readable reason strings explaining the score."""
    reasons: list[str] = []

    # ---- Text reasons ------------------------------------------------
    if text_score >= 0.80:
        level = "high"
    elif text_score >= 0.50:
        level = "moderate"
    else:
        level = "low"

    if text_score >= 0.40:
        cats = ", ".join(text_categories) if text_categories else "general toxicity"
        reasons.append(
            f"Message contains {level}-confidence harmful language "
            f"({int(text_score * 100)}% confidence) – categories: {cats}."
        )

    # ---- Image reasons -----------------------------------------------
    if image_score >= 0.40:
        cats = ", ".join(image_categories) if image_categories else "explicit content"
        reasons.append(
            f"Image flagged as potentially NSFW "
            f"({int(image_score * 100)}% confidence) – categories: {cats}."
        )

    # ---- Behavioral reasons ------------------------------------------
    flood_rate = behavior.get("flood_rate", 0.0)
    unanswered = behavior.get("unanswered_streak", 0)
    odd_hour = behavior.get("odd_hour", False)
    escalation = behavior.get("escalation_rate", 0.0)
    keyword_alarm = behavior.get("keyword_alarm", False)
    total_messages = behavior.get("total_messages", 0)

    if flood_rate >= 0.5:
        msgs_per_min = behavior.get("messages_per_minute", 0.0)
        reasons.append(
            f"Sender is flooding messages: "
            f"{msgs_per_min:.1f} messages per minute detected."
        )

    if unanswered >= 5:
        reasons.append(
            f"Sender sent {unanswered} consecutive unanswered messages – "
            "possible stalking or pressure pattern."
        )

    if odd_hour:
        reasons.append(
            "Messages are being sent during late-night hours (00:00–05:00), "
            "which is a known harassment pattern."
        )

    if escalation >= 0.3:
        reasons.append(
            "Message toxicity is escalating over the conversation window – "
            "aggressive behavioral pattern detected."
        )

    if keyword_alarm:
        reasons.append(
            "Message contains a keyword or phrase associated with threats or stalking."
        )

    if total_messages >= 20 and not reasons:
        reasons.append(
            f"High message volume ({total_messages} messages) from this sender "
            "in the current session."
        )

    # ---- Fallback ----------------------------------------------------
    if not reasons and creep_score >= 0.40:
        reasons.append(
            f"Combined signals produced a Creep Score of {creep_score:.2f} "
            "which exceeds the warning threshold."
        )

    return reasons
