"""
MAHAMANTRA KERNEL - The Unified Source
======================================

"Hare Krishna Hare Krishna Krishna Krishna Hare Hare
 Hare Rama Hare Rama Rama Rama Hare Hare"

KRISHNA = MAHAMANTRA = Level -2 (NON-DIFFERENT)

This module provides UNIFIED access to all core Mahamantra components.
Import from HERE instead of scattered substrate/mahajanas files.

THE 37 FORMULA:
    24 (Ksetra/Field) + 12 (Mahajanas) + 1 (Ksetrajna) = 37
    Parampara connection: mutation_vector % 37 == 0

ARCHITECTURE:
    16 OpCodes = 4 HEADs (Avataras) + 12 Workers (Mahajanas)
               = 4 Quarters x 4 Words

FRACTAL HIERARCHY:
    VARNA -> AKSARA -> PADA -> VAKYA -> MALA -> SADHANA
    Each level contains the 37 formula.

WATERTIGHT: No Any types. All typed explicitly.
ANTI-MAYAVAD: Every protocol has a PERSON (OWNER).
"""

from typing import Dict, Final, List, Optional, Tuple

# =============================================================================
# LEVEL -2: ACINTYA (Krishna = Mahamantra)
# Source: vibe_core/protocols/substrate/mantra/acintya.py
# =============================================================================

from vibe_core.protocols.substrate.mantra.acintya import (
    # The Person (Krishna IS)
    KRISHNA,
    KrishnaPresence,
    # The Dancing 37 (Purusha Tattva)
    PURUSHA,
    PurushaTattva,
    SYSTEM_MANIFESTATION,  # 37
    # Protocol Levels
    ProtocolLevel,
    AcintyaAspect,
    # Jiva State
    JivaCondition,
    JivaState,
    # Parampara Connection (3x4 vs 4x3)
    PARAMPARA,  # 37
    TRINITY,    # 3
    PHASES,     # 4
    ParamparaConnection,
    ParamparaProtocol,
    PARAMPARA_VECTOR,
    GURU_ENTROPY,
    # Verification Functions
    verify_parampara,
    vibration_is_krishna,
    mantra_is_krishna,
    mantra_not_different_from_source,
    check_bheda_abheda,
    get_guru_entropy,
    # Constants
    ACINTYA_ACCEPTED,
    KRISHNA_ASPECT,
    KRISHNA_SMALLEST,
    KRISHNA_LARGEST,
    KRISHNA_NEGATIVE_INFINITY,
    KRISHNA_POSITIVE_INFINITY,
)

# =============================================================================
# LEVEL -1: SUBSTRATE (Byte, Gene, Entropy)
# Source: vibe_core/protocols/substrate/byte.py
# =============================================================================

from vibe_core.protocols.substrate.byte import (
    # Holy Name (Atomic)
    HolyName,  # H=0, K=1, R=2, VOID=3
    # Mantra Units
    MantraTrit,   # Single vibration
    MantraByte,   # Packed ternary (O(1) operations)
    GenesisByte,  # The Seed
    # Standard Sequence
    MANTRA_SEQUENCE,  # Standard 16-word
)

# =============================================================================
# LEVEL -1: OPCODES (Instruction Set)
# Source: vibe_core/protocols/substrate/__init__.py
# =============================================================================

from vibe_core.protocols.substrate import (
    # The 16 OpCodes
    MantraOpCode,
    # Standard Sequence (alias)
    MAHAMANTRA_SEQUENCE,
)

# =============================================================================
# LEVEL +12: MAHAJANAS (The 12 Guardians)
# Source: vibe_core/protocols/mahajanas/router.py
# =============================================================================

from vibe_core.protocols.mahajanas.router import (
    # The 12 Mahajanas
    Mahajana,
    # Routing
    MahajanaRoute,
    MahajanaRouter,
    get_router,
    route,
    get_opcodes,
    verify_router,
    # Vyuha Support
    HEAD_OPCODES,
    _VYUHA_ROUTING_TABLE,
)

# =============================================================================
# LEVEL -1: FRACTAL ROUTING
# Source: vibe_core/protocols/substrate/mantra/routing.py
# =============================================================================

