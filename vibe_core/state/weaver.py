"""
OPUS-096: State Sync Holon Weaver - Unified State Orchestration

The Weaver is the meta-orchestration layer for ALL state synchronization.
It unifies the previously independent commit mechanisms:

1. StateSyncHolon - Plugin state discovery & healing
2. GitTools.seal_history() - Chronicle cartridge commits
3. Prakriti.commit_if_dirty() - Core state engine commits
4. Heartbeat._chronicle_commit() - Scheduled runtime state commits
5. ManasOracle - Cognitive layer wisdom interface

The Weaver Pattern:
    DISCOVER → CLASSIFY → DECIDE → EXECUTE

Design Philosophy:
    "The Weaver doesn't create the threads - it reveals the fabric that was always there."
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import (
    PrakritiProtocol,
    StateServiceProtocol,
    StateSyncHolonProtocol,
    StateSyncWeaverProtocol,
)
from vibe_core.state.schema import CommitResult

from .runtime_state import RuntimeStateDefinition, get_runtime_state_definition

if TYPE_CHECKING:
    from .guna_classifier import StateGuna


class CommitStrategy(str, Enum):
    """Commit decision strategies."""

    IMMEDIATE = "immediate"  # Commit now (session boundary)
    DEFERRED = "deferred"  # Queue for heartbeat
    BATCHED = "batched"  # Combine with other commits
    SKIP = "skip"  # No action needed


class WeaverMode(str, Enum):
    """Two-mode operation per OPUS-096."""

    REFLEX = "reflex"  # Fast, rule-based (< 10ms)
    ORACLE = "oracle"  # Slow, cognitive (100-500ms)


@dataclass
class StatePathInfo:
    """Info about a single state path."""

    path: Path
    plugin: str
    guna: str  # "SATTVA", "RAJAS", "TAMAS"
    layer: str  # "VIBE" or "PLUGIN"
    sensitivity: str = "PUBLIC"  # PUBLIC, PRIVATE, CONFIDENTIAL
    volatility: str = "PERSISTENT"  # EPHEMERAL, PERSISTENT, IMMUTABLE


@dataclass
class WeaverStateMap:
    """Unified state discovery result."""

    plugin_states: Dict[str, List[StatePathInfo]] = field(default_factory=dict)
    runtime_files: List[str] = field(default_factory=list)
    session_state: Dict[str, Any] = field(default_factory=dict)
    cognitive_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassifiedState:
    """State after Guna classification."""

    sattva: List[StatePathInfo] = field(default_factory=list)  # Clean/synced
    rajas: List[StatePathInfo] = field(default_factory=list)  # Dirty/active
    tamas: List[StatePathInfo] = field(default_factory=list)  # Stale/broken


@dataclass
class WeavingAdvice:
    """Advice from MANAS Oracle (or rules-based fallback)."""

    priority_paths: List[Path] = field(default_factory=list)  # Commit these first
    patterns: List[str] = field(default_factory=list)  # Observed patterns
    healing_suggestions: List[str] = field(default_factory=list)
    mode: WeaverMode = WeaverMode.REFLEX


@dataclass
class CommitPlan:
    """The decision of what/how to commit."""

    paths: List[Path]
    strategy: CommitStrategy
    message: str
    no_verify: bool = True  # Runtime state skips hooks
    sign: bool = False  # GPG signing


class StateSyncWeaver(StateSyncWeaverProtocol):
    """
    Meta-orchestration layer for unified state synchronization.

    Implements the Weaver Pattern:
        DISCOVER → CLASSIFY → DECIDE → EXECUTE

    Usage:
        weaver = StateSyncWeaver(prakriti)

        # Heartbeat integration
        result = weaver.pulse()

        # Session end integration
        result = weaver.on_session_end()

    Thread Safety:
        Single commit authority via _commit_lock.
        All commits go through this lock to prevent index.lock crashes.
    """

    # Single commit authority lock
    _commit_lock: ClassVar[Lock] = Lock()

    def __init__(
        self,
        prakriti: Optional[PrakritiProtocol] = None,
        sync_holon: Optional[StateSyncHolonProtocol] = None,
    ):
        """
        Initialize the Weaver.

        Args:
            prakriti: Optional prakriti engine (if None, fetched from DI)
            sync_holon: Optional sync holon (if None, fetched from DI)
        """
        self._prakriti_override = prakriti
        self._sync_holon_override = sync_holon
        self.workspace = Path(".")  # Will be updated during first pulse if needed
        self._runtime_definition = None

    @property
    def prakriti(self) -> Optional[PrakritiProtocol]:
        """Fetch Prakriti from registry (or override)."""
        return self._prakriti_override or ServiceRegistry.get(PrakritiProtocol)

    @property
    def sync_holon(self) -> Optional[StateSyncHolonProtocol]:
        """Fetch StateSyncHolon from registry (or override)."""
        return self._sync_holon_override or ServiceRegistry.get(StateSyncHolonProtocol)

    def _ensure_initialized(self) -> bool:
        """Ensure workspace-dependent state is initialized."""
        if self._runtime_definition:
            return True

        prakriti = self.prakriti
        if not prakriti:
            return False

        if hasattr(prakriti, "_workspace"):
            self.workspace = prakriti._workspace
        elif hasattr(prakriti, "workspace"):
            self.workspace = prakriti.workspace

        self._runtime_definition = get_runtime_state_definition(self.workspace)
        return True

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def pulse(self) -> CommitResult:
        """
        Run one weave cycle.
        (Sovereign Intelligence Mode)

        OPUS-211 FIX: Uses REFLEX mode only (no oracle consultation).
        Oracle consultation was causing a feedback loop:
        - Weaver calls ManasOracle
        - MANAS updates manas_awareness.json
        - StateService marks file dirty
        - Triggers another commit
        - Infinite loop!

        State commits should be dumb batches. Oracle is for significant events only.
        """
        import os

        if os.environ.get("VIBE_NO_GIT_COMMIT") == "1":
            return CommitResult(git_sha="0000000", message="Git disabled (Shunyata)", success=True)

        if not self._ensure_initialized():
            return CommitResult(success=False, error="StateSyncWeaver: Dependencies (Prakriti) not ready", message="Dependency error")

        with self._commit_lock:
            # 1. Discover
            state_map = self._discover_all_state()

            # 2. Classify
            classified = self._classify_state(state_map)

            # 3. REFLEX mode - no oracle consultation for routine commits
            advice = WeavingAdvice(mode=WeaverMode.REFLEX)

            # 4. Decide
            plan = self._decide_commit_strategy(classified, advice)

            # 5. Execute if needed
            if plan.strategy == CommitStrategy.SKIP:
                return CommitResult(success=True, message="Nothing to commit")

            return self._execute_commit(plan)

    def on_session_end(self) -> CommitResult:
        """
        Session boundary integration - Called when session ends.
        """
        if not self._ensure_initialized():
            return CommitResult(success=False, error="StateSyncWeaver: Dependencies not ready", message="Dependency error")

        with self._commit_lock:
            state_map = self._discover_all_state()
            classified = self._classify_state(state_map)

            # Session end always uses Oracle if possible
            advice = self._consult_oracle(classified)
            plan = self._decide_commit_strategy(classified, advice)

            # Force IMMEDIATE for session end
            if plan.strategy != CommitStrategy.SKIP:
                plan.strategy = CommitStrategy.IMMEDIATE

            result = self._execute_commit(plan)
            return result

    def weave(self) -> CommitResult:
        """
        Full weaving cycle with cognitive intelligence.
        """
        if not self._ensure_initialized():
            return CommitResult(success=False, error="StateSyncWeaver: Dependencies not ready", message="Dependency error")

        with self._commit_lock:
            state_map = self._discover_all_state()
            classified = self._classify_state(state_map)
            advice = self._consult_oracle(classified)
            plan = self._decide_commit_strategy(classified, advice)

            if plan.strategy == CommitStrategy.SKIP:
                return CommitResult(success=True, message="Nothing to commit")

            result = self._execute_commit(plan)
            return result

    # =========================================================================
    # INTERNAL METHODS (The Weaver Pattern)
    # =========================================================================

    def _consult_oracle(self, classified: ClassifiedState) -> WeavingAdvice:
        """
        Phase 3: CONSULT - Optionally consult MANAS for intelligent commit decisions.

        The Weaver (Mahat) asks MANAS (Mind) for advice.
        If MANAS is sleeping or unavailable, Weaver falls back to REFLEX mode.
        """
        try:
            # Lazy import to avoid circular dependency
            from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

            # Context for the oracle
            context = {
                "task_title": "State Synchronization",
                "task_type": "state_commit",
                "risk_level": "low",  # State sync is generally low risk
                "changes": [str(p.path) for p in classified.rajas],
                "is_automated": True,
                "user_approval": False,
                "classified_state": {
                    "sattva": len(classified.sattva),
                    "rajas": len(classified.rajas),
                    "tamas": len(classified.tamas),
                },
            }

            oracle = ManasOracle()
            analysis = oracle.consult(context)

            mode = WeaverMode.ORACLE
            priority_paths = []

            # If MANAS suggests high caution, maybe we defer?
            # For now, we trust the Oracle's safety score.
            # If very unsafe (< 0.4), we might want to skip/defer.

            return WeavingAdvice(
                mode=mode,
                priority_paths=priority_paths,
                # Simple mapping for now
                healing_suggestions=analysis.precautions,
            )

        except ImportError:
            # MANAS not installed - standard reflex mode
            return WeavingAdvice(mode=WeaverMode.REFLEX)
        except Exception as e:
            # MANAS failed - don't block the state machine
            # logger.warning(f"Weaver oracle consultation failed: {e}")
            return WeavingAdvice(mode=WeaverMode.REFLEX)

    def _discover_all_state(self) -> WeaverStateMap:
        """
        Phase 1: DISCOVER - What exists?

        Unified discovery across all sources:
        - StateSyncHolon discovered plugins
        - RuntimeStateDefinition patterns
        """
        state_map = WeaverStateMap()

        # 1. Plugin states from SyncHolon
        if self.sync_holon and hasattr(self.sync_holon, "_discovered"):
            for plugin, infos in self.sync_holon._discovered.items():
                state_map.plugin_states[plugin] = [
                    StatePathInfo(
                        path=info.path,
                        plugin=plugin,
                        guna="UNKNOWN",
                        layer="PLUGIN",
                    )
                    for info in infos
                ]

        # 2. Runtime files - OPUS-206 FIX: Use git as source of truth!
        # The previous "Trust StateService" approach was BROKEN because many
        # systems write directly to disk without going through StateService.
        # Git is the ONLY reliable way to know what's actually changed.
        state_map.runtime_files = self._discover_dirty_from_git()

        # 3. Session state
        if hasattr(self.prakriti, "session") and self.prakriti.session:
            state_map.session_state = {
                "id": self.prakriti.session.session_id,
                "start_time": str(self.prakriti.session.start_time),
            }

        # 4. P0: StateService dirty files (Direct Push model)
        try:
            state_service = ServiceRegistry.get(StateServiceProtocol)
            if state_service:
                dirty_files = state_service.get_dirty_files()
                for path in dirty_files:
                    # Add to runtime_files if not already tracked
                    try:
                        rel_path = str(path.relative_to(self.workspace))
                        if rel_path not in state_map.runtime_files:
                            state_map.runtime_files.append(rel_path)
                    except ValueError:
                        continue
        except Exception:
            pass  # StateService not initialized yet

        return state_map

    def _classify_state(self, state_map: WeaverStateMap) -> ClassifiedState:
        """
        Phase 2: CLASSIFY - What is it?

        Classify by Guna:
        - Sattva: Clean, synced
        - Rajas: Dirty, active
        - Tamas: Stale, broken
        """
        classified = ClassifiedState()

        # Classify plugin states
        for plugin, infos in state_map.plugin_states.items():
            for info in infos:
                if self.sync_holon and hasattr(self.sync_holon, "diagnose_guna"):
                    guna = self.sync_holon.diagnose_guna(info.path)
                    info.guna = guna.name if hasattr(guna, "name") else str(guna)

                    if info.guna == "SATTVA":
                        classified.sattva.append(info)
                    elif info.guna == "RAJAS":
                        classified.rajas.append(info)
                    else:
                        classified.tamas.append(info)
                else:
                    # Default: assume dirty
                    info.guna = "RAJAS"
                    classified.rajas.append(info)

        # Runtime files are dirty by definition
        for file_path in state_map.runtime_files:
            info = StatePathInfo(
                path=Path(file_path),
                plugin="runtime",
                guna="RAJAS",
                layer="VIBE",
            )
            classified.rajas.append(info)

        return classified

    def _decide_commit_strategy(self, classified: ClassifiedState, advice: WeavingAdvice) -> CommitPlan:
        """
        Phase 4: DECIDE - What to do?

        Decide the commit strategy based on classified state and advice.
        """
        if not classified.rajas:
            return CommitPlan(
                paths=[],
                strategy=CommitStrategy.SKIP,
                message="Nothing to commit",
            )

        paths = advice.priority_paths or [info.path for info in classified.rajas]

        return CommitPlan(
            paths=paths,
            strategy=CommitStrategy.IMMEDIATE,
            message="chore(state): Auto-sync runtime state",
            no_verify=True,  # Runtime state skips hooks
        )

    def _execute_commit(self, plan: CommitPlan) -> CommitResult:
        """
        Phase 5: EXECUTE - Do it! (Sovereign Mode)
        """
        if plan.strategy == CommitStrategy.SKIP:
            return CommitResult(success=True, message="Skipped")

        try:
            # Stage and commit via Prakriti
            if hasattr(self.prakriti, "commit_if_dirty"):
                runtime_patterns = [str(p) for p in plan.paths] if plan.paths else []

                if not runtime_patterns:
                    return CommitResult(success=True, message="No runtime files to commit")

                result = self.prakriti.commit_if_dirty(
                    message=plan.message.split(":", 1)[-1].strip() if ":" in plan.message else plan.message,
                    commit_type="chore",
                    scope="state",
                    stage_patterns=runtime_patterns,  # Only stage specific runtime files
                )

                if result:
                    # P0: Clear StateService dirty flags after successful commit
                    try:
                        state_service = ServiceRegistry.get(StateServiceProtocol)
                        if state_service:
                            state_service.clear_dirty_flags()
                    except Exception:
                        pass

                    return CommitResult(
                        success=True,
                        git_sha=result.git_sha if hasattr(result, "git_sha") else None,
                        files_committed=[str(p) for p in plan.paths],
                    )
                else:
                    return CommitResult(
                        success=True,
                        message="Nothing to commit (clean)",
                    )
            else:
                return CommitResult(
                    success=False,
                    error="Prakriti.commit_if_dirty not available",
                )

        except Exception as e:
            return CommitResult(
                success=False,
                error=str(e),
            )

    def _discover_dirty_from_git(self) -> List[str]:
        """
        OPUS-206 FIX: Discover dirty state files directly from git.

        This is the ONLY reliable way to find ALL dirty files because:
        1. StateService._dirty_files only tracks files that go through save()
        2. Many systems write directly to disk (Prakriti.session.lock, etc.)
        3. Git is the single source of truth for what's actually changed

        Returns:
            List of relative paths to dirty state files
        """
        import subprocess

        try:
            # Get all modified and untracked files from git
            result = subprocess.run(
                ["git", "status", "--porcelain", "-uall"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5,  # Fast timeout - don't block
            )

            if result.returncode != 0:
                return []

            dirty_files = []
            for line in result.stdout.splitlines():
                if not line or len(line) < 3:
                    continue

                # Parse porcelain format: "XY filename" or "XY orig -> dest"
                # Status is line[:2] but we only need the filepath for now
                filepath = line[3:].split(" -> ")[-1].strip()

                # Only include state-related paths
                if self._is_state_path(filepath):
                    dirty_files.append(filepath)

            return dirty_files

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            # Git failed - fall back to empty (StateService tracking only)
            return []

    def _is_state_path(self, path: str) -> bool:
        """
        Check if a path is a state file (not source code).

        Uses RuntimeStateDefinition patterns + hardcoded state directories.
        """
        # Fast check: known state directories
        state_prefixes = (
            ".opus_state/",
            ".vibe/state/",
            ".vibe/config/",
            ".prakriti/",
            "data/vibe_",  # Ledger files
        )

        if any(path.startswith(prefix) for prefix in state_prefixes):
            return True

        # Check via RuntimeStateDefinition for plugin-specific patterns
        if self._runtime_definition and self._runtime_definition.is_runtime_state(path):
            return True

        return False


# =========================================================================
# SINGLETON ACCESS
# =========================================================================

_global_weaver: Optional[StateSyncWeaver] = None


def get_state_sync_weaver(
    prakriti: Optional[PrakritiProtocol] = None,
    sync_holon: Optional[StateSyncHolonProtocol] = None,
) -> Optional[StateSyncWeaver]:
    """Get the global StateSyncWeaver singleton."""
    global _global_weaver

    if _global_weaver is None:
        _global_weaver = StateSyncWeaver(prakriti, sync_holon)

        # Register in DI for protocol-based discovery
        ServiceRegistry.register(StateSyncWeaverProtocol, _global_weaver)

    return _global_weaver


def reset_state_sync_weaver() -> None:
    """Reset the global singleton (mainly for testing)."""
    global _global_weaver
    _global_weaver = None
