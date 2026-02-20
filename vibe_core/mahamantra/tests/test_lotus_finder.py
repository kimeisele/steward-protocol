"""
Tests for LotusFinder — the import-level Lotus routing.

Verifies that:
1. Normal imports still work (zero overhead when files are in place)
2. Moved files are discoverable via the finder
3. The module map builds correctly from filesystem
4. install/uninstall is idempotent
"""

import importlib
import sys
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Module map tests (no sys.meta_path mutation needed)
# ---------------------------------------------------------------------------

class TestModuleMap:
    """Test the filesystem scanning logic."""

    def test_build_module_map_finds_modules(self):
        """Modules in substrate/ (direct or nested) are in the map."""
        from vibe_core.mahamantra.substrate.lotus_finder import _build_module_map, _SUBSTRATE_ROOT

        module_map = _build_module_map()

        # seed.py exists (may be direct or nested after reorg)
        assert "seed" in module_map
        assert module_map["seed"].name == "seed.py"

        # wiring.py is a direct child
        assert "wiring" in module_map
        assert module_map["wiring"] == _SUBSTRATE_ROOT / "wiring.py"

    def test_build_module_map_finds_subpackages(self):
        """Subpackages (dirs with __init__.py) are in the map."""
        from vibe_core.mahamantra.substrate.lotus_finder import _build_module_map

        module_map = _build_module_map()

        # language/ is a subpackage
        assert "language" in module_map

    def test_build_module_map_skips_private(self):
        """Files starting with _ are not in the map."""
        from vibe_core.mahamantra.substrate.lotus_finder import _build_module_map

        module_map = _build_module_map()

        assert "_legacy" not in module_map
        assert "__init__" not in module_map

    def test_build_module_map_direct_wins_over_nested(self):
        """Direct child takes priority over nested file with same name."""
        from vibe_core.mahamantra.substrate.lotus_finder import _build_module_map, _SUBSTRATE_ROOT

        module_map = _build_module_map()

        # wiring.py exists as a direct child — must resolve to root
        assert module_map["wiring"].parent == _SUBSTRATE_ROOT

    def test_module_map_covers_known_modules(self):
        """Key modules that are heavily imported must be in the map."""
        from vibe_core.mahamantra.substrate.lotus_finder import _build_module_map

        module_map = _build_module_map()

        critical_modules = [
            "seed", "lotus_core", "opcode", "wiring", "pancha_walk",
            "rama_grid", "venu_orchestrator", "mantra_vm", "cell",
            "chamber", "registry", "antaranga", "shuddhi",
        ]
        for name in critical_modules:
            assert name in module_map, f"{name} not found in module map"


# ---------------------------------------------------------------------------
# Install / Uninstall tests
# ---------------------------------------------------------------------------

class TestInstallation:
    """Test sys.meta_path installation."""

    def test_install_is_idempotent(self):
        """Calling install() twice doesn't add two finders."""
        from vibe_core.mahamantra.substrate import lotus_finder as lf

        was_installed = lf.is_installed()

        lf.install()
        lf.install()  # Second call

        # Count how many LotusFinders are in meta_path
        count = sum(1 for f in sys.meta_path if isinstance(f, lf.LotusFinder))
        assert count == 1

        if not was_installed:
            lf.uninstall()

    def test_uninstall_removes_finder(self):
        """uninstall() removes the finder from sys.meta_path."""
        from vibe_core.mahamantra.substrate import lotus_finder as lf

        lf.install()
        assert lf.is_installed()

        lf.uninstall()
        assert not lf.is_installed()

    def test_uninstall_is_idempotent(self):
        """Calling uninstall() when not installed doesn't error."""
        from vibe_core.mahamantra.substrate import lotus_finder as lf

        lf.uninstall()  # Ensure clean state
        lf.uninstall()  # Should not raise


# ---------------------------------------------------------------------------
# Finder resolution tests
# ---------------------------------------------------------------------------

