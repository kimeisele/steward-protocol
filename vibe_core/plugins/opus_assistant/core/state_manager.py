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

# Default state directory name (DEPRECATED - StateService computes path dynamically)
# Kept for backwards compatibility but not used when StateService is available
DEFAULT_STATE_DIR = ".vibe/state/plugins/opus_assistant"


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
class SyscallEntry:
    """
    A single syscall execution record for experience replay.

    OPUS-031 Layer 2: Syscall Console
    This is NOT a log - it's an Experience Replay Buffer.
    Successful syscalls become few-shot examples for future executions.

    Example:
        SyscallEntry(
            timestamp="2025-12-13T14:30:00",
            intent="Create a Python file with hello world",
            syscall_type="WRITE_FILE",
            parameters={"path": "hello.py", "content": "print('Hello')"},
            result="SUCCESS",
            output="File created: hello.py",
            execution_time_ms=150
        )
    """

    timestamp: str
    intent: str  # Natural language intent from user/AI
    syscall_type: str  # WRITE_FILE, RUN_COMMAND, SPAWN_AGENT, etc.
    parameters: Dict[str, Any]  # The actual syscall parameters
    result: str  # SUCCESS, FAILURE, PARTIAL, ROLLBACK
    output: Optional[str] = None  # Output/error message
    execution_time_ms: int = 0
    context_hash: Optional[str] = None  # Git commit at time of execution
    rollback_info: Optional[str] = None  # How to undo this syscall

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyscallEntry":
        return cls(
            timestamp=data.get("timestamp", ""),
            intent=data.get("intent", ""),
            syscall_type=data.get("syscall_type", "UNKNOWN"),
            parameters=data.get("parameters", {}),
            result=data.get("result", "UNKNOWN"),
            output=data.get("output"),
            execution_time_ms=data.get("execution_time_ms", 0),
            context_hash=data.get("context_hash"),
            rollback_info=data.get("rollback_info"),
        )

    def is_successful(self) -> bool:
        """Check if this syscall was successful (for experience replay)."""
        return self.result in ("SUCCESS", "PARTIAL")


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
    # 🎯 INTENT BUFFER: Current pending intent awaiting execution/approval
    # Layer 1.5: The "Frontallappen" - what the system plans to do next
    pending_intent: Optional[Dict[str, Any]] = field(default=None)

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
            # 🎯 Load pending intent (if any)
            pending_intent=data.get("pending_intent"),
        )


