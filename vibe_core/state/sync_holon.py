"""
OPUS-210: StateSyncHolon - TANMATRA Bridge of Prakriti

Sanskrit: तन्मात्र (Tanmatra) = "That-only" / Subtle Element / Essence

In Samkhya philosophy, Tanmatras are the subtle essences from which
gross elements emerge. In Steward Protocol, StateSyncHolon is the
TANMATRA bridge - it binds Plugin state (holons) to Prakriti (substrate).

Named after Arthur Koestler's "holon" concept:
A holon is something that is simultaneously a WHOLE and a PART.

The StateSyncHolon is:
- A PART of Prakriti (the larger state system)
- A WHOLE that contains plugin state discovery, tracking, and sync
- A BRIDGE that binds Plugin holons to unified Prakriti

OPUS-009: "State files in .gitignore = Lobotomy"

Responsibilities:
1. DISCOVER all plugin state paths (Protocol + Convention + Manifest)
2. DIAGNOSE the Guna of each state path (SATTVA/RAJAS/TAMAS)
3. WATCH for changes (file system events via watchdog)
4. STAGE on session boundaries
5. COMMIT via CommitAuthority → Weaver → Git
6. HEAL merge conflicts (UntotbarMergeEngine)
7. RESURRECT from Tamas (stale, broken, ignored)

Lifecycle:
- on_boot(): Discover → Diagnose → Heal Tamas
- on_change(): Update Guna → Queue for commit
- on_shutdown(): Stage all → Commit → Verify
- on_conflict(): Heal → Auto-merge → Log

Tattva Mapping (OPUS-097):
    Prakriti → Tanmatra (SyncHolon) → Plugin Holons (gross elements)

OPUS Reference: OPUS-210-STATE-UNIFICATION, OPUS-009, OPUS-097
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import StateSyncHolonProtocol, StateSyncWeaverProtocol

# OPUS-098: Import StateGuna from canonical location
from vibe_core.state.guna_classifier import StateGuna

if TYPE_CHECKING:
    from vibe_core.state.prakriti import Prakriti

logger = logging.getLogger("SYNC_HOLON")


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class StatePathInfo:
    """Information about a discovered state path."""

    path: Path
    plugin: str
    guna: StateGuna
    last_commit: Optional[str] = None
    last_modified: Optional[float] = None
    is_ignored: bool = False
    content_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": str(self.path),
            "plugin": self.plugin,
            "guna": self.guna.value,
            "last_commit": self.last_commit,
            "last_modified": self.last_modified,
            "is_ignored": self.is_ignored,
            "content_hash": self.content_hash,
        }


@dataclass
class WatcherConfig:
    """Configuration for file system watching."""

    enabled: bool = False
    debounce_seconds: float = 2.0
    watch_patterns: List[str] = field(default_factory=lambda: ["*.json", "*.yaml", "*.db"])
    ignore_patterns: List[str] = field(default_factory=lambda: ["*.tmp", "*.swp", "*~"])


# =============================================================================
# Protocols (Contracts)
# =============================================================================


@runtime_checkable
class PluginStateContract(Protocol):
    """
    Contract every stateful plugin MUST implement.

    This is how plugins declare their state to Prakriti.
    The Fractal Prakriti Contract - every plugin is a Mini-Prakriti.

    Example implementation:

        class MyPlugin:
            def get_state_paths(self) -> List[Path]:
                return [Path(".my_plugin/state/")]

            def snapshot_state(self) -> Dict[str, Any]:
                return {"version": 1, "data": self._runtime_data}

            def restore_state(self, snapshot: Dict[str, Any]) -> None:
                self._runtime_data = snapshot.get("data", {})
    """

    def get_state_paths(self) -> List[Path]:
        """
        Return all paths where this plugin stores state.

        These paths will be:
        1. Auto-discovered by Prakriti
        2. Auto-committed on session boundaries
        3. NEVER ignored by git (LOBOTOMY PREVENTION)

        Examples:
            - [Path(".opus_state/")]
            - [Path(".vibe/state/"), Path("data/vibe_agency.db")]
        """
        ...

    def snapshot_state(self) -> Dict[str, Any]:
        """Return current runtime state for inclusion in system snapshot."""
        ...

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from snapshot (crash recovery)."""
        ...


# =============================================================================
# Exception
# =============================================================================


class GovernanceViolation(Exception):
    """Raised when state governance rules are violated."""

    pass


# =============================================================================
# Main Class: StateSyncHolon
# =============================================================================


