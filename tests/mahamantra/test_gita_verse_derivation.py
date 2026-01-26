"""
Tests for Gita Verse Derivation - Reverse Expansive Compression
===============================================================

100% SSOT-konform: Alle Werte aus _seed.py abgeleitet.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    CHAITANYA_BIRTH,
    EPOCH_KEY,
    GITA_CHAPTERS,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    NADI_RESONANCE,
    NAVA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_KRISHNA,
    QUALITIES,
    QUARTERS,
    SEVEN,
    TEN,
    TRINITY,
    WORDS,
)
from vibe_core.mahamantra.research.gita_verse_derivation import (
    ACINTYA_13_35,
    CHAPTER_FORMULAS,
    DERIVED_VERSES_COUNT,
    GITA_ARC,
    KEY_VERSES,
    PRABHUPADA_ACTIVE_YEARS,
    PRABHUPADA_AMERICA,
    PRABHUPADA_APPEARANCE,
    PRABHUPADA_DEPARTURE,
    TOTAL_GITA_VERSES,
    DerivedVerse,
)


class TestHistoricalAnchors:
    """Test historical anchor years - all derived from axioms."""

    def test_chaitanya_birth(self) -> None:
        """Chaitanya Mahaprabhu appeared in 1486."""
        assert CHAITANYA_BIRTH == 1486

    def test_prabhupada_appearance(self) -> None:
        """Prabhupada appeared in 1896 = EPOCH_KEY - (NADI + QUARTERS)."""
        expected = EPOCH_KEY - (NADI_RESONANCE + QUARTERS)
        assert PRABHUPADA_APPEARANCE == expected == 1896

    def test_prabhupada_america(self) -> None:
        """Prabhupada arrived America 1965 = EPOCH_KEY - SEVEN."""
        expected = EPOCH_KEY - SEVEN
        assert PRABHUPADA_AMERICA == expected == 1965

    def test_epoch_key(self) -> None:
        """Gita As It Is published 1972 = EPOCH_KEY."""
        assert EPOCH_KEY == 1972

    def test_prabhupada_departure(self) -> None:
        """Prabhupada departed 1977 = EPOCH_KEY + PANCHA."""
        expected = EPOCH_KEY + PANCHA
        assert PRABHUPADA_DEPARTURE == expected == 1977

    def test_prabhupada_active_years(self) -> None:
        """Prabhupada was active 12 years = MAHAJANA_COUNT."""
        assert PRABHUPADA_ACTIVE_YEARS == MAHAJANA_COUNT == 12


class TestChapterFormulas:
    """Test chapter derivations from axioms."""

    def test_all_18_chapters_derived(self) -> None:
        """All 18 chapters have formulas."""
        assert len(CHAPTER_FORMULAS) == GITA_CHAPTERS == 18

    def test_chapter_1_ksetrajna(self) -> None:
        """Chapter 1 = KSETRAJNA = 1 (observer begins)."""
        assert KSETRAJNA == 1

    def test_chapter_4_quarters(self) -> None:
        """Chapter 4 = QUARTERS = 4 (Jnana Yoga)."""
        assert QUARTERS == 4

    def test_chapter_13_kshetra_ksetrajna(self) -> None:
        """Chapter 13 = MAHAJANA + KSETRAJNA = 12 + 1 = 13."""
        assert MAHAJANA_COUNT + KSETRAJNA == 13

    def test_chapter_15_purushottama(self) -> None:
        """Chapter 15 = PANCHA × TRINITY = 5 × 3 = 15."""
        assert PANCHA * TRINITY == 15

    def test_chapter_17_krishna_position(self) -> None:
        """Chapter 17 = POSITION_SUM_KRISHNA = 17."""
        assert POSITION_SUM_KRISHNA == 17

    def test_chapter_18_final(self) -> None:
        """Chapter 18 = GITA_CHAPTERS = 18."""
        assert GITA_CHAPTERS == 18


class TestKeyVerses:
    """Test key verse derivations."""

    def test_verse_count(self) -> None:
        """16 key verses are derived."""
        assert DERIVED_VERSES_COUNT == 16

    def test_bg_2_7_surrender(self) -> None:
        """BG 2.7 = (HALVES, SEVEN) = (2, 7)."""
        verse = KEY_VERSES[0]
        assert verse.chapter == HALVES == 2
        assert verse.verse == SEVEN == 7

    def test_bg_4_34_guru(self) -> None:
        """BG 4.34 = (QUARTERS, 2×KRISHNA_POS) = (4, 34)."""
        verse = KEY_VERSES[3]
        assert verse.chapter == QUARTERS == 4
        assert verse.verse == HALVES * POSITION_SUM_KRISHNA == 34

    def test_bg_10_8_source(self) -> None:
        """BG 10.8 = (TEN, HARE_COUNT) = (10, 8)."""
        verse = KEY_VERSES[6]
        assert verse.chapter == TEN == 10
        assert verse.verse == HARE_COUNT == 8

    def test_bg_13_35_key(self) -> None:
        """BG 13.35 = (13, 35) - Prabhupada's key verse."""
        verse = KEY_VERSES[9]
        assert verse.chapter == MAHAJANA_COUNT + KSETRAJNA == 13
        assert verse.verse == SEVEN * PANCHA == 35

    def test_bg_18_66_sarva_dharman(self) -> None:
        """BG 18.66 = (18, 66) - The surrender verse."""
        verse = KEY_VERSES[14]
        assert verse.chapter == GITA_CHAPTERS == 18
        assert verse.verse == QUALITIES + HALVES == 66

    def test_bg_18_73_confirmation(self) -> None:
        """BG 18.73 = (18, 73) - Arjuna's confirmation."""
        verse = KEY_VERSES[15]
        assert verse.chapter == GITA_CHAPTERS == 18
        assert verse.verse == NADI_RESONANCE + KSETRAJNA == 73


