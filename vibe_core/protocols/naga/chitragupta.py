"""
CHITRAGUPTA Protocol - Der Profiler (Behavioral Protocol)

Chitragupta - Der Karma-Buchhalter. Führt Buch über alle Taten.
"Er entscheidet mit Yama über Himmel oder Hölle."

Responsibilities:
- Profile component behavior over time
- Calculate baselines (mean, stddev)
- Detect anomalies (deviation from baseline)
- Sign anomaly reports (37th Principle)

Integration:
- Registers as handler for DriftSource.PERFORMANCE
- Detects performance drift via behavioral analysis
- Heals by flagging anomalous components
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Protocol, runtime_checkable

from vibe_core.protocols.correction import (
    CorrectionHandler,
    HealingResult,
    HealingStatus,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga.types import NagaStatus, NagaType


@dataclass
class AnomalyReport:
    """Report of a behavioral anomaly."""

    component_id: str
    metric: str
    current_value: float
    expected_min: float
    expected_max: float
    deviation_sigma: float
    signed_by: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@runtime_checkable
class ChitraguptaProtocol(Protocol):
    """
    Chitragupta - Der Karma-Buchhalter. Führt Buch über alle Taten.

    "Er entscheidet mit Yama über Himmel oder Hölle."

    Responsibilities:
    - Profile component behavior over time
    - Calculate baselines (mean, stddev)
    - Detect anomalies (deviation from baseline)
    - Sign anomaly reports (37th Principle)

    Integration:
    - Registers as handler for DriftSource.PERFORMANCE
    - Detects performance drift via behavioral analysis
    - Heals by flagging anomalous components

    Usage:
        chitragupta = ServiceRegistry.get(ChitraguptaProtocol)
        chitragupta.record(component_id, "latency_ms", 45.2)
        anomaly = chitragupta.detect_anomaly(component_id)
    """

    def record(self, component_id: str, metric: str, value: float) -> None:
        """Record a metric value for a component."""
        ...

    def detect_anomaly(self, component_id: str) -> Optional[AnomalyReport]:
        """Check if component is behaving anomalously."""
        ...

    def get_baseline_mean(self, component_id: str, metric: str) -> float:
        """Get baseline mean for a metric."""
        ...

    def get_baseline_stddev(self, component_id: str, metric: str) -> float:
        """Get baseline standard deviation for a metric."""
        ...

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.PERFORMANCE."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullChitragupta:
    """No-op Chitragupta for when profiling is unavailable."""

    def record(self, component_id: str, metric: str, value: float) -> None:
        pass

    def detect_anomaly(self, component_id: str) -> Optional[AnomalyReport]:
        return None

    def get_baseline_mean(self, component_id: str, metric: str) -> float:
        return 0.0

    def get_baseline_stddev(self, component_id: str, metric: str) -> float:
        return 0.0

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: Any) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_chitragupta",
                message="Chitragupta not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.CHITRAGUPTA, healthy=False, message="Not initialized")
