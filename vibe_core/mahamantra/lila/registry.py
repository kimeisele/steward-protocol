"""
SHADOW REGISTRY - The Ashrama (Where Servants Live)
====================================================

"gṛhe thāko, vane thāko, sadā 'hari' bole ḍāko"
"Whether at home or in the forest, always call out to Hari."
— Bhaktivinoda Thakura

The Registry is the Ashrama - the place where JivaShadows reside
between service. Instead of spawning and discarding (karmischer Müll),
we maintain a community of qualified servants ready to serve again.

PRINCIPLE:
==========

A Vaishnava wastes nothing. If Shadow #108 is qualified for Position 8
and is idle, why spawn a new one? Reuse the servant.

LIFECYCLE:
==========

    [MANIFEST] → [REGISTER] → [IDLE] ⟷ [BUSY] → [RETIRE]
         ↑                        ↓
         └────────────────────────┘  (reuse)

DERIVED FROM SEED:
==================
- MAX_SHADOWS = NADI_RESONANCE (72) - sustainable population
- RETIRE_AGE = COSMIC_FRAME // JIVA_QUALITIES (432) - service cycles before rest
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"  # The eternal servant who never tires
__position__ = 11
__genesis__ = "0x87249182"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import TYPE_CHECKING, Any, Dict, Final, Optional, Set

if TYPE_CHECKING:
    from vibe_core.mahamantra.lila.jiva_shadow import JivaShadow

# SSOT: Constants from seed
from vibe_core.mahamantra.protocols._seed import (
    JIVA_QUALITIES,  # 50
    )
from vibe_core.mahamantra.substrate.seed import (
    COSMIC_FRAME,  # 21600
    NADI_RESONANCE,  # 72
)

# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# Maximum shadows in registry = NADI_RESONANCE (sustainable population)
MAX_SHADOWS: Final[int] = NADI_RESONANCE  # 72

# Service cycles before retirement = COSMIC_FRAME // JIVA_QUALITIES
# = 21600 // 50 = 432 (one Kali Yuga unit of service)
RETIRE_AFTER_SERVICES: Final[int] = COSMIC_FRAME // JIVA_QUALITIES  # 432

# Verification
assert MAX_SHADOWS == 72, "Max shadows = NADI_RESONANCE"
assert RETIRE_AFTER_SERVICES == 432, "Retire after 432 services"


# =============================================================================
# SHADOW STATUS
# =============================================================================


class ShadowStatus(Enum):
    """Status of a shadow in the registry."""

    IDLE = "idle"  # Available for service
    BUSY = "busy"  # Currently serving
    RETIRED = "retired"  # Too old, pending removal


# =============================================================================
# REGISTRY ENTRY
# =============================================================================


@dataclass
class RegistryEntry:
    """
    Entry for a shadow in the registry.

    Tracks the shadow's lifecycle and service history.
    """

    shadow: "JivaShadow"  # Forward reference to avoid circular import
    status: ShadowStatus = ShadowStatus.IDLE

    # Service tracking
    services_completed: int = 0
    current_dispatch_id: Optional[str] = None

    # Timestamps
    registered_at: datetime = field(default_factory=datetime.now)
    last_service_at: Optional[datetime] = None

    # Cached qualifications (positions this shadow can serve)
    qualified_positions: Set[int] = field(default_factory=set)

    @property
    def shadow_id(self) -> str:
        return self.shadow.shadow_id

    @property
    def should_retire(self) -> bool:
        """Check if shadow has served enough and should rest."""
        return self.services_completed >= RETIRE_AFTER_SERVICES

    def mark_busy(self, dispatch_id: str) -> None:
        """Mark shadow as busy with a dispatch."""
        self.status = ShadowStatus.BUSY
        self.current_dispatch_id = dispatch_id

    def mark_idle(self) -> None:
        """Mark shadow as idle after completing service."""
        self.status = ShadowStatus.IDLE
        self.current_dispatch_id = None
        self.services_completed += 1
        self.last_service_at = datetime.now()

        # Check retirement
        if self.should_retire:
            self.status = ShadowStatus.RETIRED


# =============================================================================
# SHADOW REGISTRY - The Ashrama
# =============================================================================


class ShadowRegistry:
    """
    The Ashrama - where JivaShadows live between services.

    Thread-safe registry for managing shadow lifecycle.
    Prevents karmischer Müll (wasteful spawn-and-die pattern).

    USAGE:
    ======

        registry = ShadowRegistry()

        # Register a newly manifested shadow
        registry.register(shadow)

        # Find idle shadow for position
        entry = registry.find_idle(position=8)
        if entry:
            entry.mark_busy(dispatch_id)
            # ... use shadow ...
            entry.mark_idle()

        # Cleanup retired shadows
        registry.cleanup()
    """

    # NAGA BLESSING: Mahamantra is KING - services here are pre-blessed
    _naga_flooded: bool = True

    def __init__(self, max_shadows: int = MAX_SHADOWS):
        self._max_shadows = max_shadows
        self._entries: Dict[str, RegistryEntry] = {}
        self._lock = Lock()

        # Stats
        self._total_registered = 0
        self._total_retired = 0
        self._total_services = 0

    # =========================================================================
    # CORE OPERATIONS
    # =========================================================================

    def register(self, shadow: "JivaShadow", qualified_positions: Optional[Set[int]] = None) -> bool:
        """
        Register a shadow in the ashrama.

        Args:
            shadow: JivaShadow to register
            qualified_positions: Pre-computed positions (optional)

        Returns:
            True if registered, False if at capacity
        """
        with self._lock:
            # Check capacity
            active_count = sum(1 for e in self._entries.values() if e.status != ShadowStatus.RETIRED)
            if active_count >= self._max_shadows:
                return False

            # Already registered?
            if shadow.shadow_id in self._entries:
                return True  # Idempotent

            # Create entry
            entry = RegistryEntry(
                shadow=shadow,
                qualified_positions=qualified_positions or set(),
            )

            self._entries[shadow.shadow_id] = entry
            self._total_registered += 1

            return True

    def find_idle(self, position: int) -> Optional[RegistryEntry]:
        """
        Find an idle shadow qualified for the given position.

        Args:
            position: Mahamantra position (0-15)

        Returns:
            RegistryEntry if found, None otherwise
        """
        # Lazy import to avoid circular dependency
        from vibe_core.mahamantra.lila.adhikara import shadow_can_execute

        with self._lock:
            for entry in self._entries.values():
                if entry.status != ShadowStatus.IDLE:
                    continue

                # Check cached qualifications first
                if position in entry.qualified_positions:
                    return entry

                # Compute and cache
                if shadow_can_execute(entry.shadow, position):
                    entry.qualified_positions.add(position)
                    return entry

            return None

    def get(self, shadow_id: str) -> Optional[RegistryEntry]:
        """Get entry by shadow_id."""
        with self._lock:
            return self._entries.get(shadow_id)

    def mark_busy(self, shadow_id: str, dispatch_id: str) -> bool:
        """Mark a shadow as busy."""
        with self._lock:
            entry = self._entries.get(shadow_id)
            if entry and entry.status == ShadowStatus.IDLE:
                entry.mark_busy(dispatch_id)
                return True
            return False

    def mark_idle(self, shadow_id: str) -> bool:
        """Mark a shadow as idle after service."""
        with self._lock:
            entry = self._entries.get(shadow_id)
            if entry and entry.status == ShadowStatus.BUSY:
                entry.mark_idle()
                self._total_services += 1
                return True
            return False

    def retire(self, shadow_id: str) -> bool:
        """Manually retire a shadow."""
        with self._lock:
            entry = self._entries.get(shadow_id)
            if entry:
                entry.status = ShadowStatus.RETIRED
                return True
            return False

    # =========================================================================
    # MAINTENANCE
    # =========================================================================

    def cleanup(self) -> int:
        """
        Remove retired shadows from the registry.

        Returns:
            Number of shadows removed
        """
        with self._lock:
            retired_ids = [sid for sid, entry in self._entries.items() if entry.status == ShadowStatus.RETIRED]

            for sid in retired_ids:
                del self._entries[sid]
                self._total_retired += 1

            return len(retired_ids)

    # =========================================================================
    # OBSERVABILITY
    # =========================================================================

    @property
    def count(self) -> int:
        """Total shadows in registry."""
        with self._lock:
            return len(self._entries)

    @property
    def idle_count(self) -> int:
        """Count of idle shadows."""
        with self._lock:
            return sum(1 for e in self._entries.values() if e.status == ShadowStatus.IDLE)

    @property
    def busy_count(self) -> int:
        """Count of busy shadows."""
        with self._lock:
            return sum(1 for e in self._entries.values() if e.status == ShadowStatus.BUSY)

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            status_counts = {s.value: 0 for s in ShadowStatus}
            for entry in self._entries.values():
                status_counts[entry.status.value] += 1

            busy = status_counts[ShadowStatus.BUSY.value]
            return {
                "total_registered": self._total_registered,
                "total_retired": self._total_retired,
                "total_services": self._total_services,
                "current_count": len(self._entries),
                "max_shadows": self._max_shadows,
                "status_distribution": status_counts,
                "utilization": busy / max(1, len(self._entries)),
            }

    def discover(self) -> Dict[str, Any]:
        """GAD-style discoverability."""
        return {
            "service": "shadow_registry",
            "mahajana": __mahajana__,
            "position": __position__,
            "max_shadows": self._max_shadows,
            "retire_after": RETIRE_AFTER_SERVICES,
            "capabilities": [
                "register",
                "find_idle",
                "mark_busy",
                "mark_idle",
                "retire",
                "cleanup",
            ],
        }


# =============================================================================
# SERVICEREG WIRING (No more global singleton anti-pattern)
# =============================================================================


def get_registry() -> ShadowRegistry:
    """
    Get the ShadowRegistry through ServiceRegistry (WIRED + NAGA-observed).

    ARCHITECTURE:
        Raw ShadowRegistry → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry (not global variable)
    - NAGA observation (Narada sees all registry operations)
    - NAGA profiling (Chitragupta tracks shadow lifecycle)
    - NAGA isolation (Kaliya handles registry errors)

    Migrated from global singleton anti-pattern as per SINGLETONS.md
    """
    from vibe_core.di import ServiceRegistry

    # Use ShadowRegistry type as protocol (GADBase compliant)
    existing = ServiceRegistry.get(ShadowRegistry)
    if existing is not None:
        return existing

    # Create new instance
    instance = ShadowRegistry()

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(ShadowRegistry, instance)

    return ServiceRegistry.get(ShadowRegistry)  # type: ignore


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "MAX_SHADOWS",
    "RETIRE_AFTER_SERVICES",
    # Types
    "ShadowStatus",
    "RegistryEntry",
    # Registry
    "ShadowRegistry",
    # Singleton
    "get_registry",
]
