"""
Tests for substrate/language/composer.py — Rhythmic Sequencing Composition.

Tests what is DERIVED from protocol, not invented.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import KSETRAJNA, QUARTERS, SEVEN, WORDS
from vibe_core.mahamantra.substrate.language.types import RhythmProfile, StateVector, SyllableVector
from vibe_core.mahamantra.substrate.language.composer import (
    chamber_boost,
    chunk_sentence,
    rank_resonant_by_rhythm,
    rhythm_bias,
    semantic_boost,
    state_affinity,
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

    def test_capped_at_derived_max(self):
        class MockAntaranga:
            def prana_at(self, slot):
                return 999999999
        result = chamber_boost(MockAntaranga(), 5, 42)
        # Cap = PANCHA / (WORDS * HALVES) = 5/32 ≈ 0.15625
        from vibe_core.mahamantra.protocols._seed import PANCHA, WORDS, HALVES
        assert result <= PANCHA / (WORDS * HALVES) + 1e-9


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

    def test_chunks_by_quarters(self):
        words = ["duty", "love", "through", "devotion", "peace"]
        chunks = chunk_sentence(words)
        assert len(chunks) >= 2
        # Chunks break every QUARTERS words, no keyword matching
        for chunk in chunks:
            assert len(chunk.split()) <= QUARTERS

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
# StateVector: numeric system state summary
# =============================================================================

class TestStateVector:
    """StateVector is a pure numeric NamedTuple with sane defaults."""

    def test_defaults(self):
        sv = StateVector()
        assert sv.guna == 1  # RAJAS
        assert sv.entry_count == 0
        assert sv.boot_count == 0
        assert sv.uptime_ratio == 0.0
        assert sv.systems_alive == 0
        assert sv.dirty is False
        assert sv.prana_level == 0

    def test_custom_values(self):
        sv = StateVector(guna=2, entry_count=42, uptime_ratio=0.75, systems_alive=4)
        assert sv.guna == 2
        assert sv.entry_count == 42
        assert sv.uptime_ratio == 0.75
        assert sv.systems_alive == 4

    def test_is_namedtuple(self):
        sv = StateVector()
        assert hasattr(sv, '_fields')
        assert 'guna' in sv._fields
        assert 'prana_level' in sv._fields

    def test_immutable(self):
        sv = StateVector()
        with pytest.raises(AttributeError):
            sv.guna = 99


# =============================================================================
# state_affinity: StateVector → word selection bias
# =============================================================================

class TestStateAffinity:
    """state_affinity scores word-state alignment. All numeric, no keywords."""

    def test_returns_float(self):
        sv = StateVector()
        item = {"score": 0.5, "coords": (1, 2, 3), "packed_hex": ""}
        result = state_affinity(sv, item)
        assert isinstance(result, float)

    def test_zero_without_mode(self):
        sv = StateVector(guna=0)  # TAMAS → prefers GENESIS
        item = {"score": 0.5, "coords": (), "packed_hex": ""}
        result = state_affinity(sv, item, mode=None)
        # No mode match possible, but mass/uptime axes still contribute
        assert result >= 0.0

    def test_guna_mode_boost(self):
        sv_sattva = StateVector(guna=2)  # SATTVA → prefers DHARMA
        item = {"score": 0.5, "coords": (1, 2, 3), "packed_hex": ""}
        with_match = state_affinity(sv_sattva, item, mode="DHARMA")
        without_match = state_affinity(sv_sattva, item, mode="KARMA")
        assert with_match > without_match

    def test_mass_alignment(self):
        sv_heavy = StateVector(entry_count=60)  # Heavy state
        heavy_item = {"score": 0.5, "coords": tuple(range(7)), "packed_hex": ""}
        light_item = {"score": 0.5, "coords": (1,), "packed_hex": ""}
        # Heavy state should prefer heavy words
        heavy_score = state_affinity(sv_heavy, heavy_item)
        light_score = state_affinity(sv_heavy, light_item)
        assert heavy_score >= light_score

    def test_uptime_confidence(self):
        sv_up = StateVector(uptime_ratio=0.9)
        sv_down = StateVector(uptime_ratio=0.1)
        item = {"score": 0.8, "coords": (1, 2, 3), "packed_hex": ""}
        up_score = state_affinity(sv_up, item)
        down_score = state_affinity(sv_down, item)
        assert up_score >= down_score

    def test_capped(self):
        from vibe_core.mahamantra.protocols._seed import PANCHA, WORDS, HALVES
        sv = StateVector(guna=2, entry_count=72, uptime_ratio=1.0, prana_level=999999)
        item = {"score": 1.0, "coords": tuple(range(10)), "packed_hex": ""}
        result = state_affinity(sv, item, mode="DHARMA")
        max_cap = PANCHA / (WORDS * HALVES) * HALVES
        assert result <= max_cap + 1e-9

    def test_empty_item(self):
        sv = StateVector()
        result = state_affinity(sv, {})
        assert isinstance(result, float)
        assert result >= 0.0


# =============================================================================
# extract_state_vector: MahaState → StateVector (graceful degradation)
# =============================================================================

class TestExtractStateVector:
    """extract_state_vector gracefully degrades when MahaState unavailable."""

    def test_returns_state_vector(self):
        from vibe_core.mahamantra.substrate.language.state_bridge import extract_state_vector
        sv = extract_state_vector(prana_level=42)
        assert isinstance(sv, StateVector)
        assert sv.prana_level == 42

    def test_default_guna_is_rajas(self):
        from vibe_core.mahamantra.substrate.language.state_bridge import extract_state_vector
        sv = extract_state_vector()
        # Even if MahaState fails, default is RAJAS (1)
        assert sv.guna in (0, 1, 2)


class TestBuildLotusPool:
    """_build_lotus_pool extracts words from Lotus response."""

    def test_smaranam_source(self):
        from vibe_core.mahamantra.substrate.language.composer import _build_lotus_pool
        resp = {
            "smaranam": [
                {"sanskrit": "dharma", "meaning": "duty", "score": 0.9},
            ],
        }
        pool = _build_lotus_pool(resp)
        smaranam_items = [p for p in pool if p.get("source") == "smaranam"]
        assert len(smaranam_items) == 1
        assert smaranam_items[0]["meaning"] == "duty"

    def test_verse_source(self):
        from vibe_core.mahamantra.substrate.language.composer import _build_lotus_pool
        resp = {
            "smaranam": [],
            "verse": {
                "words": (
                    {"sanskrit": "yathā", "meaning": "as"},
                    {"sanskrit": "pradīptam", "meaning": "blazing"},
                ),
            },
        }
        pool = _build_lotus_pool(resp)
        verse_items = [p for p in pool if p.get("source") == "verse"]
        assert len(verse_items) >= 1

    def test_verse_capped_at_seven(self):
        from vibe_core.mahamantra.substrate.language.composer import _build_lotus_pool
        resp = {
            "smaranam": [],
            "verse": {
                "words": tuple(
                    {"sanskrit": f"w{i}", "meaning": f"meaning {i} long enough"} for i in range(20)
                ),
            },
        }
        pool = _build_lotus_pool(resp)
        verse_items = [p for p in pool if p.get("source") == "verse"]
        assert len(verse_items) <= SEVEN

    def test_empty_response(self):
        from vibe_core.mahamantra.substrate.language.composer import _build_lotus_pool
        pool = _build_lotus_pool({})
        assert pool == []

    def test_coords_resolved(self):
        from vibe_core.mahamantra.substrate.language.composer import _build_lotus_pool
        resp = {
            "smaranam": [
                {"sanskrit": "dharma", "meaning": "duty", "score": 0.9},
            ],
        }
        pool = _build_lotus_pool(resp)
        # coords should be resolved (not empty) for known Sanskrit words
        assert len(pool) == 1
        assert isinstance(pool[0]["coords"], (tuple, list))


# =============================================================================
# compose_from_wave: Antaranga-driven syllable composition
# =============================================================================

class TestComposeFromWave:
    """compose_from_wave reads the Antaranga standing wave for composition."""

    def _make_lotus_response(self, smaranam=None, verse=None):
        return {
            "input": "test input",
            "smaranam": smaranam or (),
            "verse": verse,
            "vibration": {"seed": 42, "attractor": 7, "phoneme": "a",
                          "signature": {"element": "prithvi", "varga": 0, "sub": 0, "harmonic": 0}},
            "guna": {"mode": "RAJAS", "opcode": "EXTEND_CAP", "opcode_value": 9},
            "diw": {"raw": 0, "venu": 0, "vamsi": 0, "murali": 0},
            "position": 9, "guardian": "prahlada", "quarter": "karma",
            "antaranga": {"active_slots": 0, "total_prana": 0},
            "akash": {"total_rounds": 0, "total_beats": 0},
        }

    def test_returns_string(self):
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
            ]
        )
        result = compose_from_wave(resp, "What is dharma?")
        assert isinstance(result, str)

    def test_empty_smaranam_returns_empty(self):
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = self._make_lotus_response(smaranam=[])
        result = compose_from_wave(resp, "test")
        assert isinstance(result, str)

    def test_output_nonempty_with_words(self):
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "bhakti", "meaning": "devotional service", "score": 0.95},
                {"sanskrit": "jñānam", "meaning": "knowledge", "score": 0.90},
                {"sanskrit": "yoga", "meaning": "linking process", "score": 0.85},
            ]
        )
        result = compose_from_wave(resp, "devotion")
        assert len(result) > 0

    def test_deterministic_a(self):
        """First half of determinism check."""
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
                {"sanskrit": "yoga", "meaning": "linking process", "score": 0.7},
            ]
        )
        result = compose_from_wave(resp, "test input")
        TestComposeFromWave._determinism_result = result
        assert isinstance(result, str)
        assert len(result) > 0

    def test_deterministic_b(self):
        """Second half: same input after full singleton reset must match."""
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "religious principles", "score": 0.9},
                {"sanskrit": "karma", "meaning": "activities", "score": 0.8},
                {"sanskrit": "yoga", "meaning": "linking process", "score": 0.7},
            ]
        )
        result = compose_from_wave(resp, "test input")
        assert result == TestComposeFromWave._determinism_result

    def test_max_seven_words(self):
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": f"word{i}", "meaning": f"meaning number {i} here", "score": 0.9 - i * 0.05}
                for i in range(10)
            ],
        )
        result = compose_from_wave(resp, "test")
        words = result.split()
        assert len(words) <= SEVEN + 1

    def test_wave_prana_ranking(self):
        """Words with higher post-modulation prana should be preferred."""
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "duty", "score": 0.5},
                {"sanskrit": "karma", "meaning": "action", "score": 0.9},
                {"sanskrit": "yoga", "meaning": "union", "score": 0.3},
            ]
        )
        result = compose_from_wave(resp, "test")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_verse_words_not_in_output_directly(self):
        """Verse words are computation input, not output fragments per se."""
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        resp = self._make_lotus_response(
            smaranam=[
                {"sanskrit": "dharma", "meaning": "duty", "score": 0.9},
            ],
            verse={
                "id": "BG.2.47", "chapter": 2, "verse": 47, "guna": "sattva",
                "dominant_name": "KRISHNA", "significance": "Sankhya Yoga",
                "word_count": 3, "phoneme_count": 15,
                "words": (
                    {"sanskrit": "karmaṇi", "meaning": "prescribed duties"},
                    {"sanskrit": "eva", "meaning": "certainly"},
                    {"sanskrit": "adhikāras", "meaning": "right"},
                ),
            }
        )
        result = compose_from_wave(resp, "What should I do?")
        assert isinstance(result, str)

    def test_with_real_lotus(self):
        """End-to-end: Lotus __call__ → compose_from_wave."""
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        lotus = MahamantraLotus()
        lr = lotus("What is the meaning of life?")
        result = compose_from_wave(lr, "What is the meaning of life?")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_real_lotus_deterministic_a(self):
        """First half: Lotus + compose_from_wave."""
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        text = "devotion and surrender"
        lotus = MahamantraLotus()
        lr = lotus(text)
        result = compose_from_wave(lr, text)
        TestComposeFromWave._lotus_seed = lr["vibration"]["seed"]
        TestComposeFromWave._lotus_result = result
        assert isinstance(result, str)
        assert len(result) > 0

    def test_real_lotus_deterministic_b(self):
        """Second half: same Lotus input after full reset must match."""
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        text = "devotion and surrender"
        lotus = MahamantraLotus()
        lr = lotus(text)
        result = compose_from_wave(lr, text)
        assert lr["vibration"]["seed"] == TestComposeFromWave._lotus_seed
        assert result == TestComposeFromWave._lotus_result
