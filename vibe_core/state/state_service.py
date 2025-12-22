"""
P0+: StateService - Single Point of Truth for All State Operations

This is the ONLY authorized interface for writing state files.
All direct file writes MUST go through this service.

Architecture (P0+: Apple Magic - "It Just Works"):
    Writer → StateService.save() → File Write + mark_dirty()
                    ↓
                _maybe_auto_commit()  ← NEW: Invisible hand
                    ↓
            Auto-commits when threshold reached OR session ends
            (Works regardless of Heartbeat presence)

Features:
    - Thread-safe singleton
    - Automatic backup rotation (max 5 per file)
    - JSONL append support for logs
    - 🍎 AUTO-COMMIT: Threshold-based commits (no manual intervention)
    - 🍎 SESSION-END: atexit handler for clean shutdown
    - Integration with Weaver for commits (when available)
    - Cleanup policies for unbounded files

The Apple Philosophy:
    "Simple is hard. We did the hard work so you don't have to think about it."

OPUS Reference: P0-STATE-AUDIT.md, OPUS-140-SANSKRIT-MATRIX.md
"""

import atexit
import json
import logging
import shutil
import subprocess
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger("STATE.SERVICE")


@dataclass
class StatePolicy:
    """Policy for a state file."""

    max_backups: int = 5
    max_size_kb: int = 500  # Trigger consolidation above this
    retention_days: int = 7  # For backups
    append_mode: bool = False  # True for JSONL files
    consolidation_fn: Optional[Callable[[List[Dict]], List[Dict]]] = None


# Lazy import for Samskara consolidation (avoid circular imports)
def _get_viveka_consolidation_fn():
    """Get consolidation function for viveka_decisions.json."""
    try:
        from .samskara import consolidate_viveka_decisions

        return consolidate_viveka_decisions
    except ImportError:
        return None


# Default policies by file pattern
DEFAULT_POLICIES: Dict[str, StatePolicy] = {
    "viveka_decisions.json": StatePolicy(
        max_backups=3,
        max_size_kb=100,
        consolidation_fn=None,  # Set at runtime via _init_consolidation
    ),
    "synapses.json": StatePolicy(max_backups=5, max_size_kb=50),
    "session.json": StatePolicy(max_backups=2, max_size_kb=1000),
    "karma_history.jsonl": StatePolicy(append_mode=True, max_size_kb=100),
    "observations.jsonl": StatePolicy(append_mode=True, max_size_kb=100),
    "syscalls.jsonl": StatePolicy(append_mode=True, max_size_kb=500),
}


def _init_consolidation_policies():
    """Initialize consolidation functions (called once at startup)."""
    fn = _get_viveka_consolidation_fn()
    if fn:
        DEFAULT_POLICIES["viveka_decisions.json"].consolidation_fn = fn


@dataclass
class WriteResult:
    """Result of a write operation."""

    success: bool
    path: Path
    backup_created: bool = False
    consolidation_triggered: bool = False
    error: Optional[str] = None


