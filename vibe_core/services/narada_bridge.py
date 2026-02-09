"""
NARADA BRIDGE — The Messenger Between Krishna's Flute and the Jivas
====================================================================

"nārada muni bājāya vīṇā, rādhikā-ramaṇa-nāme"
"Narada Muni plays his vina, singing the name of Radhika-Ramana"

Narada hears Krishna's flute (VenuOrchestrator) and carries the rhythm
to all agents (EventBus). This bridge connects the two event systems:

    VenuOrchestrator  →  NaradaBridge  →  EventBus
    (19-bit DIW)         (translates)     (agent events)

The bridge:
1. Implements DIWSubscriberProtocol — receives every tick from the flute
2. Stamps agent events with DIW context (position, phase, tick)
3. Emits phase-transition events when quarters change
4. Provides the current rhythmic context to any caller

BOOT ORDER:
    EventBus is created early (BootOrchestrator.__init__).
    NaradaBridge is wired later (VenuService.discover_subscribers).
    Before wiring: EventBus works normally, no DIW context.
    After wiring:  Every event carries the flute's rhythm.

GRACEFUL DEGRADATION:
    If VenuService never starts (CLI, tests), the bridge is never
    wired and the EventBus works exactly as before. Zero regression.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xec02c0c4"

import logging
from typing import Dict, Optional, TypedDict

from vibe_core.mahamantra.protocols._seed import QUARTERS
from vibe_core.mahamantra.protocols._venu import DIWEvent

logger = logging.getLogger("NARADA.BRIDGE")

# Quarter names derived from the Mahamantra's 4-fold structure
_QUARTER_NAMES = ("genesis", "dharma", "karma", "moksha")


class DIWContext(TypedDict):
    """Rhythmic context stamped onto every agent event after bridge is wired."""

    diw: int           # 19-bit Divine Instruction Word
    tick: int          # Absolute tick count
    position: int      # Position in 16-beat cycle (0..15)
    phase: int         # Quarter/phase (0..3)
    quarter: str       # Quarter name (genesis/dharma/karma/moksha)
    mode: int          # Kirtan mode (0=Solo, 1=CallResponse, 2=Chorus)


class NaradaBridge:
    """
    The bridge between Krishna's flute and the agent event bus.

    Implements DIWSubscriberProtocol so VenuService auto-discovers it.
    Holds the current DIW context and stamps it onto agent events.

    Usage:
        bridge = NaradaBridge()
        # VenuService.discover_subscribers() finds it automatically.
        # After wiring, bridge.context returns the current DIW state.
    """

    __slots__ = (
        "_context", "_prev_phase", "_total_ticks",
        "_phase_transitions", "_event_bus_ref",
    )

    def __init__(self) -> None:
        self._context: Optional[DIWContext] = None
        self._prev_phase: int = -1
        self._total_ticks: int = 0
        self._phase_transitions: int = 0
        self._event_bus_ref = None  # Lazy — set when first needed

    # =========================================================================
    # DIWSubscriberProtocol implementation
    # =========================================================================

    @property
    def subscriber_name(self) -> str:
        return "narada_bridge"

    def on_diw(self, event: DIWEvent) -> None:
        """
        Called by VenuOrchestrator on every tick.

        Updates the bridge's rhythmic context and detects phase transitions.
        When a quarter changes (genesis→dharma→karma→moksha), emits a
        PHASE_TRANSITION event on the EventBus so agents know the rhythm shifted.
        """
        phase = event["murali"]
        quarter_idx = phase % QUARTERS
        quarter_name = _QUARTER_NAMES[quarter_idx]

        self._context = DIWContext(
            diw=event["diw"],
            tick=event["tick"],
            position=event["position"],
            phase=phase,
            quarter=quarter_name,
            mode=event["mode"],
        )
        self._total_ticks += 1

        # Detect phase transition
        if self._prev_phase >= 0 and phase != self._prev_phase:
            self._phase_transitions += 1
            self._emit_phase_transition(
                from_phase=self._prev_phase,
                to_phase=phase,
                tick=event["tick"],
            )

        self._prev_phase = phase

    # =========================================================================
    # Public API
    # =========================================================================

    @property
    def context(self) -> Optional[DIWContext]:
        """Current DIW context, or None if bridge not yet wired."""
        return self._context

    @property
    def is_wired(self) -> bool:
        """True if the bridge has received at least one DIW tick."""
        return self._context is not None

    @property
    def total_ticks(self) -> int:
        """Total DIW ticks received since wiring."""
        return self._total_ticks

    @property
    def phase_transitions(self) -> int:
        """Number of quarter transitions observed."""
        return self._phase_transitions

    def stamp_event_details(self, details: Dict) -> Dict:
        """
        Stamp an event's details dict with the current DIW context.

        If the bridge is not yet wired (no VenuService), returns
        the details unchanged. Zero regression for pre-wiring callers.

        Args:
            details: The event's existing details dict.

        Returns:
            The details dict with 'diw_context' added (if wired).
        """
        if self._context is None:
            return details
        stamped = dict(details) if details else {}
        stamped["diw_context"] = dict(self._context)
        return stamped

    def summary(self) -> Dict:
        """Bridge telemetry summary."""
        return {
            "is_wired": self.is_wired,
            "total_ticks": self._total_ticks,
            "phase_transitions": self._phase_transitions,
            "current_context": dict(self._context) if self._context else None,
        }

    # =========================================================================
    # Phase Transition Events
    # =========================================================================

    def _emit_phase_transition(self, from_phase: int, to_phase: int, tick: int) -> None:
        """Emit a phase-transition event on the EventBus.

        This is the bridge in action: the flute's rhythm becomes an agent event.
        Agents subscribed to PHASE_TRANSITION events can adjust their behavior
        based on which quarter the system is in.
        """
        bus = self._get_event_bus()
        if bus is None:
            return

        from_quarter = _QUARTER_NAMES[from_phase % QUARTERS]
        to_quarter = _QUARTER_NAMES[to_phase % QUARTERS]

        bus.emit_sync(
            event_type="PHASE_TRANSITION",
            agent_id="narada_bridge",
            message=f"{from_quarter} → {to_quarter} (tick {tick})",
            data={
                "message": f"Phase transition: {from_quarter} → {to_quarter}",
                "result_summary": f"from={from_phase},to={to_phase},tick={tick}",
            },
        )

        logger.debug(
            "Phase transition: %s → %s at tick %d",
            from_quarter, to_quarter, tick,
        )

    def _get_event_bus(self):
        """Lazy-load the EventBus singleton. Avoids circular imports at module level."""
        if self._event_bus_ref is None:
            try:
                from vibe_core.mahamantra.substrate.event_bus import get_event_bus
                self._event_bus_ref = get_event_bus()
            except Exception:
                return None
        return self._event_bus_ref

    def __repr__(self) -> str:
        status = "WIRED" if self.is_wired else "UNWIRED"
        return f"NaradaBridge({status}, ticks={self._total_ticks})"


# =============================================================================
# MODULE-LEVEL SINGLETON
# =============================================================================
# One bridge per process. Same pattern as get_event_bus().

_bridge_instance: Optional[NaradaBridge] = None


def get_narada_bridge() -> NaradaBridge:
    """Get or create the NaradaBridge singleton.

    The bridge is created once and reused. It starts UNWIRED (no DIW context).
    When VenuService discovers it as a DIWSubscriber, it becomes WIRED and
    every subsequent agent event can carry the flute's rhythm.
    """
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = NaradaBridge()
    return _bridge_instance


__all__ = [
    "NaradaBridge",
    "DIWContext",
    "get_narada_bridge",
]
