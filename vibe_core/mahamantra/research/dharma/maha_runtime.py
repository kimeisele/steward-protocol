"""
MAHA RUNTIME - The Mahamantra as Computation Engine
====================================================

"harer nāma harer nāma harer nāmaiva kevalam
 kalau nāsty eva nāsty eva nāsty eva gatir anyathā"

In Kali Yuga, there is NO OTHER WAY but chanting!
The Mahamantra IS the algorithm. Each invocation = 1 compute cycle.

USAGE:
    from vibe_core.mahamantra.research.dharma.maha_runtime import MahaRuntime

    runtime = MahaRuntime()
    result = runtime.chant(rounds=16)  # 16 rounds = WORDS
    print(result.total_bits)  # 236,736 bits encoded

PANCHA TATTVA PRESENCE:
    When this code runs, the names are invoked.
    NAMA = NAMI (Name = Named = IDENTICAL!)
    Maximum compute = 710,208,000 bits/day (~85 MB!)
"""

from dataclasses import dataclass
from typing import Final

from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,
    DAILY_MANTRAS,
    HALVES,
    HARE_COUNT,
    JIVA_CYCLE,
    KSETRAJNA,
    LILA,
    MAHA_QUANTUM,
    MALA,
    NADI_RESONANCE,
    NAVA,
    PANCHA,
    POSITION_SUM_KRISHNA,
    QUARTERS,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

# =============================================================================
# THE MAHAMANTRA PATTERN (The Algorithm Itself!)
# =============================================================================
# H = Hare, K = Krishna, R = Rama
# Position: 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
# Pattern:  H  K  H  K  K  K  H  H  H  R  H  R  R  R  H  H

MAHAMANTRA_PATTERN: Final[tuple[str, ...]] = (
    "H",
    "K",
    "H",
    "K",
    "K",
    "K",
    "H",
    "H",  # Krishna-half (GENESIS + DHARMA)
    "H",
    "R",
    "H",
    "R",
    "R",
    "R",
    "H",
    "H",  # Rama-half (KARMA + MOKSHA)
)

# Binary encoding: H=0, Name(K/R)=1
MAHAMANTRA_BINARY: Final[tuple[int, ...]] = (
    0,
    1,
    0,
    1,
    1,
    1,
    0,
    0,  # 01011100 = 92 (decimal)
    0,
    1,
    0,
    1,
    1,
    1,
    0,
    0,  # 01011100 = 92 (decimal)
)

# Verify pattern length
assert len(MAHAMANTRA_PATTERN) == WORDS, "Pattern must be 16 words"
assert len(MAHAMANTRA_BINARY) == WORDS, "Binary must be 16 bits"


# 1096 TRANSCENDENTAL CONSTANT (defined before class for use in dataclass)
TRANSCENDENTAL_1096: Final[int] = HARE_COUNT * MAHA_QUANTUM  # 8 × 137 = 1096

assert TRANSCENDENTAL_1096 == 1096, "1096 = 8 × 137"
assert TRANSCENDENTAL_1096 == HALVES**TEN + NADI_RESONANCE, "1096 = 1024 + 72"


@dataclass(frozen=True)
class ChantResult:
    """Result of a chanting session (compute cycle)."""

    rounds: int
    mantras: int
    bits_per_mantra: int
    total_bits: int
    sankirtan_multiplier: int
    amplified_bits: int

    @property
    def kilobytes(self) -> float:
        """Total bits as kilobytes."""
        return self.amplified_bits / 8 / 1024

    @property
    def megabytes(self) -> float:
        """Total bits as megabytes."""
        return self.amplified_bits / 8 / 1024 / 1024

    @property
    def blocks_1096(self) -> int:
        """Total compute in 1096-bit transcendental blocks."""
        return self.amplified_bits // TRANSCENDENTAL_1096


