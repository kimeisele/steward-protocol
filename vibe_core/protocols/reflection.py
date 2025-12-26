"""
OPUS-311 Sprint 3: Reflection Protocol

The Viveka (Discrimination) that learns from experience.

Self-improvement through execution analysis.
Closes the One-Way Feedback Loop (Critical 5% #3).

Usage:
    # Via ServiceRegistry
    reflection: ReflectionProtocol = ServiceRegistry.get(ReflectionProtocol) or NullReflection()

    # After execution
    execution = ExecutionRecord(command="status", success=True, duration_ms=50)
    insights = reflection.analyze_execution(execution)

    # Propose improvements
    proposal = reflection.propose_improvement(insights)
    if proposal:
        reflection.apply_improvement(proposal)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


class InsightType(str, Enum):
    """Types of insights from execution analysis."""

    PERFORMANCE = "performance"  # Slow execution
    FAILURE_PATTERN = "failure_pattern"  # Repeated failures
    USAGE_PATTERN = "usage_pattern"  # Frequently used commands
    UNUSED = "unused"  # Commands never used
    IMPROVEMENT = "improvement"  # Suggested improvement


class ProposalType(str, Enum):
    """Types of improvement proposals."""

    NEW_ALIAS = "new_alias"  # Create command alias
    DEPRECATE = "deprecate"  # Mark command as deprecated
    OPTIMIZE = "optimize"  # Performance optimization
    AUTO_CORRECT = "auto_correct"  # Auto-correct common mistakes
    SUGGEST_ALTERNATIVE = "suggest_alternative"  # Suggest better command


class ProposalStatus(str, Enum):
    """Status of improvement proposals."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"


@dataclass
class ExecutionRecord:
    """Record of a single command execution."""

    command: str
    args: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None


@dataclass
class Insight:
    """An insight derived from execution analysis."""

    type: InsightType
    message: str
    confidence: float = 0.0  # 0.0 to 1.0
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Proposal:
    """An improvement proposal."""

    id: str
    type: ProposalType
    title: str
    description: str
    status: ProposalStatus = ProposalStatus.PENDING
    insights: List[Insight] = field(default_factory=list)
    implementation: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReflectionStats:
    """Statistics about reflection activity."""

    executions_analyzed: int = 0
    insights_generated: int = 0
    proposals_created: int = 0
    proposals_applied: int = 0
    failure_rate: float = 0.0
    avg_duration_ms: float = 0.0


