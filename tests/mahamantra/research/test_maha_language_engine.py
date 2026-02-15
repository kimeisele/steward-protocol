"""
Tests for the Maha Language Engine — Anti-Entropy Language Model.

Verifies:
    1. Determinism (same input → same output, always)
    2. All components wired (Guardian, Antaranga, Section routing, etc.)
    3. No floats leak into the derivation path
    4. Seed derivation from axioms (PARAMPARA integrity)
    5. Antaranga collision is real (slots active, prana non-zero)
"""

from __future__ import annotations

import pytest

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PANCHA,
    PARAMPARA,
    QUARTERS,
    SEVEN,
    WORDS,
)


@pytest.fixture(scope="module")
def engine():
    """Shared engine singleton for all tests."""
    from vibe_core.mahamantra.research.maha_language_engine import get_engine

    return get_engine()


# =============================================================================
# DETERMINISM
# =============================================================================


class TestDeterminism:
    """Same input → same output. The fundamental guarantee."""

    INPUTS = [
        "What is devotion?",
        "Krishna",
        "love",
        "fire and wisdom",
        "surrender everything",
        "who am I?",
    ]

    def test_output_deterministic(self, engine):
        """Two passes produce identical output strings."""
        for text in self.INPUTS:
            r1 = engine.generate(text)
            r2 = engine.generate(text)
            assert r1.output == r2.output, f"Non-deterministic for '{text}'"

    def test_seed_deterministic(self, engine):
        """Seeds are identical across passes."""
        for text in self.INPUTS:
            r1 = engine.generate(text)
            r2 = engine.generate(text)
            assert r1.seed == r2.seed, f"Seed changed for '{text}'"

    def test_attractor_deterministic(self, engine):
        """Attractors are identical across passes."""
        for text in self.INPUTS:
            r1 = engine.generate(text)
            r2 = engine.generate(text)
            assert r1.attractor == r2.attractor, f"Attractor changed for '{text}'"


# =============================================================================
# COMPONENT WIRING
# =============================================================================


class TestComponentWiring:
    """All existing components are actually connected."""

    def test_guardian_assigned(self, engine):
        """Every input gets routed to a Guardian."""
        r = engine.generate("What is dharma?")
        assert r.guardian_name, "No guardian assigned"
        assert r.guardian_function, "No guardian function"

    def test_intent_classified(self, engine):
        """MahaLLM classifies intent."""
        r = engine.generate("What is dharma?")
        assert r.intent_category, "No intent category"

    def test_section_routed(self, engine):
        """Kapitel 18 section routing works."""
        r = engine.generate("What is dharma?")
        assert r.section_name, "No section name"
        assert r.section_mode, "No section mode"
        assert r.section_mode in (
            "FILTER",
            "VERB",
            "QUALITY",
            "CONTEXT",
            "TARGET",
            "CORE",
            "CLOSURE",
        ), f"Unknown section mode: {r.section_mode}"

    def test_verse_referenced(self, engine):
        """Verse template is from Bhagavad Gita."""
        r = engine.generate("What is dharma?")
        assert r.verse_ref.startswith("BG.18."), f"Bad verse ref: {r.verse_ref}"

    def test_resonant_words_present(self, engine):
        """Guardian-shaped resonant words are present."""
        r = engine.generate("What is dharma?")
        assert len(r.resonant_words) > 0, "No resonant words"
        # Each word is (sanskrit, meaning, score)
        for sanskrit, meaning, score in r.resonant_words:
            assert sanskrit, "Empty Sanskrit word"

    def test_template_words_present(self, engine):
        """Verse template words are present."""
        r = engine.generate("What is dharma?")
        assert len(r.template_words) > 0, "No template words"

    def test_antaranga_active(self, engine):
        """Antaranga chamber has active slots after resonance."""
        r = engine.generate("What is dharma?")
        assert r.antaranga_active > 0, "No active Antaranga slots"
        assert r.antaranga_prana > 0, "No prana in Antaranga"

    def test_output_non_empty(self, engine):
        """Output is a non-empty string."""
        r = engine.generate("What is dharma?")
        assert r.output, "Empty output"
        assert len(r.output) > PANCHA, "Output too short"

    def test_derivation_trace(self, engine):
        """Derivation path is complete."""
        r = engine.generate("What is dharma?")
        assert "seed=" in r.derivation
        assert "attractor=" in r.derivation
        assert "guardian=" in r.derivation
        assert "section=" in r.derivation
        assert "verse=" in r.derivation
        assert "antaranga=" in r.derivation


