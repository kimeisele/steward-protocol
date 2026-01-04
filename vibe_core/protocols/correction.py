"""
OPUS-LZ2: CorrectionDispatcher Protocol - Unified Drift Detection & Healing.

The Missing Link: Unifies 4 drift detection systems and 3 healing systems
under a single dispatch mechanism.

EXISTING SYSTEMS (Before):
    OS-Level:
    ├── ReactorProtocol.detect_drift() → DriftEvent (performance)
    ├── VajraEnforcer.detect_drift() → bool (config)
    └── ShuddhiEngine.heal_all_violations() → ShuddhiResult (structural)

    Plugin-Level:
    ├── DriftDetector.detect() → DriftReport (code-doc)
    └── dharma.check_drift_for_chat() → str (cognitive)

NEW ARCHITECTURE (After):
    ┌─────────────────────────────────────────────────┐
    │  DriftRegistry (unified detection)              │
    │  ├── register_detector(source, detector)        │
    │  └── detect_all() → List[UnifiedDriftReport]    │
    │                                                 │
    │         ↓ all return UnifiedDriftReport         │
    │                                                 │
    │  CorrectionDispatcher (unified healing)         │
    │  ├── register_handler(source, handler)          │
    │  ├── dispatch(drift) → HealingResult            │
    │  └── dispatch_all() → List[HealingResult]       │
    │                                                 │
    │         ↓ all return HealingResult              │
    │                                                 │
    │  Knowledge Graph (unified feedback)             │
    └─────────────────────────────────────────────────┘

Usage:
    # Via ServiceRegistry
    dispatcher = ServiceRegistry.get(CorrectionDispatcherProtocol)

    # Detect all drift
    drifts = dispatcher.detect_all()

    # Dispatch corrections
    for drift in drifts:
        result = dispatcher.dispatch(drift)
        if result.healed:
            kg.record_healing(result)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

# =============================================================================
# Enums: Unified taxonomy across all drift/healing systems
# =============================================================================


class DriftSource(str, Enum):
    """Source/category of drift detection."""

    PERFORMANCE = "performance"  # ReactorProtocol - execution metrics
    RELIABILITY = "reliability"  # ReactorProtocol - failure rates
    CONFIG = "config"  # VajraEnforcer - manifest mismatches
    STRUCTURAL = "structural"  # Shuddhi - code violations
    CODE_DOC = "code_doc"  # DriftDetector - code-documentation sync
    COGNITIVE = "cognitive"  # dharma - agent behavior patterns
    STATE = "state"  # GunaClassifier - state health


class DriftSeverity(str, Enum):
    """Unified severity levels."""

    INFO = "info"  # Observation only
    WARNING = "warning"  # Attention needed
    ERROR = "error"  # Correction required
    CRITICAL = "critical"  # Immediate action


class HealingStrategy(str, Enum):
    """How correction should be applied."""

    AUTO = "auto"  # Apply immediately (dry_run=False)
    DRY_RUN = "dry_run"  # Compute but don't apply
    MANUAL = "manual"  # Requires human approval
    CIRCUIT = "circuit"  # Delegate to healing circuit


class HealingStatus(str, Enum):
    """Outcome of healing attempt."""

    HEALED = "healed"  # Successfully corrected
    SKIPPED = "skipped"  # No action needed
    FAILED = "failed"  # Correction failed
    DEFERRED = "deferred"  # Queued for later
    MANUAL_REQUIRED = "manual_required"  # Needs human


# =============================================================================
# Data Classes: Unified report formats
# =============================================================================


@dataclass
class UnifiedDriftReport:
    """
    Unified drift report - the common format all detectors produce.

    Adapters convert from legacy formats:
        DriftEvent (reactor) → UnifiedDriftReport
        bool (vajra) → UnifiedDriftReport
        DriftReport (opus) → UnifiedDriftReport
    """

    id: str
    source: DriftSource
    severity: DriftSeverity
    message: str
    detected_at: datetime = field(default_factory=datetime.now)

    # Location context
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    component: Optional[str] = None  # Agent/plugin/cartridge ID

    # Detection metadata
    detector_id: str = ""  # Which detector found this
    rule_id: Optional[str] = None  # For structural violations
    baseline_value: Optional[float] = None  # For metrics drift
    current_value: Optional[float] = None

    # Healing hints
    suggested_handler: Optional[str] = None  # Preferred handler
    auto_healable: bool = False  # Safe for AUTO strategy
    requires_approval: bool = False  # Needs human sign-off

    # Raw data from original detector
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/storage."""
        return {
            "id": self.id,
            "source": self.source.value,
            "severity": self.severity.value,
            "message": self.message,
            "detected_at": self.detected_at.isoformat(),
            "file_path": str(self.file_path) if self.file_path else None,
            "component": self.component,
            "detector_id": self.detector_id,
            "rule_id": self.rule_id,
            "auto_healable": self.auto_healable,
        }


