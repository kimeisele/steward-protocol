"""
Tests for OPUS CLI Commands (Phase 3).

Tests the "Remote Control" functionality:
- steward opus:status → State of Mind
- steward opus:log → Journal entries
- steward opus:verify → Manual verification
"""

import json
import tempfile
from pathlib import Path

# =============================================================================
# CLI Commands Module Tests
# =============================================================================


class TestCLICommandsModule:
    """Test cli/commands.py module."""

    def test_module_importable(self):
        """CLI commands module should be importable."""
        from vibe_core.plugins.opus_assistant.cli import commands

        assert commands is not None

    def test_format_functions_exist(self):
        """All format functions should exist."""
        from vibe_core.plugins.opus_assistant.cli.commands import (
            build_cli_response,
            format_log_output,
            format_status_output,
            format_verify_output,
            parse_journal_from_opus,
        )

        assert callable(format_status_output)
        assert callable(format_log_output)
        assert callable(format_verify_output)
        assert callable(parse_journal_from_opus)
        assert callable(build_cli_response)


class TestFormatStatusOutput:
    """Test status formatting."""

    def test_format_none_context(self):
        """Should handle None context gracefully."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_status_output

        result = format_status_output(None)

        assert result["success"] is False
        assert "error" in result
        assert result["status_icon"] == "🔴"

    def test_format_healthy_context(self):
        """Should format healthy context with green icon."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_status_output

        context = {
            "health": {
                "status": "HEALTHY",
                "overall": 1.0,
                "opus_exists": True,
                "harness_valid": True,
                "kernel_active": True,
            },
            "drift": {"has_drift": False},
            "context_hash": "abc123def456",
        }

        result = format_status_output(context)

        assert result["success"] is True
        assert result["status_icon"] == "🟢"
        assert result["status"] == "HEALTHY"
        assert "100%" in result["health_score"]

    def test_format_degraded_context(self):
        """Should format degraded context with yellow icon."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_status_output

        context = {
            "health": {
                "status": "DEGRADED",
                "overall": 0.6,
            },
            "drift": {"has_drift": True, "files": ["file1.py", "file2.py"]},
            "context_hash": "xyz789",
        }

        result = format_status_output(context)

        assert result["success"] is True
        assert result["status_icon"] == "🟡"
        assert result["drift_detected"] is True
        assert "drift_summary" in result

    def test_format_json_mode(self):
        """JSON mode should return raw context."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_status_output

        context = {"health": {"status": "HEALTHY"}, "drift": {"has_drift": False}}

        result = format_status_output(context, json_mode=True)

        assert result["success"] is True
        assert result["data"] == context


class TestFormatLogOutput:
    """Test log formatting."""

    def test_format_empty_log(self):
        """Should handle empty observations."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_log_output

        result = format_log_output([])

        assert result["success"] is True
        assert "No observations" in result["message"]

    def test_format_observations(self):
        """Should format observations with icons."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_log_output

        observations = [
            {"timestamp": "2025-01-01T12:00:00", "severity": "WARN", "source": "test", "message": "Test warning"},
            {"timestamp": "2025-01-01T12:01:00", "severity": "INFO", "source": "test", "message": "Test info"},
        ]

        result = format_log_output(observations)

        assert result["success"] is True
        assert len(result["observations"]) == 2
        assert result["observations"][0]["icon"] == "⚠️"
        assert result["observations"][1]["icon"] == "ℹ️"

    def test_format_with_limit(self):
        """Should respect limit parameter."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_log_output

        observations = [
            {"timestamp": f"2025-01-01T12:0{i}:00", "severity": "INFO", "source": "test", "message": f"Msg {i}"}
            for i in range(10)
        ]

        result = format_log_output(observations, limit=5)

        assert result["showing"] == 5
        assert result["total"] == 10
        assert len(result["observations"]) == 5

    def test_format_json_mode(self):
        """JSON mode should return raw observations."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_log_output

        observations = [
            {"timestamp": "2025-01-01T12:00:00", "severity": "INFO", "source": "test", "message": "Test"},
        ]

        result = format_log_output(observations, json_mode=True)

        assert result["success"] is True
        assert result["data"] == observations


