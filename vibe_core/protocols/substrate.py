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
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    runtime_checkable,
)

# =============================================================================
# TYPE VARIABLES (Generic Support)
# =============================================================================

T = TypeVar("T")
GeneT = TypeVar("GeneT", bound="IGene")


# =============================================================================
# TYPED DICTS (VIMANA RANGE ROVER - No Dict[str, Any])
# =============================================================================


class GeneMetrics(TypedDict, total=False):
    """
    Metrics for a gene's runtime performance.

    WATERTIGHT: No Any - all fields typed.
    """

    activation_count: int  # Times activated
    deactivation_count: int  # Times deactivated
    error_count: int  # Errors encountered
    last_error: str  # Most recent error message
    uptime_seconds: float  # Time since last activation
    invocation_count: int  # Times gene methods called
    avg_latency_ms: float  # Average method latency


class GeneAnalysisResult(TypedDict, total=False):
    """
    Result of analyzing a class for gene requirements.

    WATERTIGHT: No Any - all fields typed.
    """

    class_name: str  # Name of analyzed class
    module: str  # Module path
    proposed_genes: List[str]  # Genes to splice in
    detected_patterns: List[str]  # Patterns found in code
    confidence: float  # 0.0-1.0 confidence score
    reason: str  # Human-readable explanation
    warnings: List[str]  # Any warnings during analysis


class SubstrateEventData(TypedDict, total=False):
    """
    Event data emitted to genes via SHANKHA broadcast.

    WATERTIGHT: No Any - all fields typed.
    """

    source: str  # Event source identifier
    timestamp: str  # ISO format timestamp
    payload: str  # Serialized payload (JSON string)
    correlation_id: str  # For tracing event chains
    priority: int  # Event priority (higher = more urgent)


# =============================================================================
# BINDING CERTIFICATES (Anti-Mayavadi - Personal Identity at Every Binding)
# =============================================================================


class BindingCertificate(TypedDict, total=False):
    """
    Certificate proving WHO bound WHAT to WHOM.

    ANTI-MAYAVADI: Every binding must be PERSONAL, not impersonal.
    This certificate creates a chain of custody for gene bindings.

    Without this, Any entity can bind - UNVERIFIED = MAYA.
    With this, only verified entities can bind - PERSONAL = TRUTH.
    """

    binder_id: str  # WHO performed the binding (identity)
    target_id: str  # WHAT was bound (gene/host name)
    host_id: str  # TO WHOM it was bound (host identity)
    timestamp: str  # WHEN (ISO format)
    signature: str  # CRYPTOGRAPHIC PROOF (hex-encoded)
    lineage: List[str]  # Chain of custody (previous binder_ids)


class RegistrationCertificate(TypedDict, total=False):
    """
    Certificate proving gene registration legitimacy.

    ANTI-MAYAVADI: No anonymous gene registration.
    Every gene must prove its HERITAGE (Erbgut).
    """

    gene_name: str  # Gene being registered
    registrar_id: str  # WHO registered it
    manifest_hash: str  # Hash of GeneManifest (integrity)
    timestamp: str  # WHEN
    signature: str  # Registrar's signature
    authorized_by: str  # Higher authority (if delegated)


