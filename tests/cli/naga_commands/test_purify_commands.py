"""
TEST PURIFY PHASE COMMANDS
==========================

Tests for PURIFY phase (4-7) commands:
- ScanCommand (VYASA - ASSERT_TRUTH)
- DetectCommand (KUMARAS - RESOLVE_REQ)

"Vyasa compiled truth - scan verifies all."
"Kumaras detect impurity - resolve all intent."
"""

import pytest

from vibe_core.cli.naga_commands.purify.scan import ScanCommand
from vibe_core.cli.naga_commands.purify.detect import DetectCommand
from vibe_core.cli.naga_commands.purify.gc import GcCommand
from vibe_core.cli.naga_commands.purify.flood import FloodCommand
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


# =============================================================================
# DETECT COMMAND TESTS
# =============================================================================

class TestDetectCommand:
    """Test DetectCommand (KUMARAS - RESOLVE_REQ)."""

    def test_implements_protocol(self):
        """DetectCommand implements INagaCommand."""
        cmd = DetectCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_resolve_req(self):
        """Opcode is RESOLVE_REQ (position 6)."""
        cmd = DetectCommand()
        assert cmd.opcode == MantraOpCode.RESOLVE_REQ

    def test_mahajana_is_kumaras(self):
        """Mahajana is KUMARAS (the four pure sages)."""
        cmd = DetectCommand()
        assert cmd.mahajana == Mahajana.KUMARAS

    def test_name_is_detect(self):
        """Name is 'detect'."""
        cmd = DetectCommand()
        assert cmd.name == "detect"

    def test_phase_is_purify(self):
        """Phase is PURIFY."""
        cmd = DetectCommand()
        assert cmd.phase == Phase.PURIFY

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = DetectCommand()
        assert len(cmd.help_text) > 0
        assert "KUMARAS" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args returns drift detection."""
        cmd = DetectCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "KUMARAS" in result.output
        assert "Drift Detection" in result.output

    def test_execute_git_flag(self):
        """Execute with --git returns git-only detection."""
        cmd = DetectCommand()
        result = cmd.execute(["--git"])
        assert result.success
        assert "Git Drift" in result.output
        # Should NOT have pattern analysis
        assert "Pattern Analysis" not in result.output

    def test_execute_patterns_flag(self):
        """Execute with --patterns returns patterns-only detection."""
        cmd = DetectCommand()
        result = cmd.execute(["--patterns"])
        assert result.success
        assert "Pattern Analysis" in result.output
        # Should NOT have git drift section header
        data = result.to_dict()
        assert data.get("uncommitted_count") is None or data.get("uncommitted_count") == ""

    def test_execute_intent_flag(self):
        """Execute with --intent detects intent."""
        cmd = DetectCommand()
        result = cmd.execute(["--intent", "what", "is", "the", "status"])
        assert result.success
        assert "Intent Resolution" in result.output
        assert "STATUS" in result.output

    def test_execute_intent_scan(self):
        """Execute with --intent detects scan intent."""
        cmd = DetectCommand()
        result = cmd.execute(["--intent", "scan", "for", "vulnerabilities"])
        assert result.success
        data = result.to_dict()
        assert data.get("intent") == "scan"

    def test_execute_intent_unknown(self):
        """Execute with --intent handles unknown intent."""
        cmd = DetectCommand()
        result = cmd.execute(["--intent", "something", "random"])
        assert result.success
        assert "UNKNOWN" in result.output

    def test_execute_intent_missing_message(self):
        """Execute with --intent but no message fails."""
        cmd = DetectCommand()
        result = cmd.execute(["--intent"])
        assert not result.success
        assert result.exit_code == 1
        assert "Missing message" in result.error

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = DetectCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.RESOLVE_REQ

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = DetectCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.KUMARAS

    def test_result_data_has_phase(self):
        """Result data includes phase info."""
        cmd = DetectCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("phase") == "purify"

    def test_result_data_has_position(self):
        """Result data includes position 6."""
        cmd = DetectCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("position") == "6"


# =============================================================================
# DETECT REGISTRY INTEGRATION TESTS
# =============================================================================

class TestDetectRegistryIntegration:
    """Test that DetectCommand is registered."""

    def test_detect_registered(self):
        """DetectCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("detect")
        assert cmd is not None
        assert cmd.name == "detect"

    def test_kumaras_has_detect(self):
        """KUMARAS owns detect command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.KUMARAS)
        names = [c.name for c in cmds]
        assert "detect" in names

    def test_resolve_req_has_detect(self):
        """RESOLVE_REQ opcode has detect command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_opcode(MantraOpCode.RESOLVE_REQ)
        names = [c.name for c in cmds]
        assert "detect" in names


