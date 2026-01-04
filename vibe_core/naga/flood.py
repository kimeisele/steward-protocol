"""
NAGA Organic Flooding - Hardened Implementation.

"Wie Wasser in jede Ritze" - but with safety guards.

Critical Safety Mechanisms (from Gemini's critique):
1. RECURSION GUARD: Prevent NAGAs from catching their own events
2. ASYNC DECOUPLING: Fire and forget, don't block the bus
3. SIDE CHANNEL: Violations go to Ledger, not back to EventBus

The Three Deadly Risks Avoided:
- Ouroboros Recursion Trap (infinite loop)
- Observer Effect (latency death)
- Signal Noise (bus pollution)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set
from weakref import WeakSet

if TYPE_CHECKING:
    from vibe_core.naga.services.sesha import SeshaService
    from vibe_core.naga.services.takshaka import TakshakaService
    from vibe_core.protocols.event import Event

logger = logging.getLogger("NAGA.FLOOD")


# =============================================================================
# CONSTANTS
# =============================================================================

# Events from these sources are NEVER intercepted (recursion prevention)
NAGA_SOURCE_IDS = frozenset(
    [
        "NAGA_EYE",
        "sesha",
        "vasuki",
        "takshaka",
        "naga_flood",
        "naga_watcher",
    ]
)

# Event types that are too noisy to analyze (performance protection)
SKIP_EVENT_TYPES = frozenset(
    [
        "DEBUG",
        "TRACE",
        "HEARTBEAT",
        "METRIC",
        "PING",
        "PONG",
    ]
)

# Maximum events to queue for async analysis
MAX_ANALYSIS_QUEUE = 1000

# Timeout for async analysis (prevents hanging)
ANALYSIS_TIMEOUT_MS = 50


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class FloodStats:
    """Statistics for flood monitoring."""

    events_seen: int = 0
    events_skipped_recursion: int = 0
    events_skipped_noise: int = 0
    events_analyzed: int = 0
    violations_detected: int = 0
    analysis_timeouts: int = 0
    queue_overflows: int = 0
    started_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        uptime = (datetime.now() - self.started_at).total_seconds()
        return {
            "events_seen": self.events_seen,
            "events_skipped_recursion": self.events_skipped_recursion,
            "events_skipped_noise": self.events_skipped_noise,
            "events_analyzed": self.events_analyzed,
            "violations_detected": self.violations_detected,
            "analysis_timeouts": self.analysis_timeouts,
            "queue_overflows": self.queue_overflows,
            "uptime_seconds": uptime,
            "events_per_second": self.events_seen / uptime if uptime > 0 else 0,
        }


# =============================================================================
# NAGA FLOOD CONTROLLER
# =============================================================================


class NagaFloodController:
    """
    Hardened controller for organic NAGA flooding.

    Implements the "Prahlad Maharaj Pattern" - serving invisibly
    without causing system epilepsy.

    Key Design Principles:
    1. NEVER block the EventBus
    2. NEVER create recursion loops
    3. ALWAYS fail silently (observer must not crash system)
    4. Use side channels for violations (not EventBus)
    """

    def __init__(
        self,
        sesha: Optional["SeshaService"] = None,
        takshaka: Optional["TakshakaService"] = None,
        enabled: bool = True,
    ):
        self._sesha = sesha
        self._takshaka = takshaka
        self._enabled = enabled
        self._stats = FloodStats()
        self._subscribed = False

        # Async analysis queue (bounded)
        self._analysis_queue: asyncio.Queue = asyncio.Queue(maxsize=MAX_ANALYSIS_QUEUE)
        self._analysis_task: Optional[asyncio.Task] = None

        # Seen event IDs (prevent duplicate analysis)
        self._seen_events: Set[str] = set()
        self._seen_events_max = 10000

        logger.debug("[FLOOD] Controller initialized")

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    def start(self) -> None:
        """Start the flood controller - subscribe to EventBus."""
        if not self._enabled:
            logger.info("[FLOOD] Controller disabled, not starting")
            return

        if self._subscribed:
            logger.warning("[FLOOD] Already subscribed")
            return

        try:
            from vibe_core.protocols.event import get_event_bus_safe

            bus = get_event_bus_safe()

            # Subscribe to ALL events (global subscriber)
            if hasattr(bus, "subscribe_all"):
                bus.subscribe_all(self._on_event_sync)
                self._subscribed = True
                logger.info("[FLOOD] 🌊 Subscribed to EventBus (global)")
            elif hasattr(bus, "subscribe"):
                # Fallback: subscribe without type filter
                bus.subscribe(self._on_event_sync)
                self._subscribed = True
                logger.info("[FLOOD] 🌊 Subscribed to EventBus (fallback)")
            else:
                logger.warning("[FLOOD] EventBus has no subscribe method")

        except ImportError:
            logger.debug("[FLOOD] EventBus not available")
        except Exception as e:
            logger.error(f"[FLOOD] Failed to subscribe: {e}")

    def stop(self) -> None:
        """Stop the flood controller."""
        if self._analysis_task and not self._analysis_task.done():
            self._analysis_task.cancel()

        self._subscribed = False
        logger.info("[FLOOD] Controller stopped")

    # =========================================================================
    # EVENT HANDLING (SYNCHRONOUS - FAST PATH)
    # =========================================================================

    def _on_event_sync(self, event: "Event") -> None:
        """
        Synchronous event handler - MUST BE FAST.

        This runs on the EventBus thread. Any blocking here
        causes system-wide latency.

        Strategy: Quick checks, then fire-and-forget to async queue.
        """
        self._stats.events_seen += 1

        # --- RECURSION GUARD (The Mirror Shield) ---
        # Check if event is from NAGA itself
        source = getattr(event, "agent_id", None)
        if source is None:
            source = getattr(event, "source", None)
        if source is None:
            source = ""
        # Convert to string for comparison (handles MagicMock)
        source_str = str(source) if source else ""
        if source_str in NAGA_SOURCE_IDS:
            self._stats.events_skipped_recursion += 1
            return

        # Check if already marked as seen by NAGA
        # Must be explicitly True (not just truthy - MagicMock is truthy)
        naga_seen = getattr(event, "_naga_seen", None)
        if naga_seen is True:
            self._stats.events_skipped_recursion += 1
            return

        # --- NOISE FILTER ---
        event_type = getattr(event, "event_type", None)
        event_type_str = str(event_type) if event_type else ""
        if event_type_str in SKIP_EVENT_TYPES:
            self._stats.events_skipped_noise += 1
            return

        # --- DUPLICATE CHECK ---
        event_id = getattr(event, "id", None) or id(event)
        if event_id in self._seen_events:
            return

        # Mark as seen (prevent re-analysis)
        self._seen_events.add(event_id)
        if len(self._seen_events) > self._seen_events_max:
            # Trim oldest (simple LRU)
            self._seen_events = set(list(self._seen_events)[-5000:])

        # --- ASYNC HANDOFF (Fire and Forget) ---
        try:
            self._analysis_queue.put_nowait(event)
        except asyncio.QueueFull:
            self._stats.queue_overflows += 1
            # Silent drop - observer must not block

    # =========================================================================
    # ASYNC ANALYSIS (SLOW PATH - OFF MAIN THREAD)
    # =========================================================================

    async def start_analysis_loop(self) -> None:
        """Start the async analysis loop."""
        logger.info("[FLOOD] 🔬 Analysis loop starting")

        while True:
            try:
                # Wait for event from queue
                event = await asyncio.wait_for(
                    self._analysis_queue.get(),
                    timeout=5.0,  # Check for shutdown every 5s
                )

                # Analyze with timeout
                try:
                    await asyncio.wait_for(
                        self._analyze_event(event),
                        timeout=ANALYSIS_TIMEOUT_MS / 1000,
                    )
                    self._stats.events_analyzed += 1
                except asyncio.TimeoutError:
                    self._stats.analysis_timeouts += 1

            except asyncio.TimeoutError:
                # No events in queue, continue waiting
                continue
            except asyncio.CancelledError:
                logger.info("[FLOOD] Analysis loop cancelled")
                break
            except Exception as e:
                # Silent fail - observer must not crash
                logger.debug(f"[FLOOD] Analysis error: {e}")

    async def _analyze_event(self, event: "Event") -> None:
        """
        Analyze event for toxicity (async, isolated).

        If analysis crashes or hangs, only this task dies,
        not the EventBus.
        """
        if not self._takshaka:
            return

        try:
            # Extract content to analyze
            content = self._extract_content(event)
            if not content:
                return

            # Run toxicity scan
            toxicity = self._takshaka.scan_toxicity(content)

            if toxicity.blocked:
                self._stats.violations_detected += 1

                # --- SIDE CHANNEL DISPATCH ---
                # Write to Ledger directly, NOT back to EventBus
                await self._dispatch_violation(event, toxicity)

        except Exception as e:
            # Silent fail
            logger.debug(f"[FLOOD] Analysis failed: {e}")

    def _extract_content(self, event: "Event") -> str:
        """Extract analyzable content from event."""
        parts = []

        # Try common attributes
        for attr in ["message", "content", "data", "payload", "text"]:
            value = getattr(event, attr, None)
            if value:
                if isinstance(value, str):
                    parts.append(value)
                elif isinstance(value, dict):
                    parts.append(str(value))

        return " ".join(parts)[:10000]  # Limit size

    async def _dispatch_violation(self, event: "Event", toxicity: Any) -> None:
        """
        Dispatch violation via SIDE CHANNEL (not EventBus).

        This prevents the Ouroboros trap - violations go directly
        to Ledger/Sesha, not back into the event stream.
        """
        from vibe_core.protocols.naga import VajraViolation

        violation = VajraViolation(
            violation_type="TOXIC_EVENT",
            source=getattr(event, "agent_id", "unknown"),
            details={
                "event_type": getattr(event, "event_type", "unknown"),
                "patterns": toxicity.patterns if hasattr(toxicity, "patterns") else [],
                "score": toxicity.score if hasattr(toxicity, "score") else 0,
                "detected_at": datetime.now().isoformat(),
            },
        )

        # Write to Takshaka (which writes to Ledger)
        if self._takshaka:
            self._takshaka.bite(violation)
            logger.warning(f"[FLOOD] 🐍 BITE: Toxic event from {violation.source}")

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get flood statistics."""
        return {
            "enabled": self._enabled,
            "subscribed": self._subscribed,
            "queue_size": self._analysis_queue.qsize(),
            **self._stats.to_dict(),
        }


