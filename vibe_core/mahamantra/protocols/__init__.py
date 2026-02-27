"""
MAHAMANTRA PROTOCOLS - The Protocols That Define Protocols
==========================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

SIKSASTAKAM OPTIMIZED:
    This module uses LAZY IMPORTS (Effect #1: ceto-darpaṇa-mārjanaṁ).
    Import time: ~10ms instead of ~200ms.

    Use direct imports for best performance:
        from vibe_core.mahamantra.protocols._seed import WORDS
        from vibe_core.mahamantra.protocols._core import Quarter

USAGE:
    from vibe_core.mahamantra.protocols import MahamantraProtocol

    class MyProtocol(MahamantraProtocolBase):
        __protocol_identity__ = ProtocolIdentity(...)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xbe27e031"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# FAST CONSTANTS (from _seed - SSOT)
# =============================================================================
# These are the most commonly used constants - imported eagerly for convenience.

from vibe_core.mahamantra.protocols._seed import (
    AVATAR_COUNT,
    GITA_CHAPTERS,
    HALF_SIZE,
    HALVES,
    HARE_COUNT,
    KRISHNA_COUNT,
    KSETRAJNA,
    KSHETRA,
    LILA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    MALA,
    NAVA,
    PANCHA,
    PARAMPARA,
    QUALITIES,
    QUARTERS,
    RAMA_COUNT,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

# =============================================================================
# LAZY IMPORTS via __getattr__
# =============================================================================
# Everything else is loaded only when accessed.

# TYPE_CHECKING block removed — all 22 re-exports were unused.
# Symbols are discovered at runtime via __getattr__ below.


def __getattr__(name: str):
    """Lazy load protocols only when accessed."""

    # Extended seed constants (from full _seed.py)
    if name in (
        "COSMIC_FRAME",
        "NAKSHATRA_UNIT",
        "TITHI_UNIT",
        "PADA_UNIT",
        "QUARTER_UNIT",
        "JIVA_CYCLE",
        "NADI_RESONANCE",
        "FIELD_RESONANCE",
        "POSITION_SUM_TOTAL",
        "POSITION_SUM_KRISHNA",
        "POSITION_SUM_RAMA",
    ):
        from vibe_core.mahamantra.protocols import _seed

        return getattr(_seed, name)

    # Core protocol types
    if name in (
        "Quarter",
        "Level",
        "ProtocolIdentity",
        "ProtocolCapability",
        "MahamantraProtocol",
        "MahamantraProtocolBase",
        "CoreProtocol",
        "KSETRA_COUNT",
        "KSETRAJNA_COUNT",
    ):
        from vibe_core.mahamantra.protocols import _core

        return getattr(_core, name)

    # Declaration
    if name in (
        "DeclarationType",
        "MahajanaCard",
        "ModuleDeclaration",
        "DeclarationRegistry",
        "DeclarationProtocol",
        "read_declaration",
    ):
        from vibe_core.mahamantra.protocols import _declaration

        return getattr(_declaration, name)

    # Fractal
    if name in (
        "FractalAddress",
        "FractalNode",
        "FractalTree",
        "GrowthPattern",
        "GrowthRule",
        "FractalProtocol",
    ):
        from vibe_core.mahamantra.protocols import _fractal

        return getattr(_fractal, name)

    # Holographic
    if name in (
        "Hologram",
        "CoherenceLevel",
        "CoherencePolicy",
        "Reflection",
        "Projection",
        "HolographicProtocol",
    ):
        from vibe_core.mahamantra.protocols import _holographic

        return getattr(_holographic, name)

    # Header/Cell
    if name in ("MahaCell", "MahaHeader", "NavaBhaktiField"):
        from vibe_core.mahamantra.protocols import _header

        return getattr(_header, name)

    # Payload
    if name in ("PayloadType", "PayloadQuarter", "SiksastakamOp", "MahaPayload"):
        from vibe_core.mahamantra.protocols import _payload

        return getattr(_payload, name)

    # GAD
    if name in ("GADBase", "GADProtocol"):
        from vibe_core.mahamantra.protocols import _gad

        return getattr(_gad, name)

    # MahaCompute
    if name in (
        "MahaComputeProtocol",
        "MahaComputeResult",
        "MahaComputeState",
        "AttractorType",
        "ATTRACTOR_FIXED",
        "ATTRACTOR_CYCLE",
        "ALL_ATTRACTORS",
        "get_gita_chapter",
        "get_gita_insight",
        "PATTERN",
    ):
        from vibe_core.mahamantra.protocols import _maha_compute

        return getattr(_maha_compute, name)

    # Lotus
    if name in ("LotusProtocol", "LotusPetal"):
        from vibe_core.mahamantra.protocols import _lotus

        return getattr(_lotus, name)

    # Shabda Derivation
    if name in (
        "ShabdaSeedProtocol",
        "ShabdaTreeProtocol",
        "ShabdaForestProtocol",
        "ShabdaDerivationProtocol",
        "VibrationProtocol",
        "ROOT_WORDS",
        "POS_HARE",
        "POS_KRISHNA",
        "POS_RAMA",
        "verify_rama_hare_identity",
        "verify_total_mahajana_identity",
    ):
        from vibe_core.mahamantra.protocols import _shabda_derivation

        return getattr(_shabda_derivation, name)

    # Buddhi (Discriminative Intelligence - Mahat-tattva)
    if name in ("BuddhiProtocol", "BuddhiResult", "BuddhiEvaluation"):
        from vibe_core.mahamantra.protocols import _buddhi

        return getattr(_buddhi, name)

    # Veda Protocol (from vibe_core/protocols/veda.py - NOT mahamantra!)
    if name in ("VedaProtocol", "VedaMixin", "is_vedic", "veda_audit"):
        from vibe_core.protocols import veda

        return getattr(veda, name)

    raise AttributeError(f"module 'vibe_core.mahamantra.protocols' has no attribute '{name}'")


# =============================================================================
# EXPORTS (for * import - use sparingly!)
# =============================================================================

__all__ = [
    # Fast constants (from _seed - SSOT)
    "WORDS",
    "TRINITY",
    "QUARTERS",
    "PANCHA",
    "HALVES",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "KSETRAJNA",
    "HALF_SIZE",
    "LILA",
    "KSHETRA",
    "NAVA",
    "SHARANAGATI",
    "SEVEN",
    "TEN",
    "MAHAJANA_COUNT",
    "AVATAR_COUNT",
    "QUALITIES",
    "MALA",
    "MAHA_QUANTUM",
    "GITA_CHAPTERS",
    "PARAMPARA",
    # Everything else via lazy __getattr__
]
