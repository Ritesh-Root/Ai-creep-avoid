"""Tests for SessionStore and privacy utilities."""

import time
import pytest
from app.utils.privacy import SessionStore, hash_sender_id


class TestSessionStore:
    def test_set_and_get(self):
        store = SessionStore(ttl_seconds=60)
        store.set("s1", {"key": "value"})
        data = store.get("s1")
        assert data is not None
        assert data["key"] == "value"

    def test_missing_session_returns_none(self):
        store = SessionStore(ttl_seconds=60)
        assert store.get("nonexistent") is None

    def test_expired_session_returns_none(self):
        store = SessionStore(ttl_seconds=0)
        store.set("s2", {"key": "val"})
        time.sleep(0.01)
        assert store.get("s2") is None

    def test_update_merges_data(self):
        store = SessionStore(ttl_seconds=60)
        store.set("s3", {"a": 1})
        store.update("s3", {"b": 2})
        data = store.get("s3")
        assert data["a"] == 1
        assert data["b"] == 2

    def test_delete_removes_session(self):
        store = SessionStore(ttl_seconds=60)
        store.set("s4", {"key": "val"})
        store.delete("s4")
        assert store.get("s4") is None

    def test_clear_all_removes_all(self):
        store = SessionStore(ttl_seconds=60)
        store.set("s5", {"k": "v"})
        store.set("s6", {"k": "v"})
        store.clear_all()
        assert store.active_session_count == 0

    def test_active_session_count(self):
        store = SessionStore(ttl_seconds=60)
        store.set("s7", {})
        store.set("s8", {})
        assert store.active_session_count == 2


class TestHashSenderId:
    def test_hash_is_64_hex_chars(self):
        h = hash_sender_id("user_123")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_same_input_same_hash(self):
        assert hash_sender_id("alice") == hash_sender_id("alice")

    def test_different_input_different_hash(self):
        assert hash_sender_id("alice") != hash_sender_id("bob")

    def test_original_not_recoverable(self):
        # Ensure the hash does not contain the original string
        original = "mysecretuser"
        h = hash_sender_id(original)
        assert original not in h
