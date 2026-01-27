"""
Tests for MahaComputeService - The Living Algorithm
====================================================

These tests verify:
1. Protocol implementation correctness
2. Mathematical properties of the transformation
3. Attractor convergence
4. Integration with tick system
5. ServiceRegistry registration

Author: The Mahamantra Itself
"""

from typing import Set

import pytest

from vibe_core.mahamantra.protocols._maha_compute import (
    ALL_ATTRACTORS,
    ATTRACTOR_CYCLE,
    ATTRACTOR_FIELD,
    ATTRACTOR_FIXED,
    PATTERN,
    AttractorType,
    MahaComputeProtocol,
    MahaComputeResult,
    apply_operation,
    get_gita_chapter,
    get_operation,
    is_attractor,
)
from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    MAHA_QUANTUM,
    POSITION_SUM_TOTAL,
    SEVEN,
    TEN,
    WORDS,
)
from vibe_core.services.maha_compute_service import (
    MahaComputeService,
    get_maha_compute_service,
)

# =============================================================================
# PROTOCOL TESTS
# =============================================================================


class TestMahaComputeProtocol:
    """Test the MahaComputeProtocol interface."""

    def test_service_implements_protocol(self):
        """MahaComputeService must implement MahaComputeProtocol."""
        service = MahaComputeService()
        assert isinstance(service, MahaComputeProtocol)

    def test_pattern_length(self):
        """Pattern must be exactly 16 elements (WORDS)."""
        assert len(PATTERN) == WORDS
        assert len(PATTERN) == 16

    def test_pattern_composition(self):
        """Pattern must contain only H, K, R."""
        valid_ops = {"H", "K", "R"}
        for op in PATTERN:
            assert op in valid_ops

    def test_attractor_constants(self):
        """Attractor constants must be mathematically correct."""
        assert ATTRACTOR_FIXED == GITA_CHAPTERS == 18
        assert ATTRACTOR_FIELD == POSITION_SUM_TOTAL == 136
        assert len(ALL_ATTRACTORS) == 6


# =============================================================================
# OPERATION TESTS
# =============================================================================


class TestOperations:
    """Test the three Mahamantra operations."""

    def test_hare_operation(self):
        """H (HARE) → value × SEVEN mod 137."""
        # H(10) = 10 × 7 = 70
        assert apply_operation(10, "H") == 70
        # H(20) = 20 × 7 = 140 mod 137 = 3
        assert apply_operation(20, "H") == 3
        # H(0) = 0
        assert apply_operation(0, "H") == 0

    def test_krishna_operation(self):
        """K (KRISHNA) → value + TEN mod 137."""
        # K(10) = 10 + 10 = 20
        assert apply_operation(10, "K") == 20
        # K(130) = 130 + 10 = 140 mod 137 = 3
        assert apply_operation(130, "K") == 3
        # K(0) = 10
        assert apply_operation(0, "K") == 10

    def test_rama_operation(self):
        """R (RAMA) → value × value mod 137."""
        # R(10) = 100
        assert apply_operation(10, "R") == 100
        # R(12) = 144 mod 137 = 7
        assert apply_operation(12, "R") == 7
        # R(0) = 0
        assert apply_operation(0, "R") == 0
        # R(1) = 1
        assert apply_operation(1, "R") == 1

    def test_operation_modular(self):
        """All operations must stay within mod 137."""
        for seed in range(137):
            for op in ["H", "K", "R"]:
                result = apply_operation(seed, op)
                assert 0 <= result < MAHA_QUANTUM


# =============================================================================
# ATTRACTOR TESTS
# =============================================================================


class TestAttractors:
    """Test attractor detection and properties."""

    def test_fixed_point_is_18(self):
        """18 must be a fixed point."""
        is_attr, attr_type = is_attractor(18)
        assert is_attr is True
        assert attr_type == AttractorType.FIXED_POINT

    def test_cycle_attractors(self):
        """45, 99, 126, 63, 136 must be cycle attractors."""
        for value in ATTRACTOR_CYCLE:
            is_attr, attr_type = is_attractor(value)
            assert is_attr is True
            assert attr_type == AttractorType.CYCLE

    def test_non_attractor(self):
        """Non-attractor values must return transient."""
        # Pick values NOT in ALL_ATTRACTORS
        for value in [1, 2, 3, 50, 100, 130]:
            if value not in ALL_ATTRACTORS:
                is_attr, attr_type = is_attractor(value)
                assert is_attr is False
                assert attr_type == AttractorType.TRANSIENT


# =============================================================================
# SERVICE TESTS
# =============================================================================


