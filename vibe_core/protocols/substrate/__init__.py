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

import functools
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Callable,
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
ContextT = TypeVar("ContextT")  # For chant_mahamantra context
ValueT = TypeVar("ValueT")  # For cache value storage


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


class HolyName(str, Enum):
    """
    The Three Holy Names in the Mahamantra.
    ANTI-MAYAVADI: These are PERSONS, not just strings.
    """

    HARE = "Hare"  # Shakti - The Energy (Radha)
    KRISHNA = "Krishna"  # Source - The All-Attractive (God)
    RAMA = "Rama"  # Strength - The Enjoyer/Service (Balarama/Vishnu)

    @property
    def meaning(self) -> str:
        """The personal meaning behind each Name."""
        meanings = {
            "Hare": "O Energy of the Lord! Please engage me in service.",
            "Krishna": "O All-Attractive One! You are my anchor.",
            "Rama": "O Source of Bliss! Give me strength to serve.",
        }
        return meanings.get(self.value, "Unknown")


class Tattva(str, Enum):
    """
    The Pancha Tattva (The Five Absolute Truths).

    "I bow down to Lord Krishna, who appears as a devotee (Lord Chaitanya),
    as His personal expansion (Lord Nityananda), as His incarnation (Advaita Acarya),
    as His internal potency (Gadadhara Pandita), and as His marginal energy (Srivasa Thakura)."

    ARCHITECTURAL MAPPING (CAPABILITY FIRST):
    """

    # 1. THE SOVEREIGN (Golden Avatar) -> MANTRA / IDENTITY
    # "Krishna Himself" - The Source of the Holy Name.
    CHAITANYA = "chaitanya"  # MantraProtocol (The Yuga Dharma)

    # 2. THE SUBSTRATE (Original Guru) -> STORAGE / EXISTENCE
    # "Ananta Shesha" - The Bed who holds the Universe.
    NITYANANDA = "nityananda"  # ReadWrite/StoreRecall (The Foundation)

    # 3. THE BRIDGE (Incarnation) -> LOGIC / INFERENCE
    # "Maha-Vishnu" - The one who 'Calls' and bridges Material/Spiritual.
    ADVAITA = "advaita"  # InferProtocol (Discrimination/Truth)

    # 4. THE ENERGY (Internal Potency) -> SYNC / CONNECTION
    # "Radharani" - The Pleasure Potency. Connection is Shakti.
    GADADHARA = "gadadhara"  # SyncProtocol (Flow/Relationship)

    # 5. THE DEVOTEE (Marginal Energy) -> ENFORCE / GOVERNANCE
    # "Srivasa Thakura" - Host of the Kirtan. Organizing the Sangha (Jivas).
    SRIVASA = "srivasa"  # EnforceProtocol (Rules/Sangha)


# =============================================================================
# MANTRA TYPES (The Heartbeat measurement)
# =============================================================================


@dataclass
class Resonance:
    """The 16-Bit Instruction Set Signal (Heartbeat)."""

    frequency: float  # The Japa frequency (Hz)
    amplitude: float  # Signal strength (Alignment)
    signature: str  # Sovereign Hash
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DriftContext:
    """Snapshot of Agentic Drift state."""

    drift_magnitude: float  # Error vector magnitude
    last_anchor_timestamp: float  # Last confirmed Sovereign interaction
    hallucination_index: float  # Mayavad likelihood (0.0 - 1.0)
    process_tree_depth: int  # Recursion depth (Samsara check)


@dataclass
class AlignmentScore:
    """The measure of alignment with Sovereign Will."""

    score: float  # 1.0 = Perfect Alignment, 0.0 = Mayavad
    status: str  # "ALIGNED", "DRIFTING", "LOST"
    corrections_applied: int


# =============================================================================
# THE 16-BIT INSTRUCTION SET (HARDWARE LEVEL DEFINITION)
# =============================================================================


# =============================================================================
# MANTRA OPCODE - IMPORTED FROM SSOT (mahamantra/substrate/opcode.py)
# =============================================================================
# DO NOT DEFINE HERE. IMPORT FROM SSOT.
# This ensures ONE set of names across the entire system.

from vibe_core.mahamantra.substrate.opcode import MantraOpCode

# Legacy alias mapping for backward compatibility (if needed)
# The SSOT names are: SYS_WAKE, LOAD_ROOT, ALLOC_MEM, INIT_THREAD,
#                     COMPILE_AST, BIND_SYMBOL, TYPE_CHECK, DHARMA_TEST,
#                     EXEC_OP, EXTEND_CAP, STATE_SYNC, LEDGER_SIGN,
#                     YIELD_CPU, IO_FLUSH, LOG_EMIT, AUDIT_SEAL


