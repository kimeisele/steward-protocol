"""
OPUS-210: CommitAuthority - Single Point of Commit Execution

All commits in Steward Protocol flow through here.

Architecture:
    INTENT → WEAVER (orchestration) → COMMIT_AUTHORITY (execution) → GIT

The Weaver ORCHESTRATES (6 phases: DISCOVER → CLASSIFY → CONSULT → DECIDE → EXECUTE → LEARN)
CommitAuthority EXECUTES with:
    - UntotbarMergeEngine for conflict healing
    - panic_dump for irrecoverable failures (lost+found)
    - Resonance caching for performance
    - MANAS timeout handling (reflex fallback)

Design Constraints:
    1. State works WITHOUT MANAS (reflex mode)
    2. UntotbarMergeEngine "never fails" but we have panic_dump just in case
    3. No circular dependencies
    4. Thread-safe via single lock

<!-- @HARNESS
files:
  - path: vibe_core/state/commit_authority.py
    required: true
    rationale: "Single commit execution point for OPUS-210"

wiring:
  - pattern: "class CommitAuthority"
    in: vibe_core/state/commit_authority.py
  - pattern: "def panic_dump"
    in: vibe_core/state/commit_authority.py
  - pattern: "class ResonanceCache"
    in: vibe_core/state/commit_authority.py

tests:
  - tests/test_opus210_commit_authority.py
-->
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .git_state import GitCommit
    from .merge_engine import HealedConflict, UntotbarMergeEngine
    from .weaver import ClassifiedState, CommitPlan, StateSyncWeaver

logger = logging.getLogger("COMMIT_AUTHORITY")


# =============================================================================
# Enums and Data Classes
# =============================================================================


class OracleDecision(str, Enum):
    """Decision from MANAS oracle (or reflex fallback)."""

    REFLEX = "reflex"  # No cognition, automatic commit
    COMMIT_NOW = "commit_now"  # MANAS advises immediate commit
    DEFER = "defer"  # MANAS advises waiting
    HEAL_FIRST = "heal_first"  # MANAS sees TAMAS, heal before commit


class CommitOutcome(str, Enum):
    """Outcome of commit attempt."""

    SUCCESS = "success"
    SKIPPED = "skipped"  # Nothing to commit
    DEFERRED = "deferred"  # Oracle advised deferral
    HEALED = "healed"  # Conflicts healed, then committed
    PANIC_DUMPED = "panic_dumped"  # Irrecoverable, dumped to lost+found


@dataclass
class CommitResult:
    """Result of commit execution."""

    outcome: CommitOutcome
    sha: Optional[str] = None
    message: str = ""
    paths_committed: List[Path] = field(default_factory=list)
    healed_conflicts: List[str] = field(default_factory=list)
    panic_dump_path: Optional[Path] = None
    duration_ms: float = 0.0
    oracle_decision: OracleDecision = OracleDecision.REFLEX

    @property
    def success(self) -> bool:
        """Was commit successful (including healed)?"""
        return self.outcome in (CommitOutcome.SUCCESS, CommitOutcome.HEALED, CommitOutcome.SKIPPED)


@dataclass
class ResonanceResult:
    """Cached resonance computation result."""

    intent_signature: str
    state_signature: str
    resonance: float
    computed_at: float
    ttl_seconds: float = 60.0

    def is_valid(self) -> bool:
        """Check if cache entry is still valid."""
        return (time.time() - self.computed_at) < self.ttl_seconds


# =============================================================================
# Resonance Cache (Performance Optimization)
# =============================================================================


class ResonanceCache:
    """
    Caches resonance computations to avoid per-commit overhead.

    Resonance between intent and state changes slowly,
    so we cache for 60 seconds by default.
    """

    def __init__(self, ttl_seconds: float = 60.0):
        self._cache: Dict[str, ResonanceResult] = {}
        self._ttl = ttl_seconds
        self._lock = threading.Lock()

    def get(self, intent_sig: str, state_sig: str) -> Optional[float]:
        """Get cached resonance if valid."""
        key = f"{intent_sig}:{state_sig}"
        with self._lock:
            if key in self._cache and self._cache[key].is_valid():
                return self._cache[key].resonance
        return None

    def set(self, intent_sig: str, state_sig: str, resonance: float) -> None:
        """Cache resonance result."""
        key = f"{intent_sig}:{state_sig}"
        with self._lock:
            self._cache[key] = ResonanceResult(
                intent_signature=intent_sig,
                state_signature=state_sig,
                resonance=resonance,
                computed_at=time.time(),
                ttl_seconds=self._ttl,
            )

    def clear(self) -> int:
        """Clear all cached entries. Returns count cleared."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def prune_expired(self) -> int:
        """Remove expired entries. Returns count pruned."""
        with self._lock:
            before = len(self._cache)
            self._cache = {k: v for k, v in self._cache.items() if v.is_valid()}
            return before - len(self._cache)


