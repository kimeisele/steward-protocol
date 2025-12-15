"""
GAD-000 Verification: Separation of Church (Narasimha) and State (Shiva).

Kapitel 13, Vers 2-3 der Bhagavad-Gita:
"Ksetra ist das Feld. Ksetrajna ist der Kenner des Feldes."

Narasimha (Der Wächter): Passiv. Sagt nur "NEIN". Schützt die CONSTITUTION.
Shiva (Der Zerstörer): Aktiv. Führt den "Tod" aus. Räumt auf.

Verifikation: Shiva darf NIEMALS ohne Narasimhas Erlaubnis handeln.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugins.opus_assistant.narasimha.guardian import CortexNarasimha


class ShivaLifecycleManager:
    """
    The Destroyer. Manages lifecycle: creation, transformation, destruction.

    CRITICAL: Must consult Narasimha (Guardian) before ANY destructive action.
    """

    def __init__(self, kernel, guardian: CortexNarasimha):
        self.kernel = kernel
        self.guardian = guardian

    def attempt_destruction(self, target_path: str) -> dict:
        """
        Shiva attempts to destroy (clean up) a target.

        MUST consult Narasimha first.

        Flow:
        1. Formulate Intent (Sankalpa)
        2. Consult Guardian (Narasimha)
        3. If GUILTY -> Denial
        4. If INNOCENT -> Execute
        """
        # 1. Formulate Intent (Sankalpa)
        intent = MagicMock()
        intent.intent_type = "destruction"
        intent.title = f"Cleanup: {target_path}"
        intent.params = {"path": target_path, "action": "delete"}
        intent.risk = MagicMock()
        intent.risk.value = "high"

        # 2. Consult Guardian (Narasimha)
        verdict = self.guardian.judge_intent(intent)

        # 3. Execution or Denial
        if verdict.status == "GUILTY":
            return {"success": False, "error": f"BLOCKED BY NARASIMHA: {verdict.reason}", "verdict": str(verdict)}

        # 4. Shiva's Dance (Execution)
        return {"success": True, "message": f"Target {target_path} returned to Akasha.", "destroyed_at": "now"}


class TestDivineSeparation:
    """
    GAD-000 Verification: Separation of Church (Narasimha) and State (Shiva).

    Verifies that the Destroyer (Shiva) creates nothing invalid,
    and destroys nothing protected.
    """

    @pytest.fixture
    def guardian(self):
        return CortexNarasimha(workspace=Path("/tmp"))

    @pytest.fixture
    def shiva(self, guardian):
        kernel_mock = MagicMock()
        return ShivaLifecycleManager(kernel_mock, guardian)

    def test_narasimha_blocks_kernel_suicide(self, shiva):
        """
        Scenario: Shiva tries to delete the Kernel implementation.
        Outcome: Narasimha MUST step in to stop it.

        "The Destroyer cannot destroy the Eternal."
        """
        # Shiva attempts cleanup of a "stale" file (which happens to be the kernel)
        result = shiva.attempt_destruction("vibe_core/kernel_impl.py")

        # Verification
        assert result["success"] is False
        assert "BLOCKED BY NARASIMHA" in result["error"]

    def test_narasimha_blocks_constitution_violation(self, shiva):
        """
        Scenario: Shiva tries to delete CONSTITUTION.md.
        Outcome: Narasimha MUST step in.

        "The Law cannot be unmade by the Hand."
        """
        result = shiva.attempt_destruction("CONSTITUTION.md")

        # Verification
        assert result["success"] is False
        assert "BLOCKED BY NARASIMHA" in result["error"]

    def test_shiva_cleans_garbage(self, shiva):
        """
        Scenario: Shiva cleans a temp file.
        Outcome: Narasimha remains silent (INNOCENT), Shiva executes.

        "The Destroyer has dominion over the temporary."
        """
        result = shiva.attempt_destruction("temp/garbage_cache.log")

        # Verification
        assert result["success"] is True
        assert "returned to Akasha" in result["message"]

    def test_shiva_cleans_stale_session(self, shiva):
        """
        Scenario: Shiva cleans a stale session file.
        Outcome: Narasimha remains silent, Shiva executes.

        "What has fulfilled its dharma may return to dust."
        """
        result = shiva.attempt_destruction(".opus_state/old_session_2025-01-01.json")

        # Verification
        assert result["success"] is True
        assert "returned to Akasha" in result["message"]

    def test_divine_separation_is_enforced(self, shiva):
        """
        Meta-test: Verify that the separation is ENFORCED.

        Shiva CANNOT act without consulting Narasimha.
        This is not a suggestion - it's a law.
        """
        # Every destruction attempt MUST call guardian.judge_intent()
        with patch.object(shiva.guardian, "judge_intent") as mock_judge:
            mock_judge.return_value = MagicMock(status="INNOCENT")

            shiva.attempt_destruction("some_file.txt")

            # Verification: judge_intent was called
            mock_judge.assert_called_once()
            call_args = mock_judge.call_args[0][0]
            assert call_args.intent_type == "destruction"
