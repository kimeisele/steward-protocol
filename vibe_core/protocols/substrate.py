"""
SUBSTRATE PROTOCOLS - Layer -1 (Below NAGA LOKA)

"Om Purnamadah Purnamidam" - From the Whole comes the Whole.

This module defines the PURE INTERFACES for Ananta Shesha.
It has ZERO imports from vibe_core - it IS the foundation.

Mythological Context:
    Ananta Shesha is the infinite serpent upon whom Vishnu rests.
    He exists BEFORE creation, DURING creation, and AFTER destruction.
    He is not part of the material world - he CARRIES it.

Architectural Context:
    Layer -1: SUBSTRATE (This file) - Pure protocols, no deps
    Layer  0: NAGA LOKA - Infrastructure that implements these protocols
    Layer  1: SERVICES - Application code protected by NAGA
    Layer  2: USER - The external consumer

Design Principle (Dependency Inversion):
    - Mixins depend on IAnantaBridge (abstraction), not AnantaService (concretion)
    - AnantaService implements IAnantaBridge and injects itself into Mixins
    - The energy flows TOP-DOWN (Avatara), not bottom-up

Usage:
    # In a Mixin (Layer 0)
    from vibe_core.protocols.substrate import IGeneHost

    class SeshaMixin:
        _host: IGeneHost = None

        def bind(self, host: IGeneHost) -> None:
            self._host = host  # Injection from above

    # In AnantaService (Layer -1)
    from vibe_core.protocols.substrate import IAnantaBridge
    from vibe_core.naga.mixins import SeshaMixin  # WE import THEM

    class AnantaService(IAnantaBridge):
        def __init__(self):
            self.genes = {"sesha": SeshaMixin()}
            for gene in self.genes.values():
                gene.bind(self)  # Top-down injection
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    runtime_checkable,
)

# =============================================================================
# TYPE VARIABLES (Generic Support)
# =============================================================================

T = TypeVar("T")
GeneT = TypeVar("GeneT", bound="IGene")


# =============================================================================
# ENUMS (Pure Value Types)
# =============================================================================


class GeneActivationState(str, Enum):
    """State of a gene in the substrate."""

    DORMANT = "dormant"  # Defined but not bound
    BOUND = "bound"  # Bound to host but not active
    ACTIVE = "active"  # Fully operational
    SUSPENDED = "suspended"  # Temporarily disabled
    MUTATED = "mutated"  # Modified by flood


class SubstrateHealth(str, Enum):
    """Health status of the substrate."""

    PRISTINE = "pristine"  # Perfect state
    HEALTHY = "healthy"  # Normal operation
    DEGRADED = "degraded"  # Some issues
    CRITICAL = "critical"  # Major problems
    COLLAPSED = "collapsed"  # System failure


# =============================================================================
# DATA CLASSES (Pure Data, No Behavior)
# =============================================================================


@dataclass(frozen=True)
class GeneManifest:
    """
    Manifest describing a gene's capabilities.

    This is the "DNA sequence" - static definition of what a gene CAN do.
    The actual behavior is in the gene class itself.
    """

    name: str  # Unique identifier (e.g., "sesha", "takshaka")
    capabilities: Tuple[str, ...]  # What this gene provides
    requires: Tuple[str, ...]  # What this gene needs from host
    priority: int = 50  # Activation order (higher = earlier)
    optional: bool = False  # Can system run without this gene?


@dataclass
class GeneStatus:
    """
    Runtime status of a gene.

    This is the "RNA expression" - current state of the gene.
    """

    manifest: GeneManifest
    state: GeneActivationState
    bound_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metrics is None:
            self.metrics = {}


@dataclass
class SubstrateStatus:
    """Overall status of the Ananta Shesha substrate."""

    health: SubstrateHealth
    genes_total: int
    genes_active: int
    genes_dormant: int
    genes_failed: int
    uptime_seconds: float
    last_heartbeat: datetime
    message: str = ""


# =============================================================================
# PROTOCOLS (Pure Interfaces - The Platonic Ideals)
# =============================================================================


@runtime_checkable
class IGene(Protocol):
    """
    Protocol for a gene (Mixin) that can be bound to a host.

    A gene is a unit of capability that:
    1. Defines what it needs (via GeneManifest)
    2. Can be bound to a host (dependency injection)
    3. Can be activated/deactivated

    Genes do NOT know about AnantaService - only about IGeneHost.
    This is the Dependency Inversion Principle in action.
    """

    @property
    def manifest(self) -> GeneManifest:
        """Get the gene's manifest (static capabilities)."""
        ...

    @property
    def state(self) -> GeneActivationState:
        """Get the gene's current activation state."""
        ...

    def bind(self, host: "IGeneHost") -> None:
        """
        Bind this gene to a host.

        This is DEPENDENCY INJECTION from above.
        The host calls this method, passing itself.
        The gene stores the reference but doesn't import the host's class.

        Args:
            host: The IGeneHost that will power this gene
        """
        ...

    def activate(self) -> bool:
        """
        Activate this gene.

        Returns:
            True if activation successful, False otherwise
        """
        ...

    def deactivate(self) -> None:
        """Deactivate this gene (but keep it bound)."""
        ...

    def unbind(self) -> None:
        """Unbind from host completely."""
        ...


