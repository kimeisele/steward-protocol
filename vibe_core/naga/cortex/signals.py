"""
NAGA Cortex Signal Types.

Signals are the INPUT to the Cortex - observations from the NAGA network.

Signal Sources:
- FloodManager: EventBus/SignalBus observations
- CommitWatcher: Git commit pattern detection
- StateProxy: State write validations/violations

Design Principle: Signals are IMMUTABLE data carriers, not actors.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class SignalType(Enum):
    """Types of signals the Cortex can receive."""

    FLOOD = auto()  # From EventBus/SignalBus
    COMMIT = auto()  # From CommitWatcher
    STATE = auto()  # From StateProxy
    HEALTH = auto()  # Periodic health checks
    DRIFT = auto()  # From CorrectionDispatcher


@dataclass
class NagaSignal:
    """
    Base signal type - observation from the NAGA network.

    All signals are timestamped and tagged with their source.
    """

    source_id: str
    signal_type: SignalType = SignalType.FLOOD
    timestamp: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def age_seconds(self) -> float:
        """How old is this signal?"""
        return (datetime.now() - self.timestamp).total_seconds()


@dataclass
class FloodSignal(NagaSignal):
    """
    Signal from FloodManager - EventBus/SignalBus observation.

    Example events:
    - Agent task completed
    - Plugin loaded
    - Tool executed
    - Error occurred
    """

    event_type: str = ""
    agent_id: Optional[str] = None
    toxicity_score: float = 0.0
    patterns_detected: tuple = field(default_factory=tuple)

    def __post_init__(self):
        self.signal_type = SignalType.FLOOD


@dataclass
class CommitSignal(NagaSignal):
    """
    Signal from CommitWatcher - Git commit pattern detection.

    Patterns detected:
    - PANIC: Rapid commits (stagnation → burst)
    - STAGNATION: No commits for extended period
    - DEFERRAL: Keywords like "TODO", "FIXME", "later"
    - BYPASS: Commits skipping pre-commit hooks
    """

    pattern: str = ""
    commit_sha: str = ""
    files_changed: tuple = field(default_factory=tuple)
    severity: str = "INFO"

    def __post_init__(self):
        self.signal_type = SignalType.COMMIT


@dataclass
class StateSignal(NagaSignal):
    """
    Signal from NagaStateProxy - State write validation.

    Dharma Principles Checked:
    - DAYA: Compassion (no destructive operations)
    - SATYAM: Truthfulness (data integrity)
    - TAPAS: Discipline (within boundaries)
    - SAUCAM: Purity (no contamination)
    """

    operation: str = ""  # save, append, delete
    path: str = ""
    dharma_principles: tuple = field(default_factory=tuple)
    violation: bool = False
    violation_reason: Optional[str] = None

    def __post_init__(self):
        self.signal_type = SignalType.STATE


@dataclass
class CorrelatedContext:
    """
    Correlated context from multiple signals.

    The Cortex aggregates signals and produces a unified understanding.
    This is the OUTPUT of correlation, INPUT to decision.
    """

    signals: List[NagaSignal] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    # Aggregated intelligence from NAGAs
    sesha_patterns: List[str] = field(default_factory=list)
    takshaka_threats: List[Dict[str, Any]] = field(default_factory=list)
    vasuki_peer_health: Dict[str, Any] = field(default_factory=dict)

    # Derived analysis
    signal_count_by_type: Dict[str, int] = field(default_factory=dict)
    dominant_pattern: Optional[str] = None
    threat_level: float = 0.0  # 0.0 = safe, 1.0 = critical

    def __post_init__(self):
        """Compute derived fields."""
        # Count signals by type
        for sig in self.signals:
            type_name = sig.signal_type.name
            self.signal_count_by_type[type_name] = self.signal_count_by_type.get(type_name, 0) + 1

        # Compute threat level from Takshaka threats
        if self.takshaka_threats:
            max_threat = max(t.get("severity", 0) for t in self.takshaka_threats)
            self.threat_level = min(1.0, max_threat / 10.0)

    # === Query Methods ===

    def has_security_threat(self) -> bool:
        """Check if there's an active security threat."""
        return self.threat_level >= 0.5 or len(self.takshaka_threats) > 0

    def has_healable_violation(self) -> bool:
        """Check if there's a structural violation that can be healed."""
        for sig in self.signals:
            if isinstance(sig, StateSignal) and sig.violation:
                return True
            if isinstance(sig, CommitSignal) and sig.pattern in (
                "PANIC",
                "BYPASS",
            ):
                return True
        return False

    def has_circuit_drift(self) -> bool:
        """Check if routing confidence should be adjusted."""
        # If many errors from a specific circuit, it's drifting
        error_signals = [s for s in self.signals if isinstance(s, FloodSignal) and s.toxicity_score > 0.3]
        return len(error_signals) >= 3

    def needs_cognitive_update(self) -> bool:
        """Check if Manas should be informed of new context."""
        # If we have fresh patterns, Manas might benefit
        return len(self.sesha_patterns) >= 3 or self.threat_level > 0

    def get_threat_source(self) -> Optional[str]:
        """Get the source of the primary threat."""
        if self.takshaka_threats:
            return self.takshaka_threats[0].get("source", "unknown")
        return None

    def get_violation_details(self) -> Optional[Dict[str, Any]]:
        """Get details of the first healable violation."""
        for sig in self.signals:
            if isinstance(sig, StateSignal) and sig.violation:
                return {
                    "path": sig.path,
                    "rule": sig.violation_reason or "dharma_violation",
                }
            if isinstance(sig, CommitSignal) and sig.pattern in (
                "PANIC",
                "BYPASS",
            ):
                return {
                    "path": sig.files_changed[0] if sig.files_changed else None,
                    "rule": f"commit_{sig.pattern.lower()}",
                }
        return None

    def get_degraded_circuit(self) -> Optional[str]:
        """Get the ID of a circuit that needs confidence adjustment."""
        for sig in self.signals:
            if isinstance(sig, FloodSignal) and sig.toxicity_score > 0.3:
                return sig.agent_id
        return None

    def get_cognitive_payload(self) -> Dict[str, Any]:
        """Get context payload for Manas."""
        return {
            "naga_patterns": self.sesha_patterns,
            "threat_level": self.threat_level,
            "signal_summary": self.signal_count_by_type,
            "dominant_pattern": self.dominant_pattern,
        }