class MahaRuntime:
    """
    The Mahamantra Computation Engine.

    Each chant() call invokes the Mahamantra pattern and computes encoding.
    Pancha Tattva presence amplifies all operations!

    KEY UNIT: 1096 bits = TRANSCENDENTAL_BLOCK
        1096 = HARE_COUNT × MAHA_QUANTUM = 8 × 137
        1096 = 2^10 + NADI_RESONANCE = 1024 + 72
    """

    # Constants (from _seed.py)
    BITS_PER_MANTRA: Final[int] = MAHA_QUANTUM  # 137
    MANTRAS_PER_ROUND: Final[int] = MALA  # 108
    MINIMUM_ROUNDS: Final[int] = WORDS  # 16

    # THE 1096 TRANSCENDENTAL BLOCK (Key compute unit!)
    # 1096 = 8 × 137 = HARE_COUNT × MAHA_QUANTUM
    # 1 block = 8 mantras worth of encoding
    TRANSCENDENTAL_BLOCK: Final[int] = HARE_COUNT * MAHA_QUANTUM  # 1096
    MANTRAS_PER_BLOCK: Final[int] = HARE_COUNT  # 8

    # Multipliers
    SOLO_MULTIPLIER: Final[int] = KSETRAJNA  # 1
    CALL_RESPONSE_MULTIPLIER: Final[int] = HALVES  # 2
    PANCHA_TATTVA_MULTIPLIER: Final[int] = PANCHA  # 5
    FULL_SANKIRTAN_MULTIPLIER: Final[int] = TEN  # 10 = PANCHA × HALVES

    # Maximum (with all Nadi cycles)
    NADI_CYCLES: Final[int] = COSMIC_FRAME // NADI_RESONANCE  # 300
    MAX_MULTIPLIER: Final[int] = PANCHA * HALVES * NADI_CYCLES  # 3000

    def __init__(self, sankirtan_mode: str = "solo") -> None:
        """
        Initialize the Maha Runtime.

        Args:
            sankirtan_mode: "solo", "call_response", "pancha_tattva", "full", or "max"
        """
        self.sankirtan_mode = sankirtan_mode
        self._multiplier = self._get_multiplier(sankirtan_mode)

    def _get_multiplier(self, mode: str) -> int:
        """Get the sankirtan multiplier for the given mode."""
        multipliers = {
            "solo": self.SOLO_MULTIPLIER,
            "call_response": self.CALL_RESPONSE_MULTIPLIER,
            "pancha_tattva": self.PANCHA_TATTVA_MULTIPLIER,
            "full": self.FULL_SANKIRTAN_MULTIPLIER,
            "max": self.MAX_MULTIPLIER,
        }
        return multipliers.get(mode, self.SOLO_MULTIPLIER)

    def chant(self, rounds: int = WORDS) -> ChantResult:
        """
        Execute chanting rounds and compute encoding.

        Args:
            rounds: Number of rounds (default: WORDS = 16)

        Returns:
            ChantResult with encoding statistics
        """
        mantras = rounds * self.MANTRAS_PER_ROUND
        total_bits = mantras * self.BITS_PER_MANTRA
        amplified_bits = total_bits * self._multiplier

        return ChantResult(
            rounds=rounds,
            mantras=mantras,
            bits_per_mantra=self.BITS_PER_MANTRA,
            total_bits=total_bits,
            sankirtan_multiplier=self._multiplier,
            amplified_bits=amplified_bits,
        )

    def daily_compute(self) -> ChantResult:
        """Execute standard daily chanting (16 rounds)."""
        return self.chant(rounds=self.MINIMUM_ROUNDS)

    def maximum_compute(self) -> ChantResult:
        """Execute maximum daily compute (200 rounds = singularity!)."""
        singularity_rounds = COSMIC_FRAME // MALA  # 200
        return self.chant(rounds=singularity_rounds)

    @staticmethod
    def get_pattern() -> tuple[str, ...]:
        """Get the Mahamantra pattern."""
        return MAHAMANTRA_PATTERN

    @staticmethod
    def get_binary() -> tuple[int, ...]:
        """Get the binary encoding of the Mahamantra."""
        return MAHAMANTRA_BINARY

    @staticmethod
    def encode_quarter(quarter: int) -> tuple[str, ...]:
        """
        Get one quarter of the Mahamantra.

        Args:
            quarter: 1-4 (Q1=HKHK, Q2=KKHH, Q3=HRHR, Q4=RRHH)

        Returns:
            4-word tuple for that quarter
        """
        if quarter < 1 or quarter > QUARTERS:
            raise ValueError(f"Quarter must be 1-{QUARTERS}")
        start = (quarter - 1) * QUARTERS
        end = start + QUARTERS
        return MAHAMANTRA_PATTERN[start:end]

    def compute_1096_blocks(self, rounds: int = WORDS) -> int:
        """
        Compute in terms of 1096-bit transcendental blocks.

        1096 = HARE_COUNT × MAHA_QUANTUM = 8 × 137
        1096 = 2^10 + NADI_RESONANCE = 1024 + 72

        Args:
            rounds: Number of rounds (default: WORDS = 16)

        Returns:
            Number of 1096-bit blocks generated
        """
        result = self.chant(rounds=rounds)
        return result.blocks_1096


