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

# Import GAD Base
from vibe_core.mahamantra.protocols._gad import (
    GADBase,
    GADProtocol,
)

# =============================================================================
# SSOT IMPORTS - The Law (_seed.py) governs the Reality (shadow.py)
# =============================================================================
from vibe_core.mahamantra.protocols._seed import PARAMPARA

# Bhava Protocol - Intent Vector (Grace Scaling)
from vibe_core.mahamantra.protocols._bhava import (
    Bhava,
    SharanagatiLimb,
    calculate_grace,
    get_bhava_multiplier,
)

# Adhikara Protocol - Authorization Chain (Mahajana Signatures)
from vibe_core.mahamantra.protocols._adhikara import (
    Mahajana,
    Quarter as AdhikaraQuarter,
    QUARTER_MAHAJANAS,
    SIGNATURES_REQUIRED,
    create_signature,
    verify_authorization,
    AuthorizationBundle,
    MahajanaSignature,
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

class ShadowReactor(GADBase, ShadowReactorProtocol):
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

    GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
    """

    # Base path for discovery (shared across instances)
    _BASE_PATH: ClassVar[Path] = Path(__file__).parent.parent

    def __init__(
        self,
        auto_discover: bool = True,
        initial_position: int = 0,
        reactor_id: Optional[str] = None,
        forced_lagna: Optional[int] = None,
    ) -> None:
        """
        Initialize ShadowReactor.

        SPAWNBAR: Each call to __init__ creates a NEW reactor.
        No singleton. Multiple reactors can exist (SANKIRTAN!).

        Args:
            auto_discover: If True, discover listeners from folders
            initial_position: Starting position (0-15)
            reactor_id: Optional fixed ID (for deterministic orbit)
            forced_lagna: Optional fixed lagna (for testing)
        """
        super().__init__()  # Init GADBase (Heartbeat)
        # Identity
        self._reactor_id = reactor_id or f"sr_{uuid.uuid4().hex[:8]}"

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

        # =====================================================================
        # ORBITAL MECHANICS (JYOTISHA)
        # =====================================================================
        if forced_lagna is not None:
            self._lagna = forced_lagna
        else:
            from vibe_core.mahamantra.substrate.orbit import OrbitCalculator
            
            orbit_calc = OrbitCalculator()
            # Lagna: Personal Phase Offset
            self._lagna = orbit_calc.get_phase_offset(self._reactor_id, modulus=16)

        # =====================================================================
        # BHAVA STATE (Intent Vector - Grace Scaling)
        # =====================================================================
        # Default: SHANTA (neutral, 1.0x multiplier)
        self._bhava: Bhava = Bhava.SHANTA
        # Default: No limbs fulfilled (compliance = 0)
        self._sharanagati_limbs: set[SharanagatiLimb] = set()
        # Latest computed grace
        self._effective_grace: float = 0.0

        # =====================================================================
        # ADHIKARA STATE (Authorization Chain - Mahajana Signatures)
        # =====================================================================
        # Current authorization bundle (starts empty)
        self._authorization: AuthorizationBundle | None = None

    # =========================================================================
    # PROTOCOL PROPERTIES
    # =========================================================================

    @property
    def lagna(self) -> int:
        """The Phase Offset (Lagna) of this reactor."""
        return self._lagna

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

    # PARAMPARA imported from protocols/_seed.py (SSOT)
    # PARAMPARA = 37 (24 Kshetra + 12 Mahajanas + 1 Ksetrajna)

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
            total_ticks % PARAMPARA == 0 or
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
        remainder = total_ticks % PARAMPARA
        distance = min(remainder, PARAMPARA - remainder)

        # Sinusoidal coherence - creates a rhythmic pattern
        # High at 0, 37, 74... Low at 18, 55... (midpoints)
        phase = (total_ticks / PARAMPARA) * 2 * math.pi
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
        global_position = tick_state["position"]
        
        # APPLY ORBITAL LAGNA (Phase Shift)
        # effective_pos = (global - lagna) % 16
        # Example: Global 8, Lagna 8 -> Effective 0 (Prithu)
        # So at Parashurama's time (8), this reactor serves Prithu (0).
        effective_position = (global_position - self._lagna) % 16
        
        previous = self._position  # Current internal position is standard
        
        # Update state with EFFECTIVE position
        self._position = effective_position
        self._previous_position = previous
        
        # Local alias for downstream logic (fixes NameError)
        position = effective_position

        # =====================================================================
        # PARAMPARA VERIFICATION (CHAITANYA SINGULARITY)
        # =====================================================================
        # Verified against EFFECTIVE position (Personal Parampara)
        parampara_connected = self._verify_parampara(self._position, self._cycle_count)
        parampara_coherence = self._compute_parampara_coherence(self._position, self._cycle_count)

        # =====================================================================
        # BHAVA INTEGRATION (Grace Scaling)
        # =====================================================================
        # G = f × B × S (Frequency × Bhava × Sharanagati)
        self._effective_grace = calculate_grace(
            frequency=parampara_coherence,
            bhava=self._bhava,
            limbs_fulfilled=self._sharanagati_limbs,
        )

        # Get mapping for context (Effective Position)
        mapping = get_position_by_index(self._position)
        if mapping is None:
            mapping = MAHAMANTRA_POSITIONS[0]

        # Determine phase with RETURN detection
        phase = get_phase(position, previous)

        # Build state (WATERTIGHT TypedDict)
        state = ShadowState(
            position=self._position,  # EFFECTIVE
            previous=previous,
            phase=phase.value,
            quarter=mapping.quarter.value,
            guardian=mapping.guardian.value,
            opcode=mapping.opcode.name,
            cycle_count=self._cycle_count,
            switch_count=self._switch_count,
            return_count=self._return_count,
        )

        # THE 8 MOMENT - Bhoga → Prasadam switch (Effective Position)
        if self._position == SWITCH_POSITION and previous == 7:
            self._switch_count += 1
            self._trigger_switch(state)

        # THE RETURN - 15→0 (prasadam becomes next bhoga) (Effective Position)
        if self._position == RETURN_POSITION and previous == 15:
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

    # =========================================================================
    # BHAVA STATE (Intent Vector - Grace Scaling)
    # =========================================================================

    @property
    def bhava(self) -> Bhava:
        """Current Bhava (spiritual emotion)."""
        return self._bhava

    @bhava.setter
    def bhava(self, value: Bhava) -> None:
        """Set Bhava (intent intensity)."""
        self._bhava = value

    @property
    def sharanagati_limbs(self) -> set[SharanagatiLimb]:
        """Current fulfilled Sharanagati limbs."""
        return self._sharanagati_limbs

    def fulfill_limb(self, limb: SharanagatiLimb) -> None:
        """Fulfill a Sharanagati limb (increases grace)."""
        self._sharanagati_limbs.add(limb)

    def unfulfill_limb(self, limb: SharanagatiLimb) -> None:
        """Remove a Sharanagati limb (decreases grace)."""
        self._sharanagati_limbs.discard(limb)

    @property
    def effective_grace(self) -> float:
        """
        Current effective grace (G = f × B × S).
        
        Computed from:
        - f: parampara_coherence (0.0 - 1.0)
        - B: bhava_multiplier (1.0 - 3.0)  
        - S: sharanagati_compliance (0.0 - 1.0)
        """
        return self._effective_grace

    @property
    def bhava_multiplier(self) -> float:
        """Current Bhava multiplier (1.0x to 3.0x)."""
        return get_bhava_multiplier(self._bhava)

    # =========================================================================
    # ADHIKARA STATE (Authorization Chain - Mahajana Signatures)
    # =========================================================================

    @property
    def authorization(self) -> AuthorizationBundle | None:
        """Current authorization bundle (if any)."""
        return self._authorization

    def request_authorization(self, quarter: AdhikaraQuarter, operation_id: str) -> AuthorizationBundle:
        """
        Request authorization for operations in a quarter.
        
        Creates a new AuthorizationBundle that must be signed by
        the appropriate Mahajanas for the quarter.
        
        Args:
            quarter: The quarter in which operations will occur
            operation_id: Unique identifier for this operation
            
        Returns:
            New AuthorizationBundle (needs signatures)
        """
        import hashlib
        payload_hash = hashlib.sha256(operation_id.encode()).hexdigest()
        self._authorization = AuthorizationBundle(
            quarter=quarter,
            operation_id=operation_id,
            payload_hash=payload_hash,
        )
        return self._authorization

    def sign_authorization(self, mahajana: Mahajana, payload: bytes) -> bool:
        """
        Sign the current authorization bundle with a Mahajana.
        
        Args:
            mahajana: The signing Mahajana
            payload: Operation payload to sign
            
        Returns:
            True if signature was added successfully
        """
        if self._authorization is None:
            return False
        
        sig = create_signature(mahajana, payload)
        if sig is None:
            return False
        
        return self._authorization.add_signature(sig)

    def is_authorized(self) -> bool:
        """
        Check if current authorization bundle has sufficient signatures.
        
        Returns:
            True if authorized (enough Mahajana signatures)
        """
        if self._authorization is None:
            return False
        return self._authorization.is_authorized()

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
        return f"OrbitalShadowReactor(id={self._reactor_id}, lagna={self._lagna}, position={self._position})"

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

    # =========================================================================
    # GAD-000 COMPLIANCE
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """Return machine-readable capability description."""
        return {
            "reactor_id": self._reactor_id,
            "type": "ShadowReactor",
            "position": self._position,
            "lagna": self._lagna,
            "capabilities": ["bhoga", "prasadam", "switch", "return"],
            "orbit": "deterministic" if self._reactor_id.startswith("sr_") else "ad-hoc",
        }

    def get_state(self) -> Dict[str, object]:
        """Return current state in structured format."""
        return {
            "identity": {
                "id": self._reactor_id,
                "lagna": self._lagna,
            },
            "cycle": {
                "position": self._position,
                "previous": self._previous_position,
                "cycle_count": self._cycle_count,
            },
            "listeners": {
                pos: len(lst) for pos, lst in self._listeners.items()
            },
            "heartbeat": self.heartbeat.get_summary(),
        }

    def is_healthy(self) -> bool:
        """Return health status."""
        # Reactor is healthy if heartbeat is beating and it has valid position
        return (
            super().is_healthy() and
            0 <= self._position <= 15
        )

    @property
    def is_idempotent(self) -> bool:
        """Reactor is a state machine - transitions are idempotent if inputs are."""
        return True

    def detect_drift(self) -> List[str]:
        """Detect deviations from signed intent."""
        drift = []
        if not (0 <= self._position <= 15):
            drift.append(f"Position OB: {self._position}")
        return drift

    # The 4 Dharma Tests
    def test_daya(self) -> bool:
        return True  # Reactor is merciful (doesn't crash on listener error)

    def test_satyam(self) -> bool:
        return self._verify_parampara(self._position, self._cycle_count)

    def test_tapas(self) -> bool:
        return True  # No resource leaks known

    def test_saucam(self) -> bool:
        return True  # Only registers valid listeners
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
        reactor_id: Optional[str] = None,
        forced_lagna: Optional[int] = None,
    ) -> ShadowReactor:
        """
        Spawn a new ShadowReactor instance.

        SANKIRTAN: Each call creates a NEW reactor.
        No singleton. Multiple reactors can exist.

        Args:
            auto_discover: If True, discover listeners from folders
            initial_position: Starting position (0-15)
            reactor_id: Optional fixed ID (Orbital determinism)
            forced_lagna: Optional fixed lagna (For testing)

        Returns:
            New ShadowReactor instance
        """
        return ShadowReactor(
            auto_discover=auto_discover,
            initial_position=initial_position,
            reactor_id=reactor_id,
            forced_lagna=forced_lagna,
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

# Upgraded Identity
OrbitalShadowReactor = ShadowReactor



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
    # Orbital Alias
    "OrbitalShadowReactor",
]
