#!/usr/bin/env python3
"""
Integration Test: Kernel Markdown Interfaces (SETTINGS.md + ENVOY.md)
======================================================================

Tests the markdown-based control interfaces:

1. SETTINGS.md - Command Queue Interface
   - Renders configuration and agent status
   - Parses commands (SET, PAUSE, RESUME)
   - Executes commands with whitelist enforcement
   - Tracks execution history

2. ENVOY.md - Terminal Interface (Frontend Chat)
   - Renders terminal with Request/Status/History sections
   - Detects user requests via file change
   - Routes via PlaybookRouter (NO LLM)
   - Dispatches tasks async to scheduler
   - Updates status and history on completion

NO MOCKS. Real kernel, real scheduler, real PlaybookRouter.
"""

import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.config import ConfigLoader


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_workdir():
    """Create a temporary working directory for tests."""
    original_cwd = Path.cwd()
    temp_dir = tempfile.mkdtemp(prefix="vibe_test_")

    # Copy necessary config files
    config_src = original_cwd / "config"
    if config_src.exists():
        shutil.copytree(config_src, Path(temp_dir) / "config")

    # Copy knowledge directory if exists
    knowledge_src = original_cwd / "knowledge"
    if knowledge_src.exists():
        shutil.copytree(knowledge_src, Path(temp_dir) / "knowledge")

    # Copy playbook registry if exists
    playbook_src = original_cwd / "vibe_core" / "playbook" / "_registry.yaml"
    if playbook_src.exists():
        playbook_dst = Path(temp_dir) / "vibe_core" / "playbook"
        playbook_dst.mkdir(parents=True, exist_ok=True)
        shutil.copy(playbook_src, playbook_dst / "_registry.yaml")

    import os
    os.chdir(temp_dir)

    yield Path(temp_dir)

    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kernel():
    """Create a real kernel instance (no boot, just kernel)."""
    return RealVibeKernel()


@pytest.fixture
def booted_kernel():
    """Create a fully booted kernel with agents."""
    try:
        loader = ConfigLoader()
        config = loader.load()
    except Exception:
        config = None

    orchestrator = BootOrchestrator(config=config)
    return orchestrator.boot()


# =============================================================================
# SETTINGS.md TESTS
# =============================================================================

