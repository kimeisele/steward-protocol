"""
Tests for Phoenix Paths Configuration.

OPUS-025: PATH LOBOTOMY CRISIS - Tests verifying path configuration works correctly.

Tests:
- PathsConfig section is discovered
- Template variable resolution via resolve()
- XDG environment variable override (ADR-025a)
- Tool vs Project scope separation (ADR-025b)
- No hardcoded paths leak through

@HARNESS: This file is required by docs/architecture/OPUS/025-PATH-LOBOTOMY-CRISIS.md
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from vibe_core.phoenix import get_config, reset_config
from vibe_core.phoenix.sections.paths.section_main import (
    ProjectPathsConfig,
    ToolPathsConfig,
)


@pytest.fixture(scope="module")
def phoenix_config():
    """Get PhoenixConfig ONCE per module."""
    reset_config()
    config = get_config()
    return config


class TestPathsSectionDiscovery:
    """Test that paths section is properly discovered and loaded."""

    def test_paths_section_exists(self, phoenix_config):
        """Paths section is discovered from config/paths.yaml."""
        assert hasattr(phoenix_config, "paths")
        assert phoenix_config.paths is not None

    def test_data_paths_exist(self, phoenix_config):
        """Data paths subsection exists."""
        assert hasattr(phoenix_config.paths, "data")

    def test_system_paths_exist(self, phoenix_config):
        """System paths subsection exists."""
        assert hasattr(phoenix_config.paths, "system")

    def test_cartridges_paths_exist(self, phoenix_config):
        """Cartridges paths subsection exists."""
        assert hasattr(phoenix_config.paths, "cartridges")


class TestResolveMethod:
    """Test that resolve() method works for template variables."""

    def test_data_resolve_economy_db(self, phoenix_config):
        """resolve('economy_db') returns path under data root."""
        path = phoenix_config.paths.data.resolve("economy_db")
        assert isinstance(path, Path)
        assert "economy" in str(path)

    def test_data_resolve_vibe_ledger(self, phoenix_config):
        """resolve('vibe_ledger') returns path for ledger database."""
        path = phoenix_config.paths.data.resolve("vibe_ledger")
        assert isinstance(path, Path)
        assert "ledger" in str(path).lower() or "vibe" in str(path).lower()

    def test_system_resolve_lineage_db(self, phoenix_config):
        """resolve('lineage_db') returns path for lineage database."""
        path = phoenix_config.paths.system.resolve("lineage_db")
        assert isinstance(path, Path)
        assert "lineage" in str(path)


class TestToolPathsXDG:
    """Test XDG environment variable compliance (ADR-025a)."""

    def test_tool_paths_config_defaults(self):
        """ToolPathsConfig has XDG-compliant defaults."""
        config = ToolPathsConfig()
        assert "~/.config/steward" in config.config_root
        assert "~/.local/share/steward" in config.data_root
        assert "~/.cache/steward" in config.cache_root

    def test_xdg_config_home_override(self):
        """XDG_CONFIG_HOME overrides config_root."""
        config = ToolPathsConfig()
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            path = config.resolve("keys")
            assert str(path).startswith("/custom/config/steward")

    def test_xdg_data_home_override(self):
        """XDG_DATA_HOME overrides data_root."""
        config = ToolPathsConfig()
        with patch.dict(os.environ, {"XDG_DATA_HOME": "/custom/data"}):
            path = config.resolve("lib")
            assert str(path).startswith("/custom/data/steward")

    def test_xdg_cache_home_override(self):
        """XDG_CACHE_HOME overrides cache_root."""
        config = ToolPathsConfig()
        with patch.dict(os.environ, {"XDG_CACHE_HOME": "/custom/cache"}):
            path = config.resolve("cache_root")
            assert str(path).startswith("/custom/cache/steward")


class TestProjectPathsScope:
    """Test project scope separation (ADR-025b)."""

    def test_project_paths_config_defaults(self):
        """ProjectPathsConfig has .vibe/ defaults."""
        config = ProjectPathsConfig()
        assert config.vibe_root == ".vibe"
        assert "{vibe_root}" in config.state_db

    def test_project_resolve_state_db(self):
        """resolve('state_db') returns .vibe/vibe.db path."""
        config = ProjectPathsConfig()
        path = config.resolve("state_db")
        assert ".vibe" in str(path)
        assert "vibe.db" in str(path)

    def test_project_resolve_runtime(self):
        """resolve('runtime') returns .vibe/runtime path."""
        config = ProjectPathsConfig()
        path = config.resolve("runtime")
        assert ".vibe" in str(path)
        assert "runtime" in str(path)


class TestNoHardcodedPaths:
    """Verify no hardcoded paths leak into config."""

    def test_no_tmp_vibe_os_in_defaults(self):
        """No /tmp/vibe_os in default project paths."""
        config = ProjectPathsConfig()
        all_values = [
            config.vibe_root,
            config.state_db,
            config.runtime,
            config.sandboxes,
            config.logs,
        ]
        for val in all_values:
            assert "/tmp/vibe_os" not in val

    def test_no_home_vibe_in_project(self):
        """No ~/.vibe in project paths (use .vibe/ instead)."""
        config = ProjectPathsConfig()
        all_values = [
            config.vibe_root,
            config.state_db,
            config.runtime,
        ]
        for val in all_values:
            assert "~/.vibe" not in val
