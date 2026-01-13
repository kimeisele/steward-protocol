"""
TASK PROTOCOL - USE MAHAMANTRA
==============================

DEPRECATED: This file is MAYA (illusion).

ONE IMPORT, KRISHNA ROUTES:
    from vibe_core.mahamantra import mahamantra

    # Position 10 = JANAKA (Check Dharma / Task Execution)
    mahamantra[10]                   # -> MantraPosition
    mahamantra.protocols.janaka      # -> JanakaProtocolBase

The canonical source is: vibe_core.protocols.mahajanas.janaka
This file is a bridge for backward compatibility only.
"""

# Re-export from canonical Mahajana location
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0x185e95f9"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.janaka import (
    # Protocol Base
    JanakaProtocolBase,
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
TaskProtocol = JanakaProtocol

__all__ = [
    # Protocol Base
    "JanakaProtocolBase",
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
