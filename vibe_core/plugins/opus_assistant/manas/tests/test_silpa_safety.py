"""
GAD-000 Verification: The Platinum Protocol.

"No surgery without anesthesia. No refactoring without tests."

This test suite verifies that Silpa (Self-Architect) cannot break the system.
The Platinum Protocol ensures:
1. Pre-Gate Check: Tests must pass before refactoring
2. Refactoring: Code is transformed
3. Post-Gate Check: Tests must still pass after refactoring
4. Rollback Reflex: If post-gate fails, original code is restored
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
    RefactorRisk,
    RefactorType,
    SilpaArchitect,
    SilpaPlan,
    SilpaRefactoring,
    SilpaTestResult,
)


class TestSilpaPlatinumProtocol:
    """
    GAD-000 Verification: The Platinum Protocol.

    "No surgery without anesthesia. No refactoring without tests."
    """

    @pytest.fixture
    def architect(self):
        with patch("vibe_core.plugins.opus_assistant.manas.cortex.silpa.SilpaAuditor") as mock_auditor:
            arch = SilpaArchitect(workspace=Path("/tmp/vibe_test"))
            arch._auditor = mock_auditor.return_value
            # Mock the transformer to just return "new code"
            arch._transformer = MagicMock()
            arch._transformer.transform.return_value = ("print('refactored')", [])
            return arch

    def test_platinum_protocol_success(self, architect):
        """
        Verify the Happy Path:
        Green Tests -> Refactor -> Green Tests -> Success
        """
        # Mock PRE-GATE (Green)
        architect._auditor.run_tests.side_effect = [
            SilpaTestResult(True, 0, 5, 5, 0, "", "", 100),  # Pre
            SilpaTestResult(True, 0, 5, 5, 0, "", "", 100),  # Post
        ]

        # Setup Plan
        refactoring = SilpaRefactoring(
            target_file=Path("test_file.py"),
            refactor_type=RefactorType.RENAME_VARIABLE,
            description="Rename x to y",
            instructions="Target: x",
        )
        plan = SilpaPlan(
            refactoring=refactoring,
            original_code="print('original')",
            original_hash="abc",
            planned_code="print('refactored')",
            risk_level=RefactorRisk.SAFE,
            affected_functions=[],
            affected_classes=[],
            estimated_impact="Low",
            approval_required=False,
        )

        # Mock File Ops
        with (
            patch("pathlib.Path.write_text") as mock_write,
            patch("pathlib.Path.read_text", return_value="print('original')"),
            patch("shutil.copy2") as mock_backup,
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            result = architect.execute(plan)

            # Verification
            assert result.success is True
            assert any("PRE-GATE PASSED" in entry for entry in result.audit_trail)
            assert any("POST-GATE PASSED" in entry for entry in result.audit_trail)
            mock_write.assert_called_with("print('refactored')")
            mock_backup.assert_called()  # Backup created
            mock_unlink.assert_called()  # Backup cleaned up

    def test_platinum_protocol_rollback(self, architect):
        """
        Verify the Pratyaya Reflex (Rollback):
        Green Tests -> Refactor -> RED Tests -> ROLLBACK
        """
        # Mock PRE-GATE (Green) then POST-GATE (Red)
        architect._auditor.run_tests.side_effect = [
            SilpaTestResult(True, 0, 5, 5, 0, "", "", 100),  # Pre (Pass)
            SilpaTestResult(False, 1, 5, 4, 1, "Error", "Error", 100),  # Post (Fail)
        ]

        refactoring = SilpaRefactoring(
            target_file=Path("test_file.py"),
            refactor_type=RefactorType.RENAME_VARIABLE,
            description="Break everything",
            instructions="Target: x",
        )
        plan = SilpaPlan(
            refactoring=refactoring,
            original_code="print('original')",
            original_hash="abc",
            planned_code="print('broken')",
            risk_level=RefactorRisk.SAFE,
            affected_functions=[],
            affected_classes=[],
            estimated_impact="Low",
            approval_required=False,
        )

        # Mock File Ops
        with (
            patch("pathlib.Path.write_text") as mock_write,
            patch("shutil.copy2") as mock_copy,
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            result = architect.execute(plan)

            # Verification
            assert result.success is False
            assert result.rollback_performed is True
            assert any("POST-GATE FAILED" in entry for entry in result.audit_trail)
            assert any("ROLLBACK" in entry for entry in result.audit_trail)

            # Verify rollback copy (backup -> target)
            # The second copy call is the rollback
            assert mock_copy.call_count == 2

    def test_platinum_protocol_pre_gate_fails(self, architect):
        """
        Verify the Pre-Gate Check:
        RED Tests -> ABORT (no refactoring attempted)
        """
        # Mock PRE-GATE (Red) - tests already failing
        architect._auditor.run_tests.return_value = SilpaTestResult(
            False, 2, 5, 3, 2, "Existing failures", "Existing failures", 100
        )

        refactoring = SilpaRefactoring(
            target_file=Path("test_file.py"),
            refactor_type=RefactorType.RENAME_VARIABLE,
            description="Attempt refactor",
            instructions="Target: x",
        )
        plan = SilpaPlan(
            refactoring=refactoring,
            original_code="print('original')",
            original_hash="abc",
            planned_code="print('refactored')",
            risk_level=RefactorRisk.SAFE,
            affected_functions=[],
            affected_classes=[],
            estimated_impact="Low",
            approval_required=False,
        )

        result = architect.execute(plan)

        # Verification
        assert result.success is False
        assert any("PRE-GATE FAILED" in entry for entry in result.audit_trail)