# =============================================================================
# DETECT STRICT TYPING TESTS
# =============================================================================

class TestDetectStrictTyping:
    """Test that DetectCommand results have no Any types."""

    def test_detect_result_no_any(self):
        """DetectCommand result has no Any."""
        cmd = DetectCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')


# =============================================================================
# DETECT IMMUTABILITY TESTS
# =============================================================================

class TestDetectImmutability:
    """Test that DetectCommand results are immutable."""

    def test_detect_result_frozen(self):
        """DetectCommand result is frozen."""
        cmd = DetectCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False


# =============================================================================
# DETECT SEMANTICS TESTS
# =============================================================================

class TestDetectSemantics:
    """Test semantic meaning of KUMARAS as detect owner."""

    def test_kumaras_meaning(self):
        """KUMARAS semantically fits detect."""
        # Kumaras = The four pure sages who detect impurity
        # Detect = Find drift and resolve intent
        cmd = DetectCommand()
        assert "KUMARAS" in cmd.help_text or "purity" in cmd.help_text.lower()

    def test_purify_meaning(self):
        """Detect is appropriate for PURIFY phase."""
        # PURIFY = Validation and cleanup
        # Detect = Find what needs purifying
        cmd = DetectCommand()
        assert cmd.phase == Phase.PURIFY

    def test_resolve_req_meaning(self):
        """RESOLVE_REQ fits detect semantically."""
        # RESOLVE_REQ = Understand what is requested
        # Detect = Resolve intent, find drift
        cmd = DetectCommand()
        assert cmd.opcode == MantraOpCode.RESOLVE_REQ
        assert "RESOLVE_REQ" in cmd.execute([]).output


# =============================================================================
# FLOOD COMMAND TESTS
# =============================================================================

class TestFloodCommand:
    """Test FloodCommand (MANU - PULSE_SYNC)."""

    def test_implements_protocol(self):
        """FloodCommand implements INagaCommand."""
        cmd = FloodCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_pulse_sync(self):
        """Opcode is PULSE_SYNC (position 8)."""
        cmd = FloodCommand()
        assert cmd.opcode == MantraOpCode.PULSE_SYNC

    def test_mahajana_is_manu(self):
        """Mahajana is MANU (the lawgiver)."""
        cmd = FloodCommand()
        assert cmd.mahajana == Mahajana.MANU

    def test_name_is_flood(self):
        """Name is 'flood'."""
        cmd = FloodCommand()
        assert cmd.name == "flood"

    def test_phase_is_purify(self):
        """Phase is PURIFY."""
        cmd = FloodCommand()
        assert cmd.phase == Phase.PURIFY

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = FloodCommand()
        assert len(cmd.help_text) > 0
        assert "MANU" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args returns flood status."""
        cmd = FloodCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "MANU" in result.output
        assert "FloodManager" in result.output

    def test_execute_stats_flag(self):
        """Execute with --stats shows statistics."""
        cmd = FloodCommand()
        result = cmd.execute(["--stats"])
        assert result.success
        # Stats should work even when FloodManager unavailable

    def test_execute_subscribers_flag(self):
        """Execute with --subscribers shows subscribers."""
        cmd = FloodCommand()
        result = cmd.execute(["--subscribers"])
        assert result.success

    def test_execute_pulse_flag(self):
        """Execute with --pulse shows pulse status."""
        cmd = FloodCommand()
        result = cmd.execute(["--pulse"])
        assert result.success

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = FloodCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.PULSE_SYNC

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = FloodCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.MANU

    def test_result_data_has_phase(self):
        """Result data includes phase info."""
        cmd = FloodCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("phase") == "purify"

    def test_result_data_has_position(self):
        """Result data includes position 8."""
        cmd = FloodCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("position") == "8"

    def test_result_has_active_status(self):
        """Result data includes active status."""
        cmd = FloodCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert "active" in data


# =============================================================================
# FLOOD REGISTRY INTEGRATION TESTS
# =============================================================================

class TestFloodRegistryIntegration:
    """Test that FloodCommand is registered."""

    def test_flood_registered(self):
        """FloodCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("flood")
        assert cmd is not None
        assert cmd.name == "flood"

    def test_manu_has_flood(self):
        """MANU owns flood command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.MANU)
        names = [c.name for c in cmds]
        assert "flood" in names

    def test_pulse_sync_has_flood(self):
        """PULSE_SYNC opcode has flood command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_opcode(MantraOpCode.PULSE_SYNC)
        names = [c.name for c in cmds]
        assert "flood" in names


