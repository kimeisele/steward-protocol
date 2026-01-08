"""
UNION PROTOCOL - The State of the Union (Layer 1)

"Ekam Sat Vipra Bahudha Vadanti" - Truth is One, the wise call it by many names.

This protocol provides a unified view of all living entities (Nagas, Agents, Plugins)
and traces their heritage back to their respective Protocols.

GAD-000 COMPLIANT:
- Discoverability: get_union_summary()
- Observability: EntityStatus dataclass
- Parseability: Typed returns
- Composability: Iterator for streaming ← RED-006 FIX
- Idempotency: Read-only operations
- Recoverability: timeout + partial handling ← RED-007 FIX
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Protocol, runtime_checkable


@dataclass
class EntityStatus:
    """The status of a living entity in the Union."""

    id: str
    type: str  # "naga", "agent", "plugin", "kernel"
    status: str  # "ACTIVE", "DORMANT", "DEGRADED"
    protocol: Optional[str]  # The Protocol class path this entity obeys
    is_living: bool  # True if heartbeat is fresh
    tuv_score: float  # Compliance score from 0.0 to 1.0
    last_heartbeat: Optional[datetime]


@dataclass
class UnionScanResult:
    """GAD-000 Recoverability: Result of a union scan with partial handling."""

    entities: List[EntityStatus] = field(default_factory=list)
    complete: bool = True  # False if scan was interrupted
    scanned_count: int = 0
    error_count: int = 0
    timeout_reached: bool = False
    errors: List[str] = field(default_factory=list)


@runtime_checkable
class UnionProtocol(Protocol):
    """
    The Union Protocol.

    Provides the 'State of the Union' report.
    Used by the Gateway to present the living reality of the system.

    GAD-000:
    - Composability via Iterator (streaming)
    - Recoverability via timeout + partial results
    """

    def get_living_entities(
        self,
        timeout_seconds: Optional[float] = None,  # RED-007 FIX
    ) -> Iterator[EntityStatus]:  # RED-006 FIX: Iterator, not List
        """
        List all entities that are currently active and registered.
        Traces every entity back to its Protocol heritage.

        Args:
            timeout_seconds: Optional timeout (GAD-000 Recoverability).

        Returns:
            Iterator of EntityStatus (streaming for large unions).
        """
        ...

    def get_living_entities_safe(
        self,
        timeout_seconds: float = 5.0,
    ) -> UnionScanResult:
        """
        GAD-000 Recoverability: Scan with timeout + partial result handling.

        Args:
            timeout_seconds: Max time for scan.

        Returns:
            UnionScanResult with partial data if timeout reached.
        """
        ...

    def get_union_summary(self) -> Dict[str, object]:
        """
        Get high-level statistics of the Union.
        Includes population counts and average compliance scores.
        """
        ...
