"""
Tests for Sanskrit Lookup - Verse Word-for-Word via RAMA Coordinates.

Verifies production access to the Gita word-for-word lexicon.
"""

import pytest

from vibe_core.mahamantra.substrate.sanskrit_lookup import (
    VerseWords,
    WordEntry,
    hkr_signature,
    lexicon_stats,
    verse_words,
    word_by_coords,
    word_by_iast,
)
from vibe_core.mahamantra.substrate.varnamala_codec import encode


class TestVerseLookup:
    """verse_words() must return correct Sanskrit content."""

    def test_bg_18_66_exists(self):
        """The fixed point verse must exist."""
        vw = verse_words(18, 66)
        assert vw is not None
        assert vw.ref == "BG.18.66"
        assert vw.chapter == 18
        assert vw.verse == 66

    def test_bg_18_66_has_words(self):
        vw = verse_words(18, 66)
        assert len(vw.words) > 0
        assert all(isinstance(w, WordEntry) for w in vw.words)

    def test_bg_18_66_sarva_dharman(self):
        """First word of BG 18.66 is sarva-dharmān."""
        vw = verse_words(18, 66)
        assert vw.words[0].sanskrit == "sarva-dharmān"

    def test_bg_1_1_exists(self):
        vw = verse_words(1, 1)
        assert vw is not None
        assert vw.ref == "BG.1.1"

    def test_nonexistent_verse(self):
        assert verse_words(99, 99) is None

    def test_phoneme_count(self):
        vw = verse_words(18, 66)
        assert vw.phoneme_count > 0
        assert vw.phoneme_count == sum(len(w.coords) for w in vw.words)


class TestWordLookup:
    """Individual word lookup."""

    def test_word_by_iast(self):
        w = word_by_iast("dharma")
        assert w is not None
        assert "dharma" in w.sanskrit.lower() or w.sanskrit == "dharma"

    def test_word_by_coords(self):
        coords = encode("yoga")
        w = word_by_coords(coords)
        # May or may not exist in lexicon depending on exact form
        # The test validates the lookup path works without error


class TestHKRSignature:
    """H/K/R signature system."""

    def test_signature_is_hkr(self):
        coords = encode("bhakti")
        sig = hkr_signature(coords, cycle=0)
        assert all(c in "HKR" for c in sig)

    def test_signature_length_matches_coords(self):
        coords = encode("dharma")
        sig = hkr_signature(coords, cycle=0)
        assert len(sig) == len(coords)

    def test_signature_changes_with_cycle(self):
        """Signature is a rotating lens, not fixed."""
        coords = encode("dharma")
        sigs = {hkr_signature(coords, cycle=c) for c in range(49)}
        assert len(sigs) > 1  # Must produce multiple distinct signatures


class TestVenuSpell:
    """VenuOrchestrator.spell() must round-trip through VENU field."""

    def test_spell_roundtrip(self):
        """VENU field carries RAMA coordinates losslessly."""
        from vibe_core.mahamantra.protocols.diw import unpack
        from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator

        venu = VenuOrchestrator()
        coords = encode("dharma")
        diws = venu.spell(coords, cycle=0)

        recovered = tuple(unpack(d).venu for d in diws)
        assert recovered == coords

    def test_spell_vamsi_hkr(self):
        """VAMSI region must match H/K/R signature."""
        from vibe_core.mahamantra.protocols.diw import unpack
        from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator

        venu = VenuOrchestrator()
        coords = encode("dharma")
        sig = hkr_signature(coords, cycle=0)
        diws = venu.spell(coords, cycle=0)

        for i, d in enumerate(diws):
            p = unpack(d)
            region = min(p.vamsi // 170, 2)
            name = ["H", "K", "R"][region]
            assert name == sig[i], f"pos {i}: VAMSI region {name} != sig {sig[i]}"

    def test_spell_verse(self):
        """Spelling a full verse must produce correct tick count."""
        from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator

        venu = VenuOrchestrator()
        vw = verse_words(18, 66)
        total = 0
        for w in vw.words:
            diws = venu.spell(w.coords)
            total += len(diws)
        assert total == vw.phoneme_count


class TestLexiconStats:
    """Lexicon must satisfy architectural invariants."""

    def test_stats_available(self):
        stats = lexicon_stats()
        assert stats["total_verses"] == 700
        assert stats["fits_in_65k"] is True
        assert stats["unique_words"] > 4000
        # 45815 = deduplicated (grouped verses counted once)
        # Previous: 54423 was inflated by multi-verse group duplication
        assert stats["total_phonemes"] == 45815
        # 45815 / VARNAMALA(49) = 935 exactly
        assert stats["total_phonemes"] % 49 == 0
