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
# Backward-compat constants - derived from mahamantra position 10
from typing import Final

from vibe_core.protocols.mahajanas.janaka import (
    CheckResult,
    CognitiveCycleProtocol,
    CycleContextState,
    CycleElement,
    CycleOwnedProtocol,
    # Cycle Protocol (WATERTIGHT)
    CyclePhase,
    CycleRegistryProtocol,
    CycleRegistryStats,
    CycleState,
    CycleStatus,
    ExecutionResult,
    ExecutionState,
    HeartbeatConfig,
    # Protocol
    JanakaProtocol,
    # Protocol Base
    JanakaProtocolBase,
    KernelConfig,
    LimitsConfig,
    NullCognitiveCycle,
    NullCycleRegistry,
    # Implementations
    NullJanaka,
    NullScheduler,
    OpusConfig,
    PhaseResult,
    PranaConfig,
    RetentionConfig,
    # Instructions
    SankalpaInstruction,
    ScheduledTask,
    Scheduler,
    SchedulerProtocol,
    # Scheduler (Task Scheduling)
    SchedulingAlgorithm,
    # === MIGRATED TYPES ===
    SessionStartConfig,
    Task,
    TaskExecutor,
    # Handler Protocol
    TaskHandler,
    TaskPriority,
    TaskStatus,
    # State Types (WATERTIGHT)
    TaskValue,
    ensure_kernel_running,
    get_last_heartbeat,
    is_kernel_running,
    load_config,
    record_heartbeat,
)

POSITION: Final[int] = 10
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "STATE_SYNC"
PARAMPARA_VECTOR: Final[int] = 407

# JanakaBase for backward compat (alias to JanakaProtocolBase)
JanakaBase = JanakaProtocolBase


def execute(input_text: str, context: dict = None) -> dict:
    """
    JANAKA EXECUTION - State Sync (Position 10)

    Stateless execution wrapper.
    OpCode: STATE_SYNC
    """
    from vibe_core.di import ServiceRegistry
    from vibe_core.protocols.mahajanas.janaka import JanakaProtocol
    from vibe_core.protocols.mahajanas.janaka.service import JanakaService

    # Use ServiceRegistry for singleton (mahamantra = force, consistent routing)
    service = ServiceRegistry.get(JanakaProtocol)
    if service is None:
        service = JanakaService()
        ServiceRegistry.register(JanakaProtocol, service)
    intent = input_text.lower().strip()

    # STATE_SYNC operations
    if "check" in intent or "status" in intent:
        state = service.get_state()
        return {"success": True, "action": "get_state", "state": state}

    if "sync" in intent:
        result = service.sync_state()
        return {"success": result, "action": "sync_state"}

    # Default: return current state
    return {
        "success": True,
        "mahajana": "janaka",
        "position": 10,
        "quarter": "karma",
        "opcode": "STATE_SYNC",
        "input": input_text,
    }


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


_fractal_getattr_fn = None


def __getattr__(name: str) -> object:
    """Explicit exports + fractal discovery fallback."""
    if name == "JanakaService":
        from vibe_core.protocols.mahajanas.janaka.service import JanakaService

        return JanakaService

    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