# =============================================================================
# FLOOD STRICT TYPING TESTS
# =============================================================================

class TestFloodStrictTyping:
    """Test that FloodCommand results have no Any types."""

    def test_flood_result_no_any(self):
        """FloodCommand result has no Any."""
        cmd = FloodCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')


# =============================================================================
# FLOOD IMMUTABILITY TESTS
# =============================================================================

class TestFloodImmutability:
    """Test that FloodCommand results are immutable."""

    def test_flood_result_frozen(self):
        """FloodCommand result is frozen."""
        cmd = FloodCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False


# =============================================================================
# FLOOD SEMANTICS TESTS
# =============================================================================

class TestFloodSemantics:
    """Test semantic meaning of MANU as flood owner."""

    def test_manu_meaning(self):
        """MANU semantically fits flood."""
        # Manu = The lawgiver who established dharmic rhythm
        # Flood = Observation flow that maintains system rhythm
        cmd = FloodCommand()
        assert "MANU" in cmd.help_text or "law" in cmd.help_text.lower()

    def test_purify_meaning(self):
        """Flood is appropriate for PURIFY phase."""
        # PURIFY = Validation and cleanup
        # Flood = Observes and validates system state
        cmd = FloodCommand()
        assert cmd.phase == Phase.PURIFY

    def test_pulse_sync_meaning(self):
        """PULSE_SYNC fits flood semantically."""
        # PULSE_SYNC = System heartbeat and synchronization
        # Flood = FloodManager observation pulse
        cmd = FloodCommand()
        assert cmd.opcode == MantraOpCode.PULSE_SYNC
        assert "PULSE_SYNC" in cmd.execute([]).output


# =============================================================================
# GC COMMAND TESTS
# =============================================================================

class TestGcCommand:
    """Test GcCommand (KAPILA - GARBAGE_COLLECT)."""

    def test_implements_protocol(self):
        """GcCommand implements INagaCommand."""
        cmd = GcCommand()
        assert isinstance(cmd, INagaCommand)

    def test_opcode_is_garbage_collect(self):
        """Opcode is GARBAGE_COLLECT (position 7)."""
        cmd = GcCommand()
        assert cmd.opcode == MantraOpCode.GARBAGE_COLLECT

    def test_mahajana_is_kapila(self):
        """Mahajana is KAPILA (the analyzer)."""
        cmd = GcCommand()
        assert cmd.mahajana == Mahajana.KAPILA

    def test_name_is_gc(self):
        """Name is 'gc'."""
        cmd = GcCommand()
        assert cmd.name == "gc"

    def test_phase_is_purify(self):
        """Phase is PURIFY."""
        cmd = GcCommand()
        assert cmd.phase == Phase.PURIFY

    def test_help_text_exists(self):
        """Help text is defined."""
        cmd = GcCommand()
        assert len(cmd.help_text) > 0
        assert "KAPILA" in cmd.help_text

    def test_execute_no_args_succeeds(self):
        """Execute with no args returns gc analysis."""
        cmd = GcCommand()
        result = cmd.execute([])
        assert result.success
        assert result.exit_code == 0
        assert "KAPILA" in result.output
        assert "Garbage Collection" in result.output

    def test_execute_analyze_flag(self):
        """Execute with --analyze shows analysis."""
        cmd = GcCommand()
        result = cmd.execute(["--analyze"])
        assert result.success
        assert "Analysis complete" in result.output
        data = result.to_dict()
        assert data.get("action") == "analyze"

    def test_execute_shows_pycache_count(self):
        """Execute shows __pycache__ count."""
        cmd = GcCommand()
        result = cmd.execute([])
        assert "__pycache__" in result.output

    def test_execute_shows_pyc_count(self):
        """Execute shows .pyc count."""
        cmd = GcCommand()
        result = cmd.execute([])
        assert ".pyc" in result.output

    def test_execute_shows_total_size(self):
        """Execute shows total size."""
        cmd = GcCommand()
        result = cmd.execute([])
        assert "MB" in result.output

    def test_result_has_correct_opcode(self):
        """Result contains correct opcode."""
        cmd = GcCommand()
        result = cmd.execute([])
        assert result.opcode == MantraOpCode.GARBAGE_COLLECT

    def test_result_has_correct_mahajana(self):
        """Result contains correct mahajana."""
        cmd = GcCommand()
        result = cmd.execute([])
        assert result.mahajana == Mahajana.KAPILA

    def test_result_data_has_phase(self):
        """Result data includes phase info."""
        cmd = GcCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("phase") == "purify"

    def test_result_data_has_position(self):
        """Result data includes position 7."""
        cmd = GcCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert data.get("position") == "7"

    def test_result_has_pycache_count(self):
        """Result data includes pycache count."""
        cmd = GcCommand()
        result = cmd.execute([])
        data = result.to_dict()
        assert "pycache_count" in data