class TestSettingsMarkdownInterface:
    """Tests for SETTINGS.md command queue interface."""

    def test_render_settings_creates_file(self, kernel, temp_workdir):
        """Test that _render_settings_file creates SETTINGS.md."""
        settings_path = temp_workdir / "SETTINGS.md"
        assert not settings_path.exists()

        # Create minimal snapshot
        snapshot = {
            "timestamp": "2025-01-01T00:00:00",
            "kernel_status": "RUNNING",
            "agents": {},
            "scheduler": {"queue_length": 0, "completed": 0},
            "ledger_stats": {"total_events": 0},
        }

        kernel._render_settings_file(snapshot)

        assert settings_path.exists()
        content = settings_path.read_text()

        # Verify structure
        assert "# ⚙️ SYSTEM SETTINGS" in content
        assert "## 🔧 Kernel Configuration" in content
        assert "## 🤖 Agent Registry" in content
        assert "## ⚡ Pending Commands" in content
        assert "## 🏛️ Execution Ledger" in content

    def test_render_settings_shows_agents(self, kernel, temp_workdir):
        """Test that SETTINGS.md shows registered agents."""
        snapshot = {
            "timestamp": "2025-01-01T00:00:00",
            "kernel_status": "RUNNING",
            "agents": {
                "steward": {"status": "ACTIVE", "tasks_completed": 5},
                "herald": {"status": "IDLE", "tasks_completed": 0},
            },
            "scheduler": {"queue_length": 0, "completed": 5},
            "ledger_stats": {"total_events": 10},
        }

        kernel._render_settings_file(snapshot)

        content = (temp_workdir / "SETTINGS.md").read_text()
        assert "`steward`" in content
        assert "`herald`" in content
        assert "Agents Registered:** 2" in content

    def test_parse_set_command(self, kernel, temp_workdir):
        """Test parsing SET commands from SETTINGS.md."""
        settings_content = """# SETTINGS

## ⚡ Pending Commands

- SET kernel.log_level=DEBUG
- SET kernel.log_level=INFO

## 🏛️ Execution Ledger
"""
        (temp_workdir / "SETTINGS.md").write_text(settings_content)

        commands = kernel._parse_settings_commands()

        assert len(commands) == 2
        assert commands[0]["action"] == "SET"
        assert commands[0]["key"] == "kernel.log_level"
        assert commands[0]["value"] == "DEBUG"
        assert commands[1]["value"] == "INFO"

    def test_parse_pause_resume_commands(self, kernel, temp_workdir):
        """Test parsing PAUSE and RESUME commands."""
        settings_content = """# SETTINGS

## ⚡ Pending Commands

- PAUSE agent.steward
- RESUME agent.herald

## 🏛️ Execution Ledger
"""
        (temp_workdir / "SETTINGS.md").write_text(settings_content)

        commands = kernel._parse_settings_commands()

        assert len(commands) == 2
        assert commands[0]["action"] == "PAUSE"
        assert commands[0]["agent_id"] == "agent.steward"
        assert commands[1]["action"] == "RESUME"
        assert commands[1]["agent_id"] == "agent.herald"

    def test_execute_set_log_level(self, kernel, temp_workdir):
        """Test executing SET kernel.log_level command."""
        commands = [{"action": "SET", "key": "kernel.log_level", "value": "DEBUG"}]

        kernel._execute_settings_commands(commands)

        # Check execution history
        assert len(kernel._settings_execution_history) == 1
        record = kernel._settings_execution_history[0]
        assert record["status"] == "SUCCESS"
        assert "log_level" in record["command"]["key"]

    def test_execute_set_blocked_by_whitelist(self, kernel, temp_workdir):
        """Test that non-whitelisted settings are blocked."""
        commands = [{"action": "SET", "key": "kernel.status", "value": "STOPPED"}]

        kernel._execute_settings_commands(commands)

        # Should be blocked
        assert len(kernel._settings_execution_history) == 1
        record = kernel._settings_execution_history[0]
        assert record["status"] == "FAILED"
        assert "whitelist" in record["reason"].lower()

    def test_execute_pause_agent(self, booted_kernel, temp_workdir):
        """Test PAUSE command pauses an agent."""
        # Get a real registered agent
        agent_ids = list(booted_kernel._agent_registry.keys())
        if not agent_ids:
            pytest.skip("No agents registered")

        agent_id = agent_ids[0]
        commands = [{"action": "PAUSE", "agent_id": f"agent.{agent_id}"}]

        assert agent_id not in booted_kernel._paused_agents

        booted_kernel._execute_settings_commands(commands)

        assert agent_id in booted_kernel._paused_agents
        assert booted_kernel._settings_execution_history[-1]["status"] == "SUCCESS"

    def test_execute_resume_agent(self, booted_kernel, temp_workdir):
        """Test RESUME command resumes a paused agent."""
        agent_ids = list(booted_kernel._agent_registry.keys())
        if not agent_ids:
            pytest.skip("No agents registered")

        agent_id = agent_ids[0]

        # First pause
        booted_kernel._paused_agents.add(agent_id)
        assert agent_id in booted_kernel._paused_agents

        # Then resume
        commands = [{"action": "RESUME", "agent_id": f"agent.{agent_id}"}]
        booted_kernel._execute_settings_commands(commands)

        assert agent_id not in booted_kernel._paused_agents
        assert booted_kernel._settings_execution_history[-1]["status"] == "SUCCESS"

    def test_file_change_detection(self, kernel, temp_workdir):
        """Test that file changes are detected via mtime."""
        settings_path = temp_workdir / "SETTINGS.md"

        # No file = no change
        assert not kernel._check_settings_file_changed()

        # Create file
        settings_path.write_text("# SETTINGS")
        kernel._settings_last_modified = 0  # Reset

        # File exists and mtime > last_modified
        assert kernel._check_settings_file_changed()

        # Update last_modified
        kernel._settings_last_modified = settings_path.stat().st_mtime

        # No change now
        assert not kernel._check_settings_file_changed()

    def test_full_sync_flow(self, kernel, temp_workdir):
        """Test full SETTINGS -> REALITY sync flow."""
        settings_content = """# SETTINGS

## ⚡ Pending Commands

- SET kernel.log_level=WARNING

## 🏛️ Execution Ledger
"""
        settings_path = temp_workdir / "SETTINGS.md"
        settings_path.write_text(settings_content)
        kernel._settings_last_modified = 0

        # Sync
        kernel._sync_settings_to_reality()

        # Command should be executed and removed
        assert len(kernel._settings_execution_history) == 1
        assert kernel._settings_execution_history[0]["status"] == "SUCCESS"


