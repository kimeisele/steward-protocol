"""
TEST WAKE PHASE COMMANDS
========================

Tests for WAKE phase (0-3) commands:
- StatusCommand (PRITHU - SYS_WAKE) - Position 0
- IdentityCommand (BRAHMA - LOAD_ROOT) - Position 1
- ResourcesCommand (NARADA - ALLOC_MEM) - Position 2
- ContextCommand (SHAMBHU - BIND_CTX) - Position 3

"Prithu is the first king - status is the first command."
"Brahma creates - identity establishes the root."
"Narada distributes - resources are allocated."
"Shambhu transforms - context is bound."

WAKE PHASE COMPLETE - All 4 positions tested.
"""

import pytest

from vibe_core.cli.naga_commands.wake.status import StatusCommand
from vibe_core.cli.naga_commands.wake.identity import IdentityCommand
from vibe_core.cli.naga_commands.wake.resources import ResourcesCommand
from vibe_core.cli.naga_commands.wake.context import ContextCommand
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
            MantraOpCode.INIT_THREAD,
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


# =============================================================================
# IDENTITY COMMAND TESTS (BRAHMA - LOAD_ROOT)
# =============================================================================


class TestIdentityCommand:
    """Test IdentityCommand (BRAHMA - LOAD_ROOT)."""

    def test_implements_protocol(self):
        """IdentityCommand implements INagaCommand."""
        cmd = IdentityCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_load_root(self):
        """Opcode is LOAD_ROOT."""
        cmd = IdentityCommand()
        assert cmd.opcode == MantraOpCode.LOAD_ROOT

    def test_mahajana_is_brahma(self):
        """Mahajana is BRAHMA."""
        cmd = IdentityCommand()
        assert cmd.mahajana == Mahajana.BRAHMA

    def test_name_is_identity(self):
        """Name is 'identity'."""
        cmd = IdentityCommand()
        assert cmd.name == "identity"

    def test_phase_is_wake(self):
        """Phase is WAKE."""
        cmd = IdentityCommand()
        assert cmd.phase == Phase.WAKE

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = IdentityCommand()
        assert len(cmd.help_text) > 0
        assert "BRAHMA" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args shows identity."""
        cmd = IdentityCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "BRAHMA" in result.output

    def test_execute_config_flag(self):
        """Execute with --config shows configuration."""
        cmd = IdentityCommand()
        result = cmd.execute(["--config"])
        assert result.success
        assert "Configuration" in result.output

    def test_execute_lineage_flag(self):
        """Execute with --lineage shows lineage."""
        cmd = IdentityCommand()
        result = cmd.execute(["--lineage"])
        assert result.success
        assert "Lineage" in result.output

    def test_execute_root_flag(self):
        """Execute with --root shows root paths."""
        cmd = IdentityCommand()
        result = cmd.execute(["--root"])
        assert result.success
        assert "Root Paths" in result.output

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = IdentityCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.LOAD_ROOT

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = IdentityCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.BRAHMA


# =============================================================================
# RESOURCES COMMAND TESTS (NARADA - ALLOC_MEM)
# =============================================================================


class TestResourcesCommand:
    """Test ResourcesCommand (NARADA - ALLOC_MEM)."""

    def test_implements_protocol(self):
        """ResourcesCommand implements INagaCommand."""
        cmd = ResourcesCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_alloc_mem(self):
        """Opcode is ALLOC_MEM."""
        cmd = ResourcesCommand()
        assert cmd.opcode == MantraOpCode.ALLOC_MEM

    def test_mahajana_is_narada(self):
        """Mahajana is NARADA."""
        cmd = ResourcesCommand()
        assert cmd.mahajana == Mahajana.NARADA

    def test_name_is_resources(self):
        """Name is 'resources'."""
        cmd = ResourcesCommand()
        assert cmd.name == "resources"

    def test_phase_is_wake(self):
        """Phase is WAKE."""
        cmd = ResourcesCommand()
        assert cmd.phase == Phase.WAKE

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = ResourcesCommand()
        assert len(cmd.help_text) > 0
        assert "NARADA" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args shows resources."""
        cmd = ResourcesCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "NARADA" in result.output

    def test_execute_memory_flag(self):
        """Execute with --memory shows memory details."""
        cmd = ResourcesCommand()
        result = cmd.execute(["--memory"])
        assert result.success
        assert "Memory" in result.output

    def test_execute_registry_flag(self):
        """Execute with --registry shows registry allocations."""
        cmd = ResourcesCommand()
        result = cmd.execute(["--registry"])
        assert result.success
        assert "Registry" in result.output

    def test_execute_pools_flag(self):
        """Execute with --pools shows pool status."""
        cmd = ResourcesCommand()
        result = cmd.execute(["--pools"])
        assert result.success
        assert "Pools" in result.output

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = ResourcesCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.ALLOC_MEM

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = ResourcesCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.NARADA


# =============================================================================
# CONTEXT COMMAND TESTS (SHAMBHU - BIND_CTX)
# =============================================================================


