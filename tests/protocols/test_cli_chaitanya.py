"""
TEST CLI CHAITANYA SINGULARITY
==============================

Tests for the graceful CLI protocol.

PULL IN PATTERN:
- Every error → MahamantraGrace (not rejection!)
- Nityananda pattern: accept everyone
- Retry always available

ACINTYA PRINCIPLE:
- AnantaShesha (strict) coexists with ChaitanyaShell (graceful)
- Both implement ShellProtocol
- User chooses based on need
"""

import pytest
from datetime import datetime

from vibe_core.protocols.universal.cli import (
    # Strict Types (Anti-Mayavad)
    CliInput,
    CliPayload,
    CliResult,
    # Original (strict)
    AnantaResponse,
    ShellProtocol,
    AnantaShesha,
    ANANTA_SHESHA,
    # Chaitanya Singularity (graceful)
    MAHAMANTRA,
    GraceType,
    MahamantraGrace,
    ICliProtocol,
    NavigationResult,
    ChaitanyaShell,
    CHAITANYA_SHELL,
    # ICommand Protocol (16-Command Interface)
    CommandResult,
    CommandHelp,
    ICliCommand,
    # MantraProcessor (Computational Engine)
    MantraProcessorResult,
    MantraProcessor,
    # GAD-000 Seal (No Manual Labour)
    GAD000Seal,
    verify_gad000,
)


class TestMahamantraGrace:
    """Test the MahamantraGrace response type."""

    def test_grace_is_always_truthy(self):
        """Grace is always available - always truthy."""
        grace = MahamantraGrace()
        assert bool(grace) is True

    def test_grace_contains_mahamantra(self):
        """Grace always contains the Mahamantra."""
        grace = MahamantraGrace()
        assert "Hare Kṛṣṇa" in grace.mantra
        assert "Rāma" in grace.mantra

    def test_grace_default_type_is_mahamantra(self):
        """Default grace type is MAHAMANTRA."""
        grace = MahamantraGrace()
        assert grace.grace_type == GraceType.MAHAMANTRA

    def test_grace_retry_allowed_by_default(self):
        """Retry is allowed by default."""
        grace = MahamantraGrace()
        assert grace.retry_allowed is True

    def test_grace_string_contains_message_and_mantra(self):
        """String representation contains message and mantra."""
        grace = MahamantraGrace(message="Test message")
        s = str(grace)
        assert "Test message" in s
        assert "Hare Kṛṣṇa" in s


class TestGraceTypes:
    """Test the different grace types."""

    def test_mahamantra_grace(self):
        """MAHAMANTRA - default grace for everyone."""
        grace = MahamantraGrace(grace_type=GraceType.MAHAMANTRA)
        assert grace.grace_type == GraceType.MAHAMANTRA

    def test_nityananda_grace(self):
        """NITYANANDA - extra mercy for the fallen."""
        grace = MahamantraGrace(grace_type=GraceType.NITYANANDA)
        assert grace.grace_type == GraceType.NITYANANDA

    def test_prabhupada_grace(self):
        """PRABHUPADA - instruction-based grace."""
        grace = MahamantraGrace(grace_type=GraceType.PRABHUPADA)
        assert grace.grace_type == GraceType.PRABHUPADA

    def test_chaitanya_grace(self):
        """CHAITANYA - direct grace from the source."""
        grace = MahamantraGrace(grace_type=GraceType.CHAITANYA)
        assert grace.grace_type == GraceType.CHAITANYA