# =============================================================================
# CommitAuthority - The Single Point of Commit Execution
# =============================================================================


class CommitAuthority:
    """
    The SINGLE authority for all Git commits in Steward Protocol.

    Weaver ORCHESTRATES (6 phases).
    CommitAuthority EXECUTES.
    UntotbarMergeEngine HEALS conflicts.
    panic_dump saves data on irrecoverable failure.

    Thread Safety:
        Single _commit_lock prevents concurrent commits.
        Resonance cache has its own lock.

    MANAS Integration:
        _consult_oracle() returns REFLEX if MANAS is:
        - Not installed
        - Disabled
        - Timed out

        The system ALWAYS works without cognition.
    """

    # Class-level commit lock (shared across instances)
    _commit_lock = threading.Lock()

    # Oracle timeout (ms) - if MANAS takes longer, fall back to REFLEX
    ORACLE_TIMEOUT_MS = 500

    # Lost+found directory for panic dumps
    LOST_FOUND_DIR = ".vibe/lost+found"

    def __init__(
        self,
        workspace: Optional[Path] = None,
        oracle_timeout_ms: Optional[int] = None,
    ):
        """
        Initialize CommitAuthority.

        Args:
            workspace: Workspace root (default: cwd)
            oracle_timeout_ms: MANAS timeout in ms (default: 500)
        """
        self._workspace = workspace or Path.cwd()
        self._oracle_timeout = oracle_timeout_ms or self.ORACLE_TIMEOUT_MS
        self._resonance_cache = ResonanceCache()

        # Lazy-loaded components
        self._weaver: Optional[StateSyncWeaver] = None
        self._merge_engine: Optional[UntotbarMergeEngine] = None
        self._git_state = None

        logger.info(f"[COMMIT_AUTHORITY] Initialized (timeout: {self._oracle_timeout}ms)")

    # =========================================================================
    # Lazy Component Loading
    # =========================================================================

    def _get_weaver(self) -> Optional[StateSyncWeaver]:
        """Get or create Weaver instance."""
        if self._weaver is None:
            try:
                from .weaver import get_state_sync_weaver

                self._weaver = get_state_sync_weaver()
            except ImportError:
                logger.warning("[COMMIT_AUTHORITY] Weaver not available")
        return self._weaver

    def _get_merge_engine(self) -> UntotbarMergeEngine:
        """Get or create UntotbarMergeEngine instance."""
        if self._merge_engine is None:
            from .merge_engine import UntotbarMergeEngine

            self._merge_engine = UntotbarMergeEngine()
        return self._merge_engine

    def _get_git_state(self):
        """Get or create GitState instance."""
        if self._git_state is None:
            from .git_state import GitState

            self._git_state = GitState(self._workspace)
        return self._git_state

    # =========================================================================
    # Main API
    # =========================================================================

    def commit(
        self,
        paths: Optional[List[Path]] = None,
        message: str = "chore(state): Auto-sync",
        intent_context: Optional[Dict[str, Any]] = None,
    ) -> CommitResult:
        """
        Execute a commit through the Weaver pipeline.

        1. Weaver.discover() - Find all dirty state
        2. Weaver.classify() - Tri-Guna classification
        3. _consult_oracle() - Ask MANAS (optional, with timeout)
        4. Weaver.decide() - COMMIT/DEFER/HEAL
        5. Execute via Git (with UntotbarMergeEngine)
        6. Weaver.learn() - Update patterns

        Args:
            paths: Specific paths to commit (None = all dirty)
            message: Commit message
            intent_context: Optional context for oracle

        Returns:
            CommitResult with outcome, sha, paths committed
        """
        start_time = time.time()

        with self._commit_lock:
            try:
                # Check if we have anything to commit
                git = self._get_git_state()
                if not git.is_dirty():
                    return CommitResult(
                        outcome=CommitOutcome.SKIPPED,
                        message="Nothing to commit",
                        duration_ms=(time.time() - start_time) * 1000,
                    )

                # Phase 1-3: Consult oracle (with timeout)
                oracle_decision = self._consult_oracle_with_timeout(intent_context)

                # Phase 4: Decide based on oracle
                if oracle_decision == OracleDecision.DEFER:
                    return CommitResult(
                        outcome=CommitOutcome.DEFERRED,
                        message="Oracle advised deferral",
                        oracle_decision=oracle_decision,
                        duration_ms=(time.time() - start_time) * 1000,
                    )

                # Phase 5: Heal if needed
                healed = []
                if oracle_decision == OracleDecision.HEAL_FIRST:
                    healed = self._heal_conflicts(paths)

                # Execute commit
                result = self._execute_commit(paths, message)

                return CommitResult(
                    outcome=CommitOutcome.HEALED if healed else CommitOutcome.SUCCESS,
                    sha=result.sha if result else None,
                    message=message,
                    paths_committed=paths or [],
                    healed_conflicts=healed,
                    oracle_decision=oracle_decision,
                    duration_ms=(time.time() - start_time) * 1000,
                )

            except Exception as e:
                logger.error(f"[COMMIT_AUTHORITY] Commit failed: {e}")

                # PANIC DUMP - save data to lost+found
                dump_path = self._panic_dump(paths, message, intent_context, str(e))

                return CommitResult(
                    outcome=CommitOutcome.PANIC_DUMPED,
                    message=f"Commit failed, data saved to {dump_path}",
                    panic_dump_path=dump_path,
                    duration_ms=(time.time() - start_time) * 1000,
                )

    # =========================================================================
    # Oracle Consultation (with Timeout)
    # =========================================================================

    def _consult_oracle_with_timeout(
        self,
        context: Optional[Dict[str, Any]] = None,
    ) -> OracleDecision:
        """
        Consult MANAS with timeout fallback to REFLEX.

        If MANAS is:
        - Not installed → REFLEX
        - Disabled → REFLEX
        - Times out → REFLEX

        The system ALWAYS works without cognition.
        """
        import concurrent.futures

        def _do_consult() -> OracleDecision:
            return self._consult_manas(context)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_do_consult)
                return future.result(timeout=self._oracle_timeout / 1000.0)

        except concurrent.futures.TimeoutError:
            logger.warning(f"[COMMIT_AUTHORITY] Oracle timed out ({self._oracle_timeout}ms), using REFLEX")
            return OracleDecision.REFLEX

        except Exception as e:
            logger.warning(f"[COMMIT_AUTHORITY] Oracle failed ({e}), using REFLEX")
            return OracleDecision.REFLEX

    def _consult_manas(self, context: Optional[Dict[str, Any]] = None) -> OracleDecision:
        """
        Consult MANAS via PrakritiSense for intelligent commit decisions.

        OPUS-210: Uses PrakritiSense (the 6th Jnanendriya) to perceive
        system state health and advise on commit strategy.

        Decision Logic:
            - TAMAS dominant → HEAL_FIRST (heal before commit)
            - RAJAS dominant → COMMIT_NOW (active state, commit it)
            - SATTVA dominant → REFLEX (already healthy, no urgency)

        Returns REFLEX if MANAS/PrakritiSense not available.
        """
        try:
            # Late import to avoid circular dependency
            from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import (
                PrakritiSense,
            )

            # Create PrakritiSense for this workspace
            sense = PrakritiSense(workspace=self._workspace)

            # Perceive current state health
            summary = sense.perceive_state()

            logger.debug(
                f"[COMMIT_AUTHORITY] PrakritiSense: "
                f"Sattva={summary.sattva_count}, Rajas={summary.rajas_count}, Tamas={summary.tamas_count}"
            )

            # Decision based on dominant Guna
            if summary.tamas_count > 0:
                # Tamas detected - heal first before committing
                logger.info(f"[COMMIT_AUTHORITY] MANAS advises: HEAL_FIRST ({summary.tamas_count} Tamas paths)")
                return OracleDecision.HEAL_FIRST

            elif summary.rajas_count > summary.sattva_count:
                # More active than balanced - commit now
                logger.info(f"[COMMIT_AUTHORITY] MANAS advises: COMMIT_NOW ({summary.rajas_count} Rajas paths)")
                return OracleDecision.COMMIT_NOW

            else:
                # Sattva dominant or equal - no urgency, reflex mode
                logger.debug("[COMMIT_AUTHORITY] MANAS advises: REFLEX (state healthy)")
                return OracleDecision.REFLEX

        except ImportError:
            # MANAS/PrakritiSense not installed
            logger.debug("[COMMIT_AUTHORITY] PrakritiSense not available, using REFLEX")
            return OracleDecision.REFLEX

        except Exception as e:
            logger.debug(f"[COMMIT_AUTHORITY] MANAS consultation error: {e}")
            return OracleDecision.REFLEX

    # =========================================================================
    # Conflict Healing
    # =========================================================================

    def _heal_conflicts(self, paths: Optional[List[Path]] = None) -> List[str]:
        """
        Heal merge conflicts using UntotbarMergeEngine.

        Returns list of healed file paths.
        """
        merge_engine = self._get_merge_engine()
        healed = []

        # Find files with conflict markers
        git = self._get_git_state()
        workspace = self._workspace

        if paths:
            check_paths = paths
        else:
            # Check all staged files
            staged = git._get_staged_files()
            check_paths = [workspace / f for f in staged]

        for path in check_paths:
            if isinstance(path, str):
                path = Path(path)
            full_path = workspace / path if not path.is_absolute() else path

            if merge_engine.detect_conflicts(full_path):
                result = merge_engine.auto_heal_file(full_path)
                if result:
                    # Write healed content
                    full_path.write_bytes(result.healed_content)
                    healed.append(str(path))
                    logger.info(f"[COMMIT_AUTHORITY] Healed: {path}")

        return healed

    # =========================================================================
    # Commit Execution
    # =========================================================================

    def _execute_commit(
        self,
        paths: Optional[List[Path]],
        message: str,
    ) -> Optional[GitCommit]:
        """Execute the actual Git commit."""
        git = self._get_git_state()

        # Stage paths if specified
        if paths:
            patterns = [str(p) for p in paths]
            git.stage(patterns)

        # Commit
        return git.commit(
            message=message,
            commit_type="chore",
            scope="state",
            no_verify=True,  # Runtime state skips hooks
        )

    # =========================================================================
    # Panic Dump (Lost+Found Safety Net)
    # =========================================================================

    def _panic_dump(
        self,
        paths: Optional[List[Path]],
        message: str,
        context: Optional[Dict[str, Any]],
        error: str,
    ) -> Path:
        """
        Dump failed commit data to lost+found.

        This ensures NO DATA LOSS even on irrecoverable failure.
        The user can manually recover from .vibe/lost+found/
        """
        lost_found = self._workspace / self.LOST_FOUND_DIR
        lost_found.mkdir(parents=True, exist_ok=True)

        # Create unique dump filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        dump_file = lost_found / f"panic_{timestamp}.json"

        # Gather data
        dump_data = {
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "message": message,
            "paths": [str(p) for p in (paths or [])],
            "context": context or {},
            "workspace": str(self._workspace),
        }

        # Add file contents for dirty files
        if paths:
            file_contents = {}
            for path in paths:
                full_path = self._workspace / path if not Path(path).is_absolute() else Path(path)
                if full_path.exists():
                    try:
                        content = full_path.read_text()
                        file_contents[str(path)] = content
                    except Exception as e:
                        file_contents[str(path)] = f"<error reading: {e}>"
            dump_data["file_contents"] = file_contents

        # Write dump
        dump_file.write_text(json.dumps(dump_data, indent=2))
        logger.warning(f"[COMMIT_AUTHORITY] Panic dump saved: {dump_file}")

        return dump_file

    # =========================================================================
    # Resonance (Cached)
    # =========================================================================

    def compute_resonance(self, intent: str, paths: Optional[List[Path]] = None) -> float:
        """
        Compute resonance between intent and current state (cached).

        High resonance = natural evolution
        Low resonance = disruptive change

        Uses cache to avoid per-commit overhead.
        """
        # Generate signatures
        intent_sig = intent[:50]  # Truncate for cache key
        state_sig = self._get_state_signature(paths)

        # Check cache
        cached = self._resonance_cache.get(intent_sig, state_sig)
        if cached is not None:
            return cached

        # Compute fresh
        try:
            from vibe_core.reactor.quantum import compute_resonance

            resonance = compute_resonance(intent, state_sig)
        except ImportError:
            # QuantumReactor not available
            resonance = 0.5  # Neutral

        # Cache result
        self._resonance_cache.set(intent_sig, state_sig, resonance)
        return resonance

    def _get_state_signature(self, paths: Optional[List[Path]] = None) -> str:
        """Generate signature for current state."""
        if paths:
            return ":".join(sorted(str(p) for p in paths))

        # Use git status as signature
        git = self._get_git_state()
        status = git.status()
        return f"{status.get('branch', 'unknown')}:{status.get('sha', '0000000')}"


# =============================================================================
# Singleton Access
# =============================================================================

_global_authority: Optional[CommitAuthority] = None


def get_commit_authority(workspace: Optional[Path] = None) -> CommitAuthority:
    """Get or create global CommitAuthority singleton."""
    global _global_authority

    if _global_authority is None:
        _global_authority = CommitAuthority(workspace)

    return _global_authority


def reset_commit_authority() -> None:
    """Reset global singleton (mainly for testing)."""
    global _global_authority
    _global_authority = None
