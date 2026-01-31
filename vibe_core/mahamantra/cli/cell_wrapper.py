"""
MAHACELL CLI WRAPPER - The Interface
====================================

"All interaction is Yajna."

Wraps raw CLI commands into MahaCells, ensuring every interaction
flows through the Sankirtan Chamber.

Pattern:
    CLI Args -> Compression -> MahaCell -> Chamber -> Result -> Console
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "arjuna"
__position__ = 2
__genesis__ = "0xc8e2b91a"

from typing import List, Final

from vibe_core.mahamantra.protocols._seed import WORDS
from vibe_core.mahamantra.substrate.cell import MahaCellUnified
from vibe_core.mahamantra.substrate.chamber import SankirtanChamber
from vibe_core.mahamantra.adapters.compression import MahaCompression

class MahaCellCLI:
    """
    MahaCell as universal CLI wrapper.

    Every CLI operation creates/transforms MahaCells.
    This enforces the "Everything is a Cell" paradigm.
    """

    def __init__(self) -> None:
        self._chamber = SankirtanChamber.create()
        self._compression = MahaCompression()

    def wrap(self, command: str, args: List[str]) -> MahaCellUnified:
        """
        Wrap a CLI command as MahaCell.

        Input text -> MahaCompression -> Seed -> MahaCell
        """
        # Join input
        full_input = f"{command} {' '.join(args)}".strip()
        
        # Compress to find Intent (Seed)
        # Using MahaCompression (from adapters/compression.py)
        result = self._compression.compress(full_input)

        # Create the Cell
        # Source: Position from compression (Intent Source)
        # Target: 0 (Will be set by Chamber/Attractor)
        # Operation: Hash of command mapped to 16 words (Functional Slot)
        # Intent: The compressed seed
        # DNA: The original command string
        op_code = hash(command) % WORDS
        
        cell = MahaCellUnified.create(
            source=result.position,
            target=0,
            operation=op_code,
            dna=full_input, 
            initial_state=full_input # Payload is the command
        )
        
        return cell

    def execute(self, cell: MahaCellUnified) -> MahaCellUnified:
        """
        Execute a MahaCell command through the Chamber.

        The Chamber transforms the cell via the Orchestrator/Registry.
        Returns the transformed Result Cell.
        """
        # 1. Enter the Chamber
        # In the unified architecture, cells flow through.
        # kirtan() runs the transformation cycle.
        
        # We run 1 full cycle (16 steps) to ensure processing
        result_cell = self._chamber.kirtan(cell, cycles=1)

        return result_cell

    def unwrap(self, cell: MahaCellUnified) -> str:
        """
        Extract result from MahaCell.
        
        If the payload changed, return it.
        Otherwise, return a formatted string of the transformation.
        """
        # In a real system, the payload would be the result of the command execution.
        # For now, the Chamber transforms the METADATA (Prana, Integrity, Header).
        # We return a report of the transformation.
        
        return (
            f"=== MAHA EXECUTION ===\n"
            f"Command: {cell.lifecycle.dna}\n"
            f"State:   Active={cell.is_alive} Cycle={cell.lifecycle.cycle}\n"
            f"Prana:   {cell.prana} (Integrity: {cell.membrane_integrity:.2%})\n"
            f"Result:  {cell.header.target} (Attractor)\n"
        )

