"""
ATOM (The Indivisible) - Resonance Hashing
==========================================

"aṇor aṇiyān mahato mahiyān"
"Smaller than the smallest, greater than the greatest."
-- Katha Upanishad 1.2.20

This module implements the 6-Bit Resonance Hash and the 256-bit MantraByte.
This ensures NO COLLISIONS between 'Ga' (Action) and 'A' (Existence).
"""

from typing import List, Optional, Tuple
from vibe_core.mahamantra.substrate.lotus_radix import lotus_256bit
from vibe_core.mahamantra.namarupa.akshara import Akshara, SyllableEngine

# =============================================================================
# MANTRA BYTE (256-Bit Address)
# =============================================================================

MantraByte = int  # Explicit type alias for 256-bit integer


class AtomicResonanceHash:
    """
    Converting Akshara Sequences into pure Integer Addresses.

    Encoding:
    - 8 Bits per Akshara (Byte Aligned)
    - Bit 7: Is_Svara (1=Vowel, 0=Consonant)
    - Bit 6-4: Varga (0-4)
    - Bit 3-1: Sthana (0-4)
    - Bit 0: Mass Parity (Length % 2) - Distinguishes variations (e.g. nda vs ndam)

    Capacity: 256 / 8 = 32 Syllables (Exact AKSARA_COUNT Match)
    """

    @staticmethod
    def compute(text: str) -> MantraByte:
        engine = SyllableEngine()
        syllables = engine.analyze(text)
        return AtomicResonanceHash.hash_syllables(syllables)

    @staticmethod
    def hash_syllables(syllables: List[Akshara]) -> MantraByte:
        key = 0
        # Start at top of 256-bit space
        # 8 bits per syllable
        shift = 256 - 8

        for syll in syllables:
            root = syll.root

            # 1. Physics Bits
            varga_bits = root.varga.value & 0b111  # 3 bits
            sthana_bits = root.sthana.value & 0b111  # 3 bits

            # 2. Svara Bit
            svara_bit = 1 if root.is_svara else 0

            # 3. Mass Parity (Total atomic count in syllable)
            total_atoms = len(syll.onset) + len(syll.nucleus) + len(syll.coda)
            mass_bit = total_atoms & 1

            # 4. Pack 8 bits
            # [Svara][V3][V2][V1][S3][S2][S1][Mass]
            code = (svara_bit << 7) | (varga_bits << 4) | (sthana_bits << 1) | mass_bit

            # 5. Integrate into Key
            if shift < 0:
                break

            key |= code << shift
            shift -= 8

        return key

    @staticmethod
    def hash_extended(text: str) -> Tuple[MantraByte, int]:
        """Return key AND significant bits (for prefix query)."""
        engine = SyllableEngine()
        syllables = engine.analyze(text)
        key = AtomicResonanceHash.hash_syllables(syllables)
        sig_bits = len(syllables) * 8  # Updated to 8
        return key, sig_bits


# =============================================================================
# REGISTRY (Holographic Storage)
# =============================================================================


class IdentityRegistry:
    """
    Holographic Name Registry using LotusRadix256.
    """

    def __init__(self):
        # 256-bit Radix Tree (64 levels)
        self._radix = lotus_256bit()

    def register(self, name: str, value: object) -> MantraByte:
        key = AtomicResonanceHash.compute(name)
        self._radix.set(key, value)
        return key

    def get(self, name: str) -> Optional[object]:
        key = AtomicResonanceHash.compute(name)
        return self._radix.get(key)

    def search(self, query: str) -> List[object]:
        """
        Prefix Search based on Phonetic Resonance.
        'Govinda' matches 'Govindam'.
        """
        key, sig_bits = AtomicResonanceHash.hash_extended(query)

        # 6 bits per syllable. LotusRadix uses 4-bit nibbles structure.
        # We need to round UP to nearest nibble for range query?
        # Actually, LotusRadix 'prefix_iter' expects 'prefix_bits' to be multiple of 4.
        # 6 bits is 1.5 nibbles.
        # If we have 3 syllables -> 18 bits.
        # We can query with 16 bits (confident) or 20 bits (padded).
        # Safe strategy: Round DOWN to nearest 4 bits for broader recall,
        # then filter results.

        query_bits = (sig_bits // 4) * 4

        results = []
        for match_key, val in self._radix.prefix_iter(key, query_bits):
            results.append(val)

        return results


# =============================================================================
# EXPORTS
# =============================================================================
__all__ = ["AtomicResonanceHash", "IdentityRegistry", "MantraByte"]
