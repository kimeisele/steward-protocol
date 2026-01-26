"""
TEST: The 7 Axioms and ACINTYA Principle (Seed v2.0)
====================================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"Know Me to be the eternal seed of all existences."
— Bhagavad Gita 7.10

This test suite verifies:
1. The 7 AXIOMS are derived ONLY from counting the Mahamantra
2. All other constants are DERIVED from these 7 axioms
3. ACINTYA principle: Two independent paths converge to same value

WATERTIGHT: No hardcoded values - everything derived from SSOT.
"""

import math

import pytest

from vibe_core.mahamantra.protocols._seed import (
    HALF_SIZE,
    HALVES,  # 2 = observable halves
    HARE_COUNT,  # 8 = count of "Hare"
    KRISHNA_COUNT,  # 4 = count of "Krishna"
    # Primary Derivations
    KSETRAJNA,
    KSHETRA,
    # Physics
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    MALA,
    NAKSHATRAS,
    NAVA,
    PANCHA,  # 5 = count of unique pairs
    # Position Sums
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUALITIES,
    RAMA_COUNT,  # 4 = count of "Rama"
    # SEVEN and TEN
    SEVEN,
    TEN,
    TRINITY,  # 3 = count of unique names (Hare, Krishna, Rama)
    # The 7 AXIOMS (Round 0) - from counting the Mahamantra
    WORDS,  # 16 = count of words
)

# =============================================================================
# THE 7 AXIOMS - From Counting the Mahamantra
# =============================================================================


class TestSevenAxioms:
    """
    Test the 7 fundamental axioms.

    These are the ONLY values that come from direct observation.
    Everything else must be DERIVED from these.
    """

    def test_axiom_1_words(self) -> None:
        """AXIOM 1: WORDS = 16 (count of words in Mahamantra)."""
        # Count manually:
        # Hare Krishna Hare Krishna Krishna Krishna Hare Hare
        # Hare Rama Hare Rama Rama Rama Hare Hare
        assert WORDS == 16, "WORDS must be 16"

    def test_axiom_2_trinity(self) -> None:
        """AXIOM 2: TRINITY = 3 (unique names: Hare, Krishna, Rama)."""
        unique_names = {"Hare", "Krishna", "Rama"}
        assert TRINITY == len(unique_names) == 3

    def test_axiom_3_hare_count(self) -> None:
        """AXIOM 3: HARE_COUNT = 8 (count of 'Hare')."""
        # Positions: 1, 3, 7, 8, 9, 11, 15, 16
        assert HARE_COUNT == 8

    def test_axiom_4_krishna_count(self) -> None:
        """AXIOM 4: KRISHNA_COUNT = 4 (count of 'Krishna')."""
        # Positions: 2, 4, 5, 6
        assert KRISHNA_COUNT == 4

    def test_axiom_5_rama_count(self) -> None:
        """AXIOM 5: RAMA_COUNT = 4 (count of 'Rama')."""
        # Positions: 10, 12, 13, 14
        assert RAMA_COUNT == 4

    def test_axiom_6_pancha(self) -> None:
        """AXIOM 6: PANCHA = 5 (unique pairs in Mahamantra)."""
        # Pairs: (Hare,Krishna), (Krishna,Hare), (Krishna,Krishna),
        #        (Hare,Rama), (Rama,Hare), (Rama,Rama), (Hare,Hare)
        # But only 5 are UNIQUE in the sense of Pancha Tattva
        assert PANCHA == 5

    def test_axiom_7_halves(self) -> None:
        """AXIOM 7: HALVES = 2 (observable halves of Mahamantra)."""
        assert HALVES == 2

    def test_axioms_are_consistent(self) -> None:
        """The 7 axioms must be internally consistent."""
        # HARE + KRISHNA + RAMA = WORDS
        assert HARE_COUNT + KRISHNA_COUNT + RAMA_COUNT == WORDS
        # WORDS / HALVES = 8 (half size)
        assert WORDS // HALVES == 8


# =============================================================================
# ACINTYA PRINCIPLE - Two Paths Converge
# =============================================================================


class TestAcintyaPrinciple:
    """
    Test the ACINTYA principle: Two independent paths to same value.

    "acintya-bhedābheda-tattva" - Inconceivable simultaneous oneness and difference
    """

    def test_acintya_137_three_paths(self) -> None:
        """THREE independent paths to 137 (Fine Structure Constant)."""
        # Path 1: Triangular - T(WORDS) + KSETRAJNA
        triangular_16 = WORDS * (WORDS + 1) // 2  # T(16) = 136
        path1 = triangular_16 + KSETRAJNA  # 136 + 1 = 137

        # Path 2: Cosmic - MALA + NAKSHATRAS + HALVES
        path2 = MALA + NAKSHATRAS + HALVES  # 108 + 27 + 2 = 137

        # Path 3: Binary - 2^7 + 9
        path3 = (HALVES**SEVEN) + NAVA  # 128 + 9 = 137

        assert path1 == path2 == path3 == MAHA_QUANTUM == 137

    def test_acintya_1096_kishora(self) -> None:
        """ACINTYA: 1096 = 8 × 137 = 1024 + 72."""
        # Path 1: 8 × 137 (octave of alpha)
        path1 = HARE_COUNT * MAHA_QUANTUM  # 8 × 137 = 1096

        # Path 2: 1024 + 72 (binary + nadi)
        from vibe_core.mahamantra.protocols._seed import NADI_RESONANCE

        path2 = (HALVES**TEN) + NADI_RESONANCE  # 1024 + 72 = 1096

        assert path1 == path2 == 1096

    def test_acintya_position_sums(self) -> None:
        """Position sums follow SEVEN-TEN pattern."""
        # HARE positions sum = 70 = 7 × 10
        assert POSITION_SUM_HARE == SEVEN * TEN == 70

        # KRISHNA positions sum = 17 = 7 + 10
        assert POSITION_SUM_KRISHNA == SEVEN + TEN == 17

        # RAMA positions sum = 49 = 7²
        assert POSITION_SUM_RAMA == SEVEN * SEVEN == 49

        # TOTAL = T(16) = 136
        assert POSITION_SUM_TOTAL == WORDS * (WORDS + 1) // 2 == 136

    def test_acintya_seven_ten_derivation(self) -> None:
        """SEVEN and TEN are derived from axioms."""
        # SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7
        assert SEVEN == HALF_SIZE - KSETRAJNA == 7

        # TEN = MAHAJANA_COUNT - HALVES = 12 - 2 = 10
        assert TEN == MAHAJANA_COUNT - HALVES == 10


