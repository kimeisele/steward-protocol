"""
AKSHARA (The Imperishable) - Syllable Physics Engine
===================================================

"na kṣarati iti akṣaraḥ" - "That which does not decay is Akshara."

This module implements the Finite State Machine (FSM) to split
continuous sound into discrete syllables based on Energy/Frequency
rather than dictionary lookups.

SOURCE OF TRUTH:
- Structure: vibe_core.reactor.matrix (OPUS-200)
- Energy: vibe_core.mahamantra.substrate.phonetics.shabda
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple

from vibe_core.reactor.matrix import (
    Varga, Sthana, analyze_phonemes, PHONEME_MATRIX
)
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    SANSKRIT_PHONEME_MAP, VibrationSignature, NADI_RESONANCE, VoicingType
)

# =============================================================================
# PHYSICS MODEL
# =============================================================================

@dataclass
class VarnaPhysics:
    """Combined physics properties of a single sound."""
    char: str
    varga: Varga          # Articulation Point (0-4)
    sthana: Sthana        # Position/Action (0-4)
    energy: int           # Frequency (Hz/Resonance ID)
    is_svara: bool        # Is it a Vowel/Nucleus capable?

    @classmethod
    def from_char(cls, char: str) -> "VarnaPhysics":
        # 1. Structure from Reactor
        # Handle case sensitivity strictly as per Matrix logic
        key = char if char in PHONEME_MATRIX else char.lower()
        if key not in PHONEME_MATRIX:
             # Fallback for now, though we should be strict
             # Default to Dental/Voiced (Generic Consonant) ?
             # Or raise/skip?
             # For robustness, we map unknown to 'space' (Null)
             varga, sthana = Varga.KANTHYA, Sthana.SPARSHA 
        else:
             varga, sthana = PHONEME_MATRIX[key]

        # 2. Energy from Shabda
        # Default to LILA (48) if unknown
        sig = SANSKRIT_PHONEME_MAP.get(char.lower())
        energy = sig.base_frequency if sig else 48
        voicing = sig.voicing if sig else VoicingType.VOICED # Default to voiced
        
        # 3. Svara Detection (PURE PHYSICS)
        # Axiom: "Svaras shine by themselves" (High Energy Nucleus)
        # Condition: Energy >= NADI (72) AND NOT Voiced-Aspirated ('h')
        # 'h' (72Hz) is the only consonant with Nadi resonance, but it is Aspirated.
        # Vowels are Voiced (2) but NOT Aspirated (3).
        
        is_high_energy = energy >= 72
        is_not_aspirated = voicing != VoicingType.VOICED_ASPIRATED
        
        is_svara = is_high_energy and is_not_aspirated
        
        return cls(char, varga, sthana, energy, is_svara)

@dataclass
class Akshara:
    """
    A Complete Syllable (Consonantal Skeleton + Vowel Soul).
    
    Structure: ONSET + NUCLEUS + CODA
    """
    onset: List[VarnaPhysics] = field(default_factory=list)
    nucleus: List[VarnaPhysics] = field(default_factory=list)
    coda: List[VarnaPhysics] = field(default_factory=list)
    
    @property
    def root(self) -> VarnaPhysics:
        """The primary consonant (first of Onset, or Nucleus if no onset)."""
        if self.onset:
            return self.onset[0]
        if self.nucleus:
            return self.nucleus[0]
        # Should not happen in valid akshara
        return self.coda[0]

    def __str__(self) -> str:
        parts = []
        parts.extend(v.char for v in self.onset)
        parts.extend(v.char for v in self.nucleus)
        parts.extend(v.char for v in self.coda)
        return "".join(parts)

# =============================================================================
# STATE MACHINE (FSM)
# =============================================================================

class SyllableState(Enum):
    START = auto()
    ONSET = auto()
    NUCLEUS = auto()
    CODA = auto()

class SyllableEngine:
    """
    Deterministic Finite Automaton for Syllable Splitting.
    No Lookups. Pure State Transition.
    """
    
    def analyze(self, text: str) -> List[Akshara]:
        stream = [VarnaPhysics.from_char(c) for c in text if c.isalpha()] # Filter punctuation
        syllables: List[Akshara] = []
        
        current = Akshara()
        state = SyllableState.START
        
        # Buffer to handle Coda move-over
        
        for i, v in enumerate(stream):
            # TRANSITION LOGIC
            
            if state == SyllableState.START:
                if v.is_svara:
                    current.nucleus.append(v)
                    state = SyllableState.NUCLEUS
                else:
                    current.onset.append(v)
                    state = SyllableState.ONSET
                    
            elif state == SyllableState.ONSET:
                if v.is_svara:
                    current.nucleus.append(v)
                    state = SyllableState.NUCLEUS
                else:
                    current.onset.append(v)
                    # Stay in ONSET (Cluster)
                    
            elif state == SyllableState.NUCLEUS:
                if v.is_svara:
                    current.nucleus.append(v)
                    # Stay in NUCLEUS (Diphthong/Extension)
                else:
                    # Lookahead: Is this a Coda or the Onset of next?
                    # Pure FSM cannot lookahead easily, but we can transition to CODA
                    # and decide later (Split Event).
                    current.coda.append(v)
                    state = SyllableState.CODA
                    
            elif state == SyllableState.CODA:
                if v.is_svara:
                    # SPLIT EVENT!
                    # The consonants in CODA actually belong to NEXT Onset.
                    # 1. Move Coda to Next
                    next_onset = current.coda
                    current.coda = [] # Clear coda from current
                    
                    # 2. Emit Current
                    syllables.append(current)
                    
                    # 3. Start New
                    current = Akshara()
                    current.onset = next_onset
                    current.nucleus.append(v) # The svara that triggered split
                    state = SyllableState.NUCLEUS
                else:
                    # Another consonant - append to Coda buffer
                    current.coda.append(v)
                    # Stay in CODA
        
        # End of Stream
        if current.nucleus or current.onset:
            syllables.append(current)
            
        return syllables

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ["Akshara", "VarnaPhysics", "SyllableEngine"]
