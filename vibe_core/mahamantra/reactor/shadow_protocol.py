"""
SHADOW REACTOR PROTOCOL - The Yajna Cycle Contract
===================================================

"yajñārthāt karmaṇo 'nyatra loko 'yaṁ karma-bandhanaḥ"
"Work done as a sacrifice for Vishnu has to be performed."
— Bhagavad Gita 3.9

This protocol defines WHAT a ShadowReactor does, not HOW it does it.
All callers MUST depend on this protocol, NOT on ShadowReactor directly.

ARCHITECTURE:
=============

    Substrate (clock.py) = STATELESS map (answers "what WOULD be at tick X?")
    ShadowReactor       = STATEFUL walker (answers "where am I NOW?")

    Just like TaskKernel, ShadowReactor is:
    - Lightweight: Minimal boot time
    - Ephemeral: Can be spawned and discarded
    - Spawnable: Multiple instances can run in parallel (SANKIRTAN!)

THE COMPLETE YAJNA CYCLE:
========================

    Position 0-7:   BHOGA (Offering) - Krishna half
    Position 8:     THE SWITCH (Parashurama transforms)
    Position 8-15:  PRASADAM (Grace) - Rama half
    Position 15→0:  THE RETURN (Prasadam becomes next Bhoga)

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0xd2f4c898"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from typing import (
    Dict,
    Final,
    Optional,
    Protocol,
    TypedDict,
    runtime_checkable,
)

# =============================================================================
# THE 8 MOMENT - Bhoga/Prasadam Phase
# =============================================================================


class YajnaPhase(str, Enum):
    """
    The phases of Yajna (sacrifice).

    BHOGA: Positions 0-7 (Krishna half) - Offering
    PRASADAM: Positions 8-15 (Rama half) - Grace
    RETURN: Position 15→0 - Prasadam becomes next Bhoga
    """

    BHOGA = "bhoga"  # Offering phase (0-7)
    PRASADAM = "prasadam"  # Grace phase (8-15)
    RETURN = "return"  # Cycle completion (15→0)


# Constants
SWITCH_POSITION: Final[int] = 8  # Parashurama - EXEC_OP
RETURN_POSITION: Final[int] = 0  # Prithu - SYS_WAKE (after 15)


def get_phase(position: int, previous_position: int = -1) -> YajnaPhase:
    """
    Get Yajna phase from position.

    Args:
        position: Current position (0-15)
        previous_position: Previous position (-1 if unknown)

    Returns:
        YajnaPhase: BHOGA, PRASADAM, or RETURN
    """
    # THE RETURN: 15→0 transition
    if position == RETURN_POSITION and previous_position == 15:
        return YajnaPhase.RETURN

    # Normal phases
    if position < SWITCH_POSITION:
        return YajnaPhase.BHOGA
    return YajnaPhase.PRASADAM


# =============================================================================
# WATERTIGHT TYPES
# =============================================================================


class TickStateInput(TypedDict):
    """
    Input from mahamantra.tick() - WATERTIGHT.

    This is what we receive from the Lotus.
    """

    tick: int
    position: int
    quarter: str
    guardian: str
    word: str
    opcode: Optional[int]


class ShadowState(TypedDict):
    """
    State of the Shadow Reactor - WATERTIGHT.

    Tracks the full Bhoga-Prasadam-Return cycle.
    """

    position: int  # Current position (0-15)
    previous: int  # Previous position (for RETURN detection)
    phase: str  # Current phase (bhoga/prasadam/return)
    quarter: str  # Current quarter
    guardian: str  # Current guardian
    opcode: str  # Current opcode
    cycle_count: int  # How many full cycles completed
    switch_count: int  # How many Bhoga→Prasadam switches
    return_count: int  # How many 15→0 RETURNs (cycle completions)
    dissonance_report: Optional[str]  # Audit log for silent failures (Aparadha)
    payload: Optional[bytes]  # The intent/content from the MahaCell (WATERTIGHT)
    execution_result: Optional[Dict]  # Result from the listener (Phase 1 Bridge)


@dataclass
class ShadowReactorResult:
    """
    Result of ShadowReactor execution cycle.

    Similar to TaskKernelResult - used for folding results.
    """

    # Identity
    reactor_id: str

    # State
    position: int
    phase: YajnaPhase
    cycle_count: int

    # Metrics
    ticks_processed: int = 0
    bhoga_count: int = 0
    prasadam_count: int = 0
    return_count: int = 0

    # Callbacks triggered
    callbacks_triggered: int = 0
    callbacks_failed: int = 0

    def to_dict(self) -> Dict:
        """Serialize for IPC/logging."""
        return {
            "reactor_id": self.reactor_id,
            "position": self.position,
            "phase": self.phase.value,
            "cycle_count": self.cycle_count,
            "ticks_processed": self.ticks_processed,
            "bhoga_count": self.bhoga_count,
            "prasadam_count": self.prasadam_count,
            "return_count": self.return_count,
            "callbacks_triggered": self.callbacks_triggered,
            "callbacks_failed": self.callbacks_failed,
        }


# =============================================================================
# SHADOW REACTOR LISTENER PROTOCOL
# =============================================================================


@runtime_checkable
class ShadowReactorListenerProtocol(Protocol):
    """
    Protocol for Shadow Reactor listeners.

    Shadow Reactors are auto-discovered from folder structure.
    They don't register themselves - they just exist.

    THE COMPLETE CYCLE:
        on_bhoga:    Called during offering phase (0-7) - Krishna
        on_switch:   Called at THE 8 MOMENT (position 8) - transformation
        on_prasadam: Called during grace phase (8-15) - Rama
        on_return:   Called at THE RETURN (15→0) - cycle completion

    "The output becomes the input. Prasadam becomes next Bhoga."
    """

    def on_bhoga(self, state: ShadowState) -> None:
        """Called during BHOGA phase (positions 0-7) - Krishna half."""
        ...

    def on_switch(self, state: ShadowState) -> None:
        """Called at THE 8 MOMENT (position 8) - Bhoga→Prasadam."""
        ...

    def on_prasadam(self, state: ShadowState) -> None:
        """Called during PRASADAM phase (positions 8-15) - Rama half."""
        ...

    def on_return(self, state: ShadowState) -> None:
        """Called at THE RETURN (15→0) - Prasadam becomes next Bhoga."""
        ...


# =============================================================================
# SHADOW REACTOR PROTOCOL - The Contract
# =============================================================================


@runtime_checkable
class ShadowReactorProtocol(Protocol):
    """
    The Yajna Cycle Contract.

    This protocol defines what every ShadowReactor MUST provide.

    CHARACTERISTICS (like TaskKernel):
        - Lightweight: Minimal state
        - Spawnable: Multiple instances can run in parallel
        - Stateful: Tracks position, cycle, phase
        - Auto-discovery: Finds listeners from folder structure

    SANKIRTAN PATTERN:
        Unlike Ashvamedha (single central reactor), Sankirtan
        allows multiple reactors to run simultaneously.
        Each reactor can walk its own path through the mantra.
    """

    # =========================================================================
    # IDENTITY
    # =========================================================================

    @property
    def reactor_id(self) -> str:
        """Unique identifier for this reactor instance."""
        ...

    # =========================================================================
    # STATE (Read-Only)
    # =========================================================================

    @property
    def position(self) -> int:
        """Current position (0-15)."""
        ...

    @property
    def phase(self) -> YajnaPhase:
        """Current phase (BHOGA/PRASADAM/RETURN)."""
        ...

    @property
    def cycle_count(self) -> int:
        """Number of complete cycles."""
        ...

    @property
    def switch_count(self) -> int:
        """Number of Bhoga→Prasadam switches."""
        ...

    @property
    def return_count(self) -> int:
        """Number of 15→0 RETURNs (cycle completions)."""
        ...

    # =========================================================================
    # TICK - The Heartbeat
    # =========================================================================

    def tick(self, tick_state: TickStateInput) -> ShadowState:
        """
        Process a tick through complete Bhoga-Prasadam-Return cycle.

        Args:
            tick_state: Input from mahamantra.tick()

        Returns:
            ShadowState with current position and cycle info
        """
        ...

    def get_state(self) -> ShadowState:
        """Get current state without advancing."""
        ...

    # =========================================================================
    # LISTENER MANAGEMENT
    # =========================================================================

    def register_listener(
        self,
        position: int,
        listener: ShadowReactorListenerProtocol,
    ) -> None:
        """
        Register a listener at a specific position.

        Args:
            position: Position (0-15) to listen on
            listener: Object implementing ShadowReactorListenerProtocol
        """
        ...

    def unregister_listener(
        self,
        position: int,
        listener: ShadowReactorListenerProtocol,
    ) -> None:
        """Unregister a listener from a position."""
        ...

    @property
    def discovered_count(self) -> int:
        """Number of discovered/registered listeners."""
        ...


# =============================================================================
# SHADOW REACTOR FACTORY PROTOCOL
# =============================================================================


@runtime_checkable
class ShadowReactorFactoryProtocol(Protocol):
    """
    Factory for creating ShadowReactor instances.

    Enables SANKIRTAN pattern - multiple reactors running in parallel.
    Each reactor walks its own path through the mantra.

    Usage:
        # In service (CORRECT):
        factory = get_shadow_reactor_factory()
        reactor = factory.spawn()

        # NOT this (WRONG - creates hard dependency):
        from vibe_core.mahamantra.reactor.shadow import ShadowReactor
        reactor = ShadowReactor()
    """

    def spawn(
        self,
        auto_discover: bool = True,
        initial_position: int = 0,
    ) -> ShadowReactorProtocol:
        """
        Spawn a new ShadowReactor instance.

        SANKIRTAN: Each call creates a NEW reactor.
        No singleton. Multiple reactors can exist.

        Args:
            auto_discover: If True, discover listeners from folders
            initial_position: Starting position (0-15)

        Returns:
            New ShadowReactor instance
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