# =============================================================================
# ENVOY.md TESTS (Terminal/Frontend Chat Interface)
# =============================================================================

class TestEnvoyTerminalInterface:
    """Tests for ENVOY.md terminal interface (markdown frontend chat)."""

    def test_render_envoy_creates_file(self, kernel, temp_workdir):
        """Test that _render_envoy_file creates ENVOY.md."""
        envoy_path = temp_workdir / "ENVOY.md"
        assert not envoy_path.exists()

        snapshot = {
            "timestamp": "2025-01-01T00:00:00",
            "kernel_status": "RUNNING",
            "agents": {},
            "scheduler": {"queue_length": 0, "completed": 0},
            "ledger_stats": {"total_events": 0},
        }

        kernel._render_envoy_file(snapshot)

        assert envoy_path.exists()
        content = envoy_path.read_text()

        # Verify structure
        assert "# 📬 ENVOY TERMINAL" in content
        assert "## 💬 Request" in content
        assert "## 📊 Status" in content
        assert "## 📜 Response History" in content
        assert "## 🎯 Available Routes" in content

    def test_render_envoy_shows_available_routes(self, kernel, temp_workdir):
        """Test that ENVOY.md shows PlaybookRouter routes."""
        snapshot = {
            "timestamp": "2025-01-01T00:00:00",
            "kernel_status": "RUNNING",
            "agents": {},
            "scheduler": {"queue_length": 0, "completed": 0},
            "ledger_stats": {"total_events": 0},
        }

        kernel._render_envoy_file(snapshot)

        content = (temp_workdir / "ENVOY.md").read_text()

        # Should show some routes from PlaybookRouter
        assert "Available Routes" in content
        # At minimum, should have bootstrap route
        assert "bootstrap" in content.lower() or "status" in content.lower()

    def test_extract_user_request(self, kernel, temp_workdir):
        """Test extracting user-written request from ENVOY.md."""
        envoy_content = """# ENVOY TERMINAL

## 💬 Request

> Write your request here.

Build me a new REST API for user management

---

## 📊 Status
"""
        envoy_path = temp_workdir / "ENVOY.md"
        envoy_path.write_text(envoy_content)

        content = kernel._extract_envoy_request_content(envoy_path)

        assert "Build me a new REST API" in content
        assert "user management" in content
        # Should NOT include blockquote instructions
        assert "Write your request" not in content

    def test_extract_skips_placeholder(self, kernel, temp_workdir):
        """Test that placeholder text is skipped during extraction."""
        envoy_content = """# ENVOY TERMINAL

## 💬 Request

> Instructions here.

_No pending request. Write your request above this line._

---
"""
        envoy_path = temp_workdir / "ENVOY.md"
        envoy_path.write_text(envoy_content)

        content = kernel._extract_envoy_request_content(envoy_path)

        # Should be empty (placeholder is skipped)
        assert content.strip() == ""

    def test_extract_skips_separator(self, kernel, temp_workdir):
        """Test that --- separators are skipped during extraction."""
        envoy_content = """# ENVOY TERMINAL

## 💬 Request

> Instructions.

---

## 📊 Status
"""
        envoy_path = temp_workdir / "ENVOY.md"
        envoy_path.write_text(envoy_content)

        content = kernel._extract_envoy_request_content(envoy_path)

        # Should not include ---
        assert "---" not in content
        assert content.strip() == ""

    def test_parse_envoy_requests(self, kernel, temp_workdir):
        """Test parsing multiple requests from ENVOY.md."""
        envoy_content = """# ENVOY TERMINAL

## 💬 Request

> Instructions.

start a new project
show me the status

---

## 📊 Status
"""
        envoy_path = temp_workdir / "ENVOY.md"
        envoy_path.write_text(envoy_content)

        requests = kernel._parse_envoy_requests()

        assert len(requests) == 2
        assert "start a new project" in requests
        assert "show me the status" in requests

    def test_file_change_detection(self, kernel, temp_workdir):
        """Test that ENVOY.md changes are detected via mtime."""
        envoy_path = temp_workdir / "ENVOY.md"

        # No file = no change
        assert not kernel._check_envoy_file_changed()

        # Create file
        envoy_path.write_text("# ENVOY")
        kernel._envoy_last_modified = 0

        # File exists and mtime > last_modified
        assert kernel._check_envoy_file_changed()

        # Update last_modified
        kernel._envoy_last_modified = envoy_path.stat().st_mtime

        # No change now
        assert not kernel._check_envoy_file_changed()

    def test_dispatch_request_routes_via_playbook(self, kernel, temp_workdir):
        """Test that requests are routed via PlaybookRouter (NO LLM)."""
        result = kernel._dispatch_envoy_request("start a new project")

        assert result["status"] == "QUEUED"
        assert result["task_id"] is not None
        assert result["route"] is not None
        # Should match bootstrap or similar pattern
        assert result["confidence"] in ["explicit", "contextual", "suggested"]

    def test_dispatch_request_queues_task(self, kernel, temp_workdir):
        """Test that dispatched requests create tasks in scheduler."""
        result = kernel._dispatch_envoy_request("check project status")

        # Task should be queued and returned
        assert result["task_id"] is not None
        assert result["status"] == "QUEUED"
        assert result["route"] is not None

        # Note: _dispatch_envoy_request returns metadata but doesn't add to
        # _envoy_pending_tasks. That's done by _sync_envoy_to_reality().
        # We verify the task was submitted to scheduler by checking the result.

    def test_sync_envoy_processes_and_clears(self, kernel, temp_workdir):
        """Test full ENVOY -> REALITY sync: process and clear requests."""
        envoy_content = """# ENVOY TERMINAL

## 💬 Request

> Instructions.

initialize the system

---

## 📊 Status
"""
        envoy_path = temp_workdir / "ENVOY.md"
        envoy_path.write_text(envoy_content)
        kernel._envoy_last_modified = 0

        # Sync
        kernel._sync_envoy_to_reality()

        # Should have dispatched task
        assert len(kernel._envoy_pending_tasks) == 1

        # Request should be cleared from file
        new_content = envoy_path.read_text()
        assert "initialize the system" not in new_content

    def test_update_task_status_moves_to_history(self, kernel, temp_workdir):
        """Test that completing a task moves it from pending to history."""
        # Dispatch a request and manually add to pending (simulating _sync_envoy_to_reality)
        result = kernel._dispatch_envoy_request("test request")
        task_id = result["task_id"]

        # Manually add to pending tasks (normally done by _sync_envoy_to_reality)
        kernel._envoy_pending_tasks[task_id] = result

        assert task_id in kernel._envoy_pending_tasks
        assert len(kernel._envoy_request_history) == 0

        # Complete the task
        kernel.update_envoy_task_status(task_id, "COMPLETED", "Task done successfully")

        # Should be in history, not pending
        assert task_id not in kernel._envoy_pending_tasks
        assert len(kernel._envoy_request_history) == 1
        assert kernel._envoy_request_history[0]["status"] == "COMPLETED"
        assert kernel._envoy_request_history[0]["response"] == "Task done successfully"

    def test_render_shows_pending_tasks(self, kernel, temp_workdir):
        """Test that pending tasks are shown in Status section."""
        # Dispatch a request and add to pending (simulating _sync_envoy_to_reality)
        result = kernel._dispatch_envoy_request("build new feature")
        kernel._envoy_pending_tasks[result["task_id"]] = result

        snapshot = {
            "timestamp": "2025-01-01T00:00:00",
            "kernel_status": "RUNNING",
            "agents": {},
            "scheduler": {"queue_length": 1, "completed": 0},
            "ledger_stats": {"total_events": 0},
        }

        kernel._render_envoy_file(snapshot)

        content = (temp_workdir / "ENVOY.md").read_text()

        # Should show pending task in status
        assert "QUEUED" in content
        assert "build new feature" in content

    def test_render_shows_history(self, kernel, temp_workdir):
        """Test that completed tasks are shown in Response History."""
        # Dispatch a request, add to pending, then complete
        result = kernel._dispatch_envoy_request("old request")
        kernel._envoy_pending_tasks[result["task_id"]] = result
        kernel.update_envoy_task_status(result["task_id"], "COMPLETED", "Done!")

        snapshot = {
            "timestamp": "2025-01-01T00:00:00",
            "kernel_status": "RUNNING",
            "agents": {},
            "scheduler": {"queue_length": 0, "completed": 1},
            "ledger_stats": {"total_events": 0},
        }

        kernel._render_envoy_file(snapshot)

        content = (temp_workdir / "ENVOY.md").read_text()

        # Should show in history
        assert "old request" in content
        assert "Done!" in content or "COMPLETED" in content

    def test_preserves_user_request_on_render(self, kernel, temp_workdir):
        """Test that user's request is preserved when re-rendering."""
        # First render
        snapshot = {
            "timestamp": "2025-01-01T00:00:00",
            "kernel_status": "RUNNING",
            "agents": {},
            "scheduler": {"queue_length": 0, "completed": 0},
            "ledger_stats": {"total_events": 0},
        }
        kernel._render_envoy_file(snapshot)

        # User writes a request
        envoy_path = temp_workdir / "ENVOY.md"
        content = envoy_path.read_text()
        content = content.replace(
            "_No pending request. Write your request above this line._",
            "User's important request here"
        )
        envoy_path.write_text(content)

        # Re-render (should preserve user request)
        kernel._render_envoy_file(snapshot)

        new_content = envoy_path.read_text()
        assert "User's important request here" in new_content


