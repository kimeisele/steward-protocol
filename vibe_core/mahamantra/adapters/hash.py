"""
DETERMINISTIC HASH - Intent-to-Integer Encoding
================================================

Enterprise-compatible wrapper for MahaOracle intent encoding.

WHAT IT IS:
    A deterministic hash function that encodes strings to integers
    using position-weighted character encoding.

WHY IT'S SPECIAL:
    - Deterministic: Same input → same output (always)
    - Triangular weighting: Earlier characters matter more
    - Multiple "lenses": Same input viewed through different mod spaces
    - Parampara validation: Disciplic chain verification (mod 37 check)

THE MATH:
    hash(s) = Σ(char_value × T(position)) mod space
    where T(n) = n(n+1)/2 (triangular number)

LENSES (7 views of same input):
    TRINITY (3), PANCHA (5), SEVEN (7), PRIME (17),
    PARAMPARA (37), PRIME_73 (73), MAHA_QUANTUM (137)

USAGE:
    hasher = DeterministicHash()

    # Simple hash
    h = hasher.hash("my_intent")
    print(h)  # integer in [0, 137)

    # Multi-lens analysis
    reading = hasher.analyze("my_intent")
    print(reading.primary_hash)
    print(reading.lenses)  # 7 different views

    # Parampara validation (disciplic chain check)
    is_valid = hasher.validate_parampara("my_intent")
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "narada"
__position__ = 3
__genesis__ = "0x36552212"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Final, Tuple, Optional

from vibe_core.mahamantra.protocols.hash import (
    MahaHashProtocol,
    HashResult,
    LensReading,
    MultiLensReading,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    TRINITY,
    PANCHA,
    SEVEN,
)


# =============================================================================
# CONSTANTS
# =============================================================================

# The 7 sacred lenses (mod spaces)
LENSES: Final[Tuple[Tuple[str, int], ...]] = (
    ("TRINITY", TRINITY),        # 3 - minimal
    ("PANCHA", PANCHA),          # 5 - five elements
    ("SEVEN", SEVEN),            # 7 - effects
    ("PRIME_17", 17),            # 17 - first prime in chain
    ("PARAMPARA", PARAMPARA),    # 37 - disciplic chain
    ("PRIME_73", 73),            # 73 - third prime in chain
    ("MAHA_QUANTUM", MAHA_QUANTUM),  # 137 - full quantum
)


# =============================================================================
# THE ADAPTER
# =============================================================================

class DeterministicHash(MahaHashProtocol):
    """
    Deterministic Intent-to-Integer Hash Function.

    Uses triangular position weighting for character encoding.
    Same algorithm as MahaOracle, enterprise naming.
    """

    _naga_flooded: bool = True
    _naga_gene: str = "deterministic_hash_adapter"

    def __init__(self, default_mod: int = MAHA_QUANTUM) -> None:
        self.default_mod = default_mod

    @staticmethod
    def triangular(n: int) -> int:
        """Triangular number T(n) = n(n+1)/2."""
        return n * (n + 1) // 2

    def encode(self, text: str) -> int:
        """
        Encode string to integer using position-weighted scheme.

        Args:
            text: Input string

        Returns:
            Raw integer encoding (not yet mod'd)
        """
        total = 0
        for i, char in enumerate(text.lower()):
            # Position 1-indexed, weight by triangular number
            pos = i + 1
            char_val = ord(char) - ord('a') + 1 if char.isalpha() else ord(char)
            total += char_val * self.triangular(pos)
        return total

    def hash(self, text: str, mod_space: Optional[int] = None) -> int:

        """
        Hash string to integer in [0, mod_space).

        Args:
            text: Input string
            mod_space: Modular space (default: 137)

        Returns:
            Hash value
        """
        if mod_space is None:
            mod_space = self.default_mod
        return self.encode(text) % mod_space

    def hash_to_result(self, text: str, mod_space: Optional[int] = None) -> HashResult:
        """Hash with full result object."""
        if mod_space is None:
            mod_space = self.default_mod
        return HashResult(
            input=text,
            value=self.hash(text, mod_space),
            mod_space=mod_space,
        )

    def analyze(self, text: str) -> MultiLensReading:
        """
        Analyze input through all 7 lenses.

        Returns multi-dimensional view of the input.
        """
        seed = self.encode(text)

        # Calculate each lens
        lens_readings = tuple(
            LensReading(name=name, mod_space=mod, value=seed % mod)
            for name, mod in LENSES
        )

        # Find holographic factors (values appearing in multiple lenses)
        values = [lr.value for lr in lens_readings]
        from collections import Counter
        counts = Counter(values)
        holographic = tuple(v for v, c in counts.items() if c > 1)

        return MultiLensReading(
            input=text,
            seed=seed,
            primary_hash=seed % MAHA_QUANTUM,
            lenses=lens_readings,
            parampara_validated=(seed % PARAMPARA == 0),
            holographic_factors=holographic,
        )

    def validate_parampara(self, text: str) -> bool:
        """
        Check if input passes disciplic chain validation.

        The Parampara check: seed % 37 == 0
        Represents alignment with the disciplic succession.
        """
        return self.encode(text) % PARAMPARA == 0


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def deterministic_hash(text: str, mod_space: int = MAHA_QUANTUM) -> int:
    """Quick hash function."""
    return DeterministicHash().hash(text, mod_space)


def multi_lens_hash(text: str) -> MultiLensReading:
    """Quick multi-lens analysis."""
    return DeterministicHash().analyze(text)


__all__ = [
    "DeterministicHash",
    "HashResult",
    "LensReading",
    "MultiLensReading",
    "deterministic_hash",
    "multi_lens_hash",
    "MahaHash",
]

MahaHash = DeterministicHash