# =============================================================================
# VERIFICATION
# =============================================================================

# Verify constants
assert MahaRuntime.BITS_PER_MANTRA == 137, "137 = MAHA_QUANTUM"
assert MahaRuntime.MANTRAS_PER_ROUND == 108, "108 = MALA"
assert MahaRuntime.MINIMUM_ROUNDS == 16, "16 = WORDS"
assert MahaRuntime.MAX_MULTIPLIER == 3000, "3000 = max sankirtan"

# Verify daily compute
_runtime = MahaRuntime()
_daily = _runtime.daily_compute()
assert _daily.mantras == DAILY_MANTRAS, "1728 mantras daily"
assert _daily.total_bits == 236736, "236,736 bits daily (solo)"

# Verify maximum compute
_max_runtime = MahaRuntime(sankirtan_mode="max")
_max_daily = _max_runtime.daily_compute()
assert _max_daily.amplified_bits == 710208000, "710,208,000 bits max (~85 MB)"

# Verify quarters
assert MahaRuntime.encode_quarter(1) == ("H", "K", "H", "K"), "GENESIS"
assert MahaRuntime.encode_quarter(2) == ("K", "K", "H", "H"), "DHARMA"
assert MahaRuntime.encode_quarter(3) == ("H", "R", "H", "R"), "KARMA"
assert MahaRuntime.encode_quarter(4) == ("R", "R", "H", "H"), "MOKSHA"


__all__ = [
    "MAHAMANTRA_PATTERN",
    "MAHAMANTRA_BINARY",
    "ChantResult",
    "MahaRuntime",
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MAHA RUNTIME - The Mahamantra Computation Engine")
    print("=" * 60)
    print()

    # Show pattern
    print("MAHAMANTRA PATTERN:")
    print(" ".join(MAHAMANTRA_PATTERN[:8]), " | Krishna-half")
    print(" ".join(MAHAMANTRA_PATTERN[8:]), " | Rama-half")
    print()

    # Show quarters
    print("QUARTERS:")
    for i, name in enumerate(["GENESIS", "DHARMA", "KARMA", "MOKSHA"], 1):
        quarter = MahaRuntime.encode_quarter(i)
        print(f"  {i}. {name}: {' '.join(quarter)}")
    print()

    # Compute examples
    print("COMPUTE MODES:")
    for mode in ["solo", "call_response", "pancha_tattva", "full", "max"]:
        rt = MahaRuntime(sankirtan_mode=mode)
        result = rt.daily_compute()
        print(f"  {mode:15} = {result.amplified_bits:>12,} bits ({result.kilobytes:,.1f} KB)")
    print()

    print("Hare Krishna!")
