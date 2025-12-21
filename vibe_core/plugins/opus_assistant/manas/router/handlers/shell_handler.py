"""
Shell Handler - Git and shell command processing.

OPUS-171 Phase 5: Extracted from IntentRouter.

OPUS-SILPA: Real Git operations via GitTools.
OPUS-106: VEDA-4 ToolLoader integration.

Handles:
- commit_pending_changes, commit_and_push
- git_push, create_pr, merge_pr
- cleanup_stale_branches, cleanup_old_logs
"""

import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.loaders import ToolLoader
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.Shell")


@register_handler
class ShellHandler(BaseHandler):
    """
    Handle Git and shell command intents.

    OPUS-SILPA: Real Git operations via GitTools.
    OPUS-106: VEDA-4 ToolLoader integration.

    Agent-First: This handler belongs to the GIT domain.
    Future routing: Intent → GitAgent → ShellHandler
    """

    # === REQUIRED CLASS ATTRIBUTES ===
    name = "shell"
    intent_types = [
        "commit_pending_changes",
        "commit_and_push",
        "git_push",
        "create_pr",
        "merge_pr",
        "cleanup_stale_branches",
        "cleanup_old_logs",
    ]

    # === AGENT-FIRST ROUTING ===
    agent_type = AgentType.GIT
    priority = 20  # High priority for git operations

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workspace, config)
        self._tool_loader: Optional["ToolLoader"] = None

    def inject_tool_loader(self, tool_loader: "ToolLoader") -> None:
        """Inject ToolLoader for VEDA-4 tool access."""
        self._tool_loader = tool_loader

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to appropriate Git/Shell operation."""
        logger.info(f"🐚 ShellHandler handling: {intent.title}")

        try:
            # Git commit operations
            if intent.intent_type == "commit_pending_changes":
                return self._execute_git_commit(intent)
            elif intent.intent_type == "commit_and_push":
                intent.params["auto_push"] = True
                return self._execute_git_commit(intent)
            elif intent.intent_type == "git_push":
                git = self._get_git_tools()
                branch = intent.params.get("branch")
                return self._execute_git_push(git, branch)
            elif intent.intent_type == "create_pr":
                return self._execute_create_pr(intent)
            elif intent.intent_type == "merge_pr":
                return self._execute_merge_pr(intent)

            # Shell cleanup operations
            return self._execute_shell_cleanup(intent)

        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}

    def _get_git_tools(self):
        """
        Get GitTools via VEDA-4 ToolLoader (Fractal Pattern).

        OPUS-106: Dynamic tool retrieval.
        Falls back to legacy import if no ToolLoader available.
        """
        if self._tool_loader:
            tool = self._tool_loader.get("chronicle.git")
            if tool:
                logger.debug("🔧 VEDA-4: GitTools loaded via ToolLoader[fractal]")
                return tool

        # Fallback to legacy import
        logger.debug("⚠️ VEDA-4: Falling back to legacy GitTools import")
        from vibe_core.cartridges.system.chronicle.tools.git_tools import GitTools

        return GitTools()

    def _execute_shell_cleanup(self, intent: "Intent") -> Dict[str, Any]:
        """Execute shell cleanup commands."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

        shell = ShellCortex(workspace=self._workspace)
        if self._kernel:
            shell.inject_kernel(self._kernel)

        cmd = None
        if intent.intent_type == "cleanup_stale_branches":
            cmd = "git branch --merged | grep -v main | head -5"
        elif intent.intent_type == "cleanup_old_logs":
            cmd = "find . -name '*.log' -mtime +7 | head -10"

        if cmd:
            result = shell.execute(cmd, safe_mode=True)
            return {
                "success": result.exit_code == 0,
                "handler": self.name,
                "command": cmd,
                "output": result.stdout[:500] if result.stdout else "",
                "exit_code": result.exit_code,
            }
        else:
            return {
                "success": True,
                "handler": self.name,
                "message": "Intent acknowledged, no specific command defined",
            }

    def _execute_git_commit(self, intent: "Intent") -> Dict[str, Any]:
        """
        OPUS-SILPA: Execute real git commit via GitTools.

        Intent params:
            - files: Optional list of files to commit (default: all staged)
            - auto_push: If True, push to remote after commit (default: False)
            - branch: Branch to push to (default: current branch)
        """
        logger.info(f"🔐 SILPA executing git commit: {intent.title}")

        try:
            git = self._get_git_tools()

            # Check status
            status = git.get_status()
            if not status.get("dirty"):
                return {
                    "success": True,
                    "handler": self.name,
                    "action": "no_changes",
                    "message": "No pending changes to commit",
                }

            # Build commit message
            commit_msg = f"chore(manas): {intent.title}\n\nIntent ID: {intent.id}\nGenerated by MANAS Cognitive Kernel"

            files = intent.params.get("files")
            result = git.seal_history(message=commit_msg, files=files, sign=False)

            if not result.get("success"):
                return {
                    "success": False,
                    "handler": self.name,
                    "action": "commit_failed",
                    "error": result.get("message", "Unknown error"),
                }

            commit_hash = result.get("commit_hash_short")
            logger.info(f"✅ MANAS committed: {commit_hash}")

            # Auto-push if requested
            auto_push = intent.params.get("auto_push", False)
            push_result = None

            if auto_push:
                branch = intent.params.get("branch")
                push_result = self._execute_git_push(git, branch)

                if not push_result.get("success"):
                    logger.warning(f"⚠️ Commit succeeded but push failed: {push_result.get('error')}")
                    return {
                        "success": True,
                        "handler": self.name,
                        "action": "committed_push_failed",
                        "commit_hash": result.get("commit_hash"),
                        "commit_hash_short": commit_hash,
                        "push_error": push_result.get("error"),
                        "message": f"MANAS committed {commit_hash} but push failed",
                    }
                else:
                    logger.info("🚀 MANAS pushed to remote")

            return {
                "success": True,
                "handler": self.name,
                "action": "committed_and_pushed" if auto_push and push_result else "committed",
                "commit_hash": result.get("commit_hash"),
                "commit_hash_short": commit_hash,
                "pushed": auto_push and push_result and push_result.get("success"),
                "message": f"MANAS committed: {commit_hash} - {intent.title}" + (" (pushed)" if auto_push else ""),
            }

        except Exception as e:
            logger.error(f"❌ Git commit failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}

    def _execute_git_push(self, git, branch: Optional[str] = None) -> Dict[str, Any]:
        """Push commits to remote."""
        try:
            result = git.push_to_remote(remote="origin", branch=branch)
            if result.get("success"):
                logger.info(f"🚀 MANAS pushed to origin/{branch or 'current'}")
            return result
        except Exception as e:
            logger.error(f"❌ Git push failed: {e}")
            return {"success": False, "error": str(e)}

    def _execute_create_pr(self, intent: "Intent") -> Dict[str, Any]:
        """
        OPUS-SILPA: Create a Pull Request via GitHub CLI.

        Intent params:
            - title: PR title (default: intent title)
            - body: PR body/description
            - base: Base branch (default: main)
            - draft: Create as draft PR (default: False)
        """
        logger.info(f"📝 MANAS creating PR: {intent.title}")

        try:
            title = intent.params.get("title", intent.title)
            body = intent.params.get(
                "body", f"## Summary\n\n{intent.description}\n\n---\n*Created by MANAS (Intent: {intent.id})*"
            )
            base = intent.params.get("base", "main")
            draft = intent.params.get("draft", False)

            cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]
            if draft:
                cmd.append("--draft")

            result = subprocess.run(
                cmd,
                cwd=self._workspace,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                pr_url = result.stdout.strip()
                logger.info(f"✅ MANAS created PR: {pr_url}")
                return {
                    "success": True,
                    "handler": self.name,
                    "action": "pr_created",
                    "pr_url": pr_url,
                    "message": f"PR created: {pr_url}",
                }
            else:
                error = result.stderr.strip() or result.stdout.strip()
                logger.error(f"❌ PR creation failed: {error}")
                return {
                    "success": False,
                    "handler": self.name,
                    "action": "pr_create_failed",
                    "error": error,
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "handler": self.name, "error": "PR creation timed out"}
        except Exception as e:
            logger.error(f"❌ PR creation failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}

    def _execute_merge_pr(self, intent: "Intent") -> Dict[str, Any]:
        """
        OPUS-SILPA: Merge a Pull Request via GitHub CLI.

        Intent params:
            - pr_number: PR number to merge
            - pr_url: PR URL to merge (alternative)
            - merge_method: "merge", "squash", or "rebase" (default: "squash")
            - delete_branch: Delete branch after merge (default: True)
            - auto: Use auto-merge if checks pending (default: False)
        """
        logger.info(f"🔀 MANAS merging PR: {intent.title}")

        try:
            pr_number = intent.params.get("pr_number")
            pr_url = intent.params.get("pr_url")

            if not pr_number and not pr_url:
                pr_identifier = None
            elif pr_url:
                pr_identifier = pr_url
            else:
                pr_identifier = str(pr_number)

            merge_method = intent.params.get("merge_method", "squash")
            delete_branch = intent.params.get("delete_branch", True)
            auto_merge = intent.params.get("auto", False)

            cmd = ["gh", "pr", "merge"]
            if pr_identifier:
                cmd.append(pr_identifier)

            if merge_method == "squash":
                cmd.append("--squash")
            elif merge_method == "rebase":
                cmd.append("--rebase")
            else:
                cmd.append("--merge")

            if delete_branch:
                cmd.append("--delete-branch")
            if auto_merge:
                cmd.append("--auto")

            result = subprocess.run(
                cmd,
                cwd=self._workspace,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                logger.info("✅ MANAS merged PR successfully")
                return {
                    "success": True,
                    "handler": self.name,
                    "action": "pr_merged",
                    "merge_method": merge_method,
                    "message": f"PR merged via {merge_method}",
                    "output": result.stdout.strip(),
                }
            else:
                error = result.stderr.strip() or result.stdout.strip()
                logger.error(f"❌ PR merge failed: {error}")
                return {
                    "success": False,
                    "handler": self.name,
                    "action": "pr_merge_failed",
                    "error": error,
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "handler": self.name, "error": "PR merge timed out"}
        except Exception as e:
            logger.error(f"❌ PR merge failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class HygieneHandler(BaseHandler):
    """
    Handle hygiene check intents (lint, format, quick tests).

    OPUS-089: Sankalpa Hygiene Check.
    """

    name = "hygiene"
    intent_types = ["hygiene_check"]
    agent_type = AgentType.GIT
    priority = 5

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Run lint, format check, and quick tests."""
        logger.info("🧹 MANAS: Running Daily Hygiene Check...")

        results = {"success": True, "checks": {}}
        actions = intent.params.get("actions", ["lint", "format", "test_quick"])

        try:
            if "lint" in actions:
                lint_result = subprocess.run(
                    ["ruff", "check", "."],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self._workspace),
                )
                results["checks"]["lint"] = {
                    "passed": lint_result.returncode == 0,
                    "issues": lint_result.stdout.count("\n") if lint_result.stdout else 0,
                }
                if lint_result.returncode != 0:
                    results["success"] = False

            if "format" in actions:
                format_result = subprocess.run(
                    ["ruff", "format", "--check", "."],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self._workspace),
                )
                results["checks"]["format"] = {"passed": format_result.returncode == 0}
                if format_result.returncode != 0:
                    results["success"] = False

            if "test_quick" in actions:
                test_result = subprocess.run(
                    ["python", "-m", "pytest", "tests/manas/", "-x", "-q", "--timeout=30"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(self._workspace),
                )
                results["checks"]["test_quick"] = {
                    "passed": test_result.returncode == 0,
                    "output": test_result.stdout[-500:] if test_result.stdout else "",
                }
                if test_result.returncode != 0:
                    results["success"] = False

            results["handler"] = self.name
            logger.info(f"🧹 Hygiene complete: {results['success']}")
            return results

        except Exception as e:
            logger.error(f"🧹 Hygiene failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}
