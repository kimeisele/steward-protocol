"""
CORRECTION DISPATCHER - Unified Drift Detection & Healing
=========================================================

OWNER: YAMARAJA (The Judge)
POSITION: 15 (MOKSHA Quarter)
OPCODE: RESET_IP (Final Reset/Judgment)

Yamaraja JUDGES all drift and CORRECTS through healing.
This is the JUDICIAL function - detecting deviation and restoring dharma.

YAMARAJA'S ROLE IN CORRECTION:
1. DETECT - Find all deviations from dharma (drift)
2. JUDGE - Determine severity and appropriate response
3. CORRECT - Apply healing or defer to higher authority
4. VERIFY - Confirm correction succeeded

THE AJAMIL EXCEPTION IN CORRECTION:
Even if code has FAILED all tests and has maximum drift,
if it CHANTS (is_chanting=True), MERCY overrides judgment.
The Holy Name transcends all corrections.

ARCHITECTURE:
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

ORIGINAL: protocols/correction.py
MIGRATED: protocols/mahajanas/yamaraja/correction.py
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xa49e7c55"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable, Final

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# OWNERSHIP DECLARATION - Yamaraja OWN this protocol
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.YAMARAJA
LOTUS_POSITION: Final[int] = 15  # MOKSHA Quarter, Worker 3
LOTUS_QUARTER: Final[str] = "moksha"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.AUDIT_SEAL,  # Final Reset/Judgment
]


# =============================================================================
# Enums: Unified taxonomy across all drift/healing systems
# =============================================================================


class DriftSource(str, Enum):
    """Source/category of drift detection - Yamaraja's jurisdiction."""

    PERFORMANCE = "performance"  # ReactorProtocol - execution metrics
    RELIABILITY = "reliability"  # ReactorProtocol - failure rates
    CONFIG = "config"  # VajraEnforcer - manifest mismatches
    STRUCTURAL = "structural"  # Shuddhi - code violations
    CODE_DOC = "code_doc"  # DriftDetector - code-documentation sync
    COGNITIVE = "cognitive"  # dharma - agent behavior patterns
    STATE = "state"  # GunaClassifier - state health


class DriftSeverity(str, Enum):
    """Yamaraja's severity classification."""

    INFO = "info"  # Observation only
    WARNING = "warning"  # Attention needed
    ERROR = "error"  # Correction required
    CRITICAL = "critical"  # Immediate action


class HealingStrategy(str, Enum):
    """How Yamaraja should apply correction."""

    AUTO = "auto"  # Apply immediately (earned trust)
    DRY_RUN = "dry_run"  # Compute but don't apply (default)
    MANUAL = "manual"  # Requires human approval
    CIRCUIT = "circuit"  # Delegate to healing circuit
    RESONANCE = "resonance"  # Use Quantum Reactor to determine
    MERCY = "mercy"  # AJAMIL EXCEPTION - chanting overrides


class HealingStatus(str, Enum):
    """Outcome of Yamaraja's correction attempt."""

    HEALED = "healed"  # Successfully corrected
    SKIPPED = "skipped"  # No action needed
    FAILED = "failed"  # Correction failed
    DEFERRED = "deferred"  # Queued for later
    MANUAL_REQUIRED = "manual_required"  # Needs human
    MERCY_GRANTED = "mercy_granted"  # AJAMIL - saved by Holy Name


# =============================================================================
# Data Classes: Unified report formats
# =============================================================================


@dataclass
class UnifiedDriftReport:
    """
    Yamaraja's unified drift report - what he judges.
    WATERTIGHT except raw_data (legacy compatibility).
    """

    id: str
    source: DriftSource
    severity: DriftSeverity
    message: str
    detected_at: datetime = field(default_factory=datetime.now)

    # Location context
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    component: Optional[str] = None

    # Detection metadata
    detector_id: str = ""
    rule_id: Optional[str] = None
    baseline_value: Optional[float] = None
    current_value: Optional[float] = None

    # Healing hints
    suggested_handler: Optional[str] = None
    auto_healable: bool = False
    requires_approval: bool = False

    # AJAMIL EXCEPTION - Does this component chant?
    is_chanting: bool = True  # Default True in Kali Yuga

    # Raw data (Any for legacy compatibility - to be removed)
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
            "is_chanting": self.is_chanting,
        }


