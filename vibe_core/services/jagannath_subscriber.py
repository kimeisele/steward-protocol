"""
JAGANNATH BEAT SUBSCRIBER - Ratha Yatra on Rhythm
==================================================

Triggers Jagannath's Ratha Yatra (system-wide orphan scan) on the
VenuService heartbeat via BeatSubscriberProtocol.

Interval: FIELD (144 ticks = 36 seconds) — harmonically derived.

MIGRATION (Feb 2026):
    Was: Closure hack in boot_orchestrator.py with mutable dict counter
    Now: BeatSubscriberProtocol, auto-discovered at boot
    Why: Same pattern as all other beat subscribers. No special wiring.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0x386870f6"  # GenesisByte: parampara % 37 == 0

import logging

from vibe_core.mahamantra.protocols._venu import VENU_FIELD_TICKS

logger = logging.getLogger("JAGANNATH.BEAT")


class JagannathSubscriber:
    """
    Triggers Ratha Yatra (orphan scan + naturalization) every FIELD interval.

    Implements BeatSubscriberProtocol. VenuService discovers this
    at boot via ServiceRegistry.get_all(BeatSubscriberProtocol).

    Beat interval: FIELD (144 ticks = 36s).
    """

    @property
    def beat_name(self) -> str:
        return "jagannath_ratha_yatra"

    @property
    def beat_interval(self) -> int:
        return VENU_FIELD_TICKS  # 144 ticks = 36 seconds

    def on_beat_tick(self, tick_count: int, position: int) -> None:
        """Called by VenuService every FIELD interval."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.lila.jagannath import IJagannath

            jagannath = ServiceRegistry.get(IJagannath)
            if jagannath is None:
                return

            jagannath.start_ratha_yatra()
        except Exception as e:
            logger.debug("[RATHA] Ratha Yatra tick skipped: %s", e)


__all__ = ["JagannathSubscriber"]
