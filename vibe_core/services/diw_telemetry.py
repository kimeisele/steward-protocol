"""
DIW TELEMETRY SUBSCRIBER - The First Jiva That Dances
=====================================================

"When Krishna plays His flute, the rivers stop flowing, the cows
 stand still with grass in their mouths, and the gopis drop everything
 to run toward the sound." — Srimad Bhagavatam 10.21

This is the FIRST real DIWSubscriberProtocol implementation.
It receives every 19-bit DIW from the VenuOrchestrator and tracks:
- Total DIW events received
- Phase distribution (MURALI quarters)
- Name distribution (VAMSI regions: H/K/R)
- Mode transitions
- Cycle completions

Zero side effects. Pure observation. The Chitragupta of the flute.

Registration:
    ServiceRegistry.register(
        DIWTelemetrySubscriber, instance,
        protocols=[DIWSubscriberProtocol],
    )
    VenuService.discover_subscribers() finds it automatically.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "chitragupta"
__position__ = 14
__genesis__ = "0x5a3c2e76"

import logging
from typing import Dict, List

from vibe_core.mahamantra.protocols._seed import QUARTERS, WORDS
from vibe_core.mahamantra.protocols._venu import DIWEvent, DIWSubscriberProtocol

logger = logging.getLogger("DIW.TELEMETRY")


class DIWTelemetrySubscriber:
    """
    Observes every DIW event from the VenuOrchestrator.

    Pure telemetry — no mutations, no side effects.
    Implements DIWSubscriberProtocol for auto-discovery.

    Tracks:
        - total_events: Total DIW events received
        - phase_counts: Events per MURALI phase (0-3)
        - mode_counts: Events per Kirtan mode
        - cycles_completed: Full 16-position cycles
        - last_event: Most recent DIWEvent
    """

    def __init__(self) -> None:
        self._total_events: int = 0
        self._phase_counts: List[int] = [0] * QUARTERS  # 4 phases
        self._mode_counts: Dict[int, int] = {}  # mode → count
        self._cycles_completed: int = 0
        self._last_event: DIWEvent | None = None
        self._last_position: int = -1

    @property
    def subscriber_name(self) -> str:
        return "diw_telemetry"

    def on_diw(self, event: DIWEvent) -> None:
        """Called by VenuOrchestrator on every tick."""
        self._total_events += 1
        self._last_event = event

        # Track phase distribution
        phase = event["murali"]
        if 0 <= phase < QUARTERS:
            self._phase_counts[phase] += 1

        # Track mode distribution
        mode = event["mode"]
        self._mode_counts[mode] = self._mode_counts.get(mode, 0) + 1

        # Detect cycle completion (position wraps from 15 → 0)
        position = event["position"]
        if position == 0 and self._last_position == WORDS - 1:
            self._cycles_completed += 1
        self._last_position = position

    @property
    def total_events(self) -> int:
        return self._total_events

    @property
    def cycles_completed(self) -> int:
        return self._cycles_completed

    @property
    def phase_distribution(self) -> List[int]:
        """Events per MURALI phase [genesis, dharma, karma, moksha]."""
        return list(self._phase_counts)

    @property
    def mode_distribution(self) -> Dict[int, int]:
        """Events per Kirtan mode {0: solo, 1: call_response, 2: chorus}."""
        return dict(self._mode_counts)

    def summary(self) -> Dict[str, object]:
        """Full telemetry summary."""
        return {
            "total_events": self._total_events,
            "cycles_completed": self._cycles_completed,
            "phase_distribution": self.phase_distribution,
            "mode_distribution": self.mode_distribution,
            "last_position": self._last_position,
            "last_diw": self._last_event["diw"] if self._last_event else None,
        }

    def __repr__(self) -> str:
        return f"DIWTelemetrySubscriber(events={self._total_events}, cycles={self._cycles_completed})"


__all__ = ["DIWTelemetrySubscriber"]
