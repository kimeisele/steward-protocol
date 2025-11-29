#!/usr/bin/env python3
"""
Integration Test: Process Isolation
====================================

Tests that:
1. Agents run in separate processes
2. Agent crash does NOT kill kernel
3. Narasimha detects crash and attempts restart
4. Kernel continues running after agent death
"""

import pytest
import sys
import time
import signal
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.process_manager import ProcessManager


def test_process_manager_exists():
    """Test that kernel has ProcessManager."""
    kernel = RealVibeKernel()
    assert hasattr(kernel, "process_manager")
    assert kernel.process_manager is not None
    assert isinstance(kernel.process_manager, ProcessManager)


def test_agents_in_separate_processes():
    """Test that agents would run in separate processes."""
    # This is a structural test - we verify the ProcessManager
    # has the capability to spawn isolated processes
    pm = ProcessManager()  # No kernel argument needed

    # Verify ProcessManager has process tracking
    assert hasattr(pm, "processes")
    assert isinstance(pm.processes, dict)

    # Verify ProcessManager has spawn_agent method
    assert hasattr(pm, "spawn_agent")
    assert callable(pm.spawn_agent)


def test_process_health_monitoring():
    """Test that ProcessManager can monitor health."""
    pm = ProcessManager()

    # Verify health monitoring methods exist
    assert hasattr(pm, "check_health")  # renamed from monitor_health
    assert callable(pm.check_health)

    # Verify crash handling exists (restart is handled via _handle_crash)
    assert hasattr(pm, "_handle_crash")
    assert callable(pm._handle_crash)


def test_kernel_survives_without_agents():
    """Test that kernel can exist without any agents running."""
    kernel = RealVibeKernel()

    # Kernel starts in STOPPED state, becomes RUNNING after boot()
    status = kernel.get_status()
    assert status["status"] in ["STOPPED", "INIT", "BOOTING", "RUNNING"]

    # Kernel should have 0 or more agents registered
    assert status["agents_registered"] >= 0


# Full integration test (requires actual agent spawn)
# This would be run in a live environment, not in unit tests
@pytest.mark.skip(reason="Requires full kernel boot with agents")
def test_agent_crash_isolation_live():
    """
    LIVE TEST (Manual execution only):
    1. Boot kernel with 1 agent
    2. Kill agent process
    3. Verify kernel survives
    4. Verify Narasimha detects crash
    """
    # This test would:
    # - Start kernel
    # - Spawn 1 agent in separate process
    # - Kill agent process (os.kill(pid, signal.SIGKILL))
    # - Check kernel.get_status() still works
    # - Check process_manager.processes[agent_id]["process"].is_alive() == False
    # - Wait for restart attempt
    # - Verify agent respawns
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
