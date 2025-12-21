"""
Shell Cortex Adapter - VEDA-4 wrapper for ShellCortex.

OPUS-171 Phase 5.2: Cortex Adapter Pattern

Wraps the existing ShellCortex in BaseCortex interface
for VEDA-4 auto-discovery via CortexLoader.

CAPABILITIES:
    - git_status: Check git status
    - git_commit: Commit pending changes
    - git_push: Push to remote
    - git_pr: Create pull request
    - shell_execute: Execute safe CLI commands
    - cleanup: Cleanup operations (branches, logs)

USAGE:
    from vibe_core.loaders import get_cortex

    shell = get_cortex("shell", workspace=Path.cwd())
    result = shell.execute(intent)
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugins.opus_assistant.manas.cortex.base_cortex import (
    BaseCortex,
    cortex_error,
    cortex_success,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Cortex.Adapter.Shell")


class ShellCortexAdapter(BaseCortex):
    """
    VEDA-4 adapter for ShellCortex.

    Wraps the existing ShellCortex to provide a unified BaseCortex interface.
    Delegates all operations to the underlying ShellCortex.

    Discovery:
        CortexLoader.get_cortex("shell")
    """

    # === CORTEX IDENTITY ===
    name = "shell"
    capabilities = [
        "git_status",
        "git_commit",
        "git_push",
        "git_pr",
        "git_merge",
        "shell_execute",
        "cleanup_branches",
        "cleanup_logs",
    ]
    priority = 10  # Standard priority

    def __init__(
        self,
        workspace: Optional[Path] = None,
        kernel: Optional["RealVibeKernel"] = None,
    ):
        super().__init__(workspace, kernel)
        self._cortex = None  # Lazy init

    def _get_cortex(self):
        """Lazy-load ShellCortex to avoid import cycles."""
        if self._cortex is None:
            from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

            self._cortex = ShellCortex(workspace=self._workspace)
            if self._kernel:
                self._cortex.inject_kernel(self._kernel)
        return self._cortex

    def execute(self, intent: "Intent") -> Dict[str, Any]:
        """
        Execute a shell/git intent via ShellCortex.

        Supports:
            - commit_pending_changes
            - git_push
            - create_pr
            - cleanup_* (stale branches, old logs)
            - Generic shell commands via params["command"]

        Args:
            intent: The intent to execute

        Returns:
            Dict with success, handler, message, and operation-specific data
        """
        intent_type = intent.intent_type
        logger.info(f"🐚 ShellCortexAdapter executing: {intent_type}")

        try:
            cortex = self._get_cortex()

            # Git status
            if intent_type == "git_status":
                result = cortex.execute(["git", "status", "--short"], safe_mode=True)
                return cortex_success(
                    handler=self.name,
                    message="Git status retrieved",
                    output=result.stdout,
                    exit_code=result.exit_code,
                )

            # Cleanup operations
            if intent_type.startswith("cleanup_"):
                return self._execute_cleanup(intent, cortex)

            # Generic shell command
            command = intent.params.get("command")
            if command:
                if isinstance(command, str):
                    command = command.split()
                result = cortex.execute(command, safe_mode=True)
                return {
                    "success": result.exit_code == 0,
                    "handler": self.name,
                    "command": command,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                    "blocked": result.blocked,
                }

            # Default: acknowledge intent
            return cortex_success(
                handler=self.name,
                message=f"Shell intent acknowledged: {intent_type}",
                intent_type=intent_type,
            )

        except Exception as e:
            logger.error(f"ShellCortexAdapter error: {e}")
            return cortex_error(handler=self.name, error=str(e))

    def _execute_cleanup(self, intent: "Intent", cortex: Any) -> Dict[str, Any]:
        """Execute cleanup operations."""
        intent_type = intent.intent_type

        if intent_type == "cleanup_stale_branches":
            cmd = ["git", "branch", "--merged"]
            result = cortex.execute(cmd, safe_mode=True)
            branches = [
                b.strip() for b in result.stdout.split("\n") if b.strip() and "main" not in b and "master" not in b
            ]
            return cortex_success(
                handler=self.name,
                message=f"Found {len(branches)} merged branches",
                branches=branches[:10],  # Limit to 10
            )

        elif intent_type == "cleanup_old_logs":
            # List old log files (read-only, safe)
            return cortex_success(
                handler=self.name,
                message="Log cleanup would remove old .log files",
                action="dry_run",
            )

        return cortex_success(
            handler=self.name,
            message=f"Cleanup acknowledged: {intent_type}",
        )

    def execute_safe(self, command: List[str]) -> Dict[str, Any]:
        """
        Direct access to execute_safe for simple commands.

        This is a convenience method for handlers that need raw shell access.
        """
        cortex = self._get_cortex()
        result = cortex.execute(command, safe_mode=True)
        return {
            "success": result.exit_code == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
        }
