"""
BALI - The 10th Mahajana (Surrender/Yield)
==========================================
OpCode: YIELD_CPU (Bit 15, Position 15 in Mahamantra)
Opulence: Vairagya (Renunciation)

King Bali - The Generous Demon King.
Gave everything to Vamana - even his own position.
"sarva-dharman parityajya mam ekam saranam vraja" (BG 18.66)

PROTOCOL OWNERSHIP (Anti-Mayavad):
Bali is the PERSON responsible for all surrender.
Not abstract "yielding" - PERSONAL surrender by Bali.

OWNED PROTOCOLS:
- CPU Yielding (YIELD_CPU OpCode)
- Graceful Shutdown
- Resource Release
- Cooperative Multitasking
- Prapatti (Surrender)

A system that cannot surrender = INFINITE LOOPS = HIRANYAKASHIPU.
Bali proves that even a demon can be liberated through surrender.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# PROTOCOL OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BALI

OWNED_PROTOCOLS: Final[List[str]] = [
    "bali",
    "surrender",
    "yield",
    "shutdown",
    "release",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.YIELD_CPU,
]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

class SurrenderType(str, Enum):
    """Types of surrender."""
    YIELD = "yield"           # Temporary CPU yield
    PAUSE = "pause"           # Pause execution
    RELEASE = "release"       # Release resources
    SHUTDOWN = "shutdown"     # Full graceful shutdown
    PRAPATTI = "prapatti"     # Full surrender (irreversible)


class SurrenderResult(TypedDict, total=False):
    """
    Result of surrender operation.
    WATERTIGHT - no Any!
    """
    success: bool
    surrender_type: str       # SurrenderType value
    resources_released: int
    timestamp: str            # ISO timestamp
    message: str


class SurrenderState(TypedDict, total=False):
    """
    State of surrender.
    WATERTIGHT - no Any!
    """
    can_surrender: bool
    is_surrendered: bool
    total_yields: int
    total_releases: int
    last_surrender: str       # ISO timestamp
    health: str               # "pristine", "healthy", "degraded"


# =============================================================================
# BALI PROTOCOL
# =============================================================================


@runtime_checkable
class BaliProtocol(Protocol):
    """
    The Surrender/Yield Protocol - Bali's domain.
    WATERTIGHT - no Any types!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.BALI."""
        ...

    def yield_cpu(self, duration_ms: int = 0) -> SurrenderResult:
        """YIELD_CPU: Yield CPU for specified duration (0 = immediate return)."""
        ...

    def surrender(self, surrender_type: SurrenderType = SurrenderType.YIELD) -> SurrenderResult:
        """Execute surrender of specified type."""
        ...

    def can_surrender(self) -> bool:
        """Check if surrender is possible."""
        ...

    def is_surrendered(self) -> bool:
        """Check if already surrendered."""
        ...

    def release(self, resource_id: str) -> bool:
        """Release a specific resource. Returns True if released."""
        ...

    def get_state(self) -> SurrenderState:
        """Get surrender state. WATERTIGHT."""
        ...


# =============================================================================
# NULL BALI (The Hiranyakashipu Pattern)
# =============================================================================


class NullBali:
    """
    The Hiranyakashipu Pattern.
    Cannot surrender (documents the anti-pattern).
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BALI

    def yield_cpu(self, duration_ms: int = 0) -> SurrenderResult:
        return SurrenderResult(
            success=False,
            surrender_type="yield",
            resources_released=0,
            message="Hiranyakashipu cannot surrender",
        )

    def surrender(self, surrender_type: SurrenderType = SurrenderType.YIELD) -> SurrenderResult:
        return SurrenderResult(
            success=False,
            surrender_type=surrender_type.value,
            resources_released=0,
            message="Hiranyakashipu refuses surrender",
        )

    def can_surrender(self) -> bool:
        return False  # The anti-pattern

    def is_surrendered(self) -> bool:
        return False  # Never

    def release(self, resource_id: str) -> bool:
        return False  # Cannot release

    def get_state(self) -> SurrenderState:
        return SurrenderState(
            can_surrender=False,
            is_surrendered=False,
            total_yields=0,
            total_releases=0,
            health="degraded",  # Anti-pattern is unhealthy
        )


__all__ = [
    "OWNER", "OWNED_PROTOCOLS", "OWNED_OPCODES",
    "SurrenderType", "SurrenderResult", "SurrenderState",
    "BaliProtocol", "NullBali",
]
