"""
Tests for the Fractal CLI System.

Tests:
- Command discovery from plugin manifests
- CLI argument parsing
- GAD-000 compliant output (JSON, YAML, human)
- Execution modes (OFFLINE, BOOT)
"""

from vibe_core.cli import CLICommand, CLILoader, CLIResponse, ExecutionMode


class TestCLILoader:
    """Test command discovery from manifests."""

    def test_discover_commands(self):
        """Should discover CLI commands from plugin manifests."""
        commands = CLILoader.discover_commands(force_refresh=True)

        # Should find test_orchestration commands
        assert "test:run" in commands
        assert "test:summary" in commands
        assert "test:pytest" in commands
        assert "test:guardian" in commands

    def test_command_has_plugin_id(self):
        """Commands should have plugin_id for import resolution."""
        commands = CLILoader.discover_commands()

        cmd = commands["test:summary"]
        assert cmd.plugin_id == "test_orchestration"
        assert cmd.namespace == "test"

    def test_command_has_handler(self):
        """Commands should have handler method name."""
        commands = CLILoader.discover_commands()

        cmd = commands["test:summary"]
        assert cmd.handler == "cmd_summary"

    def test_command_has_execution_mode(self):
        """Commands should have execution mode."""
        commands = CLILoader.discover_commands()

        cmd = commands["test:summary"]
        assert cmd.execution_mode == ExecutionMode.BOOT

    def test_command_args_parsed(self):
        """Command arguments should be parsed from manifest."""
        commands = CLILoader.discover_commands()

        cmd = commands["test:run"]
        assert len(cmd.args) > 0

        # Find target arg
        target_arg = next((a for a in cmd.args if a.name == "target"), None)
        assert target_arg is not None
        assert target_arg.default == "all"
        assert target_arg.required is False


class TestCLIResponse:
    """Test GAD-000 compliant response handling."""

    def test_response_to_dict(self):
        """Response should serialize to dict."""
        response = CLIResponse(
            success=True,
            data={"key": "value"},
            execution_mode=ExecutionMode.OFFLINE,
        )

        result = response.to_dict()
        assert result["success"] is True
        assert result["data"] == {"key": "value"}
        assert result["execution_mode"] == "offline"

    def test_response_with_error(self):
        """Response should include error when present."""
        response = CLIResponse(
            success=False,
            data=None,
            error="Something went wrong",
            execution_mode=ExecutionMode.BOOT,
        )

        result = response.to_dict()
        assert result["success"] is False
        assert result["error"] == "Something went wrong"


class TestCLICommand:
    """Test CLICommand dataclass."""

    def test_full_name_with_namespace(self):
        """full_name should include namespace."""
        cmd = CLICommand(name="run", namespace="test")
        assert cmd.full_name == "test:run"

    def test_full_name_without_namespace(self):
        """full_name should be just name without namespace."""
        cmd = CLICommand(name="boot")
        assert cmd.full_name == "boot"

    def test_to_argparse_name(self):
        """argparse name should replace : with -."""
        cmd = CLICommand(name="run", namespace="test")
        assert cmd.to_argparse_name() == "test-run"
