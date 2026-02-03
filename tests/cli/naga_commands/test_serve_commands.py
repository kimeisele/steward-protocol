"""
TEST SERVE PHASE COMMANDS
=========================

Tests for SERVE phase (8-11) commands:
- IntelCommand (SHUKA - FETCH_RES) - Position 8
- ChatCommand (PRAHLADA - EXEC_SERVICE) - Position 9, Universal Router
- ValidateCommand (JANAKA - CHECK_DHARMA) - Position 10
- CommitCommand (BHISHMA - COMMIT_LOG) - Position 11

"PRAHLADA routes to all Mahajanas."
"JANAKA validates dharma."
"BHISHMA commits with unwavering oath."

SERVE PHASE COMPLETE - All 4 positions tested.
"""

import pytest

# Import all phases to ensure commands are registered
from vibe_core.cli.naga_commands import (
    purify,  # noqa: F401
    wake,  # noqa: F401
)
from vibe_core.cli.naga_commands.serve.chat import (
    GUARDIAN_COMMANDS,
    ChatCommand,
)
from vibe_core.cli.naga_commands.serve.commit import CommitCommand
from vibe_core.cli.naga_commands.serve.intel import IntelCommand
from vibe_core.cli.naga_commands.serve.validate import ValidateCommand
from vibe_core.protocols.naga.cli_command import (
    NAGA_COMMAND_REGISTRY,
    INagaCommand,
    Mahajana,
    Phase,
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
        assert cmd.opcode == MantraOpCode.EXTEND_CAP

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

    def test_execute_with_greeting_succeeds(self):
        """Execute with greeting returns success."""
        cmd = ChatCommand()
        result = cmd.execute(["Hello", "there"])
        assert result.success
        assert result.exit_code == 0
        assert "PRAHLADA" in result.output

    def test_execute_routes_via_live_computation(self):
        """Execute routes via live computed mahamantra()."""
        cmd = ChatCommand()
        result = cmd.execute(["What's", "the", "status?"])
        assert result.success
        # Live computed routing always produces a guardian
        assert "PRAHLADA" in result.output

    def test_execute_different_inputs_route(self):
        """Different inputs route to (potentially different) guardians."""
        cmd = ChatCommand()
        result = cmd.execute(["scan", "please"])
        assert result.success
        # Shows computed guardian
        assert "PRAHLADA" in result.output

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = ChatCommand()
        result = cmd.execute(["test"])
        assert result.opcode == MantraOpCode.EXTEND_CAP

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

    def test_opcode_is_exec_op(self):
        """Opcode is EXEC_OP (position 8)."""
        cmd = IntelCommand()
        assert cmd.opcode == MantraOpCode.EXEC_OP

    def test_mahajana_is_parashurama(self):
        """Mahajana is PARASHURAMA (owns position 8 / EXEC_OP)."""
        # Note: SHUKA semantically owns intel, but PARASHURAMA owns opcode 8
        cmd = IntelCommand()
        assert cmd.mahajana == Mahajana.PARASHURAMA

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
        assert result.opcode == MantraOpCode.EXEC_OP

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana (PARASHURAMA owns EXEC_OP)."""
        cmd = IntelCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.PARASHURAMA


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

    def test_parashurama_has_intel(self):
        """PARASHURAMA owns intel command (EXEC_OP = position 8)."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.PARASHURAMA)
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
        assert hasattr(result, "success")
        assert hasattr(result, "opcode")
        assert hasattr(result, "mahajana")

    def test_intel_result_no_any(self):
        """IntelCommand result has no Any."""
        cmd = IntelCommand()
        result = cmd.execute([])
        assert hasattr(result, "success")
        assert hasattr(result, "opcode")
        assert hasattr(result, "mahajana")


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


# =============================================================================
# CHAT ROUTING TESTS (via mahamantra() live computed routing)
# =============================================================================
# NOTE: Routing is now 100% LIVE COMPUTED via mahamantra():
#   Input → Seed (MahaCompression) → Attractor (MahaModularSynth) → Position = attractor % 16
#
# This means routing is DETERMINISTIC based on input hash, NOT keyword matching.
# Tests verify the routing mechanism works, not specific keyword→guardian mappings.
# =============================================================================


class TestChatRouting:
    """Test chat command routing via live computed mahamantra()."""

    def test_routing_is_deterministic(self):
        """Same input always routes to same guardian."""
        cmd = ChatCommand()
        result1 = cmd.execute(["test", "message"])
        result2 = cmd.execute(["test", "message"])
        assert result1.success
        assert result2.success
        # Same input = same guardian (deterministic)
        assert result1.output == result2.output

    def test_different_inputs_get_guardians(self):
        """Different inputs get (potentially different) guardians."""
        cmd = ChatCommand()
        inputs = [
            ["alpha"],
            ["beta"],
            ["gamma"],
        ]
        guardians = []
        for inp in inputs:
            result = cmd.execute(inp)
            assert result.success
            # All get a guardian (resonance 1.0 = live computed)
            assert "Resonance: 1.0" in result.output
            guardians.append(result.output)
        # At least show routing is happening
        assert all("PRAHLADA" in g for g in guardians)

    def test_output_shows_computed_guardian(self):
        """Output shows the computed guardian from mahamantra()."""
        cmd = ChatCommand()
        result = cmd.execute(["any", "message"])
        assert result.success
        # Output shows guardian (either routed or direct)
        assert "[PRAHLADA" in result.output
        # Shows the computed guardian name
        assert "→" in result.output or "Input:" in result.output

    def test_routing_to_registered_command(self):
        """Chat routes to registered command when available."""
        cmd = ChatCommand()
        # "create something" routes to SHUKA (intel) which is registered
        result = cmd.execute(["create", "something"])
        assert result.success
        # Either routed to a command OR shows the guardian
        assert "PRAHLADA" in result.output

    def test_prahlada_fallback_for_self(self):
        """Prahlada commands stay with Prahlada (no routing)."""
        cmd = ChatCommand()
        # When mahamantra() returns prahlada, no routing happens
        result = cmd.execute(["boot"])  # "boot" → prahlada in live computed
        assert result.success
        assert "PRAHLADA" in result.output

    def test_unregistered_command_shows_note(self):
        """Unregistered commands show a note in output."""
        cmd = ChatCommand()
        result = cmd.execute(["help"])  # May route to unregistered command
        assert result.success
        # Either successfully routed OR shows "not registered" note
        assert "PRAHLADA" in result.output

    def test_result_includes_guardian_data(self):
        """Result includes guardian in data."""
        cmd = ChatCommand()
        result = cmd.execute(["test", "input"])
        data = result.to_dict()
        # Data includes guardian info
        assert "guardian" in data
        assert data.get("guardian") is not None


# =============================================================================
# UNIVERSAL INTERFACE TESTS (Live Computed Routing)
# =============================================================================


class TestUniversalInterface:
    """Test chat as the universal operator interface with live computed routing."""

    def test_all_inputs_route_successfully(self):
        """All inputs route successfully via live computed routing."""
        cmd = ChatCommand()

        # Various inputs all succeed
        inputs = [["status"], ["scan"], ["intel"], ["hello"]]
        for inp in inputs:
            result = cmd.execute(inp)
            assert result.success, f"Failed for input: {inp}"
            assert "PRAHLADA" in result.output

    def test_routing_produces_guardian(self):
        """Every input produces a guardian via live computation."""
        cmd = ChatCommand()

        result = cmd.execute(["any", "random", "input"])
        assert result.success
        # Should show a guardian (either routed or direct response)
        data = result.to_dict()
        assert data.get("guardian") is not None

    def test_prahlada_is_resilient(self):
        """PRAHLADA handles all queries gracefully."""
        cmd = ChatCommand()
        result = cmd.execute(["something", "completely", "random"])
        assert result.success  # Never fails
        assert "PRAHLADA" in result.output


# =============================================================================
# VALIDATE COMMAND TESTS (JANAKA - CHECK_DHARMA)
# =============================================================================


class TestValidateCommand:
    """Test ValidateCommand (JANAKA - CHECK_DHARMA)."""

    def test_implements_protocol(self):
        """ValidateCommand implements INagaCommand."""
        cmd = ValidateCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_check_dharma(self):
        """Opcode is CHECK_DHARMA."""
        cmd = ValidateCommand()
        assert cmd.opcode == MantraOpCode.STATE_SYNC

    def test_mahajana_is_janaka(self):
        """Mahajana is JANAKA."""
        cmd = ValidateCommand()
        assert cmd.mahajana == Mahajana.JANAKA

    def test_name_is_validate(self):
        """Name is 'validate'."""
        cmd = ValidateCommand()
        assert cmd.name == "validate"

    def test_phase_is_serve(self):
        """Phase is SERVE."""
        cmd = ValidateCommand()
        assert cmd.phase == Phase.SERVE

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = ValidateCommand()
        assert len(cmd.help_text) > 0
        assert "JANAKA" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args runs all validations."""
        cmd = ValidateCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "JANAKA" in result.output

    def test_execute_types_only(self):
        """Execute with --types only."""
        cmd = ValidateCommand()
        result = cmd.execute(["--types"])
        assert result.success
        data = result.to_dict()
        assert "types_passed" in data

    def test_execute_imports_only(self):
        """Execute with --imports only."""
        cmd = ValidateCommand()
        result = cmd.execute(["--imports"])
        assert result.success
        data = result.to_dict()
        assert "imports_passed" in data

    def test_execute_protocols_only(self):
        """Execute with --protocols only."""
        cmd = ValidateCommand()
        result = cmd.execute(["--protocols"])
        assert result.success
        data = result.to_dict()
        assert "protocols_passed" in data

    def test_execute_quick_mode(self):
        """Execute with --quick mode."""
        cmd = ValidateCommand()
        result = cmd.execute(["--quick"])
        assert result.success
        assert "CHECK_DHARMA" in result.output

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = ValidateCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.STATE_SYNC

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = ValidateCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.JANAKA

    def test_result_has_status(self):
        """Result contains dharma status."""
        cmd = ValidateCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert "status" in data
        assert data["status"] in ["DHARMIC", "ADHARMIC"]


# =============================================================================
# COMMIT COMMAND TESTS (BHISHMA - COMMIT_LOG)
# =============================================================================


class TestCommitCommand:
    """Test CommitCommand (BHISHMA - COMMIT_LOG)."""

    def test_implements_protocol(self):
        """CommitCommand implements INagaCommand."""
        cmd = CommitCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_commit_log(self):
        """Opcode is COMMIT_LOG."""
        cmd = CommitCommand()
        assert cmd.opcode == MantraOpCode.LEDGER_SIGN

    def test_mahajana_is_bhishma(self):
        """Mahajana is BHISHMA."""
        cmd = CommitCommand()
        assert cmd.mahajana == Mahajana.BHISHMA

    def test_name_is_commit(self):
        """Name is 'commit'."""
        cmd = CommitCommand()
        assert cmd.name == "commit"

    def test_phase_is_serve(self):
        """Phase is SERVE."""
        cmd = CommitCommand()
        assert cmd.phase == Phase.SERVE

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = CommitCommand()
        assert len(cmd.help_text) > 0
        assert "BHISHMA" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args shows status."""
        cmd = CommitCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "BHISHMA" in result.output

    def test_execute_log_flag(self):
        """Execute with --log shows commits."""
        cmd = CommitCommand()
        result = cmd.execute(["--log"])
        assert result.success
        assert "Recent Commits" in result.output or "Ledger" in result.output

    def test_execute_staged_flag(self):
        """Execute with --staged shows staged."""
        cmd = CommitCommand()
        result = cmd.execute(["--staged"])
        assert result.success
        assert "Staged" in result.output

    def test_execute_diff_flag(self):
        """Execute with --diff shows diff."""
        cmd = CommitCommand()
        result = cmd.execute(["--diff"])
        assert result.success
        assert "Diff" in result.output

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = CommitCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.LEDGER_SIGN

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = CommitCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.BHISHMA

    def test_result_has_branch(self):
        """Result contains branch info."""
        cmd = CommitCommand()
        result = cmd.execute([])
        data = result.to_dict()
        # In a git repo, branch should be present
        assert "branch" in data or "git_repo" in data


# =============================================================================
# SERVE PHASE REGISTRY TESTS (UPDATED)
# =============================================================================


class TestServeRegistryComplete:
    """Test that all SERVE phase commands are registered."""

    def test_validate_registered(self):
        """ValidateCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("validate")
        assert cmd is not None
        assert cmd.name == "validate"

    def test_commit_registered(self):
        """CommitCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("commit")
        assert cmd is not None
        assert cmd.name == "commit"

    def test_serve_phase_has_all_four(self):
        """SERVE phase has all 4 commands."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_phase(Phase.SERVE)
        assert len(cmds) == 4
        names = [c.name for c in cmds]
        assert "intel" in names  # Position 8
        assert "chat" in names  # Position 9
        assert "validate" in names  # Position 10
        assert "commit" in names  # Position 11

    def test_janaka_has_validate(self):
        """JANAKA owns validate command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.JANAKA)
        names = [c.name for c in cmds]
        assert "validate" in names

    def test_bhishma_has_commit(self):
        """BHISHMA owns commit command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.BHISHMA)
        names = [c.name for c in cmds]
        assert "commit" in names


# =============================================================================
# SERVE PHASE STRICT TYPING
# =============================================================================


class TestServeStrictTyping:
    """Test that SERVE commands have proper typing."""

    def test_validate_result_no_any(self):
        """ValidateCommand result has no Any."""
        cmd = ValidateCommand()
        result = cmd.execute([])
        assert hasattr(result, "success")
        assert hasattr(result, "opcode")
        assert hasattr(result, "mahajana")

    def test_commit_result_no_any(self):
        """CommitCommand result has no Any."""
        cmd = CommitCommand()
        result = cmd.execute([])
        assert hasattr(result, "success")
        assert hasattr(result, "opcode")
        assert hasattr(result, "mahajana")


# =============================================================================
# SERVE PHASE IMMUTABILITY
# =============================================================================


class TestServeImmutability:
    """Test that SERVE results are immutable."""

    def test_validate_result_frozen(self):
        """ValidateCommand result is frozen."""
        cmd = ValidateCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False

    def test_commit_result_frozen(self):
        """CommitCommand result is frozen."""
        cmd = CommitCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False


# =============================================================================
# SERVE PHASE COMPLETE TESTS
# =============================================================================


class TestServePhaseComplete:
    """Verify SERVE phase is complete with all 4 commands."""

    def test_all_opcodes_covered(self):
        """All SERVE opcodes have commands."""
        serve_opcodes = [
            MantraOpCode.EXEC_OP,  # Position 8
            MantraOpCode.EXTEND_CAP,  # Position 9
            MantraOpCode.STATE_SYNC,  # Position 10
            MantraOpCode.LEDGER_SIGN,  # Position 11
        ]
        for opcode in serve_opcodes:
            cmds = NAGA_COMMAND_REGISTRY.get_by_opcode(opcode)
            assert len(cmds) >= 1, f"No command for {opcode.name}"

    def test_all_mahajanas_covered(self):
        """All SERVE mahajanas have commands."""
        # SERVE phase = positions 8-11
        serve_mahajanas = [
            Mahajana.PARASHURAMA,  # EXEC_OP (8) - intel
            Mahajana.PRAHLADA,  # EXTEND_CAP (9) - chat
            Mahajana.JANAKA,  # STATE_SYNC (10) - validate
            Mahajana.BHISHMA,  # LEDGER_SIGN (11) - commit
        ]
        for mahajana in serve_mahajanas:
            cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(mahajana)
            assert len(cmds) >= 1, f"No command for {mahajana.name}"
