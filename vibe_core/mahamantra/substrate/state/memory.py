"""
MAHAMANTRA MEMORY - The Akshara (Indestructible)
================================================

Implements a generic, persistent Key-Value memory for the Mahamantra.
Complies with `vibe_core.protocols.memory.MemoryProtocol`.
Persists to `.vibe/state/mahamantra/memory.json`.

"akṣarāṇām a-kāro 'smi" - Of letters I am the letter A.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import asdict

from vibe_core.protocols.memory import MemoryProtocol, MemoryEntry, Entity, MemoryStats

logger = logging.getLogger("Mahamantra.Memory")


class PersistentMemory:
    """
    JSON-backed persistent memory implementing MemoryProtocol.
    """

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._state_dir = self._workspace / ".vibe" / "state" / "mahamantra"
        self._memory_file = self._state_dir / "memory.json"
        self._store: Dict[str, MemoryEntry] = {}
        self._entities: Dict[str, List[Entity]] = {}

        self._load()

    def _get_key(self, key: str, session_id: Optional[str]) -> str:
        return f"{session_id or 'global'}::{key}"

    def _load(self):
        """Load from disk."""
        if not self._memory_file.exists():
            return

        try:
            data = json.loads(self._memory_file.read_text())
            # Rehydrate MemoryEntries
            for k, v in data.get("store", {}).items():
                self._store[k] = MemoryEntry(**v)
            # Rehydrate Entities (if necessary, simple dict for now)
            # Entities are transient in this simple impl unless we persist them too
            # Let's persist them for now
            # (Skipping complex Entity hydration for MVP, focusing on KV)
            logger.info(f"Loaded {len(self._store)} memories.")
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")

    def _save(self):
        """Atomic save to disk."""
        try:
            self._state_dir.mkdir(parents=True, exist_ok=True)

            # Serialize
            data = {
                "store": {k: asdict(v) for k, v in self._store.items() if not v.is_expired},
                "updated_at": datetime.now().isoformat(),
            }

            temp = self._memory_file.with_suffix(".tmp")
            temp.write_text(json.dumps(data, indent=2, default=str))
            temp.replace(self._memory_file)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    # --- MemoryProtocol Implementation ---

    def remember(
        self,
        key: str,
        value: object,
        session_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Store a value."""
        store_key = self._get_key(key, session_id)

        expires_at = None
        if ttl_seconds:
            from datetime import timedelta

            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

        entry = MemoryEntry(
            key=key,
            value=value,
            session_id=session_id,
            created_at=datetime.now(),
            expires_at=expires_at,
            tags=tags or [],
        )

        self._store[store_key] = entry
        self._save()
        logger.debug(f"Remembered: {key}")

    def recall(
        self,
        key: str,
        session_id: Optional[str] = None,
    ) -> Optional[object]:
        """Retrieve a value."""
        store_key = self._get_key(key, session_id)
        entry = self._store.get(store_key)

        if not entry:
            return None

        if entry.is_expired:
            del self._store[store_key]
            self._save()
            return None

        return entry.value

    def forget(
        self,
        key: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """Remove a value."""
        store_key = self._get_key(key, session_id)
        if store_key in self._store:
            del self._store[store_key]
            self._save()
            return True
        return False

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """Simple search."""
        query = query.lower()
        results = []
        for k, entry in self._store.items():
            if session_id and entry.session_id != session_id:
                continue
            if query in entry.key.lower() or any(query in t.lower() for t in entry.tags):
                results.append(entry)
        return results[:limit]

    def remember_entities(self, entities: List[Entity], session_id: str) -> None:
        self._entities[session_id] = entities

    def resolve_reference(self, reference: str, session_id: str) -> Optional[Entity]:
        # Simple resolution for MVP
        entities = self._entities.get(session_id, [])
        if not entities:
            return None
        if "last" in reference:
            return entities[-1]
        return None

    def get_stats(self) -> MemoryStats:
        return MemoryStats(total_entries=len(self._store))

    def clear_session(self, session_id: str) -> int:
        keys = [k for k in self._store if k.startswith(f"{session_id}::")]
        for k in keys:
            del self._store[k]
        self._save()
        return len(keys)

    def clear_expired(self) -> int:
        keys = [k for k, v in self._store.items() if v.is_expired]
        for k in keys:
            del self._store[k]
        self._save()
        return len(keys)