@runtime_checkable
class IGeneHost(Protocol):
    """
    Protocol for a host that can hold genes.

    This is the "body" that genes attach to.
    The host provides capabilities that genes need.

    AnantaService implements this protocol.
    But genes don't know that - they only know IGeneHost.
    """

    def get_gene(self, name: str) -> Optional[IGene]:
        """Get a gene by name."""
        ...

    def has_gene(self, name: str) -> bool:
        """Check if a gene is registered."""
        ...

    def get_capability(self, capability: str) -> Optional[Any]:
        """
        Get a capability from any gene that provides it.

        Args:
            capability: Name of the capability (e.g., "ledger", "validation")

        Returns:
            The capability provider, or None if not available
        """
        ...

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit an event to all listening genes.

        This is the SHANKHA (broadcast) capability at the substrate level.
        """
        ...


@runtime_checkable
class IAnantaBridge(Protocol):
    """
    The full Ananta Shesha interface.

    This extends IGeneHost with substrate-specific operations:
    - Gene registration and lifecycle
    - Flood operations (soft flood via mixin injection)
    - Health monitoring
    - Boot sequence coordination

    This is the "platonic ideal" of Ananta.
    The concrete AnantaService implements this.
    External code programs against THIS interface, not the class.
    """

    # =========================================================================
    # Gene Lifecycle
    # =========================================================================

    def register_gene(self, gene: IGene) -> bool:
        """
        Register a gene with the substrate.

        Args:
            gene: The gene to register

        Returns:
            True if registration successful
        """
        ...

    def unregister_gene(self, name: str) -> bool:
        """Unregister a gene by name."""
        ...

    def activate_all(self) -> int:
        """
        Activate all registered genes in priority order.

        Returns:
            Number of genes successfully activated
        """
        ...

    def deactivate_all(self) -> None:
        """Deactivate all genes."""
        ...

    # =========================================================================
    # Flood Operations (Soft Flood / Gene Splicing)
    # =========================================================================

    def analyze_class(self, cls: Type[T]) -> Dict[str, Any]:
        """
        Analyze a class to determine what genes it needs.

        This is the "genetic analysis" - looking at the class's code
        to determine what capabilities (NAGAs) it should have.

        Args:
            cls: The class to analyze

        Returns:
            Analysis result with proposed genes
        """
        ...

    def create_flooded_class(
        self,
        original: Type[T],
        genes: List[str],
    ) -> Type[T]:
        """
        Create a new class with genes spliced in.

        This is SOFT FLOOD - mixin inheritance that preserves isinstance.

        Args:
            original: The original class
            genes: Names of genes to splice in

        Returns:
            New class with gene capabilities
        """
        ...

    def flood_instance(self, instance: T, genes: List[str]) -> T:
        """
        Flood an existing instance by swapping its class.

        Uses Python's runtime class swap: instance.__class__ = flooded_class

        Args:
            instance: The instance to flood
            genes: Names of genes to splice in

        Returns:
            The same instance with flooded class
        """
        ...

    # =========================================================================
    # Health & Status
    # =========================================================================

    def get_status(self) -> SubstrateStatus:
        """Get overall substrate status."""
        ...

    def get_gene_status(self, name: str) -> Optional[GeneStatus]:
        """Get status of a specific gene."""
        ...

    def heartbeat(self) -> datetime:
        """Record a heartbeat and return timestamp."""
        ...

    # =========================================================================
    # IGeneHost Implementation (inherited)
    # =========================================================================

    def get_gene(self, name: str) -> Optional[IGene]:
        """Get a gene by name."""
        ...

    def has_gene(self, name: str) -> bool:
        """Check if a gene is registered."""
        ...

    def get_capability(self, capability: str) -> Optional[Any]:
        """Get a capability from any gene that provides it."""
        ...

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to all listening genes."""
        ...


# =============================================================================
# FACTORY PROTOCOL (For External/Hybrid Mode - Future)
# =============================================================================


@runtime_checkable
class ISubstrateFactory(Protocol):
    """
    Factory for creating substrate instances.

    This enables Option C (Hybrid) in the future:
    - Local factory returns embedded AnantaService
    - Remote factory returns proxy to external service

    The consumer doesn't care which - Dependency Inversion.
    """

    def create(self) -> IAnantaBridge:
        """Create or connect to an Ananta Shesha instance."""
        ...

    def is_local(self) -> bool:
        """Check if this factory creates local or remote instances."""
        ...


# =============================================================================
# HELPER FUNCTIONS (Pure, No Side Effects)
# =============================================================================


def create_gene_manifest(
    name: str,
    capabilities: List[str],
    requires: Optional[List[str]] = None,
    priority: int = 50,
    optional: bool = False,
) -> GeneManifest:
    """
    Helper to create a GeneManifest with proper typing.

    Args:
        name: Unique gene identifier
        capabilities: What this gene provides
        requires: What this gene needs (default: empty)
        priority: Activation priority (default: 50)
        optional: Can system run without this? (default: False)

    Returns:
        Immutable GeneManifest
    """
    return GeneManifest(
        name=name,
        capabilities=tuple(capabilities),
        requires=tuple(requires or []),
        priority=priority,
        optional=optional,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "GeneActivationState",
    "SubstrateHealth",
    # Data Classes
    "GeneManifest",
    "GeneStatus",
    "SubstrateStatus",
    # Protocols (The Core)
    "IGene",
    "IGeneHost",
    "IAnantaBridge",
    "ISubstrateFactory",
    # Type Variables
    "T",
    "GeneT",
    # Helpers
    "create_gene_manifest",
]
