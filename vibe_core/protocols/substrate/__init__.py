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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x253336b8"  # GenesisByte: parampara % 37 == 0

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

# SSOT: HolyName from byte.py (IntEnum with VOID for binary encoding)
from vibe_core.mahamantra.substrate.byte import HolyName

# =============================================================================
# TYPE VARIABLES (Generic Support)
# =============================================================================

T = TypeVar("T")
GeneT = TypeVar("GeneT", bound="IGene")
ContextT = TypeVar("ContextT")  # For chant_mahamantra context
ValueT = TypeVar("ValueT")  # For cache value storage


# =============================================================================
# TYPES (Re-exported from types.py — was inline, now split)
# =============================================================================
from vibe_core.protocols.substrate.types import (
    ActionData,
    AlignmentScore,
    BindingCertificate,
    ChittaBlock,
    DriftContext,
    FieldState,
    FloodAuthorization,
    GeneActivationState,
    GeneAnalysisResult,
    GeneManifest,
    GeneMetrics,
    GeneStatus,
    NadiChannel,
    PranaLevel,
    Resonance,
    RegistrationCertificate,
    SankalpaIntent,
    SenseData,
    SubstrateEventData,
    SubstrateHealth,
    SubstrateStatus,
    Tattva,
    Vritti,
    YugaState,
    get_holy_name_meaning,
)

# =============================================================================
# MANTRA OPCODE - IMPORTED FROM SSOT (mahamantra/substrate/opcode.py)
# =============================================================================
from vibe_core.mahamantra.substrate.opcode import MAHAMANTRA_SEQUENCE, MantraOpCode


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


# =============================================================================
# MANTRA PROTOCOL + DECORATOR (Re-exported from mantra.py)
# =============================================================================
from vibe_core.protocols.substrate.mantra_protocol import (
    MantraProtocol,
    mantra_governed,
    register_governance_hook,
)


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


# =============================================================================
# HARDWARE PROTOCOLS (Re-exported from hardware.py)
# =============================================================================
from vibe_core.protocols.substrate.hardware import (
    AkashaProtocol,
    ChittaProtocol,
    IndriyaProtocol,
    KalaProtocol,
    NadiProtocol,
    PranaProtocol,
    SankalpaProtocol,
    SmritiProtocol,
)


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
    "get_holy_name_meaning",
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
    "register_governance_hook",
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
# LAZY IMPORT: CPU PROTOCOL (Fractal Processor)
# =============================================================================
from vibe_core.protocols.substrate.cpu import (
    INSTRUCTION_SET,
    OPCODE_NAMES,
    OWNER_NAMES,
    CPURegisters,
    CPUState,
    FractalLevel,
    Instruction,
    InstructionResult,
    MantraCPU,
    MantraCPUProtocol,
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
    resolve,
    resolve_position,
    resonate,
)

# =============================================================================
# LAZY IMPORT: SAMSKARA PROTOCOL (4-Phase Pipeline)
# =============================================================================
from vibe_core.protocols.substrate.samskara import (
    PARAMPARA as SAMSKARA_PARAMPARA,
)
from vibe_core.protocols.substrate.samskara import (
    PHASES,
    POSITIONS_PER_PHASE,
    NullSamskara,
    Phase,
    PhaseResult,
    PhaseStatus,
    PipelineContext,
    PipelineExecutor,
    SamskaraProtocol,
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
    ScannedFile,
    ScannerProtocol,
    ScanProgress,
    ScanResult,
    extract_declarations,
    get_default_config,
    path_to_module,
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
