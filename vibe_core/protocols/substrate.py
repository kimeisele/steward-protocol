"""
SUBSTRATE PROTOCOLS - Layer -1 (Below NAGA LOKA)

"Om Purnamadah Purnamidam" - From the Whole comes the Whole.

This module defines the PURE INTERFACES for Ananta Shesha.
It imports the PRICAL FOUNDATION (Layer -2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
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

# IMPORT FROM PRIMAL (Layer -2)
from vibe_core.protocols.primal import (
    watertight,
    MantraOpCode,
    HolyName,
    Tattva,
    Resonance,
    AlignmentScore,
    DriftContext,
    MAHAMANTRA_SEQUENCE
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
    """Metrics for a gene's runtime performance."""
    activation_count: int
    deactivation_count: int
    error_count: int
    last_error: str
    uptime_seconds: float
    invocation_count: int
    avg_latency_ms: float


class GeneAnalysisResult(TypedDict, total=False):
    """Result of analyzing a class for gene requirements."""
    class_name: str
    module: str
    proposed_genes: List[str]
    detected_patterns: List[str]
    confidence: float
    reason: str
    warnings: List[str]


class SubstrateEventData(TypedDict, total=False):
    """Event data emitted to genes via SHANKHA broadcast."""
    source: str
    timestamp: str
    payload: str
    correlation_id: str
    priority: int


# =============================================================================
# BINDING CERTIFICATES (Anti-Mayavadi - Personal Identity at Every Binding)
# =============================================================================


class BindingCertificate(TypedDict, total=False):
    """Certificate proving WHO bound WHAT to WHOM."""
    binder_id: str
    target_id: str
    host_id: str
    timestamp: str
    signature: str
    lineage: List[str]


class RegistrationCertificate(TypedDict, total=False):
    """Certificate proving gene registration legitimacy."""
    gene_name: str
    registrar_id: str
    manifest_hash: str
    timestamp: str
    signature: str
    authorized_by: str


class FloodAuthorization(TypedDict, total=False):
    """Authorization for flood operations (EXTREMELY POWERFUL)."""
    target_class: str
    target_instance_id: str
    genes_to_splice: List[str]
    authorizer_id: str
    authorization_level: str
    timestamp: str
    signature: str
    expires_at: str


# =============================================================================
# ENUMS (Pure Value Types)
# =============================================================================


class GeneActivationState(str, Enum):
    """State of a gene in the substrate."""
    DORMANT = "dormant"
    BOUND = "bound"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    MUTATED = "mutated"


class SubstrateHealth(str, Enum):
    """Health status of the substrate."""
    PRISTINE = "pristine"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    COLLAPSED = "collapsed"


# =============================================================================
# DATA CLASSES (Pure Data, No Behavior)
# =============================================================================


@dataclass(frozen=True)
class GeneManifest:
    """Manifest describing a gene's capabilities."""
    name: str
    capabilities: Tuple[str, ...]
    requires: Tuple[str, ...]
    priority: int = 50
    optional: bool = False
    tattva: Optional[Tattva] = None


@dataclass
class GeneStatus:
    """Runtime status of a gene."""
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


@watertight
@runtime_checkable
class IGene(Protocol):
    """Protocol for a gene (Mixin) that can be bound to a host."""

    @property
    def manifest(self) -> GeneManifest: ...

    @property
    def state(self) -> GeneActivationState: ...

    def bind(self, host: "IGeneHost", certificate: Optional[BindingCertificate] = None) -> None: ...

    def activate(self) -> bool: ...

    def deactivate(self) -> None: ...

    def unbind(self) -> None: ...


@watertight
@runtime_checkable
class IGeneHost(Protocol):
    """Protocol for a host that can hold genes."""

    def get_gene(self, name: str) -> Optional[IGene]: ...

    def has_gene(self, name: str) -> bool: ...

    def get_capability(self, capability: str) -> Optional[object]: ...

    def emit_event(self, event_type: str, data: SubstrateEventData, caller_id: str = "anonymous") -> None: ...

    def shutdown(self) -> None: ...


