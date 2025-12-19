"""
OPUS-118: Canonical Circuit Types - Split-Brain Surgery

This module contains the CANONICAL definitions of shared circuit types.
Previously, these classes were duplicated across:
  - vibe_core/circuit_executor.py
  - vibe_core/cortex/engines/circuit_engine.py

The duplication caused isinstance() failures when objects created in one
module were checked against types from another.

SINGLE SOURCE OF TRUTH:
  All circuit-related code should import from this module.

Note: vibe_core/cartridges/system/auditor/tools/invariant_tool.py has
      AuditViolation (formerly InvariantViolation) which is a DIFFERENT
      type for a different purpose (auditing events vs circuit state).
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.semantic_syscalls import SyscallResult


# ============================================================================
# INVARIANT TYPES
# ============================================================================


@dataclass
class InvariantViolation:
    """
    Record of an invariant violation during circuit execution.

    This captures violations of circuit state invariants - rules that must
    hold true at specific points during circuit execution.

    Fields:
        invariant: The invariant expression that was violated
        state: The circuit state name where violation occurred
        variables: Snapshot of circuit variables at violation time
        reason: Human-readable explanation of why it failed
    """

    invariant: str
    state: str
    variables: Dict[str, Any]
    reason: str


# ============================================================================
# CIRCUIT STATE TYPES
# ============================================================================


@dataclass
class CircuitState:
    """
    Current state of circuit execution.

    Tracks the evolving state as a circuit progresses through its
    state machine.

    Fields:
        current_state: Name of the current state in the circuit
        variables: Dict of all circuit variables
        history: List of state names visited (in order)
        syscall_results: Results from executed syscalls
        is_terminal: Whether we've reached a terminal state
        output: Final output when circuit completes
    """

    current_state: str
    variables: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    syscall_results: Dict[str, "SyscallResult"] = field(default_factory=dict)
    is_terminal: bool = False
    output: Optional[Dict[str, Any]] = None


@dataclass
class CircuitExecutionResult:
    """
    Result of executing a cognitive circuit.

    Returned after a circuit completes (successfully or not).

    Fields:
        success: Whether the circuit completed successfully
        final_state: The state the circuit ended in
        output: Output data from the terminal state
        state_history: Ordered list of all states visited
        syscall_count: Number of syscalls executed
        error: Error message if failed (None if success)
    """

    success: bool
    final_state: str
    output: Dict[str, Any]
    state_history: List[str]
    syscall_count: int
    error: Optional[str] = None


# ============================================================================
# META-CIRCUIT TYPES (TASK_LEDGER, ERROR_RECOVERY)
# ============================================================================


@dataclass
class TaskLedgerEntry:
    """
    Entry in the task ledger for tracking circuit execution progress.

    Used by the MetaCircuitManager to implement TASK_LEDGER_V1 -
    tracking progress, detecting stuck states, triggering reflection.

    Fields:
        circuit_id: ID of the circuit being executed
        execution_id: Unique ID for this execution instance
        started_at: Unix timestamp when execution began
        states_visited: List of states visited (in order)
        transitions: Detailed transition records
        reflections: Records of reflection/evaluation points
        stuck_count: Counter for detecting stuck states
        last_state: Most recently visited state
        completed_at: Unix timestamp when completed (None if running)
        success: Whether execution succeeded (None if running)
    """

    circuit_id: str
    execution_id: str
    started_at: float
    states_visited: List[str] = field(default_factory=list)
    transitions: List[Dict[str, Any]] = field(default_factory=list)
    reflections: List[Dict[str, Any]] = field(default_factory=list)
    stuck_count: int = 0
    last_state: str = ""
    completed_at: Optional[float] = None
    success: Optional[bool] = None


@dataclass
class ErrorRecoveryAttempt:
    """
    Record of an error recovery attempt.

    Used by the MetaCircuitManager to implement ERROR_RECOVERY_V1 -
    tracking recovery attempts and strategies used.

    Fields:
        error_type: Classified type (transient, input_error, state_error, etc.)
        error_message: The original error message
        state: The circuit state where error occurred
        timestamp: Unix timestamp of the error
        strategy: Recovery strategy selected (retry_same, retry_adjusted, etc.)
        success: Whether recovery succeeded
        retry_count: Number of retries attempted so far
    """

    error_type: str
    error_message: str
    state: str
    timestamp: float
    strategy: str
    success: bool
    retry_count: int = 0


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "InvariantViolation",
    "CircuitState",
    "CircuitExecutionResult",
    "TaskLedgerEntry",
    "ErrorRecoveryAttempt",
]
