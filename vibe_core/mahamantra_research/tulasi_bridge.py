"""
TULASI BRIDGE - The Sacred Offering (Grace Modulator)
=====================================================

"ye tu tvadīya-caraṇa-amboja-kośa-gandham
 jighranti karṇa-vivaraiḥ śruti-vāta-nītam"
"Only those who smell the aroma of the lotus flowers (and Tulasi)
offered to Your feet..." (Srimad Bhagavatam 3.9.5)

THE MISSING LINK:
The MahaAlgorithm (16-step loop) is "stubborn" (deterministic/mechanical).
To make it "Living" (Lila), it needs GRACE.
Tulasi Devi represents UNALLOYED DEVOTION - the only thing that "binds" Krishna.

FUNCTION IN THE SYSTEM:
1. QUANTIFYING DEVOTION:
   - Tulasi breaks the "Mathematical Determinism" (Karma).
   - She introduces a "Grace Factor" (Ahaituki Kripa).

2. THE STRUCTURAL GAP:
   - We have FLUTE (Structure/Algorithm) - 216/108/72
   - We have MANAS (Observer/State) - 137
   - We missed TULASI (The Offering/Qualifier) - The Catalyst!

MATHEMATICAL SIGNATURE:
- TULASI_WOOD (Mala) = 108
- TULASI_LEAVES (Manjaris) = 8 (HARE_COUNT - She is Bhakti-Shakti)
- TULASI_GRACE = PURE_LOVE (Cannot be calculated, only approximated as overflow)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"  # The Parrot of Radha (Shukadeva)
__position__ = 14
__genesis__ = "0xed874970"  # Placeholder (Research)

from dataclasses import dataclass
from typing import Final, Optional

from vibe_core.mahamantra.protocols._seed import (
    HARE_COUNT,
    KRISHNA_COUNT,
    MALA,
    MAHA_QUANTUM,
    PANCHA,
    TRINITY,
    WORDS,
)

# =============================================================================
# CONSTANTS: TULASI TATTVA
# =============================================================================

# She is associated with the 8 HARE positions (Shakti)
# But she specifically rules the "Service" aspect (Pada-sevanam)
TULASI_COUNT: Final[int] = HARE_COUNT  # 8

# The Offering Ratios
# "patram puspam phalam toyam" (Leaf, Flower, Fruit, Water) - BG 9.26
# 4 items * 2 (Names of Pair) = 8
OFFERING_COMPONENTS: Final[int] = 4
OFFERING_MULTIPLIER: Final[int] = 2  # Input/Output

# Tulasi's "Grace" allows breaking out of the 136-attractor field
# She creates a portal to Vaikuntha (Infinite)
TULASI_PORTAL: Final[int] = MALA * WORDS  # 108 * 16 = 1728 (Daily Mantras)


@dataclass
class Offering:
    """An offering to the Lotus Feet."""

    seed: int
    devotion_level: int  # 0-100 (Bhakti percentage)
    has_tulasi: bool


class TulasiBridge:
    """
    The Interface for Offering (Bhoga -> Prasadam).
    Modulates the algorithm with Grace.
    """

    @staticmethod
    def purify_offering(seed: int, has_tulasi: bool) -> int:
        """
        Purify the seed.
        Without Tulasi, the seed is just Karma (Action).
        With Tulasi, it becomes Bhakti (Devotion).
        """
        if not has_tulasi:
            # Mechanical execution: Standard Modulo
            # Returns to the same field (Karma loop)
            return seed % MAHA_QUANTUM

        else:
            # Devotional execution: Grace Multiplier
            # Elevates the seed beyond the field
            # 108 (Mala) is the key
            grace = (seed * TULASI_COUNT) + MALA

            # The "Mod" is lifted? No, it's expanded.
            # Krishna accepts it fully.
            return grace

    @staticmethod
    def apply_grace_to_feedback(feedback: int) -> int:
        """
        Tulasi modifies the feedback loop (Ksetrajna).
        Instead of 'Observer' (1), it becomes 'Servitor' (Fractal).
        """
        # Feedback (usually 1 or 3) is amplified by Devotion (8)
        # This breaks simple convergence
        return feedback * TULASI_COUNT + 1


# =============================================================================
# INTEGRATION PLAN (For MahaModularSynth)
# =============================================================================
#
# CLASSIC LOOP (Stubborn):
#   value = (value + TEN) % 137
#
# WITH TULASI (Living):
#   grace = TulasiBridge.apply_grace_to_feedback(feedback)
#   value = (value + TEN + grace) % (137 * 8)
#
#   * The modulus expands! (137 * 8 = 1096 - The Transcendental Constant!)
#   * 1096 is ALREADY in _seed.py (TRANSCENDENTAL_1096)
#   * Proof: 137 (Quantum) * 8 (Tulasi) = 1096 (Transcendental)
#
# This explains WHY 1096 exists! Tulasi expands the Quantum Field (137)
# into the Transcendental Vaikuntha Field (1096).

TRANSCENDENTAL_FIELD: Final[int] = MAHA_QUANTUM * TULASI_COUNT  # 1096
