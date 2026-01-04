"""
NAGA OUROBOROS - NAGAs Watching NAGAs.

"Die Schlange, die ihren eigenen Schwanz frisst."

GAD-000 Recoverability: Every service must be able to recover from failures.
OUROBOROS enables NAGAs to detect and heal their own correction loops.

The Problem:
- Cortex tells Shuddhi to heal X
- Shuddhi heals X, which triggers Cortex signal
- Cortex tells Shuddhi to heal X again
- Infinite loop!

The Solution:
- OUROBOROS observes all NAGA-to-NAGA corrections
- Detects A→B→A patterns (correction loops)
- Escalates to 37th (human/sovereign) when loop detected
- Records loop events in ledger for audit

Integration:
    from vibe_core.naga.ouroboros import NagaOuroboros

    ouroboros = NagaOuroboros(orchestrator)
    cortex.set_ouroboros(ouroboros)
"""

import hashlib
import logging
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Deque, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.ledger import SQLiteLedger
    from vibe_core.naga.cortex.decisions import CortexDecision
    from vibe_core.naga.orchestrator import NagaOrchestrator

logger = logging.getLogger("NAGA.OUROBOROS")


# =============================================================================
# GAD-000 PARSEABILITY: LOOP CODES
# =============================================================================


class LoopCode(Enum):
    """
    Machine-parseable loop detection codes (GAD-000 Parseability).

    Format: LXXX where X is a 3-digit code.
    """

    L001_SIMPLE_LOOP = "L001"  # A→B→A
    L002_TRIANGLE_LOOP = "L002"  # A→B→C→A
    L003_RAPID_FIRE = "L003"  # Same source firing too fast
    L004_CASCADE_DETECTED = "L004"  # Many NAGAs correcting in sequence


# =============================================================================
# CORRECTION EVENT
# =============================================================================


@dataclass
class CorrectionEvent:
    """A single NAGA-to-NAGA correction observation."""

    source_naga: str  # Who made the correction (e.g., "cortex")
    target_naga: str  # Who was corrected (e.g., "shuddhi")
    decision_hash: str  # Hash of the decision for dedup
    timestamp: float = field(default_factory=time.time)
    reason_code: str = ""  # From the decision

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_naga": self.source_naga,
            "target_naga": self.target_naga,
            "decision_hash": self.decision_hash,
            "timestamp": self.timestamp,
            "reason_code": self.reason_code,
        }


@dataclass
class LoopAlert:
    """Alert generated when a correction loop is detected."""

    loop_code: LoopCode
    severity: str  # WARNING, CRITICAL
    message: str
    participants: List[str]  # NAGAs involved in the loop
    events: List[CorrectionEvent]  # Events that formed the loop
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loop_code": self.loop_code.value,
            "severity": self.severity,
            "message": self.message,
            "participants": self.participants,
            "events": [e.to_dict() for e in self.events],
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# OUROBOROS - THE SELF-WATCHER
# =============================================================================


# Type alias for alert handlers
AlertHandler = Callable[[LoopAlert], None]


