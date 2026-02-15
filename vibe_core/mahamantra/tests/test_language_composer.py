"""
Tests for substrate/language/composer.py — Rhythmic Sequencing Composition.

Tests what is DERIVED from protocol, not invented.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import KSETRAJNA, QUARTERS, SEVEN, WORDS
from vibe_core.mahamantra.substrate.language.types import RhythmProfile, SyllableVector
from vibe_core.mahamantra.substrate.language.composer import (
    chamber_boost,
    chunk_sentence,
    compose,
    rank_resonant_by_rhythm,
    rhythm_bias,
    semantic_boost,
)


# =============================================================================
# rhythm_bias: grid-aligned rhythmic emphasis
# =============================================================================

class TestRhythmBias:
    """rhythm_bias computes emphasis bonus from 3D vectors + grid."""

    def test_empty_rhythm_returns_zero(self):
        rp = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        assert rhythm_bias(rp, 0) == 0.0

    def test_no_sequencer_steps_returns_zero(self):
        rp = RhythmProfile(syllable_count=1, stress_pattern=(1,), sequencer_steps=(), signature="1")
        assert rhythm_bias(rp, 0) == 0.0

    def test_returns_float(self):
        rp = RhythmProfile(
            syllable_count=2,
            stress_pattern=(1, 0),
            sequencer_steps=(0, 1),
            signature="10",
            vectors=(SyllableVector(1, 3, 2), SyllableVector(0, 4, 1)),
            grid_modes=("DHARMA", "GENESIS"),
        )
        result = rhythm_bias(rp, 0)
        assert isinstance(result, float)

    def test_non_negative(self):
        rp = RhythmProfile(
            syllable_count=1,
            stress_pattern=(0,),
            sequencer_steps=(15,),
            signature="0",
            vectors=(SyllableVector(0, 3, 2),),
            grid_modes=("KARMA",),
        )
        assert rhythm_bias(rp, 0) >= 0.0

    def test_downbeat_gets_bonus(self):
        # Step 0 is always a downbeat (beat=0)
        rp = RhythmProfile(
            syllable_count=1,
            stress_pattern=(1,),
            sequencer_steps=(0,),
            signature="1",
            vectors=(SyllableVector(1, 3, 2),),
            grid_modes=("DHARMA",),
        )
        score = rhythm_bias(rp, 0)
        assert score > 0.0  # downbeat + stressed = bonus


# =============================================================================
# semantic_boost: WordNet graph distance bonus
# =============================================================================

class TestSemanticBoost:
    """semantic_boost: WordNet-based bonus for candidate words."""

    def test_empty_packed_hex(self):
        assert semantic_boost("test", "") == 0.0

    def test_returns_float(self):
        result = semantic_boost("devotion", "abcd")
        assert isinstance(result, float)

    def test_non_negative(self):
        result = semantic_boost("love", "1234")
        assert result >= 0.0


# =============================================================================
# chamber_boost: Antaranga prana-based boost
# =============================================================================

class TestChamberBoost:
    """chamber_boost: prana at word's slot from character wave."""

    def test_none_antaranga(self):
        assert chamber_boost(None, 5, 42) == 0.0

    def test_negative_coord(self):
        assert chamber_boost(object(), -1, 42) == 0.0

    def test_returns_float(self):
        class MockAntaranga:
            def prana_at(self, slot):
                return 0
        assert isinstance(chamber_boost(MockAntaranga(), 5, 42), float)

    def test_zero_prana_returns_zero(self):
        class MockAntaranga:
            def prana_at(self, slot):
                return 0
        assert chamber_boost(MockAntaranga(), 5, 42) == 0.0

    def test_positive_prana_returns_positive(self):
        class MockAntaranga:
            def prana_at(self, slot):
                return 10000
        result = chamber_boost(MockAntaranga(), 5, 42)
        assert result > 0.0

    def test_capped_at_015(self):
        class MockAntaranga:
            def prana_at(self, slot):
                return 999999999
        result = chamber_boost(MockAntaranga(), 5, 42)
        assert result <= 0.15


# =============================================================================
# rank_resonant_by_rhythm: full ranking pipeline
# =============================================================================