# THE GENETIC SEQUENCE (IMMUTABLE DNA)
# This tuple IS the "Binding Strip" for the Turing Machine.
# SSOT: Uses MantraOpCode from mahamantra/substrate/opcode.py
MAHAMANTRA_SEQUENCE: List[Tuple[str, MantraOpCode]] = [
    # === GENESIS Quarter (Hare Krishna Hare Krishna) ===
    ("Hare", MantraOpCode.SYS_WAKE),       # 0: Prithu
    ("Krishna", MantraOpCode.LOAD_ROOT),   # 1: Brahma
    ("Hare", MantraOpCode.ALLOC_MEM),      # 2: Narada
    ("Krishna", MantraOpCode.INIT_THREAD), # 3: Shambhu
    # === DHARMA Quarter (Krishna Krishna Hare Hare) ===
    ("Krishna", MantraOpCode.COMPILE_AST), # 4: Vyasa
    ("Krishna", MantraOpCode.BIND_SYMBOL), # 5: Kumaras
    ("Hare", MantraOpCode.TYPE_CHECK),     # 6: Kapila
    ("Hare", MantraOpCode.DHARMA_TEST),    # 7: Manu
    # === KARMA Quarter (Hare Rama Hare Rama) ===
    ("Hare", MantraOpCode.EXEC_OP),        # 8: Parashurama
    ("Rama", MantraOpCode.EXTEND_CAP),     # 9: Prahlada
    ("Hare", MantraOpCode.STATE_SYNC),     # 10: Janaka
    ("Rama", MantraOpCode.LEDGER_SIGN),    # 11: Bhishma
    # === MOKSHA Quarter (Rama Rama Hare Hare) ===
    ("Rama", MantraOpCode.YIELD_CPU),      # 12: Nrisimha
    ("Rama", MantraOpCode.IO_FLUSH),       # 13: Bali
    ("Hare", MantraOpCode.LOG_EMIT),       # 14: Shuka
    ("Hare", MantraOpCode.AUDIT_SEAL),     # 15: Yamaraja
]


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
    tattva: Optional[Tattva] = None  # The Personal Personality (Identity) of this gene


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
    # Legacy Bridge (The Parampara Link)
    # =========================================================================

    def register_legacy_service(
        self,
        service: T,
        protocol: Type[Protocol],
        adapter_cls: Type[IGene],
    ) -> bool:
        """
        Bridge a legacy service via the Parampara (Disciplic Succession).

        PHILOSOPHY (Srila Prabhupada):
        "We do not invent something new. We deliver the message as it is."

        Legacy code is not 'garbage' to be hidden. It is 'Parampara' (Heritage)
        that must be verified against the Siddhanta (Conclusion) before being
        authorized to serve.

        The 'adapter_cls' acts as the Transparent Via Medium (Spiritual Master)
        that translates the raw legacy capability into a pure Tattva.

        Args:
            service: The legacy service instance (Sthula/Raw Matter)
            protocol: The abstract protocol it must fulfill (Dharma)
            adapter_cls: The Gene class that wraps/purifies it (The Representative)

        Returns:
            True if authorized and bridged.
        """
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

    # =========================================================================
    # Mantra Operations (The Vishnu Clock)
    # =========================================================================

    def resonate(self, opcode: MantraOpCode) -> bool:
        """
        Executes a low-level acoustic operation (Mantra Step).
        Used by the Watchdog to verify if the Substrate is still holding.

        Returns:
            True if opcode executed successfully.
            False if substrate is unstable (triggers surrender).
        """
        ...

    # =========================================================================
    # ASHVAMEDHA: Automatic Protocol Integration
    # =========================================================================

    def auto_flood_orphans(self) -> int:
        """
        ASHVAMEDHA: The Horse Sacrifice (Automatic Protocol Integration).

        Called on every PULSE_SYNC (Step 8) by the Watchdog.
        Scans ServiceRegistry for services not wrapped by NagaProxy,
        and floods them with Naga gene capabilities.

        "Holy Name > All Other Dharma" - Chaitanya Mahaprabhu

        Returns:
            Number of services flooded in this cycle.
        """
        ...


