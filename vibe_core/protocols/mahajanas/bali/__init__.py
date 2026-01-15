"""
BALI - The 10th Mahajana (Surrender/Yield)
==========================================

POSITION: 13 (MOKSHA Quarter, OPTIMIZE OpCode)

King Bali - The Generous Demon King.
Gave everything to Vamana - even his own position.
"sarva-dharman parityajya mam ekam saranam vraja" (BG 18.66)

DERIVED FROM MAHAMANTRA:
    Position 13 → guardian=BALI, opcode=OPTIMIZE, quarter=MOKSHA
    All properties derived from truth table. No manual wiring.

A system that cannot surrender = INFINITE LOOPS = HIRANYAKASHIPU.
Bali proves that even a demon can be liberated through surrender.

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x0e07c175"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode, ProtocolRegistry


# =============================================================================
# BALI PROTOCOL BASE - Derives from MantraPosition 13
# =============================================================================

@ProtocolRegistry.register
class BaliProtocolBase(WorkerProtocol):
    """
    Bali protocol ownership - DERIVED from Mahamantra position 13.

    NO MANUAL WIRING:
        _position_index = 13 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  → Mahajana.BALI
        opcode()    → MantraOpCode.IO_FLUSH
        quarter()   → Quarter.MOKSHA
        is_head()   → False (Worker position)
        parampara_vector() → 518 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 13  # THE ONLY CONFIGURATION
    _intents: ClassVar[List[str]] = ["yield", "surrender", "release", "optimize", "flush"]


# NO MANUAL WIRING - Everything derived from mahamantra[13]


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


class SurrenderCliResult(TypedDict):
    """Result of CLI surrender operation. WATERTIGHT - no Any!"""
    success: bool
    surrender_type: str
    can_surrender: bool
    health: str


# =============================================================================
# BALI PROTOCOL
# =============================================================================


@runtime_checkable
class BaliProtocol(Protocol):
    """
    The Surrender/Yield Protocol - Bali's domain.

    DERIVED: Position 13 → BALI, OPTIMIZE, MOKSHA
    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 13 in the Mahamantra."""
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


class NullBali(BaliProtocolBase):
    """
    The Hiranyakashipu Pattern.
    Cannot surrender (documents the anti-pattern).

    Inherits from BaliProtocolBase → position 13 → BALI.
    """

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

    def surrender_cli(self, target: str = "yield") -> SurrenderCliResult:
        """CLI: Surrender/yield. WATERTIGHT."""
        result = self.surrender(SurrenderType.YIELD)
        state = self.get_state()
        return SurrenderCliResult(
            success=result.get("success", False),
            surrender_type="yield",
            can_surrender=self.can_surrender(),
            health=state.get("health", "degraded"),
        )


# =============================================================================
# SHUTDOWN - Graceful Shutdown Protocol
# =============================================================================

from vibe_core.protocols.mahajanas.bali.shutdown import (
    ShutdownPhase,
    ShutdownReason,
    ShutdownResult,
    ShutdownHook,
    ShutdownHookEntry,
    ShutdownProtocol,
    ShutdownCoordinator,
    NullShutdown,
    LOTUS_POSITION as SHUTDOWN_POSITION,
)

# =============================================================================
# YIELD_CPU - Cooperative Scheduling Protocol
# =============================================================================

from vibe_core.protocols.mahajanas.bali.yield_cpu import (
    YieldPolicy,
    YieldResult,
    YieldStats,
    YieldProtocol,
    YieldScheduler,
    Hiranyakashipu,  # Anti-pattern
    NullYield,
    LOTUS_POSITION as YIELD_POSITION,
)

# =============================================================================
# MIGRATED TYPES - Accessed via mahamantra.mod.bali
# =============================================================================

from vibe_core.protocols.mahajanas.bali.types import (
    # resource_manager.py
    ResourceManager,
)

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "BaliProtocolBase",
    # Bali Protocol (WATERTIGHT)
    "SurrenderType", "SurrenderResult", "SurrenderState", "SurrenderCliResult",
    "BaliProtocol", "NullBali",
    # Shutdown
    "ShutdownPhase",
    "ShutdownReason",
    "ShutdownResult",
    "ShutdownHook",
    "ShutdownHookEntry",
    "ShutdownProtocol",
    "ShutdownCoordinator",
    "NullShutdown",
    # Yield CPU
    "YieldPolicy",
    "YieldResult",
    "YieldStats",
    "YieldProtocol",
    "YieldScheduler",
    "Hiranyakashipu",
    "NullYield",
    # Service (Real Implementation)
    "BaliService",
    # === MIGRATED TYPES (mahamantra.mod.bali) ===
    # resource_manager.py
    "ResourceManager",
]

# =============================================================================
# BALI SERVICE - The Real Implementation
# =============================================================================

from vibe_core.protocols.mahajanas.bali.service import BaliService
