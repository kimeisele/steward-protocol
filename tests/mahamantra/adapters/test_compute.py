"""
TESTS: MahaCompute - Unified Compute Adapter
============================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all varieties of dharma and surrender unto Me alone."
— Bhagavad Gita 18.66

These tests make MahaCompute ALTAR-WORTHY.
"""

import pytest

from vibe_core.mahamantra.adapters.compute import (
    MahaCompute,
    ComputeUnit,
    DataAnalysis,
    MemoryTier,
    # Constants
    SIMD_LANES,
    CACHE_LINE_BYTES,
    ADDRESS_SPACE,
    L1_CACHE_KB,
    L2_CACHE_KB,
    L3_CACHE_MB,
)
from vibe_core.mahamantra.protocols._seed import WORDS, QUARTERS, QUALITIES


# =============================================================================
# CONSTANTS TESTS
# =============================================================================


class TestMahaComputeConstants:
    """Test constants are derived from seed."""

    def test_simd_lanes_is_words(self):
        """SIMD_LANES must equal WORDS (16)."""
        assert SIMD_LANES == WORDS == 16

    def test_cache_line_is_qualities(self):
        """CACHE_LINE_BYTES must equal QUALITIES (64)."""
        assert CACHE_LINE_BYTES == QUALITIES == 64

    def test_address_space_is_words_pow_quarters(self):
        """ADDRESS_SPACE must be WORDS^QUARTERS (65536)."""
        assert ADDRESS_SPACE == WORDS ** QUARTERS == 65536

    def test_l1_cache_is_qualities(self):
        """L1_CACHE_KB must equal QUALITIES (64)."""
        assert L1_CACHE_KB == QUALITIES

    def test_l2_cache_is_derived(self):
        """L2_CACHE_KB must be QUARTERS * QUALITIES (256)."""
        assert L2_CACHE_KB == QUARTERS * QUALITIES == 256


# =============================================================================
# MEMORY TIER TESTS
# =============================================================================


class TestMemoryTier:
    """Test MemoryTier dataclass."""

    def test_create_memory_tier(self):
        """Can create MemoryTier."""
        tier = MemoryTier(
            name="L1",
            size_kb=64,
            latency_cycles=4,
            lotus_entries=1024,
            quarter=0,
            quarter_name="GENESIS",
        )
        assert tier.name == "L1"
        assert tier.size_kb == 64
        assert tier.lotus_entries == 1024

    def test_size_bytes(self):
        """size_bytes converts KB to bytes."""
        tier = MemoryTier(
            name="L1",
            size_kb=64,
            latency_cycles=4,
            lotus_entries=1024,
            quarter=0,
            quarter_name="GENESIS",
        )
        assert tier.size_bytes == 64 * 1024

    def test_lotus_depth(self):
        """lotus_depth calculates correct depth."""
        tier = MemoryTier(
            name="L2",
            size_kb=256,
            latency_cycles=12,
            lotus_entries=65536,
            quarter=1,
            quarter_name="DHARMA",
        )
        # 65536 = 16^4, so depth should be 4
        assert tier.lotus_depth == 4


# =============================================================================
# COMPUTE UNIT TESTS
# =============================================================================


class TestComputeUnit:
    """Test ComputeUnit alignment analysis."""

    def test_perfect_alignment(self):
        """Perfect Mahamantra alignment scores 1.0."""
        unit = ComputeUnit(
            name="MahaProcessor",
            simd_lanes=16,  # WORDS
            cache_kb=256,   # Multiple of 64
            memory_levels=4,  # QUARTERS
        )
        assert unit.alignment == 1.0
        assert unit.is_unified is True

    def test_partial_alignment(self):
        """Partial alignment scores less than 1.0."""
        unit = ComputeUnit(
            name="StandardCPU",
            simd_lanes=8,   # Not 16
            cache_kb=256,
            memory_levels=3,  # Not 4
        )
        assert 0.0 < unit.alignment < 1.0

    def test_misaligned_unit(self):
        """Misaligned unit is not unified."""
        unit = ComputeUnit(
            name="OddProcessor",
            simd_lanes=7,   # Not power of 2
            cache_kb=100,   # Not multiple of 64
            memory_levels=2,
        )
        assert unit.alignment < 0.5
        assert unit.is_unified is False

    def test_parallelism_factor(self):
        """parallelism_factor returns SIMD lanes."""
        unit = ComputeUnit(
            name="Test",
            simd_lanes=16,
            cache_kb=256,
            memory_levels=4,
        )
        assert unit.parallelism_factor == 16

    def test_verdict_perfect(self):
        """Perfect alignment gives perfect verdict."""
        unit = ComputeUnit(
            name="Perfect",
            simd_lanes=16,
            cache_kb=256,
            memory_levels=4,
        )
        assert "PERFECT" in unit.verdict

    def test_verdict_unified(self):
        """Unified unit gets unified verdict."""
        unit = ComputeUnit(
            name="Unified",
            simd_lanes=16,
            cache_kb=128,  # Not perfect but okay
            memory_levels=4,
        )
        # Should still be unified
        assert unit.is_unified is True


# =============================================================================
# DATA ANALYSIS TESTS
# =============================================================================