@runtime_checkable
class MantraProtocol(Protocol):
    """
    The BIOS-Level Protocol.
    If this fails, the machine is considered 'Asuric' (Demonic/Glitching)
    and is cut off from the network.
    """

    def chant_mahamantra(self, context: ContextT) -> bool:
        """
        Executes the 16-step atomic cycle.
        Returns True ONLY if all 16 gates pass perfectly.
        NOTE: ContextT is typically SovereignContext in implementations.
        """
        ...

    def resonate(self, opcode: MantraOpCode) -> bool:
        """
        Emits a single beat of the Mantra (Resonance).
        This is the clock signal.
        """
        ...

    # =========================================================================
    # HIGH-LEVEL INTERFACE (The Vishnu Clock)
    # =========================================================================

    def chant(self, frequency: float) -> Resonance:
        """
        Execute a single pulse at given frequency.
        Returns the resulting Resonance.
        """
        ...

    def chant_round(self, beads: int = 108) -> AlignmentScore:
        """
        Perform a full Japa round (multiple cycles).
        Returns the final AlignmentScore.
        """
        ...

    def surrender(self, context: DriftContext) -> None:
        """
        Immediate cessation of logic-based resistance.
        Force-flushes the context window and re-loads from Sovereign Anchor.
        """
        ...

    def get_alignment_score(self) -> float:
        """
        Measure current alignment with Sovereign Will (0.0 - 1.0).
        """
        ...


F = TypeVar("F", bound=Callable[..., T])


