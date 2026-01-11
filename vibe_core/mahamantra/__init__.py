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

from typing import Final

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
    KSETRA_COUNT,
    MAHAJANA_COUNT,
    KSETRAJNA_COUNT,
    # Classes
    FractalNode,
    FractalTree,
    # Functions
    scale_up,
    scale_down,
    verify_fractal_integrity,
)

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
    "KSETRA_COUNT",
    "MAHAJANA_COUNT",
    "KSETRAJNA_COUNT",
    "FractalNode",
    "FractalTree",
    "scale_up",
    "scale_down",
    "verify_fractal_integrity",
]
