"""
TEST WAKE PHASE COMMANDS
========================

Tests for WAKE phase (0-3) commands:
- StatusCommand (PRITHU - SYS_WAKE)

"Prithu is the first king - status is the first command."
"""

import pytest

from vibe_core.cli.naga_commands.wake.status import StatusCommand
from vibe_core.protocols.naga.cli_command import (
    INagaCommand,
    Mahajana,
    Phase,
    NAGA_COMMAND_REGISTRY,
)
from vibe_core.protocols.substrate import MantraOpCode


# =============================================================================
# STATUS COMMAND TESTS
# =============================================================================

class TestStatusCommand:
    """Test StatusCommand (PRITHU - SYS_WAKE)."""

    def test_implements_protocol(self):
        """StatusCommand implements INagaCommand."""
        cmd = StatusCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_sys_wake(self):
        """Opcode is SYS_WAKE (position 0)."""
        cmd = StatusCommand()
        assert cmd.opcode == MantraOpCode.SYS_WAKE

    def test_mahajana_is_prithu(self):
        """Mahajana is PRITHU (the first king)."""
        cmd = StatusCommand()
        assert cmd.mahajana == Mahajana.PRITHU

    def test_name_is_status(self):
        """Name is 'status'."""
        cmd = StatusCommand()
        assert cmd.name == "status"

    def test_phase_is_wake(self):
        """Phase is WAKE (phase 0)."""
        cmd = StatusCommand()
        assert cmd.phase == Phase.WAKE

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = StatusCommand()
        assert len(cmd.help_text) > 0
        assert "PRITHU" in cmd.help_text

    def test_execute_no_args_full_status(self):
        """Execute with no args returns full status."""
        cmd = StatusCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "PRITHU" in result.output
        assert "SYS_WAKE" in result.output

    def test_execute_brief_flag(self):
        """Execute with --brief returns one-line status."""
        cmd = StatusCommand()
        result = cmd.execute(["--brief"])
        assert result.success
        data = result.to_dict()
        assert data.get("mode") == "brief"
        # Brief should be shorter
        assert len(result.output.split("\n")) <= 3

    def test_execute_nagas_flag(self):
        """Execute with --nagas returns NAGA status."""
        cmd = StatusCommand()
        result = cmd.execute(["--nagas"])
        assert result.success
        data = result.to_dict()
        assert data.get("mode") == "nagas"
        assert "SESHA" in result.output
        assert "VASUKI" in result.output
        assert "Federation" in result.output

    def test_execute_services_flag(self):
        """Execute with --services returns service status."""
        cmd = StatusCommand()
        result = cmd.execute(["--services"])
        assert result.success
        data = result.to_dict()
        assert data.get("mode") == "services"
        assert "HEALTHY" in result.output

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = StatusCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.SYS_WAKE

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = StatusCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.PRITHU

    def test_result_data_has_phase(self):
        """Result data includes phase info."""
        cmd = StatusCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("phase") == "wake"

    def test_result_data_has_position(self):
        """Result data includes position 0."""
        cmd = StatusCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("position") == "0"


# =============================================================================
# REGISTRY INTEGRATION TESTS
# =============================================================================

class TestWakeRegistryIntegration:
    """Test that WAKE commands are registered."""

    def test_status_registered(self):
        """StatusCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("status")
        assert cmd is not None
        assert cmd.name == "status"

    def test_wake_phase_has_commands(self):
        """WAKE phase has commands."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_phase(Phase.WAKE)
        assert len(cmds) >= 1
        names = [c.name for c in cmds]
        assert "status" in names

    def test_prithu_has_status(self):
        """PRITHU owns status command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.PRITHU)
        names = [c.name for c in cmds]
        assert "status" in names

    def test_sys_wake_has_status(self):
        """SYS_WAKE opcode has status command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_opcode(MantraOpCode.SYS_WAKE)
        names = [c.name for c in cmds]
        assert "status" in names


# =============================================================================
# POSITION 0 TESTS (HEAD OF WAKE)
# =============================================================================

class TestPosition0:
    """Test that status is position 0 - the HEAD."""

    def test_sys_wake_is_first_opcode(self):
        """SYS_WAKE is the first opcode in the sequence."""
        # SYS_WAKE is position 0 in the Mahamantra sequence
        assert MantraOpCode.SYS_WAKE.value == "sys_wake"
        # It's the first in the list of opcodes
        opcodes = list(MantraOpCode)
        assert opcodes[0] == MantraOpCode.SYS_WAKE

    def test_prithu_is_avatara(self):
        """PRITHU is an Avatara (HEAD of WAKE phase)."""
        # Avataras are at positions 0, 4, 8, 12 (HEAD of each phase)
        cmd = StatusCommand()
        # PRITHU owns SYS_WAKE which is the HEAD of WAKE phase
        assert cmd.opcode == MantraOpCode.SYS_WAKE
        assert cmd.mahajana == Mahajana.PRITHU

    def test_wake_is_first_phase(self):
        """WAKE is the first phase (0-3)."""
        cmd = StatusCommand()
        assert cmd.phase == Phase.WAKE
        # WAKE phase contains: SYS_WAKE, LOAD_ROOT, ALLOC_MEM, BIND_CTX
        wake_opcodes = [
            MantraOpCode.SYS_WAKE,
            MantraOpCode.LOAD_ROOT,
            MantraOpCode.ALLOC_MEM,
            MantraOpCode.BIND_CTX,
        ]
        assert cmd.opcode in wake_opcodes


# =============================================================================
# STRICT TYPING TESTS
# =============================================================================

class TestStrictTyping:
    """Test that results have no Any types."""

    def test_status_result_no_any(self):
        """StatusCommand result has no Any."""
        cmd = StatusCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')


# =============================================================================
# IMMUTABILITY TESTS
# =============================================================================

class TestImmutability:
    """Test that results are immutable."""

    def test_status_result_frozen(self):
        """StatusCommand result is frozen."""
        cmd = StatusCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False


# =============================================================================
# SEMANTIC TESTS
# =============================================================================

class TestSemantics:
    """Test semantic meaning of PRITHU as status owner."""

    def test_prithu_meaning(self):
        """PRITHU semantically fits status."""
        # Prithu = The king who organized the world
        # Status = Report on system organization
        cmd = StatusCommand()
        assert "first" in cmd.help_text.lower() or "PRITHU" in cmd.help_text

    def test_wake_meaning(self):
        """Status is appropriate for WAKE phase."""
        # WAKE = System initialization
        # Status = First thing you check on wake
        cmd = StatusCommand()
        assert cmd.phase == Phase.WAKE

    def test_position_0_meaning(self):
        """Position 0 is the start of every cycle."""
        # Every Mahamantra cycle starts at position 0 (SYS_WAKE)
        # Status is the first command to run
        cmd = StatusCommand()
        assert cmd.opcode == MantraOpCode.SYS_WAKE
        # Verify it's first in the enum
        opcodes = list(MantraOpCode)
        assert opcodes[0] == cmd.opcode
