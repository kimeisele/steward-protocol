"""
OPUS-100: Shell Action - VEDA-4 Compliant Action Module.

This wraps ShellCortex in a BaseAction interface for auto-discovery.

Karmendriya: VAK (Speech) - The ability to speak/execute commands.

Handled Intent Types:
- shell_execute: Execute a shell command
- git_status: Get git status
- git_commit: Commit changes
- git_push: Push to remote

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/shell.py
    required: true
wiring:
  - pattern: "class ShellAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
  - pattern: "handled_intent_types.*shell_execute"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
-->
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from .base_action import ActionResult, BaseAction
from .shell import ShellCortex, ShellResult

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Action.Shell")


class ShellAction(BaseAction):
    """
    Shell Action - Execute CLI commands.

    Wraps ShellCortex in BaseAction interface for ActionLoader discovery.

    "VAK (Speech) - The power of the spoken command."
    """

    # OPUS-100: VEDA-4 auto-discovery
    name = "shell_action"

    # Intent types this action handles
    # NOTE: run_tests moved to TestAction (PAYU) - use TestAction for test operations
    handled_intent_types: Set[str] = {
        "shell_execute",
        "shell_safe",
        "git_status",
        "git_diff",
        "git_commit",
        "git_push",
        "run_command",
    }

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Shell Action.

        Args:
            workspace: Workspace root
            config: Configuration dict
        """
        super().__init__(workspace, config)
        self._shell_cortex = ShellCortex(workspace=self._workspace)
        logger.info("[SHELL_ACTION] Initialized - VAK (The Voice)")

    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute a shell-related intent.

        Routes to appropriate ShellCortex method based on intent type.

        Args:
            intent: The intent to execute

        Returns:
            ActionResult with execution status
        """
        intent_type = intent.type
        params = intent.params or {}

        try:
            if intent_type == "shell_execute":
                return self._handle_shell_execute(intent, params)
            elif intent_type == "shell_safe":
                return self._handle_shell_safe(intent, params)
            elif intent_type in ("git_status", "git_diff"):
                return self._handle_git_query(intent, params)
            elif intent_type == "git_commit":
                return self._handle_git_commit(intent, params)
            elif intent_type == "git_push":
                return self._handle_git_push(intent, params)
            elif intent_type == "run_command":
                return self._handle_run_command(intent, params)
            else:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent_type,
                    error=f"Unknown intent type for ShellAction: {intent_type}",
                )

        except Exception as e:
            logger.error(f"[SHELL_ACTION] Error handling {intent_type}: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=str(e),
            )

    def _handle_shell_safe(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle safe shell commands (auto-executable)."""
        command = params.get("command", [])
        if isinstance(command, str):
            command = command.split()

        result = self._shell_cortex.execute_safe(command)
        return self._shell_result_to_action_result(result, intent.type)

    def _handle_shell_execute(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle shell execute with approval."""
        command = params.get("command", [])
        approval_token = params.get("approval_token", "")

        if isinstance(command, str):
            command = command.split()

        result = self._shell_cortex.execute_with_approval(command, approval_token)
        return self._shell_result_to_action_result(result, intent.type)

    def _handle_git_query(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle git status/diff queries."""
        if intent.type == "git_status":
            result = self._shell_cortex.execute_safe(["git", "status"])
        else:
            result = self._shell_cortex.execute_safe(["git", "diff"])

        return self._shell_result_to_action_result(result, intent.type)

    def _handle_git_commit(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle git commit."""
        message = params.get("message", "Auto-commit by MANAS")
        approval_token = params.get("approval_token", "")

        result = self._shell_cortex.execute_with_approval(
            ["git", "commit", "-m", message],
            approval_token,
        )
        return self._shell_result_to_action_result(result, intent.type)

    def _handle_git_push(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle git push."""
        approval_token = params.get("approval_token", "")
        remote = params.get("remote", "origin")
        branch = params.get("branch", "")

        cmd = ["git", "push", remote]
        if branch:
            cmd.append(branch)

        result = self._shell_cortex.execute_with_approval(cmd, approval_token)
        return self._shell_result_to_action_result(result, intent.type)

    def _handle_run_command(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle generic run command."""
        command = params.get("command", [])
        approval_token = params.get("approval_token", "")

        if isinstance(command, str):
            command = command.split()

        # Check if it's a safe command first
        result = self._shell_cortex.execute_safe(command)
        if result.blocked:
            # Not safe, need approval
            result = self._shell_cortex.execute_with_approval(command, approval_token)

        return self._shell_result_to_action_result(result, intent.type)

    def _shell_result_to_action_result(self, shell_result: ShellResult, intent_type: str) -> ActionResult:
        """Convert ShellResult to ActionResult."""
        return ActionResult(
            success=shell_result.exit_code == 0 and not shell_result.blocked,
            action_name=self.name,
            intent_type=intent_type,
            result={
                "exit_code": shell_result.exit_code,
                "stdout": shell_result.stdout,
                "stderr": shell_result.stderr,
                "blocked": shell_result.blocked,
            },
            error=shell_result.error,
            metadata={"command": shell_result.command},
        )