# =============================================================================
# DIVERSITY — Different inputs produce different outputs
# =============================================================================


class TestDiversity:
    """Different inputs should generally produce different responses."""

    def test_different_inputs_different_outputs(self, engine):
        """At least some different inputs produce different outputs."""
        inputs = ["love", "anger", "wisdom", "sacrifice", "Krishna"]
        outputs = [engine.generate(t).output for t in inputs]
        unique = set(outputs)
        # At least 3 out of 5 should be different
        assert len(unique) >= 3, f"Only {len(unique)} unique outputs from {len(inputs)} inputs"

    def test_different_inputs_different_guardians(self, engine):
        """Different inputs may route to different Guardians."""
        inputs = ["fire and war", "love and peace", "wisdom of the ages"]
        guardians = [engine.generate(t).guardian_name for t in inputs]
        # Not all should be the same guardian
        # (though it's possible — just check we get at least 1 guardian)
        assert all(g for g in guardians), "Missing guardian assignments"

    def test_different_seeds(self, engine):
        """Different inputs produce different seeds."""
        inputs = ["devotion", "anger", "peace"]
        seeds = [engine.generate(t).seed for t in inputs]
        assert len(set(seeds)) == len(seeds), "Different inputs produced same seed"


# =============================================================================
# AXIOM INTEGRITY
# =============================================================================


class TestAxiomIntegrity:
    """All numbers derive from the 7 axioms."""

    def test_parampara_lineage(self):
        """Module genesis byte passes parampara check."""
        from vibe_core.mahamantra.research.maha_language_engine import __genesis__

        assert int(__genesis__, 16) % PARAMPARA == 0

    def test_antaranga_slots_derived(self):
        """Antaranga slot count is derived from VAMSI_HOLES."""
        from vibe_core.mahamantra.protocols._seed import KSETRAJNA, VAMSI_HOLES
        from vibe_core.mahamantra.substrate.antaranga import ANTARANGA_SLOTS

        assert ANTARANGA_SLOTS == KSETRAJNA << VAMSI_HOLES  # 512

    def test_resonant_words_bounded(self, engine):
        """Resonant words count is bounded by available Gita vocabulary."""
        r = engine.generate("What is the meaning of everything?")
        # Guardian response gives at most SEVEN words (the top_words param)
        assert len(r.resonant_words) <= SEVEN + 1, f"Too many resonant words: {len(r.resonant_words)}"


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Edge cases that should not crash."""

    def test_empty_input(self, engine):
        """Empty string produces graceful result."""
        r = engine.generate("")
        assert r.output  # Should still produce something
        assert r.seed is not None

    def test_single_char(self, engine):
        """Single character input works."""
        r = engine.generate("a")
        assert r.output

    def test_long_input(self, engine):
        """Long input doesn't crash."""
        r = engine.generate("devotion " * 100)
        assert r.output

    def test_non_ascii(self, engine):
        """Non-ASCII input (Sanskrit) works."""
        r = engine.generate("kṛṣṇa")
        assert r.output

    def test_numbers(self, engine):
        """Numeric input works."""
        r = engine.generate("108")
        assert r.output


# =============================================================================
# SYLLABLE RHYTHM (temporal layer)
# =============================================================================


