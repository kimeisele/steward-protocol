"""
Prakriti - The Unified State Engine

OPUS-009: "The Repository IS the Mind"

Prakriti (Sanskrit: "Primordial Matter") unifies state across three layers:
- STHULA (Layer 1): Git + Files (Physical)
- PRANA (Layer 2): Kernel + Ephemeral (Runtime)
- PURUSHA (Layer 3): Personas (Identity)

GAD-000 Compliant:
- All methods return dict/dataclass
- Errors use StructuredError with codes
- get_capabilities() for discoverability
- get_system_status() for observability
"""

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import PrakritiProtocol
from vibe_core.state.schema import CommitResult

from .ephemeral_state import EphemeralState
from .file_state import FileState
from .git_state import GitDiff, GitState
from .kernel_state import KernelState
from .ledger_state import LedgerState
from .machine_state import MachineState
from .persona import PersonaManager

if TYPE_CHECKING:
    from vibe_core.protocols import VibeKernel

logger = logging.getLogger("PRAKRITI")


@dataclass
class StateSnapshot:
    """Complete state snapshot across all layers."""

    timestamp: float
    git: Dict[str, Any]
    files: Dict[str, Any]
    kernel: Optional[Dict[str, Any]] = None
    ephemeral: Optional[Dict[str, Any]] = None
    personas: Optional[Dict[str, Any]] = None


@dataclass
class KernelSessionContext:
    """Kernel-level session tracking (OPUS-027).

    Different from per-agent SessionContext - this tracks
    the entire kernel session from boot to shutdown.
    """

    session_id: str
    boot_time: float
    boot_commit: str
    pid: int = field(default_factory=os.getpid)
    last_commit: Optional[str] = None
    commit_count: int = 0
    crash_recovery: bool = False

    def mark_commit(self, sha: str) -> None:
        """Record a commit in this session."""
        self.last_commit = sha
        self.commit_count += 1

    def to_trailers(self) -> Dict[str, str]:
        """Generate Git trailers for commits."""
        return {
            "Session-ID": self.session_id,
            "Crash-Recovery": str(self.crash_recovery).lower(),
            "Commits-In-Session": str(self.commit_count + 1),
        }


@dataclass
class SyncResult:
    """Result of a sync operation."""

    action: str  # "none", "ledger_catchup", "git_reset", "error"
    message: str
    git_sha: Optional[str] = None
    ledger_hash: Optional[str] = None