@runtime_checkable
class ReflectionProtocol(Protocol):
    """
    OPUS-311: Self-improvement through execution analysis.

    The Viveka - "discriminative wisdom" that learns from experience.

    Features:
    - Analyze command executions
    - Detect patterns (failures, performance, usage)
    - Propose improvements
    - Apply improvements (with governance)
    """

    def record_execution(self, record: ExecutionRecord) -> None:
        """
        Record an execution for later analysis.

        Called after every command execution.
        """
        ...

    def analyze_execution(self, record: ExecutionRecord) -> List[Insight]:
        """
        Analyze a single execution for insights.

        Returns immediate insights (e.g., "this command is slow").
        """
        ...

    def analyze_patterns(self, limit: int = 100) -> List[Insight]:
        """
        Analyze recent executions for patterns.

        Returns aggregated insights (e.g., "command X fails 80% of the time").
        """
        ...

    def propose_improvement(self, insights: List[Insight]) -> Optional[Proposal]:
        """
        Create an improvement proposal from insights.

        Returns None if no actionable improvement found.
        """
        ...

    def get_pending_proposals(self) -> List[Proposal]:
        """Get all pending improvement proposals."""
        ...

    def approve_proposal(self, proposal_id: str) -> bool:
        """Mark a proposal as approved."""
        ...

    def reject_proposal(self, proposal_id: str, reason: str) -> bool:
        """Mark a proposal as rejected."""
        ...

    def apply_proposal(self, proposal_id: str) -> bool:
        """
        Apply an approved proposal.

        Returns True if successfully applied.
        """
        ...

    def get_stats(self) -> ReflectionStats:
        """Get reflection activity statistics."""
        ...

    def get_failure_patterns(self, command: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get failure patterns for learning.

        Args:
            command: Optional filter by command

        Returns:
            List of failure patterns with context
        """
        ...


class NullReflection:
    """
    Arjuna Pattern: No-op reflection.

    No learning, no improvement.
    Use when reflection service is not available.
    """

    def record_execution(self, record: ExecutionRecord) -> None:
        pass

    def analyze_execution(self, record: ExecutionRecord) -> List[Insight]:
        return []

    def analyze_patterns(self, limit: int = 100) -> List[Insight]:
        return []

    def propose_improvement(self, insights: List[Insight]) -> Optional[Proposal]:
        return None

    def get_pending_proposals(self) -> List[Proposal]:
        return []

    def approve_proposal(self, proposal_id: str) -> bool:
        return False

    def reject_proposal(self, proposal_id: str, reason: str) -> bool:
        return False

    def apply_proposal(self, proposal_id: str) -> bool:
        return False

    def get_stats(self) -> ReflectionStats:
        return ReflectionStats()

    def get_failure_patterns(self, command: Optional[str] = None) -> List[Dict[str, Any]]:
        return []


class BasicReflection:
    """
    OPUS-311: Basic implementation of ReflectionProtocol.

    In-memory storage with simple pattern detection.
    """

    # Thresholds for pattern detection
    SLOW_THRESHOLD_MS = 1000  # Commands taking > 1s are "slow"
    FAILURE_RATE_THRESHOLD = 0.5  # > 50% failure rate triggers insight
    PATTERN_MIN_SAMPLES = 5  # Need at least 5 executions for patterns

    def __init__(self):
        from uuid import uuid4

        self._uuid = uuid4
        self._executions: List[ExecutionRecord] = []
        self._proposals: Dict[str, Proposal] = {}
        self._max_history = 1000

    def record_execution(self, record: ExecutionRecord) -> None:
        self._executions.append(record)
        # Trim history
        if len(self._executions) > self._max_history:
            self._executions = self._executions[-self._max_history :]

    def analyze_execution(self, record: ExecutionRecord) -> List[Insight]:
        insights = []

        # Check for slow execution
        if record.duration_ms > self.SLOW_THRESHOLD_MS:
            insights.append(
                Insight(
                    type=InsightType.PERFORMANCE,
                    message=f"Command '{record.command}' took {record.duration_ms:.0f}ms",
                    confidence=0.9,
                    data={"command": record.command, "duration_ms": record.duration_ms},
                )
            )

        # Check for failure
        if not record.success:
            insights.append(
                Insight(
                    type=InsightType.FAILURE_PATTERN,
                    message=f"Command '{record.command}' failed: {record.error}",
                    confidence=1.0,
                    data={
                        "command": record.command,
                        "error": record.error,
                        "args": record.args,
                    },
                )
            )

        return insights

    def analyze_patterns(self, limit: int = 100) -> List[Insight]:
        insights = []
        recent = self._executions[-limit:]

        if not recent:
            return insights

        # Group by command
        by_command: Dict[str, List[ExecutionRecord]] = {}
        for rec in recent:
            if rec.command not in by_command:
                by_command[rec.command] = []
            by_command[rec.command].append(rec)

        for cmd, records in by_command.items():
            if len(records) < self.PATTERN_MIN_SAMPLES:
                continue

            # Calculate failure rate
            failures = sum(1 for r in records if not r.success)
            failure_rate = failures / len(records)

            if failure_rate > self.FAILURE_RATE_THRESHOLD:
                # Get common error
                errors = [r.error for r in records if r.error]
                common_error = max(set(errors), key=errors.count) if errors else "unknown"

                insights.append(
                    Insight(
                        type=InsightType.FAILURE_PATTERN,
                        message=f"Command '{cmd}' has {failure_rate:.0%} failure rate",
                        confidence=min(0.5 + len(records) / 20, 0.95),
                        data={
                            "command": cmd,
                            "failure_rate": failure_rate,
                            "sample_size": len(records),
                            "common_error": common_error,
                        },
                    )
                )

            # Calculate average duration
            avg_duration = sum(r.duration_ms for r in records) / len(records)
            if avg_duration > self.SLOW_THRESHOLD_MS:
                insights.append(
                    Insight(
                        type=InsightType.PERFORMANCE,
                        message=f"Command '{cmd}' averages {avg_duration:.0f}ms",
                        confidence=min(0.5 + len(records) / 20, 0.95),
                        data={
                            "command": cmd,
                            "avg_duration_ms": avg_duration,
                            "sample_size": len(records),
                        },
                    )
                )

        # Usage patterns - frequently used commands
        usage_counts = {cmd: len(recs) for cmd, recs in by_command.items()}
        if usage_counts:
            top_cmd = max(usage_counts, key=usage_counts.get)
            insights.append(
                Insight(
                    type=InsightType.USAGE_PATTERN,
                    message=f"Most used command: '{top_cmd}' ({usage_counts[top_cmd]} times)",
                    confidence=0.95,
                    data={"top_commands": dict(sorted(usage_counts.items(), key=lambda x: -x[1])[:5])},
                )
            )

        return insights

    def propose_improvement(self, insights: List[Insight]) -> Optional[Proposal]:
        # Filter high-confidence failure patterns
        failures = [i for i in insights if i.type == InsightType.FAILURE_PATTERN and i.confidence > 0.7]

        if failures:
            # Propose auto-correction
            failure = failures[0]
            cmd = failure.data.get("command", "unknown")

            return Proposal(
                id=str(self._uuid()),
                type=ProposalType.AUTO_CORRECT,
                title=f"Improve reliability of '{cmd}'",
                description=f"Command '{cmd}' has high failure rate. Consider adding validation or better error handling.",
                insights=failures,
                implementation={
                    "action": "add_validation",
                    "command": cmd,
                    "common_error": failure.data.get("common_error"),
                },
            )

        # Filter performance issues
        perf = [i for i in insights if i.type == InsightType.PERFORMANCE and i.confidence > 0.7]

        if perf:
            issue = perf[0]
            cmd = issue.data.get("command", "unknown")

            return Proposal(
                id=str(self._uuid()),
                type=ProposalType.OPTIMIZE,
                title=f"Optimize slow command '{cmd}'",
                description=f"Command '{cmd}' averages {issue.data.get('avg_duration_ms', 0):.0f}ms. Consider caching or async execution.",
                insights=perf,
                implementation={
                    "action": "add_caching",
                    "command": cmd,
                },
            )

        return None

    def get_pending_proposals(self) -> List[Proposal]:
        return [p for p in self._proposals.values() if p.status == ProposalStatus.PENDING]

    def approve_proposal(self, proposal_id: str) -> bool:
        if proposal_id in self._proposals:
            self._proposals[proposal_id].status = ProposalStatus.APPROVED
            return True
        return False

    def reject_proposal(self, proposal_id: str, reason: str) -> bool:
        if proposal_id in self._proposals:
            self._proposals[proposal_id].status = ProposalStatus.REJECTED
            return True
        return False

    def apply_proposal(self, proposal_id: str) -> bool:
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return False
        if proposal.status != ProposalStatus.APPROVED:
            return False

        # In a real implementation, this would modify CommandRegistry
        # For now, just mark as applied
        proposal.status = ProposalStatus.APPLIED
        return True

    def get_stats(self) -> ReflectionStats:
        total = len(self._executions)
        failures = sum(1 for e in self._executions if not e.success)
        avg_duration = sum(e.duration_ms for e in self._executions) / total if total else 0

        return ReflectionStats(
            executions_analyzed=total,
            insights_generated=0,  # Would need separate tracking
            proposals_created=len(self._proposals),
            proposals_applied=sum(1 for p in self._proposals.values() if p.status == ProposalStatus.APPLIED),
            failure_rate=failures / total if total else 0,
            avg_duration_ms=avg_duration,
        )

    def get_failure_patterns(self, command: Optional[str] = None) -> List[Dict[str, Any]]:
        failures = [e for e in self._executions if not e.success]
        if command:
            failures = [e for e in failures if e.command == command]

        # Group by error
        by_error: Dict[str, List[ExecutionRecord]] = {}
        for f in failures:
            error = f.error or "unknown"
            if error not in by_error:
                by_error[error] = []
            by_error[error].append(f)

        return [
            {
                "error": error,
                "count": len(records),
                "commands": list(set(r.command for r in records)),
                "first_seen": min(r.timestamp for r in records),
                "last_seen": max(r.timestamp for r in records),
            }
            for error, records in by_error.items()
        ]


def get_reflection_safe() -> ReflectionProtocol:
    """
    Get Reflection via ServiceRegistry with NullReflection fallback.

    OPUS-311: Use this for guaranteed non-None return.
    """
    try:
        from vibe_core.di import ServiceRegistry

        reflection = ServiceRegistry.get(ReflectionProtocol)
        if reflection is not None:
            return reflection
    except ImportError:
        pass

    return NullReflection()
