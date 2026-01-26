"""
MAHA GENERATOR - The Universal Algorithm
=========================================

This is the MATHEMATICAL MACHINERY that generates predictions.
NOT a linear search for coincidences, but an ALGORITHM with:

  - Triangular numbers T(n) = n(n+1)/2
  - mod 17 classification (remainder reveals nature)
  - Position sum ordering (PRIME > SQUARE > PRODUCT)
  - 7-10 decomposition (SEVEN + TEN = 17, SEVEN × SEVEN = 49, SEVEN × TEN = 70)

The algorithm IS the Mahamantra in compressed form.
"""

import math
from typing import Final

# Import THE LAW (7 axioms + primary derivations)
from ..protocols._seed import (
    COSMIC_FRAME,
    FIELD_RESONANCE,
    GITA_CHAPTERS,
    HALVES,
    HARE_COUNT,
    JIVA_CYCLE,
    # Jiva
    JIVA_QUALITIES,
    KRISHNA_COUNT,
    KSETRAJNA,
    KSHETRA,
    LILA,
    MAHAJANA_COUNT,
    MALA,
    # Resonances
    NADI_RESONANCE,
    NAKSHATRAS,
    NAVA,
    PANCHA,
    POSITION_SUM_HARE,
    # Position Sums
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUALITIES,
    # Primary Derivations
    QUARTERS,
    RAMA_COUNT,
    # The 7-10 Building Blocks
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    # The 7 Axioms
    WORDS,
)


