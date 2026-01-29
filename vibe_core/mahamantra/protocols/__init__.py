"""
MAHAMANTRA PROTOCOLS - The Protocols That Define Protocols
==========================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

This module contains the META-PROTOCOLS:

LEVEL -2 (ACINTYA):
- _core.py: What IS a protocol? (self-referential)
- _declaration.py: How does something declare itself?
- _fractal.py: How does something grow fractally?
- _holographic.py: How does each part contain the whole?

LEVEL 0 (CONTRACT):
- _lotus.py: The Mahamantra as Kernel (16 petals)
- _graph.py: Vedic knowledge graphs
- _bridge.py: Fractal bridges between parts
- _steward.py: System identity (THE Steward)

ACINTYA PRINCIPLE:
    These protocols define themselves.
    The Protocol Protocol IS a protocol.
    Krishna knowing Krishna through Krishna.

USAGE:
    from vibe_core.mahamantra.protocols import MahamantraProtocol

    class MyProtocol(MahamantraProtocolBase):
        __protocol_identity__ = ProtocolIdentity(
            name="MyProtocol",
            mahajana="brahma",
            position=1,
            level=Level.CONTRACT,
            quarter=Quarter.GENESIS,
        )
        __protocol_capability__ = ProtocolCapability.create(
            provides=["my_capability"],
            requires=["CoreProtocol"],
        )
"""

# =============================================================================
# CORE - The Protocol Protocol
# =============================================================================

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xbe27e031"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# SEED - The Mathematical Constitution
# =============================================================================

from vibe_core.mahamantra.protocols._seed import (
    # Sacred Constants
    WORDS,
    TRINITY,
    QUARTERS,
    PANCHA,
    SHARANAGATI,
    NAVA,
    LILA,
    MALA,
    # Resolution Constants (COSMIC_FRAME)
    COSMIC_FRAME,
    NAKSHATRA_UNIT,
    TITHI_UNIT,
    PADA_UNIT,
    QUARTER_UNIT,
    # Derived Constants
    HARE_COUNT,
    KRISHNA_COUNT,
    RAMA_COUNT,
    KSHETRA,
    # KSHETRA_GAD removed - was Shaiva, not Gaudiya
    MAHAJANA_COUNT,
    AVATAR_COUNT,
)

from vibe_core.mahamantra.protocols._core import (
    # Constants - The 37 Formula
    KSETRA_COUNT,
    MAHAJANA_COUNT,
    KSETRAJNA_COUNT,
    PARAMPARA,
    # Enums
    Quarter,
    Level,
    # Identity & Capability
    ProtocolIdentity,
    ProtocolCapability,
    # The Protocol Protocol
    MahamantraProtocol,
    MahamantraProtocolBase,
    # Self-reference
    CoreProtocol,
)

# =============================================================================
# DECLARATION - How things declare themselves
# =============================================================================

from vibe_core.mahamantra.protocols._declaration import (
    # Types
    DeclarationType,
    # Card
    MahajanaCard,
    # Module Declaration
    ModuleDeclaration,
    # Registry
    DeclarationRegistry,
    # Protocol
    DeclarationProtocol,
    # Helper
    read_declaration,
)

# =============================================================================
# FRACTAL - How things grow
# =============================================================================

from vibe_core.mahamantra.protocols._fractal import (
    # Address
    FractalAddress,
    # Node
    FractalNode,
    # Tree
    FractalTree,
    # Growth
    GrowthPattern,
    GrowthRule,
    # Protocol
    FractalProtocol,
)

# =============================================================================
# HOLOGRAPHIC - Each part contains the whole
# =============================================================================

from vibe_core.mahamantra.protocols._holographic import (
    # Hologram
    Hologram,
    # Coherence
    CoherenceLevel,
    CoherencePolicy,
    # Reflection & Projection
    Reflector,
    Projector,
    # System
    HolographicSystem,
    # Protocol
    HolographicProtocol,
    # Singleton
    get_holographic_system,
)

# =============================================================================
# LOTUS - The Mahamantra as Kernel
# =============================================================================

from vibe_core.mahamantra.protocols._lotus import (
    # Constants
    LOTUS_PETALS,
    LOTUS_QUARTERS,
    PETALS_PER_QUARTER,
    MALA_BEADS,
    # Mappings
    MAHAJANA_POSITIONS,
    POSITION_MAHAJANAS,
    get_mahajana_position,
    get_position_mahajana,
    # Enums
    LotusMode,
    # Types
    LotusPetal,
    LotusState,
    LotusRoute,
    # Protocol
    LotusProtocol,
    # Base Class
    LotusBase,
    # Tree (Fractal)
    LotusTree,
    # Hologram
    LotusHologram,
    # Protocol Definition
    LotusProtocolDef,
)

