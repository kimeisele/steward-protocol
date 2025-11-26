"""
🔨 GIT TOOLS - Chronicle's Arsenal

Provides safe, subprocess-based Git operations.
All commits are cryptographically signed using the bridge's key management.

Architecture:
- Operates on subprocess calls (maximum control, no external libs)
- Signing uses configured git user.signingKey (from vibe_core.bridge)
- All operations logged for audit trail
- Failures are explicit and non-destructive
"""

import subprocess
import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone

logger = logging.getLogger("CHRONICLE_GIT_TOOLS")


class GitTools:
    """
    The Chronicle Agent's Git Arsenal.

    Provides deterministic, auditable Git operations:
    - seal_history(message): Create signed commits
    - read_history(pattern): Query git log
    - fork_reality(branch_name): Create branches
    - manifest_reality(files): Stage and prepare
    """

    def __init__(self, repo_path: str = "."):
        """
        Initialize Git Tools.

        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = Path(repo_path)
        self.logger = logger

        # Verify we're in a git repo
        if not (self.repo_path / ".git").exists():
            self.logger.warning(f"⚠️  Not a git repository: {self.repo_path}")
            self.is_git_repo = False
        else:
            self.is_git_repo = True
            self.logger.info(f"✅ Git repository detected: {self.repo_path}")

    def _run_git_command(
        self,
        args: List[str],
        check: bool = True,
        capture_output: bool = False
    ) -> Tuple[int, str, str]:
        """
        Execute a git command safely.

        Args:
            args: List of git arguments (git is prepended)
            check: If True, raise on non-zero exit
            capture_output: If True, return stdout/stderr

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if not self.is_git_repo:
            self.logger.error("❌ Not a git repository. Cannot execute git commands.")
            return (128, "", "fatal: not a git repository")

        cmd = ["git"] + args

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=30
            )

            if check and result.returncode != 0:
                error_msg = result.stderr or result.stdout
                self.logger.error(f"❌ Git command failed: {' '.join(cmd)}")
                self.logger.error(f"   Error: {error_msg}")
                raise RuntimeError(f"Git command failed: {error_msg}")

            return (result.returncode, result.stdout.strip(), result.stderr.strip())

        except subprocess.TimeoutExpired:
            msg = f"Git command timed out: {' '.join(cmd)}"
            self.logger.error(f"❌ {msg}")
            return (124, "", msg)
        except Exception as e:
            msg = f"Git command error: {str(e)}"
            self.logger.error(f"❌ {msg}")
            return (1, "", msg)

    def seal_history(
        self,
        message: str,
        files: Optional[List[str]] = None,
        sign: bool = True
    ) -> Dict[str, any]:
        """
        Seal the timeline: Create a signed commit.

        This is the "Genesis Ceremony" for code changes.
        The commit is cryptographically signed (if sign=True).

        Args:
            message: Commit message
            files: List of files to commit (if None, commits all staged)
            sign: Whether to sign the commit (default: True)

        Returns:
            Dict with:
            - success: bool
            - commit_hash: str (SHA1 if successful)
            - message: str
            - timestamp: ISO8601 timestamp
        """
        self.logger.info(f"🔐 Sealing history: {message[:50]}...")

        result = {
            "success": False,
            "commit_hash": None,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # 1. Stage files
            if files:
                self.logger.info(f"   📝 Staging {len(files)} files...")
                for file in files:
                    code, out, err = self._run_git_command(["add", file], check=False)
                    if code != 0:
                        self.logger.warning(f"   ⚠️  Could not stage {file}: {err}")
            else:
                # Stage all modified files
                self._run_git_command(["add", "-A"], check=False)

            # 2. Check if there's anything to commit
            code, out, err = self._run_git_command(
                ["diff", "--cached", "--quiet"],
                check=False
            )
            if code == 0:
                # No changes
                self.logger.warning("⚠️  No changes to commit")
                result["message"] = "No changes to commit"
                return result

            # 3. Create commit
            commit_cmd = ["commit", "-m", message]
            if sign:
                commit_cmd.append("-S")  # Sign the commit

            code, out, err = self._run_git_command(commit_cmd, check=False)
            if code != 0:
                self.logger.error(f"❌ Commit failed: {err}")
                result["message"] = err
                return result

            # 4. Get commit hash
            code, hash_out, _ = self._run_git_command(
                ["rev-parse", "HEAD"],
                check=True
            )
            commit_hash = hash_out[:7]  # Short hash

            result["success"] = True
            result["commit_hash"] = hash_out
            result["commit_hash_short"] = commit_hash

            self.logger.info(f"✅ Sealed: {commit_hash} | {message[:40]}")

        except Exception as e:
            self.logger.error(f"❌ seal_history failed: {e}")
            result["message"] = str(e)

        return result

    def read_history(
        self,
        pattern: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, any]:
        """
        Read the timeline: Query git log.

        Args:
            pattern: Optional file pattern to filter commits
            limit: Number of commits to return (default: 10)

        Returns:
            Dict with:
            - success: bool
            - commits: List of commit objects
            - message: str
        """
        self.logger.info(f"📖 Reading history (limit: {limit})...")

        result = {
            "success": False,
            "commits": [],
            "message": ""
        }

        try:
            # Build log format: one JSON object per line
            format_str = "%H%n%h%n%an%n%ae%n%aI%n%s%n"

            cmd = [
                "log",
                f"--max-count={limit}",
                f"--format={format_str}"
            ]

            if pattern:
                cmd.extend(["--", pattern])

            code, output, err = self._run_git_command(cmd, check=False)

            if code != 0:
                self.logger.error(f"❌ Log failed: {err}")
                result["message"] = err
                return result

            # Parse output
            if not output:
                self.logger.warning("⚠️  No commits found")
                result["message"] = "No commits found"
                result["success"] = True
                return result

            lines = output.split("\n")
            for i in range(0, len(lines), 6):
                if i + 5 >= len(lines):
                    break

                commit = {
                    "hash": lines[i],
                    "hash_short": lines[i + 1],
                    "author": lines[i + 2],
                    "email": lines[i + 3],
                    "timestamp": lines[i + 4],
                    "subject": lines[i + 5] if i + 5 < len(lines) else ""
                }
                result["commits"].append(commit)

            result["success"] = True
            result["message"] = f"Found {len(result['commits'])} commits"

            self.logger.info(f"✅ Read {len(result['commits'])} commits from history")

        except Exception as e:
            self.logger.error(f"❌ read_history failed: {e}")
            result["message"] = str(e)

        return result

    def fork_reality(self, branch_name: str) -> Dict[str, any]:
        """
        Fork reality: Create a new branch (possible timeline).

        Args:
            branch_name: Name of the new branch

        Returns:
            Dict with:
            - success: bool
            - branch: str
            - message: str
        """
        self.logger.info(f"🔀 Forking reality: {branch_name}...")

        result = {
            "success": False,
            "branch": branch_name,
            "message": ""
        }

        try:
            # Validate branch name
            if not branch_name or "/" not in branch_name:
                branch_name = f"claude/{branch_name}"
                self.logger.info(f"   → Auto-prefixed: {branch_name}")

            # Create and checkout branch
            code, out, err = self._run_git_command(
                ["checkout", "-b", branch_name],
                check=False
            )

            if code != 0:
                self.logger.error(f"❌ Branch creation failed: {err}")
                result["message"] = err
                return result

            result["success"] = True
            result["message"] = f"Branch created: {branch_name}"

            self.logger.info(f"✅ Reality forked: {branch_name}")

        except Exception as e:
            self.logger.error(f"❌ fork_reality failed: {e}")
            result["message"] = str(e)

        return result

    def manifest_reality(self, files: List[str]) -> Dict[str, any]:
        """
        Manifest reality: Stage files for sealing.

        Args:
            files: List of files to stage

        Returns:
            Dict with:
            - success: bool
            - staged_files: List of successfully staged files
            - message: str
        """
        self.logger.info(f"📋 Manifesting {len(files)} files...")

        result = {
            "success": True,
            "staged_files": [],
            "message": ""
        }

        for file in files:
            code, out, err = self._run_git_command(
                ["add", file],
                check=False
            )

            if code == 0:
                result["staged_files"].append(file)
                self.logger.info(f"   ✅ Staged: {file}")
            else:
                self.logger.warning(f"   ⚠️  Could not stage {file}: {err}")

        result["message"] = f"Staged {len(result['staged_files'])} files"
        self.logger.info(f"✅ Manifested: {result['message']}")

        return result

    def get_status(self) -> Dict[str, any]:
        """
        Get current git status.

        Returns:
            Dict with:
            - success: bool
            - branch: str (current branch)
            - dirty: bool (has uncommitted changes)
            - files_changed: List of changed files
        """
        result = {
            "success": False,
            "branch": None,
            "dirty": False,
            "files_changed": []
        }

        try:
            # Get current branch
            code, branch, _ = self._run_git_command(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                check=False
            )
            if code == 0:
                result["branch"] = branch

            # Get changed files
            code, output, _ = self._run_git_command(
                ["status", "-s"],
                check=False
            )
            if code == 0 and output:
                result["files_changed"] = output.split("\n")
                result["dirty"] = True

            result["success"] = True

        except Exception as e:
            self.logger.error(f"❌ get_status failed: {e}")

        return result

    def push_to_remote(
        self,
        remote: str = "origin",
        branch: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Push commits to remote (manifest timeline across network).

        Args:
            remote: Remote name (default: origin)
            branch: Branch to push (default: current branch)

        Returns:
            Dict with:
            - success: bool
            - remote: str
            - branch: str
            - message: str
        """
        self.logger.info(f"☁️  Pushing to {remote}...")

        result = {
            "success": False,
            "remote": remote,
            "branch": branch,
            "message": ""
        }

        try:
            # Get current branch if not specified
            if not branch:
                code, branch_out, _ = self._run_git_command(
                    ["rev-parse", "--abbrev-ref", "HEAD"],
                    check=False
                )
                if code == 0:
                    branch = branch_out
                else:
                    result["message"] = "Could not determine current branch"
                    return result

            # Push with -u flag (track remote)
            code, out, err = self._run_git_command(
                ["push", "-u", remote, branch],
                check=False
            )

            if code != 0:
                self.logger.error(f"❌ Push failed: {err}")
                result["message"] = err
                return result

            result["success"] = True
            result["branch"] = branch
            result["message"] = out

            self.logger.info(f"✅ Pushed to {remote}/{branch}")

        except Exception as e:
            self.logger.error(f"❌ push_to_remote failed: {e}")
            result["message"] = str(e)

        return result