class FloodAuthorization(TypedDict, total=False):
    """
    Authorization for flood operations (EXTREMELY POWERFUL).

    ANTI-MAYAVADI: Flood operations can MUTATE reality.
    Only verified entities with proper authorization can flood.
    This is the 37th key - sovereign-level operation.
    """

    target_class: str  # Class being flooded
    target_instance_id: str  # Instance ID (if instance flood)
    genes_to_splice: List[str]  # Genes being injected
    authorizer_id: str  # WHO authorized this flood
    authorization_level: str  # "sovereign" | "delegated" | "emergency"
    timestamp: str  # WHEN
    signature: str  # Authorizer's signature
    expires_at: str  # Authorization expiry (ISO format)


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
    WATERTIGHT: metrics uses GeneMetrics TypedDict, not Dict[str, Any].
    """

    manifest: GeneManifest
    state: GeneActivationState
    bound_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    error: Optional[str] = None
    metrics: Optional[GeneMetrics] = None

    def __post_init__(self) -> None:
        if self.metrics is None:
            self.metrics = GeneMetrics()


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

    def bind(
        self,
        host: "IGeneHost",
        certificate: Optional[BindingCertificate] = None,
    ) -> None:
        """
        Bind this gene to a host.

        This is DEPENDENCY INJECTION from above.
        The host calls this method, passing itself.
        The gene stores the reference but doesn't import the host's class.

        ANTI-MAYAVADI: Certificate proves WHO is binding.
        Without certificate, binding is UNVERIFIED (legacy mode).
        With certificate, binding has chain of custody.

        Args:
            host: The IGeneHost that will power this gene
            certificate: Optional binding certificate for verified binding
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

    def get_capability(self, capability: str) -> Optional[object]:
        """
        Get a capability from any gene that provides it.

        Args:
            capability: Name of the capability (e.g., "ledger", "validation")

        Returns:
            The capability provider (typed as object - caller must cast), or None

        WATERTIGHT: Returns object not Any - caller must know expected type.
        """
        ...

    def emit_event(
        self,
        event_type: str,
        data: SubstrateEventData,
        caller_id: str = "anonymous",
    ) -> None:
        """
        Emit an event to all listening genes.

        This is the SHANKHA (broadcast) capability at the substrate level.
        WATERTIGHT: data is SubstrateEventData TypedDict, not Dict[str, Any].

        ANTI-MAYAVADI: caller_id identifies WHO is emitting.
        "anonymous" is legacy mode - unverified emitter.
        Named caller_id enables event tracing and accountability.

        Args:
            event_type: Type of event being emitted
            data: Event payload (typed)
            caller_id: Identity of emitter (default: "anonymous" for legacy)
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

    def register_gene(
        self,
        gene: IGene,
        certificate: Optional[RegistrationCertificate] = None,
    ) -> bool:
        """
        Register a gene with the substrate.

        ANTI-MAYAVADI: Certificate proves WHO is registering and WHY.
        Without certificate, registration is UNVERIFIED (legacy mode).
        With certificate, gene has proven HERITAGE (Erbgut).

        Args:
            gene: The gene to register
            certificate: Optional registration certificate for verified registration

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

    def analyze_class(self, cls: Type[T]) -> GeneAnalysisResult:
        """
        Analyze a class to determine what genes it needs.

        This is the "genetic analysis" - looking at the class's code
        to determine what capabilities (NAGAs) it should have.

        Args:
            cls: The class to analyze

        Returns:
            GeneAnalysisResult with proposed genes

        WATERTIGHT: Returns GeneAnalysisResult TypedDict, not Dict[str, Any].
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

    def flood_instance(
        self,
        instance: T,
        genes: List[str],
        authorization: Optional[FloodAuthorization] = None,
    ) -> T:
        """
        Flood an existing instance by swapping its class.

        Uses Python's runtime class swap: instance.__class__ = flooded_class

        ANTI-MAYAVADI: Flood is EXTREMELY POWERFUL - can mutate reality!
        This is 37th key territory - sovereign-level operation.
        Without authorization, flood is UNVERIFIED (legacy mode).
        With authorization, flood has cryptographic proof of legitimacy.

        Args:
            instance: The instance to flood
            genes: Names of genes to splice in
            authorization: Optional flood authorization for verified mutation

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
    # WATERTIGHT: Same signatures as IGeneHost - no Any types.
    # =========================================================================

    def get_gene(self, name: str) -> Optional[IGene]:
        """Get a gene by name."""
        ...

    def has_gene(self, name: str) -> bool:
        """Check if a gene is registered."""
        ...

    def get_capability(self, capability: str) -> Optional[object]:
        """Get a capability from any gene that provides it."""
        ...

    def emit_event(
        self,
        event_type: str,
        data: SubstrateEventData,
        caller_id: str = "anonymous",
    ) -> None:
        """Emit an event to all listening genes (caller_id for tracing)."""
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
    # TypedDicts (WATERTIGHT - No Any)
    "GeneMetrics",
    "GeneAnalysisResult",
    "SubstrateEventData",
    # Binding Certificates (ANTI-MAYAVADI - Personal Identity)
    "BindingCertificate",
    "RegistrationCertificate",
    "FloodAuthorization",
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
