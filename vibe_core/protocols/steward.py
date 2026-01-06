"""
StewardProtocol - The Namesake Protocol.

"Ein Steward verwaltet einen Bereich im Auftrag eines höheren Zwecks."

This protocol defines what it means to be a STEWARD:
- Verwalter eines Bereichs (Manager of a domain)
- Hat Verantwortung über Ressourcen (Has responsibility over resources)
- Dient einem höheren Zweck (Serves a higher purpose)

Hierarchy:
    Prahlad = Head Steward (Governance)
    Each NAGA = Steward of their domain
    Kernel = Steward of the entire system

Usage:
    from vibe_core.protocols.steward import StewardProtocol

    class MyService(StewardProtocol):
        @property
        def domain(self) -> str:
            return "cache"

        def get_health(self) -> StewardHealth:
            return StewardHealth(...)

GAP-001: This protocol was identified as CRITICAL by TÜV.
The project is called "steward-protocol" but lacked a StewardProtocol.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Protocol, runtime_checkable


class StewardStatus(str, Enum):
    """Status of a Steward."""

    ACTIVE = "active"  # Functioning normally
    DEGRADED = "degraded"  # Reduced capacity
    RECOVERING = "recovering"  # Coming back online
    OFFLINE = "offline"  # Not functioning


class StewardDomain(str, Enum):
    """Well-known stewardship domains."""

    KERNEL = "kernel"  # System orchestration
    DATA = "data"  # Data persistence (Sesha)
    SECURITY = "security"  # Security enforcement (Takshaka)
    NETWORK = "network"  # Network communication (Vasuki)
    AUDIT = "audit"  # Auditing (Chitragupta)
    GOVERNANCE = "governance"  # Governance (Prahlad)
    CACHE = "cache"  # Caching (Padma)
    DISCOVERY = "discovery"  # Service discovery (Narada)
    QUARANTINE = "quarantine"  # Isolation (Kaliya)


@dataclass
class StewardHealth:
    """Health report from a Steward."""

    status: StewardStatus
    domain: str
    last_heartbeat: datetime
    resources_managed: int = 0
    errors_last_hour: int = 0
    uptime_seconds: float = 0.0
    details: Dict[str, str] = field(default_factory=dict)


@dataclass
class StewardshipReport:
    """Report on what a Steward is managing."""

    domain: str
    steward_id: str
    resources: List[str]  # What resources are under stewardship
    dependencies: List[str]  # What this steward depends on
    dependents: List[str]  # What depends on this steward
    last_audit: Optional[datetime] = None


@runtime_checkable
class StewardProtocol(Protocol):
    """
    The Steward Protocol - What every Steward MUST provide.

    A Steward is responsible for:
    1. Managing a domain of resources
    2. Reporting health status
    3. Participating in governance
    4. Serving a higher purpose (the Kernel's mission)

    NAGAs implement this to be recognized as Stewards.
    Services implement this to participate in stewardship.
    """

    # =========================================================================
    # IDENTITY
    # =========================================================================

    @property
    def domain(self) -> str:
        """The domain this Steward manages."""
        ...

    @property
    def steward_id(self) -> str:
        """Unique identifier for this Steward."""
        ...

    # =========================================================================
    # HEALTH
    # =========================================================================

    def get_health(self) -> StewardHealth:
        """Get health status of this Steward."""
        ...

    def heartbeat(self) -> datetime:
        """Record a heartbeat. Returns timestamp."""
        ...

    # =========================================================================
    # STEWARDSHIP
    # =========================================================================

    def get_stewardship_report(self) -> StewardshipReport:
        """Report on what this Steward is managing."""
        ...

    def accept_responsibility(self, resource: str) -> bool:
        """Accept responsibility for a resource. Returns success."""
        ...

    def release_responsibility(self, resource: str) -> bool:
        """Release responsibility for a resource. Returns success."""
        ...

    # =========================================================================
    # GOVERNANCE
    # =========================================================================

    def can_handle(self, request_type: str) -> bool:
        """Check if this Steward can handle a request type."""
        ...


# =============================================================================
# NULL IMPLEMENTATION
# =============================================================================


class NullSteward:
    """No-op Steward when stewardship is unavailable."""

    @property
    def domain(self) -> str:
        return "null"

    @property
    def steward_id(self) -> str:
        return "null-steward"

    def get_health(self) -> StewardHealth:
        return StewardHealth(
            status=StewardStatus.OFFLINE,
            domain="null",
            last_heartbeat=datetime.now(),
        )

    def heartbeat(self) -> datetime:
        return datetime.now()

    def get_stewardship_report(self) -> StewardshipReport:
        return StewardshipReport(
            domain="null",
            steward_id="null-steward",
            resources=[],
            dependencies=[],
            dependents=[],
        )

    def accept_responsibility(self, resource: str) -> bool:
        return False

    def release_responsibility(self, resource: str) -> bool:
        return False

    def can_handle(self, request_type: str) -> bool:
        return False


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "StewardProtocol",
    "StewardStatus",
    "StewardDomain",
    "StewardHealth",
    "StewardshipReport",
    "NullSteward",
]
