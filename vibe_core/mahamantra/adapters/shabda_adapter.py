"""
SHABDA ADAPTER - Phoneme & Vibration Extraction
================================================

"śabda-brahma paraṁ brahma"
"Sound is Brahman, the Supreme is Brahman."

Extracts phonemes and vibration signatures from Mahamantra positions.
Clean interface to RAMA Grid + Shabda substrate modules.
"""

from __future__ import annotations

__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x2c80316d"

__all__ = ["ShabdaAdapter", "ShabdaResult"]

from dataclasses import dataclass
from typing import Optional

from vibe_core.mahamantra.substrate.phonetic_bridge import (
    PhoneticTensor,
    UniversalPhoneticBridge,
)
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    VibrationSignature,
    text_to_vibration,
)
from vibe_core.mahamantra.substrate.rama_grid import krishna_route, rama_to_phoneme


@dataclass(frozen=True)
class ShabdaResult:
    """Result from Shabda extraction."""

    phoneme: str
    rama_index: int
    vibration: Optional[VibrationSignature]
    tensor: Optional[PhoneticTensor] = None


class ShabdaAdapter:
    """
    Bridge between Mahamantra position and phonetic representation.

    Flow:
        Position (0-15) → RAMA[0-48] → Phoneme → Vibration
    """

    def __init__(self):
        self._bridge = UniversalPhoneticBridge()

    def extract(self, position: int) -> ShabdaResult:
        """
        Extract phoneme and vibration from Mahamantra position.

        Args:
            position: Mahamantra position (0-15)

        Returns:
            ShabdaResult with phoneme, RAMA index, and vibration
        """
        # Position → RAMA Grid
        rama_idx = krishna_route(position)

        # RAMA → Phoneme
        phoneme = rama_to_phoneme(rama_idx)

        # Phoneme → Vibration (returns list, take primary/first)
        vibration_list = text_to_vibration(phoneme)
        vibration = vibration_list[0] if vibration_list else None

        # Phoneme → Phonetic Analysis (optional)
        try:
            tensor = self._bridge.analyze(phoneme)
        except Exception:
            tensor = None

        return ShabdaResult(
            phoneme=phoneme,
            rama_index=rama_idx,
            vibration=vibration,
            tensor=tensor,
        )


# Singleton
_adapter: Optional[ShabdaAdapter] = None


def get_shabda_adapter() -> ShabdaAdapter:
    """Get singleton Shabda adapter."""
    global _adapter
    if _adapter is None:
        _adapter = ShabdaAdapter()
    return _adapter