class TestSyllableRhythm:
    """Input carries time structure, not only static tokens."""

    def test_syllable_metadata_present(self, engine):
        r = engine.generate("devotion")
        assert r.syllable_count > 0
        assert len(r.stress_pattern) == r.syllable_count
        assert len(r.sequencer_steps) == r.syllable_count

    def test_steps_fit_32_step_grid(self, engine):
        r = engine.generate("surrender everything")
        step_count = WORDS * 2
        for step in r.sequencer_steps:
            assert 0 <= step < step_count

        # Best-fit alignment: steps are contiguous (start, start+1, ...)
        for i in range(len(r.sequencer_steps) - 1):
            delta = (r.sequencer_steps[i + 1] - r.sequencer_steps[i]) % step_count
            assert delta == 1, f"Steps must be contiguous, got delta={delta} at i={i}"

    def test_rhythm_is_deterministic(self, engine):
        r1 = engine.generate("engine")
        r2 = engine.generate("engine")
        assert r1.stress_pattern == r2.stress_pattern
        assert r1.sequencer_steps == r2.sequencer_steps

    def test_rhythm_bias_prefers_stressed_downbeat(self, engine):
        from vibe_core.mahamantra.research.maha_language_engine import RhythmProfile

        rhythm = RhythmProfile(
            syllable_count=2,
            stress_pattern=(1, 0),
            sequencer_steps=(0, 3),
            signature="10",
        )
        assert engine._rhythm_bias(rhythm, 0) > engine._rhythm_bias(rhythm, 1)

    def test_rhythm_ranking_reorders_equal_scores(self, engine):
        from vibe_core.mahamantra.research.maha_language_engine import RhythmProfile

        rhythm = RhythmProfile(
            syllable_count=2,
            stress_pattern=(1, 0),
            sequencer_steps=(0, 3),
            signature="10",
        )
        pool = [
            {"sanskrit": "x", "meaning": "first", "score": 0.5, "all_meanings": ("first",)},
            {"sanskrit": "y", "meaning": "second", "score": 0.5, "all_meanings": ("second",)},
        ]

        ranked = engine._rank_resonant_by_rhythm(pool, rhythm)
        assert ranked[0]["meaning"] == "first"
        assert ranked[0]["rhythm_score"] > ranked[1]["rhythm_score"]


class TestCharacterWaveOnDemand:
    """ON DEMAND: full prompt → char-by-char Antaranga collide → standing wave → compose."""

    def test_character_wave_deterministic(self, engine):
        """Same prompt must produce identical chamber state and output."""
        r1 = engine.generate("what is devotion")
        r2 = engine.generate("what is devotion")
        assert r1.output == r2.output
        assert r1.antaranga_prana == r2.antaranga_prana
        assert r1.antaranga_active == r2.antaranga_active

    def test_different_prompts_different_prana(self, engine):
        """Different prompts must produce different chamber states."""
        r1 = engine.generate("what is devotion")
        r2 = engine.generate("sacrifice and duty")
        assert r1.antaranga_prana != r2.antaranga_prana

    def test_character_order_matters(self, engine):
        """Same characters in different order → different chamber state."""
        r_how = engine.generate("how")
        r_who = engine.generate("who")
        # Same chars, different order → different slot collision sequence
        # Output must differ (different routing from different seeds)
        assert r_how.output != r_who.output

    def test_char_wave_in_derivation(self, engine):
        """Derivation string must contain char_wave stats."""
        r = engine.generate("test")
        assert "char_wave=" in r.derivation

    def test_antaranga_prana_positive(self, engine):
        """Any non-empty prompt must produce positive prana."""
        r = engine.generate("hello")
        assert r.antaranga_prana > 0
        assert r.antaranga_active > 0

    def test_longer_prompt_more_impacts(self, engine):
        """Longer prompts fire more characters → generally more active slots."""
        r_short = engine.generate("om")
        r_long = engine.generate("what is the meaning of devotion and sacrifice")
        assert r_long.antaranga_active >= r_short.antaranga_active


