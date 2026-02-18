"""
NAVABHAKTI INSTRUCTION SET — The 12 VM Operations
===================================================

"nava-vidha bhakti" — Nine forms of devotion, extended to 12 (MAHAJANA_COUNT).

Each instruction maps to a VAMSI address at PARAMPARA(37) stride:
    addr = PARAMPARA * (index + KSETRAJNA)

Collision-free with THE_FLUTE_CYCLE (verified: 0 overlaps).

USAGE:
    from vibe_core.mahamantra.protocols._navabhakti import CYCLE, DISPATCH
    for op in CYCLE:
        DISPATCH[op](lotus, ctx)
"""

from __future__ import annotations

from enum import IntEnum
from typing import Callable, Dict, Final, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    MAHAJANA_COUNT,
    PARAMPARA,
)


class NavaBhaktiOp(IntEnum):
    """12 VM instructions = MAHAJANA_COUNT."""
    SRAVANAM = 0
    NAMA = 1
    KIRTANAM = 2
    PADA_SEVANAM = 3
    ARCANAM = 4
    SMARANAM = 5
    VANDANAM = 6
    DASYAM = 7
    SAKHYAM = 8
    KIRTAN = 9
    YAJNA = 10
    ATMA_NIVEDANAM = 11


assert len(NavaBhaktiOp) == MAHAJANA_COUNT

# Gate index per instruction (TattvaGate.value)
GATE_INDEX: Final[Tuple[int, ...]] = (
    0, 0, 0,    # PARSE:    SRAVANAM, NAMA, KIRTANAM
    1, 1,       # VALIDATE: PADA_SEVANAM, ARCANAM
    2, 2,       # EXECUTE:  SMARANAM, VANDANAM
    3,          # RESULT:   DASYAM
    4, 4, 4, 4, # SYNC:     SAKHYAM, KIRTAN, YAJNA, ATMA_NIVEDANAM
)

assert len(GATE_INDEX) == MAHAJANA_COUNT

# VAMSI addresses: PARAMPARA * (i + KSETRAJNA) for i in range(12)
VAMSI_ADDR: Final[Tuple[int, ...]] = tuple(
    PARAMPARA * (i + KSETRAJNA) for i in range(MAHAJANA_COUNT)
)
# = (37, 74, 111, 148, 185, 222, 259, 296, 333, 370, 407, 444)

# The fixed execution cycle (Phase 1: static, like THE_FLUTE_CYCLE)
CYCLE: Final[Tuple[NavaBhaktiOp, ...]] = tuple(NavaBhaktiOp(i) for i in range(MAHAJANA_COUNT))


@runtime_checkable
class VMCapabilityProtocol(Protocol):
    """Protocol for services that register custom ops into the Mantra VM.

    Implement this to inject custom operations into the VM execution cycle.
    The CycleCompiler discovers all VMCapability implementations at bootstrap
    and registers their ops automatically.

    USAGE:
        class MyAnalyzer:
            def vm_ops(self) -> List[VMOpDeclaration]:
                return [VMOpDeclaration(
                    name="my_analysis",
                    gate=2,  # EXECUTE phase
                    handler=self._analyze,
                    condition=lambda ctx: ctx.get("seed") is not None,
                )]

            def _analyze(self, lotus, ctx):
                ctx["my_result"] = do_analysis(ctx["seed"])
    """

    def vm_ops(self) -> List["VMOpDeclaration"]:
        """Return list of ops to register in the VM cycle."""
        ...


from dataclasses import dataclass


@dataclass(frozen=True)
class VMOpDeclaration:
    """Declaration of a custom VM operation.

    name: Unique name for the op.
    gate: TattvaGate index (0=PARSE, 1=VALIDATE, 2=EXECUTE, 3=RESULT, 4=SYNC).
    handler: Function(lotus, ctx) -> None.
    priority: Ordering within same gate (higher = later). Default 0.
    condition: Optional callable(ctx) -> bool. None = always run.
    """
    name: str
    gate: int
    handler: Callable
    priority: int = 0
    condition: Optional[Callable[[dict], bool]] = None


__all__ = [
    "NavaBhaktiOp",
    "GATE_INDEX",
    "VAMSI_ADDR",
    "CYCLE",
    "VMCapabilityProtocol",
    "VMOpDeclaration",
]
