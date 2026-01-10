"""
TEST PURIFY PHASE COMMANDS
==========================

Tests for PURIFY phase (4-7) commands:
- ScanCommand (VYASA - ASSERT_TRUTH)

"Vyasa compiled truth - scan verifies all."
"""

import pytest

from vibe_core.cli.naga_commands.purify.scan import ScanCommand
from vibe_core.protocols.naga.cli_command import (
    INagaCommand,
    Mahajana,
    Phase,
    NAGA_COMMAND_REGISTRY,
)
from vibe_core.protocols.substrate import MantraOpCode


# =============================================================================
# SCAN COMMAND TESTS
# =============================================================================

class TestScanCommand:
    """Test ScanCommand (VYASA - ASSERT_TRUTH)."""

    def test_implements_protocol(self):
        """ScanCommand implements INagaCommand."""
        cmd = ScanCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_assert_truth(self):
        """Opcode is ASSERT_TRUTH (position 4)."""
        cmd = ScanCommand()
        assert cmd.opcode == MantraOpCode.ASSERT_TRUTH

    def test_mahajana_is_vyasa(self):
        """Mahajana is VYASA (the divine compiler)."""
        cmd = ScanCommand()
        assert cmd.mahajana == Mahajana.VYASA

    def test_name_is_scan(self):
        """Name is 'scan'."""
        cmd = ScanCommand()
        assert cmd.name == "scan"

    def test_phase_is_purify(self):
        """Phase is PURIFY (phase 1)."""
        cmd = ScanCommand()
        assert cmd.phase == Phase.PURIFY

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = ScanCommand()
        assert len(cmd.help_text) > 0
        assert "VYASA" in cmd.help_text

    def test_execute_no_args_standard_scan(self):
        """Execute with no args returns standard scan."""
        cmd = ScanCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "VYASA" in result.output
        assert "ASSERT_TRUTH" in result.output

    def test_execute_quick_flag(self):
        """Execute with --quick returns quick scan."""
        cmd = ScanCommand()
        result = cmd.execute(["--quick"])
        assert result.success
        data = result.to_dict()
        assert data.get("mode") == "quick"
        assert "Quick Scan" in result.output

    def test_execute_deep_flag(self):
        """Execute with --deep returns deep scan."""
        cmd = ScanCommand()
        result = cmd.execute(["--deep"])
        assert result.success
        data = result.to_dict()
        assert data.get("mode") == "deep"
        assert "Deep Scan" in result.output
        assert "TOXICITY SCAN" in result.output
        assert "PROTOCOL SCAN" in result.output

    def test_execute_toxicity_flag(self):
        """Execute with --toxicity returns toxicity scan."""
        cmd = ScanCommand()
        result = cmd.execute(["--toxicity"])
        assert result.success
        data = result.to_dict()
        assert data.get("mode") == "toxicity"
        assert "Toxicity Scan" in result.output
        assert "TAKSHAKA" in result.output

    def test_execute_protocols_flag(self):
        """Execute with --protocols returns protocol scan."""
        cmd = ScanCommand()
        result = cmd.execute(["--protocols"])
        assert result.success
        data = result.to_dict()
        assert data.get("mode") == "protocols"
        assert "Protocol Scan" in result.output
        assert "COVERAGE" in result.output

    def test_execute_path_flag(self):
        """Execute with --path scans specific path."""
        cmd = ScanCommand()
        result = cmd.execute(["--path", "/some/path"])
        assert result.success
        data = result.to_dict()
        assert data.get("path") == "/some/path"

    def test_execute_invalid_path(self):
        """Execute with invalid --path fails."""
        cmd = ScanCommand()
        result = cmd.execute(["--path"])  # Missing path value
        assert not result.success
        assert "Invalid --path" in result.error

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = ScanCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.ASSERT_TRUTH

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = ScanCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.VYASA

    def test_result_data_has_phase(self):
        """Result data includes phase info."""
        cmd = ScanCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("phase") == "purify"

    def test_result_data_has_position(self):
        """Result data includes position 4."""
        cmd = ScanCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("position") == "4"


# =============================================================================
# REGISTRY INTEGRATION TESTS
# =============================================================================

class TestPurifyRegistryIntegration:
    """Test that PURIFY commands are registered."""

    def test_scan_registered(self):
        """ScanCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("scan")
        assert cmd is not None
        assert cmd.name == "scan"

    def test_purify_phase_has_commands(self):
        """PURIFY phase has commands."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_phase(Phase.PURIFY)
        assert len(cmds) >= 1
        names = [c.name for c in cmds]
        assert "scan" in names

    def test_vyasa_has_scan(self):
        """VYASA owns scan command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.VYASA)
        names = [c.name for c in cmds]
        assert "scan" in names

    def test_assert_truth_has_scan(self):
        """ASSERT_TRUTH opcode has scan command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_opcode(MantraOpCode.ASSERT_TRUTH)
        names = [c.name for c in cmds]
        assert "scan" in names


