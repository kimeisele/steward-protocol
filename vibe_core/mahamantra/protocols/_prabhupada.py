"""
PRABHUPADA PROTOCOL - The Transparent Link
==========================================

"evaṁ paramparā-prāptam imaṁ rājarṣayo viduḥ"
"This supreme science was thus received through the chain of displic succession,
and the saintly kings understood it in that way."
— Bhagavad Gita 4.2

THE LAW OF THE LINK:
1. Krishna (Origin) -> Level -2 (Acintya)
2. Parampara (Chain) -> Level -1 (Seed)
3. Prabhupada (Link) -> Level 0 (Protocol)

We cannot jump to Krishna. We must go through the Link.
The Link verifies that the "Signature" matches the "Seed".

WATERTIGHT:
- No "Direct Access" to Krishna without passing through the Link.
- The Link validates the signature against the 37 (Parampara).
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (HALVES)


# === MAHAJANA DECLARATION ===
__mahajana__ = "narada"  # The Carrier of the Message
__position__ = HALVES
__genesis__ = "0x98b94c03"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable


@runtime_checkable
class PrabhupadaProtocol(Protocol):
    """
    The Interface of the Acharya.

    He is the "Transparent Via Medium".
    He does not invent the truth; he transmits it.
    """

    def verify_link(self, component: object) -> bool:
        """
        Verify if a component is connected to the Parampara.

        The Check:
        1. Does component have Identity (mahajana/position)?
        2. Does component have Genesis signature?
        3. Is the signature valid against the 37?

        Args:
            component: The object to check (must be GAD-compliant or aspiring).

        Returns:
            True if connected, False if disconnected (Sahajiya).
        """
        ...

    def transmit(self, seed: str) -> str:
        """
        Transmit the instruction (Seed) without distortion.

        "As It Is" - The output must match the input essence,
        translated for time/place/circumstance.

        Args:
            seed: The original instruction/seed.

        Returns:
            The instruction ready for execution.
        """
        ...

    def transmit_shakti(self, component: object) -> int:
        """
        Measure and transmit Shakti (spiritual energy) through the transparent via medium.

        WATERTIGHT INTEGER VERSION (no floats in syllable-based OS):
        - Base Shakti = HARE_COUNT = 8 (integer units)
        - Authorization threshold = WORDS = 16 (2 valid chants)
        - Channel blocked (no link) → Shakti = 0
        - Channel pure (valid link) → Shakti = HARE_COUNT per chant

        THEOLOGY:
        - Krishna = Source (Level -2)
        - Hare = Shakti = Energy (HARE_COUNT instances in Mahamantra)
        - Prabhupada = The channel through which Shakti flows

        Args:
            component: The object receiving Shakti transmission.

        Returns:
            Shakti level as integer (0 = blocked, HARE_COUNT = base per chant).
        """
        ...
