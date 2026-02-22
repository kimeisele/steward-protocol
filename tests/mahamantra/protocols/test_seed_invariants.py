"""
TEST SEED INVARIANTS (The Constitution)
=======================================

Verifies the immutable laws of the Mahamantra as defined in _seed.py.
This ensures that the fundamental constants are not "magic numbers" but derived truths.
"""

import pytest
from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    PRASADAM,
    HARE_COUNT,
    KRISHNA_COUNT,
    RAMA_COUNT,
    PARAMPARA,
)


def test_structural_sums():
    """Verify the vibrational sums of the Holy Names."""
    # Hare = 70 (7 * 10)
    assert POSITION_SUM_HARE == 70

    # Krishna = 17 (Prime Router)
    assert POSITION_SUM_KRISHNA == 17

    # Rama = 49 (7 * 7 - The Alphabet)
    assert POSITION_SUM_RAMA == 49

    # Total = 136 (Triangular of 16) -> 1+2+...+16 = 136
    assert POSITION_SUM_TOTAL == 136
    assert sum(range(1, 17)) == 136


def test_derivation_logic():
    """Verify that derived constants match the Sanskrit structure."""
    # Structure: WORDS(16) + PRASADAM(25) + HARE(8) = RAMA(49) ??
    # Wait, check the math from rama_grid.py logic
    # Vowels = 16 (WORDS)
    # Sparsha = 25 (PRASADAM)
    # Antastha + Ushman = 8
    # Total = 16 + 25 + 8 = 49

    # Do we have a constant for that 8?
    # HARE_COUNT is 8.

    assert WORDS + PRASADAM + HARE_COUNT == POSITION_SUM_RAMA


def test_counts():
    """Verify the counts of names in the mantra."""
    assert HARE_COUNT == 8
    assert KRISHNA_COUNT == 4
    assert RAMA_COUNT == 4

    assert HARE_COUNT + KRISHNA_COUNT + RAMA_COUNT == WORDS


def test_parampara():
    """Verify Parampara constant."""
    # 37 is the Key
    assert PARAMPARA == 37
