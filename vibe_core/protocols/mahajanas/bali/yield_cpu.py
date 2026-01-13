"""
YIELD_CPU - Cooperative Scheduling Protocol
===========================================

OWNER: BALI (The Surrendered King)
POSITION: 13 (MOKSHA Quarter)
OPCODE: OPTIMIZE (YIELD_CPU)

Bali gave Vamana TEMPORARY use of land, then PERMANENTLY surrendered.
This mirrors cooperative scheduling: yield temporarily, surrender permanently.

SHASTRA BASIS:
    Bali's surrender was not weakness - it was STRENGTH.
    He could have fought (he was powerful), but chose to yield.

    "sarva-dharman parityajya mam ekam saranam vraja"
    "Abandon all varieties of religion and just surrender unto Me."
    — Bhagavad Gita 18.66

    In code:
    - YIELD = Temporary surrender (give up CPU, get it back)
    - SURRENDER = Permanent surrender (shutdown)

    The opposite is HIRANYAKASHIPU:
    - Infinite loops
    - CPU hogging
    - Resource starvation

SCHEDULING POLICIES:
    - YIELD: Give up CPU for specified duration
    - COOPERATIVE: Yield periodically (every N operations)
    - FAIR: Yield when others are waiting
    - PRIORITY: Yield to higher priority tasks

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x221c69a7"  # GenesisByte: parampara % 37 == 0

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Final, List, Optional, Protocol, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.bali import (
    SurrenderType,
    SurrenderResult,
    SurrenderState,
)


# =============================================================================
# OWNERSHIP DECLARATION - Bali OWNS this protocol
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BALI
LOTUS_POSITION: Final[int] = 13  # MOKSHA Quarter, Worker 1
LOTUS_QUARTER: Final[str] = "moksha"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.IO_FLUSH,  # YIELD_CPU
]


# =============================================================================
# YIELD POLICY
# =============================================================================

class YieldPolicy(str, Enum):
    """Policies for CPU yielding."""
    NEVER = "never"           # Hiranyakashipu mode (anti-pattern)
    EXPLICIT = "explicit"     # Only yield when asked
    COOPERATIVE = "cooperative"  # Yield every N operations
    FAIR = "fair"             # Yield when others waiting
    AGGRESSIVE = "aggressive"  # Yield frequently


# =============================================================================
# YIELD RESULT
# =============================================================================

@dataclass(frozen=True)
class YieldResult:
    """Result of a yield operation."""
    yielded: bool             # Did we actually yield?
    duration_ms: int          # How long we yielded
    policy: YieldPolicy       # Policy that caused yield
    waiting_count: int        # How many were waiting
    message: str

    def to_surrender_result(self) -> SurrenderResult:
        """Convert to SurrenderResult for BaliProtocol compatibility."""
        return SurrenderResult(
            success=self.yielded,
            surrender_type=SurrenderType.YIELD.value,
            resources_released=0,
            timestamp=datetime.now().isoformat(),
            message=self.message,
        )


# =============================================================================
# YIELD STATS
# =============================================================================

@dataclass
class YieldStats:
    """Statistics about yielding behavior."""
    total_yields: int = 0
    total_yield_time_ms: int = 0
    operations_since_yield: int = 0
    last_yield_time: Optional[str] = None
    policy: YieldPolicy = YieldPolicy.COOPERATIVE
    cooperative_interval: int = 100  # Yield every N operations


# =============================================================================
# YIELD PROTOCOL
# =============================================================================

@runtime_checkable
class YieldProtocol(Protocol):
    """
    The Cooperative Scheduling Protocol - Bali's Yield.

    OWNER: Mahajana.BALI

    Like Bali who yielded to Vamana,
    this protocol enables cooperative multitasking:
    - Yield CPU voluntarily
    - Allow other tasks to run
    - Resume when ready

    ANTI-MAYAVAD:
    - No Any types
    - Bali OWNS yielding
    - PERSONAL decision to yield (not forced)
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.BALI."""
        ...

    @property
    def policy(self) -> YieldPolicy:
        """Current yield policy."""
        ...

    # =========================================================================
    # Yield Operations
    # =========================================================================

    def yield_cpu(self, duration_ms: int = 0) -> YieldResult:
        """
        Yield CPU for specified duration.
        duration_ms=0 means yield and return immediately.
        """
        ...

    def maybe_yield(self) -> YieldResult:
        """
        Maybe yield based on policy.
        Call this periodically in long-running operations.
        """
        ...

    def force_yield(self) -> YieldResult:
        """Force an immediate yield regardless of policy."""
        ...

    # =========================================================================
    # Policy Management
    # =========================================================================

    def set_policy(self, policy: YieldPolicy) -> None:
        """Set the yield policy."""
        ...

    def set_cooperative_interval(self, operations: int) -> None:
        """Set interval for cooperative yielding."""
        ...

    # =========================================================================
    # Operation Counting
    # =========================================================================

    def tick(self) -> Optional[YieldResult]:
        """
        Tick the operation counter.
        Returns YieldResult if yield was triggered.
        """
        ...

    def reset_counter(self) -> None:
        """Reset the operation counter."""
        ...

    # =========================================================================
    # Stats
    # =========================================================================

    def get_stats(self) -> YieldStats:
        """Get yield statistics."""
        ...


# =============================================================================
# YIELD SCHEDULER - Implementation
# =============================================================================

class YieldScheduler:
    """
    Bali's Yield Scheduler - Cooperative Multitasking.

    OWNER: Mahajana.BALI

    Enables cooperative scheduling like Bali's yield:
    - Voluntary CPU yielding
    - Policy-based decisions
    - Fair scheduling

    Features:
    - Multiple yield policies
    - Operation counting
    - Statistics tracking
    """

    def __init__(
        self,
        policy: YieldPolicy = YieldPolicy.COOPERATIVE,
        cooperative_interval: int = 100,
    ) -> None:
        """Initialize yield scheduler."""
        self._policy = policy
        self._cooperative_interval = cooperative_interval
        self._operations_since_yield = 0
        self._total_yields = 0
        self._total_yield_time_ms = 0
        self._last_yield_time: Optional[str] = None
        self._waiting_count = 0  # Simulated waiting queue

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BALI

    @property
    def policy(self) -> YieldPolicy:
        return self._policy

    # =========================================================================
    # Yield Operations
    # =========================================================================

    def yield_cpu(self, duration_ms: int = 0) -> YieldResult:
        """Yield CPU for specified duration."""
        if self._policy == YieldPolicy.NEVER:
            return YieldResult(
                yielded=False,
                duration_ms=0,
                policy=self._policy,
                waiting_count=self._waiting_count,
                message="Hiranyakashipu mode - yield refused",
            )

        # Actually yield (sleep)
        if duration_ms > 0:
            time.sleep(duration_ms / 1000.0)

        self._record_yield(duration_ms)

        return YieldResult(
            yielded=True,
            duration_ms=duration_ms,
            policy=self._policy,
            waiting_count=self._waiting_count,
            message=f"Yielded for {duration_ms}ms",
        )

    def maybe_yield(self) -> YieldResult:
        """Maybe yield based on policy."""
        should_yield = False

        if self._policy == YieldPolicy.NEVER:
            should_yield = False
        elif self._policy == YieldPolicy.EXPLICIT:
            should_yield = False  # Only explicit yield_cpu()
        elif self._policy == YieldPolicy.COOPERATIVE:
            should_yield = self._operations_since_yield >= self._cooperative_interval
        elif self._policy == YieldPolicy.FAIR:
            should_yield = self._waiting_count > 0
        elif self._policy == YieldPolicy.AGGRESSIVE:
            should_yield = True

        if should_yield:
            return self.yield_cpu(0)

        return YieldResult(
            yielded=False,
            duration_ms=0,
            policy=self._policy,
            waiting_count=self._waiting_count,
            message="No yield needed",
        )

    def force_yield(self) -> YieldResult:
        """Force an immediate yield regardless of policy."""
        time.sleep(0)  # Minimal yield
        self._record_yield(0)

        return YieldResult(
            yielded=True,
            duration_ms=0,
            policy=self._policy,
            waiting_count=self._waiting_count,
            message="Forced yield",
        )

    def _record_yield(self, duration_ms: int) -> None:
        """Record a yield in statistics."""
        self._total_yields += 1
        self._total_yield_time_ms += duration_ms
        self._operations_since_yield = 0
        self._last_yield_time = datetime.now().isoformat()

    # =========================================================================
    # Policy Management
    # =========================================================================

    def set_policy(self, policy: YieldPolicy) -> None:
        """Set the yield policy."""
        self._policy = policy

    def set_cooperative_interval(self, operations: int) -> None:
        """Set interval for cooperative yielding."""
        self._cooperative_interval = max(1, operations)

    # =========================================================================
    # Operation Counting
    # =========================================================================

    def tick(self) -> Optional[YieldResult]:
        """Tick the operation counter."""
        self._operations_since_yield += 1

        if self._policy == YieldPolicy.COOPERATIVE:
            if self._operations_since_yield >= self._cooperative_interval:
                return self.yield_cpu(0)

        return None

    def reset_counter(self) -> None:
        """Reset the operation counter."""
        self._operations_since_yield = 0

    # =========================================================================
    # Waiting Queue (Simulation)
    # =========================================================================

    def add_waiter(self) -> None:
        """Simulate adding a waiter."""
        self._waiting_count += 1

    def remove_waiter(self) -> None:
        """Simulate removing a waiter."""
        self._waiting_count = max(0, self._waiting_count - 1)

    # =========================================================================
    # Stats
    # =========================================================================

    def get_stats(self) -> YieldStats:
        """Get yield statistics."""
        return YieldStats(
            total_yields=self._total_yields,
            total_yield_time_ms=self._total_yield_time_ms,
            operations_since_yield=self._operations_since_yield,
            last_yield_time=self._last_yield_time,
            policy=self._policy,
            cooperative_interval=self._cooperative_interval,
        )

    def get_state(self) -> SurrenderState:
        """Get state for BaliProtocol compatibility."""
        return SurrenderState(
            can_surrender=self._policy != YieldPolicy.NEVER,
            is_surrendered=False,
            total_yields=self._total_yields,
            total_releases=0,
            last_surrender=self._last_yield_time or "",
            health="healthy" if self._policy != YieldPolicy.NEVER else "degraded",
        )


# =============================================================================
# HIRANYAKASHIPU - Anti-Pattern Implementation
# =============================================================================

class Hiranyakashipu:
    """
    The Hiranyakashipu Pattern - REFUSES to yield.

    Documents the ANTI-PATTERN:
    - Never yields CPU
    - Causes starvation
    - Infinite loops possible

    Named after Prahlada's father who refused to
    acknowledge Vishnu and was killed by Nrisimha.
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BALI  # Still owned by Bali (as anti-pattern)

    @property
    def policy(self) -> YieldPolicy:
        return YieldPolicy.NEVER

    def yield_cpu(self, duration_ms: int = 0) -> YieldResult:
        return YieldResult(
            yielded=False,
            duration_ms=0,
            policy=YieldPolicy.NEVER,
            waiting_count=0,
            message="Hiranyakashipu REFUSES to yield!",
        )

    def maybe_yield(self) -> YieldResult:
        return self.yield_cpu(0)

    def force_yield(self) -> YieldResult:
        # Even force doesn't work on Hiranyakashipu
        return YieldResult(
            yielded=False,
            duration_ms=0,
            policy=YieldPolicy.NEVER,
            waiting_count=0,
            message="Hiranyakashipu cannot be forced to yield!",
        )

    def set_policy(self, policy: YieldPolicy) -> None:
        pass  # Ignored

    def set_cooperative_interval(self, operations: int) -> None:
        pass  # Ignored

    def tick(self) -> Optional[YieldResult]:
        return None

    def reset_counter(self) -> None:
        pass

    def get_stats(self) -> YieldStats:
        return YieldStats(
            total_yields=0,
            total_yield_time_ms=0,
            operations_since_yield=0,
            policy=YieldPolicy.NEVER,
        )

    def get_state(self) -> SurrenderState:
        return SurrenderState(
            can_surrender=False,  # ANTI-PATTERN
            is_surrendered=False,
            total_yields=0,
            total_releases=0,
            health="degraded",  # Unhealthy pattern
        )