class TestChaitanyaShell:
    """Test the ChaitanyaShell graceful wrapper."""

    @pytest.fixture
    def shell(self):
        return ChaitanyaShell()

    def test_shell_has_inner_ananta(self, shell):
        """Shell wraps AnantaShesha."""
        assert shell._inner is not None
        assert isinstance(shell._inner, AnantaShesha)

    def test_chant_with_grace_returns_grace_on_invalid_input(self, shell):
        """Invalid input returns grace, not rejection."""
        # Pass invalid input (not CommandContext or CLICapabilityToken)
        result = shell.chant_with_grace("invalid", "test")

        # Should return MahamantraGrace, not rejection!
        assert isinstance(result, MahamantraGrace)
        assert result.retry_allowed is True
        assert "Hare Kṛṣṇa" in result.mantra

    def test_chant_with_grace_nityananda_type_on_error(self, shell):
        """Errors get NITYANANDA grace type."""
        result = shell.chant_with_grace("invalid", "test")
        assert result.grace_type == GraceType.NITYANANDA

    def test_chant_with_grace_preserves_original_error(self, shell):
        """Original error is preserved in grace."""
        result = shell.chant_with_grace("invalid", "test")
        assert result.original_error is not None

    def test_history_tracks_commands(self, shell):
        """History tracks all commands."""
        shell.chant_with_grace("input1", "cmd1")
        shell.chant_with_grace("input2", "cmd2")

        assert len(shell.history) == 2

    def test_retry_returns_grace(self, shell):
        """Retry returns grace when no previous command."""
        result = shell.retry()
        assert isinstance(result, MahamantraGrace)
        assert result.retry_allowed is False  # No previous command

    def test_retry_after_command(self, shell):
        """Retry after command re-executes with grace."""
        shell.chant_with_grace("input", "cmd")
        result = shell.retry()
        assert isinstance(result, MahamantraGrace)
        # History should have 2 entries now
        assert len(shell.history) == 2

    def test_clear_history(self, shell):
        """Clear history returns grace and empties history."""
        shell.chant_with_grace("input", "cmd")
        result = shell.clear_history()

        assert isinstance(result, MahamantraGrace)
        assert len(shell.history) == 0


class TestChaitanyaShellNavigation:
    """Test fractal navigation."""

    @pytest.fixture
    def shell(self):
        return ChaitanyaShell()

    def test_navigate_returns_result(self, shell):
        """Navigate returns NavigationResult."""
        result = shell.navigate("proto/om")
        assert isinstance(result, NavigationResult)

    def test_navigate_preserves_path(self, shell):
        """Navigate preserves the requested path."""
        result = shell.navigate("proto/om")
        assert result.path == "proto/om"

    def test_navigate_includes_grace(self, shell):
        """Navigate includes grace (for unimplemented paths)."""
        result = shell.navigate("unimplemented/path")
        assert result.grace is not None
        assert isinstance(result.grace, MahamantraGrace)


class TestChaitanyaShellReport:
    """Test JSON report generation."""

    @pytest.fixture
    def shell(self):
        return ChaitanyaShell()

    def test_report_returns_json(self, shell):
        """Report returns valid JSON."""
        import json

        report = shell.report(format="json")
        data = json.loads(report)
        assert "session" in data
        assert "mahamantra" in data

    def test_report_contains_mahamantra(self, shell):
        """Report contains the Mahamantra."""
        import json

        report = shell.report()
        data = json.loads(report)
        assert "Hare Kṛṣṇa" in data["mahamantra"]

    def test_report_tracks_grace_given(self, shell):
        """Report tracks how much grace was given."""
        shell.chant_with_grace("invalid1", "cmd1")
        shell.chant_with_grace("invalid2", "cmd2")

        import json

        report = shell.report()
        data = json.loads(report)

        assert data["session"]["grace_given"] == 2


class TestAcintyaPrinciple:
    """
    Test that strict and graceful coexist (Acintya).

    Both AnantaShesha (strict) and ChaitanyaShell (graceful)
    should be valid and usable.
    """

    def test_ananta_shesha_is_strict(self):
        """AnantaShesha rejects invalid input."""
        shell = ANANTA_SHESHA
        result = shell.chant("invalid", "test")

        # Should return AnantaResponse with success=False
        assert isinstance(result, AnantaResponse)
        assert result.success is False
        assert "ANANTA REJECTS" in result.message

    def test_chaitanya_shell_is_graceful(self):
        """ChaitanyaShell gives grace on invalid input."""
        shell = CHAITANYA_SHELL
        result = shell.chant_with_grace("invalid", "test")

        # Should return MahamantraGrace
        assert isinstance(result, MahamantraGrace)
        assert "Hare Kṛṣṇa" in result.mantra

    def test_both_implement_shell_protocol(self):
        """Both shells implement ShellProtocol."""
        # AnantaShesha has chant method
        assert hasattr(ANANTA_SHESHA, "chant")
        assert callable(ANANTA_SHESHA.chant)

        # ChaitanyaShell has chant method
        assert hasattr(CHAITANYA_SHELL, "chant")
        assert callable(CHAITANYA_SHELL.chant)

    def test_user_can_choose(self):
        """User can choose between strict and graceful."""
        # Strict mode - for those who want it
        strict_result = ANANTA_SHESHA.chant("invalid", "test")
        assert isinstance(strict_result, AnantaResponse)

        # Graceful mode - for Kali Yuga
        graceful_result = CHAITANYA_SHELL.chant_with_grace("invalid", "test")
        assert isinstance(graceful_result, MahamantraGrace)