# =============================================================================
# GRAPH - Vedic Knowledge Graphs
# =============================================================================

from vibe_core.mahamantra.protocols._graph import (
    # Constants
    PRAKRITI_COUNT,
    PURIFICATION_CYCLE,
    # Enums
    NodeType,
    EdgeType,
    Sampradaya,
    # Types
    GraphNode,
    GraphEdge,
    # Protocol
    GraphProtocol,
    # Implementation
    VedicGraph,
    # Builder
    GraphBuilder,
    # Protocol Graph
    ProtocolGraph,
    # Protocol Definition
    GraphProtocolDef,
)

# =============================================================================
# BRIDGE - Fractal Bridges
# =============================================================================

from vibe_core.mahamantra.protocols._bridge import (
    # Enums
    BridgeType,
    BridgeDirection,
    BridgeState,
    # Types
    BridgeEndpoint,
    BridgeSpec,
    Bridge,
    # Protocol
    BridgeProtocol,
    # Registry
    BridgeRegistry,
    get_bridge_registry,
    # Builder
    BridgeBuilder,
    # Protocol Definition
    BridgeProtocolDef,
)

# =============================================================================
# STEWARD - System Identity
# =============================================================================

from vibe_core.mahamantra.protocols._steward import (
    # Constants
    STEWARD_NAME,
    STEWARD_VERSION,
    # Enums
    StewardMode,
    StewardHealth,
    # State
    StewardState,
    # Audit
    StewardAudit,
    # System
    StewardSystem,
    # Protocol
    StewardProtocol,
    # Protocol Definition
    StewardProtocolDef,
    # Convenience
    get_steward,
    steward,
)

# =============================================================================
# GAD - Operator Inversion Principle
# =============================================================================

from vibe_core.mahamantra.protocols._gad import (
    # Constants
    CRITERIA_COUNT,
    # KSHETRA_SIZE removed - was invented 6×6 matrix without Shastra basis
    KSHETRAJNA,
    DHARMA_COUNT,
    MANTRA_CHECKS,
    # Enums
    GADCriterion,
    DharmaPrinciple,
    JapaState,
    HolyName,
    # Heartbeat
    MantraHeartbeat,
    # Audit
    GADAudit,
    # Protocol
    GADProtocol,
    # Base Class
    GADBase,
    # Formula
    legitimacy_formula,
    # Protocol Definition
    GADProtocolDef,
)

# =============================================================================
# OPCODE - From SSOT (substrate/opcode.py)
# =============================================================================
# NOTE: OpCodes are now SSOT in substrate/opcode.py
# Import from there, not from protocols/_opcode.py (DELETED)

from vibe_core.mahamantra.substrate.opcode import (
    MantraOpCode,
    OPCODE_NAMES,
    MAHAJANA_OPCODES,
    get_opcode,
    get_opcode_name,
    get_mahajana_opcode,
)

# =============================================================================
# VEDA & GOVERNANCE - Lazy loaded to avoid circular imports
# =============================================================================
# These are loaded on first access to prevent:
# mahamantra -> protocols -> veda -> protocols.mahajanas -> mahamantra (cycle)

_LAZY_VEDA = {
    "VedaProtocol": "veda",
    "VedaMixin": "veda",
    "is_vedic": "veda",
    "veda_audit": "veda",
    "ShabdaProtocol": "veda",
    "ArthaProtocol": "veda",
    "PratyayaProtocol": "veda",
    "KarmaProtocol": "veda",
    "ProtocolBridge": "governance.bridge",
}