# =============================================================================
# FULL LIFECYCLE TESTS
# =============================================================================

class TestFullLifecycle:
    """End-to-end tests for the complete request lifecycle."""

    def test_settings_command_lifecycle(self, booted_kernel, temp_workdir):
        """Test: Write command → tick → execute → history updated."""
        settings_path = temp_workdir / "SETTINGS.md"

        # Generate initial SETTINGS.md
        booted_kernel._pulse()
        assert settings_path.exists()

        # Add a command
        content = settings_path.read_text()
        # Insert command after "Pending Commands" header
        content = content.replace(
            "_No pending commands. Add commands above this line._",
            "- SET kernel.log_level=ERROR"
        )
        settings_path.write_text(content)
        booted_kernel._settings_last_modified = 0  # Force change detection

        # Run tick (processes commands)
        booted_kernel.tick()

        # Command should be executed
        assert len(booted_kernel._settings_execution_history) >= 1
        # Find our command in history
        found = any(
            r.get("command", {}).get("value") == "ERROR"
            for r in booted_kernel._settings_execution_history
        )
        assert found, "Command not found in execution history"

    def test_envoy_request_lifecycle(self, booted_kernel, temp_workdir):
        """Test: Write request → tick → dispatch → task queued."""
        envoy_path = temp_workdir / "ENVOY.md"

        # Generate initial ENVOY.md
        booted_kernel._pulse()
        assert envoy_path.exists()

        # Add a request
        content = envoy_path.read_text()
        content = content.replace(
            "_No pending request. Write your request above this line._",
            "start new development"
        )
        envoy_path.write_text(content)
        booted_kernel._envoy_last_modified = 0  # Force change detection

        # Run tick (processes request)
        booted_kernel.tick()

        # Request should be dispatched
        assert len(booted_kernel._envoy_pending_tasks) >= 1

        # Check task was routed
        task_meta = list(booted_kernel._envoy_pending_tasks.values())[0]
        assert task_meta["status"] == "QUEUED"
        assert task_meta["route"] is not None

    def test_envoy_complete_lifecycle(self, booted_kernel, temp_workdir):
        """Test: request → dispatch → complete → history → render shows history."""
        envoy_path = temp_workdir / "ENVOY.md"

        # Generate initial ENVOY.md
        booted_kernel._pulse()

        # Dispatch a request and add to pending (simulating _sync_envoy_to_reality)
        result = booted_kernel._dispatch_envoy_request("complete lifecycle test")
        task_id = result["task_id"]
        booted_kernel._envoy_pending_tasks[task_id] = result

        assert task_id in booted_kernel._envoy_pending_tasks

        # Simulate task completion
        booted_kernel.update_envoy_task_status(task_id, "COMPLETED", "Lifecycle complete!")

        # Should be in history
        assert len(booted_kernel._envoy_request_history) >= 1
        history_entry = booted_kernel._envoy_request_history[-1]
        assert history_entry["request"] == "complete lifecycle test"
        assert history_entry["response"] == "Lifecycle complete!"

        # Re-render and verify history shows
        booted_kernel._pulse()

        content = envoy_path.read_text()
        assert "complete lifecycle test" in content
        assert "Lifecycle complete!" in content or "COMPLETED" in content


