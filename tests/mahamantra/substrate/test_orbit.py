"""
TESTS: orbit.py - Orbital Clockwork Logic
==========================================

"jyotir-anīkāni" - The Army of Luminaries.

REAL TESTS for:
1. OrbitCalculator class
2. get_phase_offset() method
3. should_dance() method
"""

import pytest
from vibe_core.mahamantra.substrate.orbit import OrbitCalculator


# =============================================================================
# OrbitCalculator Instantiation Tests
# =============================================================================


class TestOrbitCalculatorInstantiation:
    """Test OrbitCalculator instantiation."""

    def test_orbit_calculator_exists(self):
        """OrbitCalculator class exists."""
        assert OrbitCalculator is not None

    def test_orbit_calculator_instantiation(self):
        """OrbitCalculator can be instantiated."""
        calc = OrbitCalculator()
        assert calc is not None


# =============================================================================
# get_phase_offset Tests
# =============================================================================


class TestGetPhaseOffset:
    """Test OrbitCalculator.get_phase_offset method."""

    def test_phase_offset_is_deterministic(self):
        """Same entity_id always produces same offset."""
        calc = OrbitCalculator()
        entity_id = "test_entity_123"
        offset1 = calc.get_phase_offset(entity_id)
        offset2 = calc.get_phase_offset(entity_id)
        assert offset1 == offset2

    def test_phase_offset_in_range(self):
        """Phase offset is within modulus range."""
        calc = OrbitCalculator()
        for entity_id in ["entity_a", "entity_b", "entity_c", "xyz123"]:
            offset = calc.get_phase_offset(entity_id)
            assert 0 <= offset < 16, f"Offset {offset} out of range"

    def test_phase_offset_different_entities(self):
        """Different entities can have different offsets."""
        calc = OrbitCalculator()
        offsets = set()
        # Test many entities to find different offsets
        for i in range(100):
            offset = calc.get_phase_offset(f"entity_{i}")
            offsets.add(offset)
        # Should have multiple different offsets
        assert len(offsets) > 1

    def test_phase_offset_custom_modulus(self):
        """Phase offset respects custom modulus."""
        calc = OrbitCalculator()
        offset = calc.get_phase_offset("test", modulus=4)
        assert 0 <= offset < 4

    def test_phase_offset_modulus_1(self):
        """Phase offset with modulus 1 is always 0."""
        calc = OrbitCalculator()
        offset = calc.get_phase_offset("any_entity", modulus=1)
        assert offset == 0

    def test_phase_offset_large_modulus(self):
        """Phase offset works with large modulus."""
        calc = OrbitCalculator()
        offset = calc.get_phase_offset("test", modulus=1000)
        assert 0 <= offset < 1000


# =============================================================================
# should_dance Tests
# =============================================================================


class TestShouldDance:
    """Test OrbitCalculator.should_dance method."""

    def test_should_dance_returns_bool(self):
        """should_dance returns boolean."""
        calc = OrbitCalculator()
        result = calc.should_dance(0, "test_entity")
        assert isinstance(result, bool)

    def test_should_dance_deterministic(self):
        """should_dance is deterministic for same inputs."""
        calc = OrbitCalculator()
        entity_id = "my_entity"
        tick = 10
        result1 = calc.should_dance(tick, entity_id)
        result2 = calc.should_dance(tick, entity_id)
        assert result1 == result2

    def test_should_dance_fires_at_offset(self):
        """Entity dances when tick mod modulus equals offset."""
        calc = OrbitCalculator()
        entity_id = "test_entity"
        offset = calc.get_phase_offset(entity_id)

        # At tick == offset, should dance
        result = calc.should_dance(offset, entity_id)
        assert result is True

    def test_should_dance_not_at_other_ticks(self):
        """Entity doesn't dance at non-offset ticks."""
        calc = OrbitCalculator()
        entity_id = "test_entity"
        offset = calc.get_phase_offset(entity_id)

        # Try ticks that are NOT the offset
        for tick in range(16):
            if tick != offset:
                result = calc.should_dance(tick, entity_id)
                assert result is False, f"Should not dance at tick {tick} (offset={offset})"

    def test_should_dance_cycles(self):
        """Entity dances at offset + modulus ticks."""
        calc = OrbitCalculator()
        entity_id = "cycle_test"
        offset = calc.get_phase_offset(entity_id)

        # Should dance at offset, offset+16, offset+32, ...
        for cycle in range(5):
            tick = offset + (cycle * 16)
            result = calc.should_dance(tick, entity_id)
            assert result is True, f"Should dance at tick {tick}"

    def test_should_dance_custom_kaksha_modulus(self):
        """should_dance respects kaksha_modulus."""
        calc = OrbitCalculator()
        entity_id = "custom_kaksha"
        offset = calc.get_phase_offset(entity_id, modulus=8)

        # With modulus 8, should dance at offset, offset+8, offset+16
        result = calc.should_dance(offset, entity_id, kaksha_modulus=8)
        assert result is True


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


