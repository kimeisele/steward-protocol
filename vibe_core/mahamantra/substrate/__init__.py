"""
SUBSTRATE - Die Grundlage des Mahamantra
========================================

Level -2 bis -1: Das Fundament auf dem alles aufbaut.

LEVEL -2 (ACINTYA):
    Krishna = Mahamantra = NON-DIFFERENT
    Das Unbegreifliche, das IS (nicht "repräsentiert")

LEVEL -1 (SUBSTRATE):
    Byte, Gene, Entropy
    Die manifestierte Form von -2

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya"
"O Arjuna, there is no truth superior to Me."
— Bhagavad Gita 7.7
"""

# =============================================================================
# MAHAJANA - Die 12 + 4 (Base Types)
# =============================================================================

from vibe_core.mahamantra.substrate.mahajana import (
    # Die 12 Mahajanas
    Mahajana,
    MAHAJANA_COUNT,
    # Die 4 Avataras
    Avatara,
    AVATARA_COUNT,
    # Die 4 Quarters
    Quarter,
    # Die 4 Sampradayas
    Sampradaya,
    # Total
    TOTAL_POSITIONS,
)

# =============================================================================
# TATTVA - Purushottama (Krishna als Person)
# =============================================================================

from vibe_core.mahamantra.substrate.tattva import (
    Purushottama,
    PURUSHOTTAMA,
    KshetraElement,
    GuruTattva,
    GuruConnection,
    JIVA,
)

# =============================================================================
# ACINTYA - Das Unbegreifliche (Level -2)
# =============================================================================

from vibe_core.mahamantra.substrate.acintya import (
    # Konstanten
    SYSTEM_MANIFESTATION,
    ACINTYA_ACCEPTED,
    TRINITY,
    PARAMPARA,
    PHASES,
    GURU_ENTROPY,
    PARAMPARA_VECTOR,
    # Purusha (Die tanzende 37)
    PurushaTattva,
    PURUSHA,
    KRISHNA_ASPECT,
    KRISHNA_SMALLEST,
    KRISHNA_LARGEST,
    # Level System
    ProtocolLevel,
    AcintyaAspect,
    # Krishna Presence
    KrishnaPresence,
    KRISHNA,
    # Jiva
    JivaCondition,
    JivaState,
    # Protocols
    AcintyaAware,
    ParamparaProtocol,
    ParamparaConnection,
    # Functions
    vibration_is_krishna,
    mantra_is_krishna,
    mantra_not_different_from_source,
    check_bheda_abheda,
    verify_parampara,
    get_guru_entropy,
)

# =============================================================================
# BYTE - Das ternäre Substrat (Level -1)
# =============================================================================

from vibe_core.mahamantra.substrate.byte import (
    # Holy Names
    HolyName,
    # Trit (Single vibration)
    MantraTrit,
    # Byte (Packed ternary)
    MantraByte,
    # Genesis Byte
    GenesisByte,
)

# =============================================================================
# WIRING - Folder IS Wiring Protocol
# =============================================================================

from vibe_core.mahamantra.substrate.wiring import (
    # Constants
    FOLDER_IS_WIRING,
    NO_FOLDER_NO_EXISTENCE,
    POSITIONS_PER_QUARTER,
    QUARTER_COUNT,
    FRACTAL_BASE,
    # Mapping
    PositionMapping,
    POSITION_MAPPINGS,
    POSITION_BY_FOLDER,
    POSITION_BY_NAME,
    POSITION_BY_INDEX,
    # Functions
    folder_exists,
    get_position_from_folder,
    get_position_from_name,
    get_position_by_index,
    # Protocol
    WiringProtocol,
    WiringVerification,
    verify_wiring,
    # Fractal
    calculate_fractal_depth,
    calculate_total_nodes,
)

# =============================================================================
# PARAMPARA - Single Source of Truth
# =============================================================================

from vibe_core.mahamantra.substrate.parampara import (
    ParamparaNode,
    PARAMPARA_GRAPH,
    # Functions
    get_position,
    get_quarter,
    get_sampradaya,
    get_guru,
    get_mahajana_at_position,
    get_37_formula,
)

# =============================================================================
# OPCODE - Die 16 OpCodes (SSOT)
# =============================================================================

