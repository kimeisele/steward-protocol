#!/usr/bin/env python3
"""
LEGACY TESTS: Kernel Markdown Interfaces (SETTINGS.md + ENVOY.md)
==================================================================

⚠️ DEPRECATED: This test file uses the OLD InterfacePlugin + Renderer pattern.

The architecture has been REPLACED by:
  - kernel.manifestation (ManifestationService)
  - Plugins implement get_manifestation_data()
  - See: vibe_core/services/manifestation_service.py
  - See: vibe_core/protocols/manifestation.py

These tests fail because:
  - get_renderer(kernel, "envoy") → "envoy" renderer doesn't exist
  - get_renderer(kernel, "settings") → "settings" renderer doesn't exist
  - The old renderers were replaced by ManifestationService

DO NOT try to "fix" these tests by adding old renderers back!
Instead: Write new tests for ManifestationService.

Original docstring preserved below for reference:
-------------------------------------------------
Tests the markdown-based control interfaces via the Unified Interface Plugin:

1. SETTINGS.md - Command Queue Interface
   - Renders configuration and agent status
   - Parses commands (SET, PAUSE, RESUME)
   - Executes commands with whitelist enforcement
   - Tracks execution history

2. ENVOY.md - Terminal Interface (Frontend Chat)
   - Renders terminal with Request/Status/History sections
   - Detects user requests via file change
   - Routes via UnifiedRouter (NO LLM)
   - Dispatches tasks async to scheduler
   - Updates status and history on completion

NO MOCKS. Real kernel, real scheduler, real UnifiedRouter.
"""

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# LEGACY: Skip entire module - architecture replaced by ManifestationService
pytestmark = pytest.mark.skip(
    reason="LEGACY: InterfacePlugin+Renderer replaced by ManifestationService. "
    "See vibe_core/services/manifestation_service.py"
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.plugins.test_orchestration import TestAgents, TestKernel


def get_interface_plugin(kernel):
    """Helper to get interface plugin."""
    for plugin in kernel._plugins:
        if plugin.plugin_id == "interface":
            return plugin

    available = [p.plugin_id for p in kernel._plugins]
    raise ValueError(f"Interface plugin not found. Available: {available}")


def get_renderer(kernel, renderer_name):
    """Helper to get renderer by name."""
    plugin = get_interface_plugin(kernel)
    if renderer_name not in plugin._renderers:
        raise ValueError(f"Renderer {renderer_name} not found")
    return plugin._renderers[renderer_name]


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_workdir():
    """Create a temporary working directory for tests."""
    # Configure logging
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("PLUGIN.LOADER").setLevel(logging.DEBUG)

    original_cwd = Path.cwd()
    temp_dir = tempfile.mkdtemp(prefix="vibe_test_")
    temp_path = Path(temp_dir)

    # Copy config files
    config_src = original_cwd / "config"
    if config_src.exists():
        shutil.copytree(config_src, temp_path / "config")

    # Copy playbook registry
    playbook_src = original_cwd / "vibe_core" / "playbook" / "_registry.yaml"
    if playbook_src.exists():
        playbook_dst = temp_path / "vibe_core" / "playbook"
        playbook_dst.mkdir(parents=True, exist_ok=True)
        shutil.copy(playbook_src, playbook_dst / "_registry.yaml")

    # Copy phoenix sections (required for PhoenixConfig to load paths)
    sections_src = original_cwd / "vibe_core" / "phoenix" / "sections"
    if sections_src.exists():
        sections_dst = temp_path / "vibe_core" / "phoenix" / "sections"
        shutil.copytree(sections_src, sections_dst)

    import os

    os.chdir(temp_dir)

    yield temp_path

    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kernel(temp_workdir):
    """Create a kernel with interface plugin loaded."""
    from vibe_core.plugin_loader import PluginLoader

    # Start with minimal kernel
    kernel = TestKernel.minimal()

    # Load plugins using ABSOLUTE path so it works in temp_workdir
    scan_path = Path(__file__).parent.parent.parent / "vibe_core" / "plugins"
    registry, _ = PluginLoader.discover_and_load(scan_paths=[scan_path])
    plugins = list(registry.values())

    # Include envoy and tools plugins (required for ENVOY tests)
    wanted = {"interface", "governance", "tools", "envoy"}
    filtered = [p for p in plugins if p.plugin_id in wanted]

    # Boot in correct order (tools before envoy)
    boot_order = ["tools", "governance", "interface", "envoy"]
    kernel._plugins = [p for pid in boot_order for p in filtered if p.plugin_id == pid]

    # Boot plugins
    for plugin in kernel._plugins:
        if hasattr(plugin, "on_boot"):
            try:
                plugin.on_boot(kernel)
            except Exception as e:
                print(f"❌ Failed to boot {plugin.plugin_id}: {e}")
                # We do NOT re-raise, so we can see which tests fail due to missing plugins
                # But typically this is fatal for that plugin.

    return kernel


@pytest.fixture
def booted_kernel(temp_workdir):
    """Create a fully booted kernel with agents (Lightweight Manual Boot)."""
    from vibe_core.plugin_loader import PluginLoader

    # Manual boot to avoid BootOrchestrator complexity/phases
    kernel = TestKernel.with_governance()

    # Load plugins (configured by @pytest.mark.vibe_plugins)
    # Use ABSOLUTE scan path
    scan_path = Path(__file__).parent.parent.parent / "vibe_core" / "plugins"

    registry, _ = PluginLoader.discover_and_load(scan_paths=[scan_path])
    plugins = list(registry.values())

    # Register and boot plugins
    kernel._plugins = []
    for plugin in plugins:
        kernel._plugins.append(plugin)

    # Boot plugins
    for plugin in plugins:
        if hasattr(plugin, "on_boot"):
            try:
                plugin.on_boot(kernel)
            except Exception as e:
                print(f"❌ Failed to boot {plugin.plugin_id}: {e}")

    # Register test agent using TestAgents fixture
    dummy_agent = TestAgents.compliant("steward")
    kernel._agent_registry["steward"] = dummy_agent

    return kernel


# =============================================================================
# SETTINGS.md TESTS
# =============================================================================


@pytest.mark.vibe_plugins("interface", "governance")
class TestSettingsMarkdownInterface:
    """Tests for SETTINGS.md command queue interface."""

    def test_render_settings_creates_file(self, kernel, temp_workdir):
        """Test that render_all creates SETTINGS.md."""
        settings_path = temp_workdir / "SETTINGS.md"
        assert not settings_path.exists()

        # Trigger render
        # Trigger render via InterfacePlugin
        get_interface_plugin(kernel).render_view("settings", force=True)

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
        # Mock agents
        from unittest.mock import MagicMock

        steward = MagicMock()
        steward.report_status.return_value = {"status": "ACTIVE", "tasks_completed": 5}
        herald = MagicMock()
        herald.report_status.return_value = {"status": "IDLE", "tasks_completed": 0}
        kernel._agent_registry = {"steward": steward, "herald": herald}

        # Trigger render via InterfacePlugin
        get_interface_plugin(kernel).render_view("settings", force=True)

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

        commands = get_renderer(kernel, "settings").sync.parse_commands()

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

        commands = get_renderer(kernel, "settings").sync.parse_commands()

        assert len(commands) == 2
        assert commands[0]["action"] == "PAUSE"
        assert commands[0]["agent_id"] == "agent.steward"
        assert commands[1]["action"] == "RESUME"
        assert commands[1]["agent_id"] == "agent.herald"

    def test_execute_set_log_level(self, kernel, temp_workdir):
        """Test executing SET kernel.log_level command."""
        commands = [{"action": "SET", "key": "kernel.log_level", "value": "DEBUG"}]

        # Execute via sync_to_reality (simulated)
        from vibe_core.settings_sync import SettingsSyncState

        state = SettingsSyncState(execution_history=[])
        result = get_renderer(kernel, "settings").sync.execute_commands(commands, state)

        # Check result history
        assert len(result.history_entries) == 1
        record = result.history_entries[0]
        assert record["status"] == "SUCCESS"
        assert "log_level" in record["command"]["key"]

    def test_execute_set_blocked_by_whitelist(self, kernel, temp_workdir):
        """Test that non-whitelisted settings are blocked."""
        commands = [{"action": "SET", "key": "kernel.status", "value": "STOPPED"}]

        # Execute via sync_to_reality (simulated)
        from vibe_core.settings_sync import SettingsSyncState

        state = SettingsSyncState(execution_history=[])
        result = get_renderer(kernel, "settings").sync.execute_commands(commands, state)

        # Should be blocked
        assert len(result.history_entries) == 1
        record = result.history_entries[0]
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

        # Get paused agents from governance plugin
        paused_agents = set()
        if (
            hasattr(booted_kernel, "governance")
            and booted_kernel.governance
            and hasattr(booted_kernel.governance, "get_paused_agents")
        ):
            paused_agents = booted_kernel.governance.get_paused_agents()

        assert agent_id not in paused_agents

        # Execute via sync_to_reality (simulated)
        from vibe_core.settings_sync import SettingsSyncState

        state = SettingsSyncState(paused_agents=paused_agents, agent_ids=set(booted_kernel._agent_registry.keys()))
        result = get_renderer(booted_kernel, "settings").sync.execute_commands(commands, state)

        # Update governance plugin state (normally done by sync_all)
        if hasattr(booted_kernel, "governance") and booted_kernel.governance:
            current_paused = booted_kernel.governance.get_paused_agents()
            new_paused = result.paused_agents
            for agent_id in current_paused - new_paused:
                booted_kernel.governance.resume_agent(agent_id)
            for agent_id in new_paused - current_paused:
                booted_kernel.governance.pause_agent(agent_id)

        assert agent_id in result.paused_agents
        assert result.history_entries[-1]["status"] == "SUCCESS"

    def test_execute_resume_agent(self, booted_kernel, temp_workdir):
        """Test RESUME command resumes a paused agent."""
        agent_ids = list(booted_kernel._agent_registry.keys())
        if not agent_ids:
            pytest.skip("No agents registered")

        agent_id = agent_ids[0]

        # First pause via governance plugin
        if (
            hasattr(booted_kernel, "governance")
            and booted_kernel.governance
            and hasattr(booted_kernel.governance, "pause_agent")
        ):
            booted_kernel.governance.pause_agent(agent_id)
        paused_agents = set()
        if (
            hasattr(booted_kernel, "governance")
            and booted_kernel.governance
            and hasattr(booted_kernel.governance, "get_paused_agents")
        ):
            paused_agents = booted_kernel.governance.get_paused_agents()
        assert agent_id in paused_agents

        # Then resume
        commands = [{"action": "RESUME", "agent_id": f"agent.{agent_id}"}]

        # Execute via sync_to_reality (simulated)
        from vibe_core.settings_sync import SettingsSyncState

        state = SettingsSyncState(paused_agents=paused_agents, agent_ids=set(booted_kernel._agent_registry.keys()))
        result = get_renderer(booted_kernel, "settings").sync.execute_commands(commands, state)

        # Update governance plugin state
        if hasattr(booted_kernel, "governance") and booted_kernel.governance:
            current_paused = booted_kernel.governance.get_paused_agents()
            new_paused = result.paused_agents
            for agent_id in current_paused - new_paused:
                booted_kernel.governance.resume_agent(agent_id)
            for agent_id in new_paused - current_paused:
                booted_kernel.governance.pause_agent(agent_id)

        assert agent_id not in result.paused_agents
        assert result.history_entries[-1]["status"] == "SUCCESS"

    def test_file_change_detection(self, kernel, temp_workdir):
        """Test that file changes are detected via mtime."""
        settings_path = temp_workdir / "SETTINGS.md"

        renderer = get_renderer(kernel, "settings")

        # No file = no change
        assert not renderer.sync.check_file_changed(renderer.state.last_modified)

        # Create file
        settings_path.write_text("# SETTINGS")
        renderer.state.last_modified = 0  # Reset

        # File exists and mtime > last_modified
        assert renderer.sync.check_file_changed(renderer.state.last_modified)

        # Update last_modified
        renderer.state.last_modified = settings_path.stat().st_mtime

        # No change now
        assert not renderer.sync.check_file_changed(renderer.state.last_modified)


# =============================================================================
# ENVOY.md TESTS (Terminal/Frontend Chat Interface)
# =============================================================================


@pytest.mark.vibe_plugins("interface", "governance")
class TestEnvoyTerminalInterface:
    """Tests for ENVOY.md terminal interface (markdown frontend chat)."""

    def test_render_envoy_creates_file(self, kernel, temp_workdir):
        """Test that render creates ENVOY.md."""
        envoy_path = temp_workdir / "ENVOY.md"
        assert not envoy_path.exists()

        # Verify kernel.io exists (debug)
        assert hasattr(kernel, "io"), "kernel.io should exist"

        # Trigger render via InterfacePlugin
        get_interface_plugin(kernel).render_view("envoy", force=True)
        content = envoy_path.read_text()

        # Verify structure (no emojis in headers)
        assert "# ENVOY TERMINAL" in content
        assert "## 💬 Request" in content
        assert "## Status" in content
        assert "## Response History" in content
        assert "## Available Routes" in content

    def test_render_envoy_shows_available_routes(self, kernel, temp_workdir):
        """Test that ENVOY.md shows UnifiedRouter routes."""
        get_interface_plugin(kernel).render_view("envoy", force=True)

        content = (temp_workdir / "ENVOY.md").read_text()

        # Should show some routes from UnifiedRouter
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

        content = get_renderer(kernel, "envoy").sync.extract_request_content()

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

        content = get_renderer(kernel, "envoy").sync.extract_request_content()

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

        content = get_renderer(kernel, "envoy").sync.extract_request_content()

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

        requests = get_renderer(kernel, "envoy").sync.parse_requests()

        assert len(requests) == 2
        assert "start a new project" in requests
        assert "show me the status" in requests

    def test_file_change_detection(self, kernel, temp_workdir):
        """Test that ENVOY.md changes are detected via mtime."""
        envoy_path = temp_workdir / "ENVOY.md"
        renderer = get_renderer(kernel, "envoy")

        # No file = no change
        assert not renderer.sync.check_file_changed(renderer.state.last_modified)

        # Create file
        envoy_path.write_text("# ENVOY")
        renderer.state.last_modified = 0

        # File exists and mtime > last_modified
        assert renderer.sync.check_file_changed(renderer.state.last_modified)

        # Update last_modified
        renderer.state.last_modified = envoy_path.stat().st_mtime

        # No change now
        assert not renderer.sync.check_file_changed(renderer.state.last_modified)

    def test_dispatch_request_routes_via_playbook(self, kernel, temp_workdir):
        """Test that requests are routed via UnifiedRouter (NO LLM)."""
        # We test this via sync_to_reality since dispatch is internal to it now
        from vibe_core.envoy_sync import EnvoySyncState
        from vibe_core.scheduling import Task

        state = EnvoySyncState()

        # Mock callbacks
        def mock_submit(task):
            return "task_id_123"

        # Actually, let's just write to file and call sync_to_reality
        envoy_path = temp_workdir / "ENVOY.md"
        envoy_path.write_text("# ENVOY\n## 💬 Request\n\nstart a new project")

        result = get_renderer(kernel, "envoy").sync.sync_to_reality(
            state,
            router_callback=kernel.envoy.route,  # OPUS Phase 2: Use public API
            submit_callback=mock_submit,
            task_factory=lambda p: Task(agent_id=p["agent_id"], payload=p["payload"]),
        )

        assert len(result.pending_tasks) == 1
        task_meta = list(result.pending_tasks.values())[0]
        assert task_meta["status"] == "QUEUED"
        assert task_meta["route"] is not None
        # Should match bootstrap or similar pattern
        assert task_meta["confidence"] in ["explicit", "contextual", "suggested"]

    def test_dispatch_request_queues_task(self, kernel, temp_workdir):
        """Test that dispatched requests create tasks in scheduler."""
        # Write request to file
        envoy_path = temp_workdir / "ENVOY.md"
        envoy_path.write_text("# ENVOY\n## 💬 Request\n\ncheck project status")

        # Sync via manager (using refactored flow)
        renderer = get_renderer(kernel, "envoy")
        renderer.state.last_modified = 0
        get_interface_plugin(kernel).render_view("envoy", force=True)

        # Task should be in pending tasks
        assert len(renderer.state.pending_tasks) == 1
        task_meta = list(renderer.state.pending_tasks.values())[0]
        assert task_meta["status"] == "QUEUED"

        # Verify task in scheduler
        assert kernel._scheduler.get_queue_status()["queue_length"] == 1

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
        renderer = get_renderer(kernel, "envoy")
        renderer.state.last_modified = 0

        # Sync
        # Trigger render via InterfacePlugin
        get_interface_plugin(kernel).render_view("envoy", force=True)

        # Should have dispatched task
        assert len(renderer.state.pending_tasks) == 1

        # Request should be cleared from Request section
        new_content = envoy_path.read_text()
        # Split on "## Status" (no emoji in actual output)
        request_section = new_content.split("## Status")[0]
        assert "initialize the system" not in request_section

    def test_update_task_status_moves_to_history(self, kernel, temp_workdir):
        """Test that completing a task moves it from pending to history."""
        # Manually add to pending tasks
        task_id = "task_123"
        renderer = get_renderer(kernel, "envoy")
        renderer.state.pending_tasks[task_id] = {"task_id": task_id, "status": "QUEUED", "request": "test request"}

        assert task_id in renderer.state.pending_tasks
        assert len(renderer.state.request_history) == 0

        # The EnvoyRenderer._process_completed_tasks() uses kernel.ledger.get_task()
        # which looks for events with task_id at top level (not in details)
        # So we need to append the event directly in the same format as record_completion()
        kernel.ledger.events.append(
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "event_type": "task_completed",
                "task_id": task_id,
                "agent_id": "test",
                "result": {"message": "Task done successfully"},
            }
        )

        # Trigger render via InterfacePlugin
        get_interface_plugin(kernel).render_view("envoy", force=True)

        # Should be in history, not pending
        assert task_id not in renderer.state.pending_tasks
        assert len(renderer.state.request_history) == 1
        assert renderer.state.request_history[0]["status"] == "COMPLETED"

    def test_render_shows_pending_tasks(self, kernel, temp_workdir):
        """Test that pending tasks are shown in Status section."""
        # Add to pending
        task_id = "task_123"
        renderer = get_renderer(kernel, "envoy")
        renderer.state.pending_tasks[task_id] = {
            "task_id": task_id,
            "status": "QUEUED",
            "request": "build new feature",
        }

        # Trigger render via InterfacePlugin
        get_interface_plugin(kernel).render_view("envoy", force=True)

        content = (temp_workdir / "ENVOY.md").read_text()

        # Should show pending task in status
        assert "QUEUED" in content
        assert "build new feature" in content

    def test_render_shows_history(self, kernel, temp_workdir):
        """Test that completed tasks are shown in Response History."""
        # Add to pending then complete
        task_id = "task_123"
        renderer = get_renderer(kernel, "envoy")
        renderer.state.pending_tasks[task_id] = {
            "task_id": task_id,
            "status": "QUEUED",
            "request": "old request",
        }

        # Record completion in ledger - same format as record_completion() uses
        # get_task() looks for task_id at top level, not in details
        kernel.ledger.events.append(
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "event_type": "task_completed",
                "task_id": task_id,
                "agent_id": "test",
                "result": {"message": "Done!"},
            }
        )

        # Trigger render via InterfacePlugin
        get_interface_plugin(kernel).render_view("envoy", force=True)

        content = (temp_workdir / "ENVOY.md").read_text()

        # Should show in history
        assert "old request" in content
        assert "Done!" in content or "COMPLETED" in content

    def test_preserves_user_request_on_render(self, kernel, temp_workdir):
        """Test that user's request is preserved when re-rendering."""
        # First render
        get_interface_plugin(kernel).render_view("envoy", force=True)

        # User writes a request
        envoy_path = temp_workdir / "ENVOY.md"
        content = envoy_path.read_text()
        content = content.replace(
            "_No pending request. Write your request above this line._", "User's important request here"
        )
        envoy_path.write_text(content)

        # Re-render (should preserve user request)
        get_interface_plugin(kernel).render_view("envoy", force=True)

        new_content = envoy_path.read_text()
        assert "User's important request here" in new_content