# =============================================================================
# SIGNAL BUS FLOODING (Phase 2b)
# =============================================================================


class NagaSignalWatcher:
    """
    Watch SignalBus for critical signals.

    Unlike EventBus, SignalBus is for HIGH PRIORITY commands.
    We only watch, we don't analyze everything.
    """

    CRITICAL_SIGNALS = frozenset(
        [
            "POLICY_VIOLATION",
            "AGENT_ERROR",
            "AUDIT_REQUEST",
        ]
    )

    def __init__(
        self,
        sesha: Optional["SeshaService"] = None,
        takshaka: Optional["TakshakaService"] = None,
    ):
        self._sesha = sesha
        self._takshaka = takshaka
        self._subscribed = False
        self._signals_seen = 0

    def start(self) -> None:
        """Subscribe to critical signals."""
        try:
            from vibe_core.steward.bus import SignalType, get_bus

            bus = get_bus()

            # Only subscribe to CRITICAL signals (not all)
            for signal_name in self.CRITICAL_SIGNALS:
                try:
                    signal_type = SignalType[signal_name]
                    bus.subscribe(
                        listener_id=f"naga_{signal_name.lower()}",
                        signal_type=signal_type,
                        callback=self._on_signal,
                    )
                except (KeyError, AttributeError):
                    pass  # Signal type doesn't exist

            self._subscribed = True
            logger.info("[FLOOD] 📡 Subscribed to SignalBus (critical signals)")

        except ImportError:
            logger.debug("[FLOOD] SignalBus not available")
        except Exception as e:
            logger.error(f"[FLOOD] Failed to subscribe to SignalBus: {e}")

    def _on_signal(self, signal: Any) -> None:
        """Handle critical signal - log to Sesha."""
        self._signals_seen += 1

        if self._sesha:
            # Record in Ledger via Sesha
            try:
                signal_type = getattr(signal, "signal_type", "unknown")
                source = getattr(signal, "source_agent", "unknown")

                # Sesha audit (side channel)
                if hasattr(self._sesha, "_ledger") and self._sesha._ledger:
                    self._sesha._ledger.record_event(
                        event_type="NAGA_SIGNAL_WATCH",
                        agent_id="naga_watcher",
                        details={
                            "signal_type": str(signal_type),
                            "source": source,
                            "priority": getattr(signal, "priority", 0),
                        },
                    )
            except Exception:
                pass  # Silent fail

    def get_stats(self) -> Dict[str, Any]:
        """Get signal watcher statistics."""
        return {
            "subscribed": self._subscribed,
            "signals_seen": self._signals_seen,
        }