@watertight
@runtime_checkable
class IAnantaBridge(Protocol):
    """The full Ananta Shesha interface."""

    def register_gene(self, gene: IGene, certificate: Optional[RegistrationCertificate] = None) -> bool: ...

    def unregister_gene(self, name: str) -> bool: ...

    def activate_all(self) -> int: ...

    def deactivate_all(self) -> None: ...

    def register_legacy_service(self, service: object, protocol: Type[Protocol], adapter_cls: Type[IGene]) -> bool: ...

    def analyze_class(self, cls: Type[T]) -> GeneAnalysisResult: ...

    def create_flooded_class(self, original: Type[T], genes: List[str]) -> Type[T]: ...

    def flood_instance(self, instance: T, genes: List[str], authorization: Optional[FloodAuthorization] = None) -> T: ...

    def get_status(self) -> SubstrateStatus: ...

    def get_gene_status(self, name: str) -> Optional[GeneStatus]: ...

    def heartbeat(self) -> datetime: ...

    def get_gene(self, name: str) -> Optional[IGene]: ...

    def has_gene(self, name: str) -> bool: ...

    def get_capability(self, capability: str) -> Optional[object]: ...

    def emit_event(self, event_type: str, data: SubstrateEventData, caller_id: str = "anonymous") -> None: ...

    def resonate(self, opcode: MantraOpCode) -> bool: ...

    def auto_flood_orphans(self) -> int: ...

    def shutdown(self) -> None: ...


@watertight
@runtime_checkable
class ILivingSystem(Protocol):
    """Interface for a system that has passed the 1729-Test."""
    
    def verify_life(self, intent_signature: str, context: object) -> bool: ...
        
    def get_opulence_score(self) -> Dict[str, bool]: ...

    def dispose(self) -> None: ...


@watertight
@runtime_checkable
class MantraProtocol(Protocol):
    """The BIOS-Level Protocol."""

    def chant_mahamantra(self, context: object) -> bool: ...

    def resonate(self, opcode: MantraOpCode) -> bool: ...

    def chant(self, frequency: float) -> Resonance: ...

    def chant_round(self, beads: int = 108) -> AlignmentScore: ...

    def surrender(self, context: DriftContext) -> None: ...

    def get_alignment_score(self) -> float: ...

    def close(self) -> None: ...


def mantra_governed(opcode: MantraOpCode):
    """Decorator to wrap a function with a Mantra OpCode."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, "resonate"):
                self.resonate(opcode)
            result = func(self, *args, **kwargs)
            return result
        return wrapper
    return decorator


@runtime_checkable
class ISubstrateFactory(Protocol):
    """Factory for creating substrate instances."""

    def create(self) -> IAnantaBridge: ...

    def is_local(self) -> bool: ...


def create_gene_manifest(
    name: str,
    capabilities: List[str],
    requires: Optional[List[str]] = None,
    priority: int = 50,
    optional: bool = False,
    tattva: Optional[Tattva] = None,
) -> GeneManifest:
    """Helper to create a GeneManifest with proper typing."""
    return GeneManifest(
        name=name,
        capabilities=tuple(capabilities),
        requires=tuple(requires or []),
        priority=priority,
        optional=optional,
        tattva=tattva,
    )


__all__ = [
    "GeneActivationState",
    "SubstrateHealth",
    "MantraOpCode",
    "HolyName",
    "Tattva",
    "Resonance",
    "AlignmentScore",
    "DriftContext",
    "MAHAMANTRA_SEQUENCE",
    "GeneMetrics",
    "GeneAnalysisResult",
    "SubstrateEventData",
    "BindingCertificate",
    "RegistrationCertificate",
    "FloodAuthorization",
    "GeneManifest",
    "GeneStatus",
    "SubstrateStatus",
    "IGene",
    "IGeneHost",
    "IAnantaBridge",
    "ILivingSystem",
    "ISubstrateFactory",
    "T",
    "GeneT",
    "MantraProtocol",
    "mantra_governed",
    "create_gene_manifest",
]