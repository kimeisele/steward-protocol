"""
TEST: LifecyclePlugin Contract Tests
====================================
Target: vibe_core/plugins/lifecycle/plugin_main.py
Standard: GAD-5000 (Plugin Contract Testing)

Tests verify:
1. Plugin identity and protocol compliance
2. on_boot / on_shutdown lifecycle
3. get_capabilities (GAD-000)
4. Constitution hash calculation
5. Spawn log tracking
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.plugins.lifecycle.plugin_main import LifecyclePlugin


class TestLifecyclePluginInit:
    """Test plugin initialization and identity."""

    def test_plugin_can_be_instantiated(self):
        """Plugin should instantiate without errors."""
        plugin = LifecyclePlugin()
        assert plugin is not None

    def test_plugin_has_correct_id(self):
        """Plugin ID should be 'lifecycle'."""
        plugin = LifecyclePlugin()
        assert plugin.plugin_id == "lifecycle"

    def test_plugin_has_priority(self):
        """Plugin should have priority 10."""
        plugin = LifecyclePlugin()
        assert plugin.priority == 10

    def test_plugin_inherits_from_kernel_plugin(self):
        """Plugin should inherit from KernelPlugin."""
        plugin = LifecyclePlugin()
        assert isinstance(plugin, KernelPlugin)

    def test_plugin_starts_with_empty_spawn_log(self):
        """Plugin should start with empty spawn log."""
        plugin = LifecyclePlugin()
        assert plugin._spawn_log == []

    def test_plugin_starts_without_kernel(self):
        """Plugin should start without kernel reference."""
        plugin = LifecyclePlugin()
        assert plugin._kernel is None


class TestLifecycleOnBoot:
    """Test on_boot behavior."""

    def test_on_boot_stores_kernel_reference(self, tmp_path):
        """on_boot should store kernel reference."""
        plugin = LifecyclePlugin()
        kernel = MagicMock()

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        assert plugin._kernel is kernel

    def test_on_boot_registers_plugin_on_kernel(self, tmp_path):
        """on_boot should register plugin as kernel.lifecycle."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])  # No lifecycle attribute initially

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        assert kernel.lifecycle is plugin

    def test_on_boot_creates_sandbox_directory(self, tmp_path):
        """on_boot should create sandbox directory."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        sandbox = tmp_path / "workspaces" / "sandbox"
        assert sandbox.exists()

    def test_on_boot_calculates_constitution_hash(self, tmp_path):
        """on_boot should calculate constitution hash."""
        # Create a constitution file
        constitution = tmp_path / "CONSTITUTION.md"
        constitution.write_text("Test Constitution")

        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        assert plugin._constitution_hash is not None
        assert len(plugin._constitution_hash) == 64  # SHA256 hex length


class TestLifecycleOnShutdown:
    """Test on_shutdown behavior."""

    def test_on_shutdown_logs_spawn_count(self, tmp_path):
        """on_shutdown should log spawn count."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        # Add some spawn log entries
        plugin._spawn_log = [{"agent": "test1"}, {"agent": "test2"}]

        # Should not raise
        plugin.on_shutdown(kernel)


class TestLifecycleGetCapabilities:
    """Test get_capabilities (GAD-000 compliance)."""

    def test_get_capabilities_returns_dict(self, tmp_path):
        """get_capabilities should return dict."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        caps = plugin.get_capabilities()
        assert isinstance(caps, dict)

    def test_get_capabilities_includes_version(self, tmp_path):
        """get_capabilities should include version."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        caps = plugin.get_capabilities()
        assert "version" in caps
        assert caps["version"] == "1.0.0"

    def test_get_capabilities_includes_operations(self, tmp_path):
        """get_capabilities should include operations list."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        caps = plugin.get_capabilities()
        assert "operations" in caps
        assert "spawn_agent" in caps["operations"]
        assert "verify_audit" in caps["operations"]

    def test_get_capabilities_includes_gates(self, tmp_path):
        """get_capabilities should include 5 gates."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        caps = plugin.get_capabilities()
        assert "gates" in caps
        assert len(caps["gates"]) == 5
        assert "constitution" in caps["gates"]
        assert "auditor" in caps["gates"]

    def test_get_capabilities_includes_spawned_count(self, tmp_path):
        """get_capabilities should include spawned_count."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        plugin._spawn_log = [{"agent": "test"}]
        caps = plugin.get_capabilities()
        assert caps["spawned_count"] == 1


class TestLifecycleConstitutionHash:
    """Test constitution hash management."""

    def test_constitution_hash_property(self, tmp_path):
        """constitution_hash property should return hash."""
        constitution = tmp_path / "CONSTITUTION.md"
        constitution.write_text("We the People")

        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        assert plugin.constitution_hash is not None
        assert plugin.constitution_hash != "not_initialized"

    def test_constitution_hash_before_boot(self):
        """constitution_hash should return 'not_initialized' before boot."""
        plugin = LifecyclePlugin()
        assert plugin.constitution_hash == "not_initialized"

    def test_constitution_hash_without_file(self, tmp_path):
        """Missing constitution should use fallback hash."""
        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        assert plugin.constitution_hash == "no_constitution_found"

    def test_constitution_hash_is_sha256(self, tmp_path):
        """Constitution hash should be valid SHA256."""
        import hashlib

        constitution = tmp_path / "CONSTITUTION.md"
        content = "Test Constitution Content"
        constitution.write_text(content)

        expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        plugin = LifecyclePlugin()
        kernel = MagicMock(spec=[])

        with patch.object(plugin, "_register_syscalls"):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                plugin.on_boot(kernel)

        assert plugin.constitution_hash == expected_hash
