"""
THE SHABDA COMPONENT (Frequency/Vibration Integration)
=======================================================
"Shabda Brahman" - The Primordial Sound.

Consolidated from research/shabda_translation.py.
All constants derived from _seed.py.

Responsibility:
- VibrationSignature (Articulation, Voicing, Frequency, Duration)
- Frequency ↔ Vibration ID mapping
- Sanskrit Phoneme Map (Varnamala)
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Final
from vibe_core.mahamantra.protocols._seed import (
    PANCHA, QUARTERS, NADI_RESONANCE, AKSARA_COUNT, KIRTAN_RESONANCE,
    MALA, JIVA_CYCLE, VERDI_PITCH, COSMIC_FRAME
)

# =============================================================================
# ARTICULATION & VOICING (From Shabda Research)
# =============================================================================

class ArticulationPoint(IntEnum):
    """Where in the mouth the sound originates (5 points = PANCHA)."""
    KANTHA = 0   # Guttural (throat)
    TALU = 1     # Palatal (palate)
    MURDHA = 2   # Retroflex (roof)
    DANTA = 3    # Dental (teeth)
    OSHTHA = 4   # Labial (lips)

class VoicingType(IntEnum):
    """Voicing characteristics (4 types = QUARTERS)."""
    UNVOICED = 0
    UNVOICED_ASPIRATED = 1
    VOICED = 2
    VOICED_ASPIRATED = 3

# =============================================================================
# VIBRATION SIGNATURE (The Core Data Structure)
# =============================================================================

@dataclass(frozen=True)
class VibrationSignature:
    """
    The mathematical signature of a sound.
    Maps ANY sound to Mahamantra space.
    """
    articulation: ArticulationPoint
    voicing: VoicingType
    base_frequency: int   # Relative to NADI_RESONANCE (72)
    duration_ratio: int   # Relative to AKSARA (32)

    @property
    def signature_id(self) -> int:
        """
        Unique integer ID for this vibration.
        ID = (articulation × 4 + voicing) × NADI + frequency × AKSARA + duration
        """
        base = (self.articulation.value * QUARTERS + self.voicing.value) * NADI_RESONANCE
        return base + self.base_frequency * AKSARA_COUNT + self.duration_ratio

    @property
    def mahamantra_alignment(self) -> float:
        """How well does this vibration align with Mahamantra structure?"""
        alignment = 0.0
        
        if self.base_frequency == NADI_RESONANCE:
            alignment += 0.25
        elif self.base_frequency % NADI_RESONANCE == 0:
            alignment += 0.15
            
        if self.duration_ratio in (1, 2, 4, 8, 16, 32):
            alignment += 0.25
            
        if self.articulation.value < PANCHA and self.voicing.value < QUARTERS:
            alignment += 0.25
            
        if self.signature_id <= KIRTAN_RESONANCE:
            alignment += 0.25
            
        return min(1.0, alignment)

# =============================================================================
# FREQUENCY MAPPING (Hz ↔ Vibration ID)
# =============================================================================

def frequency_to_vibration_id(freq_hz: float) -> int:
    """
    Convert a physical frequency (Hz) to its Mahamantra vibration ID.
    Uses COSMIC_FRAME (21600) as normalization constant.
    """
    normalized = freq_hz / JIVA_CYCLE
    return int(normalized * MALA) % KIRTAN_RESONANCE

def vibration_id_to_frequency(vib_id: int, base_freq: int = JIVA_CYCLE) -> float:
    """
    Convert a Mahamantra vibration ID back to physical frequency.
    """
    return base_freq * (vib_id / MALA)

# =============================================================================
# SANSKRIT PHONEME MAP (Varnamala → Vibration)
# =============================================================================

SANSKRIT_PHONEME_MAP: Final[Dict[str, VibrationSignature]] = {
    # VOWELS (svara) - pure resonance
    "a": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, 72, 1),
    "ā": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, 72, 2),
    "i": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 72, 1),
    "ī": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 72, 2),
    "u": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 72, 1),
    "ū": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 72, 2),
    "e": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 108, 2),
    "o": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 108, 2),
    
    # CONSONANTS (vyanjana) - blocked resonance (frequency = 48 = LILA)
    "k": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, 48, 1),
    "g": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.VOICED, 48, 1),
    "j": VibrationSignature(ArticulationPoint.TALU, VoicingType.VOICED, 48, 1),
    "r": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 48, 1),
    "l": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 48, 1),
    "t": VibrationSignature(ArticulationPoint.DANTA, VoicingType.UNVOICED, 48, 1),
    "d": VibrationSignature(ArticulationPoint.DANTA, VoicingType.VOICED, 48, 1),
    "n": VibrationSignature(ArticulationPoint.DANTA, VoicingType.VOICED, 48, 1),
    "p": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.UNVOICED, 48, 1),
    "b": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 48, 1),
    "m": VibrationSignature(ArticulationPoint.OSHTHA, VoicingType.VOICED, 48, 1),
    "h": VibrationSignature(ArticulationPoint.KANTHA, VoicingType.UNVOICED, 48, 1),
    "s": VibrationSignature(ArticulationPoint.DANTA, VoicingType.UNVOICED, 48, 1),
    "ṣ": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.UNVOICED, 48, 1),
    "ṇ": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 48, 1),
    "ṛ": VibrationSignature(ArticulationPoint.MURDHA, VoicingType.VOICED, 72, 1),
}

# =============================================================================
# SHABDA ENGINE (Facade)
# =============================================================================

class ShabdaEngine:
    """The Provider of Vibration Analysis."""
    
    def get_signature(self, phoneme: str) -> VibrationSignature | None:
        """Get the VibrationSignature for a Sanskrit phoneme."""
        return SANSKRIT_PHONEME_MAP.get(phoneme)
        
    def freq_to_id(self, hz: float) -> int:
        """Convert Hz to Mahamantra Vibration ID."""
        return frequency_to_vibration_id(hz)
        
    def id_to_freq(self, vib_id: int) -> float:
        """Convert Vibration ID back to Hz."""
        return vibration_id_to_frequency(vib_id)
        
    def analyze_word(self, word: str) -> list[VibrationSignature]:
        """Analyze a word into its vibration signatures."""
        return [
            sig for char in word.lower() 
            if (sig := SANSKRIT_PHONEME_MAP.get(char)) is not None
        ]
        
    def word_alignment(self, word: str) -> float:
        """Calculate average Mahamantra alignment of a word."""
        sigs = self.analyze_word(word)
        if not sigs:
            return 0.0
        return sum(s.mahamantra_alignment for s in sigs) / len(sigs)
