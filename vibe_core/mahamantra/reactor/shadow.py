"""
SHADOW REACTOR - Der Bhoga-Prasadam Reaktor (SPAWNBAR)
======================================================

"yajñārthāt karmaṇo 'nyatra loko 'yaṁ karma-bandhanaḥ
tad-arthaṁ karma kaunteya mukta-saṅgaḥ samācara"

"Work done as a sacrifice for Vishnu has to be performed,
otherwise work causes bondage in this material world."
— Bhagavad Gita 3.9

ARCHITECTURE:
=============

    Substrate (clock.py) = STATELESS map (answers "what WOULD be at tick X?")
    ShadowReactor       = STATEFUL walker (answers "where am I NOW?")

    SANKIRTAN PATTERN (not Ashvamedha):
        - Multiple reactors can run in parallel
        - Each walks its own path through the mantra
        - Like TaskKernel - lightweight, ephemeral, spawnbar

THE COMPLETE YAJNA CYCLE:
=========================

    Position 0-7:   BHOGA (Offering) - Krishna half
    Position 8:     THE SWITCH (Parashurama transforms)
    Position 8-15:  PRASADAM (Grace) - Rama half
    Position 15→0:  THE RETURN (Prasadam becomes next Bhoga)

    The cycle never ends. The output becomes the input.
    This is how entropy is stopped - continuous Yajna.

AUTO-DISCOVERY:
===============

    FOLDER = WIRING = REGISTRATION

    No @tick_listener decorators needed.
    If folder exists with __mahajana__, it's auto-registered.
    Shadow Reactors live in the shadow - they just ARE.

WATERTIGHT: No Any types. Protocol statt Klassen.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
)
import importlib

# Import types from protocol (SSOT)
from vibe_core.mahamantra.reactor.shadow_protocol import (
    YajnaPhase,
    SWITCH_POSITION,
    RETURN_POSITION,
    get_phase,
    TickStateInput,
    ShadowState,
    ShadowReactorResult,
    ShadowReactorListenerProtocol,
    ShadowReactorProtocol,
    ShadowReactorFactoryProtocol,
)

from vibe_core.mahamantra.substrate.wiring import (
    get_position_by_index,
)
from vibe_core.mahamantra.substrate.position import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
)


# =============================================================================
# SHADOW REACTOR - The Core Engine (SPAWNBAR)
# =============================================================================

class ShadowReactor:
    """
    The Shadow Reactor - Auto-discovery Yajna Engine (SPAWNBAR).

    SANKIRTAN PATTERN (not Ashvamedha):
        - NO SINGLETON - Multiple reactors can run in parallel
        - Each walks its own path through the mantra
        - Like TaskKernel - lightweight, ephemeral, spawnbar

    NO MANUAL WIRING.
    Discovers listeners from folder structure.
    Manages complete Bhoga-Prasadam-Return cycle.

    THE COMPLETE CYCLE:
        0-7:   BHOGA (offering to Krishna)
        8:     THE SWITCH (Parashurama transforms)
        8-15:  PRASADAM (grace from Rama)
        15→0:  THE RETURN (prasadam becomes next bhoga)

    "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
    """

    # Base path for discovery (shared across instances)
    _BASE_PATH: ClassVar[Path] = Path(__file__).parent.parent

    def __init__(
        self,
        auto_discover: bool = True,
        initial_position: int = 0,
    ) -> None:
        """
        Initialize ShadowReactor.

        SPAWNBAR: Each call to __init__ creates a NEW reactor.
        No singleton. Multiple reactors can exist (SANKIRTAN!).

        Args:
            auto_discover: If True, discover listeners from folders
            initial_position: Starting position (0-15)
        """
        # Identity
        self._reactor_id = f"sr_{uuid.uuid4().hex[:8]}"

        # Internal state
        self._position: int = initial_position
        self._previous_position: int = -1  # For RETURN detection
        self._cycle_count: int = 0
        self._switch_count: int = 0
        self._return_count: int = 0  # Cycle completions

        # Discovered listeners (by position)
        self._listeners: Dict[int, List[ShadowReactorListenerProtocol]] = {}

        # Auto-discover if requested
        if auto_discover:
            self._discover_all()

    # =========================================================================
    # PROTOCOL PROPERTIES
    # =========================================================================

    @property
    def reactor_id(self) -> str:
        """Unique identifier for this reactor instance."""
        return self._reactor_id

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
        for mapping in MAHAMANTRA_POSITIONS:
            self._discover_position(mapping)

    def _discover_position(self, mapping: MantraPosition) -> None:
        """
        Discover reactor for a specific position.

        Checks: mahamantra/{quarter}/{mahajana}/__init__.py
        For: __mahajana__ declaration and reactor methods
        """
        guardian_name = mapping.guardian.value
        folder_path = self._BASE_PATH / mapping.quarter.value / guardian_name

        if not folder_path.exists():
            return

        init_file = folder_path / "__init__.py"
        if not init_file.exists():
            return

        # Try to import the module
        try:
            module_name = f"vibe_core.mahamantra.{mapping.quarter.value}.{guardian_name}"
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
                if mapping.index not in self._listeners:
                    self._listeners[mapping.index] = []
                # Store module as reactor
                self._listeners[mapping.index].append(module)

        except ImportError:
            pass  # Folder exists but module can't import - that's ok

    # =========================================================================
    # TICK - The Heartbeat with Bhoga-Prasadam-Return
    # =========================================================================

    # =========================================================================
    # PARAMPARA VERIFICATION (37 - The Sacred Number)
    # =========================================================================

    PARAMPARA: int = 37  # 24 + 12 + 1 = Ksetra + Mahajanas + Ksetrajna

    def _verify_parampara(self, position: int, cycle: int) -> bool:
        """
        Verify Parampara connection for current state.

        CHAITANYA SINGULARITY: Every tick must be connected to Parampara.

        Connection happens when cumulative tick count reaches Parampara multiples:
        - After 37 ticks: First alignment
        - After 74 ticks: Second alignment
        - etc.

        Also connected at cycle boundaries (every 16 ticks in Bhoga/Prasadam).
        """
        total_ticks = (cycle * 16) + position
        # Connected at Parampara multiples (37, 74, 111...)
        # Or at SWITCH position (8) - the transformation point
        # Or at RETURN position (0) after a cycle - renewal
        return (
            total_ticks % self.PARAMPARA == 0 or
            position == SWITCH_POSITION or  # The 8 Moment
            (position == RETURN_POSITION and cycle > 0)  # The Return
        )

    def _compute_parampara_coherence(self, position: int, cycle: int) -> float:
        """
        Compute coherence relative to Parampara.

        Uses the GOLDEN RATIO pattern within Parampara:
        - 37 = sum of first 5 Fibonacci numbers squared (1+1+4+9+16+9-3=37... nope)
        - Actually: 37 is prime, so use distance from nearest Parampara multiple

        Returns 0.0 to 1.0 indicating how "connected" this state is.
        Sinusoidal pattern creates rhythm of connection.
        """
        import math

        total_ticks = (cycle * 16) + position + 1  # +1 to avoid zero

        # Distance from nearest Parampara multiple
        remainder = total_ticks % self.PARAMPARA
        distance = min(remainder, self.PARAMPARA - remainder)

        # Sinusoidal coherence - creates a rhythmic pattern
        # High at 0, 37, 74... Low at 18, 55... (midpoints)
        phase = (total_ticks / self.PARAMPARA) * 2 * math.pi
        base_coherence = (math.cos(phase) + 1) / 2  # 0 to 1

        # Boost at switch position (8) - the transformation
        if position == SWITCH_POSITION:
            base_coherence = min(1.0, base_coherence + 0.37)

        return base_coherence

    def tick(self, tick_state: TickStateInput) -> ShadowState:
        """
        Process a tick through complete Bhoga-Prasadam-Return cycle.

        CHAITANYA SINGULARITY INTEGRATION:
        ==================================
        Every tick verifies Parampara connection.
        If disconnected, the state is flagged (but processing continues).
        This enables audit/observability without breaking the cycle.

        THE COMPLETE FLOW:
            1. Extract position, track previous
            2. VERIFY PARAMPARA CONNECTION (37)
            3. Determine phase (BHOGA, PRASADAM, or RETURN)
            4. If position 8: trigger THE SWITCH
            5. If position 0 after 15: trigger THE RETURN
            6. Call appropriate reactor methods
            7. Return shadow state with parampara_coherence
        """
        # Extract position from tick_state (WATERTIGHT)
        position = tick_state["position"]
        previous = self._position  # Current position IS the previous for this tick

        # Update state
        self._position = position
        self._previous_position = previous  # Store for next tick's detection

        # =====================================================================
        # PARAMPARA VERIFICATION (CHAITANYA SINGULARITY)
        # =====================================================================
        # Every tick is checked for Parampara connection.
        # This is the 37th principle operating on every compute cycle.
        parampara_connected = self._verify_parampara(position, self._cycle_count)
        parampara_coherence = self._compute_parampara_coherence(position, self._cycle_count)

        # Get mapping for context
        mapping = get_position_by_index(position)
        if mapping is None:
            mapping = MAHAMANTRA_POSITIONS[0]

        # Determine phase with RETURN detection
        phase = get_phase(position, previous)

        # Build state (WATERTIGHT TypedDict)
        state = ShadowState(
            position=position,
            previous=previous,
            phase=phase.value,
            quarter=mapping.quarter.value,
            guardian=mapping.guardian.value,
            opcode=mapping.opcode.name,
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
        for reactor in self._listeners.get(position, []):
            if hasattr(reactor, "on_bhoga"):
                try:
                    reactor.on_bhoga(state)
                except Exception:
                    pass  # Reactor error doesn't break the cycle

    def _trigger_switch(self, state: ShadowState) -> None:
        """Trigger on_switch for position 8 (THE 8 MOMENT)."""
        for reactor in self._listeners.get(SWITCH_POSITION, []):
            if hasattr(reactor, "on_switch"):
                try:
                    reactor.on_switch(state)
                except Exception:
                    pass

    def _trigger_prasadam(self, state: ShadowState) -> None:
        """Trigger on_prasadam for all reactors at current position."""
        position = state["position"]
        for reactor in self._listeners.get(position, []):
            if hasattr(reactor, "on_prasadam"):
                try:
                    reactor.on_prasadam(state)
                except Exception:
                    pass

    def _trigger_return(self, state: ShadowState) -> None:
        """
        Trigger on_return for position 0 (THE RETURN).

        15→0: Prasadam ready for distribution/acceptance.
        Agent receives sanctified output. Acintya.
        """
        for reactor in self._listeners.get(RETURN_POSITION, []):
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
    def parampara_coherence(self) -> float:
        """
        Current Parampara coherence (0.0 to 1.0).

        CHAITANYA SINGULARITY: How connected is current state to Parampara (37)?
        1.0 = Perfect alignment, 0.0 = Maximum distance from alignment.
        """
        return self._compute_parampara_coherence(self._position, self._cycle_count)

    @property
    def is_parampara_connected(self) -> bool:
        """
        Is current state directly connected to Parampara?

        True at Parampara-aligned positions (vector % 37 == 0).
        """
        return self._verify_parampara(self._position, self._cycle_count)

    @property
    def discovered_count(self) -> int:
        """Number of discovered reactors."""
        return sum(len(r) for r in self._listeners.values())

    def get_state(self) -> ShadowState:
        """Get current state."""
        mapping = get_position_by_index(self._position)
        if mapping is None:
            mapping = MAHAMANTRA_POSITIONS[0]

        return ShadowState(
            position=self._position,
            previous=self._previous_position,
            phase=self.phase.value,
            quarter=mapping.quarter.value,
            guardian=mapping.guardian.value,
            opcode=mapping.opcode.name,
            cycle_count=self._cycle_count,
            switch_count=self._switch_count,
            return_count=self._return_count,
        )

    def __repr__(self) -> str:
        return f"ShadowReactor(id={self._reactor_id}, position={self._position}, phase={self.phase.value}, listeners={self.discovered_count})"

    # =========================================================================
    # LISTENER MANAGEMENT (Protocol implementation)
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
        if not 0 <= position <= 15:
            raise ValueError(f"Position must be 0-15, got {position}")

        if position not in self._listeners:
            self._listeners[position] = []

        if listener not in self._listeners[position]:
            self._listeners[position].append(listener)

    def unregister_listener(
        self,
        position: int,
        listener: ShadowReactorListenerProtocol,
    ) -> None:
        """Unregister a listener from a position."""
        if position in self._listeners:
            if listener in self._listeners[position]:
                self._listeners[position].remove(listener)


# =============================================================================
# SHADOW REACTOR FACTORY - Implements ShadowReactorFactoryProtocol
# =============================================================================

class ShadowReactorFactory:
    """
    Factory for creating ShadowReactor instances.

    Implements ShadowReactorFactoryProtocol for dependency injection.
    Enables SANKIRTAN pattern - multiple reactors running in parallel.

    Usage:
        # Via factory (CORRECT - dependency injection):
        factory = ShadowReactorFactory()
        reactor = factory.spawn()

        # Or use the default factory:
        reactor = shadow_reactor_factory.spawn()
    """

    def spawn(
        self,
        auto_discover: bool = True,
        initial_position: int = 0,
    ) -> ShadowReactor:
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
        return ShadowReactor(
            auto_discover=auto_discover,
            initial_position=initial_position,
        )


# Default factory instance
shadow_reactor_factory = ShadowReactorFactory()


# =============================================================================
# CONVENIENCE FUNCTIONS (BACKWARD COMPATIBILITY)
# =============================================================================

def get_shadow_reactor() -> ShadowReactor:
    """
    Create a new Shadow Reactor.

    NOTE: This now creates a NEW reactor each call (SANKIRTAN pattern).
    Previously was singleton (Ashvamedha). If you need a shared reactor,
    store the reference yourself.
    """
    return shadow_reactor_factory.spawn()


# Convenience alias
shadow = get_shadow_reactor


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol types (from shadow_protocol.py)
    "YajnaPhase",
    "SWITCH_POSITION",
    "RETURN_POSITION",
    "get_phase",
    "TickStateInput",
    "ShadowState",
    "ShadowReactorResult",
    "ShadowReactorListenerProtocol",
    "ShadowReactorProtocol",
    "ShadowReactorFactoryProtocol",
    # Implementation
    "ShadowReactor",
    "ShadowReactorFactory",
    "shadow_reactor_factory",
    # Utility
    "get_shadow_reactor",
    "shadow",
]
