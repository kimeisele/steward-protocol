"""
VENU SERVICE - Krishna's Flute (Industrial Grade Heartbeat)
===========================================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

The VenuService is the DRUMMER of the system.
It signals beats with drift-compensated timing.
It does NOT execute tasks - it only SIGNALS.

SENIOR REQUIREMENTS (from Gemini audit):
- Monotonic time: target = start + (tick * 0.25), NOT sleep(0.25) each time
- Jitter tracking: max acceptable = 10ms
- Missed tick detection: when jitter > threshold
- Kernel signaling: callbacks instead of direct execution

ARCHITECTURE:
    VenuService
        └── MantraClock (Phase 2)
        └── Monotonic heartbeat loop
        └── Telemetry (jitter, drift, missed_ticks)
        └── Beat callbacks (kernel signaling)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x2e77ceea"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
import time
from typing import Callable, List

from vibe_core.mahamantra import (
    VENU_MAX_JITTER_MS,
    VENU_POSITIONS,
    VENU_TICK_S,
    VENU_TICKS_PER_MALA,
    BeatSubscriberProtocol,
    DIWSubscriberProtocol,
    HeartbeatMetrics,
    MantraClockProtocol,
    PanchaTattvaProtocol,
    TattvaDict,
    VenuOrchestratorProtocol,
)
from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator
from vibe_core.mahamantra.venu.clock import MantraClock

logger = logging.getLogger("VENU_SERVICE")


class VenuService(PanchaTattvaProtocol):
    """
    The Venu Service - Industrial Grade Heartbeat.

    Uses monotonic time for drift compensation.
    Signals beats to registered callbacks.
    Tracks telemetry (jitter, drift, missed ticks).

    Implements VenuServiceProtocol and PanchaTattvaProtocol.
    """

    __slots__ = (
        "_clock",
        "_orchestrator",
        "_running",
        "_beat_callbacks",
        "_beat_subscribers",
        "_beat_tick_count",
        "_start_time",
        "_cumulative_drift_ms",
        "_max_jitter_ms",
        "_missed_ticks",
        "_stop_event",
    )

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold Truth of Venu Service."""
        return {
            "chaitanya": "Rhythmic Heartbeat Service (Krishna's Flute)",
            "nityananda": "MantraClock + Monotonic Time",
            "advaita": "Drift-Compensated Beat Signaling",
            "gadadhara": "on_beat() Callbacks to Kernel",
            "srivasa": "250ms Tick = PRANA_DURATION / WORDS",
        }

    def __init__(self) -> None:
        """Initialize the VenuService.

        Gets Krishna's flute (VenuOrchestrator) from mahamantra.venu.
        The flute belongs to Krishna, not the drummer (Janaka).
        Registers it in ServiceRegistry so all consumers share it.

        EKAMEVADVITIYAM: VenuService drives the heartbeat through
        Singularity.tick(), not by playing the flute directly.
        This unifies all three broadcast systems into one.
        """
        from vibe_core.di import ServiceRegistry
        from vibe_core.mahamantra import mahamantra

        self._clock = MantraClock()
        self._orchestrator = mahamantra.venu
        self._singularity = mahamantra._get_singularity()
        self._running = False
        self._beat_callbacks: List[Callable[[int], None]] = []
        self._beat_subscribers: List[BeatSubscriberProtocol] = []
        self._beat_tick_count: int = 0
        self._start_time: float = 0.0
        self._cumulative_drift_ms: float = 0.0
        self._max_jitter_ms: float = 0.0
        self._missed_ticks: int = 0
        self._stop_event: asyncio.Event | None = None

        # Register Krishna's flute so all consumers share it
        ServiceRegistry.register(VenuOrchestratorProtocol, self._orchestrator)

    @property
    def is_running(self) -> bool:
        """True if the heartbeat is active."""
        return self._running

    @property
    def clock(self) -> MantraClockProtocol:
        """The underlying MantraClock."""
        return self._clock

    @property
    def orchestrator(self) -> VenuOrchestrator:
        """The DIW orchestrator. Use for subscriber management."""
        return self._orchestrator

    def discover_subscribers(self) -> int:
        """Auto-discover and subscribe all DIWSubscriberProtocol services.

        Queries ServiceRegistry.get_all(DIWSubscriberProtocol) and subscribes
        each one to the orchestrator. This is the enforcement layer:
        if you implement the protocol and are registered, you WILL receive
        the DIW. No manual wiring needed.

        Returns:
            Number of subscribers discovered and wired.
        """
        from vibe_core.di import ServiceRegistry

        discovered = ServiceRegistry.get_all(DIWSubscriberProtocol)
        wired = 0
        for sub in discovered:
            try:
                self._orchestrator.subscribe(sub)
                wired += 1
                logger.info(f"\U0001f3b5 DIW subscriber discovered: {sub.subscriber_name}")
            except (TypeError, Exception) as exc:
                logger.warning(f"DIW subscriber rejected: {exc}")
        if wired:
            logger.info(f"\U0001f3b5 {wired} DIW subscribers auto-wired (FOLDER=EXISTENCE)")
        return wired

    @property
    def metrics(self) -> HeartbeatMetrics:
        """Current telemetry metrics."""
        uptime = time.monotonic() - self._start_time if self._start_time > 0 else 0.0
        tick_count = self._clock.tick.tick_count

        return HeartbeatMetrics(
            total_ticks=tick_count,
            total_cycles=tick_count // VENU_POSITIONS,
            total_malas=tick_count // VENU_TICKS_PER_MALA,
            cumulative_drift_ms=self._cumulative_drift_ms,
            max_jitter_ms=self._max_jitter_ms,
            missed_ticks=self._missed_ticks,
            uptime_seconds=uptime,
        )

    def on_beat(self, callback: Callable[[int], None]) -> None:
        """
        Register a callback for each beat.

        Args:
            callback: Function called with position (0-15) on each beat
        """
        self._beat_callbacks.append(callback)

    def add_beat_subscriber(self, subscriber: BeatSubscriberProtocol) -> None:
        """Register a BeatSubscriberProtocol.

        The subscriber's on_beat_tick() will be called every
        subscriber.beat_interval ticks. Dispatch is internal —
        no external closure needed.
        """
        self._beat_subscribers.append(subscriber)

    def discover_beat_subscribers(self) -> int:
        """Auto-discover all BeatSubscriberProtocol services from ServiceRegistry.

        Returns:
            Number of subscribers discovered and registered.
        """
        from vibe_core.di import ServiceRegistry

        discovered = ServiceRegistry.get_all(BeatSubscriberProtocol) or []
        for sub in discovered:
            if sub not in self._beat_subscribers:
                self._beat_subscribers.append(sub)
                logger.info("Beat subscriber discovered: %s (every %d ticks)", sub.beat_name, sub.beat_interval)
        return len(self._beat_subscribers)

    def _dispatch_beat_subscribers(self, position: int) -> None:
        """Dispatch to all BeatSubscribers whose interval has fired."""
        self._beat_tick_count += 1
        tick = self._beat_tick_count
        for sub in self._beat_subscribers:
            try:
                if tick % sub.beat_interval == 0:
                    sub.on_beat_tick(tick, position)
            except Exception as e:
                logger.warning("⚠️ Beat subscriber %s FAILED at tick %d: %s", sub.beat_name, tick, e)

    async def start(self) -> None:
        """
        Start the heartbeat loop.

        Uses monotonic time for drift compensation:
        - target_time = start_time + (tick_count * VENU_TICK_S)
        - sleep_time = target_time - current_time
        - If sleep_time < 0, we missed a tick
        """
        if self._running:
            logger.warning("VenuService already running")
            return

        self._running = True
        self._start_time = time.monotonic()
        self._stop_event = asyncio.Event()
        self._cumulative_drift_ms = 0.0
        self._max_jitter_ms = 0.0
        self._missed_ticks = 0

        logger.info("🎵 VenuService started - Krishna's flute begins to play")

        try:
            while self._running:
                # 1. Calculate target time for this tick (DRIFT-PROOF)
                tick_count = self._clock.tick.tick_count
                target_time = self._start_time + (tick_count * VENU_TICK_S)
                current_time = time.monotonic()

                # 2. Calculate sleep time
                sleep_time = target_time - current_time

                # 3. Handle timing
                if sleep_time > 0:
                    # Normal case: wait until target time
                    try:
                        await asyncio.wait_for(self._stop_event.wait(), timeout=sleep_time)
                        # If we get here, stop was called
                        break
                    except asyncio.TimeoutError:
                        # Normal timeout - continue to tick
                        pass
                else:
                    # We're behind schedule - missed tick potential
                    jitter_ms = abs(sleep_time) * 1000
                    if jitter_ms > VENU_MAX_JITTER_MS:
                        self._missed_ticks += 1
                        logger.warning(f"⚠️ Missed tick! Jitter: {jitter_ms:.2f}ms (threshold: {VENU_MAX_JITTER_MS}ms)")

                # 4. Check if stopped during wait
                if not self._running:
                    break

                # 5. Record telemetry
                actual_time = time.monotonic()
                jitter_ms = abs(actual_time - target_time) * 1000
                self._cumulative_drift_ms += jitter_ms
                self._max_jitter_ms = max(self._max_jitter_ms, jitter_ms)

                # 6. Get current position and signal callbacks
                position = self._clock.position
                for callback in self._beat_callbacks:
                    try:
                        callback(position)
                    except Exception as e:
                        logger.error(f"Beat callback error at position {position}: {e}")

                # 6.5. Dispatch BeatSubscribers (interval-based)
                self._dispatch_beat_subscribers(position)

                # 7. Play the flute THROUGH KRISHNA: Singularity.tick()
                #    advances Kala, plays flute (venu.step()), and broadcasts
                #    TickState to ALL listeners (SravanamListener, etc.).
                #    This is the UNIFIED heartbeat — one tick, all systems hear.
                self._singularity.tick()

                # 8. Advance the clock (execute tasks in MantraClock, then advance)
                self._clock.tick_once()

        finally:
            self._running = False
            logger.info(
                f"🎵 VenuService stopped - "
                f"ticks: {self._clock.tick.tick_count}, "
                f"drift: {self._cumulative_drift_ms:.2f}ms, "
                f"missed: {self._missed_ticks}"
            )

    async def stop(self) -> None:
        """Stop the heartbeat loop gracefully."""
        if not self._running:
            return

        self._running = False
        if self._stop_event:
            self._stop_event.set()

    def __repr__(self) -> str:
        status = "RUNNING" if self._running else "STOPPED"
        return f"VenuService({status}, ticks={self._clock.tick.tick_count})"
