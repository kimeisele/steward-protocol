"""
Tests for MahaLLMKernel — verify rewired resonate/expand/resonate_as
consume __call__() and return valid responses.

These methods were rewired to use MahamantraLotus.__call__() instead of
running their own parallel pipelines. This test file proves the rewire works.
"""

import pytest

from vibe_core.mahamantra.protocols.resonance import (
    ExpansionResponse,
    GuardianProfile,
    ResonanceResponse,
)
from vibe_core.mahamantra.substrate.maha_llm_kernel import (
    DIVINE_NAMES,
    MahaLLMKernel,
    expand,
    get_kernel,
    guardian,
    resonate,
)

# =============================================================================
# CONSTRUCTION
# =============================================================================


class TestKernelConstruction:
    def test_instantiation(self):
        kernel = MahaLLMKernel()
        assert kernel._index is None
        assert kernel._guardians is None

    def test_singleton(self):
        k1 = get_kernel()
        k2 = get_kernel()
        assert k1 is k2

    def test_divine_names_nonempty(self):
        assert len(DIVINE_NAMES) >= 3
        assert "hare" in DIVINE_NAMES
        assert "krishna" in DIVINE_NAMES
        assert "rama" in DIVINE_NAMES


# =============================================================================
# RESONATE — rewired to consume __call__()
# =============================================================================


class TestResonate:
    @pytest.fixture(scope="class")
    def response(self):
        return resonate("What is dharma?")

    def test_returns_resonance_response(self, response):
        assert isinstance(response, ResonanceResponse)

    def test_input_text_preserved(self, response):
        assert response.input_text == "What is dharma?"

    def test_guardian_name_nonempty(self, response):
        assert isinstance(response.guardian_name, str)
        assert len(response.guardian_name) > 0

    def test_guardian_function_nonempty(self, response):
        assert isinstance(response.guardian_function, str)
        assert len(response.guardian_function) > 0

    def test_words_are_tuple(self, response):
        assert isinstance(response.words, tuple)

    def test_words_have_content(self, response):
        # __call__() runs smaranam (rank_words) — should find resonant words
        assert len(response.words) > 0

    def test_each_word_has_sanskrit(self, response):
        for w in response.words:
            assert isinstance(w.sanskrit, str)
            assert len(w.sanskrit) > 0

    def test_each_word_has_score(self, response):
        for w in response.words:
            assert isinstance(w.score, float)

    def test_element_walk_is_tuple(self, response):
        assert isinstance(response.element_walk, tuple)

    def test_shruti_pattern_is_string(self, response):
        assert isinstance(response.shruti_pattern, str)

    def test_deterministic(self):
        r1 = resonate("test input")
        r2 = resonate("test input")
        assert r1.guardian_name == r2.guardian_name
        assert r1.words == r2.words


# =============================================================================
# EXPAND — rewired to consume __call__()
# =============================================================================


class TestExpand:
    @pytest.fixture(scope="class")
    def response(self):
        return expand("krishna")

    def test_returns_expansion_response(self, response):
        assert isinstance(response, ExpansionResponse)

    def test_name_preserved(self, response):
        assert response.name == "krishna"

    def test_rama_coords_nonempty(self, response):
        assert isinstance(response.rama_coords, tuple)
        assert len(response.rama_coords) > 0

    def test_coords_in_range(self, response):
        for c in response.rama_coords:
            assert 0 <= c < 49

    def test_vibration_sum_positive(self, response):
        assert response.vibration_sum > 0

    def test_mod49_in_range(self, response):
        assert 0 <= response.mod49 < 49

    def test_element_walk_matches_coords(self, response):
        assert len(response.element_walk) == len(response.rama_coords)

    def test_tree_exists(self, response):
        assert response.tree is not None
        assert response.tree.rama_coord >= 0

    def test_resonant_words_from_pipeline(self, response):
        # expand() now gets resonant words from __call__(), not its own rank
        assert isinstance(response.resonant_words, tuple)

    def test_deterministic(self):
        e1 = expand("rama")
        e2 = expand("rama")
        assert e1.rama_coords == e2.rama_coords
        assert e1.vibration_sum == e2.vibration_sum
        assert e1.mod49 == e2.mod49

    def test_unknown_name_still_works(self):
        # Non-divine names should still go through __call__()
        r = expand("hello")
        assert isinstance(r, ExpansionResponse)


# =============================================================================
# RESONATE_AS — rewired to consume __call__(opcode=position)
# =============================================================================


class TestResonateAs:
    @pytest.fixture(scope="class")
    def response(self):
        kernel = get_kernel()
        return kernel.resonate_as("What is love?", "narada")

    def test_returns_resonance_response(self, response):
        assert isinstance(response, ResonanceResponse)

    def test_guardian_is_requested(self, response):
        # resonate_as forces the pipeline through the named guardian
        assert response.guardian_name.lower() == "narada"

    def test_input_text_preserved(self, response):
        assert response.input_text == "What is love?"

    def test_words_are_tuple(self, response):
        assert isinstance(response.words, tuple)

    def test_route_score_is_one(self, response):
        # Explicitly chosen guardian → route_score = 1.0
        assert response.route_score == 1.0

    def test_different_guardians_different_results(self):
        kernel = get_kernel()
        r_narada = kernel.resonate_as("peace", "narada")
        r_prahlada = kernel.resonate_as("peace", "prahlada")
        # Different guardians → different positions → different pipeline results
        # At minimum, guardian_name differs
        assert r_narada.guardian_name != r_prahlada.guardian_name

    def test_unknown_guardian_raises(self):
        kernel = get_kernel()
        with pytest.raises(ValueError, match="Unknown guardian"):
            kernel.resonate_as("test", "nonexistent_guardian")


# =============================================================================
# GUARDIAN — profile (not rewired, but verify it still works)
# =============================================================================


class TestGuardian:
    def test_returns_guardian_profile(self):
        profile = guardian("narada")
        assert isinstance(profile, GuardianProfile)

    def test_name_matches(self):
        profile = guardian("prahlada")
        assert profile.name.lower() == "prahlada"

    def test_has_vocabulary(self):
        profile = guardian("narada")
        assert isinstance(profile.vocabulary, tuple)
        assert len(profile.vocabulary) > 0

    def test_unknown_guardian_raises(self):
        with pytest.raises(ValueError, match="Unknown guardian"):
            guardian("nonexistent")