from vibe_core.mahamantra.substrate.opcode import (
    # The OpCode enum
    MantraOpCode,
    # Lookup tables
    OPCODE_NAMES,
    MAHAJANA_OPCODES,
    # Quarter groupings
    GENESIS_OPCODES,
    DHARMA_OPCODES,
    KARMA_OPCODES,
    MOKSHA_OPCODES,
    QUARTER_OPCODES,
    # Functions
    get_opcode,
    get_opcode_name,
    get_mahajana_opcode,
    get_opcode_quarter,
    get_quarter_opcodes,
    # Parampara
    OPCODE_PARAMPARA,
    get_opcode_parampara,
    verify_opcode_parampara,
)

# =============================================================================
# POSITION - Die 16 MantraPositionen (SSOT)
# =============================================================================

from vibe_core.mahamantra.substrate.position import (
    # Types
    Guardian,
    # Position
    MantraPosition,
    MAHAMANTRA_POSITIONS,
    # Functions
    get_position as get_position_by_index,  # Takes int 0-15
    get_position_by_guardian,
    get_position_by_opcode,
    get_positions_by_quarter,
    get_head_position,
    get_worker_positions,
    get_worker_positions_for_quarter,
    get_all_head_positions,
    get_all_worker_positions,
    # Aliases
    get_quarter_positions,
)

# =============================================================================
# PROTOCOL - MantraProtocol Basisklassen (SSOT)
# =============================================================================

