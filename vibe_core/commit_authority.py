"""
CommitAuthority: THE ONLY way to commit. Period.

OPUS-209 Phase 0: Single Commit Authority.

Replaces: 3+ different git commit paths in:
- StateService._commit_via_git() (uses --no-verify!)
- StateService._commit_via_weaver() (creates new Prakriti!)
- Prakriti.commit_if_dirty()
- Weaver.pulse()
- Weaver.weave()
- Weaver.on_session_end()

This ensures:
1. Single locking mechanism (no race conditions)
2. Consistent hook behavior (no --no-verify surprises)
3. Audit trail (all commits logged)
4. Environment variable respect (VIBE_NO_GIT_COMMIT)

Usage:
    from vibe_core.commit_authority import CommitAuthority

    result = CommitAuthority.commit(
        files=[Path(".vibe/state/ledger.json")],
        message="Update ledger state",
        author="state_service",
    )

    if result.success:
        print(f"Committed: {result.commit_hash}")
    else:
        print(f"Failed: {result.error or result.skipped_reason}")
"""

import logging
import os
import subprocess
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import ClassVar, List, Optional

from vibe_core.state.schema import CommitResult

logger = logging.getLogger("COMMIT_AUTHORITY")


class CommitAuthority:
    """
    THE ONLY WAY TO COMMIT. Period.

    All git commits in the entire codebase MUST go through here.

    Thread Safety:
        Uses a class-level lock to prevent concurrent commits.

    Audit Trail:
        All commits are logged with timestamp, author, message, and hash.
        Access via get_audit_log().

    Environment Variables:
        VIBE_NO_GIT_COMMIT=1 - Disable all commits (for testing)

    Security:
        --no-verify is supported but WARNED. Use sparingly.
    """

    _lock: ClassVar[threading.Lock] = threading.Lock()
    _commit_log: ClassVar[List[dict]] = []

    @classmethod
    def commit(
        cls,
        files: List[Path],
        message: str,
        author: str = "kernel",
        no_verify: bool = False,
    ) -> CommitResult:
        """
        Commit files atomically.

        Args:
            files: Files to stage and commit (Path objects)
            message: Commit message
            author: Who is committing (for audit trail)
            no_verify: Skip pre-commit hooks (DANGEROUS - use sparingly!)

        Returns:
            CommitResult with success status and details

        Example:
            result = CommitAuthority.commit(
                files=[Path(".vibe/state/ledger.json")],
                message="Update ledger",
                author="state_service",
            )
        """
        with cls._lock:
            # 1. Check environment kill-switch
            if os.environ.get("VIBE_NO_GIT_COMMIT") == "1":
                logger.debug("[COMMIT_AUTHORITY] Skipped (VIBE_NO_GIT_COMMIT=1)")
                return CommitResult(success=False, skipped_reason="VIBE_NO_GIT_COMMIT=1")

            # 2. Log dangerous operations
            if no_verify:
                logger.warning(
                    f"[COMMIT_AUTHORITY] ⚠️ --no-verify used by '{author}'! "
                    f"This bypasses pre-commit hooks including VISNU protection."
                )

            # 3. Validate we have files to commit
            existing_files = [f for f in files if f.exists()]
            if not existing_files:
                return CommitResult(success=False, skipped_reason="no_files_exist")

            try:
                # 4. Stage files
                for f in existing_files:
                    result = subprocess.run(["git", "add", str(f)], capture_output=True, text=True)
                    if result.returncode != 0:
                        logger.warning(f"[COMMIT_AUTHORITY] git add failed for {f}: {result.stderr}")

                # 5. Check if there's anything to commit
                status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
                if not status_result.stdout.strip():
                    return CommitResult(success=False, skipped_reason="nothing_to_commit")

                # 6. Build commit command
                cmd = ["git", "commit", "-m", message]
                if no_verify:
                    cmd.append("--no-verify")

                # 7. Execute commit
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    # Extract commit hash
                    hash_result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
                    commit_hash = hash_result.stdout.strip()[:8]

                    # Audit log entry
                    log_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "author": author,
                        "message": message[:100],
                        "hash": commit_hash,
                        "no_verify": no_verify,
                        "files": [str(f) for f in existing_files],
                    }
                    cls._commit_log.append(log_entry)

                    logger.info(f"[COMMIT_AUTHORITY] ✅ {commit_hash} by {author}: {message[:50]}")
                    return CommitResult(success=True, commit_hash=commit_hash)

                else:
                    # Check common failure reasons
                    stderr = result.stderr or ""
                    stdout = result.stdout or ""

                    if "nothing to commit" in stdout or "nothing to commit" in stderr:
                        return CommitResult(success=False, skipped_reason="nothing_to_commit")

                    error = stderr or stdout or "Unknown error"
                    logger.error(f"[COMMIT_AUTHORITY] ❌ Failed: {error}")
                    return CommitResult(success=False, error=error)

            except subprocess.CalledProcessError as e:
                logger.error(f"[COMMIT_AUTHORITY] ❌ Exception: {e}")
                return CommitResult(success=False, error=str(e))
            except Exception as e:
                logger.error(f"[COMMIT_AUTHORITY] ❌ Unexpected error: {e}")
                return CommitResult(success=False, error=str(e))

    @classmethod
    def get_audit_log(cls, limit: int = 100) -> List[dict]:
        """
        Get recent commit audit log.

        Args:
            limit: Maximum entries to return (default 100)

        Returns:
            List of commit log entries (newest last)
        """
        with cls._lock:
            return cls._commit_log[-limit:]

    @classmethod
    def clear_audit_log(cls) -> None:
        """
        Clear the audit log.

        FOR TESTING ONLY.
        """
        with cls._lock:
            cls._commit_log.clear()
            logger.warning("[COMMIT_AUTHORITY] Audit log cleared (test mode)")

    @classmethod
    def get_stats(cls) -> dict:
        """
        Get commit statistics.

        Returns:
            Dict with total_commits, no_verify_count, authors
        """
        with cls._lock:
            total = len(cls._commit_log)
            no_verify_count = sum(1 for entry in cls._commit_log if entry.get("no_verify"))
            authors = list(set(entry.get("author", "unknown") for entry in cls._commit_log))

            return {
                "total_commits": total,
                "no_verify_count": no_verify_count,
                "no_verify_percentage": (no_verify_count / total * 100) if total > 0 else 0,
                "unique_authors": authors,
            }
