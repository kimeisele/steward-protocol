"""
Unified State Schemas - Layer 2: Core Data Structures

OPUS-211: Structural Consolidation

This module provides the canonical definitions for common state structures
to eliminate duplication across the codebase.

"Fragmentation is the source of Tamas. Unity is the path to Sattva."
"""

from __future__ import annotations

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
