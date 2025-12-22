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

from .runtime_state import RuntimeStateDefinition, get_runtime_state_definition
from .state_service import get_state_service

if TYPE_CHECKING:
    from .guna_classifier import StateGuna
    from .prakriti import Prakriti
    from .sync_holon import StateSyncHolon


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


@dataclass
class CommitResult:
    """Result of commit execution."""

    success: bool
    sha: Optional[str] = None
    message: str = ""
    paths_committed: List[Path] = field(default_factory=list)
    error: Optional[str] = None


class StateSyncWeaver:
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
        prakriti: "Prakriti",
        sync_holon: Optional["StateSyncHolon"] = None,
        manas_oracle: Optional[Any] = None,
    ):
        """
        Initialize the Weaver.

        Args:
            prakriti: The core state engine
            sync_holon: Plugin state discovery (optional, uses prakriti's if not provided)
            manas_oracle: MANAS cognitive interface (Oracle API)
        """
        self.prakriti = prakriti
        self.sync_holon = sync_holon or getattr(prakriti, "sync_holon", None)
        self.manas_oracle = manas_oracle
        self.workspace = prakriti._workspace if hasattr(prakriti, "_workspace") else Path(".")
        self._runtime_definition = get_runtime_state_definition(self.workspace)

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def pulse(self) -> CommitResult:
        """
        Run one weave cycle.
        (Sovereign Intelligence Mode)
        """
        import os
        if os.environ.get("VIBE_NO_GIT_COMMIT") == "1":
            return CommitResult(git_sha="0000000", message="Git disabled (Shunyata)", success=True)

        with self._commit_lock:
            # 1. Discover
            state_map = self._discover_all_state()

            # 2. Classify
            classified = self._classify_state(state_map)

            # 3. Consult Oracle (Non-blocking)
            advice = self._consult_oracle(classified)

            # 4. Decide (incorporating Oracle advice if safe)
            plan = self._decide_commit_strategy(classified, advice)

            # 5. Execute if needed
            if plan.strategy == CommitStrategy.SKIP:
                return CommitResult(success=True, message="Nothing to commit")

            return self._execute_commit(plan)

    def on_session_end(self) -> CommitResult:
        """
        Session boundary integration - Called when session ends.
        """
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
        Phase 3: CONSULT - Non-blocking intelligence ingestion.
        """
        advice = WeavingAdvice(mode=WeaverMode.REFLEX)

        if not self.manas_oracle:
            return advice

        try:
            # Use non-blocking consult from MANAS Oracle API
            oracle_context = {
                "task_title": "State Persistence Pulse",
                "task_type": "maintenance",
                "risk_level": "low",
                "changes": [str(info.path) for info in classified.rajas],
                "is_automated": True,
            }

            # Oracle consult is fast/cached by design (see docs/MANAS_ORACLE_API.md)
            result = self.manas_oracle.consult(oracle_context)

            advice.mode = WeaverMode.ORACLE
            advice.patterns.append(f"Oracle advice: {result.advice}")
            if hasattr(result, "priority_paths"):
                advice.priority_paths = result.priority_paths

        except Exception as e:
            # Oracle failure never blocks the State
            advice.patterns.append(f"Oracle silent: {e}")

        return advice

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

        # 2. Runtime files (REMOVED: Slow git scanning)
        # OPUS-204: Trust StateService.mark_dirty() instead of calling git diff on every pulse
        state_map.runtime_files = []

        # 3. Session state
        if hasattr(self.prakriti, "session") and self.prakriti.session:
            state_map.session_state = {
                "id": self.prakriti.session.session_id,
                "start_time": str(self.prakriti.session.start_time),
            }

        # 4. P0: StateService dirty files (Direct Push model)
        try:
            state_service = get_state_service(self.workspace)
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
                        state_service = get_state_service(self.workspace)
                        state_service.clear_dirty_flags()
                    except Exception:
                        pass

                    return CommitResult(
                        success=True,
                        sha=result.git_sha if hasattr(result, "git_sha") else None,
                        message=plan.message,
                        paths_committed=plan.paths,
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


# =========================================================================
# SINGLETON ACCESS
# =========================================================================

_global_weaver: Optional[StateSyncWeaver] = None


def get_state_sync_weaver(prakriti: Optional["Prakriti"] = None) -> Optional[StateSyncWeaver]:
    """Get the global StateSyncWeaver singleton."""
    global _global_weaver

    if _global_weaver is None and prakriti is not None:
        _global_weaver = StateSyncWeaver(prakriti)

    return _global_weaver


def reset_state_sync_weaver() -> None:
    """Reset the global singleton (mainly for testing)."""
    global _global_weaver
    _global_weaver = None