class TestAcintyaConvergence:
    """Test ACINTYA principle - multiple paths converge."""

    def test_bg_13_35_three_paths(self) -> None:
        """BG 13.35 has THREE independent derivation paths."""
        assert len(ACINTYA_13_35.paths) == 3

    def test_path_1_seven_pancha(self) -> None:
        """Path 1: SEVEN × PANCHA = 7×5 = 35."""
        assert SEVEN * PANCHA == 35

    def test_path_2_parampara_halves(self) -> None:
        """Path 2: PARAMPARA - HALVES = 37-2 = 35."""
        assert PARAMPARA - HALVES == 35

    def test_path_3_krishna_pos(self) -> None:
        """Path 3: KRISHNA_POS × HALVES + KSETRAJNA = 17×2+1 = 35."""
        assert POSITION_SUM_KRISHNA * HALVES + KSETRAJNA == 35

    def test_all_paths_converge(self) -> None:
        """All three paths give the same result."""
        path1 = SEVEN * PANCHA
        path2 = PARAMPARA - HALVES
        path3 = POSITION_SUM_KRISHNA * HALVES + KSETRAJNA
        assert path1 == path2 == path3 == 35


class TestGitaArc:
    """Test the narrative arc of the Gita."""

    def test_arc_has_six_stages(self) -> None:
        """The arc has 6 stages."""
        assert len(GITA_ARC) == 6

    def test_arc_progression(self) -> None:
        """Arc progresses from Chapter 2 to 18."""
        chapters = [GITA_ARC[key].chapter for key in GITA_ARC]
        assert chapters[0] < chapters[-1]  # Start < End
        assert chapters[0] == 2  # Starts at BG 2.7
        assert chapters[-1] == 18  # Ends at BG 18.73


class TestDerivedVerseValidity:
    """Test that all derived verses are valid."""

    def test_all_verses_valid(self) -> None:
        """All derived verses have valid chapter/verse numbers."""
        for verse in KEY_VERSES:
            assert verse.verify(), f"{verse.reference} is invalid"
            assert 1 <= verse.chapter <= 18
            assert 1 <= verse.verse <= 78  # Max verses in any chapter

    def test_all_verses_have_meaning(self) -> None:
        """All derived verses have a meaning."""
        for verse in KEY_VERSES:
            assert verse.meaning, f"{verse.reference} has no meaning"

    def test_all_verses_have_formulas(self) -> None:
        """All derived verses have derivation formulas."""
        for verse in KEY_VERSES:
            assert verse.chapter_formula, f"{verse.reference} has no chapter formula"
            assert verse.verse_formula, f"{verse.reference} has no verse formula"


class TestTotalGitaVerses:
    """Test Gita verse constants."""

    def test_total_verses(self) -> None:
        """Gita has 700 verses = SEVEN × 100."""
        assert TOTAL_GITA_VERSES == 700
        assert TOTAL_GITA_VERSES == SEVEN * 100
