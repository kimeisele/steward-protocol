"""
KALIYA Protocol - Die Quarantäne (Isolation Protocol)

Kaliya - Von Krishna gebändigt, nicht getötet.
PROMPT.md: Isolation without destruction.

Responsibilities:
- Isolate misbehaving components WITHOUT killing them
- Track violations per component
- Auto-quarantine on threshold
- Escalate to sovereign (37th) after repeated quarantines
"""

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

from vibe_core.protocols.correction import (
    CorrectionHandler,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga.types import NagaStatus, NagaType


@dataclass
class QuarantineStatus:
    """Status of a quarantine operation."""

    component_id: str
    is_quarantined: bool
    duration_seconds: float = 0.0
    violation_count: int = 0
    is_escalated: bool = False
    signed_by: Optional[str] = None


@runtime_checkable
class KaliyaProtocol(Protocol):
    """
    Kaliya - Die Quarantäne. Von Krishna gebändigt, nicht getötet.

    PROMPT.md: Isolation without destruction.

    Responsibilities:
    - Isolate misbehaving components WITHOUT killing them
    - Track violations per component
    - Auto-quarantine on threshold
    - Escalate to sovereign (37th) after repeated quarantines

    Integration:
    - Registers as handler for DriftSource.RELIABILITY
    - Detects reliability drift (component misbehavior)
    - Heals by isolating unreliable components

    Usage:
        kaliya = ServiceRegistry.get(KaliyaProtocol)
        kaliya.quarantine(component_id, reason)
        if kaliya.is_quarantined(component_id):
            # Component is isolated
    """

    def quarantine(
        self,
        component_id: str,
        reason: str,
        duration_seconds: Optional[float] = None,
    ) -> QuarantineStatus:
        """Put a component in quarantine."""
        ...

    def is_quarantined(self, component_id: str) -> bool:
        """Check if component is currently quarantined."""
        ...

    def release(self, component_id: str) -> None:
        """Release component from quarantine (fails if escalated)."""
        ...

    def record_violation(self, component_id: str) -> None:
        """Record a violation, may trigger auto-quarantine."""
        ...

    def get_violation_count(self, component_id: str) -> int:
        """Get current violation count for component."""
        ...

    def is_escalated(self, component_id: str) -> bool:
        """Check if component has been escalated to sovereign."""
        ...

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.RELIABILITY."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullKaliya:
    """No-op Kaliya for when quarantine is unavailable."""

    def quarantine(
        self,
        component_id: str,
        reason: str,
        duration_seconds: Optional[float] = None,
    ) -> QuarantineStatus:
        return QuarantineStatus(component_id=component_id, is_quarantined=False)

    def is_quarantined(self, component_id: str) -> bool:
        return False

    def release(self, component_id: str) -> None:
        pass

    def record_violation(self, component_id: str) -> None:
        pass

    def get_violation_count(self, component_id: str) -> int:
        return 0

    def is_escalated(self, component_id: str) -> bool:
        return False

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_kaliya",
                message="Kaliya not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.KALIYA, healthy=False, message="Not initialized")
