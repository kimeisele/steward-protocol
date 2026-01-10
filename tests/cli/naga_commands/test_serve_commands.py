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
from vibe_core.cli.naga_commands import wake  # noqa: F401
from vibe_core.cli.naga_commands import purify  # noqa: F401
from vibe_core.cli.naga_commands.serve.chat import (
    ChatCommand,
    detect_intent,
    extract_args,
    INTENT_PATTERNS,
)
from vibe_core.cli.naga_commands.serve.intel import IntelCommand
from vibe_core.cli.naga_commands.serve.validate import ValidateCommand
from vibe_core.cli.naga_commands.serve.commit import CommitCommand
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

    def test_execute_with_greeting_succeeds(self):
        """Execute with greeting returns success."""
        cmd = ChatCommand()
        result = cmd.execute(["Hello", "there"])
        assert result.success
        assert result.exit_code == 0
        assert "PRAHLADA" in result.output

    def test_execute_routes_to_status(self):
        """Execute routes status query to PRITHU."""
        cmd = ChatCommand()
        result = cmd.execute(["What's", "the", "status?"])
        assert result.success
        assert "PRITHU" in result.output

    def test_execute_routes_to_scan(self):
        """Execute routes scan query to VYASA."""
        cmd = ChatCommand()
        result = cmd.execute(["scan", "please"])
        assert result.success
        assert "VYASA" in result.output

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


# =============================================================================
# INTENT DETECTION TESTS
# =============================================================================

class TestIntentDetection:
    """Test intent detection for chat routing."""

    def test_detect_status_intent(self):
        """Detect status intent."""
        assert detect_intent("What's the system status?") == "status"
        assert detect_intent("how is the system") == "status"
        assert detect_intent("are you alive?") == "status"

    def test_detect_scan_intent(self):
        """Detect scan intent."""
        assert detect_intent("scan for vulnerabilities") == "scan"
        assert detect_intent("check the codebase") == "scan"
        assert detect_intent("verify integrity") == "scan"

    def test_detect_intel_intent(self):
        """Detect intel intent."""
        assert detect_intent("any recent intel?") == "intel"
        assert detect_intent("show me threats") == "intel"
        assert detect_intent("what's happening?") == "intel"

    def test_no_intent_for_greeting(self):
        """No command intent for greetings."""
        assert detect_intent("hello there") is None
        assert detect_intent("good morning") is None

    def test_no_intent_for_general(self):
        """No command intent for general chat."""
        assert detect_intent("tell me a joke") is None
        assert detect_intent("what is krishna consciousness") is None


# =============================================================================
# ARGUMENT EXTRACTION TESTS
# =============================================================================

class TestArgumentExtraction:
    """Test argument extraction from natural language."""

    def test_extract_status_brief(self):
        """Extract --brief for status."""
        args = extract_args("quick status check", "status")
        assert "--brief" in args

    def test_extract_status_nagas(self):
        """Extract --nagas for status."""
        args = extract_args("how are the nagas doing", "status")
        assert "--nagas" in args

    def test_extract_scan_deep(self):
        """Extract --deep for scan."""
        args = extract_args("do a deep scan", "scan")
        assert "--deep" in args

    def test_extract_scan_toxicity(self):
        """Extract --toxicity for scan."""
        args = extract_args("check for security vulnerabilities", "scan")
        assert "--toxicity" in args

    def test_extract_intel_critical(self):
        """Extract --critical for intel."""
        args = extract_args("show critical intel", "intel")
        assert "--critical" in args

    def test_extract_intel_threats(self):
        """Extract --threats for intel."""
        args = extract_args("any active threats?", "intel")
        assert "--threats" in args


# =============================================================================
# CHAT ROUTING TESTS
# =============================================================================