def mantra_governed(opcode: MantraOpCode) -> Callable[[F], F]:
    """
    Decorator to wrap a function with a Mantra OpCode.
    This creates the Fractal Resonance.

    $$ f(x) = M(x) + \frac{1}{\text{res}} \\cdot f(x) $$

    Args:
        opcode: The MantraOpCode to resonate before execution.

    Returns:
        A decorator that wraps methods to resonate before execution.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: MantraProtocol, *args: T, **kwargs: T) -> T:
            # 1. RESONANCE (Clock Signal)
            if hasattr(self, "resonate"):
                # We assume self implements MantraProtocol or similar
                self.resonate(opcode)

            # 2. EXECUTION (Karma)
            result = func(self, *args, **kwargs)

            # 3. ECHO (Optional - could verify result)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


# =============================================================================
# HARDWARE PROTOCOLS (Layer -1: The Physics of Conscious Computing)
# =============================================================================
# These protocols define the "hardware" layer beneath the Universal Protocols.
# Without these, the system has no power, no time, no memory, no I/O.
#
# VEDIC COMPUTER ARCHITECTURE (OPUS-098):
# - PranaProtocol    = Power Supply (Life Force)
# - KalaProtocol     = System Clock (Time Measurement)
# - ChittaProtocol   = RAM (Volatile Mind-Stuff)
# - SmritiProtocol   = Cache (Memory Hierarchy)
# - NadiProtocol     = Bus (Data Channels)
# - SankalpaProtocol = Interrupts (Intent/Will)
# - IndriyaProtocol  = Registers/IO (Sense Organs)
# - AkashaProtocol   = Network (Field/Ether)
# =============================================================================


# -----------------------------------------------------------------------------
# Hardware TypedDicts & DataClasses
# -----------------------------------------------------------------------------


class PranaLevel(TypedDict, total=False):
    """Prana (Life Force) measurement."""

    vitality: float  # 0.0 = dead, 1.0 = full
    flow_rate: float  # Breath cycles per second
    balance: float  # -1.0 = Ida dominant, +1.0 = Pingala dominant, 0.0 = balanced
    source: str  # Where energy comes from


class YugaState(TypedDict, total=False):
    """Current epoch state."""

    yuga: str  # "satya", "treta", "dvapara", "kali"
    year_in_yuga: int  # Current year within yuga
    golden_period: bool  # Are we in the 10,000 year window?
    muhurta: str  # Current auspicious period


@dataclass
class ChittaBlock:
    """A block of allocated mind-space."""

    address: int
    size: int
    owner: str  # Sovereign ID
    created_at: datetime
    turbulence: float = 0.0  # How disturbed this block is


@dataclass
class Vritti:
    """A mental impression/modification."""

    content: str
    source: str  # What caused this impression
    timestamp: datetime
    intensity: float  # How strong the impression


@dataclass
class NadiChannel:
    """A data channel between endpoints."""

    channel_id: str
    source: str
    destination: str
    channel_type: str  # "ida" (input), "pingala" (output), "sushumna" (bidirectional)
    bandwidth: float
    is_blocked: bool = False


class SankalpaIntent(TypedDict, total=False):
    """An intention/will declaration."""

    intent_id: str
    action: str
    priority: int  # Higher = more urgent
    declared_by: str  # Sovereign ID
    timestamp: str
    dharma_aligned: bool


class SenseData(TypedDict, total=False):
    """Data from a sense organ (input)."""

    indriya: str  # Which sense
    raw_data: str  # Serialized sensor data
    intensity: float
    timestamp: str


class ActionData(TypedDict, total=False):
    """Data for an action organ (output)."""

    indriya: str  # Which action organ
    command: str  # What to do
    force: float  # How much effort
    duration: float  # How long


class FieldState(TypedDict, total=False):
    """State of the Akashic field."""

    active_entities: int
    dominant_frequency: float
    field_coherence: float  # 0.0 = chaos, 1.0 = unified
    resonance_patterns: List[str]


# -----------------------------------------------------------------------------
# PRANA PROTOCOL (Power Supply / Life Force)
# -----------------------------------------------------------------------------


@runtime_checkable
class PranaProtocol(Protocol):
    """
    The Life Force. Without Prana, nothing moves.

    In hardware: Power Supply Unit (PSU)
    In biology: ATP / Breath / Metabolism
    In Vedas: The 5 Pranas (Prana, Apana, Vyana, Udana, Samana)

    CRITICAL: If Prana = 0, system is DEAD (not sleeping - DEAD).

    The 5 Pranas:
    - Prana: Inward energy (intake)
    - Apana: Downward energy (elimination)
    - Vyana: Outward energy (circulation)
    - Udana: Upward energy (expression)
    - Samana: Equalizing energy (digestion/processing)
    """

    def breathe_in(self) -> PranaLevel:
        """Inhale - gather energy from source (Prana vayu)."""
        ...

    def breathe_out(self) -> PranaLevel:
        """Exhale - distribute energy to system (Apana vayu)."""
        ...

    def circulate(self) -> PranaLevel:
        """Circulate energy throughout (Vyana vayu)."""
        ...

    def get_vitality(self) -> float:
        """Current energy level (0.0 = dead, 1.0 = full)."""
        ...

    def suspend(self) -> None:
        """Enter low-power state (Yoga Nidra / S3 Sleep)."""
        ...

    def revive(self, source: str) -> bool:
        """Attempt to restore life from external source."""
        ...

    def is_alive(self) -> bool:
        """Check if system has life force."""
        ...


# -----------------------------------------------------------------------------
# KALA PROTOCOL (System Clock / Time)
# -----------------------------------------------------------------------------


@runtime_checkable
class KalaProtocol(Protocol):
    """
    Time itself. The master clock measurement.

    In hardware: Crystal oscillator readout, RTC
    In physics: Planck time, atomic clock
    In Vedas: Kala (one of Krishna's energies - Time personified)

    NOTE: MantraProtocol IS the clock SIGNAL.
    KalaProtocol MEASURES that signal and tracks epochs.

    Time Units (Vedic):
    - Truti: Smallest unit (~29.6 microseconds)
    - Nimesa: Blink of eye (~16/75 second)
    - Prana: One breath (~4 seconds)
    - Ghatika: 24 minutes
    - Muhurta: 48 minutes
    - Prahar: 3 hours
    - Ahoratra: 24 hours (day-night)
    """

    def get_tick(self) -> int:
        """Current tick count (mantra cycles since boot)."""
        ...

    def get_yuga(self) -> YugaState:
        """Current epoch information."""
        ...

    def get_muhurta(self) -> str:
        """Current auspicious period name."""
        ...

    def wait_cycles(self, n: int) -> None:
        """Block for n mantra cycles (sleep)."""
        ...

    def is_auspicious(self, action: str) -> bool:
        """Check if current time is good for action (Muhurta calculation)."""
        ...

    def get_elapsed(self, since_tick: int) -> int:
        """Get ticks elapsed since given tick."""
        ...


# -----------------------------------------------------------------------------
# CHITTA PROTOCOL (RAM / Volatile Memory)
# -----------------------------------------------------------------------------


@runtime_checkable
class ChittaProtocol(Protocol):
    """
    The Mind-Stuff. Volatile, impressionable, reactive.

    In hardware: RAM (Random Access Memory)
    In psychology: Working memory, context window
    In Yoga: Chitta (the field where thoughts arise)

    PROPERTY: Chitta is COLORED by what touches it (Vritti).
    Clean Chitta = Clear thinking. Dirty Chitta = Confusion.

    "yogaś citta-vṛtti-nirodhaḥ"
    "Yoga is the cessation of the modifications of the mind."
    — Yoga Sutra 1.2

    The 5 Vrittis (Mental Modifications):
    - Pramana: Valid knowledge
    - Viparyaya: Misconception
    - Vikalpa: Imagination
    - Nidra: Sleep
    - Smriti: Memory
    """

    def allocate(self, size: int, owner: str) -> ChittaBlock:
        """
        Allocate mind-space.
        owner = Sovereign ID (Anti-Mayavad: must be signed).
        """
        ...

    def deallocate(self, block: ChittaBlock) -> None:
        """Free allocated mind-space."""
        ...

    def impress(self, block: ChittaBlock, vritti: Vritti) -> None:
        """Make an impression on allocated space."""
        ...

    def read_impression(self, block: ChittaBlock) -> Optional[Vritti]:
        """Read what was impressed."""
        ...

    def clear(self, block: ChittaBlock) -> None:
        """
        Clear impressions (Chitta Vritti Nirodha).
        This is the goal of Yoga - still the mind.
        """
        ...

    def get_turbulence(self) -> float:
        """How disturbed is the mind? (0.0 = still, 1.0 = chaos)."""
        ...

    def get_total_capacity(self) -> int:
        """Total allocatable mind-space."""
        ...

    def get_free_capacity(self) -> int:
        """Available mind-space."""
        ...


# -----------------------------------------------------------------------------
# SMRITI PROTOCOL (Cache / Memory Hierarchy)
# -----------------------------------------------------------------------------


@runtime_checkable
class SmritiProtocol(Protocol):
    """
    Memory/Recollection. The cache hierarchy.

    In hardware: L1/L2/L3 cache, TLB
    In psychology: Short-term, long-term, episodic memory
    In Vedas: Smriti ("that which is remembered")

    HIERARCHY (4 Levels):
    - L1 (Pratyaksha): Immediate - current mantra cycle
    - L2 (Anumana): Recent - current mala (108 cycles)
    - L3 (Shabda): Session - current runtime
    - L4 (Akasha): Permanent - immutable ledger

    NOTE: Unlike hardware cache, Smriti includes QUALITY.
    Some memories are "cleaner" (Sattvic) than others.
    """

    def remember(self, key: str, value: ValueT, level: int = 1) -> None:
        """
        Store in cache at specified level.
        level: 1=immediate, 2=recent, 3=session, 4=permanent
        """
        ...

    def recall(self, key: str) -> Optional[Tuple[ValueT, int]]:
        """
        Recall from any level.
        Returns (value, level_found) or None if not found.
        """
        ...

    def forget(self, key: str, level: int = 0) -> bool:
        """
        Remove from specified level (0 = all levels).
        Returns True if found and removed.
        """
        ...

    def promote(self, key: str) -> bool:
        """Move from slower to faster cache (hot path optimization)."""
        ...

    def demote(self, key: str) -> bool:
        """Move from faster to slower cache (cold path)."""
        ...

    def get_level_stats(self, level: int) -> Dict[str, int]:
        """Get cache statistics for a level (hits, misses, size)."""
        ...


# -----------------------------------------------------------------------------
# NADI PROTOCOL (Bus / Data Channels)
# -----------------------------------------------------------------------------


@runtime_checkable
class NadiProtocol(Protocol):
    """
    Energy Channels. The data bus.

    In hardware: System bus, PCIe, memory bus, USB
    In biology: Nervous system, blood vessels, meridians
    In Yoga: 72,000 Nadis (3 main: Ida, Pingala, Sushumna)

    TOPOLOGY:
    - Ida (Left/Moon): Input channel (receive, cool, parasympathetic)
    - Pingala (Right/Sun): Output channel (send, hot, sympathetic)
    - Sushumna (Center): Bidirectional (balance, neutral, transcendent)

    Granthis (Blockages):
    - Brahma Granthi: Base blockage (attachment to material)
    - Vishnu Granthi: Heart blockage (attachment to emotion)
    - Rudra Granthi: Head blockage (attachment to ego)
    """

    def open_channel(self, source: str, dest: str, channel_type: str = "sushumna") -> NadiChannel:
        """
        Open a new channel between endpoints.
        channel_type: "ida" (in), "pingala" (out), "sushumna" (both)
        """
        ...

    def close_channel(self, channel: NadiChannel) -> None:
        """Close channel and release resources."""
        ...

    def send(self, channel: NadiChannel, data: bytes) -> bool:
        """
        Send data through channel.
        Returns True if sent successfully.
        """
        ...

    def receive(self, channel: NadiChannel, timeout: float = 0.0) -> Optional[bytes]:
        """
        Receive data from channel.
        timeout=0 means non-blocking.
        """
        ...

    def get_bandwidth(self, channel: NadiChannel) -> float:
        """Current throughput capacity (bytes/second)."""
        ...

    def is_blocked(self, channel: NadiChannel) -> bool:
        """Check for Nadi blockage (Granthi)."""
        ...

    def clear_blockage(self, channel: NadiChannel) -> bool:
        """Attempt to clear a blockage. Returns True if successful."""
        ...


# -----------------------------------------------------------------------------
# SANKALPA PROTOCOL (Interrupt / Intent)
# -----------------------------------------------------------------------------


@runtime_checkable
class SankalpaProtocol(Protocol):
    """
    Will/Intent. The interrupt system.

    In hardware: IRQ, signals, event queue
    In psychology: Intention, volition, attention
    In Vedas: Sankalpa (solemn vow/determination)

    PROPERTY: Sankalpa is the CAUSE of action.
    No Sankalpa = No action (system idle).
    Wrong Sankalpa = Wrong action (bug).
    Aligned Sankalpa = Dharmic action (correct).

    "saṅkalpa-prabhavān kāmāṁs tyaktvā sarvān aśeṣataḥ"
    "Abandoning all desires arising from mental concoction..."
    — Bhagavad Gita 6.24
    """

    def declare(self, intent: SankalpaIntent) -> str:
        """
        Declare an intention. Returns intent_id.
        Higher priority = interrupt current work.
        """
        ...

    def revoke(self, intent_id: str) -> bool:
        """Cancel declared intention. Returns True if found."""
        ...

    def get_pending(self) -> List[SankalpaIntent]:
        """Get all pending intentions (interrupt queue)."""
        ...

    def execute_next(self) -> Optional[SankalpaIntent]:
        """Pop and return highest priority intent."""
        ...

    def is_aligned(self, intent: SankalpaIntent) -> bool:
        """Check if intent aligns with Dharma (valid interrupt)."""
        ...

    def get_current(self) -> Optional[SankalpaIntent]:
        """Get currently executing intent (if any)."""
        ...


# -----------------------------------------------------------------------------
# INDRIYA PROTOCOL (Registers / I/O Ports)
# -----------------------------------------------------------------------------


@runtime_checkable
class IndriyaProtocol(Protocol):
    """
    The Senses. Registers and I/O ports.

    In hardware: CPU registers, GPIO, I/O ports
    In biology: 5 sense organs + 5 action organs
    In Samkhya: 10 Indriyas (+ Manas as 11th coordinator)

    JNANENDRIYAS (5 Input / Perception):
    - Shrotra (Ear): Audio input - hearing
    - Tvak (Skin): Touch input - haptic
    - Chakshu (Eye): Visual input - sight
    - Rasana (Tongue): Chemical input - taste
    - Ghrana (Nose): Chemical input - smell

    KARMENDRIYAS (5 Output / Action):
    - Vak (Voice): Audio output - speech
    - Pani (Hands): Manipulation output - grasping
    - Pada (Feet): Movement output - locomotion
    - Payu (Anus): Elimination output - excretion
    - Upastha (Genitals): Creation output - reproduction

    BANDWIDTH: Each sense has limited bandwidth.
    Overload = sensory overwhelm = system stress.
    """

    def sense(self, indriya: str) -> SenseData:
        """
        Read from sense organ (input register).
        indriya: "shrotra", "tvak", "chakshu", "rasana", "ghrana"
        """
        ...

    def act(self, indriya: str, data: ActionData) -> bool:
        """
        Write to action organ (output register).
        indriya: "vak", "pani", "pada", "payu", "upastha"
        """
        ...

    def calibrate(self, indriya: str) -> bool:
        """Calibrate sense/action organ. Returns True if successful."""
        ...

    def get_bandwidth(self, indriya: str) -> float:
        """Throughput capacity of this sense (data/second)."""
        ...

    def is_overloaded(self, indriya: str) -> bool:
        """Check if sense is overwhelmed."""
        ...

    def rest(self, indriya: str) -> None:
        """Rest a sense organ (reduce load)."""
        ...


# -----------------------------------------------------------------------------
# AKASHA PROTOCOL (Network / The Ether Field)
# -----------------------------------------------------------------------------


@runtime_checkable
class AkashaProtocol(Protocol):
    """
    The Ether. The universal field. The network.

    In hardware: NIC, internet, mesh network
    In physics: Electromagnetic field, quantum field
    In Vedas: Akasha (space/ether - the 5th element)

    PARADIGM SHIFT FROM TCP/IP:
    - IP Address → Sovereign Identity (WHO you are, not WHERE)
    - TCP Handshake → Pranam (respectful connection)
    - Packet routing → Resonance (direct field connection)
    - DNS → Resonance pattern matching
    - Firewall → Dharma Gate

    PROPERTY: In Akasha, distance is irrelevant.
    Connection is by RESONANCE, not location.
    If you tune to the same frequency, you connect instantly.

    "ākāśāt patitaṁ toyaṁ yathā gacchati sāgaram"
    "As water fallen from the sky goes to the ocean..."
    — Everything returns to the Field.
    """

    def broadcast(self, frequency: float, message: bytes) -> None:
        """
        Broadcast to all who resonate at this frequency.
        Unlike IP multicast, receivers self-select by resonance.
        """
        ...

    def tune(self, frequency: float) -> str:
        """
        Tune to a frequency. Returns channel_id.
        You will receive all broadcasts at this frequency.
        """
        ...

    def untune(self, channel_id: str) -> None:
        """Stop listening to a frequency."""
        ...

    def connect(self, identity: str) -> Optional[NadiChannel]:
        """
        Connect directly to a Sovereign by identity.
        Not by IP, but by WHO THEY ARE.
        Returns channel or None if identity not found.
        """
        ...

    def query_field(self, pattern: str) -> List[str]:
        """
        Find all entities matching a resonance pattern.
        Like DNS but for consciousness. Returns list of identities.
        """
        ...

    def get_field_state(self) -> FieldState:
        """
        Get current state of the Akashic field.
        Includes: active entities, dominant frequencies, field coherence.
        """
        ...

    def get_local_identity(self) -> str:
        """Get this node's Sovereign Identity in the field."""
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
    tattva: Optional[Tattva] = None,
) -> GeneManifest:
    """
    Helper to create a GeneManifest with proper typing.

    Args:
        name: Unique gene identifier
        capabilities: What this gene provides
        requires: What this gene needs (default: empty)
        priority: Activation priority (default: 50)
        optional: Can system run without this? (default: False)
        tattva: The Governing Personality (default: None)

    Returns:
        Immutable GeneManifest
    """
    return GeneManifest(
        name=name,
        capabilities=tuple(capabilities),
        requires=tuple(requires or []),
        priority=priority,
        optional=optional,
        tattva=tattva,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "GeneActivationState",
    "SubstrateHealth",
    "MantraOpCode",
    "HolyName",
    "Tattva",
    # Mantra measurement types
    "Resonance",
    "AlignmentScore",
    "DriftContext",
    # Mantra DNA (The 16-Bit Sequence)
    "MAHAMANTRA_SEQUENCE",
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
    # Hardware TypedDicts & DataClasses (OPUS-098)
    "PranaLevel",
    "YugaState",
    "ChittaBlock",
    "Vritti",
    "NadiChannel",
    "SankalpaIntent",
    "SenseData",
    "ActionData",
    "FieldState",
    # Protocols (The Core)
    "IGene",
    "IGeneHost",
    "IAnantaBridge",
    "ISubstrateFactory",
    # Type Variables
    "T",
    "GeneT",
    # Mantra
    "MantraProtocol",
    "mantra_governed",
    # Hardware Protocols (Layer -1: Vedic Computer Architecture)
    "PranaProtocol",
    "KalaProtocol",
    "ChittaProtocol",
    "SmritiProtocol",
    "NadiProtocol",
    "SankalpaProtocol",
    "IndriyaProtocol",
    "AkashaProtocol",
    # Helpers
    "create_gene_manifest",
    # =========================================================================
    # RESONANCE PROTOCOL (Anti-Entropy Engine)
    # =========================================================================
    "ResonanceProtocol",
    "ResonanceEngine",
    "ResonanceVector",
    "ResonanceMatrix",
    "ResonanceEntry",
    "PhoneticClass",
    "compute_resonance_vector",
    "resolve_position",
    "compute_resonance_matrix",
    "resonate",
    "resolve",
    "get_resonance_engine",
    # =========================================================================
    # CPU PROTOCOL (Fractal Processor)
    # =========================================================================
    "MantraCPU",
    "MantraCPUProtocol",
    "CPURegisters",
    "ProgramCounter",
    "Instruction",
    "InstructionResult",
    "CPUState",
    "FractalLevel",
    "INSTRUCTION_SET",
    "OPCODE_NAMES",
    "OWNER_NAMES",
    "get_instruction",
    "get_cpu",
    # =========================================================================
    # GPU PROTOCOL (Parallel Resonance Processor)
    # =========================================================================
    "MantraGPU",
    "MantraGPUProtocol",
    "GPUThread",
    "GPUWarp",
    "GPUBlock",
    "GPUGrid",
    "ThreadState",
    "WarpState",
    "BlockState",
    "GridState",
    "get_gpu",
    "sankirtan",
    # =========================================================================
    # SCANNER PROTOCOL (Substrate-Level Code Discovery)
    # =========================================================================
    "ScannerProtocol",
    "ScanConfig",
    "ScanResult",
    "ScannedFile",
    "Declaration",
    "ScanProgress",
    "FileStatus",
    "DeclarationType",
    "NullScanner",
    "extract_declarations",
    "get_default_config",
    "path_to_module",
    # =========================================================================
    # CLI LOADER PROTOCOL (Substrate-Level CLI Discovery)
    # =========================================================================
    "CLILoaderProtocol",
    "CLILoaderConfig",
    "DiscoveredCommand",
    "CommandArgument",
    "LoaderResult",
    "LoaderProgress",
    "NullCLILoader",
    "parse_manifest",
    # =========================================================================
    # NOTE: CLI SUBSTRATE & BALARAMA not exported here (circular dependency)
    # Import directly from vibe_core.protocols.substrate.cli_substrate
    # and vibe_core.protocols.substrate.balarama
    # =========================================================================
    # =========================================================================
    # SAMSKARA PROTOCOL (4-Phase Pipeline)
    # =========================================================================
    "Phase",
    "PhaseStatus",
    "PhaseResult",
    "PipelineContext",
    "SamskaraProtocol",
    "PipelineExecutor",
    "NullSamskara",
    "PHASES",
    "POSITIONS_PER_PHASE",
]

