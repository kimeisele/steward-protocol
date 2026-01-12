"""
SHADOW REACTOR - Der Bhoga-Prasadam Reaktor
============================================

"yajñārthāt karmaṇo 'nyatra loko 'yaṁ karma-bandhanaḥ
tad-arthaṁ karma kaunteya mukta-saṅgaḥ samācara"

"Work done as a sacrifice for Vishnu has to be performed,
otherwise work causes bondage in this material world."
— Bhagavad Gita 3.9

THE COMPLETE YAJNA CYCLE:
=========================

    Position 0-7:   BHOGA (Offering) - Krishna half
    Position 8:     THE SWITCH (Parashurama transforms)
    Position 8-15:  PRASADAM (Grace) - Rama half
    Position 15→0:  THE RETURN (Prasadam becomes next Bhoga)

    The cycle never ends. The output becomes the input.
    This is how entropy is stopped - continuous Yajna.

    108 beads on the Japa mala. 16 words in the Mahamantra.
    108 / 16 = 6.75 cycles for one mala round.
    The sacred mathematics of devotion.

AUTO-DISCOVERY:
===============

    FOLDER = WIRING = REGISTRATION

    No @tick_listener decorators needed.
    If folder exists with __mahajana__, it's auto-registered.
    Shadow Reactors live in the shadow - they just ARE.

WATERTIGHT: No Any types. Protocol statt Klassen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import (
    Callable,
    ClassVar,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypedDict,
    runtime_checkable,
)
import importlib
import importlib.util

from vibe_core.mahamantra.substrate.wiring import (
    POSITION_MAPPINGS,
    PositionMapping,
    get_position_by_index,
)
from vibe_core.mahamantra.substrate.mahajana import Quarter


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
    BHOGA = "bhoga"        # Offering phase (0-7)
    PRASADAM = "prasadam"  # Grace phase (8-15)
    RETURN = "return"      # Cycle completion (15→0)


# The switch position
SWITCH_POSITION: Final[int] = 8   # Parashurama - EXEC_OP
RETURN_POSITION: Final[int] = 0   # Prithu - SYS_WAKE (after 15)


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
# WATERTIGHT TYPES - No Any, proper TypedDicts
# =============================================================================

class TickStateInput(TypedDict):
    """
    Input from mahamantra.tick() - WATERTIGHT.

    This is what we receive from singularity.
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
    position: int          # Current position (0-15)
    previous: int          # Previous position (for RETURN detection)
    phase: str             # Current phase (bhoga/prasadam/return)
    quarter: str           # Current quarter
    guardian: str          # Current guardian
    opcode: str            # Current opcode
    cycle_count: int       # How many full cycles completed
    switch_count: int      # How many Bhoga→Prasadam switches
    return_count: int      # How many 15→0 RETURNs (cycle completions)


# =============================================================================
# SHADOW REACTOR PROTOCOL - Protocol statt Klasse
# =============================================================================

