"""
THE OUROBOROS PROTOCOL - _ouroboros.py
======================================

"anantaś cāsmi nāgānāṁ"
"Among the Nagas I am Ananta." (BG 10.29)

Ananta Shesha = The Infinite Remainder
    - Ananta (Time/Events) = The eternal loop
    - Shesha (Space/State) = What remains after dissolution

OUROBOROS = The serpent eating its own tail
    - Self-healing through self-consumption
    - The system that survives its own death
    - Pralaya (dissolution) → Srishti (creation) cycle

ARCHITECTURAL POSITION (from PROMPT.md):
    Layer -2: Prakriti (State Substrate)
    Layer -1: AnantaShesha (THIS - Bridge)
    Layer  0: Ouroboros (System + NAGA)
    Layer  1: Services

THE THREE BODIES (Sthula, Prana, Purusha):
    STHULA (Physical):  Ledger + Git (immutable history)
    PRANA (Vital):      Runtime state (survives restart via snapshot)
    PURUSHA (Soul):     Identity (constant even when body dies)

SELF-HEALING PATTERNS (from PROMPT.md):
    1. Arjuna-Pattern: Self-heal over crash
    2. Pralaya-Pattern: Graceful degradation
    3. Verification before Trust

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (HALVES, KSETRAJNA, TRINITY)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = TRINITY
__genesis__ = "0xd301e9ab"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import (
    Callable,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    Quarter,
    PARAMPARA,
    KSETRA_COUNT,
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
)
from vibe_core.mahamantra.protocols._seed import MALA, TRINITY


# =============================================================================
# OUROBOROS CONSTANTS - The Eternal Mathematics (DERIVED FROM _seed.py)
# =============================================================================

# The serpent has no beginning or end - but we count in cycles
OUROBOROS_CYCLE: Final[int] = MALA  # 108 = One mala = one complete cycle

# Three Bodies (Tri-Deha)
BODY_COUNT: Final[int] = TRINITY  # 3

# Layer positions
LAYER_PRAKRITI: Final[int] = -HALVES  # State Substrate
LAYER_SHESHA: Final[int] = -KSETRAJNA  # This bridge
LAYER_OUROBOROS: Final[int] = 0  # System level
LAYER_SERVICE: Final[int] = KSETRAJNA  # Application level


# =============================================================================
# THE THREE BODIES (Tri-Deha Doctrine)
# =============================================================================


class BodyType(str, Enum):
    """
    The Three Bodies from PROMPT.md.

    Data must be correctly placed in one of these layers.
    """

    STHULA = "sthula"  # Physical: Ledger + Git (immutable)
    PRANA = "prana"  # Vital: Runtime state (snapshot-able)
    PURUSHA = "purusha"  # Soul: Identity (eternal)


class BodyHealth(str, Enum):
    """Health state of a body."""

    PRISTINE = "pristine"  # Perfect
    HEALTHY = "healthy"  # Normal operation
    DEGRADED = "degraded"  # Partial failure
    CRITICAL = "critical"  # Near death
    DISSOLVED = "dissolved"  # Pralaya state


# =============================================================================
# WATERTIGHT TYPEDDICTS - No Dict[str, Any]
# =============================================================================


class GeneManifestData(TypedDict, total=False):
    """Manifest for a registered gene. WATERTIGHT."""

    name: str
    version: str
    capabilities: List[str]
    dependencies: List[str]
    layer: int


class GeneStatusData(TypedDict, total=False):
    """Status of a registered gene. WATERTIGHT."""

    name: str
    state: str  # GeneActivationState value
    health: str  # BodyHealth value
    last_heartbeat: str
    error_message: str


class HeartbeatData(TypedDict):
    """System heartbeat result. WATERTIGHT."""

    uptime_seconds: float
    genes_registered: int
    capabilities_available: int
    events_processed: int
    last_heartbeat: str
    health: str
    cycle_count: int


class ViolationData(TypedDict, total=False):
    """Data for violation events. WATERTIGHT."""

    file: str
    rule: str
    line: int
    message: str
    severity: str
    source: str
    body: str  # Which body was violated


class HealingRequestData(TypedDict, total=False):
    """Data for healing request events. WATERTIGHT."""

    target: str
    reason: str
    source: str
    pattern: str  # Which pattern to apply (arjuna, pralaya)
    body: str  # Which body needs healing


class LoopDetectionData(TypedDict, total=False):
    """Data for loop detection events. WATERTIGHT."""

    loop_id: str
    iterations: int
    pattern: str
    files_affected: List[str]
    is_healing: bool  # True if this is intentional self-healing


class PralayaData(TypedDict, total=False):
    """Data for dissolution/shutdown events. WATERTIGHT."""

    reason: str
    bodies_saved: List[str]
    snapshot_path: str
    graceful: bool


# =============================================================================
# GENE ACTIVATION STATES
# =============================================================================


class GeneActivationState(str, Enum):
    """Activation state of a gene (component)."""

    DORMANT = "dormant"  # Registered but not active
    ACTIVATING = "activating"  # Starting up
    ACTIVE = "active"  # Running normally
    HEALING = "healing"  # Self-healing in progress
    DISSOLVING = "dissolving"  # Shutting down gracefully
    DEAD = "dead"  # Failed, awaiting resurrection


# =============================================================================
# HEALING PATTERNS (from PROMPT.md)
# =============================================================================


class HealingPattern(str, Enum):
    """
    Self-healing patterns from PROMPT.md.

    ARJUNA: Self-heal over crash
        - Critical component missing → Reinitialize
        - Dependency None → Lazy-init with default
        - Corrupt state → Reset to known good

    PRALAYA: Graceful degradation
        - Shutdown → Save state before death
        - Save failed → Emergency flush, log, die
        - Resources → Always release (finally)

    RESURRECTION: Phoenix from ashes
        - After death → Check for snapshot
        - Snapshot valid → Restore and continue
        - No snapshot → Fresh genesis
    """

    ARJUNA = "arjuna"  # Self-heal over crash
    PRALAYA = "pralaya"  # Graceful degradation
    RESURRECTION = "resurrection"  # Rise from death


# =============================================================================
# EVENT TYPES
# =============================================================================


class OuroborosEventType(str, Enum):
    """Typed events for the Ouroboros system."""

    # Lifecycle
    GENE_REGISTERED = "gene.registered"
    GENE_ACTIVATED = "gene.activated"
    GENE_DEACTIVATED = "gene.deactivated"
    GENE_DIED = "gene.died"

    # Violations
    VIOLATION_DETECTED = "violation.detected"
    LOOP_DETECTED = "loop.detected"

    # Healing
    HEALING_REQUESTED = "healing.requested"
    HEALING_STARTED = "healing.started"
    HEALING_COMPLETED = "healing.completed"
    HEALING_FAILED = "healing.failed"

    # Bodies
    BODY_SNAPSHOT = "body.snapshot"
    BODY_RESTORED = "body.restored"
    BODY_CORRUPTED = "body.corrupted"

    # System
    HEARTBEAT = "system.heartbeat"
    PRALAYA_INITIATED = "system.pralaya"
    SRISHTI_INITIATED = "system.srishti"  # Creation after dissolution


# =============================================================================
# SYSTEM EVENT (WATERTIGHT)
# =============================================================================


@dataclass(frozen=True)
class OuroborosEvent:
    """
    Typed event for Ouroboros communication.

    WATERTIGHT: No Any types. Event data is typed per event_type.
    """

    event_type: OuroborosEventType
    source: str  # Gene name or "system"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Typed payloads (only one should be set based on event_type)
    violation: Optional[ViolationData] = None
    healing: Optional[HealingRequestData] = None
    loop: Optional[LoopDetectionData] = None
    pralaya: Optional[PralayaData] = None
    heartbeat: Optional[HeartbeatData] = None
    gene_status: Optional[GeneStatusData] = None


# =============================================================================
# GENE PROTOCOL (What can be registered)
# =============================================================================


@runtime_checkable
class OuroborosGene(Protocol):
    """
    Protocol for components that register with Ouroboros.

    A "Gene" is any component that:
    1. Has a manifest (identity)
    2. Can receive events
    3. Can be activated/deactivated
    4. Can report health
    """

    @property
    def manifest(self) -> GeneManifestData:
        """Return gene manifest."""
        ...

    @property
    def state(self) -> GeneActivationState:
        """Return current activation state."""
        ...

    def activate(self) -> bool:
        """Activate the gene. Returns True on success."""
        ...

    def deactivate(self) -> bool:
        """Deactivate the gene. Returns True on success."""
        ...

    def on_event(self, event: OuroborosEvent) -> None:
        """Handle an event from the system."""
        ...

    def get_health(self) -> BodyHealth:
        """Return current health status."""
        ...

    def snapshot(self) -> Optional[str]:
        """Create snapshot of state. Returns path or None."""
        ...

    def restore(self, snapshot_path: str) -> bool:
        """Restore from snapshot. Returns True on success."""
        ...


# =============================================================================
# HOST PROTOCOL (The Ouroboros itself)
# =============================================================================


@runtime_checkable
class OuroborosHost(Protocol):
    """
    Protocol for the Ouroboros system (AnantaShesha).

    The Host:
    1. Registers genes
    2. Routes events
    3. Monitors health
    4. Initiates healing
    5. Manages lifecycle (pralaya/srishti)
    """

    def register_gene(self, gene: OuroborosGene) -> bool:
        """Register a gene with the system."""
        ...

    def unregister_gene(self, name: str) -> bool:
        """Unregister a gene by name."""
        ...

    def get_gene(self, name: str) -> Optional[OuroborosGene]:
        """Get a registered gene by name."""
        ...

    def has_capability(self, capability: str) -> bool:
        """Check if any gene provides a capability."""
        ...

    def emit_event(self, event: OuroborosEvent) -> None:
        """Emit event to all listeners."""
        ...

    def subscribe(self, event_type: OuroborosEventType, gene_name: str) -> None:
        """Subscribe a gene to an event type."""
        ...

    def heartbeat(self) -> HeartbeatData:
        """Return system heartbeat."""
        ...

    def request_healing(self, target: str, pattern: HealingPattern, reason: str) -> None:
        """Request healing for a target using specified pattern."""
        ...

    def initiate_pralaya(self, reason: str) -> PralayaData:
        """Initiate graceful shutdown (dissolution)."""
        ...

    def initiate_srishti(self) -> bool:
        """Initiate creation after dissolution."""
        ...


# =============================================================================
# BODY MANAGER PROTOCOL
# =============================================================================


@runtime_checkable
class BodyManager(Protocol):
    """
    Protocol for managing the Three Bodies.

    Ensures data is correctly placed:
    - STHULA: Immutable (Ledger + Git)
    - PRANA: Snapshot-able (Runtime)
    - PURUSHA: Eternal (Identity)
    """

    def get_body_health(self, body: BodyType) -> BodyHealth:
        """Get health of a specific body."""
        ...

    def snapshot_body(self, body: BodyType) -> Optional[str]:
        """Snapshot a body. Returns path or None."""
        ...

    def restore_body(self, body: BodyType, snapshot_path: str) -> bool:
        """Restore a body from snapshot."""
        ...

    def verify_body(self, body: BodyType) -> Tuple[bool, List[str]]:
        """Verify body integrity. Returns (valid, violations)."""
        ...

    def locate_data(self, data_key: str) -> Optional[BodyType]:
        """Determine which body should hold a piece of data."""
        ...


# =============================================================================
# HEALER PROTOCOL
# =============================================================================


@runtime_checkable
class OuroborosHealer(Protocol):
    """
    Protocol for self-healing implementation.

    Implements the healing patterns from PROMPT.md.
    """

    def can_heal(self, target: str, pattern: HealingPattern) -> bool:
        """Check if healing is possible."""
        ...

    def heal_arjuna(self, target: str, reason: str) -> bool:
        """
        Arjuna Pattern: Self-heal over crash.

        - Critical component missing → Reinitialize
        - Dependency None → Lazy-init with default
        - Corrupt state → Reset to known good
        """
        ...

    def heal_pralaya(self, target: str, reason: str) -> bool:
        """
        Pralaya Pattern: Graceful degradation.

        - Save state before death
        - Emergency flush if save fails
        - Always release resources
        """
        ...

    def heal_resurrection(self, target: str) -> bool:
        """
        Resurrection Pattern: Rise from death.

        - Check for snapshot
        - Restore if valid
        - Fresh genesis if no snapshot
        """
        ...


# =============================================================================
# NULL IMPLEMENTATIONS (for testing/fallback)
# =============================================================================


class NullGene:
    """Null implementation of OuroborosGene."""

    def __init__(self, name: str = "null") -> None:
        self._name = name
        self._state = GeneActivationState.DORMANT

    @property
    def manifest(self) -> GeneManifestData:
        return GeneManifestData(
            name=self._name,
            version="0.0.0",
            capabilities=[],
            dependencies=[],
            layer=LAYER_SERVICE,
        )

    @property
    def state(self) -> GeneActivationState:
        return self._state

    def activate(self) -> bool:
        self._state = GeneActivationState.ACTIVE
        return True

    def deactivate(self) -> bool:
        self._state = GeneActivationState.DORMANT
        return True

    def on_event(self, event: OuroborosEvent) -> None:
        pass  # Null implementation ignores events

    def get_health(self) -> BodyHealth:
        return BodyHealth.HEALTHY

    def snapshot(self) -> Optional[str]:
        return None  # Null has no state to snapshot

    def restore(self, snapshot_path: str) -> bool:
        return True  # Always succeeds (nothing to restore)


# =============================================================================
# THE OUROBOROS PROTOCOL - Self-Definition
# =============================================================================


class OuroborosProtocol(MahamantraProtocolBase):
    """
    The Ouroboros Protocol.

    Position 14 (SHUKA) - The narrator, the one who sees the cycle
    Level -1 (SHESHA) - The bridge layer
    Quarter MOKSHA - Liberation, the end that is the beginning

    "Among the Nagas I am Ananta" - The infinite serpent.

    This protocol defines the eternal loop:
    - Self-healing (Arjuna)
    - Graceful death (Pralaya)
    - Resurrection (Srishti)

    The Ouroboros never truly dies. It consumes itself to be reborn.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="OuroborosProtocol",
        mahajana="shuka",  # The narrator who sees past, present, future
        position=14,
        level=Level.SUBSTRATE,  # Layer -1
        quarter=Quarter.MOKSHA,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "gene_registry",
            "event_routing",
            "health_monitoring",
            "self_healing",
            "graceful_degradation",
            "resurrection",
            "body_management",
            "loop_detection",
        ],
        requires=["CoreProtocol"],
        opcodes=["FLUSH"],  # Shuka's opcode - release/output
    )


# =============================================================================
# VALIDATION
# =============================================================================

_valid, _violations = OuroborosProtocol.validate()
assert _valid, f"OuroborosProtocol failed validation: {_violations}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "OUROBOROS_CYCLE",
    "BODY_COUNT",
    "LAYER_PRAKRITI",
    "LAYER_SHESHA",
    "LAYER_OUROBOROS",
    "LAYER_SERVICE",
    # Body types
    "BodyType",
    "BodyHealth",
    # Gene states
    "GeneActivationState",
    # Healing patterns
    "HealingPattern",
    # Event types
    "OuroborosEventType",
    # TypedDicts (WATERTIGHT)
    "GeneManifestData",
    "GeneStatusData",
    "HeartbeatData",
    "ViolationData",
    "HealingRequestData",
    "LoopDetectionData",
    "PralayaData",
    # Event
    "OuroborosEvent",
    # Protocols
    "OuroborosGene",
    "OuroborosHost",
    "BodyManager",
    "OuroborosHealer",
    # Null implementation
    "NullGene",
    # The Protocol
    "OuroborosProtocol",
]