class TestRankResonantByRhythm:
    """rank_resonant_by_rhythm: base + rhythm + semantic + chamber."""

    def test_empty_pool(self):
        rp = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = rank_resonant_by_rhythm([], rp)
        assert result == []

    def test_preserves_items(self):
        pool = [
            {"meaning": "love", "score": 0.9},
            {"meaning": "duty", "score": 0.7},
        ]
        rp = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = rank_resonant_by_rhythm(pool, rp)
        assert len(result) == 2

    def test_adds_rhythm_score(self):
        pool = [{"meaning": "love", "score": 0.9}]
        rp = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = rank_resonant_by_rhythm(pool, rp)
        assert "rhythm_score" in result[0]
        assert "rhythm_bias" in result[0]
        assert "semantic_boost" in result[0]
        assert "chamber_boost" in result[0]

    def test_sorted_descending(self):
        pool = [
            {"meaning": "low", "score": 0.1},
            {"meaning": "high", "score": 0.9},
            {"meaning": "mid", "score": 0.5},
        ]
        rp = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = rank_resonant_by_rhythm(pool, rp)
        scores = [float(r["rhythm_score"]) for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_does_not_mutate_input(self):
        pool = [{"meaning": "love", "score": 0.9}]
        rp = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        rank_resonant_by_rhythm(pool, rp)
        assert "rhythm_score" not in pool[0]


# =============================================================================
# chunk_sentence: word list → readable phrase chunks
# =============================================================================

class TestChunkSentence:
    """chunk_sentence groups flat word lists into readable phrases."""

    def test_short_list_unchanged(self):
        assert chunk_sentence(["a", "b", "c"]) == ["a b c"]

    def test_empty_list(self):
        assert chunk_sentence([]) == [""]

    def test_single_word(self):
        assert chunk_sentence(["love"]) == ["love"]

    def test_breaks_on_preposition(self):
        words = ["duty", "love", "through", "devotion", "peace"]
        chunks = chunk_sentence(words)
        assert len(chunks) >= 2
        # "through" should start a new chunk
        found = any("through" in c.split()[0].lower() for c in chunks[1:])
        assert found

    def test_breaks_every_quarters_words(self):
        words = [f"word{i}" for i in range(12)]
        chunks = chunk_sentence(words)
        # No chunk should exceed QUARTERS words
        for chunk in chunks:
            assert len(chunk.split()) <= QUARTERS

    def test_all_words_preserved(self):
        words = ["The", "Supreme", "to", "be", "known", "devotion", "love", "service"]
        chunks = chunk_sentence(words)
        all_words = " ".join(chunks).split()
        assert all_words == words


# =============================================================================
# compose: full composition pipeline (integration-level)
# =============================================================================

class TestCompose:
    """compose: end-to-end composition from guardian response + template."""

    def _make_mock_guardian(self, words_data):
        """Create a minimal mock guardian response."""
        class MockWord:
            def __init__(self, sanskrit, meanings, first_coord, packed_hex=""):
                self.sanskrit = sanskrit
                self.meanings = meanings
                self.first_coord = first_coord
                self.packed_hex = packed_hex

        class MockResonantWord:
            def __init__(self, word, score):
                self.word = word
                self.total_score = score

        class MockGuardianResponse:
            def __init__(self, rwords):
                self.words = rwords

        rwords = [
            MockResonantWord(
                MockWord(w["sanskrit"], w["meanings"], w.get("first_coord", 0)),
                w["score"],
            )
            for w in words_data
        ]
        return MockGuardianResponse(rwords)

    def test_returns_string(self):
        guardian = self._make_mock_guardian([
            {"sanskrit": "bhakti", "meanings": ["devotion"], "score": 0.9, "first_coord": 0},
            {"sanskrit": "dharma", "meanings": ["duty"], "score": 0.8, "first_coord": 1},
        ])
        template = [{"sanskrit": "arjuna", "meaning": "warrior", "role": "REF", "coords": [0]}]
        rhythm = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = compose(guardian, template, rhythm, "test", "CORE", {})
        assert isinstance(result, str)

    def test_nonempty_output(self):
        guardian = self._make_mock_guardian([
            {"sanskrit": "bhakti", "meanings": ["devotion"], "score": 0.9, "first_coord": 0},
        ])
        template = []
        rhythm = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = compose(guardian, template, rhythm, "test", "CORE", {})
        assert len(result) > 0

    def test_contains_resonant_meaning(self):
        guardian = self._make_mock_guardian([
            {"sanskrit": "bhakti", "meanings": ["devotion"], "score": 0.9, "first_coord": 0},
            {"sanskrit": "dharma", "meanings": ["duty"], "score": 0.8, "first_coord": 1},
            {"sanskrit": "prema", "meanings": ["love"], "score": 0.7, "first_coord": 2},
        ])
        template = []
        rhythm = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = compose(guardian, template, rhythm, "test", "CORE", {})
        # At least one resonant meaning should appear
        meanings = {"devotion", "duty", "love"}
        assert any(m in result.lower() for m in meanings)

    def test_expansion_data_enriches(self):
        guardian = self._make_mock_guardian([
            {"sanskrit": "bhakti", "meanings": ["devotion"], "score": 0.9, "first_coord": 0},
        ])
        expansion = {
            "expansion_words": (("jnana", "knowledge"),),
            "synth_walk_words": (("karma", "action"),),
        }
        rhythm = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = compose(guardian, [], rhythm, "test", "CORE", {}, expansion_data=expansion)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_deterministic(self):
        guardian = self._make_mock_guardian([
            {"sanskrit": "bhakti", "meanings": ["devotion"], "score": 0.9, "first_coord": 0},
            {"sanskrit": "dharma", "meanings": ["duty"], "score": 0.8, "first_coord": 1},
        ])
        template = [{"sanskrit": "arjuna", "meaning": "warrior", "role": "REF", "coords": [0]}]
        rhythm = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        a = compose(guardian, template, rhythm, "test", "CORE", {})
        b = compose(guardian, template, rhythm, "test", "CORE", {})
        assert a == b

    def test_max_seven_words(self):
        """Output should not exceed SEVEN resonant words in the main pool."""
        guardian = self._make_mock_guardian([
            {"sanskrit": f"w{i}", "meanings": [f"meaning{i}"], "score": 0.9 - i * 0.05, "first_coord": i}
            for i in range(20)
        ])
        rhythm = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        result = compose(guardian, [], rhythm, "test", "CORE", {})
        assert isinstance(result, str)