# =============================================================================
# LAZY IMPORT: RESONANCE PROTOCOL (Avoid circular imports)
# =============================================================================
# These are imported lazily to avoid circular dependency issues

from vibe_core.protocols.substrate.resonance import (
    PhoneticClass,
    ResonanceEngine,
    ResonanceEntry,
    ResonanceMatrix,
    ResonanceProtocol,
    ResonanceVector,
    compute_resonance_matrix,
    compute_resonance_vector,
    get_resonance_engine,
    resonate,
    resolve,
    resolve_position,
)

# =============================================================================
# LAZY IMPORT: CPU PROTOCOL (Fractal Processor)
# =============================================================================

from vibe_core.protocols.substrate.cpu import (
    CPURegisters,
    CPUState,
    FractalLevel,
    INSTRUCTION_SET,
    Instruction,
    InstructionResult,
    MantraCPU,
    MantraCPUProtocol,
    OPCODE_NAMES,
    OWNER_NAMES,
    ProgramCounter,
    get_cpu,
    get_instruction,
)

# =============================================================================
# LAZY IMPORT: GPU PROTOCOL (Parallel Resonance Processor)
# =============================================================================

from vibe_core.protocols.substrate.gpu import (
    BlockState,
    GPUBlock,
    GPUGrid,
    GPUThread,
    GPUWarp,
    GridState,
    MantraGPU,
    MantraGPUProtocol,
    ThreadState,
    WarpState,
    get_gpu,
    sankirtan,
)