# =============================================================================
# UNIFIED FLOOD MANAGER
# =============================================================================


class NagaFloodManager:
    """
    Unified manager for all NAGA flooding operations.

    Coordinates:
    - EventBus flooding (with safety guards)
    - SignalBus watching (critical signals only)
    - Future: Plugin hooks, CommitResult watching, etc.
    """

    def __init__(
        self,
        sesha: Optional["SeshaService"] = None,
        takshaka: Optional["TakshakaService"] = None,
        enabled: bool = True,
    ):
        self._sesha = sesha
        self._takshaka = takshaka
        self._enabled = enabled

        # Sub-controllers
        self._event_flood = NagaFloodController(sesha, takshaka, enabled)
        self._signal_watch = NagaSignalWatcher(sesha, takshaka)

        self._started = False

    def start(self) -> None:
        """Start all flooding operations."""
        if not self._enabled:
            logger.info("[FLOOD] Manager disabled")
            return

        if self._started:
            return

        logger.info("[FLOOD] 🌊 Starting NAGA Flood Manager")

        # Start EventBus flooding
        self._event_flood.start()

        # Start SignalBus watching
        self._signal_watch.start()

        self._started = True
        logger.info("[FLOOD] 🐍 Organic flooding active")

    def stop(self) -> None:
        """Stop all flooding operations."""
        self._event_flood.stop()
        self._started = False
        logger.info("[FLOOD] Manager stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get unified flood status."""
        return {
            "enabled": self._enabled,
            "started": self._started,
            "event_flood": self._event_flood.get_stats(),
            "signal_watch": self._signal_watch.get_stats(),
        }
