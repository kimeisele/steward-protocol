"""
CHITRAGUPTA SERVICE - Der Profiler.

Chitragupta - Führt Buch über alle Karmas.

"Er entscheidet mit Yama über Himmel oder Hölle."

Responsibilities:
- Profile component behavior over time
- Calculate baselines (mean, stddev)
- Detect anomalies (deviation from baseline)
- Sign anomaly reports (37th Principle)
"""

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from vibe_core.protocols.naga import NagaStatus, NagaType

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.identity import NagaIdentity

logger = logging.getLogger("CHITRAGUPTA")


@dataclass
class MetricSample:
    """A single metric sample."""

    value: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricHistory:
    """History of samples for a metric."""

    history: List[MetricSample] = field(default_factory=list)

    def add(self, value: float, timestamp: Optional[datetime] = None) -> None:
        self.history.append(MetricSample(value=value, timestamp=timestamp or datetime.now()))

    def values(self, window_seconds: Optional[float] = None) -> List[float]:
        """Get values, optionally filtered by time window."""
        if window_seconds is None:
            return [s.value for s in self.history]

        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        return [s.value for s in self.history if s.timestamp >= cutoff]


@dataclass
class ComponentProfile:
    """Behavioral profile for a component."""

    component_id: str
    metrics: Dict[str, MetricHistory] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def has_baseline(self, metric: str, min_samples: int = 5, window_seconds: Optional[float] = None) -> bool:
        """Check if enough samples for baseline calculation."""
        if metric not in self.metrics:
            return False
        values = self.metrics[metric].values(window_seconds)
        return len(values) >= min_samples

    def get_baseline_mean(self, metric: str, window_seconds: Optional[float] = None) -> float:
        """Calculate baseline mean for metric."""
        values = self.metrics[metric].values(window_seconds)
        if not values:
            return 0.0
        return sum(values) / len(values)

    def get_baseline_stddev(self, metric: str, window_seconds: Optional[float] = None) -> float:
        """Calculate baseline standard deviation for metric."""
        values = self.metrics[metric].values(window_seconds)
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)


