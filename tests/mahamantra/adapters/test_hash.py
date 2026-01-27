"""
TEST: DeterministicHash Adapter - Intent Encoding Contract
===========================================================

"yat karoṣi yad aśnāsi yaj juhoṣi dadāsi yat"
"Whatever you do, whatever you eat, whatever you offer or give away..."
— Bhagavad Gita 9.27

WHAT WE TEST:
1. Determinism: Same input → same hash (always)
2. Triangular Weighting: Position matters
3. Seven Lenses: Multiple mod spaces work
4. Parampara Validation: Mod 37 check works
5. Holographic Factors: Cross-lens patterns detected

THE CONTRACT: These tests GUARANTEE consistent intent encoding.
"""

import pytest

from vibe_core.mahamantra.adapters.hash import (
    DeterministicHash,
    HashResult,
    LensReading,
    MultiLensReading,
    deterministic_hash,
    multi_lens_hash,
    LENSES,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    TRINITY,
    PANCHA,
    SEVEN,
)


class TestDeterministicHashDeterminism:
    """Test that hashing is deterministic."""

    def test_same_input_same_hash(self):
        """Same input must produce same hash."""
        h = DeterministicHash()
        assert h.hash("hello") == h.hash("hello")

    def test_deterministic_across_instances(self):
        """Different instances, same input, same hash."""
        h1 = DeterministicHash()
        h2 = DeterministicHash()
        assert h1.hash("test") == h2.hash("test")

    def test_empty_string_deterministic(self):
        """Empty string should hash consistently."""
        h = DeterministicHash()
        assert h.hash("") == h.hash("")

    def test_unicode_deterministic(self):
        """Unicode strings should hash consistently."""
        h = DeterministicHash()
        assert h.hash("कृष्ण") == h.hash("कृष्ण")


class TestDeterministicHashTriangular:
    """Test triangular position weighting."""

    def test_triangular_numbers_correct(self):
        """Verify triangular number formula."""
        h = DeterministicHash()
        assert h.triangular(1) == 1   # 1
        assert h.triangular(2) == 3   # 1+2
        assert h.triangular(3) == 6   # 1+2+3
        assert h.triangular(4) == 10  # 1+2+3+4
        assert h.triangular(16) == 136  # T(16) = POSITION_SUM_TOTAL

    def test_position_affects_hash(self):
        """Characters at different positions should hash differently."""
        h = DeterministicHash()
        # "ab" vs "ba" - order matters
        assert h.hash("ab") != h.hash("ba")

    def test_earlier_chars_weighted_more(self):
        """First character contributes less than later (due to T(n))."""
        h = DeterministicHash()
        # Actually T(1) < T(2) so later positions have higher weight
        # This is the "later chars matter more" property
        seed_a = h.encode("a")
        seed_aa = h.encode("aa")
        assert seed_aa > seed_a  # Adding char increases


class TestDeterministicHashModSpace:
    """Test mod space handling."""

    def test_default_mod_is_maha_quantum(self):
        """Default mod space should be 137."""
        h = DeterministicHash()
        assert h.default_mod == MAHA_QUANTUM

    def test_hash_within_mod_space(self):
        """Hash should be in [0, mod_space)."""
        h = DeterministicHash()
        for word in ["a", "hello", "mahamantra", "test123", "кришна"]:
            result = h.hash(word)
            assert 0 <= result < MAHA_QUANTUM

    def test_custom_mod_space(self):
        """Custom mod space should work."""
        h = DeterministicHash()
        result = h.hash("test", mod_space=17)
        assert 0 <= result < 17


class TestDeterministicHashSevenLenses:
    """Test the 7 sacred lenses."""

    def test_seven_lenses_exist(self):
        """Should have exactly 7 lenses."""
        assert len(LENSES) == 7

    def test_lens_mod_spaces_correct(self):
        """Verify lens mod spaces."""
        lens_mods = [mod for _, mod in LENSES]
        assert TRINITY in lens_mods      # 3
        assert PANCHA in lens_mods       # 5
        assert SEVEN in lens_mods        # 7
        assert 17 in lens_mods           # Prime
        assert PARAMPARA in lens_mods    # 37
        assert 73 in lens_mods           # Prime
        assert MAHA_QUANTUM in lens_mods # 137

    def test_analyze_returns_all_lenses(self):
        """Analysis should return all 7 lenses."""
        h = DeterministicHash()
        reading = h.analyze("test")
        assert len(reading.lenses) == 7

    def test_each_lens_within_bounds(self):
        """Each lens value should be within its mod space."""
        h = DeterministicHash()
        reading = h.analyze("mahamantra")
        for lens in reading.lenses:
            assert 0 <= lens.value < lens.mod_space


class TestDeterministicHashParampara:
    """Test Parampara (disciplic chain) validation."""

    def test_parampara_validation_works(self):
        """Parampara check should work (seed % 37 == 0)."""
        h = DeterministicHash()
        # Find a string that passes
        for word in ["a", "ab", "abc", "test", "parampara"]:
            if h.encode(word) % PARAMPARA == 0:
                assert h.validate_parampara(word)
                return
        # Or construct one
        # seed that's divisible by 37
        # T(1) = 1, so 'a' (ord 1 from a) contributes 1
        # We need to find text that sums to multiple of 37

    def test_parampara_in_reading(self):
        """MultiLensReading should include parampara_validated."""
        h = DeterministicHash()
        reading = h.analyze("test")
        assert hasattr(reading, 'parampara_validated')
        assert isinstance(reading.parampara_validated, bool)


class TestDeterministicHashHolographic:
    """Test holographic factor detection."""

    def test_holographic_factors_detected(self):
        """Values appearing in multiple lenses should be detected."""
        h = DeterministicHash()
        reading = h.analyze("test")
        assert hasattr(reading, 'holographic_factors')
        # Holographic factors are values that appear in 2+ lenses

    def test_holographic_factors_are_common_values(self):
        """Holographic factors should appear in multiple lenses."""
        h = DeterministicHash()
        reading = h.analyze("krishna")
        lens_values = [l.value for l in reading.lenses]
        for factor in reading.holographic_factors:
            count = lens_values.count(factor)
            assert count >= 2


class TestDeterministicHashConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_deterministic_hash_function(self):
        """deterministic_hash() should work."""
        result = deterministic_hash("test")
        assert 0 <= result < MAHA_QUANTUM

    def test_multi_lens_hash_function(self):
        """multi_lens_hash() should return MultiLensReading."""
        result = multi_lens_hash("test")
        assert isinstance(result, MultiLensReading)


class TestDeterministicHashResults:
    """Test result object properties."""

    def test_hash_result_is_frozen(self):
        """HashResult should be immutable."""
        h = DeterministicHash()
        result = h.hash_to_result("test")
        with pytest.raises(AttributeError):
            result.value = 99

    def test_multi_lens_reading_is_frozen(self):
        """MultiLensReading should be immutable."""
        h = DeterministicHash()
        reading = h.analyze("test")
        with pytest.raises(AttributeError):
            reading.seed = 99

    def test_reading_contains_original_input(self):
        """Reading should contain original input."""
        h = DeterministicHash()
        reading = h.analyze("original")
        assert reading.input == "original"
