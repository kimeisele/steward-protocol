"""
TEST PROCESS MANAGER (The Airbag)
=================================

Verifies the resilience of the ProcessManager.
Crucial for system stability (Narasimha).
"""
import pytest
import time
import os
import multiprocessing
from vibe_core.mahamantra.substrate.process_manager import ProcessManager, ProcessStatus

# Path to the dummy fixture
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "dummy_agent.py")

class MockTask:
    def __init__(self, task_id, command):
        self.task_id = task_id
        self.payload = {"command": command}
        self.command = command # For the dummy agent to read directly via getattr if needed, or dict access
    
    # The dummy agent in fixture uses task.get("command"), creating a dict-like object wrapper
    # But wait, the ProcessManager sends `task` as payload.
    # The dummy agent `process` method receives this object.
    # Let's make it behave like a dict for the dummy agent's simple logic
    def get(self, key):
        return self.payload.get(key)

@pytest.fixture
def process_manager():
    """Setup and teardown ProcessManager."""
    pm = ProcessManager()
    yield pm
    pm.shutdown()

def test_spawn_and_communication(process_manager):
    """Verify we can spawn an agent and talk to it."""
    agent_id = "test_agent_1"
    
    # 1. Spawn
    process_manager.spawn_agent(
        agent_id=agent_id,
        cartridge_path=FIXTURE_PATH,
        cartridge_class_name="DummyAgent",
        config={"deployment": "test"}
    )
    
    # Give it a moment to boot
    time.sleep(1)
    
    # Verify status
    assert agent_id in process_manager.processes
    info = process_manager.processes[agent_id]
    assert info.status == ProcessStatus.RUNNING
    assert info.process.is_alive()
    
    # 2. Send Task
    task = MockTask("task_1", "hello")
    sent = process_manager.send_task(agent_id, task)
    assert sent is True, "Task should be sent and ACKed"
    
    # 3. Receive Result
    # Wait for result
    time.sleep(0.5)
    messages = process_manager.get_pending_messages()
    
    # Filter for our agent
    agent_msgs = [m for a, m in messages if a == agent_id]
    assert len(agent_msgs) >= 1
    
    result_msg = agent_msgs[0] # {"type": "TASK_RESULT", ...}
    assert result_msg["type"] == "TASK_RESULT"
    assert result_msg["status"] == "success"
    assert result_msg["result"] == "Processed: hello"

def test_narasimha_crash_recovery(process_manager):
    """
    THE CRITICAL TEST: Verify failover/restart logic.
    """
    agent_id = "test_agent_suicide"
    
    # 1. Spawn
    process_manager.spawn_agent(
        agent_id=agent_id,
        cartridge_path=FIXTURE_PATH,
        cartridge_class_name="DummyAgent"
    )
    time.sleep(1)
    
    original_pid = process_manager.processes[agent_id].process.pid
    
    # 2. Command Suicide
    # We send a task that triggers sys.exit(1)
    task = MockTask("death_task", "suicide")
    # Note: send_task might fail to get ACK if it dies INSTANTLY, 
    # but usually it dies during processing.
    process_manager.send_task(agent_id, task)
    
    # Wait for death
    time.sleep(1)
    
    # 3. Check Health (Narasimha Intervention)
    # The process should be dead now. check_health should notice and restart.
    process_manager.check_health()
    
    # Verify status
    info = process_manager.processes[agent_id]
    
    # Should be back to RUNNING
    assert info.status == ProcessStatus.RUNNING
    assert info.process.is_alive()
    
    # PID should have changed
    assert info.process.pid != original_pid
    assert info.restarts == 1
    
    print(f"Verified Restart: PID {original_pid} -> {info.process.pid}")

def test_shutdown_cleanup(process_manager):
    """Verify shutdown kills processes."""
    agent_id = "test_agent_cleanup"
    
    process_manager.spawn_agent(
        agent_id=agent_id,
        cartridge_path=FIXTURE_PATH,
        cartridge_class_name="DummyAgent"
    )
    time.sleep(0.5)
    
    proc = process_manager.processes[agent_id].process
    assert proc.is_alive()
    
    process_manager.shutdown()
    
    # Should be dead
    # Give OS a moment to reap
    time.sleep(0.5)
    assert not proc.is_alive()
