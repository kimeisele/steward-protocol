"""
GitState - Layer 1 (STHULA) Git Operations

Provides AI-readable Git operations for the Prakriti state engine.
This is NOT a full Git client - just what agents need.

GAD-000 Compliant:
- All methods return dict/dataclass
- Errors use StructuredError with codes
- get_capabilities() for discoverability
"""

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("GIT_STATE")


@dataclass
class GitCommit:
    """Represents a Git commit."""

    sha: str
    short_sha: str
    author: str
    message: str
    timestamp: str


@dataclass
class GitDiff:
    """Represents a Git diff for work verification."""

    files_changed: int
    insertions: int
    deletions: int
    files: List[str] = field(default_factory=list)


class GitState:
    """Git operations wrapper for Prakriti.

    Philosophy: Git is cognitive logging.
    - branch = Start thinking about something
    - commit = Crystallize a fact/decision
    - diff = Proof of Work (what changed?)
    - merge = Learning (integrate knowledge)
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        self._workspace = workspace_path or Path.cwd()
        self._git_dir = self._workspace / ".git"

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        return {
            "operations": [
                "current_branch",
                "head_sha",
                "is_dirty",
                "diff",
                "recent_commits",
                "status",
            ],
            "read_only": True,  # Phase 1 is read-only
            "workspace": str(self._workspace),
        }

    # =========================================================================
    # Core Read Operations
    # =========================================================================

    def is_git_repo(self) -> bool:
        """Check if workspace is a Git repository."""
        return self._git_dir.exists() and self._git_dir.is_dir()

    def current_branch(self) -> str:
        """Get current Git branch name."""
        if not self.is_git_repo():
            return "NOT_A_GIT_REPO"

        result = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        return result.strip() if result else "DETACHED_HEAD"

    def head_sha(self) -> str:
        """Get current HEAD commit SHA."""
        if not self.is_git_repo():
            return ""

        result = self._run_git(["rev-parse", "HEAD"])
        return result.strip() if result else ""

    def short_sha(self) -> str:
        """Get short (7 char) HEAD SHA."""
        full_sha = self.head_sha()
        return full_sha[:7] if full_sha else ""

    def is_dirty(self) -> bool:
        """Check if workspace has uncommitted changes."""
        if not self.is_git_repo():
            return False

        result = self._run_git(["status", "--porcelain"])
        return bool(result and result.strip())

    def status(self) -> Dict[str, Any]:
        """GAD-000: Get comprehensive git status as dict."""
        if not self.is_git_repo():
            return {
                "is_repo": False,
                "error": "Not a git repository",
            }

        return {
            "is_repo": True,
            "branch": self.current_branch(),
            "sha": self.short_sha(),
            "dirty": self.is_dirty(),
            "workspace": str(self._workspace),
        }

    # =========================================================================
    # Diff Operations (Proof of Work)
    # =========================================================================

    def diff(self, base_ref: str = "HEAD~1") -> GitDiff:
        """Get diff stats from base_ref to HEAD.

        Args:
            base_ref: Git ref to diff against (default: previous commit)

        Returns:
            GitDiff with files changed, insertions, deletions
        """
        if not self.is_git_repo():
            return GitDiff(files_changed=0, insertions=0, deletions=0)

        # Get diff stats
        result = self._run_git(["diff", "--stat", "--numstat", base_ref, "HEAD"])
        if not result:
            return GitDiff(files_changed=0, insertions=0, deletions=0)

        files = []
        insertions = 0
        deletions = 0

        for line in result.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                try:
                    ins = int(parts[0]) if parts[0] != "-" else 0
                    dels = int(parts[1]) if parts[1] != "-" else 0
                    insertions += ins
                    deletions += dels
                    files.append(parts[2])
                except ValueError:
                    continue

        return GitDiff(
            files_changed=len(files),
            insertions=insertions,
            deletions=deletions,
            files=files,
        )

    def diff_main(self) -> GitDiff:
        """Get diff from main/master branch to HEAD."""
        # Try main first, then master
        main_branch = self._get_main_branch()
        return self.diff(main_branch)

    # =========================================================================
    # Commit History
    # =========================================================================

    def recent_commits(self, count: int = 5) -> List[GitCommit]:
        """Get recent commits.

        Args:
            count: Number of commits to return

        Returns:
            List of GitCommit objects
        """
        if not self.is_git_repo():
            return []

        # Format: SHA|short|author|message|timestamp
        format_str = "%H|%h|%an|%s|%ci"
        result = self._run_git(["log", f"-{count}", f"--format={format_str}"])

        if not result:
            return []

        commits = []
        for line in result.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|", 4)
            if len(parts) == 5:
                commits.append(
                    GitCommit(
                        sha=parts[0],
                        short_sha=parts[1],
                        author=parts[2],
                        message=parts[3],
                        timestamp=parts[4],
                    )
                )

        return commits

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _run_git(self, args: List[str]) -> Optional[str]:
        """Run a git command and return stdout."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self._workspace,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout
            logger.debug(f"Git command failed: {result.stderr}")
            return None
        except subprocess.TimeoutExpired:
            logger.warning("Git command timed out")
            return None
        except Exception as e:
            logger.warning(f"Git command error: {e}")
            return None

    def _get_main_branch(self) -> str:
        """Detect if repo uses 'main' or 'master'."""
        result = self._run_git(["branch", "-l", "main", "master"])
        if result and "main" in result:
            return "main"
        return "master"