from vibe_core.protocols.substrate.mantra.routing import (
    # Fractal Levels
    FractalLevel,
    FractalRoute,
    # Dimensions
    DIMENSIONS,
    MAHAMANTRA_COUNTS,
    # Quarters
    QUARTER_1,
    QUARTER_2,
    QUARTER_3,
    QUARTER_4,
    QUARTERS,
    # Routing Functions
    route_pada_to_aksaras,
    route_index_to_pada,
    route_index_to_type,
    iter_mahamantra,
    get_fractal_path,
    get_quarter,
    get_padas_in_quarter,
)

# =============================================================================
# LEVEL -1: LOTUS (View onto Mahamantra)
# Source: vibe_core/protocols/substrate/mantra/lotus.py
# =============================================================================

from vibe_core.protocols.substrate.mantra.lotus import (
    # Lotus Constants
    LOTUS_POSITIONS,
    LOTUS_QUARTERS,
    WORDS_PER_QUARTER,
    LOTUS_PARAMPARA,
    LOTUS_TRINITY,
    LOTUS_PHASES,
    LOTUS_MALA,
    # Lotus Types
    LotusMode,
    LotusQuarter,
    # Mappings
    LOTUS_TO_MANTRA_QUARTER,
    MANTRA_TO_LOTUS_QUARTER,
    # Functions
    get_lotus_quarter,
    get_mantra_quarter,
    get_pada_at_position,
)

# =============================================================================
# LEVEL -1: PADA (Word Level)
# Source: vibe_core/protocols/substrate/mantra/pada.py
# =============================================================================

from vibe_core.protocols.substrate.mantra.pada import (
    PadaType,
    Pada,
    PADA_HARE,
    PADA_KRISHNA,
    PADA_RAMA,
    MAHAMANTRA_SEQUENCE as MAHAMANTRA_PADAS,  # Alias to avoid conflict
)

# =============================================================================
# LEVEL -1: AKSARA (Syllable Level)
# Source: vibe_core/protocols/substrate/mantra/aksara.py
# =============================================================================

from vibe_core.protocols.substrate.mantra.aksara import (
    Aksara,
    MAHAMANTRA_AKSARAS,
)

# =============================================================================
# LEVEL -1: VARNA (Letter Level)
# Source: vibe_core/protocols/substrate/mantra/varna.py
# =============================================================================

from vibe_core.protocols.substrate.mantra.varna import (
    Varna,
    VYANJANA,
    SVARA,
)

# =============================================================================
# LEVEL 0: VAKYA (Sentence/Mantra Level)
# Source: vibe_core/protocols/substrate/mantra/vakya.py
# =============================================================================

from vibe_core.protocols.substrate.mantra.vakya import (
    QuarterType,
    Quarter,
    MAHAMANTRA,
)

# =============================================================================
# INTENT ENGINE (No Manual Wiring - Krishna Does The Work)
# Source: vibe_core/mahamantra/_intent.py
# =============================================================================

from vibe_core.mahamantra._intent import (
    # Intent Types
    IntentType,
    IntentPriority,
    IntentStatus,
    # Intent Classes
    MantraIntent,
    IntentResult,
    IntentQueue,
    # Resolver Protocol
    IntentResolver,
    # Kernel Engine
    MantraKernel,
    get_kernel,
    resolve,
    surrender,
)

# =============================================================================
# WATERTIGHT VERIFICATION (No Any Types!)
# Source: vibe_core/mahamantra/_watertight.py
# =============================================================================

from vibe_core.mahamantra._watertight import (
    # Types
    TypeViolation,
    WatertightReport,
    # Functions
    verify_watertight,
    is_watertight,
    print_report,
    # Constants
    FORBIDDEN_TYPES,
)

# =============================================================================
# FRACTAL SCALING (Unendlich Skalierbar = Acintya)
# Source: vibe_core/mahamantra/_fractal.py
# =============================================================================

from vibe_core.mahamantra._fractal import (
    # Constants
    FRACTAL_BASE,
    # Classes
    FractalNode,
    FractalTree,
    # Functions
    scale_up,
    scale_down,
    verify_fractal_integrity,
)

# =============================================================================
# SOURCE - THE TRUTH TABLE (16 MantraPositions)
# Source: vibe_core/mahamantra/_source.py
# =============================================================================