class StateSyncHolon(StateSyncHolonProtocol):
    """
    The Zwischeninstanz - bridges Plugin State to Git.

    This is the awakening force that fights entropy.
    Without this, all state drifts toward Tamas (death).
    With this, state is constantly HEALED back toward Sattva.

    The StateSyncHolon implements the UnifiedWeaver pattern:
    - discover(): Find all plugin state paths
    - weave(): Commit state to git
    - heal(): Repair conflicts and corruption
    - emerge(): State coherence EMERGES from the healing process
    """

    def __init__(
        self,
        prakriti: "Prakriti",
        kernel: Optional[Any] = None,
        watcher_config: Optional[WatcherConfig] = None,
    ):
        """
        Initialize the StateSyncHolon.

        Args:
            prakriti: The Prakriti unified state engine
            kernel: Optional kernel reference for plugin access
            watcher_config: Optional configuration for file watching
        """
        self.prakriti = prakriti
        self.kernel = kernel
        self.watcher_config = watcher_config or WatcherConfig()

        # State tracking
        self._discovered: Dict[str, List[StatePathInfo]] = {}
        self._commit_queue: List[Path] = []
        self._change_timestamps: Dict[str, float] = {}

        # Watchdog
        self._watcher = None
        self._watcher_thread = None
        self._watcher_stop_event = threading.Event()

        logger.info("[SYNC_HOLON] Initialized")

    # =========================================================================
    # Discovery Methods
    # =========================================================================

    def discover_state_paths(self) -> Dict[str, List[StatePathInfo]]:
        """
        Auto-discover all plugin state paths.

        Three-pronged discovery strategy:
        1. PROTOCOL: Query plugins implementing PluginStateContract
        2. CONVENTION: Scan known locations (.opus_state/, .vibe/, etc.)
        3. MANIFEST: Read state_paths from manifest.json files

        Returns:
            {"plugin_name": [StatePathInfo(...), ...], ...}
        """
        paths: Dict[str, List[StatePathInfo]] = {}

        # === Method 1: Protocol Query ===
        if self.kernel and hasattr(self.kernel, "plugins"):
            for plugin in self.kernel.plugins:
                if isinstance(plugin, PluginStateContract):
                    plugin_paths = plugin.get_state_paths()
                    plugin_name = getattr(plugin, "name", type(plugin).__name__)
                    for p in plugin_paths:
                        info = self._analyze_path(p, plugin_name)
                        paths.setdefault(plugin_name, []).append(info)

        # === Method 2: Convention Scan ===
        workspace = self.prakriti.workspace
        conventions = [
            (".opus_state", "opus_assistant"),
            (".vibe/state", "task_manager"),
            (".vibe/state/vedic_dharma.json", "vedic_governance"),  # OPUS-009: Dharma State
            (".vibe/config", "system"),
            (".prakriti", "prakriti"),
        ]
        for dir_path, default_owner in conventions:
            path = workspace / dir_path
            if path.exists():
                owner = self._find_owner(path) or default_owner
                info = self._analyze_path(path, owner)
                # Avoid duplicates
                if owner not in paths or not any(i.path == path for i in paths.get(owner, [])):
                    paths.setdefault(owner, []).append(info)

        # Plugin-specific state directories
        plugin_base = workspace / "vibe_core" / "plugins"
        if plugin_base.exists():
            for plugin_dir in plugin_base.iterdir():
                if plugin_dir.is_dir():
                    state_dir = plugin_dir / "state"
                    if state_dir.exists():
                        info = self._analyze_path(state_dir, plugin_dir.name)
                        paths.setdefault(plugin_dir.name, []).append(info)

        # === Method 3: Manifest Declaration ===
        for manifest in workspace.glob("**/manifest.json"):
            try:
                data = json.loads(manifest.read_text())
                if "state_paths" in data:
                    plugin_name = data.get("name", manifest.parent.name)
                    for p in data["state_paths"]:
                        info = self._analyze_path(Path(p), plugin_name)
                        if plugin_name not in paths or not any(i.path == Path(p) for i in paths.get(plugin_name, [])):
                            paths.setdefault(plugin_name, []).append(info)
            except (json.JSONDecodeError, OSError):
                continue

        self._discovered = paths
        return paths

    def _analyze_path(self, path: Path, plugin: str) -> StatePathInfo:
        """Analyze a state path and return its info including Guna."""
        # Make path absolute if relative
        if not path.is_absolute():
            path = self.prakriti.workspace / path

        guna = self.diagnose_guna(path)
        is_ignored = self._is_ignored(path)

        content_hash = None
        last_modified = None
        if path.exists():
            try:
                last_modified = path.stat().st_mtime
                if path.is_file():
                    content_hash = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
            except (OSError, PermissionError):
                pass

        last_commit = self._get_last_commit(path)

        return StatePathInfo(
            path=path,
            plugin=plugin,
            guna=guna,
            last_commit=last_commit,
            last_modified=last_modified,
            is_ignored=is_ignored,
            content_hash=content_hash,
        )

    def _find_owner(self, path: Path) -> Optional[str]:
        """Find which plugin owns a state path."""
        if self.kernel and hasattr(self.kernel, "plugins"):
            for plugin in self.kernel.plugins:
                if isinstance(plugin, PluginStateContract):
                    try:
                        if path in plugin.get_state_paths():
                            return getattr(plugin, "name", type(plugin).__name__)
                    except Exception:
                        continue
        return None

    def _get_last_commit(self, path: Path) -> Optional[str]:
        """Get the last commit SHA that touched this path."""
        try:
            result = self.prakriti.git.log(str(path), n=1)
            if result and len(result) > 0:
                return result[0].sha if hasattr(result[0], "sha") else str(result[0])
            return None
        except Exception:
            return None

    # =========================================================================
    # Guna Diagnosis
    # =========================================================================

    def diagnose_guna(self, path: Path) -> StateGuna:
        """
        Diagnose the current Guna of a state path.

        TAMAS (dead): Missing, ignored, corrupt, stale (>7d)
        RAJAS (active): Dirty, uncommitted changes
        SATTVA (balanced): Clean, synced, recent

        This is the THREE MODES through which all state moves.
        """
        # Make path absolute if relative
        if not path.is_absolute():
            path = self.prakriti.workspace / path

        # Tamas: Path doesn't exist
        if not path.exists():
            return StateGuna.TAMAS

        # Tamas: Ignored by git
        if self._is_ignored(path):
            return StateGuna.TAMAS

        # Tamas: Corrupt (can't read)
        if not self._is_readable(path):
            return StateGuna.TAMAS

        # Tamas: Stale (>7 days since last touch)
        if self._is_stale(path, max_age_days=7):
            return StateGuna.TAMAS

        # Rajas: Has uncommitted changes
        if self._is_dirty(path):
            return StateGuna.RAJAS

        # Sattva: Clean and recent
        return StateGuna.SATTVA

    def _is_ignored(self, path: Path) -> bool:
        """Check if path is in .gitignore."""
        try:
            # Try git check-ignore
            if hasattr(self.prakriti.git, "check_ignore"):
                return self.prakriti.git.check_ignore(path)
        except Exception:
            pass

        # Fallback: manual check
        gitignore = self.prakriti.workspace / ".gitignore"
        if gitignore.exists():
            try:
                patterns = gitignore.read_text().splitlines()
                path_str = str(path.relative_to(self.prakriti.workspace))
                for pattern in patterns:
                    pattern = pattern.strip()
                    if pattern and not pattern.startswith("#"):
                        if pattern in path_str or path.match(pattern):
                            return True
            except (ValueError, OSError):
                pass
        return False

    def _is_readable(self, path: Path) -> bool:
        """Check if path can be read without errors."""
        try:
            if path.is_file():
                path.read_bytes()
            elif path.is_dir():
                list(path.iterdir())
            return True
        except Exception:
            return False

    def _is_stale(self, path: Path, max_age_days: int = 7) -> bool:
        """Check if path hasn't been touched in max_age_days."""
        try:
            mtime = path.stat().st_mtime
            age_days = (time.time() - mtime) / (60 * 60 * 24)
            return age_days > max_age_days
        except Exception:
            return True

    def _is_dirty(self, path: Path) -> bool:
        """Check if path has uncommitted changes."""
        try:
            if hasattr(self.prakriti.git, "is_path_dirty"):
                return self.prakriti.git.is_path_dirty(path)
            # Fallback: check git status
            return self.prakriti.git.is_dirty()
        except Exception:
            return False

    # =========================================================================
    # Enforcement (Lobotomy Prevention)
    # =========================================================================

    def ensure_tracked(self) -> List[str]:
        """
        Ensure all state paths are git-tracked (not ignored).

        This is the LOBOTOMY PREVENTION check.

        Raises:
            GovernanceViolation: If any state path is in .gitignore
        """
        violations = []

        for plugin, infos in self.discover_state_paths().items():
            for info in infos:
                if info.is_ignored:
                    violations.append(f"{plugin}: {info.path} is IGNORED (LOBOTOMY!)")

        if violations:
            # Log to ledger if available
            if hasattr(self.prakriti, "ledger") and hasattr(self.prakriti.ledger, "record_event"):
                self.prakriti.ledger.record_event(
                    "LOBOTOMY_DETECTED",
                    "StateSyncHolon",
                    {"violations": violations},
                )
            raise GovernanceViolation("State files in .gitignore = LOBOTOMY!\n" + "\n".join(violations))

        return list(self._discovered.keys())

    # =========================================================================
    # Healing (Tamas -> Rajas -> Sattva)
    # =========================================================================

    def heal_toward_sattva(self, path: Path) -> StateGuna:
        """
        Apply healing force to move state toward Sattva.

        Tamas -> Rajas: Resurrect, unignore, repair
        Rajas -> Sattva: Commit, sync, verify

        The StateSyncHolon's PRIMARY PURPOSE is to push state
        from Tamas -> Rajas -> Sattva.

        Returns:
            The new Guna after healing attempt
        """
        # Make path absolute if relative
        if not path.is_absolute():
            path = self.prakriti.workspace / path

        guna = self.diagnose_guna(path)

        if guna == StateGuna.TAMAS:
            # Resurrection sequence
            self._resurrect(path)
            return StateGuna.RAJAS  # Now active, needs commit

        elif guna == StateGuna.RAJAS:
            # Balancing sequence
            self._commit_and_sync(path)
            return StateGuna.SATTVA

        return StateGuna.SATTVA  # Already balanced

    def _resurrect(self, path: Path) -> None:
        """
        Resurrect a Tamas state path.

        Actions:
        1. If ignored: Remove from .gitignore
        2. If missing: Create from template or last known state
        3. If corrupt: Restore from backup or reset
        4. If stale: Touch and mark for review
        """
        # Remove from gitignore if present
        self._unignore(path)

        # Create if missing
        if not path.exists():
            self._create_from_template(path)

        # Attempt repair if corrupt
        if path.exists() and not self._is_readable(path):
            self._repair_corrupt(path)

        # Touch to mark as active
        if path.exists():
            path.touch()

        # Log resurrection
        if hasattr(self.prakriti, "ledger") and hasattr(self.prakriti.ledger, "record_event"):
            self.prakriti.ledger.record_event(
                "STATE_RESURRECTED",
                "StateSyncHolon",
                {"path": str(path)},
            )

        logger.info(f"[SYNC_HOLON] Resurrected: {path}")

    def _unignore(self, path: Path) -> None:
        """Remove a path from .gitignore."""
        gitignore = self.prakriti.workspace / ".gitignore"
        if not gitignore.exists():
            return

        try:
            lines = gitignore.read_text().splitlines()
            path_str = str(path.relative_to(self.prakriti.workspace))
        except (ValueError, OSError):
            return

        new_lines = []
        removed = False
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                if path_str in stripped or (stripped and path.match(stripped)):
                    removed = True
                    continue
            new_lines.append(line)

        if removed:
            gitignore.write_text("\n".join(new_lines) + "\n")
            if hasattr(self.prakriti, "ledger") and hasattr(self.prakriti.ledger, "record_event"):
                self.prakriti.ledger.record_event(
                    "GITIGNORE_HEALED",
                    "StateSyncHolon",
                    {"removed": path_str},
                )
            logger.info(f"[SYNC_HOLON] Removed from .gitignore: {path_str}")

    def _create_from_template(self, path: Path) -> None:
        """Create missing state from template."""
        if path.suffix == ".json":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}")
        elif path.suffix in (".yaml", ".yml"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Auto-created by StateSyncHolon\n")
        elif not path.suffix or path.is_dir() or str(path).endswith("/"):
            path.mkdir(parents=True, exist_ok=True)

    def _repair_corrupt(self, path: Path) -> None:
        """Attempt to repair corrupt state."""
        # Try to get from git history
        try:
            if hasattr(self.prakriti.git, "show"):
                relative_path = path.relative_to(self.prakriti.workspace)
                content = self.prakriti.git.show(f"HEAD:{relative_path}")
                if content:
                    path.write_bytes(content if isinstance(content, bytes) else content.encode())
                    return
        except Exception:
            pass

        # Last resort: reset to empty
        self._create_from_template(path)

    def _commit_and_sync(self, path: Path) -> None:
        """Commit dirty state and sync with ledger."""
        if self._is_dirty(path):
            try:
                self.prakriti.git.stage([str(path)])
                self.prakriti.commit_if_dirty(
                    message=f"state(sync): Auto-commit {path.name}",
                    commit_type="chore",
                    scope="state",
                )
            except Exception as e:
                logger.warning(f"[SYNC_HOLON] Failed to commit {path}: {e}")

    # =========================================================================
    # Lifecycle Hooks
    # =========================================================================

    def on_boot(self) -> Dict[str, List[StatePathInfo]]:
        """
        Boot-time state discovery and healing.

        Called by Prakriti during kernel boot.
        Implements: Discover -> Diagnose -> Heal Tamas
        """
        # Discover all state paths
        discovered = self.discover_state_paths()

        # Check for lobotomy (but don't crash, attempt healing)
        try:
            self.ensure_tracked()
        except GovernanceViolation as e:
            logger.warning(f"[SYNC_HOLON] Boot lobotomy warning: {e}")

        # Heal any Tamas states
        for plugin, infos in discovered.items():
            for info in infos:
                if info.guna == StateGuna.TAMAS:
                    self.heal_toward_sattva(info.path)

        # Start watcher if enabled
        if self.watcher_config.enabled:
            self.start_watcher()

        logger.info(f"[SYNC_HOLON] Boot complete: {len(discovered)} plugins with state")
        return discovered

    def on_shutdown(self, use_weaver: bool = True) -> None:
        """
        Shutdown-time state commit.

        OPUS-096: Now delegates to StateSyncWeaver for unified orchestration.
        Falls back to direct commit if Weaver is not available.

        Called by Prakriti during kernel shutdown.
        Implements: Stage all -> Commit -> Verify

        Args:
            use_weaver: If True (default), delegate to StateSyncWeaver
        """
        # Stop watcher if running
        self.stop_watcher()

        # OPUS-096: Try to use StateSyncWeaver for unified commit orchestration
        if use_weaver:
            try:
                weaver = ServiceRegistry.get(StateSyncWeaverProtocol)
                if weaver:
                    result = weaver.on_session_end()
                    if result.success:
                        logger.info(f"[SYNC_HOLON] Shutdown complete via Weaver: {result.message}")
                        return
                    else:
                        logger.warning(f"[SYNC_HOLON] Weaver failed: {result.error}, falling back")
                else:
                    logger.debug("[SYNC_HOLON] StateSyncWeaver not registered in DI, using direct commit")
            except Exception as e:
                logger.warning(f"[SYNC_HOLON] Weaver orchestration failed: {e}, using direct commit")

        # Fallback: Direct commit for each dirty path
        for plugin, infos in self._discovered.items():
            for info in infos:
                if self.diagnose_guna(info.path) == StateGuna.RAJAS:
                    self._commit_and_sync(info.path)

        if hasattr(self.prakriti, "ledger") and hasattr(self.prakriti.ledger, "record_event"):
            self.prakriti.ledger.record_event(
                "SHUTDOWN_STATE_SYNCED",
                "StateSyncHolon",
                {"plugins": list(self._discovered.keys())},
            )

        logger.info("[SYNC_HOLON] Shutdown complete (direct)")

    def on_conflict(self, path: Path, ours: bytes, theirs: bytes) -> bytes:
        """
        Handle merge conflict via healing.

        Called by Prakriti during git merge.
        Returns healed content that is ALWAYS valid.

        OPUS-106: Now uses UntotbarMergeEngine for intelligent conflict healing.
        """
        # Import merge engine if available
        try:
            from .merge_engine import UntotbarMergeEngine

            engine = UntotbarMergeEngine()
            healed_result = engine.heal_conflict(path, ours, theirs)

            if hasattr(self.prakriti, "ledger") and hasattr(self.prakriti.ledger, "record_event"):
                self.prakriti.ledger.record_event(
                    "CONFLICT_HEALED",
                    "StateSyncHolon",
                    {
                        "path": str(path),
                        "strategy": healed_result.strategy.value,
                        "conflicts_found": healed_result.conflicts_found,
                    },
                )

            logger.info(
                f"[SYNC_HOLON] Healed conflict: {path} "
                f"(strategy={healed_result.strategy.value}, conflicts={healed_result.conflicts_found})"
            )
            return healed_result.healed_content
        except ImportError:
            # Fallback: ours wins
            logger.warning(f"[SYNC_HOLON] MergeEngine not available, using ours for {path}")
            return ours

    # =========================================================================
    # Watchdog File Monitoring
    # =========================================================================

    def start_watcher(self) -> bool:
        """
        Start file system watcher for real-time state monitoring.

        Uses watchdog library if available, otherwise no-ops.
        The watcher detects changes and queues them for commit.

        Returns:
            True if watcher started, False otherwise
        """
        if self._watcher is not None:
            return True  # Already running

        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:
            logger.info("[SYNC_HOLON] watchdog not installed, watcher disabled")
            return False

        class StateChangeHandler(FileSystemEventHandler):
            def __init__(handler_self, holon: StateSyncHolon):
                handler_self.holon = holon

            def on_any_event(handler_self, event):
                if event.is_directory:
                    return
                # Check if this is a state path we care about
                path = Path(event.src_path)
                for pattern in handler_self.holon.watcher_config.ignore_patterns:
                    if path.match(pattern):
                        return
                for pattern in handler_self.holon.watcher_config.watch_patterns:
                    if path.match(pattern):
                        handler_self.holon._on_file_change(path)
                        break

        self._watcher_stop_event.clear()
        handler = StateChangeHandler(self)
        self._watcher = Observer()

        # Watch all discovered state directories
        watched_paths = set()
        for infos in self._discovered.values():
            for info in infos:
                watch_path = info.path if info.path.is_dir() else info.path.parent
                if watch_path.exists() and watch_path not in watched_paths:
                    self._watcher.schedule(handler, str(watch_path), recursive=True)
                    watched_paths.add(watch_path)

        self._watcher.start()
        logger.info(f"[SYNC_HOLON] Watcher started for {len(watched_paths)} directories")
        return True

    def stop_watcher(self) -> None:
        """Stop the file system watcher."""
        if self._watcher is not None:
            self._watcher_stop_event.set()
            self._watcher.stop()
            self._watcher.join(timeout=5)
            self._watcher = None
            logger.info("[SYNC_HOLON] Watcher stopped")

    def _on_file_change(self, path: Path) -> None:
        """
        Handle a file change event (debounced).

        This method is called by the watchdog handler.
        Changes are debounced to avoid excessive commits.
        """
        path_str = str(path)
        now = time.time()

        # Debounce: ignore if changed recently
        last_change = self._change_timestamps.get(path_str, 0)
        if now - last_change < self.watcher_config.debounce_seconds:
            return

        self._change_timestamps[path_str] = now

        # Queue for commit if not already queued
        if path not in self._commit_queue:
            self._commit_queue.append(path)
            logger.debug(f"[SYNC_HOLON] Queued for commit: {path}")

    def process_commit_queue(self) -> int:
        """
        Process queued file changes and commit.

        Returns:
            Number of files committed
        """
        if not self._commit_queue:
            return 0

        paths_to_commit = list(self._commit_queue)
        self._commit_queue.clear()

        committed = 0
        for path in paths_to_commit:
            if self._is_dirty(path):
                self._commit_and_sync(path)
                committed += 1

        if committed > 0:
            logger.info(f"[SYNC_HOLON] Committed {committed} queued changes")

        return committed

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_guna_summary(self) -> Dict[str, int]:
        """Get count of paths by Guna state."""
        summary = {g.value: 0 for g in StateGuna}
        for infos in self._discovered.values():
            for info in infos:
                summary[info.guna.value] += 1
        return summary

    def get_tamas_paths(self) -> List[StatePathInfo]:
        """Get all paths currently in Tamas state."""
        tamas_paths = []
        for infos in self._discovered.values():
            for info in infos:
                if info.guna == StateGuna.TAMAS:
                    tamas_paths.append(info)
        return tamas_paths

    def get_rajas_paths(self) -> List[StatePathInfo]:
        """Get all paths currently in Rajas state (need commit)."""
        rajas_paths = []
        for infos in self._discovered.values():
            for info in infos:
                if info.guna == StateGuna.RAJAS:
                    rajas_paths.append(info)
        return rajas_paths

    def get_status(self) -> Dict[str, Any]:
        """Get overall status of the StateSyncHolon."""
        return {
            "discovered_plugins": list(self._discovered.keys()),
            "total_paths": sum(len(infos) for infos in self._discovered.values()),
            "guna_summary": self.get_guna_summary(),
            "watcher_enabled": self.watcher_config.enabled,
            "watcher_running": self._watcher is not None,
            "commit_queue_size": len(self._commit_queue),
        }


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "StateSyncHolon",
    "StateGuna",
    "StatePathInfo",
    "PluginStateContract",
    "WatcherConfig",
    "GovernanceViolation",
]