class StateService:
    """
    👑 THE SUPREME STATE SERVICE (P0+ Implementation)

    Single Point of Truth for all state operations.
    Thread-safe singleton with automatic lifecycle management.

    🍎 APPLE MAGIC: Auto-commits happen invisibly - you never think about it.

    Usage:
        service = get_state_service(workspace)
        result = service.save("synapses.json", data)  # Auto-commits when ready!
        result = service.append("karma_history.jsonl", entry)
        data = service.load("synapses.json")
    """

    # =========================================================================
    # 🍎 APPLE MAGIC CONSTANTS
    # =========================================================================
    AUTO_COMMIT_THRESHOLD = 5  # Auto-commit after N writes
    AUTO_COMMIT_SECONDS = 30  # Or after N seconds since last commit
    HEARTBEAT_PULSE_FILE = "last_pulse.json"  # Check if Heartbeat is alive

    _lock = threading.Lock()
    _dirty_files: Set[Path] = set()
    _atexit_registered = False

    def __init__(self, workspace: Path):
        """
        Initialize StateService.

        Args:
            workspace: Project root directory
        """
        self.workspace = Path(workspace).resolve()
        self.state_root = self.workspace / ".opus_state"
        self.state_root.mkdir(parents=True, exist_ok=True)

        # Initialize consolidation functions (Phase 2: Samskara)
        _init_consolidation_policies()

        # Policies (can be extended at runtime)
        self.policies: Dict[str, StatePolicy] = DEFAULT_POLICIES.copy()

        # Track writes for Weaver integration
        self._write_count = 0
        self._writes_since_commit = 0
        self._last_write = None
        self._last_commit = None
        self._auto_commit_enabled = True

        # 🍎 Register session-end cleanup (Apple Magic: clean shutdown)
        self._register_atexit()

        logger.info(f"StateService initialized: {self.state_root}")

    # =========================================================================
    # PUBLIC API: File Operations
    # =========================================================================

    def save(self, filename: str, data: Any, create_backup: bool = True, indent: int = 2) -> WriteResult:
        """
        Save state to a JSON file.

        This is the ONLY way to write state files.

        Args:
            filename: Relative to .opus_state/ (e.g., "synapses.json")
            data: Data to save (will be JSON serialized)
            create_backup: Whether to create a backup first
            indent: JSON indentation (default 2)

        Returns:
            WriteResult with success status
        """
        with self._lock:
            try:
                target_path = self.state_root / filename
                policy = self._get_policy(filename)
                backup_created = False
                consolidation_triggered = False

                # 1. Backup Management (if file exists)
                if create_backup and target_path.exists():
                    self._rotate_backups(filename, policy)
                    backup_created = True

                # 2. Check size for consolidation
                if target_path.exists():
                    size_kb = target_path.stat().st_size / 1024
                    if size_kb > policy.max_size_kb and policy.consolidation_fn:
                        data = self._consolidate(filename, data, policy)
                        consolidation_triggered = True

                # 3. Atomic Write
                target_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = target_path.with_suffix(".tmp")

                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

                temp_path.replace(target_path)

                # 4. Mark as dirty for Weaver
                self._dirty_files.add(target_path)
                self._write_count += 1
                self._writes_since_commit += 1
                self._last_write = datetime.now()

                logger.debug(f"💾 State saved: {filename}")

                # 5. 🍎 APPLE MAGIC: Check if we should auto-commit
                self._maybe_auto_commit()

                return WriteResult(
                    success=True,
                    path=target_path,
                    backup_created=backup_created,
                    consolidation_triggered=consolidation_triggered,
                )

            except Exception as e:
                logger.error(f"❌ Failed to save {filename}: {e}")
                return WriteResult(
                    success=False,
                    path=self.state_root / filename,
                    error=str(e),
                )

    def append(self, filename: str, entry: Dict[str, Any]) -> WriteResult:
        """
        Append entry to a JSONL file.

        For log files (karma_history.jsonl, observations.jsonl, etc.)

        Args:
            filename: Relative to .opus_state/ (e.g., "karma_history.jsonl")
            entry: Dictionary to append as a JSON line

        Returns:
            WriteResult with success status
        """
        with self._lock:
            try:
                target_path = self.state_root / filename
                target_path.parent.mkdir(parents=True, exist_ok=True)
                policy = self._get_policy(filename)

                # Check rotation before append
                consolidation_triggered = False
                if target_path.exists():
                    size_kb = target_path.stat().st_size / 1024
                    if size_kb > policy.max_size_kb:
                        self._archive_log(filename)
                        consolidation_triggered = True

                # Append line
                with open(target_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

                # Mark dirty
                self._dirty_files.add(target_path)
                self._write_count += 1
                self._writes_since_commit += 1

                # 🍎 APPLE MAGIC: Check if we should auto-commit
                self._maybe_auto_commit()

                return WriteResult(
                    success=True,
                    path=target_path,
                    consolidation_triggered=consolidation_triggered,
                )

            except Exception as e:
                logger.error(f"❌ Failed to append to {filename}: {e}")
                return WriteResult(
                    success=False,
                    path=self.state_root / filename,
                    error=str(e),
                )

    def load(self, filename: str, default: Any = None) -> Any:
        """
        Load state from a JSON file.

        Args:
            filename: Relative to .opus_state/
            default: Default value if file doesn't exist

        Returns:
            Loaded data or default
        """
        target_path = self.state_root / filename

        if not target_path.exists():
            return default

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Invalid JSON in {filename}: {e}")
            return default
        except Exception as e:
            logger.error(f"❌ Failed to load {filename}: {e}")
            return default

    def load_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load all entries from a JSONL file.

        Args:
            filename: Relative to .opus_state/

        Returns:
            List of dictionaries
        """
        target_path = self.state_root / filename
        entries = []

        if not target_path.exists():
            return entries

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"❌ Failed to load JSONL {filename}: {e}")

        return entries

    # =========================================================================
    # PUBLIC API: Lifecycle Management
    # =========================================================================

    def get_dirty_files(self) -> List[Path]:
        """Get list of files written since last clear."""
        return list(self._dirty_files)

    def clear_dirty_flags(self) -> None:
        """Clear dirty flags after successful commit."""
        with self._lock:
            self._dirty_files.clear()

    def mark_dirty(self, path: Path) -> None:
        """
        Mark an external file as dirty for auto-commit tracking.

        This allows external writers (like IOService) to register their
        writes with StateService's unified auto-commit system.

        Args:
            path: Absolute path to the dirty file
        """
        with self._lock:
            self._dirty_files.add(path)
            self._writes_since_commit += 1
            self._last_write = datetime.now()

            # Trigger auto-commit check (same as internal writes)
            self._maybe_auto_commit()

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "write_count": self._write_count,
            "last_write": self._last_write.isoformat() if self._last_write else None,
            "dirty_files": len(self._dirty_files),
            "state_root": str(self.state_root),
        }

    def cleanup_backups(self) -> int:
        """
        Run cleanup on all backup directories.

        Returns:
            Number of files deleted
        """
        deleted = 0

        with self._lock:
            for backup_dir in self.state_root.glob("*_backup"):
                if backup_dir.is_dir():
                    # Get stem to find policy
                    stem = backup_dir.name.replace("_backup", "")

                    # Find matching policy
                    policy = None
                    for pattern, p in self.policies.items():
                        if stem in pattern:
                            policy = p
                            break

                    if policy is None:
                        policy = StatePolicy()  # Use default

                    # Sort by modification time, oldest first
                    backups = sorted(backup_dir.glob("*"), key=lambda p: p.stat().st_mtime)

                    # Delete oldest until under limit
                    while len(backups) > policy.max_backups:
                        oldest = backups.pop(0)
                        oldest.unlink()
                        deleted += 1
                        logger.debug(f"🗑️ Deleted old backup: {oldest.name}")

        if deleted:
            logger.info(f"🧹 Cleanup: deleted {deleted} old backups")

        return deleted

    # =========================================================================
    # INTERNAL: Backup & Consolidation
    # =========================================================================

    def _get_policy(self, filename: str) -> StatePolicy:
        """Get policy for a filename."""
        return self.policies.get(filename, StatePolicy())

    def _rotate_backups(self, filename: str, policy: StatePolicy) -> None:
        """Create backup and rotate old ones."""
        source = self.state_root / filename
        if not source.exists():
            return

        stem = Path(filename).stem
        backup_dir = self.state_root / f"{stem}_backup"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped backup
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{ts}_{filename}"
        shutil.copy2(source, backup_dir / backup_name)

        # Rotate: keep only max_backups
        backups = sorted(backup_dir.glob(f"*_{filename}"))
        while len(backups) > policy.max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
            logger.debug(f"🔄 Rotated out: {oldest.name}")

    def _consolidate(self, filename: str, data: Any, policy: StatePolicy) -> Any:
        """
        Consolidate data using policy's consolidation function.

        This is the SAMSKARA layer hook - where raw data becomes patterns.
        """
        if policy.consolidation_fn and isinstance(data, list):
            logger.info(f"🔮 Consolidating {filename}...")
            return policy.consolidation_fn(data)
        return data

    def _archive_log(self, filename: str) -> None:
        """Archive a log file that's too large."""
        source = self.state_root / filename
        if not source.exists():
            return

        ts = datetime.now().strftime("%Y%m%d")
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        archive_name = f"{stem}_archive_{ts}{suffix}"

        # Move current to archive
        shutil.move(source, self.state_root / archive_name)
        logger.info(f"📦 Archived log: {filename} → {archive_name}")

    # =========================================================================
    # 🍎 APPLE MAGIC: Auto-Commit System
    # =========================================================================

    def _register_atexit(self) -> None:
        """Register session-end cleanup handler."""
        if not StateService._atexit_registered:
            atexit.register(self._on_session_end)
            StateService._atexit_registered = True
            logger.debug("🍎 Session-end handler registered")

    def _on_session_end(self) -> None:
        """
        Called when Python process exits.

        Commits any remaining dirty state. This is the "Apple Magic"
        safety net - even if you forget to commit, we've got you covered.
        """
        if self._dirty_files:
            logger.info("🍎 Session ending - committing dirty state...")
            self._do_auto_commit(reason="session_end")

    def _maybe_auto_commit(self) -> None:
        """
        Check if we should auto-commit (the invisible hand).
        """
        if not self._auto_commit_enabled:
            return

        # 🛡️ CIRCUIT BREAKER: Disable commits via environment variable
        import os
        if os.environ.get("VIBE_NO_GIT_COMMIT") == "1":
            return

        if not self._dirty_files:
            return

        # Check if Heartbeat is handling commits (don't double-commit)
        if self._is_heartbeat_alive():
            return

        # Check write threshold
        if self._writes_since_commit >= self.AUTO_COMMIT_THRESHOLD:
            self._do_auto_commit(reason="threshold")
            return

        # Check time threshold
        if self._last_commit:
            elapsed = (datetime.now() - self._last_commit).total_seconds()
            if elapsed >= self.AUTO_COMMIT_SECONDS and self._writes_since_commit > 0:
                self._do_auto_commit(reason="time")
                return

    def _do_auto_commit(self, reason: str = "auto") -> bool:
        """
        Actually perform the auto-commit.

        Tries Weaver first (integrates with existing infrastructure),
        falls back to direct git if Weaver not available.

        Returns:
            True if commit succeeded
        """
        if not self._dirty_files:
            return False

        try:
            # Try Weaver first (best integration)
            committed = self._commit_via_weaver()

            if not committed:
                # Fallback: direct git
                committed = self._commit_via_git(reason)

            if committed:
                self._writes_since_commit = 0
                self._last_commit = datetime.now()
                self.clear_dirty_flags()
                logger.debug(f"🍎 Auto-commit complete ({reason})")
                return True

        except Exception as e:
            logger.debug(f"🍎 Auto-commit skipped: {e}")

        return False

    def _is_heartbeat_alive(self) -> bool:
        """
        Check if Heartbeat is actively managing commits.

        If Heartbeat is alive (pulsed recently), we don't need to auto-commit
        because it will handle it on its next pulse.
        """
        pulse_file = self.state_root / self.HEARTBEAT_PULSE_FILE
        if not pulse_file.exists():
            return False

        try:
            # Check pulse age
            mtime = pulse_file.stat().st_mtime
            age = datetime.now().timestamp() - mtime
            # If pulsed in last 60 seconds, Heartbeat is alive
            return age < 60
        except Exception:
            return False

    def _commit_via_weaver(self) -> bool:
        """Try to commit via StateSyncWeaver."""
        try:
            from .prakriti import Prakriti
            from .weaver import get_state_sync_weaver

            prakriti = Prakriti(self.workspace)
            weaver = get_state_sync_weaver(prakriti)
            result = weaver.pulse()

            return result.success if hasattr(result, "success") else bool(result)
        except Exception:
            return False

    def _commit_via_git(self, reason: str) -> bool:
        """
        Fallback: commit directly via git.

        This is used when Weaver is not available (e.g., early initialization).
        """
        try:
            # Stage all dirty files
            dirty_list = list(self._dirty_files)
            if not dirty_list:
                return False

            # Relative paths for git
            rel_paths = [str(p.relative_to(self.workspace)) for p in dirty_list]

            # Git add
            subprocess.run(
                ["git", "add"] + rel_paths,
                cwd=self.workspace,
                check=True,
                capture_output=True,
            )

            # Git commit (skip hooks for runtime state)
            msg = f"🍎 Auto-commit ({reason}): {len(dirty_list)} state files"
            subprocess.run(
                ["git", "commit", "-m", msg, "--no-verify"],
                cwd=self.workspace,
                check=True,
                capture_output=True,
            )

            logger.info(f"🍎 Direct git commit: {len(dirty_list)} files")
            return True

        except subprocess.CalledProcessError as e:
            # Might fail if nothing to commit (clean)
            if b"nothing to commit" in (e.stdout or b"") + (e.stderr or b""):
                return True  # Actually clean
            return False
        except Exception:
            return False


# =========================================================================
# SINGLETON ACCESS
# =========================================================================

_instance: Optional[StateService] = None
_instance_lock = threading.Lock()


def get_state_service(workspace: Optional[Path] = None) -> StateService:
    """
    Get the global StateService singleton.

    Args:
        workspace: Project root (required on first call)

    Returns:
        StateService instance
    """
    global _instance

    with _instance_lock:
        if _instance is None:
            if workspace is None:
                workspace = Path.cwd()
            _instance = StateService(workspace)

        return _instance


def reset_state_service() -> None:
    """Reset the global singleton (mainly for testing)."""
    global _instance
    with _instance_lock:
        _instance = None
