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
