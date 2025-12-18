"""
Tests for AnalyzerLoader - OPUS-098.

Verifies VEDA-4 auto-discovery pattern for MANAS analyzers.
"""

from pathlib import Path

import pytest

from vibe_core.loaders import AnalyzerLoader, AnalyzerLoadError


class TestAnalyzerLoaderDiscovery:
    """Test auto-discovery of analyzers."""

    def setup_method(self):
        """Clear cache before each test."""
        AnalyzerLoader.clear_cache()

    def test_discover_all_analyzers(self):
        """Verify all 5 core analyzers are discovered."""
        analyzers, metadata = AnalyzerLoader.discover_and_load(
            workspace=Path.cwd(),
            strict=True,
        )

        # Must have exactly 5 analyzers
        assert len(analyzers) == 5, f"Expected 5 analyzers, got {len(analyzers)}"

        # Verify expected analyzers exist
        expected_names = {
            "ci_monitor",
            "contract_analyzer",
            "doc_harness_analyzer",
            "pratyaya",
            "semantic_analyzer",
        }
        actual_names = set(analyzers.keys())
        assert actual_names == expected_names, f"Missing analyzers: {expected_names - actual_names}"

    def test_metadata_populated(self):
        """Verify metadata includes class name and file path."""
        analyzers, metadata = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        for name, meta in metadata.items():
            assert "class" in meta, f"Missing 'class' in metadata for {name}"
            assert "file" in meta, f"Missing 'file' in metadata for {name}"
            assert "enabled" in meta, f"Missing 'enabled' in metadata for {name}"

    def test_analyzers_have_name_property(self):
        """Verify all discovered analyzers have a name property."""
        analyzers, _ = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        for name, analyzer in analyzers.items():
            assert hasattr(analyzer, "name"), f"Analyzer {name} missing 'name' property"
            assert analyzer.name == name, f"Analyzer name mismatch: {analyzer.name} != {name}"

    def test_analyzers_have_analyze_method(self):
        """Verify all discovered analyzers have an analyze method."""
        analyzers, _ = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        for name, analyzer in analyzers.items():
            assert hasattr(analyzer, "analyze"), f"Analyzer {name} missing 'analyze' method"
            assert callable(analyzer.analyze), f"Analyzer {name}.analyze is not callable"


class TestAnalyzerLoaderCaching:
    """Test caching behavior."""

    def setup_method(self):
        """Clear cache before each test."""
        AnalyzerLoader.clear_cache()

    def test_caching_enabled(self):
        """Verify second call returns cached results."""
        # First call
        analyzers1, _ = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        # Second call should return same objects (cached)
        analyzers2, _ = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        # Same dict instance (cached)
        assert analyzers1 is analyzers2

    def test_force_refresh_bypasses_cache(self):
        """Verify force_refresh creates new instances."""
        # First call
        analyzers1, _ = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        # Force refresh
        analyzers2, _ = AnalyzerLoader.discover_and_load(
            workspace=Path.cwd(),
            force_refresh=True,
        )

        # Different dict instance (not cached)
        assert analyzers1 is not analyzers2

    def test_clear_cache_works(self):
        """Verify clear_cache resets the cache."""
        # First call
        analyzers1, _ = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        # Clear cache
        AnalyzerLoader.clear_cache()

        # Second call should create new instances
        analyzers2, _ = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        # Different dict instance (cache was cleared)
        assert analyzers1 is not analyzers2


class TestAnalyzerLoaderStrictMode:
    """Test STRICT MODE behavior."""

    def setup_method(self):
        """Clear cache before each test."""
        AnalyzerLoader.clear_cache()

    def test_strict_mode_enabled_by_default(self):
        """Verify strict_mode is True by default."""
        assert AnalyzerLoader.strict_mode is True

    def test_strict_mode_can_be_disabled(self):
        """Verify strict mode can be disabled per-call."""
        # This should not raise even if there were broken analyzers
        # (in this case there aren't, but we verify the flag works)
        analyzers, _ = AnalyzerLoader.discover_and_load(
            workspace=Path.cwd(),
            strict=False,
        )
        assert len(analyzers) == 5


class TestAnalyzerLoaderUtilities:
    """Test utility methods."""

    def setup_method(self):
        """Clear cache before each test."""
        AnalyzerLoader.clear_cache()

    def test_list_analyzers(self):
        """Test list_analyzers utility method."""
        names = AnalyzerLoader.list_analyzers(workspace=Path.cwd())
        assert isinstance(names, list)
        assert len(names) == 5

    def test_get_analyzer(self):
        """Test get_analyzer utility method."""
        analyzer = AnalyzerLoader.get_analyzer("ci_monitor", workspace=Path.cwd())
        assert analyzer is not None
        assert analyzer.name == "ci_monitor"

    def test_get_analyzer_nonexistent(self):
        """Test get_analyzer returns None for unknown analyzer."""
        analyzer = AnalyzerLoader.get_analyzer("nonexistent", workspace=Path.cwd())
        assert analyzer is None