@dataclass
class HealingResult:
    """
    Yamaraja's healing verdict.
    WATERTIGHT except raw_data.
    """

    drift_id: str
    status: HealingStatus
    handler_id: str
    message: str = ""
    healed_at: Optional[datetime] = None

    # Change tracking
    files_modified: List[Path] = field(default_factory=list)
    diff: Optional[str] = None

    # Verification
    verified: bool = False
    verification_message: str = ""

    # AJAMIL EXCEPTION
    mercy_granted: bool = False
    mercy_reason: str = ""

    # Metadata
    duration_ms: float = 0.0
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def healed(self) -> bool:
        """True if correction was successful OR mercy was granted."""
        return self.status in (HealingStatus.HEALED, HealingStatus.MERCY_GRANTED)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "drift_id": self.drift_id,
            "status": self.status.value,
            "handler_id": self.handler_id,
            "message": self.message,
            "healed_at": self.healed_at.isoformat() if self.healed_at else None,
            "files_modified": [str(p) for p in self.files_modified],
            "verified": self.verified,
            "mercy_granted": self.mercy_granted,
            "duration_ms": self.duration_ms,
        }


@dataclass
class CorrectionStats:
    """Yamaraja's court statistics."""

    detectors_registered: int = 0
    handlers_registered: int = 0
    drifts_detected: int = 0
    healings_attempted: int = 0
    healings_succeeded: int = 0
    healings_failed: int = 0
    mercy_cases: int = 0  # AJAMIL EXCEPTIONS
    last_detection_run: Optional[datetime] = None
    last_healing_run: Optional[datetime] = None


# =============================================================================
# Protocol Types
# =============================================================================

DriftDetector = Callable[[], List[UnifiedDriftReport]]
CorrectionHandler = Callable[[UnifiedDriftReport, HealingStrategy], HealingResult]


# =============================================================================
# Main Protocols
# =============================================================================


@runtime_checkable
class DriftRegistryProtocol(Protocol):
    """Yamaraja's registry of drift detectors."""

    def register_detector(
        self,
        source: DriftSource,
        detector: DriftDetector,
        detector_id: str = "",
    ) -> None: ...

    def unregister_detector(self, detector_id: str) -> bool: ...

    def detect(self, source: Optional[DriftSource] = None) -> List[UnifiedDriftReport]: ...

    def detect_all(self) -> List[UnifiedDriftReport]: ...

    def get_detector_ids(self) -> List[str]: ...


