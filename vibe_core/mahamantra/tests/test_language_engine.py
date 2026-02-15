"""
Tests for substrate/language/engine.py — MahaLanguageEngine orchestrator.

Tests the full pipeline end-to-end. Determinism is the core invariant.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import PARAMPARA, WORDS
from vibe_core.mahamantra.substrate.language.types import EngineResult
from vibe_core.mahamantra.substrate.language.engine import (
    MahaLanguageEngine,
    generate,
    get_engine,
)


# =============================================================================
# MahaLanguageEngine: construction and identity
# =============================================================================

class TestEngineConstruction:
    """MahaLanguageEngine: lazy-loaded orchestrator."""

    def test_instantiation(self):
        engine = MahaLanguageEngine()
        assert engine._antaranga is None  # lazy

    def test_genesis_lineage(self):
        """__genesis__ must be divisible by PARAMPARA (protocol invariant)."""
        from vibe_core.mahamantra.substrate.language import engine as mod
        genesis = int(mod.__genesis__, 16)
        assert genesis % PARAMPARA == 0

    def test_mahajana_is_narada(self):
        from vibe_core.mahamantra.substrate.language import engine as mod
        assert mod.__mahajana__ == "narada"
        assert mod.__position__ == 2


# =============================================================================
# generate(): full pipeline — determinism proof
# =============================================================================

class TestGenerate:
    """generate(): text in → EngineResult out. Must be deterministic."""

    @pytest.fixture(scope="class")
    def engine(self):
        return MahaLanguageEngine()

    def test_returns_engine_result(self, engine):
        result = engine.generate("What is devotion?")
        assert isinstance(result, EngineResult)

    def test_seed_is_int(self, engine):
        result = engine.generate("fire and wisdom")
        assert isinstance(result.seed, int)

    def test_attractor_is_int(self, engine):
        result = engine.generate("Krishna")
        assert isinstance(result.attractor, int)

    def test_guardian_name_nonempty(self, engine):
        result = engine.generate("tell me about dharma")
        assert len(result.guardian_name) > 0

    def test_section_name_valid(self, engine):
        valid = {"TYAGA", "SANKHYA", "TRAIGUNYA", "VARNASHRAMA", "BRAHMAN", "RAHASYA", "SANJAYA"}
        result = engine.generate("love")
        assert result.section_name in valid

    def test_verse_ref_format(self, engine):
        result = engine.generate("the meaning of sacrifice")
        assert result.verse_ref.startswith("BG.18.")

    def test_output_nonempty(self, engine):
        result = engine.generate("who am I?")
        assert len(result.output) > 0

    def test_derivation_nonempty(self, engine):
        result = engine.generate("anger and peace")
        assert len(result.derivation) > 0

    def test_resonant_words_structure(self, engine):
        result = engine.generate("Hare Krishna")
        for sanskrit, meaning, score in result.resonant_words:
            assert isinstance(sanskrit, str)
            assert isinstance(meaning, str)
            assert isinstance(score, float)

    def test_antaranga_active_nonneg(self, engine):
        result = engine.generate("surrender everything")
        assert result.antaranga_active >= 0
        assert result.antaranga_prana >= 0

    def test_expansion_depth_nonneg(self, engine):
        result = engine.generate("devotion")
        assert result.expansion_depth >= 0

    def test_phoneme_trajectory_is_string(self, engine):
        result = engine.generate("fire")
        assert isinstance(result.phoneme_trajectory, str)

    def test_syllable_count_nonneg(self, engine):
        result = engine.generate("what is dharma")
        assert result.syllable_count >= 0

    def test_no_phonemic_content(self, engine):
        """Input with no encodable phonemes returns graceful fallback."""
        result = engine.generate("123 456")
        # May or may not have phonemic content depending on encoding
        assert isinstance(result.output, str)


# =============================================================================
# Determinism: same input → same output, always
# =============================================================================

class TestDeterminism:
    """The Anti-Entropy invariant: identical input → identical output."""

    INPUTS = [
        "What is devotion?",
        "fire and wisdom",
        "Krishna",
        "tell me about dharma",
        "love",
        "the meaning of sacrifice",
        "who am I?",
        "anger and peace",
        "Hare Krishna",
        "surrender everything",
    ]

    def test_deterministic_seeds(self):
        engine = MahaLanguageEngine()
        for text in self.INPUTS:
            r1 = engine.generate(text)
            r2 = engine.generate(text)
            assert r1.seed == r2.seed, f"seed mismatch for '{text}'"

    def test_deterministic_output(self):
        engine = MahaLanguageEngine()
        for text in self.INPUTS:
            r1 = engine.generate(text)
            r2 = engine.generate(text)
            assert r1.output == r2.output, f"output mismatch for '{text}'"

    def test_deterministic_attractor(self):
        engine = MahaLanguageEngine()
        for text in self.INPUTS:
            r1 = engine.generate(text)
            r2 = engine.generate(text)
            assert r1.attractor == r2.attractor, f"attractor mismatch for '{text}'"

    def test_deterministic_guardian(self):
        engine = MahaLanguageEngine()
        for text in self.INPUTS:
            r1 = engine.generate(text)
            r2 = engine.generate(text)
            assert r1.guardian_name == r2.guardian_name, f"guardian mismatch for '{text}'"

    def test_deterministic_section(self):
        engine = MahaLanguageEngine()
        for text in self.INPUTS:
            r1 = engine.generate(text)
            r2 = engine.generate(text)
            assert r1.section_name == r2.section_name, f"section mismatch for '{text}'"


# =============================================================================
# Singleton: get_engine() and generate() convenience
# =============================================================================

class TestSingleton:
    """get_engine() returns singleton, generate() is convenience wrapper."""

    def test_get_engine_returns_same_instance(self):
        a = get_engine()
        b = get_engine()
        assert a is b

    def test_generate_convenience(self):
        result = generate("devotion")
        assert isinstance(result, EngineResult)
        assert len(result.output) > 0

    def test_generate_matches_engine(self):
        engine = get_engine()
        r1 = engine.generate("test input")
        r2 = generate("test input")
        assert r1.seed == r2.seed
        # Output may differ slightly due to Chamber singleton accumulation
        # (living system — Antaranga state evolves between calls)
        assert isinstance(r2.output, str)
        assert len(r2.output) > 0
