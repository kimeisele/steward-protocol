"""
MAHAMANTRA PROTOCOLS - The Protocols That Define Protocols
==========================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

This module contains the META-PROTOCOLS:
- _core.py: What IS a protocol? (self-referential)
- _declaration.py: How does something declare itself?
- _fractal.py: How does something grow fractally?
- _holographic.py: How does each part contain the whole?

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
]
