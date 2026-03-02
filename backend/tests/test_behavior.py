"""Tests for the behavioral tracker."""

from backend.behavior import BehaviorTracker


class TestBehaviorTracker:
    def test_initial_count_is_zero(self):
        t = BehaviorTracker()
        assert t.get_unanswered_count("a", "b") == 0

    def test_record_message_increments(self):
        t = BehaviorTracker()
        assert t.record_message("a", "b") == 1
        assert t.record_message("a", "b") == 2
        assert t.record_message("a", "b") == 3

    def test_record_reply_resets(self):
        t = BehaviorTracker()
        t.record_message("a", "b")
        t.record_message("a", "b")
        t.record_reply("a", "b")
        assert t.get_unanswered_count("a", "b") == 0

    def test_different_pairs_independent(self):
        t = BehaviorTracker()
        t.record_message("a", "b")
        t.record_message("a", "b")
        t.record_message("c", "d")
        assert t.get_unanswered_count("a", "b") == 2
        assert t.get_unanswered_count("c", "d") == 1

    def test_reset(self):
        t = BehaviorTracker()
        t.record_message("a", "b")
        t.record_message("a", "b")
        t.reset("a", "b")
        assert t.get_unanswered_count("a", "b") == 0

    def test_directional(self):
        """a→b and b→a are tracked separately."""
        t = BehaviorTracker()
        t.record_message("a", "b")
        t.record_message("a", "b")
        assert t.get_unanswered_count("a", "b") == 2
        assert t.get_unanswered_count("b", "a") == 0
