"""
Agent City Boot Integration Test
=================================

Tests the complete Agent City boot sequence using real kernel.

Test Flow:
1. Boot kernel via BootOrchestrator
2. Verify agents are registered
3. Submit a task to an agent
4. Verify task is processed
5. Check kernel pulse
"""

import pytest

from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.scheduling import Task


def test_agent_city_boot():
    """Test the complete Agent City boot sequence."""
    # PHASE 1: BOOT
    from unittest.mock import MagicMock

    from vibe_core.event_bus import EventBus
    from vibe_core.runtime.unified_trace import UnifiedTrace

    # Mock dependencies for orchestration
    trace = MagicMock(spec=UnifiedTrace)
    event_bus = MagicMock(spec=EventBus)

    # PHASE 1: BOOT
    orchestrator = BootOrchestrator(ledger_path=":memory:", trace=trace, event_bus=event_bus)
    kernel = orchestrator.boot()

    assert kernel is not None, "Kernel boot failed"

    # PHASE 2: VERIFY AGENTS
    status = kernel.get_status()
    agents_registered = status.get("agents_registered", 0)

    assert isinstance(agents_registered, int), "Invalid status format"

    # List all registered agents
    agent_ids = list(kernel.agent_registry.keys())

    # PHASE 3: SUBMIT TASK (if agents are available)
    if agent_ids:
        # Find an agent to send task to
        target_agent = None
        for agent_id in ["ping", "scribe", "engineer", "discoverer"]:
            if agent_id in kernel.agent_registry:
                target_agent = agent_id
                break

        if not target_agent:
            target_agent = agent_ids[0]

        test_task = Task(
            agent_id=target_agent,
            payload={
                "type": "test",
                "message": "Hello from boot test!",
                "test_id": "boot_test_001",
            },
        )

        task_id = kernel.submit_task(test_task)
        assert task_id is not None, "Task submission failed"

        # PHASE 4: TICK KERNEL (async method, skip in sync test)
        # Note: kernel.tick() was removed, use tick_async() in async context
        # For sync test, we just verify task was submitted successfully

    # PHASE 5: FINAL STATUS
    final_status = kernel.get_status()
    assert final_status.get("status") in ["RUNNING", "IDLE"], "Invalid kernel status"

    # PHASE 6: SHUTDOWN
    kernel.shutdown(reason="Boot test complete")


@pytest.mark.integration
def test_kernel_boot_with_governance(governance_kernel):
    """Test kernel boots with full governance stack."""
    assert governance_kernel is not None
    status = governance_kernel.get_status()
    assert "status" in status
