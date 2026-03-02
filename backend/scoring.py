"""Creep Score calculation engine for SmartShield AI.

The core engine uses a weighted formula combining text, image, and behavioral inputs.

C_score = W_t * T + W_i * I + W_b * B

Where:
  T = Text Toxicity probability [0, 1]
  I = Image NSFW probability [0, 1]
  B = Behavioral Penalty [0, 1]
  W_t = 0.35 (text weight)
  W_i = 0.45 (image weight - highest, as explicit images are immediate red flags)
  W_b = 0.20 (behavioral weight)

Behavioral Penalty (B) is calculated as: min(M_unanswered / 10, 1.0)
  e.g., 5 unanswered messages = 0.5 penalty, 10+ = 1.0 maximum.

Threshold Actions:
  C_score < 0.4       -> Allow
  0.4 <= C_score < 0.7 -> Blur (soft filter to "Hidden Requests")
  C_score >= 0.7       -> Block (hard block with AI explanation)
"""

W_TEXT = 0.35
W_IMAGE = 0.45
W_BEHAVIOR = 0.20

THRESHOLD_BLUR = 0.4
THRESHOLD_BLOCK = 0.7


def calculate_behavioral_penalty(unanswered_count: int) -> float:
    """Calculate behavioral penalty based on consecutive unanswered messages.

    Args:
        unanswered_count: Number of consecutive unanswered messages.

    Returns:
        Penalty score between 0.0 and 1.0.
    """
    return min(unanswered_count / 10.0, 1.0)


def calculate_creep_score(
    text_toxicity: float = 0.0,
    image_nsfw: float = 0.0,
    behavioral_penalty: float = 0.0,
) -> float:
    """Calculate the aggregate Creep Score.

    Args:
        text_toxicity: Text toxicity probability [0, 1].
        image_nsfw: Image NSFW probability [0, 1].
        behavioral_penalty: Behavioral penalty [0, 1].

    Returns:
        Creep Score between 0.0 and 1.0.
    """
    score = W_TEXT * text_toxicity + W_IMAGE * image_nsfw + W_BEHAVIOR * behavioral_penalty
    return min(max(score, 0.0), 1.0)


def determine_action(creep_score: float) -> str:
    """Determine the action to take based on the Creep Score.

    Args:
        creep_score: Aggregate creep score [0, 1].

    Returns:
        Action string: "allow", "blur", or "block".
    """
    if creep_score < THRESHOLD_BLUR:
        return "allow"
    elif creep_score < THRESHOLD_BLOCK:
        return "blur"
    else:
        return "block"


def build_reason(
    action: str,
    text_toxicity: float = 0.0,
    image_nsfw: float = 0.0,
    behavioral_penalty: float = 0.0,
    unanswered_count: int = 0,
) -> str:
    """Build an explainable AI reasoning string.

    Args:
        action: The determined action.
        text_toxicity: Text toxicity probability.
        image_nsfw: Image NSFW probability.
        behavioral_penalty: Behavioral penalty score.
        unanswered_count: Number of unanswered messages.

    Returns:
        Human-readable explanation of the decision.
    """
    if action == "allow":
        return "Content appears safe. No issues detected."

    reasons = []
    if text_toxicity >= 0.4:
        reasons.append(f"{text_toxicity * 100:.0f}% probability of toxic text")
    if image_nsfw >= 0.4:
        reasons.append(f"{image_nsfw * 100:.0f}% probability of NSFW image")
    if behavioral_penalty >= 0.2:
        reasons.append(
            f"Message flooding detected ({unanswered_count} unanswered messages)"
        )

    if not reasons:
        reasons.append("Combined signals exceeded safety threshold")

    prefix = "Blocked" if action == "block" else "Filtered"
    return f"{prefix}: {'; '.join(reasons)}."