class TestSingletons:
    """Test singleton instances."""

    def test_ananta_shesha_singleton(self):
        """ANANTA_SHESHA is available as singleton."""
        assert ANANTA_SHESHA is not None
        assert isinstance(ANANTA_SHESHA, AnantaShesha)

    def test_chaitanya_shell_singleton(self):
        """CHAITANYA_SHELL is available as singleton."""
        assert CHAITANYA_SHELL is not None
        assert isinstance(CHAITANYA_SHELL, ChaitanyaShell)

    def test_mahamantra_constant(self):
        """MAHAMANTRA constant is available."""
        assert MAHAMANTRA is not None
        assert "Hare Kṛṣṇa" in MAHAMANTRA
        assert "Rāma" in MAHAMANTRA


class TestCommandResult:
    """Test the CommandResult type (strict, no Any)."""

    def test_command_result_success(self):
        """CommandResult tracks success state."""
        result = CommandResult(success=True, opcode="exec_service", message="Executed successfully")
        assert result.success is True
        assert bool(result) is True

    def test_command_result_failure(self):
        """CommandResult tracks failure state."""
        result = CommandResult(success=False, opcode="exec_service", message="Execution failed")
        assert result.success is False
        assert bool(result) is False

    def test_command_result_with_data(self):
        """CommandResult can carry typed data."""
        result = CommandResult(success=True, opcode="cache_state", message="Cached", data={"key": "value", "count": 42})
        assert result.data is not None
        assert result.data["key"] == "value"
        assert result.data["count"] == 42

    def test_command_result_has_timestamp(self):
        """CommandResult has a timestamp."""
        result = CommandResult(success=True, opcode="sys_wake", message="Awake")
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)


class TestCommandHelp:
    """Test the CommandHelp type (GAD-000 compliant)."""

    def test_command_help_has_gad_000_criteria(self):
        """CommandHelp includes all GAD-000 criteria."""
        help_info = CommandHelp(
            opcode="exec_service",
            name="exec",
            phase="SERVE",
            word="RAMA",
            description="Execute work",
            input_type="ResolvedIntent",
            output_type="CliResult",
            discoverability="vibe help --json",
            observability="vibe status --json",
            parseability="E_NO_CTX, E_UNSIGNED",
            composability="vibe parse | vibe exec",
            idempotency="Same intent_hash → cached result",
            recoverability="vibe gc && vibe reset",
        )
        # D-O-P-C-I-R
        assert help_info.discoverability is not None
        assert help_info.observability is not None
        assert help_info.parseability is not None
        assert help_info.composability is not None
        assert help_info.idempotency is not None
        assert help_info.recoverability is not None

    def test_command_help_has_mantra_mapping(self):
        """CommandHelp includes Mahamantra mapping."""
        help_info = CommandHelp(
            opcode="sys_wake",
            name="wake",
            phase="WAKE",
            word="HARE",
            description="Focus system, stop maya",
            input_type="None",
            output_type="CliResult",
            discoverability="vibe help wake",
            observability="vibe status",
            parseability="E_ALREADY_AWAKE",
            composability="vibe wake | vibe identity",
            idempotency="Idempotent - multiple calls safe",
            recoverability="vibe reset",
        )
        assert help_info.phase == "WAKE"
        assert help_info.word == "HARE"
        assert help_info.opcode == "sys_wake"


class TestICliCommand:
    """Test the ICliCommand Protocol."""

    def test_protocol_is_runtime_checkable(self):
        """ICliCommand is runtime checkable."""

        # Create a minimal implementation
        class TestCommand:
            @property
            def opcode(self) -> str:
                return "sys_wake"

            @property
            def name(self) -> str:
                return "wake"

            @property
            def phase(self) -> str:
                return "WAKE"

            @property
            def word(self) -> str:
                return "HARE"

            def execute(self, ctx, payload):
                return MahamantraGrace()

            def help(self):
                return CommandHelp(
                    opcode="sys_wake",
                    name="wake",
                    phase="WAKE",
                    word="HARE",
                    description="Test",
                    input_type="None",
                    output_type="CliResult",
                    discoverability="test",
                    observability="test",
                    parseability="test",
                    composability="test",
                    idempotency="test",
                    recoverability="test",
                )

        cmd = TestCommand()
        assert isinstance(cmd, ICliCommand)

    def test_protocol_has_required_methods(self):
        """ICliCommand requires opcode, name, phase, word, execute, help."""
        # Verify protocol has expected attributes
        assert hasattr(ICliCommand, "opcode")
        assert hasattr(ICliCommand, "name")
        assert hasattr(ICliCommand, "phase")
        assert hasattr(ICliCommand, "word")
        assert hasattr(ICliCommand, "execute")
        assert hasattr(ICliCommand, "help")


