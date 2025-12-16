import logging

import pytest

# Use Standardized Fixtures (MINIATURWUNDERLAND)
from vibe_core.plugins.test_orchestration.fixtures import TestAgents, TestKernel, TestTasks
from vibe_core.plugins.vedic_governance.ashrama import Ashrama
from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

logger = logging.getLogger("TEST_VEDIC")


@pytest.fixture
def test_env():
    """
    Setup isolated test environment using TestKernel.minimal().
    Loads ONLY the VedicGovernancePlugin for targeted testing.
    """
    # 1. Create Minimal Kernel (In-memory ledger, NO plugins loaded by default)
    kernel = TestKernel.minimal()

    # 2. Manually load Vedic Governance
    governance = VedicGovernancePlugin()
    governance.on_boot(kernel)
    kernel._plugins.append(governance)

    # 3. Setup Mock Scheduler (TestKernel.minimal uses real InMemoryScheduler? Check implementation)
    # The fixture implementation creates RealVibeKernel(load_plugins=False).
    # RealVibeKernel creates a real scheduler. If we want to control execution order or avoid full scheduling:
    # We can use the real scheduler but we need to ensure the worker loop isn't running if we want synchronous stepping.
    # For this test, we want to call kernel.tick() manually.

    # Set status to RUNNING to allow ticks
    from vibe_core.protocols import KernelStatus

    kernel._status = KernelStatus.RUNNING

    return kernel, governance


@pytest.mark.asyncio
async def test_vedic_demotion_enforcement(test_env):
    """
    Verify that:
    1. Agents start as BRAHMACHARI (Student).
    2. BRAHMACHARI agents are VETOED from 'write' tasks.
    3. The Kernel HARD FAILS vetoed tasks (PermissionDenied).
    4. Promoted agents (GRIHASTHA) are ALLOWED 'write' tasks.
    5. Demoted agents lose rights again.
    """
    kernel, governance = test_env

    # 1. Register a test agent
    # Use TestAgents factory - creates a compliant agent
    agent = TestAgents.compliant(agent_id="test_student")

    # In minimal kernel, we must manually trigger governance hook or register via kernel
    # kernel.register_agent() calls plugin hooks!
    kernel.register_agent(agent, spawn_process=False)

    # Verify initial state
    ashrama = governance.get_agent_ashrama(agent.agent_id)
    assert ashrama.current_ashrama == Ashrama.BRAHMACHARI, "New agents must start as Brahmachari"

    # 2. Try to perform a WRITE task (Forbidden for Brahmachari)
    # Use TestTasks factory
    write_task = TestTasks.with_payload(agent.agent_id, {"action": "write"})
    # Monkey-patch attributes used by governance if payload isn't sufficient
    write_task.action = "write"

    # Submit task to kernel queue
    kernel.submit_task(write_task)

    # 3. Verify Kernel Enforcement (The "No Pussy Mode" Check)
    # The task is now in scheduler queue.
    # Run one tick to process it.

    # Reset ledger before tick to capture new events
    # (InMemoryLedger doesn't support reset, so we'll check latest event)
    initial_events = len(kernel._ledger.get_all_events())

    # Trick: We need to ensure the scheduler picks THIS task.
    # Since it's the only one, it should be fine.
    print(f"DEBUG: Scheduler Pending Count: {kernel._scheduler.get_queue_status().get('pending')}")
    kernel.tick()

    # Verify FAILURE was recorded in Ledger
    events = kernel._ledger.get_all_events()
    new_events = events[initial_events:]

    print(f"DEBUG: New Events: {new_events}")

    failure_event = next((e for e in new_events if e.get("event_type") == "task_failed"), None)
    if not failure_event:
        print("DEBUG: All Events Dump:", kernel._ledger.get_all_events())

    assert failure_event is not None, f"Task should have failed. Got events: {[e['event_type'] for e in new_events]}"
    # InMemoryLedger stores error at top level for record_failure
    error_msg = failure_event.get("error") or failure_event.get("details", {}).get("error", "")

    assert "PermissionDenied" in error_msg, f"Kernel must record PermissionDenied failure. Got: {error_msg}"

    # 4. Promote Agent
    success = governance.promote_agent(agent.agent_id, reason="Testing")
    assert success == True
    assert governance.get_agent_ashrama(agent.agent_id).current_ashrama == Ashrama.GRIHASTHA

    # 5. Verify Write is now ALLOWED
    # Submit task again
    write_task_2 = TestTasks.with_payload(agent.agent_id, {"action": "write"})
    write_task_2.action = "write"
    kernel.submit_task(write_task_2)

    # Capture events before
    initial_events_2 = len(kernel._ledger.get_all_events())

    # Run tick
    kernel.tick()

    # Verify START was recorded (or completion if in-process)
    events_2 = kernel._ledger.get_all_events()
    new_events_2 = events_2[initial_events_2:]

    # Should NOT have task_failed for PermissionDenied
    permission_failure = next(
        (
            e
            for e in new_events_2
            if e.get("event_type") == "task_failed" and "PermissionDenied" in (e.get("error") or "")
        ),
        None,
    )
    assert permission_failure is None, "Should allowed write task after promotion"

    # Should have task_start (lowercase)
    start_event = next((e for e in new_events_2 if e.get("event_type") == "task_start"), None)
    assert start_event is not None, f"Task should have started. Got: {[e['event_type'] for e in new_events_2]}"

    # 6. Demote Agent
    success = governance.demote_agent(agent.agent_id, reason="Testing Demotion")
    assert success == True
    assert governance.get_agent_ashrama(agent.agent_id).current_ashrama == Ashrama.BRAHMACHARI

    # 7. Verify Write is FORBIDDEN again
    write_task_3 = TestTasks.with_payload(agent.agent_id, {"action": "write"})
    write_task_3.action = "write"
    kernel.submit_task(write_task_3)

    initial_events_3 = len(kernel._ledger.get_all_events())
    kernel.tick()

    events_3 = kernel._ledger.get_all_events()
    new_events_3 = events_3[initial_events_3:]

    failure_event_3 = next((e for e in new_events_3 if e.get("event_type") == "task_failed"), None)
    assert failure_event_3 is not None
    assert "PermissionDenied" in (failure_event_3.get("error") or "")


if __name__ == "__main__":
    pytest.main([__file__])
