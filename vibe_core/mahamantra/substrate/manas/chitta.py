"""
CHITTA — Perception Pool (Manas Substrate)
===========================================

Receives raw perceptions, deduplicates, returns clean list.
Extracted from opus_assistant/manas/chitta.py — generic, no plugin logic.

Dedup key: (source, content[:60]) — prevents duplicate perceptions
from the same source about the same topic.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Sequence, Tuple

from vibe_core.mahamantra.protocols._manas import PerceptionEntry

logger = logging.getLogger("MAHAMANTRA.MANAS.CHITTA")

# Dedup key length — first 60 chars of content
_DEDUP_CONTENT_LEN = 60


class Chitta:
    """Perception pool — receive, dedup, emit clean list."""

    def __init__(self) -> None:
        self._pool: List[PerceptionEntry] = []
        self._seen: Dict[Tuple[str, str], bool] = {}

    def receive(self, entry: PerceptionEntry) -> None:
        """Add a single perception to the pool."""
        self._pool.append(entry)

    def receive_batch(self, entries: Sequence[PerceptionEntry]) -> None:
        """Add multiple perceptions to the pool."""
        self._pool.extend(entries)

    def process(self) -> Sequence[PerceptionEntry]:
        """Dedup by (source, content[:60]), clear pool, return clean list."""
        seen: Dict[Tuple[str, str], bool] = {}
        clean: List[PerceptionEntry] = []

        for entry in self._pool:
            key = (entry.source, entry.content[:_DEDUP_CONTENT_LEN])
            if key not in seen:
                seen[key] = True
                clean.append(entry)

        dupes = len(self._pool) - len(clean)
        if dupes > 0:
            logger.debug("Chitta dedup: %d → %d (-%d dupes)", len(self._pool), len(clean), dupes)

        self._pool.clear()
        self._seen = seen
        return clean

    @property
    def pool_size(self) -> int:
        """Current number of unprocessed perceptions."""
        return len(self._pool)
