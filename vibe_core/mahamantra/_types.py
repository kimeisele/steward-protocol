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
    """

    seed: int  # Input seed from MahaCompression
    transformed: int  # Output after 16-step transform
    beat: int  # Beat number (1-7)
    resonance: float  # Flute resonance (0.0-1.0)
    attractor: int  # Converged attractor (1 of 5 = PANCHA)
    parampara_channel: int  # Validation channel (0-2 or -1)
    oracle_validated: bool  # Parampara pre-filter passed


class AkashState(TypedDict):
    """
    Akash cache state - THE FIELD (136).

    This is the persistent background vibration.
    Always exists. Always accumulating. The ether.
    """

    resonance_level: float  # Accumulated resonance (grows over time)
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
]
