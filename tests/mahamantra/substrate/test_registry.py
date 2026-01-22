"""
TESTS: registry.py - Guardian Registry Dynamic Dispatch
========================================================

"yato vā imāni bhūtāni jāyante"

REAL TESTS for:
1. GuardianRegistry class
2. Dynamic module loading
3. Position-based type resolution
4. Cache management
"""

import pytest
from vibe_core.mahamantra.substrate.registry import (
    GuardianRegistry,
    load_type_from_position,
)


# =============================================================================
# GuardianRegistry.get_position Tests
# =============================================================================


class TestGuardianRegistryGetPosition:
    """Test GuardianRegistry.get_position method."""

    def test_get_position_0(self):
        """Position 0 returns MantraPosition."""
        pos = GuardianRegistry.get_position(0)
        assert pos is not None
        assert pos.index == 0

    def test_get_position_15(self):
        """Position 15 returns MantraPosition."""
        pos = GuardianRegistry.get_position(15)
        assert pos is not None
        assert pos.index == 15

    def test_get_position_invalid_negative(self):
        """Negative position returns None."""
        pos = GuardianRegistry.get_position(-1)
        assert pos is None

    def test_get_position_invalid_16(self):
        """Position 16 returns None (out of bounds)."""
        pos = GuardianRegistry.get_position(16)
        assert pos is None

    def test_all_16_positions_exist(self):
        """All 16 positions (0-15) exist."""
        for i in range(16):
            pos = GuardianRegistry.get_position(i)
            assert pos is not None, f"Position {i} should exist"


# =============================================================================
# GuardianRegistry.get_guardian_name Tests
# =============================================================================


class TestGuardianRegistryGetGuardianName:
    """Test GuardianRegistry.get_guardian_name method."""

    def test_guardian_name_position_0(self):
        """Position 0 has guardian name."""
        name = GuardianRegistry.get_guardian_name(0)
        assert name is not None
        assert isinstance(name, str)
        assert len(name) > 0

    def test_guardian_name_all_positions(self):
        """All 16 positions have guardian names."""
        for i in range(16):
            name = GuardianRegistry.get_guardian_name(i)
            assert name is not None, f"Position {i} should have guardian"
            assert isinstance(name, str)

    def test_guardian_name_invalid(self):
        """Invalid position returns None."""
        name = GuardianRegistry.get_guardian_name(100)
        assert name is None

    def test_guardian_names_are_lowercase(self):
        """Guardian names are lowercase."""
        for i in range(16):
            name = GuardianRegistry.get_guardian_name(i)
            assert name == name.lower()


# =============================================================================
# GuardianRegistry.get_all_guardians Tests
# =============================================================================


class TestGuardianRegistryGetAllGuardians:
    """Test GuardianRegistry.get_all_guardians method."""

    def test_get_all_guardians_returns_16(self):
        """get_all_guardians returns 16 guardians."""
        guardians = GuardianRegistry.get_all_guardians()
        assert len(guardians) == 16

    def test_get_all_guardians_is_list(self):
        """get_all_guardians returns a list."""
        guardians = GuardianRegistry.get_all_guardians()
        assert isinstance(guardians, list)

    def test_get_all_guardians_are_strings(self):
        """All guardians are strings."""
        guardians = GuardianRegistry.get_all_guardians()
        for g in guardians:
            assert isinstance(g, str)

    def test_get_all_guardians_are_unique(self):
        """All guardian names are unique."""
        guardians = GuardianRegistry.get_all_guardians()
        assert len(guardians) == len(set(guardians))


# =============================================================================
# GuardianRegistry._get_module_path Tests
# =============================================================================


class TestGuardianRegistryModulePath:
    """Test GuardianRegistry._get_module_path method."""

    def test_module_path_format(self):
        """Module path has correct format."""
        path = GuardianRegistry._get_module_path(0, "types")
        assert path is not None
        assert "vibe_core.protocols.mahajanas" in path
        assert ".types" in path

    def test_module_path_invalid_index(self):
        """Invalid index returns None."""
        path = GuardianRegistry._get_module_path(100, "types")
        assert path is None

    def test_module_path_different_components(self):
        """Different components produce different paths."""
        path_types = GuardianRegistry._get_module_path(0, "types")
        path_service = GuardianRegistry._get_module_path(0, "service")
        assert path_types != path_service


