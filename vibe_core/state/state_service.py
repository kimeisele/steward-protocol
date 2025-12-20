"""
P0: StateService - Single Point of Truth for All State Operations

This is the ONLY authorized interface for writing state files.
All direct file writes MUST go through this service.

Architecture:
    Writer → StateService.save() → File Write + mark_dirty()
                    ↓
    Heartbeat → Weaver.pulse() → Git Commit

Features:
    - Thread-safe singleton
    - Automatic backup rotation (max 5 per file)
    - JSONL append support for logs
    - Integration with Weaver for commits
    - Cleanup policies for unbounded files

OPUS Reference: P0-STATE-AUDIT.md
"""

import json
import logging
import shutil
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
    👑 THE SUPREME STATE SERVICE (P0 Implementation)

    Single Point of Truth for all state operations.
    Thread-safe singleton with automatic lifecycle management.

    Usage:
        service = get_state_service(workspace)
        result = service.save("synapses.json", data)
        result = service.append("karma_history.jsonl", entry)
        data = service.load("synapses.json")
    """

    _lock = threading.Lock()
    _dirty_files: Set[Path] = set()

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
        self._last_write = None

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
                self._last_write = datetime.now()

                logger.debug(f"💾 State saved: {filename}")

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
