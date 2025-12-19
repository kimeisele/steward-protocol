"""
OPUS-120: LEGACY PROXY - LOGIC FUSION
=====================================

This module is a BACKWARD COMPATIBILITY FACADE.

The actual implementation has moved to the Cortex:
  -> vibe_core/cortex/engines/circuit_engine.py

Previously, this file contained ~1400 lines of code that was 99.5% identical
to circuit_engine.py - a classic Split-Brain problem. OPUS-118 unified the
TYPES, and now OPUS-120 unifies the LOGIC.

"The shell remains, but the ghost has moved to the Cortex."

WHY THIS EXISTS:
  - Existing code imports from `vibe_core.circuit_executor`
  - We don't want to break those imports
  - But we don't want duplicate code either
  - Solution: This file re-exports everything from the canonical location

CANONICAL LOCATION:
  vibe_core/cortex/engines/circuit_engine.py

MIGRATION PATH:
  Old: from vibe_core.circuit_executor import CognitiveCircuitExecutor
  New: from vibe_core.cortex.engines import CognitiveCircuitExecutor

Both work. The new path is preferred for new code.
"""

# =============================================================================
# RE-EXPORT FROM CANONICAL CORTEX LOCATION
# =============================================================================

# Re-export canonical types
from vibe_core.circuit_types import (  # noqa: F401
    CircuitExecutionResult,
    CircuitState,
    ErrorRecoveryAttempt,
    InvariantViolation,
    TaskLedgerEntry,
)

# Import everything from the Cortex engine (the canonical location)
from vibe_core.cortex.engines.circuit_engine import (  # noqa: F401
    CognitiveCircuitExecutor,
    InvariantChecker,
    MetaCircuitManager,
    create_circuit_executor,
    create_circuit_executor_with_meta,
)

# =============================================================================
# __all__ FOR EXPLICIT EXPORTS
# =============================================================================

__all__ = [
    # Classes
    "CognitiveCircuitExecutor",
    "InvariantChecker",
    "MetaCircuitManager",
    # Types (from circuit_types.py)
    "CircuitState",
    "CircuitExecutionResult",
    "InvariantViolation",
    "TaskLedgerEntry",
    "ErrorRecoveryAttempt",
    # Factory functions
    "create_circuit_executor",
    "create_circuit_executor_with_meta",
]
