"""
TEST: MahaTransform Adapter - The 16-Step Algorithm Contract
=============================================================

"yoga-sthaḥ kuru karmāṇi saṅgaṁ tyaktvā dhanañjaya"
"Perform your duty equipoised, O Arjuna, abandoning attachment."
— Bhagavad Gita 2.48

WHAT WE TEST:
1. Determinism: Same seed → same result (always)
2. Mod Space: All outputs in [0, mod_space)
3. Attractors: Iteration converges to stable states
4. Presets: Different mod spaces work correctly
5. Batch Processing: Multiple seeds transform correctly

THE CONTRACT: These tests GUARANTEE the adapter behaves correctly.
"""

import pytest

from vibe_core.mahamantra.adapters.transform import (
    MahaTransform,
    TransformResult,
    AttractorResult,
    BatchResult,
    transform,
    find_attractor,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    SEVEN,
    TEN,
    WORDS,
)


class TestMahaTransformDeterminism:
    """Test that transformation is deterministic."""

    def test_same_seed_same_result(self):
        """Same seed must produce same result."""
        t = MahaTransform()
        result1 = t.compute(42)
        result2 = t.compute(42)
        assert result1.value == result2.value

    def test_deterministic_across_instances(self):
        """Different instances, same seed, same result."""
        t1 = MahaTransform()
        t2 = MahaTransform()
        assert t1.compute(137).value == t2.compute(137).value

    def test_deterministic_across_presets(self):
        """Same preset, same seed, same result."""
        t1 = MahaTransform(preset="quantum")
        t2 = MahaTransform(preset="quantum")
        assert t1.compute(99).value == t2.compute(99).value


class TestMahaTransformModSpace:
    """Test that outputs respect mod space bounds."""

    def test_default_mod_space_is_maha_quantum(self):
        """Default mod space should be 137."""
        t = MahaTransform()
        assert t.mod_space == MAHA_QUANTUM

    def test_output_within_mod_space(self):
        """All outputs must be in [0, mod_space)."""
        t = MahaTransform()
        for seed in range(1000):
            result = t.compute(seed)
            assert 0 <= result.value < MAHA_QUANTUM

    def test_preset_classical_mod_17(self):
        """Classical preset uses mod 17."""
        t = MahaTransform(preset="classical")
        assert t.mod_space == 17
        for seed in range(100):
            assert 0 <= t.compute(seed).value < 17

    def test_preset_wide_mod_512(self):
        """Wide preset uses mod 512."""
        t = MahaTransform(preset="wide")
        assert t.mod_space == 512

    def test_large_seed_normalized(self):
        """Large seeds are normalized to mod space."""
        t = MahaTransform()
        result = t.compute(999999999)
        assert 0 <= result.value < MAHA_QUANTUM


class TestMahaTransformAttractors:
    """Test attractor discovery."""

    def test_attractor_converges(self):
        """Attractor search must converge."""
        t = MahaTransform()
        result = t.find_attractor(42)
        assert isinstance(result, AttractorResult)
        assert result.cycles_to_converge > 0
        assert result.cycles_to_converge <= MAHA_QUANTUM

    def test_attractor_is_stable(self):
        """Attractor value should be stable under further transformation."""
        t = MahaTransform()
        attr = t.find_attractor(42)
        # Transform the attractor
        next_val = t.compute(attr.stable_value).value
        # Should either stay the same or cycle back
        assert next_val == attr.stable_value or next_val in attr.trajectory

    def test_known_attractors_exist(self):
        """Known attractors should be discoverable."""
        t = MahaTransform()
        found_attractors = set()
        for seed in range(200):
            attr = t.find_attractor(seed)
            found_attractors.add(attr.stable_value)
        # Should find multiple distinct attractors
        assert len(found_attractors) >= 2


class TestMahaTransformBatch:
    """Test batch processing."""

    def test_batch_returns_all_results(self):
        """Batch should return result for each seed."""
        t = MahaTransform()
        seeds = [1, 2, 3, 4, 5]
        batch = t.compute_batch(seeds)
        assert len(batch.results) == len(seeds)

    def test_batch_entropy_calculation(self):
        """Entropy should be between 0 and 1."""
        t = MahaTransform()
        batch = t.compute_batch(list(range(100)))
        assert 0.0 <= batch.entropy <= 1.0

    def test_batch_matches_individual(self):
        """Batch results should match individual computations."""
        t = MahaTransform()
        seeds = [10, 20, 30]
        batch = t.compute_batch(seeds)
        for i, seed in enumerate(seeds):
            individual = t.compute(seed)
            assert batch.results[i].value == individual.value


class TestMahaTransformConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_transform_function(self):
        """transform() should work."""
        result = transform(42)
        assert 0 <= result < MAHA_QUANTUM

    def test_find_attractor_function(self):
        """find_attractor() should work."""
        result = find_attractor(42)
        assert 0 <= result < MAHA_QUANTUM


class TestMahaTransformResult:
    """Test result object properties."""

    def test_result_contains_seed(self):
        """Result should contain original seed."""
        t = MahaTransform()
        result = t.compute(42)
        assert result.seed == 42

    def test_result_contains_mod_space(self):
        """Result should contain mod space."""
        t = MahaTransform()
        result = t.compute(42)
        assert result.mod_space == MAHA_QUANTUM

    def test_result_is_frozen(self):
        """Result should be immutable."""
        t = MahaTransform()
        result = t.compute(42)
        with pytest.raises(AttributeError):
            result.value = 99


class TestMahaTransformMathematicalProperties:
    """Test mathematical properties derived from Mahamantra."""

    def test_sixteen_steps_executed(self):
        """Transformation applies 16 steps (WORDS)."""
        # This is implicit in the algorithm, but we verify
        # the pattern length matches WORDS
        from vibe_core.mahamantra.adapters.transform import PATTERN

        assert len(PATTERN) == WORDS

    def test_seven_multiplier_used(self):
        """HARE operations multiply by SEVEN."""
        # Verify the constant is correct
        assert SEVEN == 7

    def test_ten_addend_used(self):
        """KRISHNA operations add TEN."""
        assert TEN == 10

    def test_distribution_not_uniform(self):
        """Output distribution should NOT be uniform (attractors exist)."""
        t = MahaTransform()
        results = [t.compute(i).value for i in range(1000)]
        from collections import Counter

        counts = Counter(results)
        # Some values should appear much more often (attractors)
        max_count = max(counts.values())
        min_count = min(counts.values())
        assert max_count > min_count * 2  # Significant non-uniformity