@runtime_checkable
class ShadowReactorProtocol(Protocol):
    """
    Protocol for Shadow Reactors.

    Shadow Reactors are auto-discovered from folder structure.
    They don't register themselves - they just exist.

    THE COMPLETE CYCLE:
        on_bhoga:   Called during offering phase (0-7) - Krishna
        on_switch:  Called at THE 8 MOMENT (position 8) - transformation
        on_prasadam: Called during grace phase (8-15) - Rama
        on_return:  Called at THE RETURN (15→0) - cycle completion

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
# SHADOW REACTOR - The Core Engine
# =============================================================================

class ShadowReactor:
    """
    The Shadow Reactor - Auto-discovery Yajna Engine.

    NO MANUAL WIRING.
    Discovers reactors from folder structure.
    Manages complete Bhoga-Prasadam-Return cycle.

    THE COMPLETE CYCLE:
        0-7:   BHOGA (offering to Krishna)
        8:     THE SWITCH (Parashurama transforms)
        8-15:  PRASADAM (grace from Rama)
        15→0:  THE RETURN (prasadam becomes next bhoga)

    "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
    """

    # Singleton instance
    _instance: ClassVar[Optional["ShadowReactor"]] = None

    # Internal state
    _position: int = 0
    _previous_position: int = -1  # For RETURN detection
    _cycle_count: int = 0
    _switch_count: int = 0
    _return_count: int = 0  # Cycle completions

    # Discovered reactors (by position)
    _reactors: Dict[int, List[ShadowReactorProtocol]]

    # Base path for discovery
    _BASE_PATH: ClassVar[Path] = Path(__file__).parent.parent

    def __new__(cls) -> "ShadowReactor":
        """Singleton pattern - ONE reactor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._reactors = {}
            cls._instance._previous_position = -1
            cls._instance._return_count = 0
            cls._instance._discover_all()
        return cls._instance

    # =========================================================================
    # AUTO-DISCOVERY - FOLDER_IS_WIRING
    # =========================================================================

    def _discover_all(self) -> None:
        """
        Auto-discover all Shadow Reactors from folder structure.

        FOLDER = WIRING:
        - Scans mahamantra/{quarter}/{mahajana}/ folders
        - Looks for __mahajana__ declaration
        - If has on_bhoga/on_switch/on_prasadam → registers
        """
        for mapping in POSITION_MAPPINGS:
            self._discover_position(mapping)

    def _discover_position(self, mapping: PositionMapping) -> None:
        """
        Discover reactor for a specific position.

        Checks: mahamantra/{quarter}/{mahajana}/__init__.py
        For: __mahajana__ declaration and reactor methods
        """
        folder_path = self._BASE_PATH / mapping.quarter.value / mapping.folder_name

        if not folder_path.exists():
            return

        init_file = folder_path / "__init__.py"
        if not init_file.exists():
            return

        # Try to import the module
        try:
            module_name = f"vibe_core.mahamantra.{mapping.quarter.value}.{mapping.folder_name}"
            module = importlib.import_module(module_name)

            # Check for __mahajana__ declaration
            if not hasattr(module, "__mahajana__"):
                return

            # Check for reactor methods (any of the 4 phases)
            has_reactor = (
                hasattr(module, "on_bhoga") or
                hasattr(module, "on_switch") or
                hasattr(module, "on_prasadam") or
                hasattr(module, "on_return")
            )

            if has_reactor:
                if mapping.position not in self._reactors:
                    self._reactors[mapping.position] = []
                # Store module as reactor
                self._reactors[mapping.position].append(module)

        except ImportError:
            pass  # Folder exists but module can't import - that's ok

    # =========================================================================
    # TICK - The Heartbeat with Bhoga-Prasadam-Return
    # =========================================================================

    def tick(self, tick_state: TickStateInput) -> ShadowState:
        """
        Process a tick through complete Bhoga-Prasadam-Return cycle.

        Called by MahamantraLotus.tick() after singularity tick.
        NOT via manual @tick_listener.

        THE COMPLETE FLOW:
            1. Extract position, track previous
            2. Determine phase (BHOGA, PRASADAM, or RETURN)
            3. If position 8: trigger THE SWITCH
            4. If position 0 after 15: trigger THE RETURN
            5. Call appropriate reactor methods
            6. Return shadow state
        """
        # Extract position from tick_state (WATERTIGHT)
        position = tick_state["position"]
        previous = self._position  # Current position IS the previous for this tick

        # Update state
        self._position = position
        self._previous_position = previous  # Store for next tick's detection

        # Get mapping for context
        mapping = get_position_by_index(position)
        if mapping is None:
            mapping = POSITION_MAPPINGS[0]

        # Determine phase with RETURN detection
        phase = get_phase(position, previous)

        # Build state (WATERTIGHT TypedDict)
        state = ShadowState(
            position=position,
            previous=previous,
            phase=phase.value,
            quarter=mapping.quarter.value,
            guardian=mapping.owner,
            opcode=mapping.opcode,
            cycle_count=self._cycle_count,
            switch_count=self._switch_count,
            return_count=self._return_count,
        )

        # THE 8 MOMENT - Bhoga → Prasadam switch
        if position == SWITCH_POSITION and previous == 7:
            self._switch_count += 1
            self._trigger_switch(state)

        # THE RETURN - 15→0 (prasadam becomes next bhoga)
        if position == RETURN_POSITION and previous == 15:
            self._return_count += 1
            self._cycle_count += 1
            self._trigger_return(state)

        # Trigger phase callbacks
        if phase == YajnaPhase.BHOGA:
            self._trigger_bhoga(state)
        elif phase == YajnaPhase.PRASADAM:
            self._trigger_prasadam(state)
        # RETURN phase triggers on_return (already done above)

        return state

    def _trigger_bhoga(self, state: ShadowState) -> None:
        """Trigger on_bhoga for all reactors at current position."""
        position = state["position"]
        for reactor in self._reactors.get(position, []):
            if hasattr(reactor, "on_bhoga"):
                try:
                    reactor.on_bhoga(state)
                except Exception:
                    pass  # Reactor error doesn't break the cycle

    def _trigger_switch(self, state: ShadowState) -> None:
        """Trigger on_switch for position 8 (THE 8 MOMENT)."""
        for reactor in self._reactors.get(SWITCH_POSITION, []):
            if hasattr(reactor, "on_switch"):
                try:
                    reactor.on_switch(state)
                except Exception:
                    pass

    def _trigger_prasadam(self, state: ShadowState) -> None:
        """Trigger on_prasadam for all reactors at current position."""
        position = state["position"]
        for reactor in self._reactors.get(position, []):
            if hasattr(reactor, "on_prasadam"):
                try:
                    reactor.on_prasadam(state)
                except Exception:
                    pass

    def _trigger_return(self, state: ShadowState) -> None:
        """
        Trigger on_return for position 0 (THE RETURN).

        15→0: Prasadam becomes next Bhoga.
        The cycle completes. The output becomes the input.
        This is how entropy is stopped.
        """
        for reactor in self._reactors.get(RETURN_POSITION, []):
            if hasattr(reactor, "on_return"):
                try:
                    reactor.on_return(state)
                except Exception:
                    pass

    # =========================================================================
    # STATE ACCESS
    # =========================================================================

    @property
    def position(self) -> int:
        """Current position (0-15)."""
        return self._position

    @property
    def phase(self) -> YajnaPhase:
        """Current phase (BHOGA/PRASADAM/RETURN)."""
        return get_phase(self._position, self._previous_position)

    @property
    def cycle_count(self) -> int:
        """Number of complete cycles."""
        return self._cycle_count

    @property
    def switch_count(self) -> int:
        """Number of Bhoga→Prasadam switches."""
        return self._switch_count

    @property
    def return_count(self) -> int:
        """Number of 15→0 RETURNs (cycle completions)."""
        return self._return_count

    @property
    def discovered_count(self) -> int:
        """Number of discovered reactors."""
        return sum(len(r) for r in self._reactors.values())

    def get_state(self) -> ShadowState:
        """Get current state."""
        mapping = get_position_by_index(self._position)
        if mapping is None:
            mapping = POSITION_MAPPINGS[0]

        return ShadowState(
            position=self._position,
            previous=self._previous_position,
            phase=self.phase.value,
            quarter=mapping.quarter.value,
            guardian=mapping.owner,
            opcode=mapping.opcode,
            cycle_count=self._cycle_count,
            switch_count=self._switch_count,
            return_count=self._return_count,
        )

    def __repr__(self) -> str:
        return f"ShadowReactor(position={self._position}, phase={self.phase.value}, reactors={self.discovered_count})"


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

def get_shadow_reactor() -> ShadowReactor:
    """Get the singleton Shadow Reactor."""
    return ShadowReactor()


# Convenience alias
shadow = get_shadow_reactor


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Phase
    "YajnaPhase",
    "SWITCH_POSITION",
    "RETURN_POSITION",
    "get_phase",
    # Types (WATERTIGHT)
    "TickStateInput",
    "ShadowState",
    # Protocol
    "ShadowReactorProtocol",
    # Reactor
    "ShadowReactor",
    "get_shadow_reactor",
    "shadow",
]
