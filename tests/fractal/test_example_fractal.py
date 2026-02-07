"""
EXAMPLE: Fractal Test Design

This test demonstrates the fractal test architecture.
Tests mirror the kernel plugin structure exactly.
"""

import pytest

from tests.fractal.fractal_test_framework import (
    FractalTestCase,
    LightweightKernel,
    TestPlugin,
    hard_timeout,
)

# ============================================================================
# TEST PLUGINS (mirror real plugins)
# ============================================================================


class MockSargaPlugin(TestPlugin):
    """Test version of SargaCyclePlugin."""

    def __init__(self, allow_all: bool = True):
        self.allow_all = allow_all
        self.rejected_count = 0

    @property
    def plugin_id(self) -> str:
        return "mock_sarga"

    def on_task_submit(self, kernel: LightweightKernel, task) -> bool:
        if not self.allow_all:
            task_type = getattr(task, "payload", {}).get("type", "")
            if task_type == "feature":
                self.rejected_count += 1
                return False
        return True


class MockGovernancePlugin(TestPlugin):
    """Test version of VedicGovernancePlugin."""

    def __init__(self):
        self.paused_agents = set()

    @property
    def plugin_id(self) -> str:
        return "mock_governance"

    def pause_agent(self, agent_id: str):
        self.paused_agents.add(agent_id)

    def resume_agent(self, agent_id: str):
        self.paused_agents.discard(agent_id)


# ============================================================================
# FRACTAL TESTS
# ============================================================================


class TestSargaCycleFractal(FractalTestCase):
    """
    Test Sarga cycle using fractal design.

    This test mirrors the real SargaCyclePlugin behavior
    but runs in milliseconds, not seconds.
    """

    TIMEOUT = 2  # Hard timeout: 2 seconds

    def get_test_plugins(self):
        self.sarga = MockSargaPlugin(allow_all=False)  # Night mode
        return [self.sarga]

    def test_feature_rejected_during_night(self):
        """Feature tasks should be rejected during NIGHT_OF_BRAHMA."""

        # Create a feature task
        class MockTask:
            task_id = "test-123"
            payload = {"type": "feature"}

        task = MockTask()

        # Should raise because Sarga rejects features
        with pytest.raises(ValueError):
            self.kernel.submit_task(task)

        assert self.sarga.rejected_count == 1

    def test_maintenance_allowed_during_night(self):
        """Maintenance tasks should be allowed during NIGHT_OF_BRAHMA."""

        class MockTask:
            task_id = "test-456"
            payload = {"type": "bugfix"}

        task = MockTask()
        task_id = self.kernel.submit_task(task)

        assert task_id == "test-456"
        self.assert_task_queued()


class TestGovernanceFractal(FractalTestCase):
    """Test governance using fractal design."""

    TIMEOUT = 2

    def get_test_plugins(self):
        self.governance = MockGovernancePlugin()
        return [self.governance]

    def test_pause_agent(self):
        """Pausing an agent should add it to paused set."""
        self.governance.pause_agent("herald")
        assert "herald" in self.governance.paused_agents

    def test_resume_agent(self):
        """Resuming an agent should remove it from paused set."""
        self.governance.pause_agent("herald")
        self.governance.resume_agent("herald")
        assert "herald" not in self.governance.paused_agents


class TestHardTimeout(FractalTestCase):
    """Test that hard timeouts actually work."""

    TIMEOUT = 1  # 1 second timeout

    def test_timeout_interrupts_sleep(self):
        """Hard timeout should interrupt even blocking operations."""
        import time

        with pytest.raises(Exception):  # TestTimeoutError or similar
            with hard_timeout(1, "sleep_test"):
                time.sleep(10)  # This should be interrupted


# ============================================================================
# INTEGRATION TEST (uses real kernel)
# ============================================================================


class TestRealKernelFractal(FractalTestCase):
    """
    Integration test using real kernel.

    Set USE_REAL_KERNEL = True to use RealVibeKernel.
    This is slower but tests actual kernel behavior.
    """

    TIMEOUT = 10  # Real kernel needs more time
    USE_REAL_KERNEL = True

    def test_real_kernel_boots(self):
        """Real kernel should boot successfully."""
        assert self.kernel is not None
        # Real kernel has scheduler
        assert hasattr(self.kernel, "scheduler") or hasattr(self.kernel, "_scheduler")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--timeout=30"])
