"""
CYCLE COMPILER — Build → Runtime Bridge
=========================================

Compiles execution cycles from registered operations.

Phase 1 (static): CYCLE = 12 fixed NavaBhaktiOps (mantra_vm.py)
Phase 3 (this):   CycleCompiler builds cycles from:
    - The 12 core NavaBhaktiOps (always present)
    - Custom ops registered at runtime via register_op()

Custom ops get VAMSI addresses above the core range (>444).
They slot into the cycle at a specified gate phase (PARSE/VALIDATE/
EXECUTE/RESULT/SYNC), running after the core ops in that phase.

This is the BUILD phase of the Realtime OS:
    1. Core ops are always compiled in
    2. Plugins/capabilities register custom ops
    3. compile() produces a frozen cycle tuple
    4. execute_cycle() dispatches it

USAGE:
    compiler = get_compiler()
    compiler.register_op("my_analysis", gate=2, handler=my_fn)
    cycle = compiler.compile()
    # cycle is now (SRAVANAM, NAMA, ..., MY_ANALYSIS, ..., ATMA_NIVEDANAM)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._navabhakti import (
    CYCLE as CORE_CYCLE,
    GATE_INDEX,
    NavaBhaktiOp,
    VAMSI_ADDR,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHAJANA_COUNT,
    PARAMPARA,
)

logger = logging.getLogger("CYCLE.COMPILER")

# Custom ops start after the core VAMSI range
# Core range: 37..444 (PARAMPARA * 1..12)
# Custom range: 481+ (PARAMPARA * 13+)
_CUSTOM_BASE: Final[int] = PARAMPARA * (MAHAJANA_COUNT + 1)  # 481


@dataclass(frozen=True)
class CompiledOp:
    """A single operation in a compiled cycle.

    Core ops have op_id < MAHAJANA_COUNT and use NavaBhaktiOp dispatch.
    Custom ops have op_id >= MAHAJANA_COUNT and use their own handler.

    condition: Optional callable(ctx) -> bool. If set and returns False,
    the op is SKIPPED. This is the Condition Bits mechanism (bits 27-30
    of the 32-bit DIW). Core ops always have condition=None (unconditional).
    """
    op_id: int          # NavaBhaktiOp value for core, sequential for custom
    name: str           # Human-readable name
    gate: int           # TattvaGate index (0-4)
    vamsi_addr: int     # VAMSI address (collision-free)
    is_core: bool       # True = NavaBhaktiOp, False = custom
    condition: Optional[Callable[[dict], bool]] = None  # None = always run


@dataclass
class CustomOp:
    """A registered custom operation."""
    name: str
    gate: int                                    # 0=PARSE, 1=VALIDATE, 2=EXECUTE, 3=RESULT, 4=SYNC
    handler: Callable[["MahamantraLotus", dict], None]  # Same signature as VM wrappers
    priority: int = 0                            # Within same gate, higher = later
    condition: Optional[Callable[[dict], bool]] = None  # None = always run


class CycleCompiler:
    """Compiles execution cycles from core + custom operations.

    Thread-safe: compile() produces an immutable tuple.
    The compiled cycle and dispatch table are frozen after compile().
    Re-register + re-compile for changes (hot reload).
    """

    def __init__(self) -> None:
        self._custom_ops: Dict[str, CustomOp] = {}
        self._next_id: int = MAHAJANA_COUNT  # First custom op ID
        self._compiled: Optional[Tuple[CompiledOp, ...]] = None
        self._dispatch: Optional[Dict[int, Callable]] = None

    def register_op(
        self,
        name: str,
        gate: int,
        handler: Callable,
        priority: int = 0,
        condition: Optional[Callable[[dict], bool]] = None,
    ) -> int:
        """Register a custom operation.

        Args:
            name: Unique name for the operation.
            gate: TattvaGate index (0=PARSE, 1=VALIDATE, 2=EXECUTE, 3=RESULT, 4=SYNC).
            handler: Function(lotus, ctx) -> None. Same signature as VM wrappers.
            priority: Ordering within same gate (higher = later). Default 0.
            condition: Optional callable(ctx) -> bool. If set and returns False,
                       the op is skipped at runtime. None = always run.

        Returns:
            The assigned op_id.

        Raises:
            ValueError: If name already registered or gate out of range.
        """
        if name in self._custom_ops:
            raise ValueError(f"Op '{name}' already registered")
        if not (0 <= gate <= 4):
            raise ValueError(f"Gate must be 0-4, got {gate}")

        self._custom_ops[name] = CustomOp(
            name=name, gate=gate, handler=handler, priority=priority,
            condition=condition,
        )
        self._compiled = None  # Invalidate
        self._dispatch = None
        op_id = self._next_id
        self._next_id += 1
        logger.info("Registered custom op: %s (gate=%d, id=%d)", name, gate, op_id)
        return op_id

    def unregister_op(self, name: str) -> bool:
        """Remove a custom operation. Returns True if found."""
        if name in self._custom_ops:
            del self._custom_ops[name]
            self._compiled = None
            self._dispatch = None
            return True
        return False

    def compile(self) -> Tuple[CompiledOp, ...]:
        """Compile the full cycle: core ops + custom ops, ordered by gate then priority.

        Returns:
            Immutable tuple of CompiledOps ready for dispatch.
        """
        if self._compiled is not None:
            return self._compiled

        # 1. Build core ops
        core_ops: List[CompiledOp] = []
        for op in CORE_CYCLE:
            core_ops.append(CompiledOp(
                op_id=op.value,
                name=op.name,
                gate=GATE_INDEX[op.value],
                vamsi_addr=VAMSI_ADDR[op.value],
                is_core=True,
            ))

        # 2. Build custom ops
        custom_sorted = sorted(
            self._custom_ops.values(),
            key=lambda c: (c.gate, c.priority, c.name),
        )
        custom_ops: List[CompiledOp] = []
        for i, cop in enumerate(custom_sorted):
            custom_ops.append(CompiledOp(
                op_id=MAHAJANA_COUNT + i,
                name=cop.name,
                gate=cop.gate,
                vamsi_addr=_CUSTOM_BASE + i * PARAMPARA,
                is_core=False,
                condition=cop.condition,
            ))

        # 3. Merge: for each gate, core ops first, then custom ops
        merged: List[CompiledOp] = []
        for gate_idx in range(5):
            # Core ops in this gate (preserve original order)
            for op in core_ops:
                if op.gate == gate_idx:
                    merged.append(op)
            # Custom ops in this gate (sorted by priority)
            for op in custom_ops:
                if op.gate == gate_idx:
                    merged.append(op)

        self._compiled = tuple(merged)

        # 4. Build dispatch table
        from vibe_core.mahamantra.substrate.mantra_vm import DISPATCH as CORE_DISPATCH
        self._dispatch = dict(CORE_DISPATCH)  # Copy core dispatch
        for i, cop in enumerate(custom_sorted):
            self._dispatch[MAHAJANA_COUNT + i] = cop.handler

        logger.info(
            "Compiled cycle: %d ops (%d core + %d custom)",
            len(self._compiled), len(core_ops), len(custom_ops),
        )
        return self._compiled

    @property
    def dispatch(self) -> Dict[int, Callable]:
        """Get the dispatch table. Compiles if needed."""
        if self._dispatch is None:
            self.compile()
        assert self._dispatch is not None
        return self._dispatch

    @property
    def custom_count(self) -> int:
        """Number of registered custom ops."""
        return len(self._custom_ops)

    @property
    def is_compiled(self) -> bool:
        """True if a compiled cycle exists (not invalidated)."""
        return self._compiled is not None


# =============================================================================
# SINGLETON
# =============================================================================

_COMPILER: Optional[CycleCompiler] = None


def get_compiler() -> CycleCompiler:
    """Get the global CycleCompiler singleton."""
    global _COMPILER
    if _COMPILER is None:
        _COMPILER = CycleCompiler()
    return _COMPILER


__all__ = ["CycleCompiler", "CompiledOp", "CustomOp", "get_compiler"]