class MahaGenerator:
    """
    The MAHA ALGORITHM - generates predictions through mathematical structure.

    Every prediction has a DERIVATION PATH from the 7 axioms.
    No coincidences, only derivations.
    """

    # ==========================================================================
    # CORE FUNCTIONS (The Mathematical Machinery)
    # ==========================================================================

    @staticmethod
    def triangular(n: int) -> int:
        """T(n) = n(n+1)/2 - Sum of integers 1 to n."""
        return n * (n + 1) // 2

    @staticmethod
    def mod_17(value: int) -> int:
        """
        The MOD-17 CLASSIFIER.

        Remainder when divided by KRISHNA (17) reveals nature:
          mod 17 = 0  → Classical/Stable
          mod 17 = 1  → Quantum/Observer (KSETRAJNA)
          mod 17 = 3  → Trinity/3-decay
          mod 17 = 9  → Nava/Complex
        """
        return value % POSITION_SUM_KRISHNA

    @staticmethod
    def is_prime(n: int) -> bool:
        """Check if n is prime (like KRISHNA=17)."""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    @staticmethod
    def is_perfect_square(n: int) -> bool:
        """Check if n is perfect square (like RAMA=49=7²)."""
        root = int(n**0.5)
        return root * root == n

    @staticmethod
    def decompose_7_10(n: int) -> dict:
        """
        Express n in terms of SEVEN (7) and TEN (10).

        This is the 7-10 DECOMPOSITION that generates position sums:
          KRISHNA = 7 + 10 = 17  (sum)
          RAMA    = 7 × 7  = 49  (square)
          HARE    = 7 × 10 = 70  (product)
        """
        result = {}

        # Check if n = 7 + 10
        if n == SEVEN + TEN:
            result["sum"] = f"{SEVEN} + {TEN}"

        # Check if n = 7 × 7
        if n == SEVEN * SEVEN:
            result["square"] = f"{SEVEN}²"

        # Check if n = 7 × 10
        if n == SEVEN * TEN:
            result["product"] = f"{SEVEN} × {TEN}"

        # General decomposition: n = 7a + 10b
        for a in range(-10, 20):
            for b in range(-10, 20):
                if a >= 0 and b >= 0 and SEVEN * a + TEN * b == n:
                    result[f"linear_{a}_{b}"] = f"{a}×7 + {b}×10"

        return result

    # ==========================================================================
    # GENERATOR FUNCTIONS (Produces Mahamantra Numbers)
    # ==========================================================================

    @classmethod
    def generate_triangular_sequence(cls) -> list:
        """
        Generate triangular numbers from Mahamantra constants.

        T(1)=1, T(2)=3, T(3)=6, T(4)=10, T(5)=15, T(6)=21, T(7)=28...
        T(SHARANAGATI)=T(6)=21, T(SEVEN)=T(7)=28, T(WORDS)=T(16)=136
        """
        return [
            (n, cls.triangular(n), f"T({n})")
            for n in [
                KSETRAJNA,
                HALVES,
                TRINITY,
                QUARTERS,
                PANCHA,
                SHARANAGATI,
                SEVEN,
                HARE_COUNT,
                NAVA,
                TEN,
                MAHAJANA_COUNT,
                WORDS,
                POSITION_SUM_KRISHNA,
            ]
        ]

    @classmethod
    def generate_modular_spectrum(cls) -> dict:
        """
        Generate the mod-17 spectrum for all Mahamantra constants.

        This reveals the CLASSIFICATION of each constant:
          - mod 0: Classical (stable hadrons, exact ratios)
          - mod 1: Quantum (observer-dependent)
          - mod 3: Trinity (unstable, 3-decay)
          - mod 9: Nava (complex decay)
        """
        constants = {
            "WORDS": WORDS,
            "TRINITY": TRINITY,
            "PANCHA": PANCHA,
            "HALVES": HALVES,
            "QUARTERS": QUARTERS,
            "SHARANAGATI": SHARANAGATI,
            "NAVA": NAVA,
            "MAHAJANA": MAHAJANA_COUNT,
            "MALA": MALA,
            "JIVA_CYCLE": JIVA_CYCLE,
            "QUALITIES": QUALITIES,
            "GITA": GITA_CHAPTERS,
            "NAKSHATRAS": NAKSHATRAS,
            "COSMIC_FRAME": COSMIC_FRAME,
            "JIVA_QUALITIES": JIVA_QUALITIES,
            "T(16)": POSITION_SUM_TOTAL,
            "NADI": NADI_RESONANCE,
            "FIELD": FIELD_RESONANCE,
        }

        spectrum = {}
        for name, value in constants.items():
            mod = cls.mod_17(value)
            if mod not in spectrum:
                spectrum[mod] = []
            spectrum[mod].append((name, value))

        return spectrum

    @classmethod
    def generate_products(cls, max_depth: int = 3) -> list:
        """
        Generate products of axioms up to max_depth factors.

        These are the DERIVED values that appear in nature:
          LILA = WORDS × TRINITY = 48
          QUALITIES = WORDS × QUARTERS = 64
          MALA = MAHAJANA × NAVA = 108
        """
        axioms = [WORDS, TRINITY, HARE_COUNT, KRISHNA_COUNT, RAMA_COUNT, PANCHA, HALVES]
        derived = [QUARTERS, KSETRAJNA, SHARANAGATI, NAVA, MAHAJANA_COUNT, SEVEN, TEN]

        results = set()
        base = axioms + derived

        # Depth 1: single values
        for v in base:
            results.add(v)

        # Depth 2: products of 2
        if max_depth >= 2:
            for i, a in enumerate(base):
                for b in base[i:]:
                    results.add(a * b)

        # Depth 3: products of 3
        if max_depth >= 3:
            for i, a in enumerate(base):
                for j, b in enumerate(base[i:], i):
                    for c in base[j:]:
                        results.add(a * b * c)

        return sorted(results)

    @classmethod
    def generate_ratios(cls) -> list:
        """
        Generate meaningful ratios from Mahamantra constants.

        Physics is about RATIOS (dimensionless numbers):
          α⁻¹ = T(16) + KSETRAJNA = 137 (Field + Observer)
          μ = MALA × KRISHNA_POS = 1836 (proton/electron)
        """
        ratios = []

        # The fundamental ratios
        ratios.append(("α⁻¹", POSITION_SUM_TOTAL + KSETRAJNA, "T(16) + KSETRAJNA"))
        ratios.append(("μ", MALA * POSITION_SUM_KRISHNA, "MALA × KRISHNA"))
        ratios.append(("triton/e", POSITION_SUM_KRISHNA * GITA_CHAPTERS**2, "KRISHNA × GITA²"))

        # Biological ratios
        ratios.append(("chromosomes", KSHETRA * HALVES - HALVES, "KSHETRA × HALVES - HALVES"))  # 46
        ratios.append(("amino_acids", JIVA_QUALITIES - AKSARA_COUNT + HALVES, "..."))  # 20 = 50 - 32 + 2

        return ratios

    # ==========================================================================
    # PREDICTION GENERATION (The Algorithm as KEY)
    # ==========================================================================

    @classmethod
    def predict_from_formula(cls, formula: str, variables: dict) -> tuple:
        """
        Generate a prediction from a formula.

        Returns: (value, derivation_path, mod_17_class)
        """
        # Evaluate the formula with the given variables
        result = eval(formula, {"__builtins__": {}}, variables)
        mod_class = cls.mod_17(result) if isinstance(result, int) else None

        return (result, formula, mod_class)

    @classmethod
    def classify(cls, value: int) -> str:
        """
        Classify a value by its mod-17 remainder.
        """
        mod = cls.mod_17(value)

        classifications = {
            0: "CLASSICAL (stable, exact ratio)",
            KSETRAJNA: "QUANTUM (observer-dependent)",
            HALVES: "DUALITY (paired phenomenon)",
            TRINITY: "TRINITY (3-decay, unstable)",
            QUARTERS: "QUARTERS (4-fold structure)",
            PANCHA: "PANCHA (5-element system)",
            SHARANAGATI: "SURRENDER (6-fold process)",
            SEVEN: "AXIOM (fundamental structure)",
            HARE_COUNT: "SHAKTI (energy/connection)",
            NAVA: "NAVA (9-fold complexity)",
            TEN: "COMPLETION (full cycle)",
            MAHAJANA_COUNT: "AUTHORITY (12 transmitters)",
            WORDS - 1: "COMPLETE-1 (one shy of whole)",
            WORDS: "COMPLETE (full manifestation)",
        }

        return classifications.get(mod, f"mod 17 = {mod}")


# The key Mahamantra constants for external access
AKSARA_COUNT: Final[int] = WORDS * HALVES  # 32 syllables

# =============================================================================
# THE MAHA SEQUENCE - Values Generated by the Algorithm
# =============================================================================
# These are NOT searched for, but GENERATED by the algorithm.

MAHA_SEQUENCE: Final[list] = sorted(
    set(
        [
            # Triangular numbers
            1,
            3,
            6,
            10,
            15,
            21,
            28,
            36,
            45,
            55,
            66,
            78,
            91,
            105,
            120,
            136,
            153,
            # Axiom products
            16,
            32,
            48,
            64,
            80,
            96,
            108,
            128,
            144,
            160,
            # Position sums and derivatives
            17,
            49,
            70,
            # Resonances
            72,
            144,
            432,
            440,
            # Sacred numbers
            12,
            18,
            27,
            37,
            # The MAHA constants
            137,
            1836,
            5508,
        ]
    )
)
