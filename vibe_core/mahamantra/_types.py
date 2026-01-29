"""
MAHAMANTRA TYPES - Watertight TypedDicts
========================================

"nānyaṁ guṇebhyaḥ kartāraṁ yadā draṣṭānupaśyati"

"When the seer sees no agent other than the gunas..."
— Bhagavad Gita 14.19

WATERTIGHT: No Any types. All typed explicitly.

EXTRACTED from __init__.py via SANKIRTAN radiation pattern.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x7c5f43fc"  # GenesisByte: parampara % 37 == 0

from typing import Optional, TypedDict

from vibe_core.mahamantra.protocols._header import MahaCell


# =============================================================================
# WATERTIGHT TYPES - No Any allowed
# =============================================================================


class TickState(TypedDict):
    """Return type for tick() - WATERTIGHT."""

    tick: int
    position: int
    quarter: str
    guardian: str
    word: str
    opcode: Optional[int]


class RouteResult(TypedDict):
    """Return type for route() - WATERTIGHT."""

    position: int
    guardian: str
    quarter: str


class VibrationState(TypedDict):
    """
    Vibration state from MahaKirtan compute - THE LICHTPUNKT (+1).

    This is the focused computation result that flows through.
    Every operation vibrates. No silent failures.

    INTEGER RESONANCE (no floats - quantum switchable mod_space):
        resonance (flute): tick % mod_space (WHEN - rhythmic position)
        vina_resonance: seed % mod_space (WHAT TYPE - harmonic position)

    mod_space is switchable (default 137 = MAHA_QUANTUM).
    """

    seed: int  # Input seed from MahaCompression
    transformed: int  # Output after 16-step transform
    beat: int  # Beat number (1-7)
    resonance: int  # Flute resonance = tick % mod_space (integer!)
    vina_resonance: int  # Vina resonance = seed % mod_space (integer!)
    vina_string: int  # Which string (1-5): CHAITANYA/NITYANANDA/ADVAITA/GADADHARA/SRIVASA
    attractor: int  # Converged attractor (1 of 5 = PANCHA)
    parampara_channel: int  # Validation channel (0-2 or -1)
    oracle_validated: bool  # Parampara pre-filter passed


class AkashState(TypedDict):
    """
    Akash cache state - THE FIELD (136).

    This is the persistent background vibration.
    Always exists. Always accumulating. The ether.
    All integers - no floats!
    """

    resonance_level: int  # Accumulated resonance % mod_space (integer!)
    accumulated_value: int  # Sum of all transforms
    total_beats: int  # How many times vibrated
    total_rounds: int  # Complete 7-beat rounds
    attractor_counts: dict  # Distribution: {136: n, 22: n, ...} PANCHA


class ExecuteResult(TypedDict):
    """Return type for execute() - WATERTIGHT with VIBRATION."""

    success: bool
    exit_code: int
    position: int
    guardian: str
    quarter: str
    guna: str  # sattva/rajas/tamas/suddha
    requires_confirmation: bool  # True for TAMAS ops
    output: str
    error: Optional[str]
    # VIBRATION - The compute result flows through!
    vibration: Optional[VibrationState]  # Current computation (+1 Fokus)
    akash: Optional[AkashState]  # Field state (136 Feld)
    # UNIVERSAL CELL - Entry-Existence-Exit
    maha_cell: Optional[MahaCell]  # The carrier of the vibration


class LilaState(TypedDict):
    """
    Return type for lila() - WATERTIGHT.

    Chaitanya's Lila = 48 positions (24 Navadvipa + 24 Puri).
    This is the COMPLETE lifecycle, not just the 16-word mantra.
    """

    lila_position: int  # 0-47
    position: int  # 0-15 (mantra position)
    phase: str  # "navadvipa" or "puri"
    cycle: int  # 1, 2, or 3
    quarter: str
    guardian: str
    word: str
    opcode: Optional[int]
    is_navadvipa: bool  # True for 0-23
    is_puri: bool  # True for 24-47


class GitaRoute(TypedDict):
    """
    Gita routing result - VERSE POINTERS via attractor + SEMANTIC MEANING.

    THE RADIO MODEL: We transmit frequencies (attractor), not text.
    The receiver (user) tunes to the verse via the pointer.

    THE SEMANTIC BRIDGE: Attractor → Meaning (from AxiomSemantics).

    ATTRACTOR → VERSES:
        136 (AKASH)  = 544 verses (dominant field)
        22 (VAYU)    = 43 verses
        18 (AGNI)    = 39 verses
        87 (JALA)    = 38 verses
        49 (PRITHVI) = 36 verses
    """

    attractor: int  # The computed attractor (PANCHA)
    verse_count: int  # How many verses match this attractor
    verse_ids: list  # Matching verse IDs (e.g., ["BG.18.66", "BG.12.8"])
    guna_filter: Optional[str]  # If filtered by guna
    dominant_guna: str  # Most common guna in matched verses

    # SEMANTIC BRIDGE (from AxiomSemantics)
    semantic_name: str  # e.g., "SURRENDER_ALL" for attractor 66
    semantic_theme: str  # e.g., "Surrender All Dharmas"
    semantic_keywords: tuple  # e.g., ("surrender", "all", "dharma")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TickState",
    "RouteResult",
    "VibrationState",
    "AkashState",
    "ExecuteResult",
    "LilaState",
    "GitaRoute",
]
