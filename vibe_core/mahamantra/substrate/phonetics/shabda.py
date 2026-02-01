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
from typing import Final, List, Dict, Optional

# === MAHAJANA DECLARATION ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0xea72176b"

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    NADI_RESONANCE,
    QUARTERS,
    PANCHA,
    KIRTAN_RESONANCE,
    FIELD_RESONANCE,
    WORDS,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    PRASADAM,
    JIVA_CYCLE,
    MALA,
    VENU_FREQ,
    VAMSI_FREQ,
    MURALI_FREQ,
    VINA_FUNDAMENTAL,
    FLUTE_VENU_VAMSI,
    ABHINNA_MATERIAL,
    ABHINNA_SPIRITUAL,
    KSETRAJNA,
    NAME_COMPLETE,
    OCTAVE_RATIO,
)

# =============================================================================
# VIBRATION SIGNATURE MODEL
# =============================================================================

class ArticulationPoint(IntEnum):
    """Where in the mouth the sound originates (5 points = PANCHA)."""
    KANTHA = 0  # Guttural (throat)
    TALU = 1    # Palatal (palate)
    MURDHA = 2   # Retroflex (roof)
    DANTA = 3    # Dental (teeth)
    OSHTHA = 4   # Labial (lips)

class VoicingType(IntEnum):
    """Voicing characteristics (4 types = QUARTERS)."""
    UNVOICED = 0
    UNVOICED_ASPIRATED = 1
    VOICED = 2
    VOICED_ASPIRATED = 3

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
    def mahamantra_alignment(self) -> float:
        alignment = 0.0
        if self.base_frequency == NADI_RESONANCE: alignment += 0.25
        elif self.base_frequency == FIELD_RESONANCE: alignment += 0.25
        elif self.base_frequency % NADI_RESONANCE == 0: alignment += 0.15
        if self.duration_ratio in (1, 2, 4, 8, 16, 32): alignment += 0.25
        if self.articulation.value < PANCHA and self.voicing.value < QUARTERS: alignment += 0.25
        if self.signature_id <= KIRTAN_RESONANCE: alignment += 0.25
        return min(1.0, alignment)

# =============================================================================
# SANSKRIT PHONEME MAP (The Canonical Reference)
# =============================================================================

SANSKRIT_PHONEME_MAP: Final[Dict[str, VibrationSignature]] = {
    # VOWELS
    "a": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, 72, 1),
    "ā": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, 72, 2),
    "i": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 72, 1),
    "ī": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 72, 2),
    "u": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 72, 1),
    "ū": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 72, 2),
    "e": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 108, 2),
    "ai": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 144, 2),
    "o": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 108, 2),
    "au": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 144, 2),
    # CONSONANTS (English mappings & Sanskrit equivalents)
    "k": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, 48, 1),
    "g": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, 48, 1),
    "c": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, 48, 1),
    "q": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, 48, 1),
    "j": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 48, 1),
    "r": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 48, 1),
    "l": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 48, 1),
    "t": VibrationSignature(ArticulationPoint.DANTA, VoicingType.UNVOICED, 48, 1),
    "d": VibrationSignature(ArticulationPoint.DANTA, VoicingType.VOICED, 48, 1),
    "n": VibrationSignature(ArticulationPoint.DANTA, VoicingType.VOICED, 48, 1),
    "s": VibrationSignature(ArticulationPoint.DANTA, VoicingType.UNVOICED, 36, 1),
    "z": VibrationSignature(ArticulationPoint.DANTA, VoicingType.VOICED, 36, 1),
    "p": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.UNVOICED, 48, 1),
    "b": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 48, 1),
    "m": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 48, 1),
    "f": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.UNVOICED, 48, 1),
    "v": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 48, 1),
    "w": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 48, 1),
    "y": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 54, 1),
    "h": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED_ASPIRATED, 72, 1),
    "x": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, 36, 1),
    # MAHAMANTRA SYLLABLES
    "ha": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED_ASPIRATED, 72, 1),
    "re": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 72, 1),
    "kṛ": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, 108, 1),
    "ṣṇa": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 72, 2),
    "rā": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 72, 2),
    "ma": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 48, 1),
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
        for length in [3, 2]:
            if i + length <= len(text_lower):
                chunk = text_lower[i:i+length]
                if chunk in SANSKRIT_PHONEME_MAP:
                    signatures.append(SANSKRIT_PHONEME_MAP[chunk])
                    i += length
                    found = True
                    break
        if not found:
            char = text_lower[i]
            if char in SANSKRIT_PHONEME_MAP:
                signatures.append(SANSKRIT_PHONEME_MAP[char])
            i += 1
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