# =============================================================================
# FULL LIFECYCLE TESTS
# =============================================================================


@pytest.mark.vibe_plugins("interface", "governance")
class TestFullLifecycle:
    """End-to-end tests for the complete request lifecycle."""

    @pytest.mark.skip(
        reason="Requires full environment setup in temp_workdir (CONSTITUTION.md, circuits, pyproject.toml)"
    )
    def test_settings_command_lifecycle(self, booted_kernel, temp_workdir):
        """Test: Write command → tick → execute → history updated."""
        settings_path = temp_workdir / "SETTINGS.md"

        # Generate initial SETTINGS.md
        booted_kernel._pulse()
        get_interface_plugin(booted_kernel).on_tick_post(booted_kernel)
        assert settings_path.exists()

        # Add a command
        content = settings_path.read_text()
        # Insert command after "Pending Commands" header
        content = content.replace(
            "_No pending commands. Add commands above this line._", "- SET kernel.log_level=ERROR"
        )
        settings_path.write_text(content)

        renderer = get_renderer(booted_kernel, "settings")
        renderer.state.last_modified = 0  # Force change detection

        # Run tick (processes commands)
        # Run tick (processes commands)
        # Note: InterfacePlugin.on_tick_post calls render(), which calls sync.
        booted_kernel.tick()
        # Manual trigger because tick() returns early if queue is empty
        get_interface_plugin(booted_kernel).on_tick_post(booted_kernel)

        # Command should be executed
        assert len(renderer.state.execution_history) >= 1
        # Find our command in history
        found = any(r.get("command", {}).get("value") == "ERROR" for r in renderer.state.execution_history)
        assert found, "Command not found in execution history"

    @pytest.mark.skip(
        reason="Requires full environment setup in temp_workdir (CONSTITUTION.md, circuits, pyproject.toml)"
    )
    def test_envoy_request_lifecycle(self, booted_kernel, temp_workdir):
        """Test: Write request → tick → dispatch → task queued."""
        envoy_path = temp_workdir / "ENVOY.md"

        # Generate initial ENVOY.md
        booted_kernel._pulse()
        get_interface_plugin(booted_kernel).on_tick_post(booted_kernel)
        assert envoy_path.exists()

        # Add a request
        content = envoy_path.read_text()
        content = content.replace("_No pending request. Write your request above this line._", "start new development")
        envoy_path.write_text(content)

        renderer = get_renderer(booted_kernel, "envoy")
        renderer.state.last_modified = 0  # Force change detection

        # Run tick (processes request)
        booted_kernel.tick()
        # Manual trigger because tick() returns early if queue is empty
        get_interface_plugin(booted_kernel).on_tick_post(booted_kernel)

        # Request should be dispatched (either pending or already completed)
        assert len(renderer.state.pending_tasks) + len(renderer.state.request_history) >= 1

        # Check task was routed
        if renderer.state.pending_tasks:
            task_meta = list(renderer.state.pending_tasks.values())[0]
        else:
            task_meta = renderer.state.request_history[-1]
        assert task_meta["status"] in ["QUEUED", "COMPLETED", "FAILED"]
        assert task_meta["route"] is not None