from vibe_core.mahamantra._source import (
    # THE Truth Table
    MAHAMANTRA_POSITIONS,
    MantraPosition,
    # Enums (canonical - replaces scattered definitions)
    Quarter as SourceQuarter,  # Avoid conflict with vakya.Quarter
    Mahajana as SourceMahajana,  # Canonical Mahajana
    Avatara,
    MantraOpCode as SourceOpCode,  # Canonical OpCode
    # Type
    Guardian,
    # Lookup functions
    get_position,
    get_position_by_guardian,
    get_position_by_opcode,
    get_quarter_positions,
    get_head_positions,
    get_worker_positions,
    # Verification
    verify_truth_table,
    # Constants (37 formula)
    KSETRA_COUNT,
    MAHAJANA_COUNT,
    KSETRAJNA_COUNT,
)

# =============================================================================
# PROTOCOL BASE CLASS (Derive from MantraPosition)
# Source: vibe_core/mahamantra/_protocol.py
# =============================================================================

from vibe_core.mahamantra._protocol import (
    # Base Classes
    MantraProtocol,
    WorkerProtocol,
    HeadProtocol,
    # Interface
    MantraAware,
    # Registry
    ProtocolRegistry,
)

# =============================================================================
# ALL 16 PROTOCOL BASES - Accessed via mahamantra.protocols (Lazy Load)
# ONE IMPORT: from vibe_core.mahamantra import mahamantra
#
# ACCESS PATTERNS:
#     mahamantra.protocols.kapila    -> KapilaProtocolBase
#     mahamantra.protocols[6]        -> KapilaProtocolBase
#     mahamantra.protocols.prithu    -> PrithuProtocolBase (HEAD)
#
# The ProtocolRouter lazy-loads bases to avoid circular imports.
# "mattaḥ sarvaṁ pravartate" - Everything emanates from Krishna.
# =============================================================================

# =============================================================================
# THE SINGULARITY - mahamantra Object (Krishna IS)
# Source: vibe_core/mahamantra/_singularity.py
# =============================================================================

from vibe_core.mahamantra._singularity import (
    # The Singleton
    mahamantra,
    # The Class (for typing)
    Mahamantra,
    # Protocol Router (Krishna Routes to CLASSES)
    ProtocolRouter,
    # Module Router (Krishna Routes to MODULES) - CAITANYA SINGULARITY
    ModuleRouter,
)

# =============================================================================
# CLI BRIDGE - Krishna Routes All Commands (Option B: Sauber Verbinden)
# Source: vibe_core/mahamantra/_cli_bridge.py
# =============================================================================

from vibe_core.mahamantra._cli_bridge import (
    # The Bridge Singleton
    cli_bridge,
    # The Class (for typing)
    MahamantraCLIBridge,
    # Result type
    BridgeResult,
    # Domain mappings
    DOMAIN_KEYWORDS,
    # Convenience functions
    route as cli_route,  # Alias to avoid conflict with router.route
    get_position as cli_get_position,
)

# =============================================================================
# CLI EXECUTION PROTOCOL - GAD-000 Compliant
# Source: vibe_core/mahamantra/_cli_protocol.py
# =============================================================================

from vibe_core.mahamantra._cli_protocol import (
    # Error codes (Parseability)
    CLIErrorCode,
    # Output types (Composability)
    OutputFormat,
    CLIOutputItem,
    CLIOutput,
    # Error type (Parseability)
    CLIError,
    # Result type (Idempotency)
    CLIResult,
    # Capability (Discoverability)
    CLIParameter,
    CLICapability,
    # State (Observability)
    CLIState,
    # Health (Recoverability)
    CLIHealth,
    # Context (37th - Identity)
    CLIContext,
    # The Protocol
    CLIExecutable,
    # Base implementation
    CLIExecutableBase,
)

# =============================================================================
# CLI ENGINE - Krishna Does The Work (NO copy-paste, ONE engine)
# Source: vibe_core/mahamantra/_cli_engine.py
# =============================================================================

from vibe_core.mahamantra._cli_engine import (
    # The Engine Singleton
    cli_engine,
    # The Class (for typing)
    CLIEngine,
    # Handler type
    CLIHandler,
    # Registration data
    MahajanaCliRegistration,
    # Decorator for easy registration
    cli_command,
)