@dataclass
class Anomaly:
    """Detected anomaly report."""

    component_id: str
    metric: str
    current_value: float
    expected_range: Optional[Tuple[float, float]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    detector_id: str = ""
    signature: Optional[bytes] = None


@dataclass
class KarmaEntry:
    """Log entry for profiler actions."""

    action: str
    component_id: str
    metric: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ChitraguptaService:
    """
    Chitragupta - The Karma Accountant.

    Profiles component behavior and detects anomalies.
    """

    def __init__(
        self,
        cortex: Optional["NagaCortex"] = None,
        identity: Optional["NagaIdentity"] = None,
        min_samples_for_baseline: int = 5,
        anomaly_threshold_sigma: float = 2.0,
        profile_window_seconds: Optional[float] = None,
    ):
        """
        Initialize Chitragupta.

        Args:
            cortex: NagaCortex for anomaly reporting
            identity: NagaIdentity for signing reports
            min_samples_for_baseline: Minimum samples needed for baseline
            anomaly_threshold_sigma: Standard deviations for anomaly
            profile_window_seconds: Time window for baseline (None = all time)
        """
        self._cortex = cortex
        self._identity = identity
        self._min_samples = min_samples_for_baseline
        self._anomaly_sigma = anomaly_threshold_sigma
        self._window_seconds = profile_window_seconds

        self._profiles: Dict[str, ComponentProfile] = {}
        self._karma_log: List[KarmaEntry] = []

        self._profiles_count = 0
        self._anomalies_detected = 0
        self._last_heartbeat = datetime.now()

        logger.info("🐍 CHITRAGUPTA initialized - The Accountant watches")

    def get_status(self) -> NagaStatus:
        """Get current status."""
        return NagaStatus(
            naga_type=NagaType.CHITRAGUPTA,
            healthy=True,
            events_processed=self._profiles_count,
            errors=self._anomalies_detected,
            last_heartbeat=self._last_heartbeat,
            details={
                "profiles": len(self._profiles),
                "anomalies_detected": self._anomalies_detected,
            },
        )

    def record(self, component_id: str, metric: str, value: float) -> None:
        """
        Record a metric value for a component.

        Args:
            component_id: ID of component
            metric: Metric name (e.g., "latency_ms", "error_rate")
            value: Metric value
        """
        profile = self._get_or_create_profile(component_id)

        if metric not in profile.metrics:
            profile.metrics[metric] = MetricHistory()

        profile.metrics[metric].add(value)
        self._profiles_count += 1
        self._last_heartbeat = datetime.now()

        # Log karma
        self._karma_log.append(
            KarmaEntry(
                action="RECORD_METRIC",
                component_id=component_id,
                metric=metric,
            )
        )

    def get_profile(self, component_id: str) -> Optional[ComponentProfile]:
        """Get profile for component."""
        return self._profiles.get(component_id)

    def detect_anomaly(self, component_id: str) -> Optional[Anomaly]:
        """
        Check if component is behaving anomalously.

        Returns:
            Anomaly if detected, None otherwise
        """
        profile = self._profiles.get(component_id)
        if not profile:
            return None

        for metric, history in profile.metrics.items():
            if not profile.has_baseline(metric, self._min_samples, self._window_seconds):
                continue

            values = history.values(self._window_seconds)
            if not values:
                continue

            current = values[-1]
            mean = profile.get_baseline_mean(metric, self._window_seconds)
            stddev = profile.get_baseline_stddev(metric, self._window_seconds)

            # Avoid division by zero
            if stddev == 0:
                stddev = 0.001

            z_score = abs(current - mean) / stddev

            if z_score > self._anomaly_sigma:
                anomaly = Anomaly(
                    component_id=component_id,
                    metric=metric,
                    current_value=current,
                    expected_range=(
                        mean - self._anomaly_sigma * stddev,
                        mean + self._anomaly_sigma * stddev,
                    ),
                )

                # Sign if identity available
                if self._identity:
                    anomaly.detector_id = self._identity.agent_id
                    anomaly.signature = self._sign_anomaly(anomaly)

                self._anomalies_detected += 1

                # Notify cortex
                if self._cortex:
                    try:
                        self._cortex.receive_chitragupta_anomaly(anomaly)
                    except Exception as e:
                        logger.warning(f"Failed to notify cortex: {e}")

                logger.warning(
                    f"🐍 CHITRAGUPTA detected anomaly: {component_id}.{metric} = {current} "
                    f"(expected {anomaly.expected_range})"
                )

                return anomaly

        return None

    def get_karma_log(self) -> List[KarmaEntry]:
        """Get the karma log of all actions."""
        return list(self._karma_log)

    def _get_or_create_profile(self, component_id: str) -> ComponentProfile:
        """Get or create profile for component."""
        if component_id not in self._profiles:
            self._profiles[component_id] = ComponentProfile(component_id=component_id)
        return self._profiles[component_id]

    def _sign_anomaly(self, anomaly: Anomaly) -> bytes:
        """Sign an anomaly report."""
        if not self._identity:
            return b""

        payload = f"{anomaly.component_id}:{anomaly.metric}:{anomaly.timestamp.isoformat()}"
        return self._identity.sign(payload.encode())

    # =========================================================================
    # CorrectionHandler Interface
    # =========================================================================

    def as_handler(self):
        """Get this NAGA as a CorrectionHandler for DriftSource.PERFORMANCE."""
        from vibe_core.protocols.correction import (
            DriftSource,
            HealingResult,
            HealingStatus,
            HealingStrategy,
            UnifiedDriftReport,
        )

        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            self._last_heartbeat = datetime.now()

            if drift.source != DriftSource.PERFORMANCE:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="chitragupta",
                    message=f"Not a PERFORMANCE drift: {drift.source}",
                )

            # Extract component from drift context
            component_id = drift.context.get("component_id", drift.id)

            if strategy == HealingStrategy.DRY_RUN:
                anomaly = self.detect_anomaly(component_id)
                if anomaly:
                    return HealingResult(
                        drift_id=drift.id,
                        status=HealingStatus.DEFERRED,
                        handler_id="chitragupta",
                        message=f"Detected anomaly in {component_id}: {anomaly.metric} (DRY_RUN)",
                    )
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="chitragupta",
                    message=f"No anomaly detected for {component_id}",
                )

            # Actual anomaly detection and flagging
            try:
                anomaly = self.detect_anomaly(component_id)
                if anomaly:
                    self._anomalies_detected += 1
                    return HealingResult(
                        drift_id=drift.id,
                        status=HealingStatus.HEALED,
                        handler_id="chitragupta",
                        message=f"Flagged anomaly: {component_id}.{anomaly.metric}",
                    )
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="chitragupta",
                    message=f"No anomaly in {component_id}",
                )
            except Exception as e:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.FAILED,
                    handler_id="chitragupta",
                    message=f"Anomaly detection failed: {e}",
                )

        return handler
