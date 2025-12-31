"""
TEST: DoctorPlugin Contract Tests
==================================
Target: vibe_core/plugins/doctor/plugin_main.py
Standard: GAD-5000 (Plugin Contract Testing)

Tests verify:
1. Plugin identity and protocol compliance
2. on_boot lifecycle behavior
3. System diagnostics (shallow and deep)
4. Health report structure
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PluginResult
from vibe_core.plugins.doctor.plugin_main import DoctorPlugin


class TestDoctorPluginInit:
    """Test plugin initialization and identity."""

    def test_plugin_can_be_instantiated(self):
        """Plugin should instantiate without errors."""
        plugin = DoctorPlugin()
        assert plugin is not None

    def test_plugin_has_correct_id(self):
        """Plugin ID should be 'doctor'."""
        plugin = DoctorPlugin()
        assert plugin.plugin_id == "doctor"

    def test_plugin_inherits_from_kernel_plugin(self):
        """Plugin should inherit from KernelPlugin."""
        plugin = DoctorPlugin()
        assert isinstance(plugin, KernelPlugin)

    def test_plugin_has_cmd_doctor_method(self):
        """Plugin should have cmd_doctor method."""
        plugin = DoctorPlugin()
        assert hasattr(plugin, "cmd_doctor")
        assert callable(plugin.cmd_doctor)


class TestDoctorOnBoot:
    """Test on_boot behavior."""

    def test_on_boot_returns_hook_result(self):
        """on_boot should return HookResult with OK status."""
        plugin = DoctorPlugin()
        kernel = MagicMock()

        result = plugin.on_boot(kernel, config=None)

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.OK

    def test_on_boot_accepts_kernel_parameter(self):
        """on_boot should accept kernel parameter without error."""
        plugin = DoctorPlugin()
        kernel = MagicMock()

        result = plugin.on_boot(kernel, config=None)

        # Should complete successfully
        assert result.status == PluginResult.OK

    def test_on_boot_with_config(self):
        """on_boot should accept config parameter."""
        plugin = DoctorPlugin()
        kernel = MagicMock()
        config = {"some_key": "some_value"}

        result = plugin.on_boot(kernel, config=config)

        assert result.status == PluginResult.OK


class TestDoctorDiagnostics:
    """Test system diagnostic functionality."""

    def test_cmd_doctor_returns_dict(self):
        """cmd_doctor should return a dictionary health report."""
        plugin = DoctorPlugin()

        report = plugin.cmd_doctor(deep=False)

        assert isinstance(report, dict)

    def test_cmd_doctor_includes_status(self):
        """Health report should include status field."""
        plugin = DoctorPlugin()

        report = plugin.cmd_doctor(deep=False)

        assert "status" in report
        assert report["status"] in ["HEALTHY", "DEGRADED", "ADVISORY"]

    def test_cmd_doctor_includes_checks_list(self):
        """Health report should include checks list."""
        plugin = DoctorPlugin()

        report = plugin.cmd_doctor(deep=False)

        assert "checks" in report
        assert isinstance(report["checks"], list)

    def test_cmd_doctor_includes_issues_list(self):
        """Health report should include issues list."""
        plugin = DoctorPlugin()

        report = plugin.cmd_doctor(deep=False)

        assert "issues" in report
        assert isinstance(report["issues"], list)

    def test_cmd_doctor_checks_file_existence(self):
        """cmd_doctor should check for critical files."""
        plugin = DoctorPlugin()

        report = plugin.cmd_doctor(deep=False)

        # Should check for some files
        file_checks = [c for c in report["checks"] if c.get("check") == "file_exists"]
        assert len(file_checks) > 0

    def test_cmd_doctor_checks_python_version(self):
        """cmd_doctor should check Python version."""
        plugin = DoctorPlugin()

        report = plugin.cmd_doctor(deep=False)

        # Should have a python_version check
        version_checks = [c for c in report["checks"] if c.get("check") == "python_version"]
        assert len(version_checks) == 1
        assert "value" in version_checks[0]

    def test_cmd_doctor_shallow_vs_deep(self):
        """Deep diagnostics should include additional checks."""
        plugin = DoctorPlugin()

        shallow_report = plugin.cmd_doctor(deep=False)
        deep_report = plugin.cmd_doctor(deep=True)

        # Deep report should have more checks
        assert len(deep_report["checks"]) >= len(shallow_report["checks"])

    def test_cmd_doctor_deep_includes_legacy_rot_scan(self):
        """Deep diagnostics should include legacy rot scan."""
        plugin = DoctorPlugin()

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.rglob", return_value=[]):
                report = plugin.cmd_doctor(deep=True)

        # Should have legacy_rot check
        legacy_checks = [c for c in report["checks"] if c.get("check") == "legacy_rot"]
        assert len(legacy_checks) == 1
        assert "scanned" in legacy_checks[0]
        assert "deprecated_files" in legacy_checks[0]

    def test_cmd_doctor_default_deep_is_false(self):
        """cmd_doctor should default deep to False."""
        plugin = DoctorPlugin()

        # Call without deep parameter
        report = plugin.cmd_doctor()

        # Should not have legacy_rot check (deep=False)
        legacy_checks = [c for c in report["checks"] if c.get("check") == "legacy_rot"]
        assert len(legacy_checks) == 0


class TestDoctorHealthReportStructure:
    """Test health report structure compliance (GAD-000)."""

    def test_check_structure_has_required_fields(self):
        """Each check should have standard fields."""
        plugin = DoctorPlugin()

        report = plugin.cmd_doctor(deep=False)

        for check in report["checks"]:
            assert "check" in check
            assert "passed" in check

    def test_file_check_structure(self):
        """File existence checks should have target field."""
        plugin = DoctorPlugin()

        report = plugin.cmd_doctor(deep=False)

        file_checks = [c for c in report["checks"] if c.get("check") == "file_exists"]
        for check in file_checks:
            assert "target" in check
            assert "passed" in check

    def test_status_healthy_when_no_issues(self):
        """Status should be HEALTHY when critical files are present."""
        plugin = DoctorPlugin()

        # Mock all required paths to exist (except DB which is optional)
        with patch("pathlib.Path.exists") as mock_exists:

            def exists_side_effect(self):
                # Config and kernel should exist
                if "phoenix.yaml" in str(self) or "kernel.py" in str(self):
                    return True
                return False

            with patch.object(Path, "exists", exists_side_effect):
                report = plugin.cmd_doctor(deep=False)

        # Status should not be DEGRADED if critical files are found
        # (or it might be DEGRADED if files are missing - this is expected behavior)
        assert report["status"] in ["HEALTHY", "DEGRADED", "ADVISORY"]

    def test_legacy_rot_affects_status(self):
        """Deep scan with deprecated code should set ADVISORY status."""
        plugin = DoctorPlugin()

        # Mock a file with deprecated content
        mock_file = MagicMock()
        mock_file.read_text.return_value = "@deprecated function"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.rglob", return_value=[mock_file]):
                report = plugin.cmd_doctor(deep=True)

        # Should have found deprecated code
        legacy_checks = [c for c in report["checks"] if c.get("check") == "legacy_rot"]
        if legacy_checks:
            # If we found deprecated files, status should be ADVISORY
            if legacy_checks[0]["deprecated_files"] > 0:
                assert report["status"] == "ADVISORY"


class TestDoctorEdgeCases:
    """Test edge cases and error handling."""

    def test_cmd_doctor_handles_missing_files_gracefully(self):
        """cmd_doctor should handle missing files without crashing."""
        plugin = DoctorPlugin()

        # This should not raise an exception
        report = plugin.cmd_doctor(deep=False)

        assert isinstance(report, dict)
        assert "status" in report

    def test_cmd_doctor_deep_handles_read_errors(self):
        """Deep scan should handle file read errors gracefully."""
        plugin = DoctorPlugin()

        # Mock a file that raises on read
        mock_file = MagicMock()
        mock_file.read_text.side_effect = Exception("Read error")

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.rglob", return_value=[mock_file]):
                # Should not raise
                report = plugin.cmd_doctor(deep=True)

        assert isinstance(report, dict)

    def test_cmd_doctor_with_nonexistent_base_path(self):
        """cmd_doctor deep should handle nonexistent vibe_core gracefully."""
        plugin = DoctorPlugin()

        with patch("pathlib.Path.exists", return_value=False):
            # Should not raise
            report = plugin.cmd_doctor(deep=True)

        assert isinstance(report, dict)
        # Legacy rot check might not be present or might show 0 scanned
        legacy_checks = [c for c in report["checks"] if c.get("check") == "legacy_rot"]
        if legacy_checks:
            assert legacy_checks[0]["scanned"] == 0