class TestFormatVerifyOutput:
    """Test verification formatting."""

    def test_format_passed_verification(self):
        """Should format passed verification with green icon."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_verify_output

        verification = {
            "passed": True,
            "checks": [
                {"name": "check1", "passed": True},
                {"name": "check2", "passed": True},
            ],
            "harness": {"files": ["a.py", "b.py"], "rules": ["rule1"]},
        }

        result = format_verify_output(verification)

        assert result["success"] is True
        assert result["status_icon"] == "🟢"
        assert result["passed"] is True
        assert result["stats"]["passed"] == 2

    def test_format_failed_verification(self):
        """Should format failed verification with failures list."""
        from vibe_core.plugins.opus_assistant.cli.commands import format_verify_output

        verification = {
            "passed": False,
            "checks": [
                {"name": "check1", "passed": True},
                {"name": "check2", "passed": False, "reason": "File missing"},
            ],
        }

        result = format_verify_output(verification)

        assert result["success"] is True
        assert result["status_icon"] == "🔴"
        assert result["passed"] is False
        assert len(result["failures"]) == 1
        assert result["failures"][0]["reason"] == "File missing"


class TestParseJournalFromOpus:
    """Test journal parsing from OPUS.md."""

    def test_parse_empty_file(self):
        """Should return empty list for non-existent file."""
        from vibe_core.plugins.opus_assistant.cli.commands import parse_journal_from_opus

        result = parse_journal_from_opus(Path("/nonexistent/OPUS.md"))

        assert result == []

    def test_parse_journal_section(self):
        """Should parse observations from journal section."""
        from vibe_core.plugins.opus_assistant.cli.commands import parse_journal_from_opus

        opus_content = """# OPUS.md

## 🧠 System Observations