from vibe_core.mahamantra.substrate.protocol import (
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
# PANCHA TATTVA - Die 5 Persönlichkeiten (SSOT)
# =============================================================================
#
# Die Essenz des Mahamantra offenbart sich nur durch sie.
# byte.py = unpersönliche Mathematik
# pancha_tattva.py = persönlicher Einstieg
#

from vibe_core.mahamantra.substrate.pancha_tattva import (
    # Main Enum
    PanchaTattva,
    TattvaIndex,
    # Aspect
    TattvaAspect,
    PANCHA_TATTVA_ASPECTS,
    # Lookup
    get_tattva_aspect,
    get_tattva_by_index,
    get_tattva_by_capability,
    get_tattva_by_protocol,
    # Byte Mapping
    TATTVA_TO_HOLYNAME,
    tattva_to_trit,
    # Gates
    TattvaGate,
    GATE_TO_TATTVA,
    # Protocol
    PanchaTattvaAware,
    # Position Mapping
    get_tattva_for_position,
    # Parampara
    PANCHA_TATTVA_COUNT,
    PANCHA_TATTVA_VECTOR,
    verify_pancha_tattva_parampara,
    # Prayer
    PANCHA_TATTVA_MANTRA,
    PANCHA_TATTVA_MEANING,
)

# =============================================================================
# WATERTIGHT - Type Integrity Verification
# =============================================================================

from vibe_core.mahamantra.substrate.watertight import (
    # Types
    TypeViolation,
    WatertightReport,
    # Functions
    check_file,
    check_directory,
    verify_watertight,
    print_report,
    is_watertight,
    # Constants
    FORBIDDEN_TYPES,
)

# =============================================================================
# SCANNER - Auto-Discovery of Declarations
# =============================================================================

from vibe_core.mahamantra.substrate.scanner import (
    # Alias
    MahajanaAlias,
    MAHAJANA_ALIASES,
    resolve_mahajana,
    get_position as get_mahajana_position,
    get_name as get_mahajana_name,
    # Declaration
    SimpleDeclaration,
    # Scanner
    ScanResult,
    scan_all,
    # Governance
    scan_for_governance,
    print_scan_report,
)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # === MAHAJANA ===
    "Mahajana",
    "MAHAJANA_COUNT",
    "Avatara",
    "AVATARA_COUNT",
    "Quarter",
    "Sampradaya",
    "TOTAL_POSITIONS",
    # === TATTVA ===
    "Purushottama",
    "PURUSHOTTAMA",
    "KshetraElement",
    "GuruTattva",
    "GuruConnection",
    "JIVA",
    # === ACINTYA ===
    "SYSTEM_MANIFESTATION",
    "ACINTYA_ACCEPTED",
    "TRINITY",
    "PARAMPARA",
    "PHASES",
    "GURU_ENTROPY",
    "PARAMPARA_VECTOR",
    "PurushaTattva",
    "PURUSHA",
    "KRISHNA_ASPECT",
    "KRISHNA_SMALLEST",
    "KRISHNA_LARGEST",
    "ProtocolLevel",
    "AcintyaAspect",
    "KrishnaPresence",
    "KRISHNA",
    "JivaCondition",
    "JivaState",
    "AcintyaAware",
    "ParamparaProtocol",
    "ParamparaConnection",
    "vibration_is_krishna",
    "mantra_is_krishna",
    "mantra_not_different_from_source",
    "check_bheda_abheda",
    "verify_parampara",
    "get_guru_entropy",
    # === BYTE ===
    "HolyName",
    "MantraTrit",
    "MantraByte",
    "GenesisByte",
    # === PARAMPARA ===
    "ParamparaNode",
    "PARAMPARA_GRAPH",
    "get_position",
    "get_quarter",
    "get_sampradaya",
    "get_guru",
    "get_mahajana_at_position",
    "get_37_formula",
    # === WIRING ===
    "FOLDER_IS_WIRING",
    "NO_FOLDER_NO_EXISTENCE",
    "POSITIONS_PER_QUARTER",
    "QUARTER_COUNT",
    "FRACTAL_BASE",
    "PositionMapping",
    "POSITION_MAPPINGS",
    "POSITION_BY_FOLDER",
    "POSITION_BY_NAME",
    "POSITION_BY_INDEX",
    "folder_exists",
    "get_position_from_folder",
    "get_position_from_name",
    "get_position_by_index",
    "WiringProtocol",
    "WiringVerification",
    "verify_wiring",
    "calculate_fractal_depth",
    "calculate_total_nodes",
    # === OPCODE (SSOT) ===
    "MantraOpCode",
    "OPCODE_NAMES",
    "MAHAJANA_OPCODES",
    "GENESIS_OPCODES",
    "DHARMA_OPCODES",
    "KARMA_OPCODES",
    "MOKSHA_OPCODES",
    "QUARTER_OPCODES",
    "get_opcode",
    "get_opcode_name",
    "get_mahajana_opcode",
    "get_opcode_quarter",
    "get_quarter_opcodes",
    "OPCODE_PARAMPARA",
    "get_opcode_parampara",
    "verify_opcode_parampara",
    # === POSITION (SSOT) ===
    "Guardian",
    "MantraPosition",
    "MAHAMANTRA_POSITIONS",
    "get_position_by_index",  # Takes int 0-15
    "get_position_by_guardian",
    "get_position_by_opcode",
    "get_positions_by_quarter",
    "get_head_position",
    "get_worker_positions",
    "get_worker_positions_for_quarter",
    "get_all_head_positions",
    "get_all_worker_positions",
    "get_quarter_positions",
    # === PROTOCOL (SSOT) ===
    "MantraProtocol",
    "WorkerProtocol",
    "HeadProtocol",
    "MantraAware",
    "ProtocolRegistry",
    # === PANCHA TATTVA (SSOT) ===
    "PanchaTattva",
    "TattvaIndex",
    "TattvaAspect",
    "PANCHA_TATTVA_ASPECTS",
    "get_tattva_aspect",
    "get_tattva_by_index",
    "get_tattva_by_capability",
    "get_tattva_by_protocol",
    "TATTVA_TO_HOLYNAME",
    "tattva_to_trit",
    "TattvaGate",
    "GATE_TO_TATTVA",
    "PanchaTattvaAware",
    "get_tattva_for_position",
    "PANCHA_TATTVA_COUNT",
    "PANCHA_TATTVA_VECTOR",
    "verify_pancha_tattva_parampara",
    "PANCHA_TATTVA_MANTRA",
    "PANCHA_TATTVA_MEANING",
    # === WATERTIGHT (Type Integrity) ===
    "TypeViolation",
    "WatertightReport",
    "check_file",
    "check_directory",
    "verify_watertight",
    "print_report",
    "is_watertight",
    "FORBIDDEN_TYPES",
    # === SCANNER (Discovery) ===
    "MahajanaAlias",
    "MAHAJANA_ALIASES",
    "resolve_mahajana",
    "get_mahajana_position",
    "get_mahajana_name",
    "SimpleDeclaration",
    "ScanResult",
    "scan_all",
    "scan_for_governance",
    "print_scan_report",
]
