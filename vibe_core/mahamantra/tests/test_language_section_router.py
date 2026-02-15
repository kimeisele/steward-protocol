"""
Tests for substrate/language/section_router.py — Kapitel 18 Section Routing.

Only tests what is DERIVED from protocol constants, not invented.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    SEVEN,
    SHARANAGATI,
)
from vibe_core.mahamantra.protocols.seed._extended import SHRUTIS
from vibe_core.mahamantra.protocols.seed._secondary import NADI_RESONANCE
from vibe_core.mahamantra.substrate.language.section_router import (
    CHAPTER_18_SECTIONS,
    CHAPTER_18_VERSES,
    SECTION_SIGNATURES,
    _infer_role,
    extract_template,
    route_to_section,
)


# =============================================================================
# CHAPTER_18_SECTIONS: topology verification
# =============================================================================

class TestChapter18Sections:
    """CHAPTER_18_SECTIONS: 7 sections covering all 78 verses."""

    def test_seven_sections(self):
        assert len(CHAPTER_18_SECTIONS) == SEVEN

    def test_total_verses(self):
        total = sum(s[3] for s in CHAPTER_18_SECTIONS)
        assert total == CHAPTER_18_VERSES
        assert total == NADI_RESONANCE + SHARANAGATI  # 72 + 6 = 78

    def test_contiguous_no_gaps(self):
        for i in range(len(CHAPTER_18_SECTIONS) - 1):
            _, _, end, _ = CHAPTER_18_SECTIONS[i]
            _, start_next, _, _ = CHAPTER_18_SECTIONS[i + 1]
            assert start_next == end + 1

    def test_starts_at_verse_1(self):
        assert CHAPTER_18_SECTIONS[0][1] == 1

    def test_ends_at_verse_78(self):
        assert CHAPTER_18_SECTIONS[-1][2] == CHAPTER_18_VERSES

    def test_section_names(self):
        names = [s[0] for s in CHAPTER_18_SECTIONS]
        assert names == ["TYAGA", "SANKHYA", "TRAIGUNYA", "VARNASHRAMA", "BRAHMAN", "RAHASYA", "SANJAYA"]

    def test_section_lengths_derived(self):
        """Each section length is a protocol-derived constant."""
        lengths = {s[0]: s[3] for s in CHAPTER_18_SECTIONS}
        assert lengths["TYAGA"] == MAHAJANA_COUNT  # 12
        assert lengths["SANKHYA"] == SHARANAGATI  # 6
        assert lengths["TRAIGUNYA"] == SHRUTIS  # 22
        assert lengths["VARNASHRAMA"] == HARE_COUNT  # 8
        assert lengths["BRAHMAN"] == SEVEN  # 7
        assert lengths["RAHASYA"] == MAHAJANA_COUNT - KSETRAJNA  # 11
        assert lengths["SANJAYA"] == MAHAJANA_COUNT  # 12

    def test_each_section_is_4_tuple(self):
        for s in CHAPTER_18_SECTIONS:
            assert len(s) == 4
            name, start, end, length = s
            assert isinstance(name, str)
            assert isinstance(start, int)
            assert isinstance(end, int)
            assert isinstance(length, int)
            assert end - start + 1 == length


# =============================================================================
# SECTION_SIGNATURES: verified phonetic + semantic profiles
# =============================================================================

class TestSectionSignatures:
    """SECTION_SIGNATURES: one entry per section with mode and metadata."""

    def test_seven_signatures(self):
        assert len(SECTION_SIGNATURES) == SEVEN

    def test_keys_match_sections(self):
        section_names = {s[0] for s in CHAPTER_18_SECTIONS}
        assert set(SECTION_SIGNATURES.keys()) == section_names

    def test_each_has_mode(self):
        for name, sig in SECTION_SIGNATURES.items():
            assert "mode" in sig
            assert isinstance(sig["mode"], str)

    def test_each_has_element(self):
        for name, sig in SECTION_SIGNATURES.items():
            assert "element" in sig
            assert sig["element"] in ("akasha", "vayu", "agni", "jala", "prithvi")

    def test_each_has_semantic(self):
        for name, sig in SECTION_SIGNATURES.items():
            assert "semantic" in sig
            assert isinstance(sig["semantic"], str)

    def test_modes_are_distinct(self):
        modes = [sig["mode"] for sig in SECTION_SIGNATURES.values()]
        assert len(modes) == len(set(modes))  # all unique


# =============================================================================
# route_to_section: attractor + seed → section + verse
# =============================================================================

class TestRouteToSection:
    """route_to_section: deterministic two-stage routing."""

    def test_returns_3_tuple(self):
        name, verse, idx = route_to_section(42, seed=7)
        assert isinstance(name, str)
        assert isinstance(verse, int)
        assert isinstance(idx, int)

    def test_section_name_valid(self):
        valid_names = {s[0] for s in CHAPTER_18_SECTIONS}
        for attractor in range(0, 200, 17):
            name, _, _ = route_to_section(attractor, seed=0)
            assert name in valid_names

    def test_verse_within_section(self):
        for attractor in range(0, 200, 13):
            for seed in range(0, 50, 7):
                name, verse, idx = route_to_section(attractor, seed=seed)
                _, start, end, _ = CHAPTER_18_SECTIONS[idx]
                assert start <= verse <= end, f"verse {verse} not in {name} [{start}-{end}]"

    def test_section_index_valid(self):
        for attractor in range(0, 100, 11):
            _, _, idx = route_to_section(attractor)
            assert 0 <= idx < SEVEN

    def test_deterministic(self):
        a = route_to_section(42, seed=17)
        b = route_to_section(42, seed=17)
        assert a == b

    def test_different_attractors_can_route_differently(self):
        results = set()
        for att in range(0, 500, 7):
            name, _, _ = route_to_section(att, seed=0)
            results.add(name)
        assert len(results) >= 2  # at least 2 different sections

    def test_different_seeds_can_route_differently(self):
        results = set()
        for seed in range(0, 100):
            name, verse, _ = route_to_section(42, seed=seed)
            results.add((name, verse))
        assert len(results) >= 2


# =============================================================================
# extract_template: chapter + verse → word slots
# =============================================================================

class TestExtractTemplate:
    """extract_template: Gita verse → grammatical template slots."""

    def test_returns_list(self):
        result = extract_template(GITA_CHAPTERS, 66)
        assert isinstance(result, list)

    def test_slots_have_required_keys(self):
        result = extract_template(GITA_CHAPTERS, 66)
        if result:
            for slot in result:
                assert "position" in slot
                assert "sanskrit" in slot
                assert "meaning" in slot
                assert "role" in slot
                assert "coords" in slot

    def test_positions_sequential(self):
        result = extract_template(GITA_CHAPTERS, 1)
        if result:
            for i, slot in enumerate(result):
                assert slot["position"] == i

    def test_roles_are_valid(self):
        valid_roles = {"NOUN", "VERB", "REF", "PARTICLE", "QUALITY", "PREP"}
        result = extract_template(GITA_CHAPTERS, 66)
        if result:
            for slot in result:
                assert slot["role"] in valid_roles

    def test_invalid_verse_returns_empty(self):
        result = extract_template(GITA_CHAPTERS, 9999)
        assert result == []

    def test_deterministic(self):
        a = extract_template(GITA_CHAPTERS, 66)
        b = extract_template(GITA_CHAPTERS, 66)
        assert a == b


# =============================================================================
# _infer_role: meaning → grammatical role
# =============================================================================

class TestInferRole:
    """_infer_role classifies English meanings into grammatical roles."""

    def test_verb_markers(self):
        assert _infer_role("to abandon", 0, 5) == "VERB"
        assert _infer_role("should perform", 0, 5) == "VERB"
        assert _infer_role("abandon", 0, 5) == "VERB"

    def test_references(self):
        assert _infer_role("unto me", 0, 5) == "REF"
        assert _infer_role("you", 0, 5) == "REF"
        assert _infer_role("all", 0, 5) == "REF"

    def test_particles(self):
        assert _infer_role("and", 0, 5) == "PARTICLE"
        assert _infer_role("indeed", 0, 5) == "PARTICLE"
        assert _infer_role("not", 0, 5) == "PARTICLE"

    def test_qualities(self):
        assert _infer_role("supreme lord", 0, 5) == "QUALITY"
        assert _infer_role("divine grace", 0, 5) == "QUALITY"

    def test_prepositions(self):
        assert _infer_role("of the world", 0, 5) == "PREP"
        assert _infer_role("by devotion", 0, 5) == "PREP"

    def test_default_noun(self):
        assert _infer_role("devotion", 0, 5) == "NOUN"
        assert _infer_role("dharma", 0, 5) == "NOUN"

    def test_empty_meaning(self):
        assert _infer_role("", 0, 5) == "NOUN"
