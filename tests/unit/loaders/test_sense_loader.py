"""
Tests for SenseLoader - OPUS-099.

Verifies VEDA-4 auto-discovery pattern for MANAS cortex senses.
"""

from pathlib import Path

import pytest

from vibe_core.loaders import SenseLoader, SenseLoadError


class TestSenseLoaderDiscovery:
    """Test auto-discovery of senses."""

    def setup_method(self):
        """Clear cache before each test."""
        SenseLoader.clear_cache()

    def test_discover_all_senses(self):
        """Verify all 8 Jnanendriyas (senses) are discovered."""
        senses, metadata = SenseLoader.discover_and_load(
            workspace=Path.cwd(),
            strict=True,
        )

        # Must have exactly 10 senses (OPUS-305: +ArchitectureSense, +NadiSense)
        assert len(senses) == 10, f"Expected 10 senses, got {len(senses)}"

        # Verify all 10 Jnanendriyas exist
        expected_names = {
            "prakriti_sense",  # System state perception
            "dharma_sense",  # Ethical alignment
            "sutra_sense",  # Documentation gaps
            "shruta_sense",  # Filesystem events
            "prana_sense",  # Agent lifecycle
            "karma_sense",  # Historical patterns
            "viveka_sense",  # Coverage discrimination
            "akasha_sense",  # Knowledge graph perception (OPUS-155)
            "architecture_sense",  # Architecture understanding (OPUS-305)
            "nadi_sense",  # Flow/channel perception (OPUS-305)
        }
        actual_names = set(senses.keys())
        assert actual_names == expected_names, f"Missing senses: {expected_names - actual_names}"

    def test_metadata_populated(self):
        """Verify metadata includes class name and file path."""
        senses, metadata = SenseLoader.discover_and_load(workspace=Path.cwd())

        for name, meta in metadata.items():
            assert "class" in meta, f"Missing 'class' in metadata for {name}"
            assert "file" in meta, f"Missing 'file' in metadata for {name}"
            assert "enabled" in meta, f"Missing 'enabled' in metadata for {name}"

    def test_senses_have_name_property(self):
        """Verify all discovered senses have a name property."""
        senses, _ = SenseLoader.discover_and_load(workspace=Path.cwd())

        for name, sense in senses.items():
            assert hasattr(sense, "name"), f"Sense {name} missing 'name' property"
            assert sense.name == name, f"Sense name mismatch: {sense.name} != {name}"

    def test_senses_have_perceive_method(self):
        """Verify all discovered senses have a perceive method."""
        senses, _ = SenseLoader.discover_and_load(workspace=Path.cwd())

        for name, sense in senses.items():
            assert hasattr(sense, "perceive"), f"Sense {name} missing 'perceive' method"
            assert callable(sense.perceive), f"Sense {name}.perceive is not callable"


class TestSenseLoaderCaching:
    """Test caching behavior."""

    def setup_method(self):
        """Clear cache before each test."""
        SenseLoader.clear_cache()

    def test_caching_enabled(self):
        """Verify second call returns cached results."""
        # First call
        senses1, _ = SenseLoader.discover_and_load(workspace=Path.cwd())

        # Second call should return same objects (cached)
        senses2, _ = SenseLoader.discover_and_load(workspace=Path.cwd())

        # Same dict instance (cached)
        assert senses1 is senses2

    def test_force_refresh_bypasses_cache(self):
        """Verify force_refresh creates new instances."""
        # First call
        senses1, _ = SenseLoader.discover_and_load(workspace=Path.cwd())

        # Force refresh
        senses2, _ = SenseLoader.discover_and_load(
            workspace=Path.cwd(),
            force_refresh=True,
        )

        # Different dict instance (not cached)
        assert senses1 is not senses2

    def test_clear_cache_works(self):
        """Verify clear_cache resets the cache."""
        # First call
        senses1, _ = SenseLoader.discover_and_load(workspace=Path.cwd())

        # Clear cache
        SenseLoader.clear_cache()

        # Second call should create new instances
        senses2, _ = SenseLoader.discover_and_load(workspace=Path.cwd())

        # Different dict instance (cache was cleared)
        assert senses1 is not senses2


class TestSenseLoaderStrictMode:
    """Test STRICT MODE behavior."""

    def setup_method(self):
        """Clear cache before each test."""
        SenseLoader.clear_cache()

    def test_strict_mode_enabled_by_default(self):
        """Verify strict_mode is True by default."""
        assert SenseLoader.strict_mode is True

    def test_strict_mode_can_be_disabled(self):
        """Verify strict mode can be disabled per-call."""
        # This should not raise even if there were broken senses
        # (in this case there aren't, but we verify the flag works)
        senses, _ = SenseLoader.discover_and_load(
            workspace=Path.cwd(),
            strict=False,
        )
        assert len(senses) == 10  # OPUS-305: 10 Jnanendriyas (+Architecture, +Nadi)


class TestSenseLoaderUtilities:
    """Test utility methods."""

    def setup_method(self):
        """Clear cache before each test."""
        SenseLoader.clear_cache()

    def test_list_senses(self):
        """Test list_senses utility method."""
        names = SenseLoader.list_senses(workspace=Path.cwd())
        assert isinstance(names, list)
        assert len(names) == 10  # OPUS-305: 10 Jnanendriyas (+Architecture, +Nadi)

    def test_get_sense(self):
        """Test get_sense utility method."""
        sense = SenseLoader.get_sense("prakriti_sense", workspace=Path.cwd())
        assert sense is not None
        assert sense.name == "prakriti_sense"

    def test_get_sense_nonexistent(self):
        """Test get_sense returns None for unknown sense."""
        sense = SenseLoader.get_sense("nonexistent", workspace=Path.cwd())
        assert sense is None