class TestFinderResolution:
    """Test that the finder correctly resolves modules."""

    def test_finder_ignores_non_substrate(self):
        """Finder returns None for non-substrate imports."""
        from vibe_core.mahamantra.substrate.lotus_finder import LotusFinder

        finder = LotusFinder()
        spec = finder.find_spec("vibe_core.services.foo", None)
        assert spec is None

    def test_finder_ignores_deep_paths(self):
        """Finder returns None for deep substrate paths (language.engine)."""
        from vibe_core.mahamantra.substrate.lotus_finder import LotusFinder

        finder = LotusFinder()
        spec = finder.find_spec(
            "vibe_core.mahamantra.substrate.language.engine", None
        )
        assert spec is None

    def test_finder_ignores_already_loaded(self):
        """Finder returns None if module is already in sys.modules."""
        from vibe_core.mahamantra.substrate.lotus_finder import LotusFinder

        finder = LotusFinder()
        # seed is already imported (we imported lotus_finder which triggers substrate)
        # Force it into sys.modules if not already
        import vibe_core.mahamantra.substrate.seed  # noqa: F401

        spec = finder.find_spec(
            "vibe_core.mahamantra.substrate.seed", None
        )
        assert spec is None  # Already loaded, finder defers

    def test_finder_resolves_known_module(self):
        """Finder can resolve a module that exists in the map."""
        from vibe_core.mahamantra.substrate.lotus_finder import LotusFinder

        finder = LotusFinder()

        # Remove seed from sys.modules temporarily to test resolution
        saved = sys.modules.pop("vibe_core.mahamantra.substrate.seed", None)
        try:
            spec = finder.find_spec(
                "vibe_core.mahamantra.substrate.seed", None
            )
            assert spec is not None
            assert "seed" in spec.origin
        finally:
            if saved is not None:
                sys.modules["vibe_core.mahamantra.substrate.seed"] = saved

    def test_finder_returns_none_for_nonexistent(self):
        """Finder returns None for modules that don't exist anywhere."""
        from vibe_core.mahamantra.substrate.lotus_finder import LotusFinder

        finder = LotusFinder()
        spec = finder.find_spec(
            "vibe_core.mahamantra.substrate.does_not_exist_xyz", None
        )
        assert spec is None


# ---------------------------------------------------------------------------
# Integration test: moved file still importable
# ---------------------------------------------------------------------------

class TestMovedFileResolution:
    """
    The critical test: move a file, verify it's still importable.

    This simulates the reorganization scenario:
    substrate/seed.py -> substrate/core/seed.py
    """

    def test_moved_file_is_discoverable_in_map(self, tmp_path):
        """
        If we add a .py file in a subdirectory and it doesn't exist
        at the top level, the module map finds it.
        """
        from vibe_core.mahamantra.substrate.lotus_finder import _SUBSTRATE_ROOT

        # Create a fake substrate tree in tmp
        fake_root = tmp_path / "substrate"
        fake_root.mkdir()
        core_dir = fake_root / "core"
        core_dir.mkdir()

        # Put a module in core/ but NOT in substrate/
        (core_dir / "moved_module.py").write_text("VALUE = 42\n")
        (core_dir / "__init__.py").write_text("")

        # Patch _SUBSTRATE_ROOT to use our fake tree
        import vibe_core.mahamantra.substrate.lotus_finder as lf
        original_root = lf._SUBSTRATE_ROOT

        try:
            lf._SUBSTRATE_ROOT = fake_root
            lf.invalidate_cache()

            module_map = lf._build_module_map()
            assert "moved_module" in module_map
            assert "core" in module_map  # subpackage
        finally:
            lf._SUBSTRATE_ROOT = original_root
            lf.invalidate_cache()


# ---------------------------------------------------------------------------
# Cache invalidation
# ---------------------------------------------------------------------------

class TestCacheInvalidation:
    """Test that invalidate_cache() forces re-scan."""

    def test_invalidate_clears_cache(self):
        from vibe_core.mahamantra.substrate import lotus_finder as lf

        # Build cache
        lf._get_module_map()
        assert lf._MODULE_MAP is not None

        # Invalidate
        lf.invalidate_cache()
        assert lf._MODULE_MAP is None

        # Rebuild
        new_map = lf._get_module_map()
        assert new_map is not None
        assert len(new_map) > 0
