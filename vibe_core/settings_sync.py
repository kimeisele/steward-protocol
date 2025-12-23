#!/usr/bin/env python3
"""
SettingsSync - Bidirectional SETTINGS.md Interface

EXTRACTED FROM kernel_impl.py to reduce kernel complexity.

Implements the Command Queue pattern:
1. User writes commands in SETTINGS.md "Pending Commands" section
2. Kernel parses and validates commands
3. Commands execute against whitelisted settings only
4. Executed commands move to "Execution Ledger" section

Security:
- Whitelist enforcement (only approved settings can change)
- All changes audited to ledger
- Execution history visible in SETTINGS.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set

if TYPE_CHECKING:
    from vibe_core.io_service import KernelIOService

logger = logging.getLogger(__name__)


# =============================================================================
# SECURITY: Settings Whitelist
# =============================================================================
# Only these settings can be modified via SETTINGS.md
# This is a HARD SECURITY BOUNDARY - do not expand without review
EDITABLE_SETTINGS = {
    "kernel.log_level",  # Safe: logging verbosity only
    "kernel.verbose",  # Safe: verbose mode (true/false)
    # Provider/Execution settings (UI Enhancement)
    "provider",  # LLM provider selection (anthropic, openai, openrouter)
    "mode",  # Execution mode (simulation, live_fire)
    # FORBIDDEN - Security risks:
    # "kernel.status"        - Could bypass shutdown
    # "agent.*.capabilities" - Capability escalation
    # "ledger.*"             - Audit trail tampering
}


@dataclass
class SettingsSyncState:
    """
    State container for settings synchronization.

    Passed from kernel to SettingsSync methods.
    """

    last_modified: float = 0.0
    writing: bool = False
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    paused_agents: Set[str] = field(default_factory=set)
    agent_ids: Set[str] = field(default_factory=set)  # Known agent IDs


@dataclass
class SettingsExecutionResult:
    """Result of executing settings commands."""

    new_mtime: float = 0.0
    commands_executed: int = 0
    history_entries: List[Dict[str, Any]] = field(default_factory=list)
    paused_agents: Set[str] = field(default_factory=set)
    restart_agents: Set[str] = field(default_factory=set)  # Agents to restart
    refresh_topology: bool = False  # Flag to trigger topology refresh
    verbose_mode: Optional[bool] = None  # Verbose mode setting (if changed)
    # UI Enhancement: Provider and execution mode
    new_provider: Optional[str] = None  # Provider change (anthropic, openai, openrouter)
    new_execution_mode: Optional[str] = None  # Mode change (simulation, live_fire)


class SettingsSync:
    """
    SETTINGS.md bidirectional synchronization.

    Usage in kernel:
        sync = SettingsSync()

        # In tick loop:
        if sync.check_file_changed(state.last_modified):
            result = sync.sync_to_reality(state, ledger_callback)
            state.last_modified = result.new_mtime
            state.paused_agents = result.paused_agents
    """

    def __init__(self, settings_path: Path = Path("SETTINGS.md"), io_service: Optional["KernelIOService"] = None):
        """
        Initialize sync with path to SETTINGS.md.

        Args:
            settings_path: Path to SETTINGS.md file
            io_service: Optional KernelIOService for audited writes
        """
        self.settings_path = settings_path
        self._io_service = io_service

    def render_document(self, content: str) -> bool:
        """
        Render the document content.

        Preserves user sections via I/O Service (BIDIRECTIONAL mode).
        """
        return self._write_settings(content)

    def _write_settings(self, content: str) -> bool:
        """
        Write settings content through I/O Service or fallback.

        BIDIRECTIONAL doc type preserves user sections.

        Returns:
            True if write succeeded, False otherwise
        """
        if self._io_service:
            from vibe_core.io_service import DocumentType

            result = self._io_service.write_document(
                name=str(self.settings_path),
                content=content,
                doc_type=DocumentType.BIDIRECTIONAL,
                writer_id="SETTINGS_SYNC",
                add_header=False,  # SETTINGS.md has its own format
            )
            if not result.success:
                logger.error(f"❌ I/O Service write failed: {result.error}")
                return False
            return True
        else:
            # Fallback: direct write for standalone/test mode (no kernel)
            try:
                self.settings_path.write_text(content, encoding="utf-8")  # Fallback: standalone mode
                return True
            except Exception as e:
                logger.error(f"❌ Direct write failed: {e}")
                return False

    def check_file_changed(self, last_modified: float) -> bool:
        """
        Check if SETTINGS.md has been modified since last read.

        Fast mtime check - suitable for tick loop.

        Args:
            last_modified: Previous mtime to compare against

        Returns:
            True if file changed, False otherwise
        """
        try:
            if not self.settings_path.exists():
                return False

            current_mtime = self.settings_path.stat().st_mtime

            if current_mtime > last_modified:
                logger.debug(f"⚙️  SETTINGS.md changed (mtime: {current_mtime})")
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Failed to check settings file: {e}")
            return False

    def parse_commands(self) -> List[Dict[str, str]]:
        """
        Parse command queue from SETTINGS.md Pending Commands section.

        Supported command formats:
        - SET kernel.log_level=DEBUG
        - SET kernel.verbose=true
        - PAUSE agent.steward
        - RESUME agent.steward
        - RESTART agent.steward
        - REFRESH topology

        Returns:
            List of command dicts with 'action' and relevant params
        """
        try:
            if not self.settings_path.exists():
                return []

            content = self.settings_path.read_text()
            commands = []

            in_commands_section = False
            for line in content.split("\n"):
                line = line.strip()

                # Detect section boundaries
                if "## ⚡ Pending Commands" in line:
                    in_commands_section = True
                    continue

                if not in_commands_section:
                    continue

                # Skip blank lines
                if not line:
                    continue

                # Detect non-command lines (separators, headers, help text)
                is_separator = line.startswith("---") or line.startswith("___") or line.startswith("***")
                is_help_text = line.startswith("- `")

                if is_separator or is_help_text:
                    continue

                # Only lines starting with "- " are valid commands
                if not line.startswith("- "):
                    continue

                # Parse command text
                command_text = line[2:].strip()  # Skip "- "

                if command_text.startswith("SET "):
                    rest = command_text[4:].strip()
                    if "=" in rest:
                        key, value = rest.split("=", 1)
                        commands.append(
                            {
                                "action": "SET",
                                "key": key.strip(),
                                "value": value.strip(),
                            }
                        )

                elif command_text.startswith("PAUSE "):
                    agent_id = command_text[6:].strip()
                    commands.append(
                        {
                            "action": "PAUSE",
                            "agent_id": agent_id,
                        }
                    )

                elif command_text.startswith("RESUME "):
                    agent_id = command_text[7:].strip()
                    commands.append(
                        {
                            "action": "RESUME",
                            "agent_id": agent_id,
                        }
                    )

                elif command_text.startswith("RESTART "):
                    agent_id = command_text[8:].strip()
                    commands.append(
                        {
                            "action": "RESTART",
                            "agent_id": agent_id,
                        }
                    )

                elif command_text.startswith("REFRESH "):
                    target = command_text[8:].strip().lower()
                    commands.append(
                        {
                            "action": "REFRESH",
                            "target": target,
                        }
                    )

                else:
                    logger.warning(f"⚠️  Unknown command format: {command_text}")

            return commands

        except Exception as e:
            logger.error(f"❌ Failed to parse settings commands: {e}")
            return []

    def execute_commands(
        self,
        commands: List[Dict[str, str]],
        state: SettingsSyncState,
        ledger_callback: Optional[Callable[[str, str, Dict], None]] = None,
    ) -> SettingsExecutionResult:
        """
        Execute settings commands with whitelist validation.

        Args:
            commands: Parsed commands from parse_commands()
            state: Current sync state (paused_agents, agent_ids)
            ledger_callback: Optional callback to record events
                             Signature: (event_type, agent_id, details)

        Returns:
            SettingsExecutionResult with updated state
        """
        result = SettingsExecutionResult(
            paused_agents=set(state.paused_agents),
            history_entries=[],
        )

        if not commands:
            return result

        logger.info(f"⚙️  Executing {len(commands)} settings commands")

        for cmd in commands:
            record = {
                "command": cmd,
                "timestamp": datetime.utcnow().strftime("%H:%M:%S UTC"),
                "status": "SUCCESS",
                "reason": "",
            }

            try:
                action = cmd.get("action")

                if action == "SET":
                    self._execute_set(cmd, record, result)

                elif action == "PAUSE":
                    self._execute_pause(cmd, record, result, state.agent_ids)

                elif action == "RESUME":
                    self._execute_resume(cmd, record, result, state.agent_ids)

                elif action == "RESTART":
                    self._execute_restart(cmd, record, result, state.agent_ids)

                elif action == "REFRESH":
                    self._execute_refresh(cmd, record, result)

                else:
                    record["status"] = "FAILED"
                    record["reason"] = f"Unknown action: {action}"

                # Record to ledger if callback provided
                if ledger_callback:
                    ledger_callback(
                        "SETTINGS_COMMAND_EXECUTED",
                        "kernel",
                        {
                            "command": cmd,
                            "status": record["status"],
                            "reason": record["reason"],
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

            except Exception as e:
                record["status"] = "FAILED"
                record["reason"] = str(e)
                logger.error(f"❌ Command execution failed: {e}")

            result.history_entries.append(record)
            result.commands_executed += 1

        return result

    def _execute_set(
        self,
        cmd: Dict[str, str],
        record: Dict[str, Any],
        result: SettingsExecutionResult,
    ) -> None:
        """Execute SET command with whitelist check."""
        key = cmd.get("key", "")
        value = cmd.get("value", "")

        if key not in EDITABLE_SETTINGS:
            record["status"] = "FAILED"
            record["reason"] = f"Setting '{key}' not editable (whitelist violation)"
            logger.warning(f"⛔ BLOCKED: '{key}' not in whitelist {list(EDITABLE_SETTINGS)}")
            return

        if key == "kernel.log_level":
            self._set_log_level(value)
            record["reason"] = "Log level updated successfully"
            logger.info(f"✅ SET {key}={value}")

        elif key == "kernel.verbose":
            verbose = value.lower() in ("true", "1", "yes", "on")
            result.verbose_mode = verbose
            record["reason"] = f"Verbose mode {'enabled' if verbose else 'disabled'}"
            logger.info(f"✅ SET {key}={verbose}")

        elif key == "provider":
            # Validate provider name
            valid_providers = ("anthropic", "openai", "openrouter")
            provider = value.lower().strip()
            if provider not in valid_providers:
                record["status"] = "FAILED"
                record["reason"] = f"Invalid provider '{value}'. Use: {', '.join(valid_providers)}"
                logger.warning(f"⛔ Invalid provider: {value}")
                return
            result.new_provider = provider
            record["reason"] = f"Provider changed to '{provider}' (requires kernel restart)"
            logger.info(f"✅ SET provider={provider}")

        elif key == "mode":
            # Validate execution mode
            valid_modes = ("simulation", "live_fire")
            mode = value.lower().strip()
            if mode not in valid_modes:
                record["status"] = "FAILED"
                record["reason"] = f"Invalid mode '{value}'. Use: {', '.join(valid_modes)}"
                logger.warning(f"⛔ Invalid mode: {value}")
                return
            result.new_execution_mode = mode
            is_live = mode == "live_fire"
            record["reason"] = f"Execution mode changed to '{mode}'" + (" ⚠️ LIVE FIRE ENABLED" if is_live else "")
            logger.info(f"✅ SET mode={mode}")

    def _execute_pause(
        self,
        cmd: Dict[str, str],
        record: Dict[str, Any],
        result: SettingsExecutionResult,
        agent_ids: Set[str],
    ) -> None:
        """Execute PAUSE command."""
        agent_id = cmd.get("agent_id", "").replace("agent.", "")

        if agent_id in agent_ids:
            result.paused_agents.add(agent_id)
            record["reason"] = f"Agent '{agent_id}' paused successfully"
            logger.info(f"⏸️  Agent '{agent_id}' PAUSED")
        else:
            record["status"] = "FAILED"
            record["reason"] = f"Agent '{agent_id}' not found"
            logger.warning(f"⚠️  PAUSE failed: Agent '{agent_id}' not found")

    def _execute_resume(
        self,
        cmd: Dict[str, str],
        record: Dict[str, Any],
        result: SettingsExecutionResult,
        agent_ids: Set[str],
    ) -> None:
        """Execute RESUME command."""
        agent_id = cmd.get("agent_id", "").replace("agent.", "")

        if agent_id in result.paused_agents:
            result.paused_agents.discard(agent_id)
            record["reason"] = f"Agent '{agent_id}' resumed successfully"
            logger.info(f"▶️  Agent '{agent_id}' RESUMED")
        elif agent_id in agent_ids:
            record["status"] = "FAILED"
            record["reason"] = f"Agent '{agent_id}' is not paused"
            logger.warning(f"⚠️  RESUME failed: Agent '{agent_id}' is not paused")
        else:
            record["status"] = "FAILED"
            record["reason"] = f"Agent '{agent_id}' not found"
            logger.warning(f"⚠️  RESUME failed: Agent '{agent_id}' not found")

    def _execute_restart(
        self,
        cmd: Dict[str, str],
        record: Dict[str, Any],
        result: SettingsExecutionResult,
        agent_ids: Set[str],
    ) -> None:
        """Execute RESTART command (pause + resume in one)."""
        agent_id = cmd.get("agent_id", "").replace("agent.", "")

        if agent_id in agent_ids:
            result.restart_agents.add(agent_id)
            record["reason"] = f"Agent '{agent_id}' marked for restart"
            logger.info(f"🔄 Agent '{agent_id}' RESTART requested")
        else:
            record["status"] = "FAILED"
            record["reason"] = f"Agent '{agent_id}' not found"
            logger.warning(f"⚠️  RESTART failed: Agent '{agent_id}' not found")

    def _execute_refresh(
        self,
        cmd: Dict[str, str],
        record: Dict[str, Any],
        result: SettingsExecutionResult,
    ) -> None:
        """Execute REFRESH command for topology or docs."""
        target = cmd.get("target", "").lower()

        if target == "topology":
            result.refresh_topology = True
            record["reason"] = "Topology refresh requested"
            logger.info("🔄 REFRESH topology requested")
        else:
            record["status"] = "FAILED"
            record["reason"] = f"Unknown refresh target: '{target}'. Use 'topology'"
            logger.warning(f"⚠️  REFRESH failed: Unknown target '{target}'")

    def _set_log_level(self, level: str) -> None:
        """Set kernel log level (whitelisted setting)."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if level.upper() not in level_map:
            raise ValueError(f"Invalid log level: {level}. Must be one of {list(level_map.keys())}")

        logging.getLogger("VIBE_KERNEL").setLevel(level_map[level.upper()])
        logger.info(f"📊 Log level changed to {level.upper()}")

    def remove_executed_commands(self) -> None:
        """
        Remove executed commands from Pending Commands section.

        Commands move from Pending → Execution Ledger (visible in SETTINGS.md).
        """
        try:
            if not self.settings_path.exists():
                return

            content = self.settings_path.read_text()
            lines = content.split("\n")

            new_lines = []
            in_pending_section = False

            for line in lines:
                # Detect section boundaries
                if "## ⚡ Pending Commands" in line:
                    in_pending_section = True
                    new_lines.append(line)
                    continue

                if in_pending_section and line.strip().startswith("##"):
                    in_pending_section = False

                # Skip executed commands (but keep examples starting with "- `")
                if in_pending_section and line.strip().startswith("- ") and not line.strip().startswith("- `"):
                    continue

                new_lines.append(line)

            content = "\n".join(new_lines)
            if not self._write_settings(content):
                logger.error("❌ Failed to write SETTINGS.md after command cleanup")
            else:
                logger.debug("⚙️  Removed executed commands from SETTINGS.md")

        except Exception as e:
            logger.error(f"❌ Failed to remove executed commands: {e}")

    def sync_to_reality(
        self,
        state: SettingsSyncState,
        ledger_callback: Optional[Callable[[str, str, Dict], None]] = None,
    ) -> SettingsExecutionResult:
        """
        Full sync: Parse → Execute → Cleanup.

        Main entry point for kernel tick loop.

        Args:
            state: Current sync state
            ledger_callback: Optional ledger recording callback

        Returns:
            SettingsExecutionResult with new mtime and updated state
        """
        result = SettingsExecutionResult(paused_agents=set(state.paused_agents))

        try:
            # Parse commands
            commands = self.parse_commands()

            if not commands:
                logger.debug("⚙️  No pending commands in SETTINGS.md")
                return result

            logger.info(f"⚙️  Found {len(commands)} pending commands")

            # Execute commands
            result = self.execute_commands(commands, state, ledger_callback)

            # Remove executed commands
            self.remove_executed_commands()

            # Update mtime
            if self.settings_path.exists():
                result.new_mtime = self.settings_path.stat().st_mtime

            logger.info("✅ Settings synchronized to reality")

        except Exception as e:
            logger.error(f"❌ Settings sync failed: {e}")

        return result
