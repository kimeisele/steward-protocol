"""
TEST RAMA GRID LOGIC (Hardening)
================================

Verifies the internal logic of the Rama Grid Substrate.
Ensures the "Father Algorithm" (Sanskrit Generation) is intact.
This is a deep test of the generative mechanics, not just routing.
"""
import pytest
from vibe_core.mahamantra.substrate.rama_grid import (
    SVARAS,
    SPARSHA_GRID,
    VARNAMALA_TOTAL,
    POSITION_SUM_RAMA,
    POSITION_SUM_KRISHNA,
    WORDS,
    PANCHA,
    PRASADAM,
    krishna_route,
    rama_to_phoneme,
    compute_mahajana_coordinate,
    MahajanaCoordinate
)

def test_varnamala_integrity():
    """Verify the Sanskrit Alphabet (Varnamala) structure."""
    # 1. Identity: Rama = Alphabet
    assert POSITION_SUM_RAMA == 49
    assert VARNAMALA_TOTAL == 49
    
    # 2. Vowels (Svaras) must match WORDS (16)
    assert len(SVARAS) == WORDS
    assert SVARAS[0] == "a"   # First vowel
    assert SVARAS[15] == "ḥ"  # Last modifier (Visarga)
    
    # 3. Consonants (Sparsha) must match PRASADAM (25)
    assert len(SPARSHA_GRID) == PANCHA  # 5 rows
    total_sparsha = sum(len(row.consonants) for row in SPARSHA_GRID)
    assert total_sparsha == PRASADAM
    
    # Verify specific grid items
    # Row 0: Ka-varga (Guttural)
    assert SPARSHA_GRID[0].name == "ka-varga"
    assert SPARSHA_GRID[0].consonants == ("ka", "kha", "ga", "gha", "ṅa")
    
    # Row 4: Pa-varga (Labial)
    assert SPARSHA_GRID[4].name == "pa-varga"
    assert SPARSHA_GRID[4].consonants == ("pa", "pha", "ba", "bha", "ma")

def test_krishna_router_math():
    """Verify the Krishna Router mathematics."""
    # Logic: (pos * 17) % 49
    
    # Pos 0 (1st beat) -> 0 * 17 = 0
    assert krishna_route(0) == 0
    
    # Pos 1 (2nd beat) -> 1 * 17 = 17
    assert krishna_route(1) == 17
    
    # Pos 15 (16th beat) -> 15 * 17 = 255
    # 255 % 49 = 10 (49 * 5 = 245)
    assert krishna_route(15) == 10
    
    # Verify uniqueness in first cycle (Prime router property)
    outputs = set(krishna_route(i) for i in range(16))
    assert len(outputs) == 16, "Krishna Router must map 16 inputs to 16 unique outputs"

def test_phoneme_generation():
    """Verify coordinate-to-phoneme conversion."""
    
    # 0 -> 'a' (First Vowel)
    assert rama_to_phoneme(0) == "a"
    
    # 15 -> 'ḥ' (Last Vowel marker)
    assert rama_to_phoneme(15) == "ḥ"
    
    # 16 -> 'ka' (First Consonant)
    # WORDS(16) + 0 = 16
    assert rama_to_phoneme(16) == "ka"
    
    # 40 -> 'ma' (Last Sparsha)
    # WORDS(16) + PRASADAM(25) - 1 = 40
    # Wait. 16 + 24 = 40?
    # Index 0..24. Last index is 24.
    # 16 + 24 = 40.
    assert rama_to_phoneme(40) == "ma"
    
    # 42 -> 'ra' (Semivowel)
    # 16 + 25 = 41 (ya). 42 is ra.
    assert rama_to_phoneme(42) == "ra"

def test_mahajana_computation():
    """Verify Mahajana Coordinate derivation."""
    # Brahma: Pos 2 -> Rama 17 -> 'kha'
    brahma = compute_mahajana_coordinate("brahma", 2, 1)
    
    assert brahma.name == "brahma"
    assert brahma.global_position == 2
    assert brahma.rama_primary == 17
    assert brahma.first_syllable == "b" # from "brahma"
    # Articulation should be labial because 'b' is in 'pbmfvw'
    assert brahma.articulation == "oshtha" 

    # Bhishma: Pos 12 -> Rama 40 -> 'ma'
    bhishma = compute_mahajana_coordinate("bhishma", 12, 3)
    
    assert bhishma.name == "bhishma"
    assert bhishma.global_position == 12
    assert bhishma.rama_primary == 40
    assert bhishma.first_syllable == "b"
    assert bhishma.articulation == "oshtha"