# =============================================================================
# MAHA ORACLE PROTOCOL - The Gita 13.35 Pre-Filter Contract
# =============================================================================
# "kṣetra-kṣetrajñayor evam antaraṁ jñāna-cakṣuṣā
# bhūta-prakṛti-mokṣaṁ ca ye vidur yānti te param"
#
# "Those who see with eyes of knowledge the difference between the field
# and the knower of the field, and can also understand the process of
# liberation from bondage in material nature, attain the supreme goal."
# — Bhagavad Gita 13.35
#
# WITHOUT AUTHENTIC GURU (PARAMPARA), TRUE KNOWLEDGE IS NOT POSSIBLE.
# Therefore: PARAMPARA (mod 37) is the MANDATORY FIRST LENS.
# =============================================================================


class OracleValidationResult(TypedDict):
    """
    Result of Oracle validation (WATERTIGHT).

    Returned by MahaOracleProtocol.validate() BEFORE any computation.
    """

    parampara_validated: bool  # True if in valid disciplic channel (Gita 13.35)
    parampara_channel: int  # Which of TRINITY (3) channels (-1 if void)
    parampara_attractor: int  # The attractor value at mod 37
    coherence: int  # Integer coherence (scaled by COSMIC_FRAME)
    prabhupada_year: Optional[int]  # Resonant year in Lila (1896-1977) or None