class OpusStateManager:
    """
    Plugin-local state manager for OPUS Assistant.

    OPUS-207 FIX: State now lives at PROJECT_ROOT/.vibe/state/plugins/opus_assistant/
    NOT inside the plugin code directory!

    This is the PROPER abstraction for state management:
    - All state lives in .vibe/state/plugins/opus_assistant/ (Sovereign State)
    - JSON-based, git-trackable
    - Clean separation: State in project root, Code in vibe_core/plugins/

    Usage:
        state_mgr = get_state_manager()  # Auto-detects project root
        # Or with explicit workspace:
        state_mgr = OpusStateManager(workspace=Path("/path/to/project"))
        state_mgr.append_observation(ObservationEntry(...))
        state_mgr.record_karma(KarmaEntry(...))
        observations = state_mgr.get_recent_observations(hours=24)
    """

    # File names within state directory
    OBSERVATIONS_FILE = "observations.jsonl"
    KARMA_FILE = "karma_history.jsonl"
    SESSION_FILE = "session.json"
    SYSCALLS_FILE = "syscalls.jsonl"  # Layer 2: Experience Replay Buffer

    def __init__(
        self,
        workspace: Path,
        state_dir_name: str = DEFAULT_STATE_DIR,
        max_observations: int = 1000,
        max_karma_entries: int = 100,
    ):
        """
        Initialize state manager.

        OPUS-207 FIX: Now takes workspace (project root), not plugin_root.
        State is stored at PROJECT_ROOT/.vibe/state/plugins/opus_assistant/

        Args:
            workspace: Path to the project root (NOT the plugin directory!)
            state_dir_name: DEPRECATED - uses namespaced StateService
            max_observations: Max observations to keep (FIFO)
            max_karma_entries: Max karma entries to keep (FIFO)
        """
        self._workspace = workspace

        # 🍎 STATE: Namespaced state service (ADR-204)
        # OPUS-207: Use workspace (project root), state goes to .vibe/state/plugins/opus_assistant/
        from vibe_core.state.state_service import get_state_service

        self._state_service = get_state_service(self._workspace, plugin_id="opus_assistant")
        self._state_dir = self._state_service.state_root

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
    # Syscalls (JSONL - append-only) - LAYER 2: Experience Replay Buffer
    # =========================================================================

    def record_syscall(self, entry: SyscallEntry) -> bool:
        """
        Record a syscall execution for experience replay.

        OPUS-031 Layer 2: The syscall history is NOT a log - it's training data.
        Successful syscalls become few-shot examples for future executions.

        Args:
            entry: SyscallEntry with execution details

        Returns:
            True if successfully written
        """
        try:
            syscalls_file = self._state_dir / self.SYSCALLS_FILE
            with open(syscalls_file, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")

            result_emoji = "✅" if entry.is_successful() else "❌"
            logger.debug(f"📟 Syscall recorded: {result_emoji} {entry.syscall_type}")

            # Keep last 500 syscalls (generous buffer for few-shot learning)
            self._trim_jsonl_file(syscalls_file, 500)

            return True
        except Exception as e:
            logger.warning(f"Failed to record syscall: {e}")
            return False

    def get_successful_syscalls(self, syscall_type: Optional[str] = None, limit: int = 10) -> List[SyscallEntry]:
        """
        Get successful syscalls for experience replay (few-shot learning).

        This is the key to autonomous improvement:
        - Find past successful executions of similar intents
        - Use them as examples for the next execution
        - The system learns from its own successes

        Args:
            syscall_type: Optional filter by type (e.g., "WRITE_FILE")
            limit: Max number to return (default: 10 for few-shot)

        Returns:
            List of successful syscalls (newest first)
        """
        syscalls_file = self._state_dir / self.SYSCALLS_FILE
        if not syscalls_file.exists():
            return []

        entries = []
        try:
            with open(syscalls_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            entry = SyscallEntry.from_dict(data)
                            # Only include successful syscalls
                            if entry.is_successful():
                                if syscall_type is None or entry.syscall_type == syscall_type:
                                    entries.append(entry)
                        except json.JSONDecodeError:
                            continue

            # Newest first (most recent successes are most relevant)
            entries.reverse()

            return entries[:limit]
        except Exception as e:
            logger.warning(f"Failed to read syscalls: {e}")
            return []

    def get_syscall_stats(self) -> Dict[str, Any]:
        """
        Get syscall execution statistics.

        OPUS-072: Now distinguishes security denials from real failures!
        Security denials (permission_denied) are CORRECT behavior, not bugs.

        Useful for:
        - Dashboard display (Layer 2 console)
        - Karma calculation (success rate)
        - Identifying patterns in failures
        """
        syscalls_file = self._state_dir / self.SYSCALLS_FILE
        if not syscalls_file.exists():
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "security_denials": 0,
                "success_rate": 0.0,
                "adjusted_success_rate": 0.0,
                "by_type": {},
            }

        stats = {"total": 0, "successful": 0, "failed": 0, "security_denials": 0, "by_type": {}}

        try:
            with open(syscalls_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            entry = SyscallEntry.from_dict(data)
                            stats["total"] += 1

                            if entry.is_successful():
                                stats["successful"] += 1
                            else:
                                stats["failed"] += 1
                                # OPUS-072: Track security denials separately
                                output_str = str(entry.output) if entry.output else ""
                                if "Permission denied" in output_str or "cannot grant" in output_str:
                                    stats["security_denials"] += 1

                            # Count by type
                            stype = entry.syscall_type
                            if stype not in stats["by_type"]:
                                stats["by_type"][stype] = {"total": 0, "successful": 0, "security_denials": 0}
                            stats["by_type"][stype]["total"] += 1
                            if entry.is_successful():
                                stats["by_type"][stype]["successful"] += 1
                            elif "Permission denied" in str(entry.output):
                                stats["by_type"][stype]["security_denials"] += 1

                        except json.JSONDecodeError:
                            continue

            # Calculate success rates
            if stats["total"] > 0:
                stats["success_rate"] = round(stats["successful"] / stats["total"] * 100, 1)
                # OPUS-072: Adjusted rate excludes security denials (they're correct behavior!)
                real_attempts = stats["total"] - stats["security_denials"]
                if real_attempts > 0:
                    stats["adjusted_success_rate"] = round(stats["successful"] / real_attempts * 100, 1)
                else:
                    stats["adjusted_success_rate"] = 100.0  # All were security denials = system working
            else:
                stats["success_rate"] = 0.0
                stats["adjusted_success_rate"] = 0.0

            return stats
        except Exception as e:
            logger.warning(f"Failed to calculate syscall stats: {e}")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "security_denials": 0,
                "success_rate": 0.0,
                "adjusted_success_rate": 0.0,
                "by_type": {},
            }

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

    # =========================================================================
    # View Preferences (Control Cables - Layer 1.5)
    # =========================================================================

    def set_preference(self, key: str, value: Any) -> bool:
        """
        Set a view preference in the current session.

        Layer 1.5 Control Cables: This allows OPUS.md to be bidirectional.
        When a human edits a checkbox in the Control Plane section,
        the ControlCablesParser calls this method to persist the change.

        Args:
            key: Preference key (e.g., "show_tests", "auto_heal", "budget_limit")
            value: Value to set (bool, int, float, str)

        Returns:
            True if successfully saved
        """
        session = self.load_session()
        if not session:
            logger.warning(f"Cannot set preference '{key}': No active session")
            return False

        # Update preference
        session.view_preferences[key] = value
        logger.debug(f"🔌 Control Cable: {key} = {value}")

        return self.save_session(session)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a view preference from the current session.

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        session = self.load_session()
        if not session:
            return default

        return session.view_preferences.get(key, default)

    # =========================================================================
    # Intent Buffer (Layer 1.5 - The "Frontallappen")
    # =========================================================================

    def set_pending_intent(
        self,
        intent: str,
        syscall_type: str,
        params: Dict[str, Any],
        requires_approval: bool = True,
    ) -> bool:
        """
        Set a pending intent awaiting execution/approval.

        Layer 1.5: This is the system's "thought" before action.
        The Intent Buffer shows what the system PLANS to do next.

        Args:
            intent: Natural language description of what we plan to do
            syscall_type: The syscall type that will be executed
            params: Parameters for the syscall
            requires_approval: Whether human approval is needed (checkbox in OPUS.md)

        Returns:
            True if successfully saved
        """
        session = self.load_session()
        if not session:
            logger.warning("Cannot set pending intent: No active session")
            return False

        session.pending_intent = {
            "intent": intent,
            "syscall_type": syscall_type,
            "params": params,
            "requires_approval": requires_approval,
            "approved": False,
            "created_at": datetime.now().isoformat(),
        }
        logger.debug(f"🎯 Intent buffered: {intent[:50]}...")

        return self.save_session(session)

    def get_pending_intent(self) -> Optional[Dict[str, Any]]:
        """
        Get the current pending intent (if any).

        Returns:
            Dict with intent details or None
        """
        session = self.load_session()
        if not session:
            return None
        return session.pending_intent

    def approve_pending_intent(self) -> bool:
        """
        Mark the pending intent as approved.

        Called when human checks the "Execute" checkbox in OPUS.md.

        Returns:
            True if successfully approved
        """
        session = self.load_session()
        if not session or not session.pending_intent:
            logger.warning("Cannot approve: No pending intent")
            return False

        session.pending_intent["approved"] = True
        logger.info(f"✅ Intent approved: {session.pending_intent['intent'][:50]}...")

        return self.save_session(session)

    def clear_pending_intent(self) -> bool:
        """
        Clear the pending intent (after execution or rejection).

        Returns:
            True if successfully cleared
        """
        session = self.load_session()
        if not session:
            return False

        session.pending_intent = None
        return self.save_session(session)

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
def get_state_manager(workspace: Optional[Path] = None) -> OpusStateManager:
    """
    Get an OpusStateManager instance.

    OPUS-207 FIX: Now takes workspace (project root), not plugin_root.

    Args:
        workspace: Project root path (auto-detected if None via pyproject.toml search)

    Returns:
        OpusStateManager instance
    """
    if workspace is None:
        workspace = _find_project_root()

    return OpusStateManager(workspace=workspace)


def _find_project_root() -> Path:
    """
    Robustly find project root by searching upward for pyproject.toml.

    OPUS-207: This is more robust than Path.cwd() which fails when
    running scripts from subdirectories.
    """
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
        if (parent / ".git").exists():
            return parent
    # Fallback: cwd (last resort)
    return Path.cwd()