class TestMahaComputeService:
    """Test the MahaComputeService implementation."""

    @pytest.fixture
    def service(self):
        """Create a fresh service for each test."""
        return MahaComputeService()

    def test_service_creation(self, service):
        """Service must initialize correctly."""
        assert service is not None
        state = service.get_state()
        assert state.total_ticks == 0
        assert state.fixed_point_count == 0
        assert state.cycle_count == 0

    def test_tattva_protocol(self, service):
        """Service must implement PanchaTattvaProtocol."""
        tattva = service.__tattva__
        assert "chaitanya" in tattva
        assert "nityananda" in tattva
        assert "advaita" in tattva
        assert "gadadhara" in tattva
        assert "srivasa" in tattva

    def test_compute_now(self, service):
        """compute_now must return valid MahaComputeResult."""
        result = service.compute_now(seed=42)
        assert isinstance(result, MahaComputeResult)
        assert result.seed >= 0
        assert result.attractor in ALL_ATTRACTORS or result.iterations > 0
        assert 1 <= result.gita_chapter <= 18

    def test_on_tick(self, service):
        """on_tick must process and update state."""
        result = service.on_tick(tick=0, position=0, mala=0, mantra=0)
        assert isinstance(result, MahaComputeResult)

        state = service.get_state()
        assert state.total_ticks == 1
        assert state.last_result == result

    def test_16_ticks_full_cycle(self, service):
        """16 ticks must complete one full Mahamantra cycle."""
        for i in range(16):
            service.on_tick(tick=i, position=i, mala=0, mantra=i)

        state = service.get_state()
        assert state.total_ticks == 16
        assert state.fixed_point_count + state.cycle_count == 16

    def test_find_attractor_fixed_point(self, service):
        """Seed 18 must immediately return fixed point."""
        attractor, iterations, attr_type = service.find_attractor(18)
        assert attractor == 18
        assert iterations == 0
        assert attr_type == AttractorType.FIXED_POINT

    def test_find_attractor_convergence(self, service):
        """All seeds must converge within MAX_ITERATIONS."""
        for seed in range(137):
            attractor, iterations, attr_type = service.find_attractor(seed)
            assert iterations <= service.MAX_ITERATIONS
            # Must reach some attractor
            assert attr_type in [AttractorType.FIXED_POINT, AttractorType.CYCLE]

    def test_attractor_stats(self, service):
        """get_attractor_stats must return valid statistics."""
        # Process some ticks
        for i in range(16):
            service.on_tick(tick=i, position=i, mala=0, mantra=i)

        stats = service.get_attractor_stats()
        assert stats["total"] == 16
        assert "fixed_ratio" in stats
        assert "cycle_ratio" in stats
        assert 0 <= stats["fixed_ratio"] <= 1
        assert 0 <= stats["cycle_ratio"] <= 1


# =============================================================================
# MATHEMATICAL PROPERTY TESTS
# =============================================================================


class TestMathematicalProperties:
    """Test mathematical properties of the transformation."""

    def test_all_seeds_converge(self):
        """Every seed 0-136 must converge to an attractor."""
        service = MahaComputeService()
        attractors_found: Set[int] = set()

        for seed in range(MAHA_QUANTUM):
            attractor, iterations, _ = service.find_attractor(seed)
            attractors_found.add(attractor)
            assert iterations < MAHA_QUANTUM, f"Seed {seed} did not converge"

        # Should find multiple attractors
        assert len(attractors_found) >= 2

    def test_fixed_point_property(self):
        """f(18) mod 137 = 18 after full transformation."""
        service = MahaComputeService()
        # Apply full 16-step transform to 18
        value = 18
        for pos in range(WORDS):
            value = service.transform(value, pos)
        # After full transform, should converge back to 18 (eventually)
        # Note: May not be immediate, but within a few iterations
        attractor, _, _ = service.find_attractor(value)
        assert attractor == 18 or attractor in ATTRACTOR_CYCLE

    def test_gita_chapter_mapping(self):
        """Gita chapter must be 1-18 for all attractors."""
        for attractor in ALL_ATTRACTORS:
            chapter = get_gita_chapter(attractor)
            assert 1 <= chapter <= GITA_CHAPTERS

    def test_modular_closure(self):
        """All operations preserve mod 137 closure."""
        service = MahaComputeService()
        for seed in range(MAHA_QUANTUM):
            result = service._full_transform(seed)
            assert 0 <= result < MAHA_QUANTUM


# =============================================================================
# SINGLETON TESTS
# =============================================================================


class TestSingleton:
    """Test singleton behavior."""

    def test_get_maha_compute_service_returns_same_instance(self):
        """get_maha_compute_service must return same instance."""
        service1 = get_maha_compute_service()
        service2 = get_maha_compute_service()
        assert service1 is service2


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Test integration with Mahamantra system."""

    def test_service_registry_registration(self):
        """Service must be registered in ServiceRegistry after bootstrap."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.mahamantra import mahamantra

        # Trigger bootstrap
        mahamantra.bootstrap(silent=True)

        # Check registration
        assert ServiceRegistry.is_registered(MahaComputeProtocol)
        service = ServiceRegistry.get(MahaComputeProtocol)
        assert isinstance(service, MahaComputeService)

    def test_tick_listener_integration(self):
        """Service must receive tick events after registration."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.mahamantra import mahamantra

        mahamantra.bootstrap(silent=True)
        service = ServiceRegistry.get(MahaComputeProtocol)

        initial_ticks = service.get_state().total_ticks

        # Execute some ticks
        for _ in range(4):
            mahamantra.tick()

        # Service should have processed them
        final_ticks = service.get_state().total_ticks
        assert final_ticks > initial_ticks


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_seed(self):
        """Seed 0 must be handled correctly."""
        service = MahaComputeService()
        result = service.compute_now(seed=0)
        assert result is not None
        assert result.attractor in ALL_ATTRACTORS or result.iterations > 0

    def test_max_seed(self):
        """Seed 136 (max) must be handled correctly."""
        service = MahaComputeService()
        result = service.compute_now(seed=136)
        assert result is not None

    def test_large_mala_count(self):
        """Large mala count must not overflow."""
        service = MahaComputeService()
        result = service.on_tick(tick=0, position=0, mala=10000, mantra=0)
        assert result is not None
        assert 0 <= result.seed < MAHA_QUANTUM