@runtime_checkable
class MahaOracleProtocol(Protocol):
    """
    The Gita 13.35 Pre-Filter Contract.

    This protocol defines WHAT the Oracle does for ShadowReactor integration:
    - VALIDATES Parampara BEFORE computation (MANDATORY)
    - CONSULTS lenses to analyze intent/seed
    - BACKFOLDS results to PRASADAM phase

    RAM-EFFICIENT: Stateless, protocol-based, no heavy objects.
    The Oracle doesn't store - it VALIDATES and RETURNS.

    "Without authentic Guru, true knowledge is not possible."
    — Gita 13.35 Principle

    INTEGRATION POINTS:
        1. BHOGA (Pre-Compute): validate() → Parampara check
        2. COMPUTE: consult_seed() → Full lens analysis (if validated)
        3. PRASADAM (Post-Compute): backfold() → Fold results to state
    """

    def validate(self, seed: int) -> OracleValidationResult:
        """
        MANDATORY PRE-FILTER: Validate Parampara connection.

        This MUST be called BEFORE any computation in the Reactor.
        If not validated, computation proceeds with WARNING flag.

        Args:
            seed: The intent/data encoded as integer

        Returns:
            OracleValidationResult with parampara status
        """
        ...

    def validate_fast(self, seed: int) -> bool:
        """
        FAST VALIDATION: Returns only the boolean.

        For hot paths where full result is not needed.
        Equivalent to: validate(seed)["parampara_validated"]
        """
        ...

    def consult_seed(self, seed: int) -> Dict:
        """
        Full Oracle consultation with all lenses.

        Only call this if Parampara is validated (or you need full analysis).
        Returns dict with all lens readings.
        """
        ...

    def backfold(self, validation: OracleValidationResult, state: ShadowState) -> ShadowState:
        """
        Backfold Oracle result into ShadowState.

        Called during PRASADAM phase to merge Oracle insight with state.
        Does NOT mutate input - returns new state.

        Args:
            validation: Result from validate()
            state: Current ShadowState

        Returns:
            New ShadowState with Oracle data folded in
        """
        ...


# =============================================================================
# PARAMPARA CHANNELS - IMPORTED FROM SSOT (_seed.py)
# =============================================================================
# The channels are MATHEMATICALLY DERIVED (mod 37 attractors), not hardcoded!
# See _seed.py RUNDE 28b for the complete derivation.
#
# TRINITY (3) attractors, not PANCHA (5) as previously hardcoded:
#   12 = MAHAJANA_COUNT (the 12 authorities)
#   26 = 2 × 13 = Chapter 13 doubled (transmission)
#   34 = PARAMPARA - TRINITY = GURU_VERSE (stability)
# -----------------------------------------------------------------------------
from vibe_core.mahamantra.protocols._seed import (
    PARAMPARA_CHANNEL_NAMES,
    PARAMPARA_CHANNELS,
)

__all__ = [
    # Phase
    "YajnaPhase",
    "SWITCH_POSITION",
    "RETURN_POSITION",
    "get_phase",
    # Types (WATERTIGHT)
    "TickStateInput",
    "ShadowState",
    "ShadowReactorResult",
    # Protocols
    "ShadowReactorListenerProtocol",
    "ShadowReactorProtocol",
    "ShadowReactorFactoryProtocol",
    # Oracle Protocol (Gita 13.35)
    "OracleValidationResult",
    "MahaOracleProtocol",
    "PARAMPARA_CHANNELS",
    "PARAMPARA_CHANNEL_NAMES",
]