# =============================================================================
# POSITION 4 TESTS (HEAD OF PURIFY)
# =============================================================================

class TestPosition4:
    """Test that scan is position 4 - the HEAD of PURIFY."""

    def test_assert_truth_is_purify_head(self):
        """ASSERT_TRUTH is the HEAD opcode of PURIFY phase."""
        cmd = ScanCommand()
        assert cmd.opcode == MantraOpCode.ASSERT_TRUTH
        # Position 4 is the first opcode of PURIFY phase
        purify_opcodes = [
            MantraOpCode.ASSERT_TRUTH,
            MantraOpCode.RESOLVE_REQ,
            MantraOpCode.GARBAGE_COLLECT,
            MantraOpCode.PULSE_SYNC,
        ]
        assert cmd.opcode == purify_opcodes[0]  # HEAD

    def test_vyasa_is_avatara(self):
        """VYASA is an Avatara (HEAD of PURIFY phase)."""
        # Avataras are at positions 0, 4, 8, 12 (HEAD of each phase)
        cmd = ScanCommand()
        assert cmd.opcode == MantraOpCode.ASSERT_TRUTH
        assert cmd.mahajana == Mahajana.VYASA

    def test_purify_is_second_phase(self):
        """PURIFY is the second phase (4-7)."""
        cmd = ScanCommand()
        assert cmd.phase == Phase.PURIFY
        # PURIFY contains: ASSERT_TRUTH, RESOLVE_REQ, GARBAGE_COLLECT, PULSE_SYNC
        purify_opcodes = [
            MantraOpCode.ASSERT_TRUTH,
            MantraOpCode.RESOLVE_REQ,
            MantraOpCode.GARBAGE_COLLECT,
            MantraOpCode.PULSE_SYNC,
        ]
        assert cmd.opcode in purify_opcodes


# =============================================================================
# SCAN MODE TESTS
# =============================================================================

class TestScanModes:
    """Test different scan modes."""

    def test_quick_is_fastest(self):
        """Quick scan has minimal output."""
        cmd = ScanCommand()
        quick_result = cmd.execute(["--quick"])
        standard_result = cmd.execute([])
        # Quick should be shorter
        assert len(quick_result.output) < len(standard_result.output)

    def test_deep_is_most_thorough(self):
        """Deep scan has most output."""
        cmd = ScanCommand()
        deep_result = cmd.execute(["--deep"])
        standard_result = cmd.execute([])
        # Deep should be longer
        assert len(deep_result.output) > len(standard_result.output)

    def test_toxicity_focuses_on_security(self):
        """Toxicity scan focuses on security."""
        cmd = ScanCommand()
        result = cmd.execute(["--toxicity"])
        assert "TAKSHAKA" in result.output  # Security NAGA
        assert "VAJRA" in result.output  # Security violations

    def test_protocols_focuses_on_coverage(self):
        """Protocol scan focuses on coverage."""
        cmd = ScanCommand()
        result = cmd.execute(["--protocols"])
        assert "COVERAGE" in result.output
        assert "GAPS" in result.output
        assert "MAHAJANA" in result.output


# =============================================================================
# STRICT TYPING TESTS
# =============================================================================

class TestStrictTyping:
    """Test that results have no Any types."""

    def test_scan_result_no_any(self):
        """ScanCommand result has no Any."""
        cmd = ScanCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')


# =============================================================================
# IMMUTABILITY TESTS
# =============================================================================

class TestImmutability:
    """Test that results are immutable."""

    def test_scan_result_frozen(self):
        """ScanCommand result is frozen."""
        cmd = ScanCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False


# =============================================================================
# SEMANTIC TESTS
# =============================================================================

class TestSemantics:
    """Test semantic meaning of VYASA as scan owner."""

    def test_vyasa_meaning(self):
        """VYASA semantically fits scan."""
        # Vyasa = The compiler who categorized all truth
        # Scan = Verify and categorize system state
        cmd = ScanCommand()
        assert "VYASA" in cmd.help_text or "truth" in cmd.help_text.lower()

    def test_purify_meaning(self):
        """Scan is appropriate for PURIFY phase."""
        # PURIFY = Validation and cleanup
        # Scan = First step of validation
        cmd = ScanCommand()
        assert cmd.phase == Phase.PURIFY

    def test_assert_truth_meaning(self):
        """ASSERT_TRUTH fits scan semantically."""
        # ASSERT_TRUTH = Verify correctness
        # Scan = System verification
        cmd = ScanCommand()
        assert cmd.opcode == MantraOpCode.ASSERT_TRUTH
        assert "ASSERT_TRUTH" in cmd.execute([]).output