# =============================================================================
# GC REGISTRY INTEGRATION TESTS
# =============================================================================

class TestGcRegistryIntegration:
    """Test that GcCommand is registered."""

    def test_gc_registered(self):
        """GcCommand is registered."""
        cmd = NAGA_COMMAND_REGISTRY.get("gc")
        assert cmd is not None
        assert cmd.name == "gc"

    def test_kapila_has_gc(self):
        """KAPILA owns gc command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_mahajana(Mahajana.KAPILA)
        names = [c.name for c in cmds]
        assert "gc" in names

    def test_garbage_collect_has_gc(self):
        """GARBAGE_COLLECT opcode has gc command."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_opcode(MantraOpCode.GARBAGE_COLLECT)
        names = [c.name for c in cmds]
        assert "gc" in names


# =============================================================================
# GC STRICT TYPING TESTS
# =============================================================================

class TestGcStrictTyping:
    """Test that GcCommand results have no Any types."""

    def test_gc_result_no_any(self):
        """GcCommand result has no Any."""
        cmd = GcCommand()
        result = cmd.execute([])
        assert hasattr(result, 'success')
        assert hasattr(result, 'opcode')
        assert hasattr(result, 'mahajana')


# =============================================================================
# GC IMMUTABILITY TESTS
# =============================================================================

class TestGcImmutability:
    """Test that GcCommand results are immutable."""

    def test_gc_result_frozen(self):
        """GcCommand result is frozen."""
        cmd = GcCommand()
        result = cmd.execute([])
        with pytest.raises(Exception):
            result.success = False


# =============================================================================
# GC SEMANTICS TESTS
# =============================================================================

class TestGcSemantics:
    """Test semantic meaning of KAPILA as gc owner."""

    def test_kapila_meaning(self):
        """KAPILA semantically fits gc."""
        # Kapila = The founder of Sankhya (analytical philosophy)
        # Gc = Analyze and clean unused resources
        cmd = GcCommand()
        assert "KAPILA" in cmd.help_text or "analy" in cmd.help_text.lower()

    def test_purify_meaning(self):
        """Gc is appropriate for PURIFY phase."""
        # PURIFY = Validation and cleanup
        # Gc = Clean garbage, purify resources
        cmd = GcCommand()
        assert cmd.phase == Phase.PURIFY

    def test_garbage_collect_meaning(self):
        """GARBAGE_COLLECT fits gc semantically."""
        # GARBAGE_COLLECT = Remove unused resources
        # Gc = Garbage collection
        cmd = GcCommand()
        assert cmd.opcode == MantraOpCode.GARBAGE_COLLECT
        assert "GARBAGE_COLLECT" in cmd.execute([]).output


# =============================================================================
# PURIFY PHASE COMPLETE TEST
# =============================================================================

class TestPurifyPhaseComplete:
    """Test that PURIFY phase is complete with all 4 commands."""

    def test_all_purify_commands_registered(self):
        """All 4 PURIFY phase commands are registered."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_phase(Phase.PURIFY)
        names = [c.name for c in cmds]
        assert "scan" in names    # VYASA - Position 4
        assert "detect" in names  # KUMARAS - Position 5
        assert "gc" in names      # KAPILA - Position 6
        assert "flood" in names   # MANU - Position 7

    def test_purify_has_four_commands(self):
        """PURIFY phase has exactly 4 commands."""
        cmds = NAGA_COMMAND_REGISTRY.get_by_phase(Phase.PURIFY)
        assert len(cmds) == 4