@dataclass
class HealingResult:
    """
    Unified healing result - the common format all handlers produce.

    Adapters convert from legacy formats:
        ShuddhiResult → HealingResult
        bool (reactor) → HealingResult
    """

    drift_id: str  # Links back to UnifiedDriftReport.id
    status: HealingStatus
    handler_id: str  # Which handler processed this
    message: str = ""
    healed_at: Optional[datetime] = None

    # Change tracking
    files_modified: List[Path] = field(default_factory=list)
    diff: Optional[str] = None

    # Verification
    verified: bool = False
    verification_message: str = ""

    # Metadata
    duration_ms: float = 0.0
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def healed(self) -> bool:
        """True if correction was successful."""
        return self.status == HealingStatus.HEALED

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/storage."""
        return {
            "drift_id": self.drift_id,
            "status": self.status.value,
            "handler_id": self.handler_id,
            "message": self.message,
            "healed_at": self.healed_at.isoformat() if self.healed_at else None,
            "files_modified": [str(p) for p in self.files_modified],
            "verified": self.verified,
            "duration_ms": self.duration_ms,
        }


@dataclass
class CorrectionStats:
    """Statistics for CorrectionDispatcher."""

    detectors_registered: int = 0
    handlers_registered: int = 0
    drifts_detected: int = 0
    healings_attempted: int = 0
    healings_succeeded: int = 0
    healings_failed: int = 0
    last_detection_run: Optional[datetime] = None
    last_healing_run: Optional[datetime] = None


# =============================================================================
# Protocol Types
# =============================================================================

# Detector: (source) -> List[UnifiedDriftReport]
DriftDetector = Callable[[], List[UnifiedDriftReport]]

# Handler: (drift, strategy) -> HealingResult
CorrectionHandler = Callable[[UnifiedDriftReport, HealingStrategy], HealingResult]


# =============================================================================
# Main Protocols
# =============================================================================


@runtime_checkable
class DriftRegistryProtocol(Protocol):
    """
    Registry for unified drift detection.

    Collects detectors from different sources and runs them all.
    """

    def register_detector(
        self,
        source: DriftSource,
        detector: DriftDetector,
        detector_id: str = "",
    ) -> None:
        """
        Register a drift detector for a source category.

        Args:
            source: The drift category this detector handles
            detector: Callable that returns list of drift reports
            detector_id: Unique identifier for this detector
        """
        ...

    def unregister_detector(self, detector_id: str) -> bool:
        """Remove a detector by ID."""
        ...

    def detect(self, source: Optional[DriftSource] = None) -> List[UnifiedDriftReport]:
        """
        Run detection for a specific source.

        Args:
            source: Filter to specific source, or None for all

        Returns:
            List of detected drifts
        """
        ...

    def detect_all(self) -> List[UnifiedDriftReport]:
        """Run all registered detectors."""
        ...

    def get_detector_ids(self) -> List[str]:
        """List all registered detector IDs."""
        ...


@runtime_checkable
class CorrectionDispatcherProtocol(Protocol):
    """
    Unified correction dispatcher.

    Routes drifts to appropriate handlers based on source.
    """

    def register_handler(
        self,
        source: DriftSource,
        handler: CorrectionHandler,
        handler_id: str = "",
        priority: int = 0,
    ) -> None:
        """
        Register a correction handler for a drift source.

        Args:
            source: The drift category this handler corrects
            handler: Callable that attempts correction
            handler_id: Unique identifier for this handler
            priority: Higher priority handlers run first (default 0)
        """
        ...

    def unregister_handler(self, handler_id: str) -> bool:
        """Remove a handler by ID."""
        ...

    def dispatch(
        self,
        drift: UnifiedDriftReport,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> HealingResult:
        """
        Dispatch a drift to appropriate handler(s).

        Args:
            drift: The drift report to correct
            strategy: How to apply the correction

        Returns:
            Result of the correction attempt
        """
        ...

    def dispatch_all(
        self,
        drifts: List[UnifiedDriftReport],
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> List[HealingResult]:
        """Dispatch multiple drifts."""
        ...

    def can_heal(self, drift: UnifiedDriftReport) -> bool:
        """Check if a handler exists for this drift source."""
        ...

    def get_handler_ids(self) -> List[str]:
        """List all registered handler IDs."""
        ...

    def get_stats(self) -> CorrectionStats:
        """Get dispatcher statistics."""
        ...


@runtime_checkable
class CorrectionOrchestratorProtocol(Protocol):
    """
    High-level orchestrator combining detection and dispatch.

    This is what biorhythm and other callers should use.
    """

    @property
    def registry(self) -> DriftRegistryProtocol:
        """Access the drift registry."""
        ...

    @property
    def dispatcher(self) -> CorrectionDispatcherProtocol:
        """Access the correction dispatcher."""
        ...

    def detect_and_report(
        self,
        source: Optional[DriftSource] = None,
    ) -> List[UnifiedDriftReport]:
        """
        Run detection and return reports (no healing).

        Use this for observation/reporting.
        """
        ...

    def detect_and_heal(
        self,
        source: Optional[DriftSource] = None,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
        auto_only: bool = True,
    ) -> List[HealingResult]:
        """
        Run detection and dispatch corrections.

        Args:
            source: Filter to specific source, or None for all
            strategy: How to apply corrections
            auto_only: Only heal drifts marked auto_healable

        Returns:
            List of healing results
        """
        ...

    def get_healable_count(self) -> Dict[DriftSource, int]:
        """Get count of healable drifts by source."""
        ...


# =============================================================================
# Null Implementations (Arjuna Pattern)
# =============================================================================


class NullDriftRegistry:
    """No-op drift registry."""

    def register_detector(self, source: DriftSource, detector: DriftDetector, detector_id: str = "") -> None:
        pass

    def unregister_detector(self, detector_id: str) -> bool:
        return False

    def detect(self, source: Optional[DriftSource] = None) -> List[UnifiedDriftReport]:
        return []

    def detect_all(self) -> List[UnifiedDriftReport]:
        return []

    def get_detector_ids(self) -> List[str]:
        return []


class NullCorrectionDispatcher:
    """No-op correction dispatcher."""

    def register_handler(
        self,
        source: DriftSource,
        handler: CorrectionHandler,
        handler_id: str = "",
        priority: int = 0,
    ) -> None:
        pass

    def unregister_handler(self, handler_id: str) -> bool:
        return False

    def dispatch(
        self,
        drift: UnifiedDriftReport,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> HealingResult:
        return HealingResult(
            drift_id=drift.id,
            status=HealingStatus.SKIPPED,
            handler_id="null",
            message="No dispatcher configured",
        )

    def dispatch_all(
        self,
        drifts: List[UnifiedDriftReport],
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> List[HealingResult]:
        return [self.dispatch(d, strategy) for d in drifts]

    def can_heal(self, drift: UnifiedDriftReport) -> bool:
        return False

    def get_handler_ids(self) -> List[str]:
        return []

    def get_stats(self) -> CorrectionStats:
        return CorrectionStats()


# =============================================================================
# Adapter Factories (convert legacy → unified)
# =============================================================================


def adapt_reactor_drift(drift_event: Any) -> UnifiedDriftReport:
    """
    Adapt ReactorProtocol.DriftEvent → UnifiedDriftReport.

    Usage:
        from vibe_core.protocols.reactor import DriftEvent
        unified = adapt_reactor_drift(drift_event)
    """
    from vibe_core.protocols.reactor import DriftType as ReactorDriftType

    # Map reactor drift types to unified sources
    source_map = {
        ReactorDriftType.PERFORMANCE: DriftSource.PERFORMANCE,
        ReactorDriftType.RELIABILITY: DriftSource.RELIABILITY,
        ReactorDriftType.CONFIG: DriftSource.CONFIG,
        ReactorDriftType.STATE: DriftSource.STATE,
        ReactorDriftType.RESOURCE: DriftSource.PERFORMANCE,
        ReactorDriftType.USAGE: DriftSource.COGNITIVE,
    }

    # Map severity
    from vibe_core.protocols.reactor import DriftSeverity as ReactorSeverity

    severity_map = {
        ReactorSeverity.INFO: DriftSeverity.INFO,
        ReactorSeverity.WARNING: DriftSeverity.WARNING,
        ReactorSeverity.ERROR: DriftSeverity.ERROR,
        ReactorSeverity.CRITICAL: DriftSeverity.CRITICAL,
    }

    return UnifiedDriftReport(
        id=drift_event.id,
        source=source_map.get(drift_event.type, DriftSource.PERFORMANCE),
        severity=severity_map.get(drift_event.severity, DriftSeverity.WARNING),
        message=drift_event.message,
        detected_at=drift_event.detected_at,
        detector_id="reactor",
        component=drift_event.source,
        baseline_value=drift_event.data.get("baseline_ms"),
        current_value=drift_event.data.get("current_ms"),
        auto_healable=False,  # Performance drift needs investigation
        raw_data=drift_event.data,
    )


def adapt_shuddhi_result(result: Any, drift_id: str) -> HealingResult:
    """
    Adapt ShuddhiResult → HealingResult.

    Usage:
        from vibe_core.protocols.shuddhi import ShuddhiResult
        unified = adapt_shuddhi_result(shuddhi_result, drift.id)
    """
    from vibe_core.protocols.shuddhi import ShuddhiStatus

    status_map = {
        ShuddhiStatus.PURIFIED: HealingStatus.HEALED,
        ShuddhiStatus.SKIPPED: HealingStatus.SKIPPED,
        ShuddhiStatus.FAILED: HealingStatus.FAILED,
        ShuddhiStatus.OUT_OF_SCOPE: HealingStatus.MANUAL_REQUIRED,
    }

    return HealingResult(
        drift_id=drift_id,
        status=status_map.get(result.status, HealingStatus.FAILED),
        handler_id="shuddhi",
        message=result.message,
        healed_at=datetime.now() if result.success else None,
        files_modified=[result.file_path] if result.success else [],
        diff=result.diff,
        verified=result.success,
    )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Enums
    "DriftSource",
    "DriftSeverity",
    "HealingStrategy",
    "HealingStatus",
    # Data Classes
    "UnifiedDriftReport",
    "HealingResult",
    "CorrectionStats",
    # Protocols
    "DriftRegistryProtocol",
    "CorrectionDispatcherProtocol",
    "CorrectionOrchestratorProtocol",
    # Type Aliases
    "DriftDetector",
    "CorrectionHandler",
    # Null Implementations
    "NullDriftRegistry",
    "NullCorrectionDispatcher",
    # Adapters
    "adapt_reactor_drift",
    "adapt_shuddhi_result",
]
