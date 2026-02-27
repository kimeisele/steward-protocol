"""
LOG PROTOCOLS - The Veda of Observation
========================================

Defines how the system interacts with the Akasha (Logs).
Separates Space (Seeking), Meaning (Indexing), and Flow (Streaming).
"""

from __future__ import annotations

from datetime import datetime
from typing import Generator, List, Optional, Protocol

from .entry import LogEntry


class LogSeeker(Protocol):
    """O(log N) Temporal Navigation."""

    def find_offset(self, target: datetime) -> int:
        """Returns the exact byte offset for the first entry >= target."""
        ...


class LogIndexer(Protocol):
    """O(1) Holographic Resonance Mapping."""

    def resolve(self, resonance_key: int) -> List[int]:
        """Returns list of offsets matching the resonance key."""
        ...


class LogReader(Protocol):
    """The High-Level Unified Interface."""

    def stream(
        self, start: datetime, end: Optional[datetime] = None, level: Optional[str] = None
    ) -> Generator[LogEntry, None, None]:
        """Streams entries from the substrate."""
        ...

    def get_at_offset(self, offset: int) -> Optional[LogEntry]:
        """Direct access to a specific point in the Akasha."""
        ...
