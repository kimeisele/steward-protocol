"""
TASK PROTOCOL - MIGRATED TO MAHAJANA OWNERSHIP
==============================================

OWNER: Mahajana.JANAKA (The Karma Yogi)
NEW LOCATION: vibe_core.protocols.mahajanas.janaka

This file re-exports from the canonical location for backwards compatibility.
All new code should import from:
    from vibe_core.protocols.mahajanas.janaka import JanakaProtocol, Task

"King Janaka - ruled a kingdom while being internally renounced.
 He ACTS but is not BOUND by action. Karma Yoga."
"""

# Re-export from canonical Mahajana location
from vibe_core.protocols.mahajanas.janaka import (
    OWNER,
    LOTUS_POSITION,
    LOTUS_QUARTER,
    # State Types (WATERTIGHT)
    TaskValue,
    TaskStatus,
    TaskPriority,
    Task,
    ExecutionResult,
    ExecutionState,
    # Handler Protocol
    TaskHandler,
    # Protocol
    JanakaProtocol,
    # Implementations
    NullJanaka,
)

# Legacy alias: TaskProtocol → JanakaProtocol
# The old TaskProtocol was less complete, JanakaProtocol is WATERTIGHT
TaskProtocol = JanakaProtocol

__all__ = [
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    # State Types
    "TaskValue",
    "TaskStatus",
    "TaskPriority",
    "Task",
    "ExecutionResult",
    "ExecutionState",
    # Handler Protocol
    "TaskHandler",
    # Protocol (canonical)
    "JanakaProtocol",
    # Legacy alias
    "TaskProtocol",
    # Implementations
    "NullJanaka",
]