<!-- @JOURNAL START -->
- `2025-01-01T12:00:00` ⚠️ **[drift_detector]** Drift detected in config.py
- `2025-01-01T12:01:00` ℹ️ **[kernel_tick]** Tick #5 processed
<!-- @JOURNAL END -->
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(opus_content)
            f.flush()
            opus_path = Path(f.name)

        try:
            result = parse_journal_from_opus(opus_path)

            assert len(result) == 2
            assert result[0]["severity"] == "WARN"
            assert result[0]["source"] == "drift_detector"
            assert "Drift detected" in result[0]["message"]
            assert result[1]["severity"] == "INFO"
        finally:
            opus_path.unlink()

    def test_parse_empty_journal(self):
        """Should handle empty journal."""
        from vibe_core.plugins.opus_assistant.cli.commands import parse_journal_from_opus

        opus_content = """# OPUS.md

## 🧠 System Observations

<!-- @JOURNAL START -->
_No observations yet._
<!-- @JOURNAL END -->
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(opus_content)
            f.flush()
            opus_path = Path(f.name)

        try:
            result = parse_journal_from_opus(opus_path)
            assert result == []
        finally:
            opus_path.unlink()


class TestBuildCliResponse:
    """Test CLI response building."""

    def test_build_json_response(self):
        """Should build valid JSON in json mode."""
        from vibe_core.plugins.opus_assistant.cli.commands import build_cli_response

        data = {"success": True, "status": "HEALTHY"}

        result = build_cli_response(data, json_mode=True)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["success"] is True

    def test_build_human_response(self):
        """Should build human-readable response."""
        from vibe_core.plugins.opus_assistant.cli.commands import build_cli_response

        data = {
            "success": True,
            "summary": "🟢 System Status: HEALTHY (100% health)",
            "context_hash": "abc123",
        }

        result = build_cli_response(data, json_mode=False)

        assert isinstance(result, str)
        assert "🟢" in result
        assert "HEALTHY" in result
        assert "abc123" in result


# =============================================================================
# Plugin Handler Tests
# =============================================================================


class TestPluginCLIHandlers:
    """Test CLI handlers on OpusAssistantPlugin."""

    def test_cmd_opus_status_exists(self):
        """cmd_opus_status handler should exist."""
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        assert hasattr(plugin, "cmd_opus_status")
        assert callable(plugin.cmd_opus_status)

    def test_cmd_opus_log_exists(self):
        """cmd_opus_log handler should exist."""
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        assert hasattr(plugin, "cmd_opus_log")
        assert callable(plugin.cmd_opus_log)

    def test_cmd_opus_verify_exists(self):
        """cmd_opus_verify handler should exist."""
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        assert hasattr(plugin, "cmd_opus_verify")
        assert callable(plugin.cmd_opus_verify)

    def test_cmd_opus_status_without_kernel(self):
        """Status should handle no kernel gracefully."""
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        result = plugin.cmd_opus_status()

        # Without kernel boot, context will be None
        assert "success" in result

    def test_cmd_opus_log_no_opus_file(self):
        """Log should handle missing OPUS.md."""
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        plugin._workspace = Path("/nonexistent")

        result = plugin.cmd_opus_log()

        assert result["success"] is True
        # Should return empty/message about no observations

    def test_cmd_opus_verify_returns_formatted(self):
        """Verify should return formatted results."""
        from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        plugin._workspace = Path(".")

        result = plugin.cmd_opus_verify(quick=True)

        assert "success" in result
        # Should have status icon and stats


# =============================================================================
# Manifest CLI Registration Tests
# =============================================================================


class TestManifestCLIRegistration:
    """Test CLI registration in manifest.json."""

    def test_manifest_has_cli_section(self):
        """Manifest should have cli section."""
        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text())
        assert "cli" in manifest

    def test_manifest_cli_namespace(self):
        """CLI should have 'opus' namespace."""
        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        assert manifest["cli"]["namespace"] == "opus"

    def test_manifest_has_status_command(self):
        """Manifest should define status command."""
        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        commands = {c["name"]: c for c in manifest["cli"]["commands"]}
        assert "status" in commands
        assert commands["status"]["handler"] == "cmd_opus_status"

    def test_manifest_has_log_command(self):
        """Manifest should define log command."""
        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        commands = {c["name"]: c for c in manifest["cli"]["commands"]}
        assert "log" in commands
        assert commands["log"]["handler"] == "cmd_opus_log"

    def test_manifest_has_verify_command(self):
        """Manifest should define verify command."""
        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        commands = {c["name"]: c for c in manifest["cli"]["commands"]}
        assert "verify" in commands
        assert commands["verify"]["handler"] == "cmd_opus_verify"

    def test_all_commands_have_json_arg(self):
        """All commands should support --json flag."""
        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        for cmd in manifest["cli"]["commands"]:
            arg_names = [a["name"] for a in cmd.get("args", [])]
            assert "json" in arg_names, f"Command {cmd['name']} missing --json arg"


# =============================================================================
# CLI Discovery Integration Tests
# =============================================================================


class TestCLILoaderDiscovery:
    """Test that CLI commands are discoverable by CLILoader."""

    def test_cli_loader_discovers_opus_commands(self):
        """CLILoader should find opus: namespace commands."""
        from vibe_core.cli.loader import CLILoader

        # Force refresh to pick up new manifest
        CLILoader.clear_cache()
        commands = CLILoader.discover_commands(force_refresh=True)

        # Find opus: namespaced commands
        opus_commands = [name for name in commands.keys() if name.startswith("opus:")]

        assert len(opus_commands) >= 3
        assert "opus:status" in commands
        assert "opus:log" in commands
        assert "opus:verify" in commands

    def test_opus_namespace_registered(self):
        """'opus' should be a registered namespace."""
        from vibe_core.cli.loader import CLILoader

        CLILoader.clear_cache()
        namespaces = CLILoader.get_namespaces()

        assert "opus" in namespaces
