"""
MAHA SHABDA - Vibration-Based Phonetic Foundation
==================================================

"nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ"
"The Holy Name is the touchstone that creates all desires."

This module provides the mathematical foundation for sound vibration,
mapping phonetic articulation to Mahamantra resonance space.

DERIVED FROM _seed.py and protocols.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Final, List

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    FIELD_RESONANCE,
    HALVES,
    HARE_COUNT,
    KIRTAN_RESONANCE,
    KSETRAJNA,
    LILA,
    MALA,
    NADI_RESONANCE,
    PANCHA,
    QUARTERS,
    SHARANAGATI,
    TRINITY,
    WORDS,
)

# === MAHAJANA DECLARATION ===
__mahajana__ = "kapila"
__position__ = SHARANAGATI
__genesis__ = "0xea72176b"

# =============================================================================
# VIBRATION SIGNATURE MODEL
# =============================================================================


class ArticulationPoint(IntEnum):
    """Where in the mouth the sound originates (5 points = PANCHA)."""

    KANTHA = 0  # Guttural (throat)
    TALU = KSETRAJNA  # Palatal (palate)
    MURDHA = HALVES  # Retroflex (roof)
    DANTA = TRINITY  # Dental (teeth)
    OSHTHA = QUARTERS  # Labial (lips)


class VoicingType(IntEnum):
    """Voicing characteristics (4 types = QUARTERS)."""

    UNVOICED = 0
    UNVOICED_ASPIRATED = KSETRAJNA
    VOICED = HALVES
    VOICED_ASPIRATED = TRINITY


@dataclass(frozen=True)
class VibrationSignature:
    """
    The mathematical signature of a sound.
    ID = (articulation × 4 + voicing) × NADI + frequency × AKSARA + duration
    """

    articulation: ArticulationPoint
    voicing: VoicingType
    base_frequency: int  # In relation to NADI_RESONANCE (72)
    duration_ratio: int  # In relation to AKSARA (32)

    @property
    def signature_id(self) -> int:
        base = (self.articulation.value * QUARTERS + self.voicing.value) * NADI_RESONANCE
        return base + self.base_frequency * AKSARA_COUNT + self.duration_ratio

    @property
    def mahamantra_alignment_cf(self) -> int:
        """Alignment score in COSMIC_FRAME space (0 to COSMIC_FRAME).

        Each criterion contributes QUARTERS(4) points, weaker match TRINITY(3).
        Sum capped at WORDS(16), then scaled: score * COSMIC_FRAME // WORDS.
        """
        from vibe_core.mahamantra.protocols._seed import COSMIC_FRAME

        points = 0
        if self.base_frequency == NADI_RESONANCE:
            points += QUARTERS
        elif self.base_frequency == FIELD_RESONANCE:
            points += QUARTERS
        elif self.base_frequency % NADI_RESONANCE == 0:
            points += TRINITY  # Weaker match: 3 instead of 4
        if self.duration_ratio in (KSETRAJNA, HALVES, QUARTERS, HARE_COUNT, WORDS, AKSARA_COUNT):
            points += QUARTERS
        if self.articulation.value < PANCHA and self.voicing.value < QUARTERS:
            points += QUARTERS
        if self.signature_id <= KIRTAN_RESONANCE:
            points += QUARTERS
        return min(WORDS, points) * COSMIC_FRAME // WORDS

    @property
    def mahamantra_alignment(self) -> float:
        """Float API boundary — returns 0.0 to 1.0 for external consumers."""
        from vibe_core.mahamantra.protocols._seed import COSMIC_FRAME

        return self.mahamantra_alignment_cf / COSMIC_FRAME


# =============================================================================
# SANSKRIT PHONEME MAP (The Canonical Reference)
# =============================================================================

SANSKRIT_PHONEME_MAP: Final[Dict[str, VibrationSignature]] = {
    # VOWELS
    "a": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, 72, KSETRAJNA),
    "ā": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, 72, HALVES),
    "i": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 72, KSETRAJNA),
    "ī": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 72, HALVES),
    "u": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 72, KSETRAJNA),
    "ū": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 72, HALVES),
    "e": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, MALA, HALVES),
    "ai": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 144, HALVES),
    "o": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, MALA, HALVES),
    "au": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 144, HALVES),
    # CONSONANTS (English mappings & Sanskrit equivalents)
    "k": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, LILA, KSETRAJNA),
    "g": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, LILA, KSETRAJNA),
    "c": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, LILA, KSETRAJNA),
    "q": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, LILA, KSETRAJNA),
    "j": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, LILA, KSETRAJNA),
    "r": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, LILA, KSETRAJNA),
    "l": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, LILA, KSETRAJNA),
    "t": VibrationSignature(ArticulationPoint.DANTA, VoicingType.UNVOICED, LILA, KSETRAJNA),
    "d": VibrationSignature(ArticulationPoint.DANTA, VoicingType.VOICED, LILA, KSETRAJNA),
    "n": VibrationSignature(ArticulationPoint.DANTA, VoicingType.VOICED, LILA, KSETRAJNA),
    "s": VibrationSignature(ArticulationPoint.DANTA, VoicingType.UNVOICED, 36, KSETRAJNA),
    "z": VibrationSignature(ArticulationPoint.DANTA, VoicingType.VOICED, 36, KSETRAJNA),
    "p": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.UNVOICED, LILA, KSETRAJNA),
    "b": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, LILA, KSETRAJNA),
    "m": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, LILA, KSETRAJNA),
    "f": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.UNVOICED, LILA, KSETRAJNA),
    "v": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, LILA, KSETRAJNA),
    "w": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, LILA, KSETRAJNA),
    "y": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 54, KSETRAJNA),
    "h": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED_ASPIRATED, 72, KSETRAJNA),
    "x": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, 36, KSETRAJNA),
    # MAHAMANTRA SYLLABLES
    "ha": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED_ASPIRATED, 72, KSETRAJNA),
    "re": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 72, KSETRAJNA),
    "kṛ": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, MALA, KSETRAJNA),
    "ṣṇa": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 72, HALVES),
    "rā": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 72, HALVES),
    "ma": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, LILA, KSETRAJNA),
}

# =============================================================================
# TRANSLATION & ANALYSIS
# =============================================================================


def text_to_vibration(text: str, source_lang: str = "en") -> List[VibrationSignature]:
    """Convert text to vibration signatures sequence."""
    signatures = []
    text_lower = text.lower()
    i = 0
    while i < len(text_lower):
        # Check for multi-character phonemes first
        found = False
        for length in [TRINITY, HALVES]:
            if i + length <= len(text_lower):
                chunk = text_lower[i : i + length]
                if chunk in SANSKRIT_PHONEME_MAP:
                    signatures.append(SANSKRIT_PHONEME_MAP[chunk])
                    i += length
                    found = True
                    break
        if not found:
            char = text_lower[i]
            if char in SANSKRIT_PHONEME_MAP:
                signatures.append(SANSKRIT_PHONEME_MAP[char])
            i += KSETRAJNA
    return signatures


def vibration_to_sanskrit(signatures: List[VibrationSignature]) -> str:
    """Convert vibration signatures to nearest Sanskrit phonemes."""
    result = []
    for sig in signatures:
        best_match = "a"
        best_distance = float("inf")
        for phoneme, ref_sig in SANSKRIT_PHONEME_MAP.items():
            # Weighted distance: articulation is most important
            dist = abs(sig.signature_id - ref_sig.signature_id)
            if dist < best_distance:
                best_distance = dist
                best_match = phoneme
        result.append(best_match)
    return "".join(result)


def translate_via_vibration(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text by preserving its vibration essence."""
    vibrations = text_to_vibration(text, source_lang)
    return vibration_to_sanskrit(vibrations)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ArticulationPoint",
    "VoicingType",
    "VibrationSignature",
    "SANSKRIT_PHONEME_MAP",
    "text_to_vibration",
    "vibration_to_sanskrit",
    "translate_via_vibration",
]