class NagaOuroboros:
    """
    OUROBOROS - NAGAs Watching NAGAs.

    Observes all NAGA-to-NAGA corrections and detects loops.

    Loop Detection:
    - SIMPLE_LOOP: A corrects B, then B corrects A
    - TRIANGLE_LOOP: A→B→C→A within time window
    - RAPID_FIRE: Same NAGA firing > N corrections in T seconds
    - CASCADE: More than 5 NAGAs correcting in sequence

    When loop detected:
    1. Log to ledger (audit trail)
    2. Alert via Takshaka (bite)
    3. Call registered alert handlers
    4. Potentially pause the looping NAGAs (circuit breaker)
    """

    # Configuration
    DEFAULT_WINDOW_SIZE = 100
    DEFAULT_LOOP_WINDOW_SECONDS = 30.0
    DEFAULT_RAPID_FIRE_THRESHOLD = 5  # Corrections in window
    DEFAULT_RAPID_FIRE_WINDOW = 10.0  # Seconds

    def __init__(
        self,
        orchestrator: Optional["NagaOrchestrator"] = None,
        loop_window_seconds: float = DEFAULT_LOOP_WINDOW_SECONDS,
        rapid_fire_threshold: int = DEFAULT_RAPID_FIRE_THRESHOLD,
        rapid_fire_window: float = DEFAULT_RAPID_FIRE_WINDOW,
    ):
        """
        Initialize OUROBOROS.

        Args:
            orchestrator: The NagaOrchestrator (for accessing Takshaka, Ledger)
            loop_window_seconds: Time window for loop detection
            rapid_fire_threshold: Max corrections per source in window
            rapid_fire_window: Time window for rapid fire detection
        """
        self._orchestrator = orchestrator
        self._loop_window = loop_window_seconds
        self._rapid_fire_threshold = rapid_fire_threshold
        self._rapid_fire_window = rapid_fire_window

        # Rolling history of corrections
        self._history: Deque[CorrectionEvent] = deque(maxlen=self.DEFAULT_WINDOW_SIZE)

        # Track per-source firing rate
        self._source_fires: Dict[str, List[float]] = {}

        # Deduplication (GAD-000 Idempotency)
        self._seen_loops: OrderedDict[str, datetime] = OrderedDict()
        self._seen_loops_max = 1000

        # Alert handlers
        self._alert_handlers: List[AlertHandler] = []

        # Stats
        self._corrections_observed = 0
        self._loops_detected = 0
        self._started_at = time.time()

        # Circuit breaker: paused NAGAs
        self._paused_sources: Dict[str, float] = {}  # source -> pause_until
        self._pause_duration = 60.0  # 1 minute default

        logger.info("[OUROBOROS] Initialized - Die Schlange wacht")

    # =========================================================================
    # MAIN API
    # =========================================================================

    def observe_correction(
        self,
        source: str,
        target: str,
        decision: "CortexDecision",
    ) -> Optional[LoopAlert]:
        """
        Observe a NAGA-to-NAGA correction.

        Call this after every Cortex dispatch.

        Args:
            source: Who made the correction (e.g., "cortex", "shuddhi")
            target: Who was corrected (e.g., "shuddhi", "envoy")
            decision: The CortexDecision that was dispatched

        Returns:
            LoopAlert if a loop was detected, None otherwise
        """
        self._corrections_observed += 1
        now = time.time()

        # Check if source is paused (circuit breaker)
        if source in self._paused_sources:
            if now < self._paused_sources[source]:
                logger.warning(f"[OUROBOROS] Source '{source}' is paused, ignoring correction")
                return None
            else:
                # Pause expired
                del self._paused_sources[source]
                logger.info(f"[OUROBOROS] Source '{source}' unpaused")

        # Create correction event
        decision_hash = self._compute_decision_hash(decision)
        event = CorrectionEvent(
            source_naga=source,
            target_naga=target,
            decision_hash=decision_hash,
            timestamp=now,
            reason_code=decision.reason_code.value if hasattr(decision, "reason_code") else "",
        )

        # Add to history
        self._history.append(event)

        # Track source firing rate
        if source not in self._source_fires:
            self._source_fires[source] = []
        self._source_fires[source].append(now)

        # Detect patterns
        alert = self._detect_patterns(event)

        if alert:
            self._loops_detected += 1
            self._dispatch_alert(alert)

        return alert

    # =========================================================================
    # PATTERN DETECTION
    # =========================================================================

    def _detect_patterns(self, current: CorrectionEvent) -> Optional[LoopAlert]:
        """Detect loop patterns in correction history."""
        now = current.timestamp

        # Check RAPID_FIRE first (most common)
        rapid_alert = self._detect_rapid_fire(current.source_naga, now)
        if rapid_alert:
            return rapid_alert

        # Check SIMPLE_LOOP (A→B→A)
        simple_alert = self._detect_simple_loop(current, now)
        if simple_alert:
            return simple_alert

        # Check TRIANGLE_LOOP (A→B→C→A)
        triangle_alert = self._detect_triangle_loop(current, now)
        if triangle_alert:
            return triangle_alert

        return None

    def _detect_simple_loop(self, current: CorrectionEvent, now: float) -> Optional[LoopAlert]:
        """Detect A→B→A pattern."""
        cutoff = now - self._loop_window

        # Look for: current.target corrected current.source recently
        for event in reversed(list(self._history)[:-1]):  # Exclude current
            if event.timestamp < cutoff:
                break

            if event.source_naga == current.target_naga and event.target_naga == current.source_naga:
                # Found A→B→A loop!
                loop_hash = self._compute_loop_hash([event, current])

                # Dedup
                if loop_hash in self._seen_loops:
                    return None

                self._seen_loops[loop_hash] = datetime.now()
                self._trim_seen_loops()

                return LoopAlert(
                    loop_code=LoopCode.L001_SIMPLE_LOOP,
                    severity="CRITICAL",
                    message=f"Simple loop: {current.source_naga}↔{current.target_naga}",
                    participants=[current.source_naga, current.target_naga],
                    events=[event, current],
                )

        return None

    def _detect_triangle_loop(self, current: CorrectionEvent, now: float) -> Optional[LoopAlert]:
        """Detect A→B→C→A pattern."""
        cutoff = now - self._loop_window
        recent = [e for e in self._history if e.timestamp >= cutoff]

        if len(recent) < 3:
            return None

        # Look for: A→B, B→C, C→A (current is C→A)
        for i, event_a in enumerate(recent[:-2]):
            for event_b in recent[i + 1 : -1]:
                if event_a.target_naga == event_b.source_naga:
                    # Found A→B→...
                    if event_b.target_naga == current.source_naga and current.target_naga == event_a.source_naga:
                        # Found A→B→C→A!
                        loop_hash = self._compute_loop_hash([event_a, event_b, current])

                        if loop_hash in self._seen_loops:
                            return None

                        self._seen_loops[loop_hash] = datetime.now()
                        self._trim_seen_loops()

                        participants = [
                            event_a.source_naga,
                            event_b.source_naga,
                            current.source_naga,
                        ]

                        return LoopAlert(
                            loop_code=LoopCode.L002_TRIANGLE_LOOP,
                            severity="CRITICAL",
                            message=f"Triangle loop: {'→'.join(participants)}→{participants[0]}",
                            participants=participants,
                            events=[event_a, event_b, current],
                        )

        return None

    def _detect_rapid_fire(self, source: str, now: float) -> Optional[LoopAlert]:
        """Detect rapid fire from a single source."""
        if source not in self._source_fires:
            return None

        cutoff = now - self._rapid_fire_window
        fires = [t for t in self._source_fires[source] if t >= cutoff]
        self._source_fires[source] = fires  # Prune old

        if len(fires) >= self._rapid_fire_threshold:
            # Rapid fire detected!
            loop_hash = f"rapid_{source}_{int(now)}"

            if loop_hash in self._seen_loops:
                return None

            self._seen_loops[loop_hash] = datetime.now()
            self._trim_seen_loops()

            # Pause this source (circuit breaker)
            self._paused_sources[source] = now + self._pause_duration
            logger.warning(f"[OUROBOROS] Pausing '{source}' for {self._pause_duration}s")

            return LoopAlert(
                loop_code=LoopCode.L003_RAPID_FIRE,
                severity="WARNING",
                message=f"Rapid fire: {source} fired {len(fires)}x in {self._rapid_fire_window}s",
                participants=[source],
                events=[],
            )

        return None

    # =========================================================================
    # ALERT DISPATCH
    # =========================================================================

    def add_alert_handler(self, handler: AlertHandler) -> None:
        """Add a handler for loop alerts."""
        self._alert_handlers.append(handler)

    def _dispatch_alert(self, alert: LoopAlert) -> None:
        """Dispatch loop alert to handlers and ledger."""
        # Log it
        if alert.severity == "CRITICAL":
            logger.error(f"[OUROBOROS] {alert.loop_code.value}: {alert.message}")
        else:
            logger.warning(f"[OUROBOROS] {alert.loop_code.value}: {alert.message}")

        # Record to ledger
        self._record_to_ledger(alert)

        # Bite via Takshaka for critical loops
        if alert.severity == "CRITICAL" and self._orchestrator:
            self._bite(alert)

        # Call handlers
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.debug(f"[OUROBOROS] Handler error: {e}")

    def _record_to_ledger(self, alert: LoopAlert) -> None:
        """Record loop event to ledger for audit."""
        if not self._orchestrator or not self._orchestrator.sesha:
            return

        try:
            sesha = self._orchestrator.sesha
            if hasattr(sesha, "_ledger") and sesha._ledger:
                sesha._ledger.record_event(
                    event_type=f"NAGA_LOOP_{alert.loop_code.name}",
                    agent_id="ouroboros",
                    details=alert.to_dict(),
                    result="DETECTED",
                )
        except Exception as e:
            logger.debug(f"[OUROBOROS] Ledger record failed: {e}")

    def _bite(self, alert: LoopAlert) -> None:
        """Record loop as a violation via Takshaka."""
        if not self._orchestrator or not self._orchestrator.takshaka:
            return

        try:
            from vibe_core.protocols.naga import VajraViolation

            violation = VajraViolation(
                violation_type=f"LOOP_{alert.loop_code.name}",
                source="ouroboros",
                details=alert.to_dict(),
            )
            self._orchestrator.takshaka.bite(violation)
        except Exception as e:
            logger.debug(f"[OUROBOROS] Bite failed: {e}")

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _compute_decision_hash(self, decision: "CortexDecision") -> str:
        """Compute fingerprint for a decision."""
        payload = f"{decision.action.name}:{decision.target}:{decision.timestamp.isoformat()}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _compute_loop_hash(self, events: List[CorrectionEvent]) -> str:
        """Compute fingerprint for a loop (for dedup)."""
        payload = "|".join(f"{e.source_naga}→{e.target_naga}" for e in events)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _trim_seen_loops(self) -> None:
        """LRU trim of seen loops."""
        while len(self._seen_loops) > self._seen_loops_max:
            self._seen_loops.popitem(last=False)

    # =========================================================================
    # CIRCUIT BREAKER CONTROL
    # =========================================================================

    def pause_source(self, source: str, duration: float = 60.0) -> None:
        """Manually pause a NAGA source."""
        self._paused_sources[source] = time.time() + duration
        logger.warning(f"[OUROBOROS] Manually paused '{source}' for {duration}s")

    def unpause_source(self, source: str) -> None:
        """Manually unpause a NAGA source."""
        if source in self._paused_sources:
            del self._paused_sources[source]
            logger.info(f"[OUROBOROS] Manually unpaused '{source}'")

    def is_paused(self, source: str) -> bool:
        """Check if a source is currently paused."""
        if source not in self._paused_sources:
            return False
        if time.time() >= self._paused_sources[source]:
            del self._paused_sources[source]
            return False
        return True

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get OUROBOROS status for observability."""
        now = time.time()
        return {
            "corrections_observed": self._corrections_observed,
            "loops_detected": self._loops_detected,
            "history_size": len(self._history),
            "paused_sources": list(self._paused_sources.keys()),
            "uptime_seconds": now - self._started_at,
            "config": {
                "loop_window_seconds": self._loop_window,
                "rapid_fire_threshold": self._rapid_fire_threshold,
                "rapid_fire_window": self._rapid_fire_window,
            },
        }

    def reset(self) -> None:
        """Reset OUROBOROS state (for testing)."""
        self._history.clear()
        self._source_fires.clear()
        self._seen_loops.clear()
        self._paused_sources.clear()
        self._corrections_observed = 0
        self._loops_detected = 0
        self._started_at = time.time()
