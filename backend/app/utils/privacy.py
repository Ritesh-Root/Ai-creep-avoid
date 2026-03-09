"""
Privacy utilities: hashed session management and ephemeral data storage.

All data is stored in RAM only (no disk, no database).
Sender IDs are stored as SHA-256 hashes so originals never persist.
Sessions automatically expire after SESSION_TTL_SECONDS.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any


# Default TTL: 30 minutes
_DEFAULT_TTL = 1800


class SessionStore:
    """In-memory, TTL-based session store.  No data is persisted to disk."""

    def __init__(self, ttl_seconds: int = _DEFAULT_TTL) -> None:
        self._ttl = ttl_seconds
        # { session_id: { "data": {...}, "created_at": float, "last_access": float } }
        self._store: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get(self, session_id: str) -> dict[str, Any] | None:
        """Return session data if it exists and has not expired."""
        self._evict_expired()
        entry = self._store.get(session_id)
        if entry is None:
            return None
        entry["last_access"] = time.monotonic()
        return entry["data"]

    def set(self, session_id: str, data: dict[str, Any]) -> None:
        """Create or overwrite a session entry."""
        now = time.monotonic()
        self._store[session_id] = {
            "data": data,
            "created_at": now,
            "last_access": now,
        }

    def update(self, session_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Merge *updates* into an existing session (creates one if absent)."""
        data = self.get(session_id) or {}
        data.update(updates)
        self.set(session_id, data)
        return data

    def delete(self, session_id: str) -> None:
        """Remove a session immediately."""
        self._store.pop(session_id, None)

    def clear_all(self) -> None:
        """Wipe all sessions (called on application shutdown)."""
        self._store.clear()

    @property
    def active_session_count(self) -> int:
        self._evict_expired()
        return len(self._store)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict_expired(self) -> None:
        """Remove sessions whose last_access is older than TTL."""
        now = time.monotonic()
        expired = [
            sid
            for sid, entry in self._store.items()
            if now - entry["last_access"] > self._ttl
        ]
        for sid in expired:
            del self._store[sid]


# ------------------------------------------------------------------
# Hashing helpers
# ------------------------------------------------------------------

def hash_sender_id(sender_id: str) -> str:
    """Return a SHA-256 hex digest of the sender ID.

    Originals are never stored; the hash is used as the storage key so
    that behavioral history can be associated across messages in a session
    without retaining personally identifiable information.
    """
    return hashlib.sha256(sender_id.encode("utf-8")).hexdigest()
