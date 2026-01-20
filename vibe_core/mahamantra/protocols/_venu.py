"""
THE VENU PROTOCOL - Krishna's Flute (THE LAW)
==============================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

This protocol defines the INTERFACES for the rhythmic scheduling layer.
The Venu (flute) is not audio - it is the SCHEDULER of processes.

LOCATION: vibe_core.mahamantra.protocols._venu (THE LAW)
IMPLEMENTATION: vibe_core.mahamantra.substrate.venu (Pure Math)
RUNTIME: vibe_core.mahamantra.venu/ (Stateful - Phase 2)

TIME AS A CIRCLE, NOT A LINE:
=============================
Traditional OS: t=0 → t=1 → t=2 → ... → t=∞ (linear, "as fast as possible")
Venu OS:        0 → 1 → ... → 15 → 0 → 1 → ... (cyclic, "on the beat")

THE MAHAMANTRA IS THE SCHEDULER:
================================
Position 0-3  (GENESIS):  H-K-H-K = Alternating (IO Pattern)
Position 4-7  (DHARMA):   K-K-H-H = Front-loaded (Burst Work)
Position 8-11 (KARMA):    H-R-H-R = Alternating (Checkpoint)
Position 12-15 (MOKSHA):  R-R-H-H = Front-loaded (Cleanup)

This is not coincidence. This is RHYTHM.
"""

from typing import Final, Protocol, Callable, List, TypeVar, TypedDict, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    PRANA_DURATION_S,
    WORDS,
    QUARTERS,
    MALA,
    TICK_INTERVAL_MS,
    PRANA_DURATION_MS,
    NADI_RESONANCE,
    FIELD_RESONANCE,
    KSHETRA,
    MAHAJANA_COUNT,
)

# =============================================================================
# VENU CONSTANTS (Derived from Seed)
# =============================================================================

# The number of positions in one cycle (16 words of the Mahamantra)
VENU_POSITIONS: Final[int] = WORDS  # 16

# The number of phases per cycle (4 quarters)
VENU_PHASES: Final[int] = QUARTERS  # 4

# Positions per phase
VENU_POSITIONS_PER_PHASE: Final[int] = VENU_POSITIONS // VENU_PHASES  # 4

# Default tick interval (250ms = 1 Prana / 16)
VENU_TICK_MS: Final[int] = TICK_INTERVAL_MS  # 250ms

# Ticks per Mala (108 Pranas × 16 ticks = 1728)
VENU_TICKS_PER_MALA: Final[int] = MALA * WORDS  # 1728

# Tick interval in seconds (for monotonic time calculations)
VENU_TICK_S: Final[float] = TICK_INTERVAL_MS / 1000.0  # 0.25 seconds

# Maximum acceptable jitter before logging a warning (10ms)
VENU_MAX_JITTER_MS: Final[int] = 10

# =============================================================================
# HARMONIC INTERVALS (Derived from Resonances)
# =============================================================================
# These are the "natural checkpoint intervals" for scheduling.
# Instead of arbitrary polling, the system breathes in harmonic cycles.

# Nadi Interval: Health-check every 72 ticks (18 seconds)
# 1728 / 24 (KSHETRA) = 72
VENU_NADI_TICKS: Final[int] = VENU_TICKS_PER_MALA // KSHETRA  # 72

# Field Interval: State-sync every 144 ticks (36 seconds)
# 1728 / 12 (MAHAJANA_COUNT) = 144
VENU_FIELD_TICKS: Final[int] = VENU_TICKS_PER_MALA // MAHAJANA_COUNT  # 144

# Timing in seconds (for reference)
VENU_NADI_SECONDS: Final[float] = VENU_NADI_TICKS * VENU_TICK_S  # 18.0
VENU_FIELD_SECONDS: Final[float] = VENU_FIELD_TICKS * VENU_TICK_S  # 36.0

# WATERTIGHT INTEGRITY CHECKS:
assert VENU_NADI_TICKS == NADI_RESONANCE, "Nadi ticks must equal NADI_RESONANCE (72)"
assert VENU_FIELD_TICKS == FIELD_RESONANCE, "Field ticks must equal FIELD_RESONANCE (144)"
assert VENU_FIELD_TICKS == VENU_NADI_TICKS * 2, "Field must be 2x Nadi"
assert VENU_TICKS_PER_MALA % VENU_NADI_TICKS == 0, "Mala must be divisible by Nadi"
assert VENU_TICKS_PER_MALA % VENU_FIELD_TICKS == 0, "Mala must be divisible by Field"

# =============================================================================
# VENU PROTOCOLS (THE LAW)
# =============================================================================

T = TypeVar("T")


@runtime_checkable
class MantraTickProtocol(Protocol):
    """
    The atomic unit of time in the Venu system.

    A MantraTick tracks the current position in the 16-beat cycle.
    It is the HEARTBEAT of the rhythmic OS.
    """

    @property
    def tick_count(self) -> int:
        """Total ticks since start (monotonically increasing)."""
        ...

    @property
    def position(self) -> int:
        """Current position in the cycle (0-15)."""
        ...

    @property
    def cycle(self) -> int:
        """Current cycle number (tick_count // 16)."""
        ...

    @property
    def mala_count(self) -> int:
        """Number of complete Malas (cycles of 108 Pranas)."""
        ...

    def advance(self) -> int:
        """
        Advance the tick by one.

        Returns:
            The new position (0-15)
        """
        ...