class TestCliResult:
    """Test the CliResult union type."""

    def test_cli_result_can_be_command_result(self):
        """CliResult accepts CommandResult."""
        result: CliResult = CommandResult(success=True, opcode="exec_service", message="OK")
        assert isinstance(result, CommandResult)

    def test_cli_result_can_be_mahamantra_grace(self):
        """CliResult accepts MahamantraGrace."""
        result: CliResult = MahamantraGrace()
        assert isinstance(result, MahamantraGrace)

    def test_cli_result_both_truthy_patterns(self):
        """CliResult types have consistent truthiness."""
        success: CliResult = CommandResult(success=True, opcode="test", message="OK")
        failure: CliResult = CommandResult(success=False, opcode="test", message="Failed")
        grace: CliResult = MahamantraGrace()

        assert bool(success) is True
        assert bool(failure) is False
        assert bool(grace) is True  # Grace is always truthy


class TestMantraProcessor:
    """Test the MantraProcessor - the Computational Engine."""

    @pytest.fixture
    def processor(self):
        return MantraProcessor()

    def test_processor_has_16_commands(self, processor):
        """MantraProcessor has exactly 16 commands (16 words of Mahamantra)."""
        commands = processor.list_commands()
        assert len(commands) == 16

    def test_processor_maps_to_opcodes(self, processor):
        """Each command maps to a MantraOpCode."""
        # Test all 16 commands
        command_names = [
            "wake",
            "identity",
            "alloc",
            "bind",
            "verify",
            "parse",
            "gc",
            "pulse",
            "fetch",
            "exec",
            "check",
            "commit",
            "cache",
            "optimize",
            "yield",
            "reset",
        ]
        for cmd in command_names:
            opcode = processor.get_opcode(cmd)
            assert opcode is not None, f"Command {cmd} should have an opcode"

    def test_processor_routes_to_mahajanas(self, processor):
        """Commands route to Mahajanas via OpCodes."""
        # Test a few known routes
        assert processor.get_mahajana("identity") == "brahma"
        assert processor.get_mahajana("exec") == "janaka"
        assert processor.get_mahajana("reset") == "kumaras"

    def test_processor_identifies_head_commands(self, processor):
        """HEAD commands (Avatara-owned) are identified."""
        # HEAD positions: 1, 5, 9, 13 = wake, verify, fetch, cache
        assert processor.is_head_command("wake") is True
        assert processor.is_head_command("verify") is True
        assert processor.is_head_command("fetch") is True
        assert processor.is_head_command("cache") is True

        # Workers are NOT heads
        assert processor.is_head_command("exec") is False
        assert processor.is_head_command("reset") is False

    def test_processor_unknown_command_returns_none(self, processor):
        """Unknown command returns None for opcode."""
        assert processor.get_opcode("unknown_cmd") is None
        assert processor.get_mahajana("unknown_cmd") is None

    def test_processor_chant_unknown_returns_grace(self, processor):
        """Chanting unknown command returns MahamantraGrace."""
        result = processor.chant("unknown_cmd", "invalid_ctx")
        assert isinstance(result, MantraProcessorResult)
        assert isinstance(result.result, MahamantraGrace)
        assert "Unknown command" in result.result.message

    def test_processor_chant_valid_returns_result(self, processor):
        """Chanting valid command returns MantraProcessorResult."""
        result = processor.chant("exec", "some_ctx")
        assert isinstance(result, MantraProcessorResult)
        assert result.command == "exec"
        assert result.opcode == "exec_service"
        # Should get grace because ctx is invalid
        assert isinstance(result.result, MahamantraGrace)

    def test_processor_list_commands_sorted_by_position(self, processor):
        """Commands are sorted by position (1-16)."""
        commands = processor.list_commands()
        positions = [c["position"] for c in commands]
        assert positions == sorted(positions)

    def test_processor_list_commands_has_all_quarters(self, processor):
        """All 4 quarters are represented in commands."""
        commands = processor.list_commands()
        quarters = set(c["quarter"] for c in commands)
        assert quarters == {1, 2, 3, 4}


