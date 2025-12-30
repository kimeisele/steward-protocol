"""
TEST: ProcessManager - The "Airbag" System
===========================================
Verifies process isolation, spawn, crash handling, and messaging.
Target: vibe_core/process_manager.py
Standard: GAD-5000

Tests mock multiprocessing components to avoid slow process spawns.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.process_manager import (
    AgentProcessInfo,
    ProcessManager,
    ProcessStatus,
)

# =============================================================================
# TEST: ProcessStatus Enum
# =============================================================================


class TestProcessStatus:
    """Test ProcessStatus enum."""

    def test_init_status_exists(self):
        """Should have INIT status."""
        assert ProcessStatus.INIT.value == "init"

    def test_running_status_exists(self):
        """Should have RUNNING status."""
        assert ProcessStatus.RUNNING.value == "running"

    def test_stopped_status_exists(self):
        """Should have STOPPED status."""
        assert ProcessStatus.STOPPED.value == "stopped"

    def test_crashed_status_exists(self):
        """Should have CRASHED status."""
        assert ProcessStatus.CRASHED.value == "crashed"

    def test_quarantined_status_exists(self):
        """Should have QUARANTINED status."""
        assert ProcessStatus.QUARANTINED.value == "quarantined"


# =============================================================================
# TEST: AgentProcessInfo Dataclass
# =============================================================================


class TestAgentProcessInfo:
    """Test AgentProcessInfo dataclass."""

    def test_create_agent_process_info(self):
        """Should create AgentProcessInfo with required fields."""
        mock_process = MagicMock()
        mock_pipe = MagicMock()

        info = AgentProcessInfo(
            process=mock_process,
            parent_pipe=mock_pipe,
            agent_id="test_agent",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path/to/cartridge.py",
            cartridge_class_name="TestCartridge",
        )

        assert info.process is mock_process
        assert info.parent_pipe is mock_pipe
        assert info.agent_id == "test_agent"
        assert info.status == ProcessStatus.RUNNING
        assert info.cartridge_path == "/path/to/cartridge.py"
        assert info.cartridge_class_name == "TestCartridge"

    def test_default_values(self):
        """Should have correct default values."""
        mock_process = MagicMock()
        mock_pipe = MagicMock()

        info = AgentProcessInfo(
            process=mock_process,
            parent_pipe=mock_pipe,
            agent_id="test",
            status=ProcessStatus.INIT,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        assert info.config is None
        assert info.restarts == 0
        assert info.last_heartbeat == 0.0


# =============================================================================
# TEST: ProcessManager Initialization
# =============================================================================


class TestProcessManagerInit:
    """Test ProcessManager initialization."""

    def test_init_creates_empty_processes(self):
        """Should initialize with empty processes dict."""
        pm = ProcessManager()

        assert isinstance(pm.processes, dict)
        assert len(pm.processes) == 0

    def test_init_sets_max_restarts(self):
        """Should set max restarts from config."""
        pm = ProcessManager()

        assert hasattr(pm, "MAX_RESTARTS")
        assert isinstance(pm.MAX_RESTARTS, int)
        assert pm.MAX_RESTARTS >= 0


# =============================================================================
# TEST: spawn_agent Method
# =============================================================================


class TestSpawnAgent:
    """Test spawn_agent method."""

    @patch("vibe_core.process_manager.Process")
    @patch("vibe_core.process_manager.Pipe")
    def test_spawn_agent_creates_process(self, mock_pipe, mock_process_class):
        """Should create and start a new process."""
        # Setup mocks
        mock_parent_conn = MagicMock()
        mock_child_conn = MagicMock()
        mock_pipe.return_value = (mock_parent_conn, mock_child_conn)

        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process_class.return_value = mock_process

        pm = ProcessManager()

        pm.spawn_agent(
            agent_id="test_agent",
            cartridge_path="/path/to/cartridge.py",
            cartridge_class_name="TestCartridge",
            config={"key": "value"},
        )

        # Verify process was created and started
        mock_process.start.assert_called_once()

    @patch("vibe_core.process_manager.Process")
    @patch("vibe_core.process_manager.Pipe")
    def test_spawn_agent_stores_info(self, mock_pipe, mock_process_class):
        """Should store AgentProcessInfo in processes dict."""
        mock_parent_conn = MagicMock()
        mock_child_conn = MagicMock()
        mock_pipe.return_value = (mock_parent_conn, mock_child_conn)

        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process_class.return_value = mock_process

        pm = ProcessManager()

        pm.spawn_agent(
            agent_id="my_agent",
            cartridge_path="/path/to/cartridge.py",
            cartridge_class_name="MyCartridge",
        )

        assert "my_agent" in pm.processes
        info = pm.processes["my_agent"]
        assert info.agent_id == "my_agent"
        assert info.status == ProcessStatus.RUNNING
        assert info.cartridge_path == "/path/to/cartridge.py"
        assert info.cartridge_class_name == "MyCartridge"

    @patch("vibe_core.process_manager.Process")
    @patch("vibe_core.process_manager.Pipe")
    def test_spawn_agent_sets_last_heartbeat(self, mock_pipe, mock_process_class):
        """Should set last_heartbeat to current time."""
        mock_pipe.return_value = (MagicMock(), MagicMock())
        mock_process_class.return_value = MagicMock(pid=123)

        pm = ProcessManager()
        before = time.time()

        pm.spawn_agent(
            agent_id="agent",
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        after = time.time()
        heartbeat = pm.processes["agent"].last_heartbeat

        assert before <= heartbeat <= after


# =============================================================================
# TEST: send_task Method
# =============================================================================


class TestSendTask:
    """Test send_task method."""

    def test_send_task_to_unknown_agent_raises(self):
        """Should raise ValueError for unknown agent."""
        pm = ProcessManager()

        with pytest.raises(ValueError) as exc_info:
            pm.send_task("nonexistent", {"type": "task"})

        assert "not running" in str(exc_info.value)

    def test_send_task_to_non_running_agent_raises(self):
        """Should raise ValueError for non-running agent."""
        pm = ProcessManager()

        # Add agent in CRASHED state
        mock_process = MagicMock()
        mock_pipe = MagicMock()
        pm.processes["crashed_agent"] = AgentProcessInfo(
            process=mock_process,
            parent_pipe=mock_pipe,
            agent_id="crashed_agent",
            status=ProcessStatus.CRASHED,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        with pytest.raises(ValueError) as exc_info:
            pm.send_task("crashed_agent", {"type": "task"})

        assert "crashed" in str(exc_info.value)

    def test_send_task_returns_true_on_ack(self):
        """Should return True when ACK received."""
        from vibe_core.scheduling import Task

        pm = ProcessManager()

        mock_pipe = MagicMock()
        mock_pipe.poll.return_value = True
        mock_pipe.recv.return_value = {"type": "TASK_ACK"}

        pm.processes["agent"] = AgentProcessInfo(
            process=MagicMock(),
            parent_pipe=mock_pipe,
            agent_id="agent",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        # Create real serializable task (not MagicMock)
        task = Task(agent_id="agent", payload={"action": "test"})

        result = pm.send_task("agent", task)

        assert result is True
        mock_pipe.send.assert_called_once()

    def test_send_task_returns_false_on_timeout(self):
        """Should return False when no ACK within timeout."""
        pm = ProcessManager()

        mock_pipe = MagicMock()
        mock_pipe.poll.return_value = False  # No message available

        pm.processes["agent"] = AgentProcessInfo(
            process=MagicMock(),
            parent_pipe=mock_pipe,
            agent_id="agent",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        mock_task = MagicMock()
        mock_task.task_id = "task_001"

        result = pm.send_task("agent", mock_task)

        assert result is False


# =============================================================================
# TEST: check_health Method
# =============================================================================


class TestCheckHealth:
    """Test check_health (Narasimha) method."""

    def test_check_health_detects_crashed_process(self):
        """Should detect and mark crashed processes."""
        pm = ProcessManager()

        mock_process = MagicMock()
        mock_process.is_alive.return_value = False
        mock_process.exitcode = 1

        mock_pipe = MagicMock()

        pm.processes["agent"] = AgentProcessInfo(
            process=mock_process,
            parent_pipe=mock_pipe,
            agent_id="agent",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path/cartridge.py",
            cartridge_class_name="Cartridge",
        )

        # Mock _handle_crash to avoid actual restart
        pm._handle_crash = MagicMock()

        pm.check_health()

        # Should mark as crashed
        assert pm.processes["agent"].status == ProcessStatus.CRASHED
        # Should call crash handler
        pm._handle_crash.assert_called_once_with("agent")

    def test_check_health_ignores_running_process(self):
        """Should not modify running processes."""
        pm = ProcessManager()

        mock_process = MagicMock()
        mock_process.is_alive.return_value = True

        pm.processes["agent"] = AgentProcessInfo(
            process=mock_process,
            parent_pipe=MagicMock(),
            agent_id="agent",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        pm._handle_crash = MagicMock()

        pm.check_health()

        # Should remain running
        assert pm.processes["agent"].status == ProcessStatus.RUNNING
        # Should not call crash handler
        pm._handle_crash.assert_not_called()


# =============================================================================
# TEST: get_pending_messages Method
# =============================================================================


class TestGetPendingMessages:
    """Test get_pending_messages method."""

    def test_get_pending_messages_returns_messages(self):
        """Should return pending messages from agents."""
        pm = ProcessManager()

        mock_pipe = MagicMock()
        mock_pipe.poll.side_effect = [True, True, False]  # 2 messages, then empty
        mock_pipe.recv.side_effect = [
            {"type": "RESULT", "data": 1},
            {"type": "STATUS", "data": 2},
        ]

        pm.processes["agent"] = AgentProcessInfo(
            process=MagicMock(),
            parent_pipe=mock_pipe,
            agent_id="agent",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        messages = pm.get_pending_messages()

        assert len(messages) == 2
        assert messages[0] == ("agent", {"type": "RESULT", "data": 1})
        assert messages[1] == ("agent", {"type": "STATUS", "data": 2})

    def test_get_pending_messages_skips_non_running(self):
        """Should skip non-running agents."""
        pm = ProcessManager()

        mock_pipe = MagicMock()
        mock_pipe.poll.return_value = True
        mock_pipe.recv.return_value = {"type": "MESSAGE"}

        pm.processes["crashed"] = AgentProcessInfo(
            process=MagicMock(),
            parent_pipe=mock_pipe,
            agent_id="crashed",
            status=ProcessStatus.CRASHED,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        messages = pm.get_pending_messages()

        assert len(messages) == 0

    def test_get_pending_messages_empty(self):
        """Should return empty list when no messages."""
        pm = ProcessManager()

        mock_pipe = MagicMock()
        mock_pipe.poll.return_value = False

        pm.processes["agent"] = AgentProcessInfo(
            process=MagicMock(),
            parent_pipe=mock_pipe,
            agent_id="agent",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        messages = pm.get_pending_messages()

        assert messages == []


# =============================================================================
# TEST: _handle_crash Method
# =============================================================================


class TestHandleCrash:
    """Test _handle_crash method."""

    @patch("vibe_core.process_manager.Process")
    @patch("vibe_core.process_manager.Pipe")
    def test_handle_crash_restarts_agent(self, mock_pipe, mock_process_class):
        """Should restart crashed agent."""
        mock_parent_conn = MagicMock()
        mock_child_conn = MagicMock()
        mock_pipe.return_value = (mock_parent_conn, mock_child_conn)

        mock_new_process = MagicMock()
        mock_new_process.pid = 99999
        mock_process_class.return_value = mock_new_process

        pm = ProcessManager()

        mock_old_process = MagicMock()
        mock_old_process.is_alive.return_value = False
        mock_old_pipe = MagicMock()

        pm.processes["agent"] = AgentProcessInfo(
            process=mock_old_process,
            parent_pipe=mock_old_pipe,
            agent_id="agent",
            status=ProcessStatus.CRASHED,
            cartridge_path="/path/cartridge.py",
            cartridge_class_name="Cartridge",
            restarts=0,
        )

        pm._handle_crash("agent")

        # Should have restarted
        mock_new_process.start.assert_called_once()
        assert pm.processes["agent"].status == ProcessStatus.RUNNING
        assert pm.processes["agent"].restarts == 1

    def test_handle_crash_quarantines_after_max_restarts(self):
        """Should quarantine agent after max restarts exceeded."""
        pm = ProcessManager()

        mock_process = MagicMock()
        mock_pipe = MagicMock()

        pm.processes["agent"] = AgentProcessInfo(
            process=mock_process,
            parent_pipe=mock_pipe,
            agent_id="agent",
            status=ProcessStatus.CRASHED,
            cartridge_path="/path",
            cartridge_class_name="Class",
            restarts=pm.MAX_RESTARTS,  # Already at max
        )

        pm._handle_crash("agent")

        # Should be quarantined, not restarted
        assert pm.processes["agent"].status == ProcessStatus.QUARANTINED


# =============================================================================
# TEST: shutdown Method
# =============================================================================


class TestShutdown:
    """Test shutdown method."""

    def test_shutdown_stops_all_agents(self):
        """Should send STOP to all agents and terminate."""
        pm = ProcessManager()

        mock_process1 = MagicMock()
        mock_process1.is_alive.return_value = True
        mock_pipe1 = MagicMock()

        mock_process2 = MagicMock()
        mock_process2.is_alive.return_value = True
        mock_pipe2 = MagicMock()

        pm.processes["agent1"] = AgentProcessInfo(
            process=mock_process1,
            parent_pipe=mock_pipe1,
            agent_id="agent1",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        pm.processes["agent2"] = AgentProcessInfo(
            process=mock_process2,
            parent_pipe=mock_pipe2,
            agent_id="agent2",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        # Make join return immediately
        mock_process1.is_alive.side_effect = [True, False]  # First alive, then stopped
        mock_process2.is_alive.side_effect = [True, False]

        pm.shutdown()

        # Should send STOP to all
        mock_pipe1.send.assert_called_with({"type": "STOP"})
        mock_pipe2.send.assert_called_with({"type": "STOP"})

        # Should join processes
        mock_process1.join.assert_called()
        mock_process2.join.assert_called()

    def test_shutdown_terminates_stuck_processes(self):
        """Should terminate processes that don't stop gracefully."""
        pm = ProcessManager()

        mock_process = MagicMock()
        mock_process.is_alive.return_value = True  # Always alive (stuck)
        mock_pipe = MagicMock()

        pm.processes["stuck"] = AgentProcessInfo(
            process=mock_process,
            parent_pipe=mock_pipe,
            agent_id="stuck",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        pm.shutdown()

        # Should terminate stuck process
        mock_process.terminate.assert_called_once()


# =============================================================================
# TEST: Message Size Limit
# =============================================================================


class TestMessageSizeLimit:
    """Test message size limit enforcement."""

    def test_oversized_message_rejected(self):
        """Should reject messages exceeding size limit."""
        pm = ProcessManager()

        mock_pipe = MagicMock()

        pm.processes["agent"] = AgentProcessInfo(
            process=MagicMock(),
            parent_pipe=mock_pipe,
            agent_id="agent",
            status=ProcessStatus.RUNNING,
            cartridge_path="/path",
            cartridge_class_name="Class",
        )

        # Create a very large task
        large_task = MagicMock()
        large_task.task_id = "task"
        large_task.data = "x" * 100_000_000  # 100MB of data

        result = pm.send_task("agent", large_task)

        # Should be rejected
        assert result is False


# =============================================================================
# TEST: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_processes_check_health(self):
        """Should handle empty processes dict."""
        pm = ProcessManager()

        # Should not raise
        pm.check_health()

    def test_empty_processes_get_pending_messages(self):
        """Should return empty list for no processes."""
        pm = ProcessManager()

        messages = pm.get_pending_messages()

        assert messages == []

    def test_empty_processes_shutdown(self):
        """Should handle shutdown with no processes."""
        pm = ProcessManager()

        # Should not raise
        pm.shutdown()
