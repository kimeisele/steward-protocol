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


class ExecuteResult(TypedDict):
    """Return type for execute() - WATERTIGHT."""
    success: bool
    exit_code: int
    position: int
    guardian: str
    quarter: str
    guna: str                       # sattva/rajas/tamas
    requires_confirmation: bool     # True for TAMAS ops
    output: str
    error: Optional[str]


class LilaState(TypedDict):
    """
    Return type for lila() - WATERTIGHT.

    Chaitanya's Lila = 48 positions (24 Navadvipa + 24 Puri).
    This is the COMPLETE lifecycle, not just the 16-word mantra.
    """
    lila_position: int      # 0-47
    position: int           # 0-15 (mantra position)
    phase: str              # "navadvipa" or "puri"
    cycle: int              # 1, 2, or 3
    quarter: str
    guardian: str
    word: str
    opcode: Optional[int]
    is_navadvipa: bool      # True for 0-23
    is_puri: bool           # True for 24-47


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TickState",
    "RouteResult",
    "ExecuteResult",
    "LilaState",
]