# =============================================================================
# NULL YIELD - For testing
# =============================================================================

class NullYield:
    """
    Null Yield - instant yields (for testing).
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BALI

    @property
    def policy(self) -> YieldPolicy:
        return YieldPolicy.COOPERATIVE

    def yield_cpu(self, duration_ms: int = 0) -> YieldResult:
        return YieldResult(yielded=True, duration_ms=0, policy=YieldPolicy.COOPERATIVE, waiting_count=0, message="NullYield")

    def maybe_yield(self) -> YieldResult:
        return self.yield_cpu(0)

    def force_yield(self) -> YieldResult:
        return self.yield_cpu(0)

    def set_policy(self, policy: YieldPolicy) -> None:
        pass

    def set_cooperative_interval(self, operations: int) -> None:
        pass

    def tick(self) -> Optional[YieldResult]:
        return None

    def reset_counter(self) -> None:
        pass

    def get_stats(self) -> YieldStats:
        return YieldStats(policy=YieldPolicy.COOPERATIVE)

    def get_state(self) -> SurrenderState:
        return SurrenderState(can_surrender=True, is_surrendered=False, total_yields=0, total_releases=0, health="pristine")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    # Enums
    "YieldPolicy",
    # Types
    "YieldResult",
    "YieldStats",
    # Protocol
    "YieldProtocol",
    # Implementations
    "YieldScheduler",
    "Hiranyakashipu",  # Anti-pattern
    "NullYield",
]
