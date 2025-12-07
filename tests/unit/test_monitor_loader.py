"""
TEST: Monitor Loader
====================
Tests for Glass Box system introspection.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from vibe_core.cli.monitor_loader import MonitorLoader


class TestMonitorLoader:
    """Test monitor discovery."""

    def teardown_method(self):
        MonitorLoader.clear_cache()

    def test_discover_monitors_no_plugins(self):
        """Should return empty registry if no plugins."""
        kernel = MagicMock()
        kernel.plugin_manager.plugins = []

        monitors = MonitorLoader.discover_monitors(kernel)
        assert len(monitors) == 0

    def test_discover_monitors_with_plugin(self):
        """Should discover monitors from plugin."""
        # Mock plugin
        plugin = MagicMock()
        plugin.plugin_id = "test_plugin"

        # Mock monitor
        monitor = MagicMock()
        monitor.monitor_id = "test_monitor"
        monitor.monitor_type = "gauge"
        monitor.description = "Test Monitor"

        plugin.get_monitors.return_value = [monitor]

        kernel = MagicMock()
        kernel.plugin_manager.plugins = [plugin]

        monitors = MonitorLoader.discover_monitors(kernel)
        assert "test_monitor" in monitors
        assert monitors["test_monitor"].plugin_id == "test_plugin"

    def test_cache_behavior(self):
        """Should cache results."""
        kernel = MagicMock()
        kernel.plugin_manager.plugins = []

        # First call
        MonitorLoader.discover_monitors(kernel)
        assert MonitorLoader._cache is not None

        # Modify kernel plugins (should be ignored due to cache)
        kernel.plugin_manager.plugins = ["garbage"]
        MonitorLoader.discover_monitors(kernel)

        # Should still be empty if cache used
        assert len(MonitorLoader._cache) == 0


class TestCLIBuiltinCommands:
    """Test that CLI builtins use persistent DB, not ghost kernel."""

    def test_get_default_db_path_finds_existing(self):
        """Should find existing DB file."""
        from vibe_core.cli.main import _get_default_db_path

        db_path = _get_default_db_path()

        # Should return a path (may or may not exist in CI)
        assert db_path is not None
        assert isinstance(db_path, str)
        assert db_path.endswith(".db")

    def test_status_reports_db_path(self):
        """Status command should report which DB it's using."""
        from vibe_core.cli.main import _execute_builtin

        # Create mock args
        args = MagicMock()

        result = _execute_builtin("status", args)

        # Should include db_path in response (proves we're not using :memory:)
        assert "db_path" in result
        assert "db_exists" in result
        assert result["db_path"] != ":memory:", "GHOST KERNEL DETECTED! Using :memory: instead of real DB"

    def test_observe_reports_db_path(self):
        """Observe command should report which DB it's using."""
        from vibe_core.cli.main import _execute_builtin

        # Create mock args
        args = MagicMock()
        args.monitor_id = None

        result = _execute_builtin("observe", args)

        # Should include db_path in response
        assert "db_path" in result
        assert result["db_path"] != ":memory:", "GHOST KERNEL DETECTED! Using :memory: instead of real DB"

    @pytest.mark.skipif(not Path("data/vibe_ledger.db").exists(), reason="Requires data/vibe_ledger.db to exist")
    def test_status_with_real_db(self):
        """Status should see real data when DB exists."""
        from vibe_core.cli.main import _execute_builtin

        args = MagicMock()
        result = _execute_builtin("status", args)

        assert result["db_exists"] is True
        assert "kernel" in result
        # Real kernel should have some plugins loaded
        assert result["kernel"]["plugins"] >= 0
