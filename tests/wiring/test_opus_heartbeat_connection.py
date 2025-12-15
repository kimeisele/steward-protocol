"""
GAD-000 Verification: Does the Heartbeat actually refresh OPUS.md?

User Hypothesis: "No, it's parallel structures."
Test: Prove it.
"""

import os
import time
from unittest.mock import patch

import pytest


class TestOpusHeartbeatWiring:
    """
    Critical Test: Is OPUS.md actually updated by the Heartbeat?

    Current Status: FAILING (Expected)
    Reason: heartbeat.py doesn't call opus_assistant to refresh OPUS.md
    """

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a fake workspace with OPUS.md"""
        # Setup TASKS.md (Heartbeat needs this)
        (tmp_path / "TASKS.md").write_text("# Tasks\n- [ ] Do setup")

        # Setup OPUS.md (old)
        opus_path = tmp_path / "OPUS.md"
        opus_path.write_text("# OPUS State\nLast Updated: 1999-01-01")

        # Set mtime to the past
        old_time = time.time() - 3600
        os.utime(opus_path, (old_time, old_time))

        return tmp_path

    def test_heartbeat_refreshes_opus(self, workspace):
        """
        THE CRITICAL TEST:
        When the Heartbeat pulses, OPUS.md MUST be updated.

        Current Result: FAILS (OPUS.md is never touched)
        """
        # Import here to avoid issues if heartbeat isn't available
        try:
            from scripts.heartbeat import HeartbeatEngine
        except ImportError:
            pytest.skip("HeartbeatEngine not available")

        with (
            patch("scripts.heartbeat.TaskManager"),
            patch("scripts.heartbeat.SQLiteLedger"),
            patch("scripts.heartbeat.UnifiedRouter"),
            patch("scripts.heartbeat.CognitiveKernel") as MockKernel,
        ):
            # Setup Mock MANAS
            mock_manas = MockKernel.return_value
            mock_manas.think.return_value = []  # No intents, just routine

            engine = HeartbeatEngine(workspace)

            # Remember the time before the pulse
            opus_path = workspace / "OPUS.md"
            mtime_before = opus_path.stat().st_mtime

            # 💓 PULSE
            engine.pulse()

            # Check
            mtime_after = opus_path.stat().st_mtime

            # DIAGNOSIS:
            if mtime_after == mtime_before:
                pytest.fail(
                    "❌ FAILURE: OPUS.md was NOT touched by Heartbeat!\n"
                    "Parallel Structures confirmed.\n"
                    "heartbeat.py updates TASKS.md but not OPUS.md.\n"
                    "Fix: Add self._refresh_opus_md() to pulse()"
                )
            else:
                print("✅ SUCCESS: OPUS.md was updated by Heartbeat.")
