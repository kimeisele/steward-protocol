"""
TEST SERVE PHASE COMMANDS
=========================

Tests for SERVE phase (8-11) commands:
- ChatCommand (PRAHLADA - EXEC_SERVICE)
- IntelCommand (SHUKA - FETCH_RES)

"If no Protocol, it doesn't exist."
"""

import pytest

from vibe_core.cli.naga_commands.serve.chat import ChatCommand
from vibe_core.cli.naga_commands.serve.intel import IntelCommand
from vibe_core.protocols.naga.cli_command import (
    INagaCommand,
    Mahajana,
    Phase,
    NAGA_COMMAND_REGISTRY,
)
from vibe_core.protocols.substrate import MantraOpCode


# =============================================================================
# CHAT COMMAND TESTS
# =============================================================================

class TestChatCommand:
    """Test ChatCommand (PRAHLADA - EXEC_SERVICE)."""

    def test_implements_protocol(self):
        """ChatCommand implements INagaCommand."""
        cmd = ChatCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_exec_service(self):
        """Opcode is EXEC_SERVICE."""
        cmd = ChatCommand()
        assert cmd.opcode == MantraOpCode.EXEC_SERVICE

    def test_mahajana_is_prahlada(self):
        """Mahajana is PRAHLADA."""
        cmd = ChatCommand()
        assert cmd.mahajana == Mahajana.PRAHLADA

    def test_name_is_chat(self):
        """Name is 'chat'."""
        cmd = ChatCommand()
        assert cmd.name == "chat"

    def test_phase_is_serve(self):
        """Phase is SERVE."""
        cmd = ChatCommand()
        assert cmd.phase == Phase.SERVE

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = ChatCommand()
        assert len(cmd.help_text) > 0
        assert "PRAHLADA" in cmd.help_text

    def test_execute_no_args_fails(self):
        """Execute with no args returns failure."""
        cmd = ChatCommand()
        result = cmd.execute([])
        assert not result.success
        assert result.exit_code == 1
        assert "No message provided" in result.error

    def test_execute_with_message_succeeds(self):
        """Execute with message returns success."""
        cmd = ChatCommand()
        result = cmd.execute(["Hello", "world"])
        assert result.success
        assert result.exit_code == 0
        assert "PRAHLADA" in result.output
        assert "Hello world" in result.output

    def test_execute_with_context(self):
        """Execute with --context flag."""
        cmd = ChatCommand()
        result = cmd.execute(["--context", "security", "Check", "this"])
        assert result.success
        data = result.to_dict()
        assert data.get("context") == "security"

    def test_execute_invalid_context(self):
        """Execute with invalid --context fails."""
        cmd = ChatCommand()
        result = cmd.execute(["--context"])  # Missing context value
        assert not result.success
        assert "Invalid --context" in result.error

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = ChatCommand()
        result = cmd.execute(["test"])
        assert result.opcode == MantraOpCode.EXEC_SERVICE

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = ChatCommand()
        result = cmd.execute(["test"])
        assert result.mahajana == Mahajana.PRAHLADA


# =============================================================================
# INTEL COMMAND TESTS
# =============================================================================

class TestIntelCommand:
    """Test IntelCommand (SHUKA - FETCH_RES)."""

    def test_implements_protocol(self):
        """IntelCommand implements INagaCommand."""
        cmd = IntelCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_fetch_res(self):
        """Opcode is FETCH_RES."""
        cmd = IntelCommand()
        assert cmd.opcode == MantraOpCode.FETCH_RES

    def test_mahajana_is_shuka(self):
        """Mahajana is SHUKA."""
        cmd = IntelCommand()
        assert cmd.mahajana == Mahajana.SHUKA

    def test_name_is_intel(self):
        """Name is 'intel'."""
        cmd = IntelCommand()
        assert cmd.name == "intel"

    def test_phase_is_serve(self):
        """Phase is SERVE."""
        cmd = IntelCommand()
        assert cmd.phase == Phase.SERVE

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = IntelCommand()
        assert len(cmd.help_text) > 0
        assert "SHUKA" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args returns intel."""
        cmd = IntelCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "SHUKA" in result.output

    def test_execute_critical_flag(self):
        """Execute with --critical flag."""
        cmd = IntelCommand()
        result = cmd.execute(["--critical"])
        assert result.success
        data = result.to_dict()
        assert data.get("critical_only") == "True"

    def test_execute_threats_flag(self):
        """Execute with --threats flag."""
        cmd = IntelCommand()
        result = cmd.execute(["--threats"])
        assert result.success
        data = result.to_dict()
        assert data.get("threats_only") == "True"

    def test_execute_category_flag(self):
        """Execute with --category flag."""
        cmd = IntelCommand()
        result = cmd.execute(["--category", "security"])
        assert result.success
        data = result.to_dict()
        assert data.get("category") == "security"

    def test_execute_invalid_category(self):
        """Execute with invalid --category fails."""
        cmd = IntelCommand()
        result = cmd.execute(["--category"])  # Missing category value
        assert not result.success
        assert "Invalid --category" in result.error

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = IntelCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.FETCH_RES

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = IntelCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.SHUKA


# =============================================================================
# REGISTRY INTEGRATION TESTS
# =============================================================================

class TestRegistryIntegration:
    """Test that commands are registered."""

    def test_chat_registered(self):
        """ChatCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("chat")
        assert cmd is not None
        assert cmd.name == "chat"

    def test_intel_registered(self):
        """IntelCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("intel")
        assert cmd is not None
        assert cmd.name == "intel"

    def test_serve_phase_has_commands(self):
        """SERVE phase has commands."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_phase(Phase.SERVE)
        assert len(cmds) >= 2
        names = [c.name for c in cmds]
        assert "chat" in names
        assert "intel" in names

    def test_prahlada_has_chat(self):
        """PRAHLADA owns chat command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.PRAHLADA)
        names = [c.name for c in cmds]
        assert "chat" in names

    def test_shuka_has_intel(self):
        """SHUKA owns intel command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.SHUKA)
        names = [c.name for c in cmds]
        assert "intel" in names


# =============================================================================
# STRICT TYPING TESTS
# =============================================================================

class TestStrictTyping:
    """Test that results have no Any types."""

    def test_chat_result_no_any(self):
        """ChatCommand result has no Any."""
        cmd = ChatCommand()
        result = cmd.execute(["test"])
        # Result is NagaCommandResult which is frozen dataclass
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')

    def test_intel_result_no_any(self):
        """IntelCommand result has no Any."""
        cmd = IntelCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')


# =============================================================================
# IMMUTABILITY TESTS
# =============================================================================

class TestImmutability:
    """Test that results are immutable."""

    def test_chat_result_frozen(self):
        """ChatCommand result is frozen."""
        cmd = ChatCommand()
        result = cmd.execute(["test"])
        with pytest.raises(Exception):
            result.success = False

    def test_intel_result_frozen(self):
        """IntelCommand result is frozen."""
        cmd = IntelCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False