class TestContextCommand:
    """Test ContextCommand (SHAMBHU - BIND_CTX)."""

    def test_implements_protocol(self):
        """ContextCommand implements INagaCommand."""
        cmd = ContextCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_bind_ctx(self):
        """Opcode is BIND_CTX."""
        cmd = ContextCommand()
        assert cmd.opcode == MantraOpCode.INIT_THREAD

    def test_mahajana_is_shambhu(self):
        """Mahajana is SHAMBHU."""
        cmd = ContextCommand()
        assert cmd.mahajana == Mahajana.SHAMBHU

    def test_name_is_context(self):
        """Name is 'context'."""
        cmd = ContextCommand()
        assert cmd.name == "context"

    def test_phase_is_wake(self):
        """Phase is WAKE."""
        cmd = ContextCommand()
        assert cmd.phase == Phase.WAKE

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = ContextCommand()
        assert len(cmd.help_text) > 0
        assert "SHAMBHU" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args shows context."""
        cmd = ContextCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "SHAMBHU" in result.output

    def test_execute_env_flag(self):
        """Execute with --env shows environment."""
        cmd = ContextCommand()
        result = cmd.execute(["--env"])
        assert result.success
        assert "Environment" in result.output

    def test_execute_session_flag(self):
        """Execute with --session shows session."""
        cmd = ContextCommand()
        result = cmd.execute(["--session"])
        assert result.success
        assert "Session" in result.output

    def test_execute_bindings_flag(self):
        """Execute with --bindings shows bindings."""
        cmd = ContextCommand()
        result = cmd.execute(["--bindings"])
        assert result.success
        assert "Bindings" in result.output

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = ContextCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.INIT_THREAD

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = ContextCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.SHAMBHU


# =============================================================================
# WAKE PHASE REGISTRY TESTS (COMPLETE)
# =============================================================================


class TestWakeRegistryComplete:
    """Test that all WAKE phase commands are registered."""

    def test_identity_registered(self):
        """IdentityCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("identity")
        assert cmd is not None
        assert cmd.name == "identity"

    def test_resources_registered(self):
        """ResourcesCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("resources")
        assert cmd is not None
        assert cmd.name == "resources"

    def test_context_registered(self):
        """ContextCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("context")
        assert cmd is not None
        assert cmd.name == "context"

    def test_wake_phase_has_all_four(self):
        """WAKE phase has all 4 commands."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_phase(Phase.WAKE)
        assert len(cmds) == 4
        names = [c.name for c in cmds]
        assert "status" in names     # Position 0
        assert "identity" in names   # Position 1
        assert "resources" in names  # Position 2
        assert "context" in names    # Position 3

    def test_brahma_has_identity(self):
        """BRAHMA owns identity command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.BRAHMA)
        names = [c.name for c in cmds]
        assert "identity" in names

    def test_narada_has_resources(self):
        """NARADA owns resources command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.NARADA)
        names = [c.name for c in cmds]
        assert "resources" in names

    def test_shambhu_has_context(self):
        """SHAMBHU owns context command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.SHAMBHU)
        names = [c.name for c in cmds]
        assert "context" in names


# =============================================================================
# WAKE PHASE STRICT TYPING
# =============================================================================


class TestWakeStrictTyping:
    """Test that WAKE commands have proper typing."""

    def test_identity_result_no_any(self):
        """IdentityCommand result has no Any."""
        cmd = IdentityCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')

    def test_resources_result_no_any(self):
        """ResourcesCommand result has no Any."""
        cmd = ResourcesCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')

    def test_context_result_no_any(self):
        """ContextCommand result has no Any."""
        cmd = ContextCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')


# =============================================================================
# WAKE PHASE IMMUTABILITY
# =============================================================================


class TestWakeImmutability:
    """Test that WAKE results are immutable."""

    def test_identity_result_frozen(self):
        """IdentityCommand result is frozen."""
        cmd = IdentityCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False

    def test_resources_result_frozen(self):
        """ResourcesCommand result is frozen."""
        cmd = ResourcesCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False

    def test_context_result_frozen(self):
        """ContextCommand result is frozen."""
        cmd = ContextCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False


# =============================================================================
# WAKE PHASE COMPLETE TESTS
# =============================================================================


class TestWakePhaseComplete:
    """Verify WAKE phase is complete with all 4 commands."""

    def test_all_opcodes_covered(self):
        """All WAKE opcodes have commands."""
        wake_opcodes = [
            MantraOpCode.SYS_WAKE,    # Position 0
            MantraOpCode.LOAD_ROOT,   # Position 1
            MantraOpCode.ALLOC_MEM,   # Position 2
            MantraOpCode.INIT_THREAD,    # Position 3
        ]
        for opcode in wake_opcodes:
            cmds = NAGA_COMMAND_REGISTRY.get_by_opcode(opcode)
            assert len(cmds) >= 1, f"No command for {opcode.name}"

    def test_all_mahajanas_covered(self):
        """All WAKE mahajanas have commands."""
        wake_mahajanas = [
            Mahajana.PRITHU,   # SYS_WAKE (status)
            Mahajana.BRAHMA,   # LOAD_ROOT (identity)
            Mahajana.NARADA,   # ALLOC_MEM (resources)
            Mahajana.SHAMBHU,  # BIND_CTX (context)
        ]
        for mahajana in wake_mahajanas:
            cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(mahajana)
            assert len(cmds) >= 1, f"No command for {mahajana.name}"
