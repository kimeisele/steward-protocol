"""
OPUS State Manager - Plugin-Local State Abstraction

This is the PROPER way to handle plugin state:
- Each plugin owns its state in its own directory
- State is JSON-based and git-trackable
- Clean abstraction - no mixing with shared system resources

Architecture (Fractal Holon):
    ┌─────────────────────────────────────────────────────────────┐
    │                    OPUS ASSISTANT PLUGIN                     │
    │  ┌─────────────────────────────────────────────────────────┐│
    │  │                   StateManager                          ││
    │  │  ┌─────────────────────────────────────────────────────┐││
    │  │  │  .opus_state/                                       │││
    │  │  │  ├── observations.jsonl   (ALERT/WARN history)     │││
    │  │  │  ├── karma_history.jsonl  (karma scores over time) │││
    │  │  │  └── session.json         (current session state)  │││
    │  │  └─────────────────────────────────────────────────────┘││
    │  └─────────────────────────────────────────────────────────┘│
    │                           │                                  │
    │                     Optional Sync                            │
    │                           │                                  │
    │                           ▼                                  │
    │              System Ledger (if needed)                       │
    └─────────────────────────────────────────────────────────────┘

This is a HOLON - self-contained, self-similar, composable.
"""

import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("OPUS_STATE")

# Default state directory name (relative to plugin root)
DEFAULT_STATE_DIR = ".opus_state"


@dataclass
class ObservationEntry:
    """A single observation entry for persistence."""

    timestamp: str
    severity: str  # INFO, WARN, ALERT, INSIGHT
    message: str
    source: str
    context_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObservationEntry":
        return cls(
            timestamp=data.get("timestamp", ""),
            severity=data.get("severity", "INFO"),
            message=data.get("message", ""),
            source=data.get("source", "unknown"),
            context_hash=data.get("context_hash"),
        )


@dataclass
class KarmaEntry:
    """A single karma score entry for history."""

    timestamp: str
    score: int
    error_count: int = 0
    warning_count: int = 0
    crash_count: int = 0
    success_count: int = 0
    boot_mode: str = "full_power"  # safe_mode, cautious_mode, full_power

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KarmaEntry":
        return cls(
            timestamp=data.get("timestamp", ""),
            score=data.get("score", 100),
            error_count=data.get("error_count", 0),
            warning_count=data.get("warning_count", 0),
            crash_count=data.get("crash_count", 0),
            success_count=data.get("success_count", 0),
            boot_mode=data.get("boot_mode", "full_power"),
        )