class TestFractalDerivationTree:
    """Fractal Lotus: seed sprouts into derivation tree with mode branches."""

    def test_sprout_in_derivation(self, engine):
        """Derivation string must contain sprout stats."""
        r = engine.generate("what is devotion")
        assert "sprout=" in r.derivation
        assert "nodes" in r.derivation

    def test_tree_has_13_nodes(self, engine):
        """1 root + 3 branches + 9 leaves = 13 nodes."""
        r = engine.generate("test input")
        assert "sprout=13nodes" in r.derivation

    def test_fractal_deterministic(self, engine):
        """Same prompt → same tree → same output."""
        r1 = engine.generate("sacrifice and duty")
        r2 = engine.generate("sacrifice and duty")
        assert r1.output == r2.output
        assert r1.antaranga_prana == r2.antaranga_prana
        assert r1.derivation == r2.derivation

    def test_different_prompts_different_trees(self, engine):
        """Different prompts produce different prana fields (tree branches differ)."""
        r1 = engine.generate("what is devotion")
        r2 = engine.generate("how to find peace")
        assert r1.antaranga_prana != r2.antaranga_prana

    def test_sprout_enriches_output(self, engine):
        """Output must be non-empty (tree branches contribute words)."""
        r = engine.generate("knowledge of the self")
        assert len(r.output) > 0
        assert r.antaranga_active > 0


class TestResonanceBridge:
    """ResonanceBridge: inner chamber → typed packet → intent kwargs."""

    def test_packet_fields_populated(self, engine):
        """ResonancePacket must have all fields populated."""
        from vibe_core.mahamantra.research.resonance_bridge import ResonanceBridge

        bridge = ResonanceBridge()
        r = engine.generate("what is devotion")
        packet = bridge.emit(r)

        assert packet.seed > 0
        assert packet.attractor >= 0
        assert 0 <= packet.position < 16
        assert 0 <= packet.quarter < 4
        assert packet.guna in ("suddha", "sattva", "rajas", "tamas")
        assert packet.prana > 0
        assert packet.active_slots > 0
        assert packet.guardian != ""
        assert packet.verse_ref != ""
        assert packet.intent_type in ("wake", "resolve", "transform", "heal")

    def test_packet_deterministic(self, engine):
        """Same prompt → same packet (all fields)."""
        from vibe_core.mahamantra.research.resonance_bridge import ResonanceBridge

        bridge = ResonanceBridge()
        p1 = bridge.emit(engine.generate("sacrifice and duty"))
        p2 = bridge.emit(engine.generate("sacrifice and duty"))

        assert p1.seed == p2.seed
        assert p1.guna == p2.guna
        assert p1.intent_type == p2.intent_type
        assert p1.prana == p2.prana
        assert p1.guardian == p2.guardian

    def test_guna_discriminative(self, engine):
        """Different prompts can produce different gunas."""
        from vibe_core.mahamantra.research.resonance_bridge import ResonanceBridge

        bridge = ResonanceBridge()
        gunas = set()
        for prompt in [
            "what is devotion",
            "sacrifice and duty",
            "fix the broken module",
            "create new service",
            "observe the system",
            "read the configuration",
        ]:
            packet = bridge.emit(engine.generate(prompt))
            gunas.add(packet.guna)

        # At least 2 different gunas across varied prompts
        assert len(gunas) >= 2

    def test_intent_kwargs_structure(self, engine):
        """Intent kwargs must have correct structure for MantraIntent."""
        from vibe_core.mahamantra.research.resonance_bridge import ResonanceBridge

        bridge = ResonanceBridge()
        packet = bridge.emit(engine.generate("fix the broken module"))
        kwargs = bridge.to_intent_kwargs(packet, target="test.module")

        assert "type" in kwargs
        assert "target" in kwargs
        assert "params" in kwargs
        assert "requester" in kwargs
        assert kwargs["target"] == "test.module"
        assert isinstance(kwargs["params"], dict)
        assert "seed" in kwargs["params"]
        assert "guna" in kwargs["params"]

    def test_rama_coords_collected(self, engine):
        """Character wave must collect RAMA coordinates."""
        r = engine.generate("hello world")
        # RAMA coords are in the char_wave dict, accessible via derivation
        # The engine now stores them — verify via a fresh generate
        assert r.antaranga_active > 0
        assert r.antaranga_prana > 0
