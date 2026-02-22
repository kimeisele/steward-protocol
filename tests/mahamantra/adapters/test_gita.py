"""
TEST: Gita Module - The Fixed Point Contract
=============================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all varieties of religion and just surrender unto Me."
— Bhagavad Gita 18.66 (THE FIXED POINT)

WHAT WE TEST:
1. Fixed Point: Chapter 18 = f(18) = 18
2. Mathematical Properties: 18 = 3 × 6, 84 = 7 × 12
3. Verification: verify_fixed_point() works
4. Structure: GITA_CHAPTERS, GITA_VERSES correct
5. Chapter 18 Verse: BG 18.66 data accessible

THE CONTRACT: These tests GUARANTEE the North Star is stable.
"""

import pytest

from vibe_core.mahamantra.research.gita import (
    GITA_CHAPTERS,
    GITA_VERSES,
    FIXED_POINT_CHAPTER,
    FIXED_POINT_VERSE,
    SHARANAGATI_SUM,
    CHAPTER_18_VERSE,
    GitaVerse,
    verify_fixed_point,
    get_chapter_significance,
)
from vibe_core.mahamantra.protocols._seed import (
    TRINITY,
    SHARANAGATI,
    SEVEN,
    MAHAJANA_COUNT,
    QUALITIES,
    HALVES,
    MAHA_QUANTUM,
)


class TestGitaConstants:
    """Test fundamental Gita constants."""

    def test_gita_chapters_is_18(self):
        """Gita has 18 chapters."""
        assert GITA_CHAPTERS == 18

    def test_gita_verses_is_700(self):
        """Gita has 700 verses."""
        assert GITA_VERSES == 700

    def test_fixed_point_chapter_is_18(self):
        """Fixed point chapter is 18."""
        assert FIXED_POINT_CHAPTER == 18
        assert FIXED_POINT_CHAPTER == GITA_CHAPTERS

    def test_fixed_point_verse_is_66(self):
        """Fixed point verse is 66."""
        assert FIXED_POINT_VERSE == 66
        assert FIXED_POINT_VERSE == QUALITIES + HALVES


class TestGitaFixedPointMath:
    """Test mathematical properties of Chapter 18."""

    def test_18_equals_3_times_6(self):
        """18 = TRINITY × SHARANAGATI = 3 × 6."""
        assert FIXED_POINT_CHAPTER == TRINITY * SHARANAGATI
        assert 18 == 3 * 6

    def test_sharanagati_sum_is_84(self):
        """18 + 66 = 84."""
        assert SHARANAGATI_SUM == FIXED_POINT_CHAPTER + FIXED_POINT_VERSE
        assert SHARANAGATI_SUM == 84

    def test_84_equals_7_times_12(self):
        """84 = SEVEN × MAHAJANA_COUNT = 7 × 12."""
        assert SHARANAGATI_SUM == SEVEN * MAHAJANA_COUNT
        assert 84 == 7 * 12

    def test_18_less_than_maha_quantum(self):
        """18 < 137 (within quantum space)."""
        assert FIXED_POINT_CHAPTER < MAHA_QUANTUM


class TestGitaVerifyFixedPoint:
    """Test fixed point verification."""

    def test_verify_fixed_point_returns_true(self):
        """verify_fixed_point() should return True."""
        assert verify_fixed_point() == True

    def test_all_checks_pass(self):
        """All mathematical checks should pass."""
        # Manually verify each check
        assert GITA_CHAPTERS == 18
        assert GITA_CHAPTERS == TRINITY * SHARANAGATI
        assert (GITA_CHAPTERS + FIXED_POINT_VERSE) == SEVEN * MAHAJANA_COUNT
        assert GITA_CHAPTERS < MAHA_QUANTUM


class TestGitaChapter18Verse:
    """Test Chapter 18 Verse 66 data."""

    def test_chapter_18_verse_exists(self):
        """CHAPTER_18_VERSE should exist."""
        assert CHAPTER_18_VERSE is not None
        assert isinstance(CHAPTER_18_VERSE, GitaVerse)

    def test_chapter_18_verse_correct_reference(self):
        """Verse should be BG 18.66."""
        assert CHAPTER_18_VERSE.chapter == 18
        assert CHAPTER_18_VERSE.verse == 66

    def test_chapter_18_verse_has_sanskrit(self):
        """Verse should have Sanskrit text."""
        assert "sarva-dharmān" in CHAPTER_18_VERSE.sanskrit

    def test_chapter_18_verse_has_translation(self):
        """Verse should have translation."""
        assert "surrender" in CHAPTER_18_VERSE.translation.lower()

    def test_chapter_18_verse_has_significance(self):
        """Verse should have significance."""
        assert "FIXED POINT" in CHAPTER_18_VERSE.significance


class TestGitaChapterSignificance:
    """Test chapter significance function."""

    def test_get_chapter_18_significance(self):
        """Chapter 18 should be identified as fixed point."""
        sig = get_chapter_significance(18)
        assert "FIXED POINT" in sig or "MOKSHA" in sig

    def test_all_chapters_have_significance(self):
        """All 18 chapters should have significance."""
        for ch in range(1, 19):
            sig = get_chapter_significance(ch)
            assert sig != "Unknown chapter"

    def test_unknown_chapter_returns_unknown(self):
        """Invalid chapter should return 'Unknown'."""
        sig = get_chapter_significance(99)
        assert sig == "Unknown chapter"


class TestGitaVerseFrozen:
    """Test immutability."""

    def test_gita_verse_is_frozen(self):
        """GitaVerse should be immutable."""
        with pytest.raises(AttributeError):
            CHAPTER_18_VERSE.chapter = 99


class TestGitaDhruvaAnalogy:
    """Test the North Star (Dhruva) analogy."""

    def test_chapter_18_is_north_star(self):
        """Chapter 18 is like Dhruva - fixed and unchanging."""
        # All paths lead here (all chapters point to surrender)
        # This is philosophical, but we verify the math
        assert FIXED_POINT_CHAPTER == 18
        # And verify it's THE chapter (not just A chapter)
        assert verify_fixed_point()

    def test_108_mala_connection(self):
        """108 = 18 × 6 = FIXED_POINT × SHARANAGATI."""
        from vibe_core.mahamantra.protocols._seed import MALA

        # Note: MALA is 108, let's verify the connection
        # 108 = 18 × 6 (simplified)
        # Actually 108 = 12 × 9 from seed, but 18 × 6 = 108 is also true
        assert 18 * 6 == 108
        assert MALA == 108
