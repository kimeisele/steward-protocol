"""
System Maintenance Agent - ARCH-044

Agent for system-level maintenance operations (git sync, dependency updates, etc.).
This is distinct from the MaintenanceSpecialist which handles production monitoring.

Responsibilities:
    - Perform system updates (git pull + uv sync)
    - Verify system integrity before/after updates
    - Handle rollback on update failure (future)
    - Report system sync status to operator

This agent implements the VibeAgent protocol for kernel-based dispatch.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any

from vibe_core.agent_protocol import AgentResponse, VibeAgent
from vibe_core.scheduling import Task

logger = logging.getLogger(__name__)


class SystemMaintenanceAgent(VibeAgent):
    """
    Agent for system-level maintenance operations (ARCH-044).

    This agent handles git synchronization and dependency management.
    It is invoked by the operator when the kernel detects out-of-sync status.

    Capabilities:
        - perform_system_update: Execute git pull + uv sync
        - verify_integrity: Pre-flight checks before update
        - check_sync_status: Query current git sync state

    Example:
        >>> agent = SystemMaintenanceAgent()
        >>> task = Task(
        ...     agent_id="system-maintenance",
        ...     payload={"operation": "perform_system_update"}
        ... )
        >>> response = agent.process(task)
        >>> print(response.success)  # True if update succeeded
    """

    def __init__(self, project_root: Path | None = None):
        """
        Initialize SystemMaintenanceAgent.

        Args:
            project_root: Path to project root (defaults to current directory)
        """
        self._agent_id = "system-maintenance"
        self.project_root = project_root or Path.cwd()

    @property
    def agent_id(self) -> str:
        """Return agent identifier."""
        return self._agent_id

    @property
    def capabilities(self) -> list[str]:
        """
        Return list of supported operations.

        Returns:
            list[str]: Capability names
        """
        return [
            "perform_system_update",
            "verify_integrity",
            "check_sync_status",
        ]

    def process(self, task: Task) -> AgentResponse:
        """
        Process a maintenance task.

        Supported operations (via task.payload["operation"]):
            - "perform_system_update": Execute git pull + uv sync
            - "verify_integrity": Run pre-flight checks
            - "check_sync_status": Return current git status

        Args:
            task: Task with payload containing "operation" key

        Returns:
            AgentResponse: Result of the operation

        Example:
            >>> task = Task(
            ...     agent_id="system-maintenance",
            ...     payload={"operation": "perform_system_update"}
            ... )
            >>> response = agent.process(task)
        """
        operation = task.payload.get("operation")

        if not operation:
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=False,
                output=None,
                error="Missing 'operation' key in task payload",
            )

        logger.info(f"SystemMaintenanceAgent: Processing operation '{operation}'")

        # Route to operation handler
        if operation == "perform_system_update":
            return self._perform_system_update(task)
        elif operation == "verify_integrity":
            return self._verify_integrity(task)
        elif operation == "check_sync_status":
            return self._check_sync_status(task)
        else:
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=False,
                output=None,
                error=f"Unknown operation: '{operation}'. Available: {self.capabilities}",
            )

    def _perform_system_update(self, task: Task) -> AgentResponse:
        """
        Execute system update (git pull + uv sync).

        This performs:
        1. Pre-flight integrity check
        2. Git pull from remote
        3. UV sync to update dependencies
        4. Post-update verification

        Args:
            task: The task being processed

        Returns:
            AgentResponse: Success if update completed, error otherwise
        """
        logger.info("SystemMaintenanceAgent: Starting system update")

        try:
            # Step 1: Pre-flight check
            logger.info("Step 1: Running pre-flight integrity check")
            integrity_check = self._run_integrity_check()
            if not integrity_check["success"]:
                return AgentResponse(
                    agent_id=self.agent_id,
                    task_id=task.id,
                    success=False,
                    output=None,
                    error=f"Pre-flight check failed: {integrity_check['error']}",
                    metadata={"step": "pre-flight", "details": integrity_check},
                )

            # Step 2: Git pull
            logger.info("Step 2: Pulling from remote")
            git_result = self._run_git_pull()
            if not git_result["success"]:
                return AgentResponse(
                    agent_id=self.agent_id,
                    task_id=task.id,
                    success=False,
                    output=None,
                    error=f"Git pull failed: {git_result['error']}",
                    metadata={"step": "git_pull", "details": git_result},
                )

            # Step 3: UV sync
            logger.info("Step 3: Syncing dependencies (uv sync)")
            uv_result = self._run_uv_sync()
            if not uv_result["success"]:
                return AgentResponse(
                    agent_id=self.agent_id,
                    task_id=task.id,
                    success=False,
                    output=None,
                    error=f"UV sync failed: {uv_result['error']}",
                    metadata={"step": "uv_sync", "details": uv_result},
                )

            # Step 4: Post-update verification
            logger.info("Step 4: Running post-update verification")
            post_check = self._run_integrity_check()
            if not post_check["success"]:
                logger.warning("Post-update check failed - system may be unstable")

            logger.info("✅ System update completed successfully")

            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=True,
                output={
                    "status": "updated",
                    "git_pull": git_result,
                    "uv_sync": uv_result,
                    "post_check": post_check,
                },
                metadata={
                    "commits_pulled": git_result.get("commits_pulled", 0),
                    "dependencies_updated": uv_result.get("packages_updated", 0),
                },
            )

        except Exception as e:
            logger.error(f"System update failed: {e}", exc_info=True)
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=False,
                output=None,
                error=f"Unexpected error during update: {e!s}",
            )

    def _verify_integrity(self, task: Task) -> AgentResponse:
        """
        Run pre-flight integrity checks.

        Checks:
        - Git repository is valid
        - Virtual environment exists
        - No uncommitted changes (prevents merge conflicts)

        Args:
            task: The task being processed

        Returns:
            AgentResponse: Success if all checks pass
        """
        logger.info("SystemMaintenanceAgent: Running integrity verification")
        result = self._run_integrity_check()

        return AgentResponse(
            agent_id=self.agent_id,
            task_id=task.id,
            success=result["success"],
            output=result,
            error=result.get("error"),
        )

    def _check_sync_status(self, task: Task) -> AgentResponse:
        """
        Check current git synchronization status.

        Returns:
            AgentResponse: Current git status (synced/behind/diverged)
        """
        logger.info("SystemMaintenanceAgent: Checking sync status")

        try:
            result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return AgentResponse(
                    agent_id=self.agent_id,
                    task_id=task.id,
                    success=False,
                    output=None,
                    error=f"Git fetch failed: {result.stderr}",
                )

            # Compare local vs remote
            local_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            ).stdout.strip()

            remote_result = subprocess.run(
                ["git", "rev-parse", "@{u}"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            # Check if upstream branch exists
            if remote_result.returncode != 0 or not remote_result.stdout.strip():
                return AgentResponse(
                    agent_id=self.agent_id,
                    task_id=task.id,
                    success=True,
                    output={
                        "status": "NO_UPSTREAM",
                        "local_hash": local_hash,
                        "remote_hash": None,
                        "behind_count": 0,
                        "message": "No upstream branch configured",
                    },
                )

            remote_hash = remote_result.stdout.strip()

            if local_hash == remote_hash:
                status = "SYNCED"
                behind_count = 0
            else:
                # Count commits behind
                behind_result = subprocess.run(
                    ["git", "rev-list", "--count", "HEAD..@{u}"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                # Handle case where rev-list fails or returns empty
                if behind_result.returncode != 0 or not behind_result.stdout.strip():
                    behind_count = 0
                    status = "DIVERGED"
                else:
                    behind_count = int(behind_result.stdout.strip())
                    status = f"BEHIND_BY_{behind_count}" if behind_count > 0 else "DIVERGED"

            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=True,
                output={
                    "status": status,
                    "local_hash": local_hash,
                    "remote_hash": remote_hash,
                    "behind_count": behind_count,
                },
            )

        except Exception as e:
            logger.error(f"Failed to check sync status: {e}", exc_info=True)
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=False,
                output=None,
                error=f"Failed to check sync status: {e!s}",
            )

    def _run_integrity_check(self) -> dict[str, Any]:
        """
        Run integrity checks.

        Returns:
            dict: {"success": bool, "checks": dict, "error": str | None}
        """
        checks = {}

        # Check 1: Git repository
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            checks["git_repo"] = result.returncode == 0
        except Exception as e:
            checks["git_repo"] = False
            logger.error(f"Git check failed: {e}")

        # Check 2: Virtual environment
        venv_path = self.project_root / ".venv"
        checks["venv_exists"] = venv_path.exists()

        # Check 3: No uncommitted changes (prevents merge conflicts)
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            checks["clean_working_tree"] = len(result.stdout.strip()) == 0
        except Exception as e:
            checks["clean_working_tree"] = False
            logger.error(f"Git status check failed: {e}")

        all_passed = all(checks.values())

        return {
            "success": all_passed,
            "checks": checks,
            "error": None if all_passed else "Some integrity checks failed",
        }

    def _run_git_pull(self) -> dict[str, Any]:
        """
        Execute git pull.

        Returns:
            dict: {"success": bool, "commits_pulled": int, "output": str, "error": str | None}
        """
        try:
            result = subprocess.run(
                ["git", "pull", "--rebase"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "commits_pulled": 0,
                    "output": result.stdout,
                    "error": result.stderr,
                }

            # Count commits pulled (rough heuristic)
            commits_pulled = result.stdout.count("Fast-forward") + result.stdout.count("Updating")

            return {
                "success": True,
                "commits_pulled": commits_pulled,
                "output": result.stdout,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Git pull failed: {e}", exc_info=True)
            return {
                "success": False,
                "commits_pulled": 0,
                "output": "",
                "error": str(e),
            }

    def _run_uv_sync(self) -> dict[str, Any]:
        """
        Execute uv sync.

        Returns:
            dict: {"success": bool, "packages_updated": int, "output": str, "error": str | None}
        """
        try:
            result = subprocess.run(
                ["uv", "sync", "--extra", "dev"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for dependency resolution
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "packages_updated": 0,
                    "output": result.stdout,
                    "error": result.stderr,
                }

            # Count packages updated (rough heuristic)
            packages_updated = result.stdout.count("Installed") + result.stdout.count("Updated")

            return {
                "success": True,
                "packages_updated": packages_updated,
                "output": result.stdout,
                "error": None,
            }

        except Exception as e:
            logger.error(f"UV sync failed: {e}", exc_info=True)
            return {
                "success": False,
                "packages_updated": 0,
                "output": "",
                "error": str(e),
            }
