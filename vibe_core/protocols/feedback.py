"""
OPUS-311 Sprint 3: Feedback Protocol

The Vedana (Feeling) that learns from success and failure.

Pain/pleasure signals for learning. Closes the One-Way Feedback Loop.
(Critical 5% #3: "When command fails, MANAS sees error but doesn't feel it")

Usage:
    # Via ServiceRegistry
    feedback: FeedbackProtocol = ServiceRegistry.get(FeedbackProtocol) or NullFeedback()

    # After command execution
    if result.success:
        feedback.signal_success("list_agents", context)
    else:
        feedback.signal_failure("list_agents", result.error, context)

    # IntentMatcher can avoid known failure patterns
    patterns = feedback.get_failure_patterns()
    for pattern in patterns:
        if matches(input, pattern):
            suggest_alternative(pattern.alternative)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


class SignalType(str, Enum):
    """Types of feedback signals."""

    SUCCESS = "success"  # Positive reinforcement
    FAILURE = "failure"  # Negative reinforcement
    PARTIAL = "partial"  # Mixed result
    TIMEOUT = "timeout"  # Operation timed out
    ABORT = "abort"  # User aborted


@dataclass
class Signal:
    """A feedback signal from execution."""

    type: SignalType
    command: str
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    session_id: Optional[str] = None


@dataclass
class FailurePattern:
    """A recognized pattern of failures."""

    command: str
    error_pattern: str  # Regex or substring
    frequency: int  # How many times seen
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    alternative: Optional[str] = None  # Suggested alternative command
    context_hints: List[str] = field(default_factory=list)  # Common context factors


@dataclass
class SuccessPattern:
    """A recognized pattern of successes."""

    command: str
    frequency: int
    avg_duration_ms: float = 0.0
    common_args: List[str] = field(default_factory=list)


@dataclass
class FeedbackStats:
    """Statistics about feedback signals."""

    total_signals: int = 0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    top_failures: List[str] = field(default_factory=list)
    top_successes: List[str] = field(default_factory=list)


@runtime_checkable
class FeedbackProtocol(Protocol):
    """
    OPUS-311: Pain/pleasure signals for learning.

    The Vedana - "feeling tone" that arises with each experience.

    Features:
    - Record success/failure signals
    - Detect failure patterns
    - Suggest alternatives for failing commands
    - Feed into Reflection for improvement proposals
    """

    def signal_success(
        self,
        command: str,
        context: Dict[str, Any],
        duration_ms: float = 0.0,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Record a successful execution.

        Positive reinforcement for learning.
        """
        ...

    def signal_failure(
        self,
        command: str,
        error: str,
        context: Dict[str, Any],
        duration_ms: float = 0.0,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Record a failed execution.

        Negative reinforcement for learning.
        """
        ...

    def signal_partial(
        self,
        command: str,
        message: str,
        context: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> None:
        """
        Record a partial success/failure.

        Mixed reinforcement (e.g., "3 of 5 tests passed").
        """
        ...

    def get_failure_patterns(
        self,
        command: Optional[str] = None,
        min_frequency: int = 2,
    ) -> List[FailurePattern]:
        """
        Get recognized failure patterns.

        Args:
            command: Optional filter by command
            min_frequency: Minimum occurrences to be a pattern

        Returns:
            List of failure patterns, most frequent first
        """
        ...

    def get_success_patterns(
        self,
        command: Optional[str] = None,
        min_frequency: int = 2,
    ) -> List[SuccessPattern]:
        """
        Get recognized success patterns.

        Useful for suggesting frequently used commands.
        """
        ...

    def should_warn(self, command: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Check if a command should trigger a warning.

        Based on historical failure patterns.

        Returns:
            Warning message if should warn, None otherwise
        """
        ...

    def suggest_alternative(self, command: str, error: str) -> Optional[str]:
        """
        Suggest an alternative command based on error.

        Returns:
            Suggested command or None
        """
        ...

    def register_alternative(
        self,
        error_pattern: str,
        alternative: str,
    ) -> None:
        """
        Register an alternative for an error pattern.

        Allows learning from corrections.
        """
        ...

    def get_stats(self) -> FeedbackStats:
        """Get feedback statistics."""
        ...

    def get_recent_signals(
        self,
        limit: int = 100,
        signal_type: Optional[SignalType] = None,
    ) -> List[Signal]:
        """Get recent signals for analysis."""
        ...


class NullFeedback:
    """
    Arjuna Pattern: No-op feedback.

    No learning, no patterns.
    Use when feedback service is not available.
    """

    def signal_success(
        self,
        command: str,
        context: Dict[str, Any],
        duration_ms: float = 0.0,
        session_id: Optional[str] = None,
    ) -> None:
        pass

    def signal_failure(
        self,
        command: str,
        error: str,
        context: Dict[str, Any],
        duration_ms: float = 0.0,
        session_id: Optional[str] = None,
    ) -> None:
        pass

    def signal_partial(
        self,
        command: str,
        message: str,
        context: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> None:
        pass

    def get_failure_patterns(
        self,
        command: Optional[str] = None,
        min_frequency: int = 2,
    ) -> List[FailurePattern]:
        return []

    def get_success_patterns(
        self,
        command: Optional[str] = None,
        min_frequency: int = 2,
    ) -> List[SuccessPattern]:
        return []

    def should_warn(self, command: str, context: Dict[str, Any]) -> Optional[str]:
        return None

    def suggest_alternative(self, command: str, error: str) -> Optional[str]:
        return None

    def register_alternative(
        self,
        error_pattern: str,
        alternative: str,
    ) -> None:
        pass

    def get_stats(self) -> FeedbackStats:
        return FeedbackStats()

    def get_recent_signals(
        self,
        limit: int = 100,
        signal_type: Optional[SignalType] = None,
    ) -> List[Signal]:
        return []


class InMemoryFeedback:
    """
    OPUS-311: In-memory implementation of FeedbackProtocol.

    Simple pattern detection for learning.
    """

    # Thresholds
    PATTERN_THRESHOLD = 2  # Min occurrences to be a pattern
    WARNING_THRESHOLD = 0.6  # >60% failure rate triggers warning
    MAX_SIGNALS = 10000

    def __init__(self):
        self._signals: List[Signal] = []
        self._alternatives: Dict[str, str] = {}  # error_pattern -> alternative

    def signal_success(
        self,
        command: str,
        context: Dict[str, Any],
        duration_ms: float = 0.0,
        session_id: Optional[str] = None,
    ) -> None:
        signal = Signal(
            type=SignalType.SUCCESS,
            command=command,
            context=context,
            duration_ms=duration_ms,
            session_id=session_id,
        )
        self._add_signal(signal)

    def signal_failure(
        self,
        command: str,
        error: str,
        context: Dict[str, Any],
        duration_ms: float = 0.0,
        session_id: Optional[str] = None,
    ) -> None:
        signal = Signal(
            type=SignalType.FAILURE,
            command=command,
            error=error,
            context=context,
            duration_ms=duration_ms,
            session_id=session_id,
        )
        self._add_signal(signal)

    def signal_partial(
        self,
        command: str,
        message: str,
        context: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> None:
        signal = Signal(
            type=SignalType.PARTIAL,
            command=command,
            error=message,
            context=context,
            session_id=session_id,
        )
        self._add_signal(signal)

    def _add_signal(self, signal: Signal) -> None:
        self._signals.append(signal)
        if len(self._signals) > self.MAX_SIGNALS:
            self._signals = self._signals[-self.MAX_SIGNALS :]

    def get_failure_patterns(
        self,
        command: Optional[str] = None,
        min_frequency: int = 2,
    ) -> List[FailurePattern]:
        # Filter failures
        failures = [s for s in self._signals if s.type == SignalType.FAILURE]
        if command:
            failures = [s for s in failures if s.command == command]

        # Group by (command, error)
        groups: Dict[tuple, List[Signal]] = {}
        for s in failures:
            key = (s.command, s.error or "unknown")
            if key not in groups:
                groups[key] = []
            groups[key].append(s)

        # Build patterns
        patterns = []
        for (cmd, error), signals in groups.items():
            if len(signals) >= min_frequency:
                patterns.append(
                    FailurePattern(
                        command=cmd,
                        error_pattern=error,
                        frequency=len(signals),
                        first_seen=min(s.timestamp for s in signals),
                        last_seen=max(s.timestamp for s in signals),
                        alternative=self._alternatives.get(error),
                    )
                )

        # Sort by frequency descending
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns

    def get_success_patterns(
        self,
        command: Optional[str] = None,
        min_frequency: int = 2,
    ) -> List[SuccessPattern]:
        # Filter successes
        successes = [s for s in self._signals if s.type == SignalType.SUCCESS]
        if command:
            successes = [s for s in successes if s.command == command]

        # Group by command
        groups: Dict[str, List[Signal]] = {}
        for s in successes:
            if s.command not in groups:
                groups[s.command] = []
            groups[s.command].append(s)

        # Build patterns
        patterns = []
        for cmd, signals in groups.items():
            if len(signals) >= min_frequency:
                avg_duration = sum(s.duration_ms for s in signals) / len(signals)
                patterns.append(
                    SuccessPattern(
                        command=cmd,
                        frequency=len(signals),
                        avg_duration_ms=avg_duration,
                    )
                )

        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns

    def should_warn(self, command: str, context: Dict[str, Any]) -> Optional[str]:
        # Get signals for this command
        cmd_signals = [s for s in self._signals if s.command == command]
        if len(cmd_signals) < self.PATTERN_THRESHOLD:
            return None

        # Calculate failure rate
        failures = sum(1 for s in cmd_signals if s.type == SignalType.FAILURE)
        failure_rate = failures / len(cmd_signals)

        if failure_rate > self.WARNING_THRESHOLD:
            return f"Warning: '{command}' has {failure_rate:.0%} failure rate"

        return None

    def suggest_alternative(self, command: str, error: str) -> Optional[str]:
        # Check registered alternatives
        for pattern, alt in self._alternatives.items():
            if pattern in error:
                return alt

        # Check success patterns for similar commands
        success_patterns = self.get_success_patterns()
        for pattern in success_patterns:
            if pattern.command != command and command in pattern.command:
                return pattern.command

        return None

    def register_alternative(
        self,
        error_pattern: str,
        alternative: str,
    ) -> None:
        self._alternatives[error_pattern] = alternative

    def get_stats(self) -> FeedbackStats:
        total = len(self._signals)
        successes = sum(1 for s in self._signals if s.type == SignalType.SUCCESS)
        failures = sum(1 for s in self._signals if s.type == SignalType.FAILURE)

        # Top failures
        failure_patterns = self.get_failure_patterns()
        top_failures = [p.command for p in failure_patterns[:5]]

        # Top successes
        success_patterns = self.get_success_patterns()
        top_successes = [p.command for p in success_patterns[:5]]

        # Avg duration
        with_duration = [s for s in self._signals if s.duration_ms > 0]
        avg_duration = sum(s.duration_ms for s in with_duration) / len(with_duration) if with_duration else 0

        return FeedbackStats(
            total_signals=total,
            success_count=successes,
            failure_count=failures,
            success_rate=successes / total if total else 0,
            avg_duration_ms=avg_duration,
            top_failures=top_failures,
            top_successes=top_successes,
        )

    def get_recent_signals(
        self,
        limit: int = 100,
        signal_type: Optional[SignalType] = None,
    ) -> List[Signal]:
        signals = self._signals
        if signal_type:
            signals = [s for s in signals if s.type == signal_type]
        return signals[-limit:]


def get_feedback_safe() -> FeedbackProtocol:
    """
    Get Feedback via ServiceRegistry with NullFeedback fallback.

    OPUS-311: Use this for guaranteed non-None return.
    """
    try:
        from vibe_core.di import ServiceRegistry

        feedback = ServiceRegistry.get(FeedbackProtocol)
        if feedback is not None:
            return feedback
    except ImportError:
        pass

    return NullFeedback()