# =============================================================================
# GuardianRegistry.load_module Tests
# =============================================================================


class TestGuardianRegistryLoadModule:
    """Test GuardianRegistry.load_module method."""

    def test_load_module_nonexistent(self):
        """Non-existent module returns None."""
        # Clear cache first
        GuardianRegistry.clear_cache()
        module = GuardianRegistry.load_module(0, "nonexistent_component_xyz")
        assert module is None

    def test_load_module_invalid_index(self):
        """Invalid index returns None."""
        module = GuardianRegistry.load_module(100, "types")
        assert module is None


# =============================================================================
# GuardianRegistry.load_type Tests
# =============================================================================


class TestGuardianRegistryLoadType:
    """Test GuardianRegistry.load_type method."""

    def test_load_type_nonexistent(self):
        """Non-existent type returns None."""
        GuardianRegistry.clear_cache()
        type_class = GuardianRegistry.load_type(0, "NonExistentType123")
        assert type_class is None

    def test_load_type_invalid_position(self):
        """Invalid position returns None."""
        type_class = GuardianRegistry.load_type(100, "BootMode")
        assert type_class is None


# =============================================================================
# GuardianRegistry.clear_cache Tests
# =============================================================================


class TestGuardianRegistryClearCache:
    """Test GuardianRegistry.clear_cache method."""

    def test_clear_cache_runs(self):
        """clear_cache runs without error."""
        GuardianRegistry.clear_cache()
        assert True  # No exception

    def test_clear_cache_empties_caches(self):
        """clear_cache empties the internal caches."""
        GuardianRegistry.clear_cache()
        assert len(GuardianRegistry._module_cache) == 0
        assert len(GuardianRegistry._type_cache) == 0


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestLoadTypeFromPosition:
    """Test load_type_from_position convenience function."""

    def test_load_type_from_position_nonexistent(self):
        """Non-existent type returns None."""
        type_class = load_type_from_position(0, "NonExistentType789")
        assert type_class is None

    def test_load_type_from_position_invalid(self):
        """Invalid position returns None."""
        type_class = load_type_from_position(100, "SomeType")
        assert type_class is None


# =============================================================================
# Module-Level Attributes Tests
# =============================================================================


class TestModuleAttributes:
    """Test module-level attributes."""

    def test_mahajana_declaration(self):
        """Module has __mahajana__ declaration."""
        from vibe_core.mahamantra.substrate import registry
        assert hasattr(registry, "__mahajana__")
        assert registry.__mahajana__ == "prithu"

    def test_position_declaration(self):
        """Module has __position__ declaration."""
        from vibe_core.mahamantra.substrate import registry
        assert hasattr(registry, "__position__")
        assert registry.__position__ == 4

    def test_genesis_declaration(self):
        """Module has __genesis__ declaration."""
        from vibe_core.mahamantra.substrate import registry
        assert hasattr(registry, "__genesis__")
        assert registry.__genesis__.startswith("0x")


# =============================================================================
# Integration Tests
# =============================================================================


class TestGuardianRegistryIntegration:
    """Integration tests for GuardianRegistry."""

    def test_position_guardian_consistency(self):
        """Position index matches guardian at that position."""
        for i in range(16):
            pos = GuardianRegistry.get_position(i)
            name = GuardianRegistry.get_guardian_name(i)
            assert pos is not None
            assert pos.guardian.value == name

    def test_all_guardians_match_positions(self):
        """All guardians from get_all_guardians match get_guardian_name."""
        guardians = GuardianRegistry.get_all_guardians()
        for i, guardian in enumerate(guardians):
            name = GuardianRegistry.get_guardian_name(i)
            assert guardian == name
