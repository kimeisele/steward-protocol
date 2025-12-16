"""
OPUS-087 E2E Test: Prove OPUS.md actually gets written.

This test verifies that the entire PRANA flow works end-to-end:
1. OpusAssistantPlugin.on_pulse() registers an update_doc mutation
2. PranaOrchestrator commits the mutation
3. The update_doc handler writes the content to the file
4. OPUS.md content is updated with new timestamp
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest


class TestPranaE2EOpusUpdate:
    """End-to-end test proving OPUS.md actually gets updated."""

    def test_update_doc_handler_writes_file(self, tmp_path):
        """Test that update_doc handler actually writes to filesystem."""
        # Setup
        import os

        from vibe_core.prana_orchestrator import (
            PranaOrchestrator,
            PulseTransaction,
            StateMutation,
        )

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            orchestrator = PranaOrchestrator(kernel=None)
            transaction = PulseTransaction()

            # Register handlers
            orchestrator._register_default_handlers(transaction)

            # Register a mutation
            test_content = f"# Test OPUS\n\nLast Pulse: {datetime.utcnow().isoformat()}"
            mutation = StateMutation(
                plugin_id="test_plugin",
                action="update_doc",
                target="OPUS.md",
                payload={"content": test_content},
            )
            transaction.register(mutation)

            # Commit
            success, failure = transaction.commit()

            # Verify
            assert success == 1, f"Expected 1 success, got {success}"
            assert failure == 0, f"Expected 0 failures, got {failure}"

            opus_path = tmp_path / "OPUS.md"
            assert opus_path.exists(), "OPUS.md should have been created"

            written_content = opus_path.read_text()
            assert "Last Pulse:" in written_content, "Content should have Last Pulse"
            assert written_content == test_content, "Content should match exactly"

        finally:
            os.chdir(original_cwd)

    def test_opus_assistant_plugin_on_pulse_e2e(self, tmp_path):
        """Test full OpusAssistantPlugin.on_pulse() integration."""
        from vibe_core.prana_orchestrator import (
            PranaOrchestrator,
            PulseTransaction,
        )

        # Try to import OpusAssistantPlugin
        try:
            from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin
        except ImportError:
            pytest.skip("OpusAssistantPlugin not available")

        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create minimal workspace structure
            (tmp_path / ".git").mkdir()  # Fake git dir

            # Initialize plugin
            plugin = OpusAssistantPlugin()

            # Create transaction with handlers
            orchestrator = PranaOrchestrator(kernel=None)
            transaction = PulseTransaction()
            orchestrator._register_default_handlers(transaction)

            # Call on_pulse
            result = plugin.on_pulse(kernel=None, transaction=transaction)

            # Check result
            assert result.status.value == "ok", f"on_pulse failed: {result.error_message}"

            # Check mutations were registered
            assert len(transaction.mutations) > 0, "Should have registered mutations"
            assert transaction.mutations[0].action == "update_doc"
            assert transaction.mutations[0].target == "OPUS.md"

            # Commit and verify file write
            success, failure = transaction.commit()

            opus_path = tmp_path / "OPUS.md"
            if success > 0:
                assert opus_path.exists(), "OPUS.md should exist after commit"
                content = opus_path.read_text()
                assert len(content) > 0, "OPUS.md should have content"
                print(f"\n✅ PROOF: OPUS.md created with {len(content)} chars")
                print(f"   First 200 chars: {content[:200]}...")

        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