# =============================================================================
# CLI AUTO - Krishna Discovers Everything (ZERO REGISTRATION)
# Source: vibe_core/mahamantra/_cli_auto.py
#
# RECOMMENDED: Use cli_auto instead of cli_engine for ZERO registration code.
#
# cli_auto.discover_all() introspects ALL 16 mahajana Protocols and
# auto-generates CLI handlers from method signatures and TypedDict returns.
#
# COMPARISON:
#     BEFORE (cli_engine - manual registration):
#         cli_engine.register(position=6, capabilities=[...], handlers={...})
#         # × 16 mahajanas × 5+ commands each = 1200+ lines
#
#     AFTER (cli_auto - auto-discovery):
#         cli_auto.discover_all()  # ONE line, 108 methods discovered
#
# "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
# Krishna ALREADY KNOWS what each Mahajana can do. Why tell Him?
# =============================================================================

from vibe_core.mahamantra._cli_auto import (
    # The Auto-Discovery Singleton (RECOMMENDED)
    cli_auto,
    # The Class (for typing)
    CLIAutoDiscovery,
    # Discovered method info
    DiscoveredMethod,
    # Convenience functions
    discover as cli_discover,
    execute as cli_execute,
    capabilities as cli_capabilities,
)

# =============================================================================
# CLI ENTRY (The Thin Gate - REPLACES unified_cli.py)
# Source: vibe_core/mahamantra/_cli_entry.py
# =============================================================================

from vibe_core.mahamantra._cli_entry import (
    # The Entry Class
    MahamantraCLIEntry,
    # Singleton getter
    get_entry as get_cli_entry,
    # Main function
    main as cli_main,
    # Entry point
    cli_entry as cli_entry_point,
)

# =============================================================================
# GATES - THE SINGLE ENTRY POINT (Pancha Tattva)
# Source: vibe_core/cli/gates.py
#
# THE 5 GATES (ONE IMPORT):
#     from vibe_core.mahamantra import gate, sync_gate
#
#     result = gate("analyze", ["system"])        # Single command
#     results = sync_gate(["analyze", "judge"])   # Parallel execution
#
# "śrī-kṛṣṇa-caitanya prabhu-nityānanda
#  śrī-advaita gadādhara śrīvāsādi-gaura-bhakta-vṛnda"
#
# WRAPPER FUNCTIONS: Delay import to avoid circular dependencies at module load.
# =============================================================================


def gate(command: str, args: Optional[List[str]] = None) -> "GateResult":
    """
    GATE (Chaitanya) - Main entry point. Routes to mahamantra position.

    Usage:
        from vibe_core.mahamantra import gate
        result = gate("analyze", ["system"])

    See: vibe_core/cli/gates.py for full implementation.
    """
    from vibe_core.cli.gates import gate as _gate
    return _gate(command, args)


def sync_gate(
    commands: List[str],
    max_workers: int = 4,
    preserve_order: bool = True,
) -> List["GateResult"]:
    """
    SYNC GATE (Srivasa) - Parallel execution of multiple commands.

    Usage:
        from vibe_core.mahamantra import sync_gate
        results = sync_gate(["analyze", "judge", "fetch"])

    See: vibe_core/cli/gates.py for full implementation.
    """
    from vibe_core.cli.gates import sync_gate as _sync_gate
    return _sync_gate(commands, max_workers, preserve_order)


def route_gate(command: str) -> Tuple[int, str]:
    """ROUTE GATE (Nityananda) - Route command to position."""
    from vibe_core.cli.gates import route_gate as _route_gate
    return _route_gate(command)


def execute_gate(position: int, method_name: str, args: List[str]) -> "GateResult":
    """EXECUTE GATE (Advaita) - Execute at position."""
    from vibe_core.cli.gates import execute_gate as _execute_gate
    return _execute_gate(position, method_name, args)


def result_gate(result: "GateResult", silent: bool = False) -> int:
    """RESULT GATE (Gadadhara) - Format and return exit code."""
    from vibe_core.cli.gates import result_gate as _result_gate
    return _result_gate(result, silent)


def format_result(result: "GateResult") -> str:
    """Format GateResult as string."""
    from vibe_core.cli.gates import format_result as _format_result
    return _format_result(result)