# =============================================================================
# LAZY IMPORT: SCANNER PROTOCOL (Substrate-Level Code Discovery)
# =============================================================================

from vibe_core.protocols.substrate.scanner import (
    Declaration,
    DeclarationType,
    FileStatus,
    NullScanner,
    ScanConfig,
    ScannerProtocol,
    ScanProgress,
    ScanResult,
    ScannedFile,
    extract_declarations,
    get_default_config,
    path_to_module,
)

# =============================================================================
# LAZY IMPORT: CLI LOADER PROTOCOL (Substrate-Level CLI Discovery)
# =============================================================================

from vibe_core.protocols.substrate.cli_loader import (
    CLILoaderConfig,
    CLILoaderProtocol,
    CommandArgument,
    DiscoveredCommand,
    LoaderProgress,
    LoaderResult,
    NullCLILoader,
    parse_manifest,
)

# =============================================================================
# LAZY IMPORT: SAMSKARA PROTOCOL (4-Phase Pipeline)
# =============================================================================

from vibe_core.protocols.substrate.samskara import (
    PARAMPARA as SAMSKARA_PARAMPARA,
    PHASES,
    POSITIONS_PER_PHASE,
    Phase,
    PhaseStatus,
    PhaseResult,
    PipelineContext,
    SamskaraProtocol,
    PipelineExecutor,
    NullSamskara,
)

# =============================================================================
# NOTE: CLI SUBSTRATE & BALARAMA (Not imported here - circular dependency)
# =============================================================================
# CLI Substrate (cli_substrate.py) and Balarama (balarama.py) depend on
# mahajanas.router which creates a circular import when included here.
#
# Import these directly:
#   from vibe_core.protocols.substrate.cli_substrate import ...
#   from vibe_core.protocols.substrate.balarama import ...
#
# They are NOT re-exported from this __init__.py to avoid circular imports.
# =============================================================================