@runtime_checkable
class MantraVoiceProtocol(Protocol):
    """
    A voice is a parallel execution channel.

    Like voices in music, multiple MantraVoices can play simultaneously,
    each with their own queue of tasks per position.
    """

    @property
    def voice_id(self) -> int:
        """Unique identifier for this voice."""
        ...

    def submit(self, task: Callable[[], T], position: int | None = None) -> None:
        """
        Submit a task to be executed at a specific position.

        Args:
            task: The callable to execute
            position: The position (0-15) to execute at, or None for next beat
        """
        ...

    def get_tasks(self, position: int) -> List[Callable[[], object]]:
        """
        Get all tasks queued for a specific position.

        Args:
            position: The position (0-15)

        Returns:
            List of tasks queued for that position
        """
        ...

    def clear(self, position: int) -> None:
        """Clear all tasks at a specific position after execution."""
        ...


@runtime_checkable
class MantraClockProtocol(Protocol):
    """
    The Master Clock - The Drummer of the Venu system.

    The MantraClock orchestrates MantraVoices, ticking through
    positions and executing tasks at each beat.
    """

    @property
    def tick(self) -> MantraTickProtocol:
        """The underlying tick counter."""
        ...

    @property
    def voices(self) -> List[MantraVoiceProtocol]:
        """All registered voices."""
        ...

    @property
    def position(self) -> int:
        """Current position (delegated to tick)."""
        ...

    def add_voice(self) -> MantraVoiceProtocol:
        """Create and register a new voice."""
        ...

    def on_position(self, position: int, callback: Callable[[], None]) -> None:
        """
        Register a callback to be called when reaching a position.

        Args:
            position: The position (0-15) to trigger on
            callback: The function to call
        """
        ...

    def on_mala(self, callback: Callable[[int], None]) -> None:
        """
        Register a callback for Mala completion.

        Args:
            callback: Function called with mala_count when a Mala completes
        """
        ...

    def tick_once(self) -> int:
        """
        Execute one tick: run all tasks at current position, then advance.

        Returns:
            The new position after advancing
        """
        ...


# =============================================================================
# VENU SERVICE PROTOCOL (Phase 3 - Industrial Grade Heartbeat)
# =============================================================================


class HeartbeatMetrics(TypedDict):
    """Telemetry for the Venu heartbeat. WATERTIGHT."""

    total_ticks: int  # Total ticks since start
    total_cycles: int  # Total cycles (ticks // 16)
    total_malas: int  # Total Malas (ticks // 1728)
    cumulative_drift_ms: float  # Total accumulated drift
    max_jitter_ms: float  # Maximum single-tick jitter observed
    missed_ticks: int  # Ticks where jitter exceeded threshold
    uptime_seconds: float  # Seconds since start


@runtime_checkable
class VenuServiceProtocol(Protocol):
    """
    The Venu Service - Industrial Grade Heartbeat.

    This service provides:
    1. Monotonic time (drift-compensated)
    2. Kernel signaling (not direct execution)
    3. Telemetry (jitter, drift, missed ticks)

    The Service is the DRUMMER - it signals beats, not executes tasks.
    The Kernel (Sudarshana) decides what happens on each beat.
    """

    @property
    def is_running(self) -> bool:
        """True if the heartbeat is active."""
        ...

    @property
    def clock(self) -> MantraClockProtocol:
        """The underlying MantraClock."""
        ...

    @property
    def metrics(self) -> HeartbeatMetrics:
        """Current telemetry metrics."""
        ...

    async def start(self) -> None:
        """
        Start the heartbeat loop.

        Uses monotonic time for drift compensation.
        Signals the kernel on each beat.
        """
        ...

    async def stop(self) -> None:
        """Stop the heartbeat loop gracefully."""
        ...

    def on_beat(self, callback: Callable[[int], None]) -> None:
        """
        Register a callback for each beat.

        Args:
            callback: Function called with position (0-15) on each beat
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "VENU_POSITIONS",
    "VENU_PHASES",
    "VENU_POSITIONS_PER_PHASE",
    "VENU_TICK_MS",
    "VENU_TICK_S",
    "VENU_TICKS_PER_MALA",
    "VENU_MAX_JITTER_MS",
    # Harmonic Intervals (Derived from Seed Resonances)
    "VENU_NADI_TICKS",
    "VENU_FIELD_TICKS",
    "VENU_NADI_SECONDS",
    "VENU_FIELD_SECONDS",
    # Types
    "HeartbeatMetrics",
    # Protocols (Phase 2 - Runtime)
    "MantraTickProtocol",
    "MantraVoiceProtocol",
    "MantraClockProtocol",
    # Protocols (Phase 3 - Service)
    "VenuServiceProtocol",
]