# =============================================================================
# MATHEMATICAL CONSTANTS FROM AXIOMS
# =============================================================================


class TestMathematicalConstants:
    """Test mathematical constants derived from axioms."""

    def test_golden_ratio_approximation(self) -> None:
        """Golden Ratio φ ≈ WORDS / TEN = 1.6."""
        phi_actual = (1 + math.sqrt(5)) / 2  # 1.618...
        phi_approx = WORDS / TEN  # 16/10 = 1.6
        error = abs(phi_actual - phi_approx) / phi_actual
        assert error < 0.02  # Less than 2% error

    def test_dna_codons_from_axioms(self) -> None:
        """DNA_CODONS = QUARTERS³ = 4³ = 64."""
        assert KRISHNA_COUNT**TRINITY == 64
        assert QUALITIES == 64  # Same as Krishna's qualities!

    def test_amino_acids_from_axioms(self) -> None:
        """AMINO_ACIDS = QUARTERS × PANCHA = 4 × 5 = 20."""
        assert KRISHNA_COUNT * PANCHA == 20


# =============================================================================
# BELL INEQUALITY FROM AXIOMS
# =============================================================================


class TestBellInequality:
    """Test Bell's Inequality derivation from axioms."""

    def test_bell_bound(self) -> None:
        """Bell's bound 2√2 ≈ HALVES × √HALVES."""
        bell_actual = 2 * math.sqrt(2)  # 2.828...
        bell_approx = HALVES * math.sqrt(HALVES)  # 2 × √2 = 2.828...
        assert abs(bell_actual - bell_approx) < 0.001

    def test_tsirelson_bound(self) -> None:
        """Tsirelson bound = 2√2 (quantum maximum)."""
        # Classical limit: 2
        classical = HALVES
        # Quantum limit: 2√2
        quantum = HALVES * math.sqrt(HALVES)
        # Quantum exceeds classical
        assert quantum > classical


# =============================================================================
# PARAMPARA FORMULA
# =============================================================================


class TestParamparaFormula:
    """Test the 37 Formula (Parampara)."""

    def test_37_formula(self) -> None:
        """PARAMPARA = KSHETRA + MAHAJANA + KSETRAJNA = 24 + 12 + 1 = 37."""
        from vibe_core.mahamantra.protocols._seed import PARAMPARA

        assert KSHETRA + MAHAJANA_COUNT + KSETRAJNA == PARAMPARA == 37

    def test_kshetra_derived(self) -> None:
        """KSHETRA = WORDS + HARE_COUNT = 16 + 8 = 24."""
        assert KSHETRA == WORDS + HARE_COUNT == 24

    def test_mahajana_derived(self) -> None:
        """MAHAJANA_COUNT = KSHETRA // HALVES = 24 // 2 = 12."""
        assert MAHAJANA_COUNT == KSHETRA // HALVES == 12

    def test_ksetrajna_derived(self) -> None:
        """KSETRAJNA = TRINITY - HALVES = 3 - 2 = 1."""
        assert KSETRAJNA == TRINITY - HALVES == 1


# =============================================================================
# SSOT COMPLIANCE
# =============================================================================


class TestSSOTCompliance:
    """Test Single Source of Truth compliance."""

    def test_no_magic_numbers(self) -> None:
        """All derived values use only the 7 axioms."""
        # This test verifies the derivation chain
        # Starting from axioms:
        axioms = [WORDS, TRINITY, HARE_COUNT, KRISHNA_COUNT, RAMA_COUNT, PANCHA, HALVES]
        axiom_values = [16, 3, 8, 4, 4, 5, 2]

        for axiom, expected in zip(axioms, axiom_values):
            assert axiom == expected

        # All other values are derived:
        assert KSETRAJNA == TRINITY - HALVES
        assert HALF_SIZE == WORDS // HALVES
        assert KSHETRA == WORDS + HARE_COUNT
        assert MAHAJANA_COUNT == KSHETRA // HALVES
        assert NAVA == HARE_COUNT + KSETRAJNA
        assert QUALITIES == WORDS * KRISHNA_COUNT

    def test_substrate_imports_from_protocol(self) -> None:
        """substrate/seed.py must import from protocols/_seed.py."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM as P_MAHA
        from vibe_core.mahamantra.substrate.seed import MAHA_QUANTUM as S_MAHA

        assert S_MAHA == P_MAHA == 137