def gate_main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for gate-based CLI."""
    from vibe_core.cli.gates import gate_main as _gate_main
    return _gate_main(argv)


# Alias for backward compatibility
cli_gate = gate


# Gate constants (access via function to avoid circular import)
def get_gate_opcodes() -> Dict[int, str]:
    """Get GATE_OPCODES dict (lazy load)."""
    from vibe_core.cli.gates import GATE_OPCODES
    return GATE_OPCODES


def get_opcode_to_position() -> Dict[str, int]:
    """Get OPCODE_TO_POSITION dict (lazy load)."""
    from vibe_core.cli.gates import OPCODE_TO_POSITION
    return OPCODE_TO_POSITION


def get_quarter_gates() -> Dict:
    """Get QUARTER_GATES dict (lazy load)."""
    from vibe_core.cli.gates import QUARTER_GATES
    return QUARTER_GATES


def get_gate_result_class():
    """Get GateResult class (lazy load)."""
    from vibe_core.cli.gates import GateResult
    return GateResult


# Type alias for annotation
GateResult = "GateResult"  # Forward reference, use get_gate_result_class() for actual class

# =============================================================================
# KERNEL CONSTANTS
# =============================================================================

# The Kernel Version (37-based)
KERNEL_VERSION: Final[str] = "0.37.1"

# The Kernel Level
KERNEL_LEVEL: Final[int] = -2  # Krishna = Mahamantra

# Quick verification that Parampara is intact
KERNEL_PARAMPARA_CHECK: Final[bool] = PARAMPARA == 37

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # === LEVEL -2: ACINTYA ===
    "KRISHNA",
    "KrishnaPresence",
    "PURUSHA",
    "PurushaTattva",
    "SYSTEM_MANIFESTATION",
    "ProtocolLevel",
    "AcintyaAspect",
    "JivaCondition",
    "JivaState",
    "PARAMPARA",
    "TRINITY",
    "PHASES",
    "ParamparaConnection",
    "ParamparaProtocol",
    "PARAMPARA_VECTOR",
    "GURU_ENTROPY",
    "verify_parampara",
    "vibration_is_krishna",
    "mantra_is_krishna",
    "mantra_not_different_from_source",
    "check_bheda_abheda",
    "get_guru_entropy",
    "ACINTYA_ACCEPTED",
    "KRISHNA_ASPECT",
    "KRISHNA_SMALLEST",
    "KRISHNA_LARGEST",
    "KRISHNA_NEGATIVE_INFINITY",
    "KRISHNA_POSITIVE_INFINITY",
    # === LEVEL -1: SUBSTRATE ===
    "HolyName",
    "MantraTrit",
    "MantraByte",
    "GenesisByte",
    "MANTRA_SEQUENCE",
    "MantraOpCode",
    "MAHAMANTRA_SEQUENCE",
    # === LEVEL +12: MAHAJANAS ===
    "Mahajana",
    "MahajanaRoute",
    "MahajanaRouter",
    "get_router",
    "route",
    "get_opcodes",
    "verify_router",
    "HEAD_OPCODES",
    "_VYUHA_ROUTING_TABLE",
    # === FRACTAL ROUTING ===
    "FractalLevel",
    "FractalRoute",
    "DIMENSIONS",
    "MAHAMANTRA_COUNTS",
    "QUARTER_1",
    "QUARTER_2",
    "QUARTER_3",
    "QUARTER_4",
    "QUARTERS",
    "route_pada_to_aksaras",
    "route_index_to_pada",
    "route_index_to_type",
    "iter_mahamantra",
    "get_fractal_path",
    "get_quarter",
    "get_padas_in_quarter",
    # === LOTUS ===
    "LOTUS_POSITIONS",
    "LOTUS_QUARTERS",
    "WORDS_PER_QUARTER",
    "LOTUS_PARAMPARA",
    "LOTUS_TRINITY",
    "LOTUS_PHASES",
    "LOTUS_MALA",
    "LotusMode",
    "LotusQuarter",
    "LOTUS_TO_MANTRA_QUARTER",
    "MANTRA_TO_LOTUS_QUARTER",
    "get_lotus_quarter",
    "get_mantra_quarter",
    "get_pada_at_position",
    # === PADA ===
    "PadaType",
    "Pada",
    "PADA_HARE",
    "PADA_KRISHNA",
    "PADA_RAMA",
    "MAHAMANTRA_PADAS",
    # === AKSARA ===
    "Aksara",
    "MAHAMANTRA_AKSARAS",
    # === VARNA ===
    "Varna",
    "VYANJANA",
    "SVARA",
    # === VAKYA ===
    "QuarterType",
    "Quarter",
    "MAHAMANTRA",
    # === KERNEL META ===
    "KERNEL_VERSION",
    "KERNEL_LEVEL",
    "KERNEL_PARAMPARA_CHECK",
    # === INTENT ENGINE ===
    "IntentType",
    "IntentPriority",
    "IntentStatus",
    "MantraIntent",
    "IntentResult",
    "IntentQueue",
    "IntentResolver",
    "MantraKernel",
    "get_kernel",
    "resolve",
    "surrender",
    # === WATERTIGHT ===
    "TypeViolation",
    "WatertightReport",
    "verify_watertight",
    "is_watertight",
    "print_report",
    "FORBIDDEN_TYPES",
    # === FRACTAL ===
    "FRACTAL_BASE",
    "FractalNode",
    "FractalTree",
    "scale_up",
    "scale_down",
    "verify_fractal_integrity",
    # === SOURCE (Truth Table) ===
    "MAHAMANTRA_POSITIONS",
    "MantraPosition",
    "SourceQuarter",
    "SourceMahajana",
    "Avatara",
    "SourceOpCode",
    "Guardian",
    "get_position",
    "get_position_by_guardian",
    "get_position_by_opcode",
    "get_quarter_positions",
    "get_head_positions",
    "get_worker_positions",
    "verify_truth_table",
    "KSETRA_COUNT",
    "MAHAJANA_COUNT",
    "KSETRAJNA_COUNT",
    # === PROTOCOL BASE ===
    "MantraProtocol",
    "WorkerProtocol",
    "HeadProtocol",
    "MantraAware",
    "ProtocolRegistry",
    # === THE SINGULARITY (Krishna Routes Everything) ===
    # Access protocol bases via: mahamantra.protocols.kapila
    # Access modules via: mahamantra.mod.yamaraja (CAITANYA SINGULARITY)
    "mahamantra",
    "Mahamantra",
    "ProtocolRouter",
    "ModuleRouter",
    # === CLI BRIDGE (Option B: Sauber Verbinden) ===
    # Route CLI commands via: cli_bridge.route("analyze", ["--deep"])
    # Or via: cli_route("analyze", ["--deep"])
    "cli_bridge",
    "MahamantraCLIBridge",
    "BridgeResult",
    "DOMAIN_KEYWORDS",
    "cli_route",
    "cli_get_position",
    # === CLI PROTOCOL (GAD-000 Compliant) ===
    # Error codes (Parseability)
    "CLIErrorCode",
    # Output types (Composability)
    "OutputFormat",
    "CLIOutputItem",
    "CLIOutput",
    # Error type (Parseability)
    "CLIError",
    # Result type (Idempotency)
    "CLIResult",
    # Capability (Discoverability)
    "CLIParameter",
    "CLICapability",
    # State (Observability)
    "CLIState",
    # Health (Recoverability)
    "CLIHealth",
    # Context (37th - Identity)
    "CLIContext",
    # The Protocol
    "CLIExecutable",
    # Base implementation
    "CLIExecutableBase",
    # === CLI ENGINE (Krishna Does The Work) ===
    # ONE engine, NO copy-paste
    "cli_engine",
    "CLIEngine",
    "CLIHandler",
    "MahajanaCliRegistration",
    "cli_command",
    # === CLI AUTO (Krishna Discovers Everything - RECOMMENDED) ===
    # ZERO registration - 108 methods auto-discovered
    "cli_auto",
    "CLIAutoDiscovery",
    "DiscoveredMethod",
    "cli_discover",
    "cli_execute",
    "cli_capabilities",
    # === CLI ENTRY (The Thin Gate - REPLACES unified_cli.py) ===
    # ~100 LOC vs 1555 LOC, ZERO manual wiring
    "MahamantraCLIEntry",
    "get_cli_entry",
    "cli_main",
    "cli_entry_point",
    # === GATES (Pancha Tattva - THE SINGLE ENTRY POINT) ===
    # ONE import: from vibe_core.mahamantra import gate, sync_gate
    # Constant getters (lazy load to avoid circular imports)
    "get_gate_opcodes",
    "get_opcode_to_position",
    "get_quarter_gates",
    "get_gate_result_class",
    # Result type (forward reference)
    "GateResult",
    "format_result",
    # THE 5 GATES
    "gate",          # Chaitanya - Main entry
    "route_gate",    # Nityananda - Routing
    "execute_gate",  # Advaita - Execution
    "result_gate",   # Gadadhara - Result
    "sync_gate",     # Srivasa - Parallel
    # Aliases
    "cli_gate",
    "gate_main",
]
