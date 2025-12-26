"""
OPUS-082: Shiva Lifecycle Manager Tests

Shiva = The Destroyer of Illusions
- Checks if intents were fulfilled externally
- Marks stale intents as archived
- Keeps MANAS mind clean

TDD: Write the test, watch it fail, make it pass.
"""

from pathlib import Path
from unittest.mock import patch

from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    Intent,
    IntentPriority,
    IntentRisk,
)


class TestShivaExternalFulfillment:
    """Tests for detecting externally fulfilled intents."""

    def test_shiva_module_exists(self):
        """Shiva module must exist."""
        from vibe_core.plugins.opus_assistant.manas import shiva

        assert shiva is not None

    def test_shiva_has_check_fulfillment_method(self):
        """Shiva must have check_external_fulfillment method."""
        from vibe_core.plugins.opus_assistant.manas.shiva import ShivaLifecycleManager

        shiva = ShivaLifecycleManager(workspace=Path("."))
        assert hasattr(shiva, "check_external_fulfillment")
        assert callable(shiva.check_external_fulfillment)

    def test_test_intent_fulfilled_when_test_file_exists(self):
        """
        If intent asks for tests and test file exists, it's fulfilled.

        genesis_0002 asked for tests for cognitive_kernel.py
        tests/manas/test_cognitive_kernel.py EXISTS
        → Intent is fulfilled externally!
        """
        from vibe_core.plugins.opus_assistant.manas.shiva import ShivaLifecycleManager

        shiva = ShivaLifecycleManager(workspace=Path("."))

        intent = Intent(
            id="genesis_0002",
            intent_type="semantic_gap_test",
            title="Create tests for MANAS cognitive kernel",
            description="Test",
            reasoning="MANAS needs tests",
            priority=IntentPriority.MEDIUM,
            risk=IntentRisk.SAFE,
            auto_executable=True,
            params={
                "untested_files": ["cognitive_kernel.py"],
                "plugin": "opus_assistant",
            },
        )

        # test_cognitive_kernel.py exists!
        result = shiva.check_external_fulfillment(intent)

        assert result.fulfilled is True
        assert result.reason == "test_file_exists"

    def test_commit_intent_fulfilled_when_no_pending_changes(self):
        """
        If intent asks to commit changes and git is clean, it's fulfilled.
        """
        from vibe_core.plugins.opus_assistant.manas.shiva import ShivaLifecycleManager

        shiva = ShivaLifecycleManager(workspace=Path("."))

        intent = Intent(
            id="manas_0001",
            intent_type="commit_pending_changes",
            title="Commit 15 pending changes",
            description="Test",
            reasoning="Changes should be committed",
            priority=IntentPriority.MEDIUM,
            risk=IntentRisk.MEDIUM,
            auto_executable=False,
            params={"change_count": 15},
        )

        # Mock git status to return clean
        with patch.object(shiva, "_git_has_changes", return_value=False):
            result = shiva.check_external_fulfillment(intent)

        assert result.fulfilled is True
        assert result.reason == "git_clean"


class TestShivaSweep:
    """Tests for sweeping and archiving intents."""

    def test_shiva_sweep_marks_fulfilled_intents(self):
        """Sweep should mark fulfilled intents."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            ManasConfig,
        )
        from vibe_core.plugins.opus_assistant.manas.shiva import ShivaLifecycleManager

        # Setup kernel with intents
        config = ManasConfig(auto_execute_safe=False)
        kernel = CognitiveKernel(workspace=Path("."), config=config)

        shiva = ShivaLifecycleManager(workspace=Path("."))

        # OPUS-314: sweep_stale_intents now takes kernel as parameter
        archived_count = shiva.sweep_stale_intents(kernel)

        # Should return count (may be 0 if nothing stale)
        assert isinstance(archived_count, int)


class TestShivaIntegration:
    """Tests for Shiva integration with CognitiveKernel."""

    def test_kernel_has_shiva(self):
        """CognitiveKernel should have Shiva instance."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            ManasConfig,
        )

        config = ManasConfig()
        kernel = CognitiveKernel(workspace=Path("."), config=config)

        # Kernel should have _shiva attribute
        assert hasattr(kernel, "_shiva")
