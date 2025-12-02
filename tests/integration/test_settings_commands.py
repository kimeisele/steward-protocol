#!/usr/bin/env python3
"""
Test: Settings Commands (SETTINGS.md Command Queue)
====================================================

Tests the full settings command pipeline:
1. SettingsSync - Parses commands from SETTINGS.md
2. SettingsExecutor - Executes commands with kernel access

Commands tested:
- SET kernel.log_level=DEBUG/INFO/...
- SET kernel.verbose=true/false
- PAUSE agent.<id>
- RESUME agent.<id>
- RESTART agent.<id>
- REFRESH topology
"""

import logging
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.settings_executor import SettingsExecutor, get_executor
from vibe_core.settings_sync import (
    EDITABLE_SETTINGS,
    SettingsExecutionResult,
    SettingsSync,
    SettingsSyncState,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_settings_file():
    """Create a temporary SETTINGS.md file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def settings_sync(temp_settings_file):
    """Create a SettingsSync instance with temp file."""
    return SettingsSync(settings_path=temp_settings_file)


@pytest.fixture
def executor():
    """Create a SettingsExecutor instance."""
    return SettingsExecutor()


@pytest.fixture
def mock_kernel():
    """Create a mock kernel for testing executor."""
    kernel = MagicMock()
    kernel.process_manager = MagicMock()
    kernel.process_manager.processes = {}
    return kernel


# =============================================================================
# SETTINGS SYNC TESTS - Parsing
# =============================================================================


class TestSettingsSyncParsing:
    """Tests for SettingsSync command parsing."""

    def test_parse_set_log_level(self, settings_sync, temp_settings_file):
        """SET kernel.log_level command is parsed correctly."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands
- SET kernel.log_level=DEBUG
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 1
        assert commands[0]["action"] == "SET"
        assert commands[0]["key"] == "kernel.log_level"
        assert commands[0]["value"] == "DEBUG"

    def test_parse_set_verbose(self, settings_sync, temp_settings_file):
        """SET kernel.verbose command is parsed correctly."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands
- SET kernel.verbose=true
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 1
        assert commands[0]["action"] == "SET"
        assert commands[0]["key"] == "kernel.verbose"
        assert commands[0]["value"] == "true"

    def test_parse_pause_agent(self, settings_sync, temp_settings_file):
        """PAUSE agent.<id> command is parsed correctly."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands
- PAUSE agent.scribe
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 1
        assert commands[0]["action"] == "PAUSE"
        assert commands[0]["agent_id"] == "agent.scribe"

    def test_parse_resume_agent(self, settings_sync, temp_settings_file):
        """RESUME agent.<id> command is parsed correctly."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands
- RESUME agent.herald
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 1
        assert commands[0]["action"] == "RESUME"
        assert commands[0]["agent_id"] == "agent.herald"

    def test_parse_restart_agent(self, settings_sync, temp_settings_file):
        """RESTART agent.<id> command is parsed correctly."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands
- RESTART agent.oracle
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 1
        assert commands[0]["action"] == "RESTART"
        assert commands[0]["agent_id"] == "agent.oracle"

    def test_parse_refresh_topology(self, settings_sync, temp_settings_file):
        """REFRESH topology command is parsed correctly."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands
- REFRESH topology
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 1
        assert commands[0]["action"] == "REFRESH"
        assert commands[0]["target"] == "topology"

    def test_parse_multiple_commands(self, settings_sync, temp_settings_file):
        """Multiple commands are parsed in order."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands
- SET kernel.log_level=DEBUG
- PAUSE agent.scribe
- REFRESH topology
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 3
        assert commands[0]["action"] == "SET"
        assert commands[1]["action"] == "PAUSE"
        assert commands[2]["action"] == "REFRESH"

    def test_parse_ignores_examples(self, settings_sync, temp_settings_file):
        """Example lines (with backticks) are ignored."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands
- `SET kernel.log_level=DEBUG` - This is an example
- SET kernel.log_level=INFO
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 1
        assert commands[0]["value"] == "INFO"

    def test_parse_empty_section(self, settings_sync, temp_settings_file):
        """Empty pending commands section returns empty list."""
        temp_settings_file.write_text("""
## ⚡ Pending Commands

_No pending commands._

## Other Section
""")
        commands = settings_sync.parse_commands()

        assert len(commands) == 0


# =============================================================================
# SETTINGS SYNC TESTS - Execution
# =============================================================================


class TestSettingsSyncExecution:
    """Tests for SettingsSync command execution."""

    def test_execute_set_log_level(self, settings_sync):
        """SET kernel.log_level changes log level."""
        commands = [{"action": "SET", "key": "kernel.log_level", "value": "DEBUG"}]
        state = SettingsSyncState(agent_ids=set())

        result = settings_sync.execute_commands(commands, state)

        assert result.commands_executed == 1
        assert result.history_entries[0]["status"] == "SUCCESS"

    def test_execute_set_verbose(self, settings_sync):
        """SET kernel.verbose sets verbose_mode flag."""
        commands = [{"action": "SET", "key": "kernel.verbose", "value": "true"}]
        state = SettingsSyncState(agent_ids=set())

        result = settings_sync.execute_commands(commands, state)

        assert result.verbose_mode is True
        assert result.history_entries[0]["status"] == "SUCCESS"

    def test_execute_pause_agent(self, settings_sync):
        """PAUSE agent adds to paused_agents set."""
        commands = [{"action": "PAUSE", "agent_id": "agent.scribe"}]
        state = SettingsSyncState(agent_ids={"scribe", "herald"})

        result = settings_sync.execute_commands(commands, state)

        assert "scribe" in result.paused_agents
        assert result.history_entries[0]["status"] == "SUCCESS"

    def test_execute_pause_unknown_agent(self, settings_sync):
        """PAUSE unknown agent fails gracefully."""
        commands = [{"action": "PAUSE", "agent_id": "agent.unknown"}]
        state = SettingsSyncState(agent_ids={"scribe"})

        result = settings_sync.execute_commands(commands, state)

        assert result.history_entries[0]["status"] == "FAILED"
        assert "not found" in result.history_entries[0]["reason"]

    def test_execute_resume_agent(self, settings_sync):
        """RESUME agent removes from paused_agents set."""
        commands = [{"action": "RESUME", "agent_id": "agent.scribe"}]
        state = SettingsSyncState(agent_ids={"scribe"}, paused_agents={"scribe"})

        result = settings_sync.execute_commands(commands, state)

        assert "scribe" not in result.paused_agents
        assert result.history_entries[0]["status"] == "SUCCESS"

    def test_execute_restart_agent(self, settings_sync):
        """RESTART agent adds to restart_agents set."""
        commands = [{"action": "RESTART", "agent_id": "agent.oracle"}]
        state = SettingsSyncState(agent_ids={"oracle"})

        result = settings_sync.execute_commands(commands, state)

        assert "oracle" in result.restart_agents
        assert result.history_entries[0]["status"] == "SUCCESS"

    def test_execute_refresh_topology(self, settings_sync):
        """REFRESH topology sets refresh_topology flag."""
        commands = [{"action": "REFRESH", "target": "topology"}]
        state = SettingsSyncState(agent_ids=set())

        result = settings_sync.execute_commands(commands, state)

        assert result.refresh_topology is True
        assert result.history_entries[0]["status"] == "SUCCESS"

    def test_whitelist_enforcement(self, settings_sync):
        """Settings not in whitelist are rejected."""
        commands = [{"action": "SET", "key": "kernel.dangerous", "value": "evil"}]
        state = SettingsSyncState(agent_ids=set())

        result = settings_sync.execute_commands(commands, state)

        assert result.history_entries[0]["status"] == "FAILED"
        assert "whitelist" in result.history_entries[0]["reason"].lower()


# =============================================================================
# SETTINGS EXECUTOR TESTS
# =============================================================================


class TestSettingsExecutor:
    """Tests for SettingsExecutor command execution."""

    def test_execute_verbose_mode_enable(self, executor):
        """Verbose mode enable sets loggers to DEBUG."""
        original_level = logging.getLogger().level

        executor._execute_verbose_mode(True)

        assert logging.getLogger().level == logging.DEBUG

        # Cleanup
        logging.getLogger().setLevel(original_level)

    def test_execute_verbose_mode_disable(self, executor):
        """Verbose mode disable sets loggers to INFO."""
        logging.getLogger().setLevel(logging.DEBUG)

        executor._execute_verbose_mode(False)

        assert logging.getLogger().level == logging.INFO

    def test_execute_refresh_topology(self, executor, mock_kernel):
        """REFRESH topology calls refresh_topology function."""
        with patch("vibe_core.topology.refresh_topology") as mock_refresh:
            mock_refresh.return_value = MagicMock(agents={})

            executor._execute_refresh_topology(mock_kernel)

            mock_refresh.assert_called_once_with(kernel=mock_kernel)

    def test_execute_restart_nonexistent_agent(self, executor, mock_kernel):
        """RESTART nonexistent agent logs warning."""
        # Agent not in processes
        mock_kernel.process_manager.processes = {}

        # Should not raise, just log warning
        executor._execute_restarts({"scribe"}, mock_kernel)

    def test_execute_empty_result(self, executor, mock_kernel):
        """Empty result does nothing."""
        result = SettingsExecutionResult()

        # Should not raise
        executor.execute(result, mock_kernel)

    def test_execute_full_result(self, executor, mock_kernel):
        """Full result executes all handlers."""
        result = SettingsExecutionResult(
            restart_agents={"scribe"},
            refresh_topology=True,
            verbose_mode=True,
        )

        with patch.object(executor, "_execute_restarts") as mock_restart:
            with patch.object(executor, "_execute_refresh_topology") as mock_refresh:
                with patch.object(executor, "_execute_verbose_mode") as mock_verbose:
                    executor.execute(result, mock_kernel)

                    mock_restart.assert_called_once()
                    mock_refresh.assert_called_once()
                    mock_verbose.assert_called_once_with(True)


# =============================================================================
# WHITELIST TESTS
# =============================================================================


class TestSettingsWhitelist:
    """Tests for settings whitelist security."""

    def test_log_level_in_whitelist(self):
        """kernel.log_level is in whitelist."""
        assert "kernel.log_level" in EDITABLE_SETTINGS

    def test_verbose_in_whitelist(self):
        """kernel.verbose is in whitelist."""
        assert "kernel.verbose" in EDITABLE_SETTINGS

    def test_dangerous_not_in_whitelist(self):
        """Dangerous settings are not in whitelist."""
        assert "kernel.status" not in EDITABLE_SETTINGS
        assert "agent.capabilities" not in EDITABLE_SETTINGS
        assert "ledger.path" not in EDITABLE_SETTINGS


# =============================================================================
# SINGLETON TESTS
# =============================================================================


class TestSettingsExecutorSingleton:
    """Tests for executor singleton pattern."""

    def test_get_executor_returns_same_instance(self):
        """get_executor() returns singleton instance."""
        executor1 = get_executor()
        executor2 = get_executor()

        assert executor1 is executor2