@dataclass
class SessionState:
    """Current session state."""

    session_id: str
    started_at: str
    last_karma_score: int = 100
    observation_count: int = 0
    boot_mode: str = "full_power"
    # 🎛️ CONTROL PLANE: Persistent view preferences for OPUS.md
    # Controls which panels are visible/hidden in the dashboard
    view_preferences: Dict[str, bool] = field(
        default_factory=lambda: {"show_tests": True, "show_debug": False, "show_code_health": True}
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        return cls(
            session_id=data.get("session_id", "unknown"),
            started_at=data.get("started_at", datetime.now().isoformat()),
            last_karma_score=data.get("last_karma_score", 100),
            observation_count=data.get("observation_count", 0),
            boot_mode=data.get("boot_mode", "full_power"),
            # 🎛️ Load view preferences (with sensible defaults)
            view_preferences=data.get(
                "view_preferences", {"show_tests": True, "show_debug": False, "show_code_health": True}
            ),
        )


class OpusStateManager:
    """
    Plugin-local state manager for OPUS Assistant.

    This is the PROPER abstraction for state management:
    - All state lives in .opus_state/ within the plugin
    - JSON-based, git-trackable
    - Clean separation from system-wide resources

    Usage:
        state_mgr = OpusStateManager(plugin_root=Path("vibe_core/plugins/opus_assistant"))
        state_mgr.append_observation(ObservationEntry(...))
        state_mgr.record_karma(KarmaEntry(...))
        observations = state_mgr.get_recent_observations(hours=24)
    """

    # File names within state directory
    OBSERVATIONS_FILE = "observations.jsonl"
    KARMA_FILE = "karma_history.jsonl"
    SESSION_FILE = "session.json"

    def __init__(
        self,
        plugin_root: Path,
        state_dir_name: str = DEFAULT_STATE_DIR,
        max_observations: int = 1000,
        max_karma_entries: int = 100,
    ):
        """
        Initialize state manager.

        Args:
            plugin_root: Path to the plugin directory
            state_dir_name: Name of state directory (default: .opus_state)
            max_observations: Max observations to keep (FIFO)
            max_karma_entries: Max karma entries to keep (FIFO)
        """
        self._plugin_root = plugin_root
        self._state_dir = plugin_root / state_dir_name
        self._max_observations = max_observations
        self._max_karma_entries = max_karma_entries

        # Ensure state directory exists
        self._ensure_state_dir()

        logger.debug(f"📁 OPUS StateManager initialized at {self._state_dir}")

    def _ensure_state_dir(self) -> None:
        """Ensure state directory exists and has .gitkeep."""
        self._state_dir.mkdir(parents=True, exist_ok=True)

        # Create .gitkeep to ensure directory is tracked
        gitkeep = self._state_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("# OPUS State Directory - git-tracked for persistence\n")

    @property
    def state_dir(self) -> Path:
        """Get the state directory path."""
        return self._state_dir

    # =========================================================================
    # Observations (JSONL - append-only)
    # =========================================================================

    def append_observation(self, entry: ObservationEntry) -> bool:
        """
        Append an observation to the observations file.

        Only ALERT and WARN should be persisted (to keep file small).
        INFO and INSIGHT are transient.

        Returns:
            True if successfully written
        """
        if entry.severity not in ("ALERT", "WARN"):
            logger.debug(f"Skipping {entry.severity} observation (not persisted)")
            return True

        try:
            obs_file = self._state_dir / self.OBSERVATIONS_FILE
            with open(obs_file, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")

            logger.debug(f"📝 Observation persisted: {entry.severity}")

            # Trim if too large
            self._trim_jsonl_file(obs_file, self._max_observations)

            return True
        except Exception as e:
            logger.warning(f"Failed to persist observation: {e}")
            return False

    def get_observations(self, limit: Optional[int] = None) -> List[ObservationEntry]:
        """
        Get observations from the state file.

        Args:
            limit: Max number to return (None = all)

        Returns:
            List of observations (newest first)
        """
        obs_file = self._state_dir / self.OBSERVATIONS_FILE
        if not obs_file.exists():
            return []

        entries = []
        try:
            with open(obs_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            entries.append(ObservationEntry.from_dict(data))
                        except json.JSONDecodeError:
                            continue

            # Newest first
            entries.reverse()

            if limit:
                entries = entries[:limit]

            return entries
        except Exception as e:
            logger.warning(f"Failed to read observations: {e}")
            return []

    def get_recent_observations(self, hours: int = 24) -> List[ObservationEntry]:
        """Get observations from the last N hours."""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(hours=hours)
        all_obs = self.get_observations()

        recent = []
        for obs in all_obs:
            try:
                obs_time = datetime.fromisoformat(obs.timestamp.replace("Z", ""))
                if obs_time >= cutoff:
                    recent.append(obs)
            except (ValueError, TypeError):
                continue

        return recent

    # =========================================================================
    # Karma History (JSONL - append-only)
    # =========================================================================

    def record_karma(self, entry: KarmaEntry) -> bool:
        """
        Record a karma score entry.

        Returns:
            True if successfully written
        """
        try:
            karma_file = self._state_dir / self.KARMA_FILE
            with open(karma_file, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")

            logger.debug(f"📊 Karma recorded: {entry.score}/100")

            # Trim if too large
            self._trim_jsonl_file(karma_file, self._max_karma_entries)

            return True
        except Exception as e:
            logger.warning(f"Failed to record karma: {e}")
            return False

    def get_karma_history(self, limit: Optional[int] = None) -> List[KarmaEntry]:
        """
        Get karma history.

        Args:
            limit: Max number to return (None = all)

        Returns:
            List of karma entries (newest first)
        """
        karma_file = self._state_dir / self.KARMA_FILE
        if not karma_file.exists():
            return []

        entries = []
        try:
            with open(karma_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            entries.append(KarmaEntry.from_dict(data))
                        except json.JSONDecodeError:
                            continue

            # Newest first
            entries.reverse()

            if limit:
                entries = entries[:limit]

            return entries
        except Exception as e:
            logger.warning(f"Failed to read karma history: {e}")
            return []

    def get_last_karma(self) -> Optional[KarmaEntry]:
        """Get the most recent karma entry."""
        history = self.get_karma_history(limit=1)
        return history[0] if history else None

    # =========================================================================
    # Session State (JSON - single file, overwritten)
    # =========================================================================

    def save_session(self, session: SessionState) -> bool:
        """
        Save current session state.

        ⚡ VAJRA: Uses atomic write to prevent corruption on crash.
        """
        try:
            session_file = self._state_dir / self.SESSION_FILE
            content = json.dumps(session.to_dict(), indent=2)
            self._atomic_write(session_file, content)

            logger.debug(f"💾 Session state saved: {session.session_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to save session: {e}")
            return False

    def load_session(self) -> Optional[SessionState]:
        """Load session state (if exists)."""
        session_file = self._state_dir / self.SESSION_FILE
        if not session_file.exists():
            return None

        try:
            with open(session_file, "r") as f:
                data = json.load(f)
            return SessionState.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
            return None

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _atomic_write(self, file_path: Path, content: str) -> None:
        """
        ⚡ VAJRA: Atomic write to prevent corruption on crash.

        Uses temp file + fsync + atomic rename pattern.
        If kernel is kill -9'd during write, file stays intact.
        """
        # Write to temp file in same directory (for same-filesystem rename)
        fd, tmp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Atomic rename (POSIX guarantees atomicity)
            os.rename(tmp_path, file_path)
            logger.debug(f"⚡ Atomic write: {file_path.name}")
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _trim_jsonl_file(self, file_path: Path, max_entries: int) -> None:
        """
        Trim a JSONL file to max entries (keep newest).

        ⚡ VAJRA: Uses atomic write for crash safety.
        """
        if not file_path.exists():
            return

        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            if len(lines) > max_entries:
                # Keep only the newest entries
                lines = lines[-max_entries:]
                content = "".join(lines)
                self._atomic_write(file_path, content)
                logger.debug(f"Trimmed {file_path.name} to {max_entries} entries")
        except Exception as e:
            logger.warning(f"Failed to trim {file_path.name}: {e}")

    def clear_all(self) -> None:
        """Clear all state (for testing)."""
        for file_name in [self.OBSERVATIONS_FILE, self.KARMA_FILE, self.SESSION_FILE]:
            file_path = self._state_dir / file_name
            if file_path.exists():
                file_path.unlink()
        logger.info("🗑️ All OPUS state cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get state statistics."""
        obs_count = len(self.get_observations())
        karma_count = len(self.get_karma_history())
        last_karma = self.get_last_karma()
        session = self.load_session()

        return {
            "state_dir": str(self._state_dir),
            "observation_count": obs_count,
            "karma_entry_count": karma_count,
            "last_karma_score": last_karma.score if last_karma else None,
            "session_id": session.session_id if session else None,
            "session_started": session.started_at if session else None,
        }


# Convenience function for getting state manager
def get_state_manager(plugin_root: Optional[Path] = None) -> OpusStateManager:
    """
    Get an OpusStateManager instance.

    Args:
        plugin_root: Plugin root path (auto-detected if None)

    Returns:
        OpusStateManager instance
    """
    if plugin_root is None:
        # Auto-detect: assume we're in vibe_core/plugins/opus_assistant/
        plugin_root = Path(__file__).parent.parent

    return OpusStateManager(plugin_root=plugin_root)
