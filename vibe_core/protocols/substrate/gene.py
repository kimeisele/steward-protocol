"""
GENE PROTOCOL - The DNA of the Runtime
======================================

"The Code is Alive."

This module defines the genetic material (iGene) that is injected
into the runtime via Balarama (Strength) and NagaProxy (Transformation).
It carries both the Curse (Entropy) and the Cure (Mantra).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x3cf4e188"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Optional
import random

from vibe_core.protocols.substrate.byte import MantraByte


@dataclass(frozen=True)
class iGene:
    """
    Das iGene ist kein passives Datum. Es ist ein Runtime-Modifikator.
    Es wird via Balarama-Proxy in den Test injiziert.
    """

    entropy_load: float  # Kali Yuga Faktor (0.0 - 1.0)
    mantra_shield: MantraByte  # Der Schutz (DNA)
    mutation_vector: int  # Bitmask für Random Bitflips

    @property
    def is_fatal(self) -> bool:
        """
        Ramanujan Logic: Wenn Entropie > Kohärenz des Mantras -> TOD.
        """
        # Threshold Logic: Life exists if Coherence > Entropy
        # But we accept "Orange" state (Struggling) if diff is small.
        # Fatal only if Entropy explicitly overwhelms Coherence.
        return self.entropy_load > self.mantra_shield.coherence

    @classmethod
    def create_random(cls, intensity: float = 0.5) -> "iGene":
        """Generates a random gene for stress testing."""
        return cls(
            entropy_load=intensity,
            mantra_shield=MantraByte.standard_16(),  # Default Shield
            mutation_vector=random.getrandbits(32),
        )