def __getattr__(name: str):
    """Lazy load veda and governance to avoid circular imports."""
    # 1. Check explicit class/function exports
    if name in _LAZY_VEDA:
        module_path = _LAZY_VEDA[name]
        import importlib

        module = importlib.import_module(f"vibe_core.protocols.{module_path}")
        return getattr(module, name)

    # ==========================================================================
    # FRACTAL ROUTING: "EIN IMPORT. KRISHNA ROUTET ALLES."
    # Any .py file or subpackage in protocols/ is auto-discoverable
    # ==========================================================================
    from pathlib import Path
    import importlib

    protocols_root = Path(__file__).parent

    # 2. Check for subpackage (folder with __init__.py)
    subpkg_path = protocols_root / name
    if subpkg_path.is_dir() and (subpkg_path / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    # 3. Check for module (.py file) - handle _prefix modules too
    for module_name in [name, f"_{name}"]:
        module_path = protocols_root / f"{module_name}.py"
        if module_path.exists():
            return importlib.import_module(f"{__name__}.{module_name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # === CORE ===
    # Constants
    "KSETRA_COUNT",
    "MAHAJANA_COUNT",
    "KSETRAJNA_COUNT",
    "PARAMPARA",
    # Enums
    "Quarter",
    "Level",
    # Identity & Capability
    "ProtocolIdentity",
    "ProtocolCapability",
    # Protocol
    "MahamantraProtocol",
    "MahamantraProtocolBase",
    "CoreProtocol",
    # === DECLARATION ===
    "DeclarationType",
    "MahajanaCard",
    "ModuleDeclaration",
    "DeclarationRegistry",
    "DeclarationProtocol",
    "read_declaration",
    # === FRACTAL ===
    "FractalAddress",
    "FractalNode",
    "FractalTree",
    "GrowthPattern",
    "GrowthRule",
    "FractalProtocol",
    # === HOLOGRAPHIC ===
    "Hologram",
    "CoherenceLevel",
    "CoherencePolicy",
    "Reflector",
    "Projector",
    "HolographicSystem",
    "HolographicProtocol",
    "get_holographic_system",
    # === LOTUS ===
    "LOTUS_PETALS",
    "LOTUS_QUARTERS",
    "PETALS_PER_QUARTER",
    "MALA_BEADS",
    "COSMIC_FRAME",
    "NAKSHATRA_UNIT",
    "TITHI_UNIT",
    "PADA_UNIT",
    "QUARTER_UNIT",
    "WORDS",
    "TRINITY",
    "QUARTERS",
    "PANCHA",
    "SHARANAGATI",
    "NAVA",
    "LILA",
    "MALA",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "KSHETRA",
    # "KSHETRA_GAD" removed - was Shaiva, not Gaudiya
    "AVATAR_COUNT",
    "MAHAJANA_POSITIONS",
    "POSITION_MAHAJANAS",
    "get_mahajana_position",
    "get_position_mahajana",
    "LotusMode",
    "LotusPetal",
    "LotusState",
    "LotusRoute",
    "LotusProtocol",
    "LotusBase",
    "LotusTree",
    "LotusHologram",
    "LotusProtocolDef",
    # === GRAPH ===
    "PRAKRITI_COUNT",
    "PURIFICATION_CYCLE",
    "NodeType",
    "EdgeType",
    "Sampradaya",
    "GraphNode",
    "GraphEdge",
    "GraphProtocol",
    "VedicGraph",
    "GraphBuilder",
    "ProtocolGraph",
    "GraphProtocolDef",
    # === BRIDGE ===
    "BridgeType",
    "BridgeDirection",
    "BridgeState",
    "BridgeEndpoint",
    "BridgeSpec",
    "Bridge",
    "BridgeProtocol",
    "BridgeRegistry",
    "get_bridge_registry",
    "BridgeBuilder",
    "BridgeProtocolDef",
    # === STEWARD ===
    "STEWARD_NAME",
    "STEWARD_VERSION",
    "StewardMode",
    "StewardHealth",
    "StewardState",
    "StewardAudit",
    "StewardSystem",
    "StewardProtocol",
    "StewardProtocolDef",
    "get_steward",
    "steward",
    # === GAD ===
    "CRITERIA_COUNT",
    # "KSHETRA_SIZE" removed - was invented 6×6 matrix without Shastra basis
    "KSHETRAJNA",
    "DHARMA_COUNT",
    "MANTRA_CHECKS",
    "GADCriterion",
    "DharmaPrinciple",
    "JapaState",
    "HolyName",
    "MantraHeartbeat",
    "GADAudit",
    "GADProtocol",
    "GADBase",
    "legitimacy_formula",
    "GADProtocolDef",
    # === OPCODE (from substrate/opcode.py SSOT) ===
    "MantraOpCode",
    "OPCODE_NAMES",
    "MAHAJANA_OPCODES",
    "get_opcode",
    "get_opcode_name",
    "get_mahajana_opcode",
    # === VEDA (from protocols/veda.py) ===
    "VedaProtocol",
    "VedaMixin",
    "is_vedic",
    "veda_audit",
    "ShabdaProtocol",
    "ArthaProtocol",
    "PratyayaProtocol",
    "KarmaProtocol",
    # === GOVERNANCE ===
    "ProtocolBridge",
]
