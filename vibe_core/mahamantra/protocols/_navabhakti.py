"""
NAVABHAKTI INSTRUCTION SET — The 9 VM Operations
===================================================

"nava-vidha bhakti" — Nine forms of devotional service (SB 7.5.23).

    sravanam kirtanam visnoh smaranam pada-sevanam
    arcanam vandanam dasyam sakhyam atma-nivedanam

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
    NAVA,
    PARAMPARA,
)


class NavaBhaktiOp(IntEnum):
    """9 VM instructions = NAVA (SB 7.5.23).

    Execution order respects data dependencies:
    SRAVANAM → KIRTANAM → PADA_SEVANAM → ARCANAM → SMARANAM →
    VANDANAM → DASYAM → SAKHYAM → ATMA_NIVEDANAM
    """
    SRAVANAM = 0        # Hearing (includes phonetic encoding)
    KIRTANAM = 1        # Chanting (compression → seed)
    PADA_SEVANAM = 2    # Serving the feet (seed → attractor)
    ARCANAM = 3         # Worship (parampara verification)
    SMARANAM = 4        # Remembering (word resonance, needs attractor)
    VANDANAM = 5        # Prayer (verse matching)
    DASYAM = 6          # Servitude (position/guardian routing)
    SAKHYAM = 7         # Friendship (cell creation + chamber)
    ATMA_NIVEDANAM = 8  # Self-surrender (reactor + akash update + result)


assert len(NavaBhaktiOp) == NAVA

# Gate index per instruction (TattvaGate.value)
GATE_INDEX: Final[Tuple[int, ...]] = (
    0,       # PARSE:    SRAVANAM
    0,       # PARSE:    KIRTANAM
    1,       # VALIDATE: PADA_SEVANAM
    1,       # VALIDATE: ARCANAM
    2,       # EXECUTE:  SMARANAM
    2,       # EXECUTE:  VANDANAM
    3,       # RESULT:   DASYAM
    4,       # SYNC:     SAKHYAM
    4,       # SYNC:     ATMA_NIVEDANAM
)

assert len(GATE_INDEX) == NAVA

# VAMSI addresses: PARAMPARA * (i + KSETRAJNA) for i in range(9)
VAMSI_ADDR: Final[Tuple[int, ...]] = tuple(
    PARAMPARA * (i + KSETRAJNA) for i in range(NAVA)
)
# = (37, 74, 111, 148, 185, 222, 259, 296, 333)

# The execution cycle — 9 steps of devotional service
CYCLE: Final[Tuple[NavaBhaktiOp, ...]] = tuple(NavaBhaktiOp(i) for i in range(NAVA))


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