class Prakriti(PrakritiProtocol):
    """The Fractal State Engine.

    The unified interface for all state operations in the Steward Protocol.
    Treats:
    - Every Agent as a Commit
    - Every Decision as a Branch
    - Every Learning as a Merge

    Layers:
    - Layer 1 (STHULA): Git + Files (Physical)
    - Layer 2 (PRANA): Kernel + Ephemeral (Runtime)
    - Layer 3 (PURUSHA): Personas (Identity)
    """

    def __init__(self, workspace_path: Optional[Path] = None, db_path: Optional[Path] = None):
        """Initialize Prakriti for a workspace.

        Args:
            workspace_path: Root of the workspace (default: cwd)
            db_path: Path to SQLite ledger (default: workspace/data/vibe_ledger.db)
        """
        self._workspace = Path(workspace_path) if workspace_path else Path.cwd()

        # Layer 1: Physical State (STHULA)
        self.git = GitState(self._workspace)
        self.files = FileState(self._workspace)

        # Layer 1: Ledger State (OPUS-027 - The Memory)
        if db_path is None:
            db_path = self._workspace / "data" / "vibe_ledger.db"
        self.ledger = LedgerState(Path(db_path))

        # Layer 1.5: Persistent Machine State (SQLite) - Legacy, use self.ledger
        self.machine = MachineState(Path(db_path))

        # Layer 2: Runtime State (PRANA)
        self.kernel = KernelState()
        self.ephemeral = EphemeralState()

        # Layer 3: Identity (PURUSHA)
        self.personas = PersonaManager(self._workspace)

        # Session tracking (OPUS-027)
        self.session: Optional[KernelSessionContext] = None
        self._prakriti_dir = self._workspace / ".prakriti"

        # Register in DI container
        ServiceRegistry.register(PrakritiProtocol, self)

        logger.info(f"[PRAKRITI] Initialized at {self._workspace} (Ledger: {db_path})")

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def from_workspace(cls, path: str) -> "Prakriti":
        """Create Prakriti instance from workspace path.

        Args:
            path: Path to workspace root

        Returns:
            Prakriti instance
        """
        return cls(Path(path))

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: What can Prakriti do?"""
        return {
            "version": "3.1.0-opus027",
            "operations": [
                "snapshot",
                "verify",
                "diff",
                "status",
                "inject_kernel",
                "get_persona",
                # OPUS-027 additions (pending implementation)
                "commit_if_dirty",
                "sync_ledger_git",
                "begin_session",
                "end_session",
            ],
            "layers": {
                "sthula": {
                    "status": "active",
                    "components": ["git", "files", "ledger"],
                },
                "prana": {
                    "status": "active",
                    "components": ["kernel", "ephemeral"],
                },
                "purusha": {
                    "status": "active",
                    "components": ["personas"],
                },
            },
            "workspace": str(self._workspace),
            "git": self.git.get_capabilities(),
            "files": self.files.get_capabilities(),
            "ledger": self.ledger.get_capabilities(),
            "kernel": self.kernel.get_capabilities(),
            "ephemeral": self.ephemeral.get_capabilities(),
            "personas": self.personas.get_capabilities(),
        }

    # =========================================================================
    # GAD-000: Observability
    # =========================================================================

    def get_system_status(self) -> Dict[str, Any]:
        """GAD-000 Test 2: Current state summary."""
        return {
            "timestamp": time.time(),
            "workspace": str(self._workspace),
            # "git": self.git.status(),  # DEBUG: Disabled (Blocking IO)
            # "files": self.files.status(), # DEBUG: Disabled (Blocking IO)
            "kernel": self.kernel.status(),
            # "ephemeral": self.ephemeral.status(),
            # "personas": self.personas.status(),
        }

    # =========================================================================
    # Core Operations
    # =========================================================================

    def snapshot(self) -> StateSnapshot:
        """Take a complete state snapshot.

        Returns:
            StateSnapshot with all layer states
        """
        return StateSnapshot(
            timestamp=time.time(),
            git=self.git.status(),
            files=self.files.status(),
            kernel=self.kernel.status(),
            ephemeral=self.ephemeral.status(),
            personas=self.personas.status(),
        )

    def inject_kernel(self, kernel: "VibeKernel") -> None:
        """Inject kernel reference for Layer 2 state access.

        Args:
            kernel: The VibeKernel instance
        """
        self.kernel.inject_kernel(kernel)
        logger.info("[PRAKRITI] Kernel injected into Layer 2")

    def verify(self) -> Dict[str, Any]:
        """Verify workspace consistency.

        Returns:
            Dict with verification results
        """
        issues = []

        # Check git repo
        if not self.git.is_git_repo():
            issues.append(
                {
                    "layer": "git",
                    "issue": "Not a git repository",
                    "severity": "warning",
                }
            )

        # Check for uncommitted changes
        if self.git.is_dirty():
            dirty_files = self.files.dirty_files()
            issues.append(
                {
                    "layer": "git",
                    "issue": "Uncommitted changes",
                    "severity": "info",
                    "details": {"dirty_count": len(dirty_files)},
                }
            )

        return {
            "status": "ok" if not issues else "issues_found",
            "issues": issues,
            "git_branch": self.git.current_branch(),
            "git_sha": self.git.short_sha(),
        }

    def diff(self, base_ref: str = "HEAD~1") -> GitDiff:
        """Get diff from base_ref to HEAD.

        This is the "Proof of Work" - what did the agent actually do?

        Args:
            base_ref: Git ref to diff against

        Returns:
            GitDiff with stats
        """
        return self.git.diff(base_ref)

    def diff_main(self) -> GitDiff:
        """Get diff from main branch to HEAD.

        Useful for verifying agent work before merge.

        Returns:
            GitDiff with stats
        """
        return self.git.diff_main()

    # =========================================================================
    # Convenience Properties
    # =========================================================================

    @property
    def workspace(self) -> Path:
        """Get workspace path."""
        return self._workspace

    @property
    def branch(self) -> str:
        """Get current git branch."""
        return self.git.current_branch()

    @property
    def is_dirty(self) -> bool:
        """Check if workspace has uncommitted changes."""
        return self.git.is_dirty()

    # =========================================================================
    # String Representation
    # =========================================================================

    def __repr__(self) -> str:
        return f"Prakriti(workspace={self._workspace}, branch={self.branch})"

    # =========================================================================
    # OPUS-027: Write Operations (Orchestration)
    # =========================================================================

    def commit_if_dirty(
        self,
        message: str = "Auto-commit",
        commit_type: str = "chore",
        scope: str = "state",
        stage_patterns: Optional[List[str]] = None,
        sync_ledger: bool = True,
    ) -> Optional[CommitResult]:
        """Commit current changes if workspace is dirty.

        This is the main orchestration method that:
        1. Stages files
        2. Creates Git commit (with VISNU protection)
        3. Syncs to Ledger (Cryptographic Zipper)
        4. Updates session tracking

        Args:
            message: Commit message
            commit_type: Conventional commit type (chore, feat, fix, etc.)
            scope: Commit scope
            stage_patterns: Patterns to stage (default: ["*.md"])
            sync_ledger: Also record in Ledger (default: True)

        Returns:
            CommitResult if committed, None if nothing to commit
        """
        if not self.is_dirty:
            logger.debug("[PRAKRITI] Nothing to commit (clean state)")
            return None

        # 1. Stage files
        patterns = stage_patterns or ["*.md"]
        self.git.stage(patterns)

        # 2. Build trailers (OPUS-027 Implementation Guidelines)
        trailers = {}
        if self.session:
            trailers = self.session.to_trailers()
        # Cryptographic Zipper: Include Ledger head hash
        ledger_head = self.ledger.get_current_head_hash()
        if ledger_head:
            trailers["Ledger-Head"] = ledger_head[:16]

        # 3. Git commit
        git_commit = self.git.commit(
            message=message,
            commit_type=commit_type,
            scope=scope,
            trailers=trailers if trailers else None,
        )
        if not git_commit:
            return None

        # 4. Ledger sync (Cryptographic Zipper - other direction)
        ledger_event_id = None
        if sync_ledger:
            staged_files = self.git._get_staged_files()
            ledger_event_id = self.ledger.record_sync(
                git_sha=git_commit.sha,
                files_committed=staged_files,
            )

        # 5. Session tracking
        if self.session:
            self.session.mark_commit(git_commit.sha)

        logger.info(f"[PRAKRITI] Committed: {git_commit.short_sha} - {message}")

        return CommitResult(
            success=True,
            git_sha=git_commit.sha,
            ledger_event_id=ledger_event_id,
            session_id=self.session.session_id if self.session else None,
            files_committed=staged_files if sync_ledger else [],
        )

    def sync_ledger_git(self, strategy: str = "git_wins") -> SyncResult:
        """Reconcile Ledger and Git if they diverged.

        Called on boot if consistency check fails.

        Args:
            strategy: Sync strategy
                - "git_wins": Ledger records catch-up events to match Git
                - "ledger_wins": Not implemented (dangerous)
                - "manual": Raise error for human intervention

        Returns:
            SyncResult with actions taken
        """
        # Check current state
        git_head = self.git.head_sha()
        ledger_last = self.ledger.get_last_sync_commit()

        if git_head == ledger_last:
            return SyncResult(
                action="none",
                message="Already in sync",
                git_sha=git_head,
                ledger_hash=self.ledger.get_current_head_hash(),
            )

        if strategy == "git_wins":
            # Ledger catches up - record the current Git state
            event_id = self.ledger.record_sync(
                git_sha=git_head,
                files_committed=["SYNC_CATCHUP"],
            )
            logger.warning(f"[PRAKRITI] Ledger synced to Git: {git_head[:7]}")
            return SyncResult(
                action="ledger_catchup",
                message=f"Ledger synced to Git {git_head[:7]}",
                git_sha=git_head,
                ledger_hash=self.ledger.get_current_head_hash(),
            )

        elif strategy == "ledger_wins":
            # This is dangerous - not implementing for now
            return SyncResult(
                action="error",
                message="ledger_wins strategy not implemented (too dangerous)",
            )

        else:
            from vibe_core.exceptions import GovernanceViolation

            raise GovernanceViolation(
                f"Git ({git_head[:7]}) and Ledger ({ledger_last[:7] if ledger_last else 'empty'}) "
                f"diverged. Manual intervention required."
            )

    # =========================================================================
    # OPUS-027: Session Management
    # =========================================================================

    def begin_session(self) -> KernelSessionContext:
        """Start a new session (called on kernel boot).

        Implements Ghost Lock Protocol for stale lock detection.
        (ADR-204: Supports bypass via VIBE_NO_LOCK for recursive test cycles)
        """
        # Ensure .prakriti directory exists
        self._prakriti_dir.mkdir(parents=True, exist_ok=True)

        # 🛡️ SOVEREIGN BYPASS: Don't lock if we are in a sub-kernel/test cycle
        if os.environ.get("VIBE_NO_LOCK") == "1":
            logger.info("[PRAKRITI] Test Mode: Bypassing session lock.")
            self.session = KernelSessionContext(
                session_id=f"test-{str(uuid.uuid4())[:4]}",
                boot_time=time.time(),
                boot_commit="0000000",
            )
            return self.session

        # Ghost Lock Protocol
        lock_file = self._prakriti_dir / "session.lock"
        if lock_file.exists():
            try:
                stored_pid = int(lock_file.read_text().strip())
                if self._is_process_alive(stored_pid):
                    raise RuntimeError(
                        f"Session already running (PID {stored_pid}). If this is incorrect, delete {lock_file}"
                    )
                else:
                    logger.warning(f"[PRAKRITI] Removed stale lock from dead session (PID {stored_pid})")
                    lock_file.unlink()
            except ValueError:
                # Invalid PID in lock file, remove it
                logger.warning("[PRAKRITI] Invalid lock file content, removing")
                lock_file.unlink()

        # Create new session
        self.session = KernelSessionContext(
            session_id=str(uuid.uuid4())[:8],
            boot_time=time.time(),
            boot_commit=self.git.head_sha(),
        )

        # Write lock file with our PID
        lock_file.write_text(str(os.getpid()))

        logger.info(f"[PRAKRITI] Session started: {self.session.session_id}")
        return self.session

    def end_session(self) -> Optional[CommitResult]:
        """End session (called on kernel shutdown).

        Returns:
            CommitResult from final commit, None if clean
        """
        if not self.session:
            logger.warning("[PRAKRITI] No active session to end")
            return None

        # 1. Save snapshot
        snapshot_name = f"shutdown_{self.session.session_id}_{int(time.time())}"
        self.save_snapshot(snapshot_name)

        # 2. Final commit
        result = self.commit_if_dirty(
            message=f"Session end: {self.session.session_id}",
            commit_type="chore",
            scope="session",
        )

        # 3. Remove lock file
        lock_file = self._prakriti_dir / "session.lock"
        if lock_file.exists():
            lock_file.unlink()

        session_id = self.session.session_id
        self.session = None

        logger.info(f"[PRAKRITI] Session ended: {session_id}")
        return result

    def recover_from_crash(self) -> Optional[CommitResult]:
        """Handle crash recovery on boot.

        Called when boot detects dirty state from previous session.

        Returns:
            CommitResult if recovery commit made, None if clean
        """
        if not self.is_dirty:
            return None

        # Mark session as crash recovery
        if self.session:
            self.session.crash_recovery = True

        # Commit with recovery marker
        result = self.commit_if_dirty(
            message="Crash recovery: uncommitted state from previous session",
            commit_type="chore",
            scope="recovery",
        )

        if result:
            logger.warning(f"[PRAKRITI] Crash recovery committed: {result.git_sha[:7]}")

        return result

    # =========================================================================
    # OPUS-027: Snapshot Operations
    # =========================================================================

    def save_snapshot(self, name: str) -> str:
        """Save complete state snapshot to disk.

        Args:
            name: Snapshot name (e.g., "shutdown_abc123_1702400000")

        Returns:
            Path to snapshot file
        """
        snapshot = self.snapshot()
        snapshots_dir = self._prakriti_dir / "snapshots"
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        path = snapshots_dir / f"{name}.json"

        # Convert snapshot to dict
        snapshot_dict = {
            "timestamp": snapshot.timestamp,
            "git": snapshot.git,
            "files": snapshot.files,
            "kernel": snapshot.kernel,
            "ephemeral": snapshot.ephemeral,
            "personas": snapshot.personas,
            "session": {
                "session_id": self.session.session_id if self.session else None,
                "boot_time": self.session.boot_time if self.session else None,
                "commit_count": self.session.commit_count if self.session else 0,
            },
        }

        path.write_text(json.dumps(snapshot_dict, indent=2, default=str))
        logger.debug(f"[PRAKRITI] Snapshot saved: {path}")
        return str(path)

    def restore_snapshot(self, name: str) -> Dict[str, Any]:
        """Restore state from snapshot.

        Note: This restores runtime state only. Git and Ledger
        are NOT modified (they are authoritative sources).

        Args:
            name: Snapshot name to restore

        Returns:
            The restored snapshot data
        """
        path = self._prakriti_dir / "snapshots" / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {name}")

        data = json.loads(path.read_text())
        logger.info(f"[PRAKRITI] Snapshot loaded: {name}")
        return data

    def list_snapshots(self) -> List[str]:
        """List available snapshots.

        Returns:
            List of snapshot names
        """
        snapshots_dir = self._prakriti_dir / "snapshots"
        if not snapshots_dir.exists():
            return []
        return sorted([p.stem for p in snapshots_dir.glob("*.json")])

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _is_process_alive(self, pid: int) -> bool:
        """Check if a process with given PID is still running.

        Args:
            pid: Process ID to check

        Returns:
            True if process is alive
        """
        try:
            os.kill(pid, 0)  # Signal 0 = check existence only
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            # Process exists but we don't have permission to signal it
            return True
