# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x51cc3e82"  # GenesisByte: parampara % 37 == 0

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from vibe_core.protocols.universal import SyncProtocol, SyncResult, SyncStatus
from vibe_core.protocols.universal.types import SovereignContext

logger = logging.getLogger("GIT_SYNC")


class GitSyncService(SyncProtocol):
    """
    Syncs the local repository with the remote origin.

    Implement's SyncProtocol for standardized "Pull/Push" operations.
    Handles 'Git Diva' behavior (merge conflicts, auth) gracefully.
    """

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self._last_sync: Optional[datetime] = None
        self._last_error: Optional[str] = None

        # Verify it's a git repo
        if not (self.repo_path / ".git").exists():
            logger.warning(f"⚠️ GitSync initialized on non-git dir: {repo_path}")

    def sync(self, context: Optional[SovereignContext] = None) -> SyncResult:
        """
        Perform git pull (and theoretically push).

        Returns a robust SyncResult that doesn't crash on merge conflicts.
        """
        # ANTI-MAYAVAD ENFORCEMENT
        if context is None:
            logger.critical(
                "🚨 ANTI-MAYAVAD VIOLATION: Anonymous GitSync Attempted! (Graceful degradation: Allowing but logging threat)"
            )
            # In Strict Mode this would raise AccessDeniedError

        if not (self.repo_path / ".git").exists():
            return SyncResult(success=False, items_synced=0, errors=["Not a git repository"], timestamp=datetime.now())

        try:
            # 1. Fetch
            fetch_res = self._run_git(["fetch", "origin"])
            if fetch_res.returncode != 0:
                logger.error(f"Git fetch failed: {fetch_res.stderr}")
                return SyncResult(
                    success=False,
                    items_synced=0,
                    errors=[f"Fetch failed: {fetch_res.stderr}"],
                    timestamp=datetime.now(),
                )

            # 2. Pull (Rebase to stay linear? Or merge? Ouroboros prefers linear history generally, but let's stick to default pull for safety or --ff-only)
            # Using --ff-only to avoid accidental merge commits. If it fails, we need manual intervention.
            pull_res = self._run_git(["pull", "--ff-only"])

            if pull_res.returncode != 0:
                error_msg = pull_res.stderr.strip()
                logger.error(f"Git pull failed: {error_msg}")

                # Analyze Error (Diva Diagnostics)
                strategy = "Manual Implementation Required"
                if "conflict" in error_msg.lower():
                    strategy = "Merge Conflict Resolution"
                elif "diverged" in error_msg.lower():
                    strategy = "Branch Divergence Resolution"

                self._last_error = error_msg
                return SyncResult(
                    success=False,
                    items_synced=0,
                    errors=[f"Pull failed ({strategy}): {error_msg}"],
                    timestamp=datetime.now(),
                )

            # Success
            self._last_sync = datetime.now()
            self._last_error = None

            # Count changes? Hard to parse validly without complex logic.
            # Assuming 'Already up to date' = 0, else 1 batch.
            items_synced = 0 if "Already up to date" in pull_res.stdout else 1

            return SyncResult(success=True, items_synced=items_synced, errors=[], timestamp=self._last_sync)

        except Exception as e:
            logger.exception("Git sync crash")
            return SyncResult(success=False, items_synced=0, errors=[f"Crash: {str(e)}"], timestamp=datetime.now())

    def get_sync_status(self, context: Optional[SovereignContext] = None) -> SyncStatus:
        """Get current sync status."""
        is_synced = False
        pending_items = 0

        if (self.repo_path / ".git").exists():
            # Check distinct commits between HEAD and @{u}
            try:
                # Behind (Need to pull)
                behind_res = self._run_git(["rev-list", "--count", "HEAD..@{u}"])
                if behind_res.returncode == 0:
                    pending_items = int(behind_res.stdout.strip())

                is_synced = (pending_items == 0) and (self._last_error is None)
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)

        return SyncStatus(
            is_synced=is_synced,
            last_sync=self._last_sync,
            pending_items=pending_items,
            details={"repo": str(self.repo_path), "last_error": self._last_error},
        )

    def is_synced(self, context: Optional[SovereignContext] = None) -> bool:
        """Check if synchronized."""
        return self.get_sync_status(context).is_synced

    def _run_git(self, args: List[str]):
        """Helper to run git commands."""
        return subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            timeout=30,  # Don't block forever
        )