class TestOrbitProtocolCompliance:
    """Test OrbitCalculator protocol compliance."""

    def test_implements_orbit_protocol(self):
        """OrbitCalculator implements OrbitProtocol."""
        from vibe_core.mahamantra.protocols._orbit import OrbitProtocol
        calc = OrbitCalculator()
        assert isinstance(calc, OrbitProtocol)

    def test_has_get_phase_offset(self):
        """OrbitCalculator has get_phase_offset method."""
        calc = OrbitCalculator()
        assert hasattr(calc, "get_phase_offset")
        assert callable(calc.get_phase_offset)

    def test_has_should_dance(self):
        """OrbitCalculator has should_dance method."""
        calc = OrbitCalculator()
        assert hasattr(calc, "should_dance")
        assert callable(calc.should_dance)


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestOrbitEdgeCases:
    """Test edge cases for OrbitCalculator."""

    def test_empty_entity_id(self):
        """Empty entity_id works."""
        calc = OrbitCalculator()
        offset = calc.get_phase_offset("")
        assert 0 <= offset < 16

    def test_unicode_entity_id(self):
        """Unicode entity_id works."""
        calc = OrbitCalculator()
        offset = calc.get_phase_offset("संस्कृत_entity_🕉️")
        assert 0 <= offset < 16

    def test_long_entity_id(self):
        """Long entity_id works."""
        calc = OrbitCalculator()
        long_id = "a" * 10000
        offset = calc.get_phase_offset(long_id)
        assert 0 <= offset < 16

    def test_tick_zero(self):
        """Tick 0 works."""
        calc = OrbitCalculator()
        result = calc.should_dance(0, "entity_at_0")
        assert isinstance(result, bool)

    def test_negative_tick(self):
        """Negative tick works (modulo handles it)."""
        calc = OrbitCalculator()
        result = calc.should_dance(-1, "negative_tick")
        assert isinstance(result, bool)

    def test_large_tick(self):
        """Large tick works."""
        calc = OrbitCalculator()
        result = calc.should_dance(1000000, "large_tick")
        assert isinstance(result, bool)


# =============================================================================
# Module Attributes Tests
# =============================================================================


class TestModuleAttributes:
    """Test module-level attributes."""

    def test_mahajana_declaration(self):
        """Module has __mahajana__ declaration."""
        from vibe_core.mahamantra.substrate import orbit
        assert hasattr(orbit, "__mahajana__")
        assert orbit.__mahajana__ == "prithu"

    def test_position_declaration(self):
        """Module has __position__ declaration."""
        from vibe_core.mahamantra.substrate import orbit
        assert hasattr(orbit, "__position__")
        assert orbit.__position__ == 4

    def test_genesis_declaration(self):
        """Module has __genesis__ declaration."""
        from vibe_core.mahamantra.substrate import orbit
        assert hasattr(orbit, "__genesis__")
        assert orbit.__genesis__.startswith("0x")
