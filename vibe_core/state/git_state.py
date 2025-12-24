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
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .runtime_state import get_runtime_state_definition

if TYPE_CHECKING:
    from .runtime_state import RuntimeStateDefinition

logger = logging.getLogger("GIT_STATE")

# VISNU Protected Files (OPUS-024)
# These files cannot be committed via Prakriti - they require manual governance
VISNU_PROTECTED = [
    "vibe_core/kernel_impl.py",
    "vibe_core/kernel_ops.py",
    "vibe_core/ledger.py",
    "vibe_core/plugin_protocol.py",
    "vibe_core/plugin_loader.py",
    "vibe_core/narasimha.py",
    "vibe_core/capability_registry.py",
    "vibe_core/bridge.py",
    "scripts/governance/restore_kernel.sh",
    "scripts/governance/verify_kernel.py",
    "scripts/governance/kernel_hashes.json",
    ".github/workflows/attest.yml",
    ".github/workflows/container-build.yml",
    ".github/workflows/deploy.yml",
    ".github/workflows/factory.yml",
    ".github/workflows/heartbeat.yml",
    ".github/workflows/integration-tests.yml",
    ".github/workflows/scheduled-agents.yml",
    ".github/workflows/scribe-docs.yml",
    ".github/workflows/steward-ci.yml",
    ".github/workflows/system-cycle.yml",
    ".pre-commit-config.yaml",
]


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

    # Thread-safe commit lock (OPUS-028)
    _commit_lock = threading.Lock()

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
                # Read operations
                "current_branch",
                "head_sha",
                "is_dirty",
                "diff",
                "recent_commits",
                "status",
                # Write operations (OPUS-028)
                "stage",
                "commit",
            ],
            "read_only": False,  # OPUS-028: Write ops enabled
            "visnu_protected_count": len(VISNU_PROTECTED),
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

    # =========================================================================
    # Write Operations (OPUS-028)
    # =========================================================================

    def stage(self, patterns: List[str]) -> int:
        """Stage files matching patterns.

        Args:
            patterns: File patterns to stage (e.g., ["*.md", "docs/"])

        Returns:
            Number of patterns processed
        """
        if not self.is_git_repo():
            return 0

        total = 0
        for pattern in patterns:
            result = self._run_git(["add", pattern])
            if result is not None:
                total += 1
        return total

    def commit(
        self,
        message: str,
        commit_type: str = "chore",
        scope: str = "auto",
        no_verify: bool = True,
        trailers: Optional[Dict[str, str]] = None,
    ) -> Optional[GitCommit]:
        """Create a commit with VISNU protection.

        Thread-safe via _commit_lock.

        Args:
            message: Commit message (subject line)
            commit_type: Conventional commit type (chore, feat, fix, etc.)
            scope: Commit scope
            no_verify: Skip pre-commit hooks (True for auto-commits)
            trailers: Git trailers for machine readability (e.g., {"Session-ID": "abc"})

        Returns:
            GitCommit if successful, None if nothing to commit

        Raises:
            GovernanceViolation: If VISNU protected files are staged
        """
        if not self.is_git_repo():
            return None

        with self._commit_lock:
            # 1. Check if anything to commit
            if not self.is_dirty():
                return None

            # 2. VISNU protection check
            staged = self._get_staged_files()
            protected = [f for f in staged if f in VISNU_PROTECTED]
            if protected:
                from vibe_core.exceptions import GovernanceViolation

                raise GovernanceViolation(
                    f"Cannot commit VISNU protected files via Prakriti: {protected}. "
                    f"See docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md"
                )

            # 3. Format message with trailers (OPUS-027 Implementation Guidelines)
            formatted_msg = f"{commit_type}({scope}): {message}"
            if trailers:
                formatted_msg += "\n"
                for key, value in trailers.items():
                    formatted_msg += f"\n{key}: {value}"

            # 4. Create commit
            cmd = ["commit", "-m", formatted_msg]
            if no_verify:
                cmd.insert(1, "--no-verify")

            result = self._run_git(cmd)
            if result is None:
                return None

            # 5. Return commit info
            return GitCommit(
                sha=self.head_sha(),
                short_sha=self.short_sha(),
                author="prakriti",
                message=formatted_msg,
                timestamp=str(time.time()),
            )

    def _get_staged_files(self) -> List[str]:
        """Get list of staged files."""
        result = self._run_git(["diff", "--cached", "--name-only"])
        if not result:
            return []
        return [f.strip() for f in result.strip().split("\n") if f.strip()]

    def unstage_all(self) -> bool:
        """Unstage all staged files.

        Returns:
            True if successful
        """
        if not self.is_git_repo():
            return False
        result = self._run_git(["reset", "HEAD"])
        return result is not None

    # =========================================================================
    # OPUS-081: Runtime State Awareness (The "Lasagna" Logic)
    # =========================================================================

    def _get_runtime_state_patterns(self) -> List[str]:
        """
        OPUS-096: Get runtime state patterns from RuntimeStateDefinition.

        This is now delegated to the canonical RuntimeStateDefinition which:
        - Provides CORE patterns (always runtime state)
        - Discovers plugin-declared patterns from manifests

        Returns:
            List of file patterns that are RUNTIME STATE (not source code).
        """
        definition = get_runtime_state_definition(self._workspace)
        return definition.get_all_patterns()

    def is_source_dirty(self) -> bool:
        """
        OPUS-081: Check if SOURCE CODE changed (excludes runtime state).
        This is what Stop Hooks should call.

        Checks:
        1. Modified tracked files
        2. Staged changes
        3. NEW (untracked) source files
        """
        if not self.is_git_repo():
            return False

        # Get runtime state patterns from plugin manifests
        ignore_patterns = self._get_runtime_state_patterns()

        # Build git diff command with exclusions
        # git diff --name-only HEAD -- . ':!OPUS.md' ':!ENVOY.md' ...
        args = ["diff", "--name-only", "HEAD", "--", "."]
        for pattern in ignore_patterns:
            args.append(f":!{pattern}")

        # Check unstaged changes
        unstaged = self._run_git(args)

        # Check staged changes
        args_cached = ["diff", "--name-only", "--cached", "HEAD", "--", "."]
        for pattern in ignore_patterns:
            args_cached.append(f":!{pattern}")
        staged = self._run_git(args_cached)

        has_unstaged = bool(unstaged and unstaged.strip())
        has_staged = bool(staged and staged.strip())

        # Also check untracked source files
        untracked_source = self._get_untracked_source_files()
        has_untracked_source = bool(untracked_source)

        return has_unstaged or has_staged or has_untracked_source

    def get_dirty_source_files(self) -> List[str]:
        """
        OPUS-081: Get list of dirty SOURCE CODE files (excludes runtime state).

        Includes:
        - Modified tracked files
        - Staged changes
        - NEW (untracked) source files
        """
        if not self.is_git_repo():
            return []

        ignore_patterns = self._get_runtime_state_patterns()

        args = ["diff", "--name-only", "HEAD", "--", "."]
        for pattern in ignore_patterns:
            args.append(f":!{pattern}")

        result = self._run_git(args)
        modified = []
        if result:
            modified = [f.strip() for f in result.strip().split("\n") if f.strip()]

        # Also include untracked source files
        untracked = self._get_untracked_source_files()

        # Combine and deduplicate
        all_files = list(set(modified + untracked))
        return sorted(all_files)

    def _get_untracked_source_files(self) -> List[str]:
        """
        Get untracked files that are SOURCE CODE (not runtime state).

        Uses RuntimeStateDefinition to filter out runtime files.
        """
        untracked = self._run_git(["ls-files", "--others", "--exclude-standard"])
        if not untracked:
            return []

        all_untracked = [f.strip() for f in untracked.strip().split("\n") if f.strip()]

        # Filter out runtime state files
        definition = get_runtime_state_definition(self._workspace)
        return definition.filter_source_files(all_untracked)

    def get_dirty_runtime_files(self) -> List[str]:
        """
        OPUS-081/096: Get list of dirty RUNTIME STATE files (excludes source code).

        This is the INVERSE of get_dirty_source_files().
        Used by Heartbeat to commit ONLY runtime files.

        Returns:
            List of runtime files that have uncommitted changes
        """
        if not self.is_git_repo():
            return []

        # Get all dirty files (both staged and unstaged)
        all_dirty = self._run_git(["diff", "--name-only", "HEAD"])
        if not all_dirty:
            all_dirty = ""

        # Also check untracked files
        untracked = self._run_git(["ls-files", "--others", "--exclude-standard"])
        if not untracked:
            untracked = ""

        all_files = set()
        for f in all_dirty.strip().split("\n"):
            if f.strip():
                all_files.add(f.strip())
        for f in untracked.strip().split("\n"):
            if f.strip():
                all_files.add(f.strip())

        # OPUS-096: Use RuntimeStateDefinition for filtering
        definition = get_runtime_state_definition(self._workspace)
        return definition.filter_runtime_files(list(all_files))
