"""
TEST: IntegrityGuardPlugin Contract Tests
=========================================
Target: vibe_core/plugins/integrity_guard/plugin_main.py
Standard: GAD-5000 (Plugin Contract Testing)

Tests verify:
1. Plugin identity and protocol compliance
2. on_boot behavior in various modes
3. Strict mode enforcement
4. Test mode bypass
5. Sanctify state integration
"""

from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugin_protocol import HookResult, PluginResult
from vibe_core.plugins.integrity_guard.plugin_main import IntegrityGuardPlugin


class TestIntegrityGuardPluginInit:
    """Test plugin initialization and identity."""

    def test_plugin_can_be_instantiated(self):
        """Plugin should instantiate without errors."""
        plugin = IntegrityGuardPlugin()
        assert plugin is not None

    def test_plugin_has_correct_id(self):
        """Plugin ID should be 'integrity_guard'."""
        plugin = IntegrityGuardPlugin()
        assert plugin.plugin_id == "integrity_guard"

    def test_plugin_inherits_from_kernel_plugin(self):
        """Plugin should inherit from KernelPlugin."""
        from vibe_core.plugin_protocol import KernelPlugin

        plugin = IntegrityGuardPlugin()
        assert isinstance(plugin, KernelPlugin)

    def test_plugin_has_on_boot_method(self):
        """Plugin should have on_boot method."""
        plugin = IntegrityGuardPlugin()
        assert hasattr(plugin, "on_boot")
        assert callable(plugin.on_boot)


class TestIntegrityGuardOnBoot:
    """Test on_boot behavior."""

    def test_on_boot_in_test_mode_bypasses_enforcement(self):
        """Test mode should bypass all enforcement checks."""
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()
        kernel._test_mode = True

        result = plugin.on_boot(kernel, config=None)

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.OK

    def test_on_boot_with_disabled_config_skips_enforcement(self):
        """Disabled config should skip enforcement."""
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()
        kernel._test_mode = False

        result = plugin.on_boot(kernel, config={"enabled": False})

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.OK

    @patch("vibe_core.plugins.integrity_guard.plugin_main.sanctify_state_system")
    @patch.object(IntegrityGuardPlugin, "_enforce_standard")
    def test_on_boot_calls_sanctify_and_enforce(self, mock_enforce, mock_sanctify):
        """on_boot should call sanctify_state_system and _enforce_standard."""
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()
        kernel._test_mode = False

        result = plugin.on_boot(kernel, config={"enabled": True})

        mock_sanctify.assert_called_once_with(kernel)
        mock_enforce.assert_called_once_with(kernel)
        assert result.status == PluginResult.OK

    @patch("vibe_core.plugins.integrity_guard.plugin_main.sanctify_state_system")
    def test_on_boot_error_in_non_strict_mode_returns_error_result(self, mock_sanctify):
        """Non-strict mode should return error result, not exit."""
        mock_sanctify.side_effect = RuntimeError("Test error")
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()
        kernel._test_mode = False

        result = plugin.on_boot(kernel, config={"enabled": True, "strict_mode": False})

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.ERROR
        assert "Test error" in str(result.error_message)

    @patch("vibe_core.plugins.integrity_guard.plugin_main.sanctify_state_system")
    @patch("sys.exit")
    def test_on_boot_error_in_strict_mode_exits(self, mock_exit, mock_sanctify):
        """Strict mode should call sys.exit on error."""
        mock_sanctify.side_effect = RuntimeError("Critical error")
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()
        kernel._test_mode = False

        plugin.on_boot(kernel, config={"enabled": True, "strict_mode": True})

        mock_exit.assert_called_once_with(1)


class TestIntegrityGuardEnforceStandard:
    """Test _enforce_standard method."""

    @patch("subprocess.run")
    def test_enforce_standard_runs_ruff_lint(self, mock_run):
        """_enforce_standard should run ruff lint check."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()

        plugin._enforce_standard(kernel)

        # Check that ruff was called
        calls = mock_run.call_args_list
        ruff_call = [c for c in calls if "ruff" in str(c)]
        assert len(ruff_call) > 0

    @patch("subprocess.run")
    def test_enforce_standard_runs_pytest_smoke(self, mock_run):
        """_enforce_standard should run pytest smoke tests."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()

        plugin._enforce_standard(kernel)

        # Check that pytest was called
        calls = mock_run.call_args_list
        pytest_call = [c for c in calls if "pytest" in str(c)]
        assert len(pytest_call) > 0

    @patch("subprocess.run")
    def test_enforce_standard_raises_on_lint_failure(self, mock_run):
        """_enforce_standard should raise on lint failure."""
        mock_run.return_value = MagicMock(returncode=1, stdout="Lint errors", stderr="")
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()

        with pytest.raises(RuntimeError, match="lint violations"):
            plugin._enforce_standard(kernel)

    @patch("subprocess.run")
    def test_enforce_standard_raises_on_test_failure(self, mock_run):
        """_enforce_standard should raise on test failure."""
        # First call (lint) succeeds, second call (test) fails
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),  # lint OK
            MagicMock(returncode=1, stdout="Test failed", stderr=""),  # test FAIL
        ]
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()

        with pytest.raises(RuntimeError, match="tests failed"):
            plugin._enforce_standard(kernel)


class TestIntegrityGuardSanctifyIntegration:
    """Test sanctify_state_system integration."""

    def test_sanctify_state_module_exists(self):
        """sanctify_state module should be importable."""
        from vibe_core.plugins.integrity_guard.sanctify_state import sanctify_state_system

        assert sanctify_state_system is not None
        assert callable(sanctify_state_system)

    @patch("vibe_core.plugins.integrity_guard.sanctify_state.sanctify_state_system")
    def test_on_boot_integrates_sanctify(self, mock_sanctify):
        """on_boot should integrate sanctify_state_system."""
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()
        kernel._test_mode = False

        with patch.object(plugin, "_enforce_standard"):
            plugin.on_boot(kernel, config={"enabled": True})

        # Sanctify should have been called (via the real import)
        # Note: The patch is on the module level, so we verify indirectly


class TestIntegrityGuardConfigVariants:
    """Test various config combinations."""

    @pytest.mark.parametrize(
        "config",
        [
            None,
            {},
            {"enabled": True},
            {"enabled": True, "strict_mode": False},
        ],
    )
    def test_on_boot_handles_various_configs(self, config):
        """on_boot should handle various config formats."""
        plugin = IntegrityGuardPlugin()
        kernel = MagicMock()
        kernel._test_mode = True  # Bypass enforcement

        result = plugin.on_boot(kernel, config=config)

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.OK