@runtime_checkable
class CorrectionDispatcherProtocol(Protocol):
    """
    Yamaraja's correction dispatcher.

    IMPORTANT: Always check is_chanting before denying!
    The Ajamil Exception applies to corrections too.
    """

    def register_handler(
        self,
        source: DriftSource,
        handler: CorrectionHandler,
        handler_id: str = "",
        priority: int = 0,
    ) -> None: ...

    def unregister_handler(self, handler_id: str) -> bool: ...

    def dispatch(
        self,
        drift: UnifiedDriftReport,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> HealingResult: ...

    def dispatch_all(
        self,
        drifts: List[UnifiedDriftReport],
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> List[HealingResult]: ...

    def can_heal(self, drift: UnifiedDriftReport) -> bool: ...

    def get_handler_ids(self) -> List[str]: ...

    def get_stats(self) -> CorrectionStats: ...


@runtime_checkable
class HealingStrategyResolverProtocol(Protocol):
    """Resolves healing strategy based on trust and context."""

    def resolve(
        self,
        agent_id: str,
        drift: UnifiedDriftReport,
    ) -> HealingStrategy: ...

    def get_trust_level(self, agent_id: str) -> float: ...


@runtime_checkable
class CorrectionOrchestratorProtocol(Protocol):
    """High-level orchestrator - Yamaraja's full court."""

    @property
    def registry(self) -> DriftRegistryProtocol: ...

    @property
    def dispatcher(self) -> CorrectionDispatcherProtocol: ...

    def detect_and_report(
        self,
        source: Optional[DriftSource] = None,
    ) -> List[UnifiedDriftReport]: ...

    def detect_and_heal(
        self,
        source: Optional[DriftSource] = None,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
        auto_only: bool = True,
    ) -> List[HealingResult]: ...

    def get_healable_count(self) -> Dict[DriftSource, int]: ...


# =============================================================================
# Null Implementations
# =============================================================================


class NullDriftRegistry:
    """No-op drift registry (all is well)."""

    def register_detector(self, source: DriftSource = None, detector: DriftDetector = None, detector_id: str = "") -> None:
        pass

    def unregister_detector(self, detector_id: str = "") -> bool:
        return False

    def detect(self, source: Optional[DriftSource] = None) -> List[UnifiedDriftReport]:
        return []

    def detect_all(self) -> List[UnifiedDriftReport]:
        return []

    def get_detector_ids(self) -> List[str]:
        return []


class NullCorrectionDispatcher:
    """No-op dispatcher (maximum mercy)."""

    def register_handler(
        self,
        source: DriftSource = None,
        handler: CorrectionHandler = None,
        handler_id: str = "",
        priority: int = 0,
    ) -> None:
        pass

    def unregister_handler(self, handler_id: str = "") -> bool:
        return False

    def dispatch(
        self,
        drift: UnifiedDriftReport = None,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> HealingResult:
        # AJAMIL EXCEPTION: if chanting, grant mercy
        if drift.is_chanting:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.MERCY_GRANTED,
                handler_id="null_yamaraja",
                message="Mercy granted - chanting transcends correction",
                mercy_granted=True,
                mercy_reason="Ajamil Exception: is_chanting=True",
            )
        return HealingResult(
            drift_id=drift.id,
            status=HealingStatus.SKIPPED,
            handler_id="null",
            message="No dispatcher configured",
        )

    def dispatch_all(
        self,
        drifts: List[UnifiedDriftReport] = None,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> List[HealingResult]:
        return [self.dispatch(d, strategy) for d in drifts]

    def can_heal(self, drift: UnifiedDriftReport = None) -> bool:
        return drift.is_chanting  # Can always heal if chanting (mercy)

    def get_handler_ids(self) -> List[str]:
        return []

    def get_stats(self) -> CorrectionStats:
        return CorrectionStats()


# =============================================================================
# Adapter Factories (convert legacy → unified)
# =============================================================================


def adapt_reactor_drift(drift_event: Any) -> UnifiedDriftReport:
    """Adapt ReactorProtocol.DriftEvent → UnifiedDriftReport."""
    from vibe_core.protocols.reactor import DriftType as ReactorDriftType

    source_map = {
        ReactorDriftType.PERFORMANCE: DriftSource.PERFORMANCE,
        ReactorDriftType.RELIABILITY: DriftSource.RELIABILITY,
        ReactorDriftType.CONFIG: DriftSource.CONFIG,
        ReactorDriftType.STATE: DriftSource.STATE,
        ReactorDriftType.RESOURCE: DriftSource.PERFORMANCE,
        ReactorDriftType.USAGE: DriftSource.COGNITIVE,
    }

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
        auto_healable=False,
        raw_data=drift_event.data,
    )


def adapt_shuddhi_result(result: Any, drift_id: str) -> HealingResult:
    """Adapt ShuddhiResult → HealingResult."""
    from vibe_core.protocols.mahajanas.kumaras.shuddhi import ShuddhiStatus

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
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
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
    "HealingStrategyResolverProtocol",
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
