"""Behavioral tracking for SmartShield AI.

Tracks consecutive unanswered messages between user pairs using an
in-memory store. In production, this would use Redis for persistence
across instances. For the hackathon MVP, a simple dictionary suffices.

Privacy note: Only anonymized counters are stored (e.g., user_1→user_2: 4),
never message content.
"""

from typing import Dict, Tuple


class BehaviorTracker:
    """Tracks message flooding / stalking-like behavioral patterns."""

    def __init__(self) -> None:
        # Key: (sender_id, receiver_id) -> unanswered message count
        self._counters: Dict[Tuple[str, str], int] = {}

    def record_message(self, sender_id: str, receiver_id: str) -> int:
        """Record a message from sender to receiver and return the updated
        unanswered count.

        When sender sends a message to receiver, increment the counter.
        This is reset when the receiver replies (see record_reply).

        Args:
            sender_id: The sender's identifier.
            receiver_id: The receiver's identifier.

        Returns:
            Updated count of consecutive unanswered messages.
        """
        key = (sender_id, receiver_id)
        self._counters[key] = self._counters.get(key, 0) + 1
        return self._counters[key]

    def record_reply(self, original_sender_id: str, original_receiver_id: str) -> None:
        """Record that the receiver replied, resetting the unanswered counter.

        Args:
            original_sender_id: The original sender's identifier.
            original_receiver_id: The original receiver's identifier (who is now replying).
        """
        key = (original_sender_id, original_receiver_id)
        self._counters[key] = 0

    def get_unanswered_count(self, sender_id: str, receiver_id: str) -> int:
        """Get the current unanswered message count.

        Args:
            sender_id: The sender's identifier.
            receiver_id: The receiver's identifier.

        Returns:
            Number of consecutive unanswered messages.
        """
        return self._counters.get((sender_id, receiver_id), 0)

    def reset(self, sender_id: str, receiver_id: str) -> None:
        """Reset the counter between two users.

        Args:
            sender_id: The sender's identifier.
            receiver_id: The receiver's identifier.
        """
        key = (sender_id, receiver_id)
        self._counters[key] = 0
