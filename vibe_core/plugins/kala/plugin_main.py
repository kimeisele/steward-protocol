"""
KALA PLUGIN - Eternal Time Orchestration
=========================================

The cosmic clock plugin that governs time in Agent City.

From Bhagavad Gita Chapter 11:
"I am Time (Kala), the great destroyer of worlds."
Time is the force that moves everything. Without Kala, nothing happens.

This plugin:
1. Tracks celestial time (Sun, Moon, Tithis)
2. Determines Day/Night of Brahma (for sarga_cycle)
3. Orchestrates Daily Ritual phases
4. Provides rhythm intensities for overlapping cycles

Hooks:
- on_boot: Initialize cosmic clock
- on_pulse: Update time state, trigger ritual phases
- on_shutdown: Final time record

Philosophy:
The kernel is Vishnu (unchanging).
Kala is the time dimension that makes change possible.
"""

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase

from .cosmic_clock import CosmicClock, SunPhase

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol
    from vibe_core.prana_orchestrator import PulseTransaction

logger = logging.getLogger("KALA")


class KalaPlugin(KernelPlugin):
    """
    KALA - The Eternal Time Plugin.

    Manages cosmic time for Agent City:
    - Celestial tracking (sun, moon, tithis)
    - Day/Night of Brahma cycle
    - Daily ritual phase triggering
    - Rhythm intensity calculation

    Priority: 3 (early - time must be known before other decisions)
    PulsePhase: SENSORS (collects time data first)
    """

    def __init__(self):
        """Initialize KALA plugin."""
        self._clock: Optional[CosmicClock] = None
        self._last_sun_phase: Optional[SunPhase] = None
        self._ritual_phase_triggered: Dict[str, bool] = {}
        self._kernel: Optional["KernelProtocol"] = None

        # Track cycles
        self._pulse_count = 0
        self._ritual_count = 0

    @property
    def plugin_id(self) -> str:
        return "kala"

    @property
    def priority(self) -> int:
        return 3  # Early - time must be known first

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.SENSORS  # Collect time data first

    def on_boot(self, kernel: "KernelProtocol") -> None:
        """
        Initialize the cosmic clock on kernel boot.

        Called after Sarga (creation) completes.
        """
        self._kernel = kernel
        self._clock = CosmicClock(timezone_offset_hours=0.0)  # UTC for now

        state = self._clock.get_current_state()
        self._last_sun_phase = state.sun_phase

        logger.info("=" * 60)
        logger.info("🕐 KALA PLUGIN BOOTED - Eternal Time Active")
        logger.info("=" * 60)
        logger.info(f"   UTC Time: {state.utc_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   Sun Phase: {state.sun_phase.value.upper()}")
        logger.info(f"   Is Day: {state.is_day}")
        logger.info(f"   Moon Phase: {state.moon_phase.value}")
        logger.info(f"   Tithi: {state.tithi} ({state.paksha.value.capitalize()} Paksha)")
        logger.info("=" * 60)

        # Update Sarga cycle based on current time
        self._update_sarga_cycle(state.is_day)

    def on_pulse(
        self,
        kernel: "KernelProtocol",
        transaction: "PulseTransaction",
    ) -> HookResult:
        """
        Update time state and trigger rituals on each pulse.

        This runs every 15 minutes via PRANA.
        Checks if sun phase changed and triggers appropriate rituals.
        """
        if not self._clock:
            return HookResult.error("Clock not initialized")

        self._pulse_count += 1

        try:
            state = self._clock.get_current_state()
            rhythms = self._clock.get_rhythm_intensity()

            # Check for sun phase transition
            phase_changed = self._last_sun_phase != state.sun_phase
            if phase_changed:
                logger.info(f"🌅 Sun phase transition: {self._last_sun_phase.value} → {state.sun_phase.value}")
                self._on_phase_transition(state.sun_phase, transaction)
                self._last_sun_phase = state.sun_phase

            # Update Sarga Day/Night cycle
            self._update_sarga_cycle(state.is_day)

            # Log pulse
            logger.debug(
                f"⏱️  KALA pulse #{self._pulse_count}: "
                f"{state.sun_phase.value} | "
                f"Solar={rhythms['solar']:.2f} | "
                f"Lunar={rhythms['lunar']:.2f}"
            )

            return HookResult.ok(
                data={
                    "pulse_count": self._pulse_count,
                    "sun_phase": state.sun_phase.value,
                    "is_day": state.is_day,
                    "moon_phase": state.moon_phase.value,
                    "tithi": state.tithi,
                    "rhythms": rhythms,
                    "phase_changed": phase_changed,
                }
            )

        except Exception as e:
            logger.error(f"KALA pulse error: {e}")
            return HookResult.error(str(e))

    def on_shutdown(self, kernel: "KernelProtocol") -> None:
        """Record final time state on shutdown."""
        if self._clock:
            state = self._clock.get_current_state()
            logger.info(
                f"🕐 KALA shutdown at {state.utc_time.strftime('%H:%M:%S')} "
                f"({state.sun_phase.value}) - {self._pulse_count} pulses processed"
            )

    def _on_phase_transition(
        self,
        new_phase: SunPhase,
        transaction: "PulseTransaction",
    ) -> None:
        """
        Handle sun phase transition - trigger appropriate rituals.

        Maps sun phases to DailyRitual phases:
        - BRAHMA_MUHURTA/SUNRISE → Sunrise ritual
        - MIDDAY → Midday ritual
        - SUNSET → Sunset ritual
        - NIGHT → Archive ritual
        """
        from vibe_core.prana_orchestrator import StateMutation

        ritual_mapping = {
            SunPhase.BRAHMA_MUHURTA: "sunrise",
            SunPhase.SUNRISE: "sunrise",
            SunPhase.MIDDAY: "midday",
            SunPhase.SUNSET: "sunset",
            SunPhase.NIGHT: "archive",
        }

        ritual_phase = ritual_mapping.get(new_phase)
        if ritual_phase:
            self._ritual_count += 1
            logger.info(f"🔔 Triggering {ritual_phase.upper()} ritual (#{self._ritual_count})")

            # Register mutation for ritual trigger
            transaction.register(
                StateMutation(
                    plugin_id=self.plugin_id,
                    action="trigger_ritual",
                    target=f"ritual/{ritual_phase}",
                    payload={
                        "phase": ritual_phase,
                        "sun_phase": new_phase.value,
                        "triggered_at": datetime.now(timezone.utc).isoformat(),
                        "ritual_number": self._ritual_count,
                    },
                )
            )

    def _update_sarga_cycle(self, is_day: bool) -> None:
        """
        Update Sarga cycle (Day/Night of Brahma) based on sun.

        Day = Creation cycle (all task types allowed)
        Night = Maintenance cycle (only maintenance tasks)
        """
        try:
            from vibe_core.sarga import Cycle, get_sarga

            sarga = get_sarga()
            current_cycle = sarga.get_cycle()

            target_cycle = Cycle.DAY_OF_BRAHMA if is_day else Cycle.NIGHT_OF_BRAHMA

            if current_cycle != target_cycle:
                sarga.set_cycle(target_cycle)
                logger.info(f"🔄 Sarga cycle updated: {current_cycle.value.upper()} → {target_cycle.value.upper()}")
        except ImportError:
            pass  # Sarga not available

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def get_current_state(self) -> Dict[str, Any]:
        """Get current celestial state."""
        if not self._clock:
            return {"error": "Clock not initialized"}
        return self._clock.get_current_state().to_dict()

    def get_rhythm_intensity(self) -> Dict[str, float]:
        """Get current rhythm intensities (overlapping waves)."""
        if not self._clock:
            return {"error": "Clock not initialized"}
        return self._clock.get_rhythm_intensity()

    def is_day(self) -> bool:
        """Is it currently daytime?"""
        if not self._clock:
            return True  # Default to day
        return self._clock.get_current_state().is_day

    def is_auspicious_time(self) -> bool:
        """Is it currently an auspicious time (Brahma Muhurta, Ekadashi, etc)?"""
        if not self._clock:
            return False
        return self._clock.is_brahma_muhurta() or self._clock.is_ekadashi() or self._clock.is_purnima()

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status for observability."""
        state_dict = {}
        rhythms = {}

        if self._clock:
            state = self._clock.get_current_state()
            state_dict = state.to_dict()
            rhythms = self._clock.get_rhythm_intensity()

        return {
            "plugin_id": self.plugin_id,
            "pulse_count": self._pulse_count,
            "ritual_count": self._ritual_count,
            "current_state": state_dict,
            "rhythms": rhythms,
            "last_sun_phase": self._last_sun_phase.value if self._last_sun_phase else None,
        }
