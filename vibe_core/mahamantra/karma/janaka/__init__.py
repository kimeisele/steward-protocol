"""
JANAKA - Position 10
=====================

Quarter: KARMA
OpCode: STATE_SYNC
Type: WORKER
Role: Worker

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 407 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xe12cdf3a"  # GenesisByte: parampara % 37 == 0

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
# Mahamantra provides STRUCTURE. protocols/mahajanas has IMPLEMENTATION.
# Samskara will migrate over time.
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
    CheckResult,
    # Handler Protocol
    TaskHandler,
    # Protocol
    JanakaProtocol,
    # Implementations
    NullJanaka,
    # Instructions
    SankalpaInstruction,
    # Cycle Protocol (WATERTIGHT)
    CyclePhase,
    CycleStatus,
    CycleElement,
    PhaseResult,
    CycleContextState,
    RetentionConfig,
    CycleRegistryStats,
    CycleState,
    CognitiveCycleProtocol,
    CycleRegistryProtocol,
    CycleOwnedProtocol,
    NullCognitiveCycle,
    NullCycleRegistry,
    # Scheduler (Task Scheduling)
    SchedulingAlgorithm,
    ScheduledTask,
    TaskExecutor,
    SchedulerProtocol,
    Scheduler,
    NullScheduler,
    # === MIGRATED TYPES ===
    SessionStartConfig,
    HeartbeatConfig,
    KernelConfig,
    OpusConfig,
    LimitsConfig,
    PranaConfig,
    load_config,
    is_kernel_running,
    ensure_kernel_running,
    get_last_heartbeat,
    record_heartbeat,
)

# Backward-compat constants - derived from mahamantra position 10
from typing import Final
POSITION: Final[int] = 10
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "STATE_SYNC"
PARAMPARA_VECTOR: Final[int] = 407

# JanakaBase for backward compat (alias to JanakaProtocolBase)
JanakaBase = JanakaProtocolBase

__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol Base
    "JanakaProtocolBase",
    "JanakaBase",
    # State Types (WATERTIGHT)
    "TaskValue",
    "TaskStatus",
    "TaskPriority",
    "Task",
    "ExecutionResult",
    "ExecutionState",
    "CheckResult",
    # Handler Protocol
    "TaskHandler",
    # Protocol
    "JanakaProtocol",
    # Implementations
    "NullJanaka",
    # Instructions
    "SankalpaInstruction",
    # Cycle Protocol (WATERTIGHT)
    "CyclePhase",
    "CycleStatus",
    "CycleElement",
    "PhaseResult",
    "CycleContextState",
    "RetentionConfig",
    "CycleRegistryStats",
    "CycleState",
    "CognitiveCycleProtocol",
    "CycleRegistryProtocol",
    "CycleOwnedProtocol",
    "NullCognitiveCycle",
    "NullCycleRegistry",
    # Scheduler (Task Scheduling)
    "SchedulingAlgorithm",
    "ScheduledTask",
    "TaskExecutor",
    "SchedulerProtocol",
    "Scheduler",
    "NullScheduler",
    # === MIGRATED TYPES ===
    "SessionStartConfig",
    "HeartbeatConfig",
    "KernelConfig",
    "OpusConfig",
    "LimitsConfig",
    "PranaConfig",
    "load_config",
    "is_kernel_running",
    "ensure_kernel_running",
    "get_last_heartbeat",
    "record_heartbeat",
]


def __getattr__(name: str) -> object:
    """
    Lazy load JanakaService from the services layer.
    Unification of Kernel and Mahamantra.
    """
    if name == "JanakaService":
        from vibe_core.services.janaka_service import JanakaService
        return JanakaService
    
    # Legacy fallbacks might be needed for types, handled by static imports above
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