class TestMantraProcessorResult:
    """Test the MantraProcessorResult type."""

    def test_result_contains_routing_metadata(self):
        """MantraProcessorResult contains routing metadata."""
        result = MantraProcessorResult(
            command="exec",
            opcode="exec_service",
            mahajana="janaka",
            quarter=3,
            position=10,
            is_head=False,
            result=MahamantraGrace(),
        )
        assert result.command == "exec"
        assert result.opcode == "exec_service"
        assert result.mahajana == "janaka"
        assert result.quarter == 3
        assert result.position == 10
        assert result.is_head is False

    def test_result_with_head_flag(self):
        """MantraProcessorResult correctly flags HEAD commands."""
        head_result = MantraProcessorResult(
            command="wake",
            opcode="sys_wake",
            mahajana="brahma",
            quarter=1,
            position=1,
            is_head=True,
            result=MahamantraGrace(),
        )
        worker_result = MantraProcessorResult(
            command="exec",
            opcode="exec_service",
            mahajana="janaka",
            quarter=3,
            position=10,
            is_head=False,
            result=CommandResult(success=True, opcode="exec_service", message="OK"),
        )

        assert head_result.is_head is True
        assert worker_result.is_head is False


class TestGAD000Seal:
    """Test the GAD-000 Seal - No Manual Labour."""

    def test_verify_gad000_returns_seal(self):
        """verify_gad000() returns a GAD000Seal."""
        seal = verify_gad000()
        assert isinstance(seal, GAD000Seal)

    def test_seal_has_16_commands(self):
        """Seal verifies 16 commands are mapped."""
        seal = verify_gad000()
        assert seal.commands_mapped == 16

    def test_seal_has_16_opcodes(self):
        """Seal verifies 16 opcodes are routed."""
        seal = verify_gad000()
        assert seal.opcodes_routed == 16

    def test_seal_has_12_worker_opcodes(self):
        """Seal verifies 12 worker opcodes (non-HEAD)."""
        seal = verify_gad000()
        assert seal.worker_opcodes == 12

    def test_seal_has_4_heads(self):
        """Seal verifies 4 HEADs (Avataras) are active."""
        seal = verify_gad000()
        assert seal.heads_active == 4

    def test_seal_has_mahajanas(self):
        """Seal verifies Mahajanas are active (9-12 depending on mode)."""
        seal = verify_gad000()
        assert seal.unique_mahajanas >= 9

    def test_seal_heartbeat_available(self):
        """Seal verifies MantraHeartbeat is available."""
        seal = verify_gad000()
        assert seal.heartbeat_available is True

    def test_seal_krishna_present(self):
        """Seal verifies Krishna is ALWAYS present (acintya)."""
        seal = verify_gad000()
        assert seal.krishna_present is True

    def test_seal_is_valid(self):
        """Seal is_valid returns True when all checks pass."""
        seal = verify_gad000()
        assert seal.is_valid is True

    def test_seal_marker_is_sealed_37(self):
        """Seal marker is 'GAD-000:SEALED:37' when valid."""
        seal = verify_gad000()
        assert seal.marker == "GAD-000:SEALED:37"

    def test_broken_seal_marker(self):
        """Broken seal marker shows what's missing."""
        broken_seal = GAD000Seal(
            commands_mapped=10,  # Missing 6
            opcodes_routed=16,
            worker_opcodes=12,
            heads_active=4,
            unique_mahajanas=9,
            heartbeat_available=True,
            krishna_present=True,
        )
        assert "cmd:10/16" in broken_seal.marker
        assert broken_seal.is_valid is False


class TestGAD000SealMath:
    """Test the mathematical correctness of GAD-000."""

    def test_37_equals_24_plus_12_plus_1(self):
        """37 = 24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna)."""
        ksetra = 24
        mahajanas = 12
        ksetrajna = 1
        assert ksetra + mahajanas + ksetrajna == 37

    def test_16_equals_12_workers_plus_4_heads(self):
        """16 opcodes = 12 worker opcodes + 4 HEADs."""
        seal = verify_gad000()
        assert seal.worker_opcodes + seal.heads_active == 16

    def test_16_words_equals_16_opcodes(self):
        """16 words of Mahamantra = 16 OpCodes."""
        seal = verify_gad000()
        assert seal.commands_mapped == 16
        assert seal.opcodes_routed == 16
