"""
Unified State Schemas - Layer 2: Core Data Structures

OPUS-211: Structural Consolidation

This module provides the canonical definitions for common state structures
to eliminate duplication across the codebase.

"Fragmentation is the source of Tamas. Unity is the path to Sattva."
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CyclePhase(str, Enum):
    """Unified orchestration phases for all cycles."""

    # OODA-based phases
    PERCEIVE = "perceive"  # Sense state / observe reality
    ORIENT = "orient"  # Classify / interpret observations
    DECIDE = "decide"  # Generate / filter / prioritize actions
    ACT = "act"  # Execute / apply actions
    PERSIST = "persist"  # Record / commit state
    RECOVER = "recover"  # Error handling / reset if needed

    # Ritual-based phases (mapped to OODA)
    SUNRISE = "sunrise"  # Morning: Initialization (PERCEIVE)
    MIDDAY = "midday"  # Noon: Work (ACT)
    SUNSET = "sunset"  # Evening: Closure (DECIDE)
    ARCHIVE = "archive"  # Night: Settlement (PERSIST)


@dataclass
class CommitResult:
    """Unified result of a commit attempt (Git/Ledger/State)."""

    success: bool
    git_sha: Optional[str] = None
    commit_hash: Optional[str] = None  # Alias for git_sha (legacy compat)
    ledger_event_id: Optional[str] = None
    session_id: Optional[str] = None
    files_committed: List[str] = field(default_factory=list)
    error: Optional[str] = None
    skipped_reason: Optional[str] = None

    def __post_init__(self):
        # Sync git_sha and commit_hash
        if self.git_sha and not self.commit_hash:
            self.commit_hash = self.git_sha
        elif self.commit_hash and not self.git_sha:
            self.git_sha = self.commit_hash

    def __bool__(self) -> bool:
        """Allow using result in boolean context."""
        return self.success


@dataclass
class ExecutionResult:
    """Unified result of intent execution or task processing."""

    success: bool
    result: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: int = 0
    blocked_reason: Optional[str] = None
    error: Optional[str] = None
    trace_id: Optional[str] = None
    executed_by: Optional[str] = None


@dataclass
class ActionResult:
    """Unified result of a single action execution."""

    success: bool
    action_name: str = "unknown"
    intent_type: str = "unknown"
    data: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None  # Alias for data (legacy compat)
    error: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    action_type: str = "unknown"

    def __post_init__(self):
        # Sync data and result
        if self.data is not None and self.result is None:
            self.result = self.data
        elif self.result is not None and self.data is None:
            self.data = self.result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "action_name": self.action_name,
            "intent_type": self.intent_type,
            "result": self.result,
            "error": self.error,
            "message": self.message,
            "metadata": self.metadata,
            "action_type": self.action_type,
        }


@dataclass
class RouteResult:
    """Unified result of a routing decision."""

    target_id: str
    target_type: str  # "agent", "plugin", "playbook", "circuit"
    confidence: float
    reason: str
    params: Dict[str, Any] = field(default_factory=dict)
    is_fallback: bool = False


# =============================================================================
# OPUS-300: Extracted from unified_execution.py to resolve circular imports
# =============================================================================


class ExecutionPath(str, Enum):
    """The type of execution to perform"""

    CIRCUIT = "circuit"
    PLAYBOOK = "playbook"
    FAST_COMMAND = "fast_command"
    FALLBACK = "fallback"


class ExecutionStatus(str, Enum):
    """Status of an execution request"""

    PENDING = "pending"
    ROUTING = "routing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class MilkOceanGate(str, Enum):
    """MilkOcean gate decisions (BREAK 8 fix: documented statuses)"""

    ALLOW = "allow"  # Proceed with execution
    QUEUE = "queue"  # Add to background queue
    BLOCK = "block"  # Veto - don't execute
    CRITICAL = "critical"  # GAJENDRA PROTOCOL - emergency


@dataclass
class ExecutionRequest:
    """
    Single source of truth for a request (BREAK 7 fix).

    All state is tracked here, not scattered across multiple systems.
    Moved from unified_execution.py to break circular dependency with kernel_impl.
    """

    # Identity
    request_id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")

    # Input
    user_input: str = ""
    source: str = "envoy"  # "envoy.md", "api", "agent", "cli"

    # Routing decision (made ONCE at routing time - BREAK 2 fix)
    execution_path: ExecutionPath = ExecutionPath.FALLBACK
    target_id: str = ""  # Circuit ID or Playbook ID or Command name
    confidence: float = 0.0

    # MilkOcean gate decision
    gate_decision: MilkOceanGate = MilkOceanGate.ALLOW

    # OPUS-200/201: Quantum Resonance Field (alternative to boolean gate)
    resonance_energy: float = 0.0  # Total energy from reactor
    resonance_inertia: float = 0.5  # Threshold for manifestation
    resonance_hash: str = ""  # Entropy chain hash for audit

    # Runtime state
    status: ExecutionStatus = ExecutionStatus.PENDING
    phase_results: Dict[str, Any] = field(default_factory=dict)

    # Lifecycle timestamps
    created_at: float = field(default_factory=time.time)
    routed_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    # Error tracking
    error: Optional[str] = None

    def mark_routed(self, path: ExecutionPath, target: str, confidence: float = 1.0):
        """Mark request as routed"""
        self.execution_path = path
        self.target_id = target
        self.confidence = confidence
        self.status = ExecutionStatus.ROUTING
        self.routed_at = time.time()

    def mark_executing(self):
        """Mark request as executing"""
        self.status = ExecutionStatus.EXECUTING
        self.started_at = time.time()

    def mark_completed(self, result: Dict[str, Any] = None):
        """Mark request as completed"""
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = time.time()
        if result:
            self.phase_results.update(result)

    def mark_failed(self, error: str):
        """Mark request as failed"""
        self.status = ExecutionStatus.FAILED
        self.completed_at = time.time()
        self.error = error

    @property
    def duration(self) -> Optional[float]:
        """Execution duration in seconds"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    @property
    def manifests(self) -> bool:
        """
        OPUS-200/201: Does this request manifest?

        True if resonance_energy > resonance_inertia.
        This replaces boolean gate checks with continuous energy.
        """
        return self.resonance_energy > self.resonance_inertia

    def mark_resonance(self, energy: float, inertia: float, field_hash: str = ""):
        """Mark request with quantum resonance values."""
        self.resonance_energy = energy
        self.resonance_inertia = inertia
        self.resonance_hash = field_hash

        # Also set legacy gate_decision based on resonance
        if energy > inertia * 1.5:
            # High energy = critical manifestation
            self.gate_decision = MilkOceanGate.CRITICAL
        elif energy > inertia:
            # Normal manifestation
            self.gate_decision = MilkOceanGate.ALLOW
        elif energy > inertia * 0.5:
            # Low energy = queue for later
            self.gate_decision = MilkOceanGate.QUEUE
        else:
            # Very low energy = doesn't manifest (soft block)
            self.gate_decision = MilkOceanGate.BLOCK
