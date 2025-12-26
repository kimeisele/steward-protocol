"""
OPUS-311 Sprint 4: Reactor Protocol

The Prajna (Awareness) that detects drift and triggers correction.

Drift detection for self-healing. Closes the loop:
Intent → Match → Execute → Feedback → Reflection → [Reactor] → Improvement

Usage:
    # Via ServiceRegistry
    reactor: ReactorProtocol = ServiceRegistry.get(ReactorProtocol) or NullReactor()

    # Check for drift
    drift = reactor.detect_drift()
    if drift:
        reactor.trigger_correction(drift)

    # Register drift handlers
    reactor.on_drift(DriftType.PERFORMANCE, handle_slow_command)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable


class DriftType(str, Enum):
    """Types of system drift."""

    PERFORMANCE = "performance"  # Commands getting slower
    RELIABILITY = "reliability"  # Failure rate increasing
    USAGE = "usage"  # Usage patterns changing
    CONFIG = "config"  # Configuration mismatch
    STATE = "state"  # State inconsistency
    RESOURCE = "resource"  # Resource exhaustion


class DriftSeverity(str, Enum):
    """Severity of detected drift."""

    INFO = "info"  # Minor drift, just logging
    WARNING = "warning"  # Significant drift, may need attention
    ERROR = "error"  # Critical drift, needs correction
    CRITICAL = "critical"  # System unstable, immediate action


@dataclass
class DriftEvent:
    """A detected drift event."""

    id: str
    type: DriftType
    severity: DriftSeverity
    message: str
    detected_at: datetime = field(default_factory=datetime.now)
    source: str = ""  # What component detected it
    data: Dict[str, Any] = field(default_factory=dict)
    corrected: bool = False
    corrected_at: Optional[datetime] = None


@dataclass
class DriftMetrics:
    """Metrics for drift detection."""

    baseline_duration_ms: float = 0.0
    current_duration_ms: float = 0.0
    baseline_failure_rate: float = 0.0
    current_failure_rate: float = 0.0
    sample_size: int = 0


@dataclass
class ReactorStats:
    """Statistics about reactor activity."""

    drift_events_detected: int = 0
    drift_events_corrected: int = 0
    handlers_registered: int = 0
    last_check: Optional[datetime] = None
    active_drifts: List[str] = field(default_factory=list)


# Type alias for drift handlers
DriftHandler = Callable[[DriftEvent], bool]


@runtime_checkable
class ReactorProtocol(Protocol):
    """
    OPUS-311: Drift detection and self-healing.

    The Prajna - "transcendent wisdom" that observes and corrects.

    Features:
    - Detect drift from baseline behavior
    - Trigger correction actions
    - Feed drift events to Reflection
    - Self-healing through Autonomy Loop
    """

    def detect_drift(self) -> List[DriftEvent]:
        """
        Detect current drift from baseline.

        Analyzes recent execution data against historical baseline.

        Returns:
            List of detected drift events
        """
        ...

    def check_drift(
        self,
        drift_type: Optional[DriftType] = None,
    ) -> Optional[DriftEvent]:
        """
        Check for specific type of drift.

        Args:
            drift_type: Optional filter by drift type

        Returns:
            Most significant drift event or None
        """
        ...

    def trigger_correction(self, drift: DriftEvent) -> bool:
        """
        Trigger correction for detected drift.

        Calls registered handlers and feeds to Reflection.

        Returns:
            True if correction was attempted
        """
        ...

    def on_drift(
        self,
        drift_type: DriftType,
        handler: DriftHandler,
    ) -> None:
        """
        Register a handler for drift type.

        Handler is called when drift is detected.
        Handler returns True if it handled the drift.
        """
        ...

    def remove_handler(
        self,
        drift_type: DriftType,
        handler: DriftHandler,
    ) -> bool:
        """Remove a drift handler."""
        ...

    def set_baseline(
        self,
        command: str,
        metrics: DriftMetrics,
    ) -> None:
        """
        Set baseline metrics for a command.

        Used for drift detection.
        """
        ...

    def update_metrics(
        self,
        command: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        """
        Update current metrics for a command.

        Called after each execution.
        """
        ...

    def get_metrics(
        self,
        command: Optional[str] = None,
    ) -> Dict[str, DriftMetrics]:
        """Get current metrics (optionally filtered by command)."""
        ...

    def get_active_drifts(self) -> List[DriftEvent]:
        """Get all uncorrected drift events."""
        ...

    def get_stats(self) -> ReactorStats:
        """Get reactor statistics."""
        ...


class NullReactor:
    """
    Arjuna Pattern: No-op reactor.

    No drift detection, no self-healing.
    Use when reactor service is not available.
    """

    def detect_drift(self) -> List[DriftEvent]:
        return []

    def check_drift(
        self,
        drift_type: Optional[DriftType] = None,
    ) -> Optional[DriftEvent]:
        return None

    def trigger_correction(self, drift: DriftEvent) -> bool:
        return False

    def on_drift(
        self,
        drift_type: DriftType,
        handler: DriftHandler,
    ) -> None:
        pass

    def remove_handler(
        self,
        drift_type: DriftType,
        handler: DriftHandler,
    ) -> bool:
        return False

    def set_baseline(
        self,
        command: str,
        metrics: DriftMetrics,
    ) -> None:
        pass

    def update_metrics(
        self,
        command: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        pass

    def get_metrics(
        self,
        command: Optional[str] = None,
    ) -> Dict[str, DriftMetrics]:
        return {}

    def get_active_drifts(self) -> List[DriftEvent]:
        return []

    def get_stats(self) -> ReactorStats:
        return ReactorStats()


class BasicReactor:
    """
    OPUS-311: Basic implementation of ReactorProtocol.

    In-memory drift detection with configurable thresholds.
    """

    # Thresholds for drift detection
    PERFORMANCE_DRIFT_RATIO = 1.5  # >50% slower than baseline
    RELIABILITY_DRIFT_THRESHOLD = 0.2  # >20% increase in failure rate
    MIN_SAMPLES = 10  # Need at least 10 executions for baseline
    WINDOW_SIZE = 100  # Rolling window for current metrics

    def __init__(self):
        import uuid

        self._uuid = uuid.uuid4
        self._baselines: Dict[str, DriftMetrics] = {}
        self._current: Dict[str, List[tuple]] = {}  # command -> [(duration, success, timestamp)]
        self._handlers: Dict[DriftType, List[DriftHandler]] = {}
        self._drift_events: Dict[str, DriftEvent] = {}
        self._stats = ReactorStats()

    def detect_drift(self) -> List[DriftEvent]:
        drifts = []
        self._stats.last_check = datetime.now()

        for command, samples in self._current.items():
            if len(samples) < self.MIN_SAMPLES:
                continue

            # Get baseline (or compute from first half)
            baseline = self._baselines.get(command)
            if not baseline:
                # Auto-baseline from first half of samples
                half = len(samples) // 2
                baseline = self._compute_metrics(samples[:half])
                self._baselines[command] = baseline

            # Compute current metrics from recent samples
            current = self._compute_metrics(samples[-self.WINDOW_SIZE :])

            # Check for performance drift
            if baseline.baseline_duration_ms > 0:
                ratio = current.current_duration_ms / baseline.baseline_duration_ms
                if ratio > self.PERFORMANCE_DRIFT_RATIO:
                    drift = DriftEvent(
                        id=str(self._uuid()),
                        type=DriftType.PERFORMANCE,
                        severity=DriftSeverity.WARNING if ratio < 2.0 else DriftSeverity.ERROR,
                        message=f"Command '{command}' is {ratio:.1f}x slower than baseline",
                        source="BasicReactor",
                        data={
                            "command": command,
                            "baseline_ms": baseline.baseline_duration_ms,
                            "current_ms": current.current_duration_ms,
                            "ratio": ratio,
                        },
                    )
                    drifts.append(drift)
                    self._drift_events[drift.id] = drift

            # Check for reliability drift
            failure_increase = current.current_failure_rate - baseline.baseline_failure_rate
            if failure_increase > self.RELIABILITY_DRIFT_THRESHOLD:
                drift = DriftEvent(
                    id=str(self._uuid()),
                    type=DriftType.RELIABILITY,
                    severity=DriftSeverity.WARNING if failure_increase < 0.4 else DriftSeverity.ERROR,
                    message=f"Command '{command}' failure rate increased by {failure_increase:.0%}",
                    source="BasicReactor",
                    data={
                        "command": command,
                        "baseline_rate": baseline.baseline_failure_rate,
                        "current_rate": current.current_failure_rate,
                        "increase": failure_increase,
                    },
                )
                drifts.append(drift)
                self._drift_events[drift.id] = drift

        self._stats.drift_events_detected += len(drifts)
        self._stats.active_drifts = [d.id for d in self._drift_events.values() if not d.corrected]

        return drifts

    def _compute_metrics(self, samples: List[tuple]) -> DriftMetrics:
        """Compute metrics from samples."""
        if not samples:
            return DriftMetrics()

        durations = [s[0] for s in samples]
        successes = [s[1] for s in samples]

        avg_duration = sum(durations) / len(durations)
        failure_rate = 1.0 - (sum(successes) / len(successes))

        return DriftMetrics(
            baseline_duration_ms=avg_duration,
            current_duration_ms=avg_duration,
            baseline_failure_rate=failure_rate,
            current_failure_rate=failure_rate,
            sample_size=len(samples),
        )

    def check_drift(
        self,
        drift_type: Optional[DriftType] = None,
    ) -> Optional[DriftEvent]:
        # Get active drifts
        active = [d for d in self._drift_events.values() if not d.corrected]

        if drift_type:
            active = [d for d in active if d.type == drift_type]

        if not active:
            return None

        # Return most severe
        severity_order = {
            DriftSeverity.CRITICAL: 0,
            DriftSeverity.ERROR: 1,
            DriftSeverity.WARNING: 2,
            DriftSeverity.INFO: 3,
        }
        return min(active, key=lambda d: severity_order.get(d.severity, 4))

    def trigger_correction(self, drift: DriftEvent) -> bool:
        # Call registered handlers
        handlers = self._handlers.get(drift.type, [])

        corrected = False
        for handler in handlers:
            try:
                if handler(drift):
                    corrected = True
                    break
            except Exception:
                pass

        if corrected:
            drift.corrected = True
            drift.corrected_at = datetime.now()
            self._stats.drift_events_corrected += 1

        return corrected

    def on_drift(
        self,
        drift_type: DriftType,
        handler: DriftHandler,
    ) -> None:
        if drift_type not in self._handlers:
            self._handlers[drift_type] = []
        self._handlers[drift_type].append(handler)
        self._stats.handlers_registered = sum(len(h) for h in self._handlers.values())

    def remove_handler(
        self,
        drift_type: DriftType,
        handler: DriftHandler,
    ) -> bool:
        handlers = self._handlers.get(drift_type, [])
        if handler in handlers:
            handlers.remove(handler)
            self._stats.handlers_registered = sum(len(h) for h in self._handlers.values())
            return True
        return False

    def set_baseline(
        self,
        command: str,
        metrics: DriftMetrics,
    ) -> None:
        self._baselines[command] = metrics

    def update_metrics(
        self,
        command: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        if command not in self._current:
            self._current[command] = []

        self._current[command].append((duration_ms, success, datetime.now()))

        # Trim to window size
        if len(self._current[command]) > self.WINDOW_SIZE * 2:
            self._current[command] = self._current[command][-self.WINDOW_SIZE * 2 :]

    def get_metrics(
        self,
        command: Optional[str] = None,
    ) -> Dict[str, DriftMetrics]:
        result = {}

        commands = [command] if command else list(self._current.keys())

        for cmd in commands:
            samples = self._current.get(cmd, [])
            if samples:
                result[cmd] = self._compute_metrics(samples)

        return result

    def get_active_drifts(self) -> List[DriftEvent]:
        return [d for d in self._drift_events.values() if not d.corrected]

    def get_stats(self) -> ReactorStats:
        self._stats.active_drifts = [d.id for d in self._drift_events.values() if not d.corrected]
        return self._stats


def get_reactor_safe() -> ReactorProtocol:
    """
    Get Reactor via ServiceRegistry with NullReactor fallback.

    OPUS-311: Use this for guaranteed non-None return.
    """
    try:
        from vibe_core.di import ServiceRegistry

        reactor = ServiceRegistry.get(ReactorProtocol)
        if reactor is not None:
            return reactor
    except ImportError:
        pass

    return NullReactor()