# =============================================================================
# IPC CALLBACK TESTS
# =============================================================================

class TestEnvoyIPCCallback:
    """Tests for automatic ENVOY.md status update via IPC callbacks."""

    def test_ipc_success_updates_envoy_status(self, kernel, temp_workdir):
        """Test that IPC TASK_RESULT success updates ENVOY.md pending tasks."""
        # Dispatch a request and add to pending
        result = kernel._dispatch_envoy_request("ipc test request")
        task_id = result["task_id"]
        kernel._envoy_pending_tasks[task_id] = result

        assert task_id in kernel._envoy_pending_tasks
        assert len(kernel._envoy_request_history) == 0

        # Mock get_pending_messages to return our test IPC message
        original_get_messages = kernel.process_manager.get_pending_messages
        kernel.process_manager.get_pending_messages = lambda: [
            ("envoy", {"type": "TASK_RESULT", "task_id": task_id, "status": "success", "result": "IPC done!"})
        ]

        try:
            # Process IPC events (this triggers the callback)
            kernel._process_ipc_events()

            # Task should be moved to history
            assert task_id not in kernel._envoy_pending_tasks
            assert len(kernel._envoy_request_history) == 1
            assert kernel._envoy_request_history[0]["status"] == "COMPLETED"
            assert "IPC done!" in kernel._envoy_request_history[0]["response"]
        finally:
            kernel.process_manager.get_pending_messages = original_get_messages

    def test_ipc_failure_updates_envoy_status(self, kernel, temp_workdir):
        """Test that IPC TASK_RESULT failure updates ENVOY.md pending tasks."""
        # Dispatch a request and add to pending
        result = kernel._dispatch_envoy_request("failing ipc test")
        task_id = result["task_id"]
        kernel._envoy_pending_tasks[task_id] = result

        assert task_id in kernel._envoy_pending_tasks

        # Mock get_pending_messages to return failure
        original_get_messages = kernel.process_manager.get_pending_messages
        kernel.process_manager.get_pending_messages = lambda: [
            ("envoy", {"type": "TASK_RESULT", "task_id": task_id, "status": "error", "error": "Task failed!"})
        ]

        try:
            # Process IPC events
            kernel._process_ipc_events()

            # Task should be in history with FAILED status
            assert task_id not in kernel._envoy_pending_tasks
            assert len(kernel._envoy_request_history) == 1
            assert kernel._envoy_request_history[0]["status"] == "FAILED"
            assert "Task failed!" in kernel._envoy_request_history[0]["response"]
        finally:
            kernel.process_manager.get_pending_messages = original_get_messages

    def test_non_envoy_task_not_affected(self, kernel, temp_workdir):
        """Test that non-ENVOY tasks don't trigger ENVOY.md updates."""
        # Create a regular task (not from ENVOY.md)
        from vibe_core.scheduling import Task
        regular_task = Task(agent_id="steward", payload={"type": "regular"})
        kernel._scheduler.submit_task(regular_task)

        # Mock get_pending_messages
        original_get_messages = kernel.process_manager.get_pending_messages
        kernel.process_manager.get_pending_messages = lambda: [
            ("steward", {"type": "TASK_RESULT", "task_id": regular_task.task_id, "status": "success", "result": "done"})
        ]

        try:
            # Process IPC events
            kernel._process_ipc_events()

            # ENVOY history should be empty (this wasn't an ENVOY task)
            assert len(kernel._envoy_request_history) == 0
            # But task should be in completed_tasks
            assert regular_task.task_id in kernel._completed_tasks
        finally:
            kernel.process_manager.get_pending_messages = original_get_messages


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
