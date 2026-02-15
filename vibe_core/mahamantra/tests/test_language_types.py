"""
Tests for substrate/language/types.py — Pure data structures.

Only tests what is DERIVED, not invented.
"""

import pytest

from vibe_core.mahamantra.substrate.language.types import (
    EngineResult,
    RhythmProfile,
    SyllableVector,
)


class TestSyllableVector:
    """SyllableVector: 3D phonetic vector (stress, height, weight)."""

    def test_is_namedtuple(self):
        sv = SyllableVector(stress=1, height=3, weight=2)
        assert isinstance(sv, tuple)
        assert sv.stress == 1
        assert sv.height == 3
        assert sv.weight == 2

    def test_indexable(self):
        sv = SyllableVector(stress=0, height=5, weight=1)
        assert sv[0] == 0
        assert sv[1] == 5
        assert sv[2] == 1

    def test_immutable(self):
        sv = SyllableVector(stress=1, height=2, weight=3)
        with pytest.raises(AttributeError):
            sv.stress = 99

    def test_equality(self):
        a = SyllableVector(stress=1, height=3, weight=2)
        b = SyllableVector(stress=1, height=3, weight=2)
        assert a == b

    def test_inequality(self):
        a = SyllableVector(stress=1, height=3, weight=2)
        b = SyllableVector(stress=0, height=3, weight=2)
        assert a != b


class TestRhythmProfile:
    """RhythmProfile: temporal profile on mantra grid."""

    def test_required_fields(self):
        rp = RhythmProfile(
            syllable_count=3,
            stress_pattern=(1, 0, 1),
            sequencer_steps=(0, 5, 12),
            signature="101",
        )
        assert rp.syllable_count == 3
        assert rp.stress_pattern == (1, 0, 1)
        assert rp.sequencer_steps == (0, 5, 12)
        assert rp.signature == "101"

    def test_optional_defaults(self):
        rp = RhythmProfile(
            syllable_count=0,
            stress_pattern=(),
            sequencer_steps=(),
            signature="-",
        )
        assert rp.vectors == ()
        assert rp.grid_modes == ()

    def test_with_vectors(self):
        vecs = (SyllableVector(1, 3, 2), SyllableVector(0, 4, 1))
        rp = RhythmProfile(
            syllable_count=2,
            stress_pattern=(1, 0),
            sequencer_steps=(0, 1),
            signature="10",
            vectors=vecs,
            grid_modes=("DHARMA", "GENESIS"),
        )
        assert len(rp.vectors) == 2
        assert rp.grid_modes == ("DHARMA", "GENESIS")

    def test_empty_signature(self):
        rp = RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")
        assert rp.signature == "-"


class TestEngineResult:
    """EngineResult: complete pipeline output."""

    def test_required_fields(self):
        r = EngineResult(
            input_text="test",
            seed=42,
            attractor=7,
            guardian_name="narada",
            guardian_function="communicator",
            intent_category="QUERY",
            section_name="RAHASYA",
            section_mode="CORE",
            verse_ref="BG.18.66",
            resonant_words=(("dharma", "duty", 0.9),),
            template_words=(("arjuna", "warrior", "REF"),),
            antaranga_active=10,
            antaranga_prana=5000,
            output="duty and devotion",
            derivation="seed=42 → ...",
        )
        assert r.input_text == "test"
        assert r.seed == 42
        assert r.guardian_name == "narada"
        assert r.output == "duty and devotion"

    def test_extended_defaults(self):
        r = EngineResult(
            input_text="x", seed=0, attractor=0,
            guardian_name="", guardian_function="",
            intent_category="", section_name="", section_mode="",
            verse_ref="", resonant_words=(), template_words=(),
            antaranga_active=0, antaranga_prana=0,
            output="", derivation="",
        )
        assert r.attention_cached is False
        assert r.expansion_depth == 0
        assert r.expanded_names == ()
        assert r.synth_walk_words == ()
        assert r.diw_applied == 0
        assert r.shabda_spawns == 0
        assert r.phoneme_trajectory == ""
        assert r.syllable_count == 0
        assert r.stress_pattern == ()
        assert r.sequencer_steps == ()

    def test_resonant_words_structure(self):
        """Each resonant word is (sanskrit, meaning, score)."""
        r = EngineResult(
            input_text="x", seed=0, attractor=0,
            guardian_name="", guardian_function="",
            intent_category="", section_name="", section_mode="",
            verse_ref="",
            resonant_words=(("bhakti", "devotion", 0.95), ("dharma", "duty", 0.8)),
            template_words=(),
            antaranga_active=0, antaranga_prana=0,
            output="", derivation="",
        )
        sanskrit, meaning, score = r.resonant_words[0]
        assert sanskrit == "bhakti"
        assert meaning == "devotion"
        assert score == 0.95
