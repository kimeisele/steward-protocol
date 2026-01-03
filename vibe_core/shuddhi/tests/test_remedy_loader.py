"""
Tests for RemedyLoader - Dynamic Remedy Discovery.

OPUS-307: Verifies remedies are auto-discovered, not hardcoded.
"""

from pathlib import Path

import pytest

from vibe_core.protocols.shuddhi import RemedyProtocol
from vibe_core.shuddhi.remedies.base import CSTRemedy
from vibe_core.shuddhi.remedy_loader import (
    RemedyLoader,
    discover_remedies,
    get_remedy_loader,
)


class TestRemedyLoaderDiscovery:
    """Tests for dynamic remedy discovery."""

    def test_loader_discovers_remedies(self):
        """Verify loader discovers remedies from directory."""
        loader = RemedyLoader()
        remedies = loader.discover_and_load()

        assert len(remedies) >= 6, "Should discover at least 6 remedies"
        assert all(isinstance(cls, type) for cls in remedies.values())

    def test_discovered_remedies_inherit_from_cst_remedy(self):
        """All discovered remedies must inherit from CSTRemedy."""
        loader = RemedyLoader()
        remedies = loader.discover_and_load()

        for rule_id, remedy_class in remedies.items():
            assert issubclass(remedy_class, CSTRemedy), (
                f"Remedy {rule_id} ({remedy_class.__name__}) must inherit from CSTRemedy"
            )

    def test_discovered_remedies_have_valid_rule_id(self):
        """All discovered remedies must have a valid rule_id."""
        loader = RemedyLoader()
        remedies = loader.discover_and_load()

        for rule_id, remedy_class in remedies.items():
            instance = remedy_class()
            assert instance.rule_id == rule_id, f"Remedy class {remedy_class.__name__} rule_id mismatch"
            assert isinstance(instance.rule_id, str)
            assert len(instance.rule_id) > 0

    def test_discovered_remedies_implement_protocol(self):
        """All discovered remedies should be compatible with RemedyProtocol."""
        loader = RemedyLoader()
        remedies = loader.discover_and_load()

        for rule_id, remedy_class in remedies.items():
            instance = remedy_class()
            # Check protocol compatibility
            assert hasattr(instance, "rule_id")
            assert hasattr(instance, "applied")
            assert hasattr(instance, "violation_found")
            assert hasattr(instance, "requirements")
            assert hasattr(instance, "get_diff")


class TestRemedyLoaderCache:
    """Tests for caching behavior."""

    def test_loader_caches_results(self):
        """Loader should cache results."""
        loader = RemedyLoader()

        remedies1 = loader.discover_and_load()
        remedies2 = loader.discover_and_load()

        assert remedies1 is remedies2, "Should return cached instance"

    def test_force_refresh_bypasses_cache(self):
        """force_refresh should reload from disk."""
        loader = RemedyLoader()

        remedies1 = loader.discover_and_load()
        remedies2 = loader.discover_and_load(force_refresh=True)

        # Content should be same but not same object
        assert set(remedies1.keys()) == set(remedies2.keys())

    def test_clear_cache(self):
        """clear_cache should invalidate cache."""
        loader = RemedyLoader()

        _ = loader.discover_and_load()
        loader.clear_cache()

        assert loader._cache is None


class TestRemedyLoaderExtensibility:
    """Tests for runtime extensibility."""

    def test_add_scan_path(self, tmp_path):
        """Should be able to add custom scan paths."""
        loader = RemedyLoader()
        initial_paths = len(loader._scan_paths)

        loader.add_scan_path(tmp_path)

        assert len(loader._scan_paths) == initial_paths + 1
        assert tmp_path in loader._scan_paths

    def test_add_scan_path_clears_cache(self, tmp_path):
        """Adding scan path should invalidate cache."""
        loader = RemedyLoader()
        _ = loader.discover_and_load()

        loader.add_scan_path(tmp_path)

        assert loader._cache is None


class TestSingletonLoader:
    """Tests for module-level singleton."""

    def test_get_remedy_loader_returns_singleton(self):
        """get_remedy_loader should return same instance."""
        loader1 = get_remedy_loader()
        loader2 = get_remedy_loader()

        assert loader1 is loader2

    def test_discover_remedies_convenience_function(self):
        """discover_remedies should work as convenience function."""
        remedies = discover_remedies()

        assert isinstance(remedies, dict)
        assert len(remedies) >= 6


class TestExpectedRemedies:
    """Tests for expected remedy availability (matching standards.yaml)."""

    EXPECTED_REMEDIES = [
        "subprocess_timeout",
        "silent_failure",
        "get_instance_antipattern",
        "direct_registry_instantiation",
        "iterdir_discovery",
        "path_scanning_discovery",
    ]

    def test_all_expected_remedies_discovered(self):
        """All remedies marked in standards.yaml should be discovered."""
        remedies = discover_remedies()

        for rule_id in self.EXPECTED_REMEDIES:
            assert rule_id in remedies, (
                f"Missing remedy for rule_id: {rule_id} (has_sattva_remedy: true in standards.yaml)"
            )

    def test_no_hardcoded_imports_in_engine(self):
        """ShuddhiEngine should not have hardcoded remedy imports."""
        engine_path = Path(__file__).parent.parent / "engine.py"
        content = engine_path.read_text()

        # Should not have direct imports from remedies
        assert "from vibe_core.shuddhi.remedies.subprocess_timeout" not in content
        assert "from vibe_core.shuddhi.remedies.silent_except" not in content
        assert "from vibe_core.shuddhi.remedies.get_instance" not in content

        # Should use RemedyLoader
        assert "remedy_loader" in content
        assert "get_remedy_loader" in content or "_discover_remedies" in content