class TestDataAnalysis:
    """Test DataAnalysis caching analysis."""

    def test_create_analysis(self):
        """Can create DataAnalysis."""
        analysis = DataAnalysis(
            entries=1000,
            bytes_per_entry=64,
            total_bytes=64000,
            optimal_depth=3,
            memory_tier="L2",
            cache_hit_rate=0.95,
            access_pattern="sequential",
            fits_in_cache=True,
            lotus_capacity=4096,
        )
        assert analysis.entries == 1000
        assert analysis.memory_tier == "L2"
        assert analysis.cache_hit_rate == 0.95

    def test_efficiency_score_high(self):
        """High cache hit + fits in cache = high score."""
        analysis = DataAnalysis(
            entries=100,
            bytes_per_entry=64,
            total_bytes=6400,
            optimal_depth=2,
            memory_tier="L1",
            cache_hit_rate=0.99,
            access_pattern="sequential",
            fits_in_cache=True,
            lotus_capacity=256,
        )
        assert analysis.efficiency_score >= 0.9

    def test_efficiency_score_low(self):
        """RAM-resident with low hit rate = low score."""
        analysis = DataAnalysis(
            entries=1000000,
            bytes_per_entry=64,
            total_bytes=64000000,
            optimal_depth=6,
            memory_tier="RAM",
            cache_hit_rate=0.3,
            access_pattern="random",
            fits_in_cache=False,
            lotus_capacity=16777216,
        )
        assert analysis.efficiency_score < 0.5

    def test_verdict_optimal(self):
        """Optimal analysis gets optimal verdict."""
        analysis = DataAnalysis(
            entries=100,
            bytes_per_entry=64,
            total_bytes=6400,
            optimal_depth=2,
            memory_tier="L1",
            cache_hit_rate=0.99,
            access_pattern="sequential",
            fits_in_cache=True,
            lotus_capacity=256,
        )
        assert "OPTIMAL" in analysis.verdict


# =============================================================================
# MAHACOMPUTE CLASS TESTS
# =============================================================================


class TestMahaCompute:
    """Test MahaCompute main class."""

    @pytest.fixture
    def compute(self) -> MahaCompute:
        """Create MahaCompute instance."""
        return MahaCompute()

    def test_create_instance(self, compute: MahaCompute):
        """Can create MahaCompute instance."""
        assert compute is not None

    def test_analyze_small_data(self, compute: MahaCompute):
        """analyze() works for small data."""
        analysis = compute.analyze(entries=100)

        assert isinstance(analysis, DataAnalysis)
        assert analysis.entries == 100
        assert analysis.memory_tier in ["L1", "L2", "L3", "RAM"]

    def test_analyze_large_data(self, compute: MahaCompute):
        """analyze() works for large data."""
        analysis = compute.analyze(entries=1000000)

        assert isinstance(analysis, DataAnalysis)
        assert analysis.entries == 1000000
        # Large data shouldn't fit in L1
        assert analysis.memory_tier in ["L2", "L3", "RAM"]

    def test_create_unit(self, compute: MahaCompute):
        """create_unit() creates ComputeUnit."""
        unit = compute.create_unit(
            name="TestCPU",
            simd_lanes=16,
            cache_kb=256,
            memory_levels=4,
        )

        assert isinstance(unit, ComputeUnit)
        assert unit.name == "TestCPU"
        assert unit.simd_lanes == 16

    def test_memory_tiers_iterator(self, compute: MahaCompute):
        """memory_tiers() returns iterator of tiers."""
        tiers = list(compute.memory_tiers())

        assert len(tiers) == 4  # L1, L2, L3, RAM
        assert all(isinstance(t, MemoryTier) for t in tiers)

    def test_memory_tiers_ordered(self, compute: MahaCompute):
        """memory_tiers() returns tiers in order."""
        tiers = list(compute.memory_tiers())

        names = [t.name for t in tiers]
        assert names == ["L1", "L2", "L3", "RAM"]

    def test_get_tier_by_name(self, compute: MahaCompute):
        """get_tier() returns tier by name."""
        tier = compute.get_tier("L1")
        assert tier is not None
        assert tier.name == "L1"

        tier = compute.get_tier("RAM")
        assert tier is not None
        assert tier.name == "RAM"

        # Unknown tier returns None
        tier = compute.get_tier("NONEXISTENT")
        assert tier is None

    def test_tier_for_entries(self, compute: MahaCompute):
        """tier_for_entries() returns correct tier for entry count."""
        # Small should fit in L1
        tier = compute.tier_for_entries(10)
        assert tier.name == "L1"

        # Very large needs RAM
        tier = compute.tier_for_entries(10000000)
        assert tier.name == "RAM"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestMahaComputeIntegration:
    """Integration tests for MahaCompute."""

    def test_full_analysis_flow(self):
        """Full analysis flow works end-to-end."""
        compute = MahaCompute()

        # Analyze data
        analysis = compute.analyze(entries=50000, bytes_per_entry=64)

        # Check results make sense
        assert analysis.total_bytes == 50000 * 64
        assert analysis.optimal_depth >= 1
        assert 0.0 <= analysis.cache_hit_rate <= 1.0
        assert analysis.lotus_capacity > 0

    def test_hardware_alignment_flow(self):
        """Hardware alignment flow works."""
        compute = MahaCompute()

        # Create perfect unit
        unit = compute.create_unit(
            name="PerfectCPU",
            simd_lanes=16,
            cache_kb=256,
            memory_levels=4,
        )

        assert unit.is_unified is True
        assert "PERFECT" in unit.verdict

        # Create imperfect unit
        unit2 = compute.create_unit(
            name="OldCPU",
            simd_lanes=4,
            cache_kb=64,
            memory_levels=2,
        )

        assert unit2.alignment < unit.alignment