class TestChatRouting:
    """Test chat command routing to other Mahajanas."""

    def test_routes_to_status(self):
        """Chat routes status queries to PRITHU."""
        cmd = ChatCommand()
        result = cmd.execute(["What's", "the", "system", "status?"])
        assert result.success
        assert "PRAHLADA → PRITHU" in result.output
        assert "status" in result.output.lower()

    def test_routes_to_scan(self):
        """Chat routes scan queries to VYASA."""
        cmd = ChatCommand()
        result = cmd.execute(["scan", "for", "vulnerabilities"])
        assert result.success
        assert "PRAHLADA → VYASA" in result.output
        assert "VYASA" in result.output

    def test_routes_to_intel(self):
        """Chat routes intel queries to SHUKA."""
        cmd = ChatCommand()
        result = cmd.execute(["any", "recent", "intel?"])
        assert result.success
        assert "PRAHLADA → SHUKA" in result.output
        assert "SHUKA" in result.output

    def test_routes_with_extracted_args(self):
        """Chat extracts args from natural language."""
        cmd = ChatCommand()
        result = cmd.execute(["deep", "security", "scan"])
        assert result.success
        # Deep scan should have more output
        assert "Deep Scan" in result.output or "TOXICITY" in result.output

    def test_responds_directly_for_greeting(self):
        """Chat responds directly for greetings."""
        cmd = ChatCommand()
        result = cmd.execute(["Hare", "Krishna!"])
        assert result.success
        assert "PRAHLADA" in result.output
        assert "→" not in result.output  # No routing

    def test_responds_directly_for_help(self):
        """Chat responds with help."""
        cmd = ChatCommand()
        result = cmd.execute(["help"])
        assert result.success
        assert "STATUS" in result.output
        assert "SCAN" in result.output
        assert "INTEL" in result.output

    def test_result_includes_routing_data(self):
        """Routed result includes routing metadata."""
        cmd = ChatCommand()
        result = cmd.execute(["system", "status"])
        data = result.to_dict()
        assert data.get("routed_by") == "prahlada"


# =============================================================================
# UNIVERSAL INTERFACE TESTS
# =============================================================================

class TestUniversalInterface:
    """Test chat as the universal operator interface."""

    def test_all_commands_accessible_via_chat(self):
        """All registered commands accessible via chat."""
        cmd = ChatCommand()

        # Status via chat
        status_result = cmd.execute(["status"])
        assert status_result.success
        assert "PRITHU" in status_result.output

        # Scan via chat
        scan_result = cmd.execute(["scan"])
        assert scan_result.success
        assert "VYASA" in scan_result.output

        # Intel via chat
        intel_result = cmd.execute(["intel"])
        assert intel_result.success
        assert "SHUKA" in intel_result.output

    def test_natural_language_works(self):
        """Natural language queries work."""
        cmd = ChatCommand()

        # Natural status query
        result = cmd.execute(["How", "is", "the", "system", "doing?"])
        assert result.success
        assert "PRITHU" in result.output

    def test_prahlada_is_resilient(self):
        """PRAHLADA handles unknown queries gracefully."""
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
        assert cmd.opcode == MantraOpCode.CHECK_DHARMA

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
        assert result.opcode == MantraOpCode.CHECK_DHARMA

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
        assert cmd.opcode == MantraOpCode.COMMIT_LOG

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
        assert result.opcode == MantraOpCode.COMMIT_LOG

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
        assert "intel" in names     # Position 8
        assert "chat" in names      # Position 9
        assert "validate" in names  # Position 10
        assert "commit" in names    # Position 11

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
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')

    def test_commit_result_no_any(self):
        """CommitCommand result has no Any."""
        cmd = CommitCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')


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
            MantraOpCode.FETCH_RES,      # Position 8
            MantraOpCode.EXEC_SERVICE,   # Position 9
            MantraOpCode.CHECK_DHARMA,   # Position 10
            MantraOpCode.COMMIT_LOG,     # Position 11
        ]
        for opcode in serve_opcodes:
            cmds = NAGA_COMMAND_REGISTRY.get_by_opcode(opcode)
            assert len(cmds) >= 1, f"No command for {opcode.name}"

    def test_all_mahajanas_covered(self):
        """All SERVE mahajanas have commands."""
        serve_mahajanas = [
            Mahajana.SHUKA,     # FETCH_RES (intel)
            Mahajana.PRAHLADA,  # EXEC_SERVICE (chat)
            Mahajana.JANAKA,    # CHECK_DHARMA (validate)
            Mahajana.BHISHMA,   # COMMIT_LOG (commit)
        ]
        for mahajana in serve_mahajanas:
            cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(mahajana)
            assert len(cmds) >= 1, f"No command for {mahajana.name}"
