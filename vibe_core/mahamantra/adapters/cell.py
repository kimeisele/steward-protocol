# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"  # Position 6 (Sankhya/Biology)
__position__ = 6
__genesis__ = "0xce110007"  # GenesisByte: parampara % 37 == 0

__all__ = ["MahaCell"]

import uuid
from typing import Dict, Optional, TypeVar

from vibe_core.mahamantra.protocols._seed import (
    JIVA_QUALITIES,
    MAHA_QUANTUM,
    TRINITY,
)
from vibe_core.mahamantra.protocols.cell import (
    MahaCellProtocol,
)

S = TypeVar("S")
M = TypeVar("M")


class MahaCell(MahaCellProtocol[S, M]):
    """
    The Fundamental Unit of Life & Compute (Jiva).

    Implements biological computing principles derived from the Seed:
    - 50 Qualities (Jiva Qualities)
    - Prana Energy Cycles
    - Membrane Integrity
    """

    _naga_flooded: bool = True
    _naga_gene: str = "maha_cell_adapter"

    def __init__(self, cell_id: Optional[str] = None) -> None:
        self._id = cell_id or str(uuid.uuid4())
        self._state: Optional[S] = None
        # Default energy: 100 * Quantum (13700)
        self._prana: int = MAHA_QUANTUM * 100
        # Membrane integrity starts at 1.0 (perfect)
        self._integrity: float = 1.0
        # Metabolic cycle count
        self._cycle: int = 0
        # DNA string (code/instruction)
        self._dna: str = ""
        # Liveness flag
        self._active: bool = False

    @property
    def id(self) -> str:
        return self._id

    @property
    def state(self) -> S:
        if self._state is None:
            raise RuntimeError("Cell not conceived yet (Janma required)")
        return self._state

    @property
    def membrane_integrity(self) -> float:
        return self._integrity

    @property
    def prana(self) -> int:
        return self._prana

    def conceive(self, dna: str, genesis_state: S) -> None:
        """Initialize the cell (Birth/Janma)."""
        self._dna = dna
        self._state = genesis_state
        self._active = True
        self._cycle = 0
        self._integrity = 1.0

    def metabolize(self, energy: int) -> int:
        """
        Process energy (Karma).

        Cost of living = TRINITY (3) units per cycle.
        """
        if not self._active:
            return 0

        # Metabolic cost
        cost = TRINITY
        self._prana -= cost
        self._prana += energy

        # Check starvation
        if self._prana <= 0:
            self._prana = 0
            self.apoptosis()
            return 0

        self._cycle += 1
        return self._prana

    def signal(self, message: M) -> Optional[M]:
        """
        Process incoming signal via Membrane.

        Requires integrity > 0.2 (20%).
        """
        if not self._active:
            return None

        # Membrane check
        if self._integrity < 0.2:
            return None  # Membrane too weak, signal ignored

        # In a real impl, we might mutate state or message here.
        # For now, simplistic refection.
        return message

    def mitosis(self) -> "MahaCellProtocol[S, M]":
        """
        Divide into two cells (Reproduction).

        Requires 2x Quantum Energy.
        """
        required_energy = MAHA_QUANTUM * 2
        if self._prana < required_energy:
            raise RuntimeError(f"Not enough prana for mitosis (Need {required_energy}, Has {self._prana})")

        # Split energy
        self._prana //= 2

        # Create child
        child = MahaCell[S, M]()
        if self._state is not None:
            # Clone state if possible, currently shared ref for Generic S
            child.conceive(self._dna, self._state)

        child._prana = self._prana
        return child

    def apoptosis(self) -> None:
        """Self-destruct (Death/Mrityu)."""
        self._active = False
        self._prana = 0
        self._integrity = 0.0

    def homeostasis(self) -> bool:
        """
        Maintain balance.

        Checks Prana and Integrity.
        """
        if self._prana <= 0:
            self.apoptosis()
            return False

        if self._integrity <= 0:
            self.apoptosis()
            return False

        return True

    def get_organelles(self) -> Dict[str, object]:
        return {
            "nucleus": "active" if self._active else "inactive",
            "mitochondria": f"{self._prana} prana",
            "membrane": f"{self._integrity:.2%} integrity",
            "dna_length": len(self._dna),
            "cycles": self._cycle,
            "jiva_qualities": JIVA_QUALITIES,  # 50
        }
