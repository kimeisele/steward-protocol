"""
Tests for Gita Verse Content - Semantic Derivation from Axioms
==============================================================

100% SSOT-konform: Semantik aus Axiomen abgeleitet.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    NADI_RESONANCE,
    NAVA,
    PANCHA,
    QUALITIES,
    QUARTERS,
    SEVEN,
    TEN,
)
from vibe_core.mahamantra.research.gita_verse_content import (
    AXIOM_SEMANTICS,
    DERIVED_ESSENCES,
    SEMANTICS_HALVES,
    SEMANTICS_KSETRAJNA,
    SEMANTICS_QUALITIES,
    SEMANTICS_SEVEN,
    derive_verse_essence,
    get_semantics_for_value,
)
from vibe_core.mahamantra.research.gita_verse_derivation import KEY_VERSES


class TestAxiomSemantics:
    """Test axiom to semantics mapping."""

    def test_ksetrajna_semantics(self) -> None:
        """KSETRAJNA = 1 = Observer, Consciousness."""
        sem = SEMANTICS_KSETRAJNA
        assert sem.value == KSETRAJNA == 1
        assert (
            "observer" in sem.keywords or "consciousness" in sem.keywords.lower()
            if isinstance(sem.keywords, str)
            else any("observer" in k or "consciousness" in k for k in sem.keywords)
        )

    def test_halves_semantics(self) -> None:
        """HALVES = 2 = Duality, Confusion."""
        sem = SEMANTICS_HALVES
        assert sem.value == HALVES == 2
        assert "duality" in sem.english_theme.lower() or "confusion" in sem.english_theme.lower()

    def test_seven_semantics(self) -> None:
        """SEVEN = 7 = Perfection, Completeness."""
        sem = SEMANTICS_SEVEN
        assert sem.value == SEVEN == 7
        assert "perfection" in sem.english_theme.lower() or "complete" in sem.english_theme.lower()

    def test_qualities_semantics(self) -> None:
        """QUALITIES = 64 = Full opulence."""
        sem = SEMANTICS_QUALITIES
        assert sem.value == QUALITIES == 64

    def test_all_base_axioms_have_semantics(self) -> None:
        """All base axiom values have semantics defined."""
        base_values = [KSETRAJNA, HALVES, QUARTERS, PANCHA, SEVEN, HARE_COUNT, NAVA, TEN]
        for val in base_values:
            assert val in AXIOM_SEMANTICS, f"Value {val} missing from AXIOM_SEMANTICS"


class TestGetSemanticsForValue:
    """Test semantic lookup for computed values."""

    def test_direct_lookup(self) -> None:
        """Direct values return their semantics."""
        sem = get_semantics_for_value(SEVEN)
        assert sem.value == 7
        assert "perfection" in sem.english_theme.lower()

    def test_computed_value_13(self) -> None:
        """13 = MAHAJANA + KSETRAJNA = Field and Knower."""
        sem = get_semantics_for_value(MAHAJANA_COUNT + KSETRAJNA)
        assert sem.value == 13
        assert "field" in sem.english_theme.lower() or "knower" in sem.english_theme.lower()

    def test_computed_value_35(self) -> None:
        """35 = SEVEN × PANCHA = Perfect Elements."""
        sem = get_semantics_for_value(SEVEN * PANCHA)
        assert sem.value == 35

    def test_computed_value_66(self) -> None:
        """66 = QUALITIES + HALVES = Surrender All."""
        sem = get_semantics_for_value(QUALITIES + HALVES)
        assert sem.value == 66
        assert "surrender" in sem.english_theme.lower()

    def test_computed_value_73(self) -> None:
        """73 = NADI + KSETRAJNA = Illusion Destroyed."""
        sem = get_semantics_for_value(NADI_RESONANCE + KSETRAJNA)
        assert sem.value == 73
        assert "illusion" in sem.english_theme.lower() or "destroyed" in sem.english_theme.lower()


class TestDeriveVerseEssence:
    """Test verse essence derivation."""

    def test_derive_all_key_verses(self) -> None:
        """All key verses can be derived."""
        for verse in KEY_VERSES:
            essence = derive_verse_essence(verse)
            assert essence.reference == verse.reference
            assert essence.chapter == verse.chapter
            assert essence.verse == verse.verse

    def test_bg_2_7_essence(self) -> None:
        """BG 2.7 essence = Duality + Perfection."""
        verse = KEY_VERSES[0]  # BG 2.7
        essence = derive_verse_essence(verse)
        assert essence.reference == "BG 2.7"
        # Should contain duality and perfection themes
        theme_lower = essence.derived_theme.lower()
        assert "duality" in theme_lower or "confusion" in theme_lower
        assert "perfection" in theme_lower or "complete" in theme_lower

    def test_bg_18_66_essence(self) -> None:
        """BG 18.66 essence = Final Teaching + Surrender All."""
        verse = KEY_VERSES[14]  # BG 18.66
        essence = derive_verse_essence(verse)
        assert essence.reference == "BG 18.66"
        assert essence.chapter == GITA_CHAPTERS == 18
        assert essence.verse == QUALITIES + HALVES == 66
        # Should contain surrender theme
        assert "surrender" in essence.derived_theme.lower() or "surrender" in essence.derived_essence.lower()


class TestDerivedEssences:
    """Test pre-computed essences."""

    def test_essences_count(self) -> None:
        """16 essences derived (one per key verse)."""
        assert len(DERIVED_ESSENCES) == len(KEY_VERSES) == 16

    def test_all_essences_have_themes(self) -> None:
        """All essences have derived themes."""
        for essence in DERIVED_ESSENCES:
            assert essence.derived_theme, f"{essence.reference} has no theme"
            assert essence.derived_essence, f"{essence.reference} has no essence"

    def test_all_essences_have_semantics(self) -> None:
        """All essences have chapter semantics."""
        for essence in DERIVED_ESSENCES:
            assert essence.chapter_semantics is not None
            assert essence.verse_semantics is not None


class TestSemanticConsistency:
    """Test that semantics are consistent with verse meaning."""

    def test_bg_4_34_guru_verse(self) -> None:
        """BG 4.34 should have guru-related semantics."""
        verse = KEY_VERSES[3]  # BG 4.34
        essence = derive_verse_essence(verse)
        # Verse 34 = 2 × 17 = approach guru
        keywords = essence.key_concepts
        theme = essence.derived_theme.lower()
        # Should relate to knowledge/guru
        assert any(k in ["guru", "knowledge", "approach", "inquire"] for k in keywords) or "guru" in theme

    def test_bg_13_35_field_knower(self) -> None:
        """BG 13.35 should have field/knower semantics."""
        verse = KEY_VERSES[9]  # BG 13.35
        essence = derive_verse_essence(verse)
        theme = essence.derived_theme.lower()
        # Should relate to field and knower distinction
        assert "field" in theme or "knower" in theme or "element" in theme

    def test_bg_18_73_illusion_destroyed(self) -> None:
        """BG 18.73 should have illusion-destroyed semantics."""
        verse = KEY_VERSES[15]  # BG 18.73
        essence = derive_verse_essence(verse)
        theme = essence.derived_theme.lower()
        essence_text = essence.derived_essence.lower()
        # Should relate to illusion being destroyed
        assert "illusion" in theme or "illusion" in essence_text or "destroyed" in theme
