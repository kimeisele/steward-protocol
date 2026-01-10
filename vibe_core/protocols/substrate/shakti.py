"""
SHAKTI - The Three Energies
===========================

"The material energy, called maya, is also one of the multi energies of the Lord.
And we, the living entities, are also the energy, marginal energy, of the Lord.
The living entities are described as superior to material energy."
- Srila Prabhupada

The Three Energies:
1. HARA (Para Shakti) - Superior/Spiritual Energy (Hladini)
2. MAYA (Apara Shakti) - Inferior/Material Energy (External)
3. JIVA (Tatastha Shakti) - Marginal Energy (Living Entities)

When the superior marginal energy (Jiva) is in contact with
the superior energy (Hara), it is established in its happy, normal condition.
"""

from enum import Enum
from typing import Final


class ShaktiType(str, Enum):
    """
    The three energies of the Lord.

    ANTI-MAYAVAD: These are PERSONAL energies, not abstract forces.
    Hara = Srimati Radharani (The Pleasure Potency)
    """
    HARA = "hara"   # Para Shakti - Superior/Spiritual (Hladini)
    MAYA = "maya"   # Apara Shakti - Inferior/Material (External)
    JIVA = "jiva"   # Tatastha Shakti - Marginal (Living Entities)


# Energy relationships
SUPERIOR_ENERGIES: Final[tuple] = (ShaktiType.HARA,)
INFERIOR_ENERGIES: Final[tuple] = (ShaktiType.MAYA,)
MARGINAL_ENERGIES: Final[tuple] = (ShaktiType.JIVA,)


def is_spiritual(shakti: ShaktiType) -> bool:
    """Check if energy is spiritual (superior)."""
    return shakti == ShaktiType.HARA


def is_material(shakti: ShaktiType) -> bool:
    """Check if energy is material (inferior)."""
    return shakti == ShaktiType.MAYA


def is_marginal(shakti: ShaktiType) -> bool:
    """Check if energy is marginal (living entity)."""
    return shakti == ShaktiType.JIVA


__all__ = [
    "ShaktiType",
    "SUPERIOR_ENERGIES",
    "INFERIOR_ENERGIES",
    "MARGINAL_ENERGIES",
    "is_spiritual",
    "is_material",
    "is_marginal",
]
