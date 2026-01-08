"""
UNION PROTOCOL - The State of the Union (Layer 1)

"Ekam Sat Vipra Bahudha Vadanti" - Truth is One, the wise call it by many names.

This protocol provides a unified view of all living entities (Nagas, Agents, Plugins)
and traces their heritage back to their respective Protocols.

GAD-000 COMPLIANT:
- Discoverability: get_union_summary()
- Observability: EntityStatus dataclass
- Parseability: Typed returns
- Composability: Iterator for streaming
- Idempotency: Read-only operations
- Recoverability: timeout + partial handling
- Identity: BindingCertificate integration (Anti-Mayavad)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Protocol, runtime_checkable

# Link to Layer -1 (Substrate) for Truth Verification
from vibe_core.protocols.substrate import BindingCertificate


@dataclass
class EntityStatus:
    """
    The status of a living entity in the Union.

    Now includes ANTI-MAYAVAD proofs (Certificate).
    Without 'certificate', the entity is a GHOST (unverified).
    """

    id: str
    type: str  # "naga", "agent", "plugin", "kernel"
    status: str  # "ACTIVE", "DORMANT", "DEGRADED", "GHOST"
    protocol: Optional[str]  # The Protocol class path this entity obeys
    is_living: bool  # True if heartbeat is fresh
    tuv_score: float  # Compliance score from 0.0 to 1.0
    last_heartbeat: Optional[datetime]

    # ANTI-MAYAVAD: The Chain of Custody
    # Who signed this entity into existence?
    certificate: Optional[BindingCertificate] = None

    # MANTRA RESONANCE: The Pulse Quality
    # How well is it chanting? (0.0 - 1.0)
    resonance_score: float = 0.0

    @property
    def is_verified(self) -> bool:
        """
        True only if the entity holds a valid BindingCertificate.
        Ghosts return False.
        """
        return self.certificate is not None


@dataclass
class UnionScanResult:
    """GAD-000 Recoverability: Result of a union scan with partial handling."""

    entities: List[EntityStatus] = field(default_factory=list)
    complete: bool = True  # False if scan was interrupted
    scanned_count: int = 0
    error_count: int = 0
    ghost_count: int = 0  # Entities without certificates
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
    - Identity via Sovereign Verification
    """

    def get_living_entities(
        self,
        timeout_seconds: Optional[float] = None,
        require_verified: bool = False,  # Filter out Ghosts
    ) -> Iterator[EntityStatus]:
        """
        List all entities that are currently active and registered.
        Traces every entity back to its Protocol heritage.

        Args:
            timeout_seconds: Optional timeout (GAD-000 Recoverability).
            require_verified: If True, only return entities with BindingCertificates.

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
        Includes population counts, average compliance scores, and GHOST COUNT.
        """
        ...

    def get_registry_slots(self) -> List[Optional[EntityStatus]]:
        """
        THE 37 SLOTS (Sri Yantra Configuration).

        Returns a fixed-size list of length 37 (REGISTRY_SIZE).

        Slot 0: The Sovereign (Guru/Owner) - MUST BE VERIFIED.
        Slots 1-4:  The Inner Circle (Guardians).
        Slots 5-36: The Field (Kshetra / Workloads).
        """
        ...

    @property
    def divine_hash(self) -> str:
        """
        The 1972 Standard Hash.
        Represents the Merkle Root of the current Union State.
        """
        ...
