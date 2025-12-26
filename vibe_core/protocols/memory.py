"""
OPUS-311 Sprint 3: Memory Protocol

The Chitta (Mind-Stuff) that remembers across sessions.

Agent persistent memory for learning and context continuity.
Solves the "Amnesia Trap" (Critical 5% #1).

Usage:
    # Via ServiceRegistry
    memory: MemoryProtocol = ServiceRegistry.get(MemoryProtocol) or NullMemory()

    # Remember something
    memory.remember("last_agents", ["herald", "archivist"], session_id="abc123")

    # Recall it later
    agents = memory.recall("last_agents", session_id="abc123")

    # Search for patterns
    results = memory.search("agent", session_id="abc123")
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class MemoryEntry:
    """A single memory entry."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    session_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


@dataclass
class Entity:
    """
    An entity extracted from conversation.

    For resolving "the second one", "that agent", etc.
    """

    type: str  # "agent", "task", "file", etc.
    id: str
    name: str
    position: int = 0  # 1-indexed position in list
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryStats:
    """Statistics about memory usage."""

    total_entries: int = 0
    expired_entries: int = 0
    sessions_tracked: int = 0
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None


@runtime_checkable
class MemoryProtocol(Protocol):
    """
    OPUS-311: Agent persistent memory for learning.

    The Chitta - "mind-stuff" that retains impressions.

    Features:
    - Session-scoped memory (for conversation context)
    - TTL-based expiration
    - Entity tracking (for "the second one" resolution)
    - Search capability
    """

    def remember(
        self,
        key: str,
        value: Any,
        session_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Store a value in memory.

        Args:
            key: Unique identifier for this memory
            value: Any JSON-serializable value
            session_id: Optional session scope
            ttl_seconds: Time to live (None = forever)
            tags: Optional tags for search
        """
        ...

    def recall(
        self,
        key: str,
        session_id: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Retrieve a value from memory.

        Returns None if not found or expired.
        """
        ...

    def forget(
        self,
        key: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """
        Remove a value from memory.

        Returns True if something was removed.
        """
        ...

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """
        Search memory by key pattern or tags.

        Args:
            query: Search string (matches key or tags)
            session_id: Optional session filter
            limit: Max results

        Returns:
            Matching entries, newest first
        """
        ...

    def remember_entities(
        self,
        entities: List[Entity],
        session_id: str,
    ) -> None:
        """
        Remember entities from a result for later resolution.

        Enables "the second one", "that agent", etc.
        """
        ...

    def resolve_reference(
        self,
        reference: str,
        session_id: str,
    ) -> Optional[Entity]:
        """
        Resolve a natural language reference to an entity.

        Args:
            reference: "the second one", "that agent", "it"
            session_id: Current session

        Returns:
            Resolved entity or None
        """
        ...

    def get_stats(self) -> MemoryStats:
        """Get memory usage statistics."""
        ...

    def clear_session(self, session_id: str) -> int:
        """
        Clear all memories for a session.

        Returns number of entries cleared.
        """
        ...

    def clear_expired(self) -> int:
        """
        Clear all expired entries.

        Returns number of entries cleared.
        """
        ...


class NullMemory:
    """
    Arjuna Pattern: No-op memory.

    Everything is forgotten immediately.
    Use when memory service is not available.
    """

    def remember(
        self,
        key: str,
        value: Any,
        session_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        pass

    def recall(
        self,
        key: str,
        session_id: Optional[str] = None,
    ) -> Optional[Any]:
        return None

    def forget(
        self,
        key: str,
        session_id: Optional[str] = None,
    ) -> bool:
        return False

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        return []

    def remember_entities(
        self,
        entities: List[Entity],
        session_id: str,
    ) -> None:
        pass

    def resolve_reference(
        self,
        reference: str,
        session_id: str,
    ) -> Optional[Entity]:
        return None

    def get_stats(self) -> MemoryStats:
        return MemoryStats()

    def clear_session(self, session_id: str) -> int:
        return 0

    def clear_expired(self) -> int:
        return 0


class InMemoryMemory:
    """
    OPUS-311: In-memory implementation of MemoryProtocol.

    Simple dict-based storage. For production, use a persistent store.
    """

    # Reference patterns for entity resolution
    ORDINAL_MAP = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "last": -1,
        "1st": 1,
        "2nd": 2,
        "3rd": 3,
        "4th": 4,
        "5th": 5,
    }

    PRONOUN_TYPES = {
        "it": None,  # Last single entity
        "that": None,
        "this": None,
        "them": None,  # Last list
        "those": None,
    }

    def __init__(self):
        # {(session_id, key): MemoryEntry}
        self._store: Dict[tuple, MemoryEntry] = {}
        # {session_id: List[Entity]} - last entities mentioned
        self._entities: Dict[str, List[Entity]] = {}

    def _make_key(self, key: str, session_id: Optional[str]) -> tuple:
        return (session_id or "__global__", key)

    def remember(
        self,
        key: str,
        value: Any,
        session_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        expires_at = None
        if ttl_seconds is not None:
            from datetime import timedelta

            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

        entry = MemoryEntry(
            key=key,
            value=value,
            session_id=session_id,
            expires_at=expires_at,
            tags=tags or [],
        )
        self._store[self._make_key(key, session_id)] = entry

    def recall(
        self,
        key: str,
        session_id: Optional[str] = None,
    ) -> Optional[Any]:
        store_key = self._make_key(key, session_id)
        entry = self._store.get(store_key)

        if entry is None:
            return None

        if entry.is_expired:
            del self._store[store_key]
            return None

        return entry.value

    def forget(
        self,
        key: str,
        session_id: Optional[str] = None,
    ) -> bool:
        store_key = self._make_key(key, session_id)
        if store_key in self._store:
            del self._store[store_key]
            return True
        return False

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        query_lower = query.lower()
        results = []

        for (sid, _), entry in self._store.items():
            # Filter by session if specified
            if session_id is not None and sid != session_id:
                continue

            # Skip expired
            if entry.is_expired:
                continue

            # Match key or tags
            if query_lower in entry.key.lower():
                results.append(entry)
            elif any(query_lower in tag.lower() for tag in entry.tags):
                results.append(entry)

        # Sort by newest first
        results.sort(key=lambda e: e.created_at, reverse=True)
        return results[:limit]

    def remember_entities(
        self,
        entities: List[Entity],
        session_id: str,
    ) -> None:
        # Assign positions
        for i, entity in enumerate(entities):
            entity.position = i + 1
        self._entities[session_id] = entities

    def resolve_reference(
        self,
        reference: str,
        session_id: str,
    ) -> Optional[Entity]:
        entities = self._entities.get(session_id, [])
        if not entities:
            return None

        ref_lower = reference.lower().strip()

        # Check ordinals: "the second one", "2nd"
        for word in ref_lower.split():
            if word in self.ORDINAL_MAP:
                pos = self.ORDINAL_MAP[word]
                if pos == -1:  # "last"
                    return entities[-1] if entities else None
                if 1 <= pos <= len(entities):
                    return entities[pos - 1]

        # Check pronouns: "it", "that"
        if ref_lower in self.PRONOUN_TYPES or "the one" in ref_lower:
            # Return last single entity
            return entities[-1] if entities else None

        # Check by type: "the agent", "that task"
        for entity in reversed(entities):
            if entity.type.lower() in ref_lower:
                return entity
            if entity.name.lower() in ref_lower:
                return entity

        return None

    def get_stats(self) -> MemoryStats:
        now = datetime.now()
        expired = sum(1 for e in self._store.values() if e.is_expired)
        sessions = len(set(sid for sid, _ in self._store.keys() if sid != "__global__"))

        entries = list(self._store.values())
        oldest = min((e.created_at for e in entries), default=None)
        newest = max((e.created_at for e in entries), default=None)

        return MemoryStats(
            total_entries=len(self._store),
            expired_entries=expired,
            sessions_tracked=sessions,
            oldest_entry=oldest,
            newest_entry=newest,
        )

    def clear_session(self, session_id: str) -> int:
        keys_to_remove = [k for k in self._store.keys() if k[0] == session_id]
        for k in keys_to_remove:
            del self._store[k]
        if session_id in self._entities:
            del self._entities[session_id]
        return len(keys_to_remove)

    def clear_expired(self) -> int:
        keys_to_remove = [k for k, e in self._store.items() if e.is_expired]
        for k in keys_to_remove:
            del self._store[k]
        return len(keys_to_remove)


def get_memory_safe() -> MemoryProtocol:
    """
    Get Memory via ServiceRegistry with NullMemory fallback.

    OPUS-311: Use this for guaranteed non-None return.
    """
    try:
        from vibe_core.di import ServiceRegistry

        memory = ServiceRegistry.get(MemoryProtocol)
        if memory is not None:
            return memory
    except ImportError:
        pass

    return NullMemory()
