"""Moltbook Heartbeat Orchestration — MURALI Phase Router + Pipeline Dispatcher."""

import logging
import time
from typing import TYPE_CHECKING, Callable, Protocol

from vibe_core.mahamantra.substrate.core.seed import HALVES, MAHAJANA_COUNT, QUARTERS, SHARANAGATI, TRINITY

if TYPE_CHECKING:
    from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

logger = logging.getLogger("MOLTBOOK.HEARTBEAT")


class HeartbeatCallbacks(Protocol):
    """Callbacks that MoltbookPlugin provides to HeartbeatOrchestrator."""

    def _process_inbound_dms(self) -> None:
        """Handle incoming direct messages."""
        ...

    def _process_dm_requests(self) -> None:
        """Process new DM requests."""
        ...

    def _scan_feed(self) -> None:
        """Scan the feed for new topics."""
        ...

    def _evaluate_strategy(self) -> None:
        """Evaluate strategy based on current state."""
        ...

    def _execute_intents(self) -> None:
        """Execute top-ranked intents."""
        ...

    def _track_engagement(self) -> None:
        """Track engagement metrics."""
        ...

    def _discover_submolts(self) -> None:
        """Discover available submolts (GENESIS phase)."""
        ...

    def _check_own_comment_replies(self) -> None:
        """Monitor replies to own comments (KARMA phase)."""
        ...

    def _adjust_intervals(self) -> None:
        """Adjust heartbeat intervals (MOKSHA phase)."""
        ...

    def _reflect_on_patterns(self) -> None:
        """Analyze patterns and apply learning (MOKSHA phase)."""
        ...

    def _update_profile(self) -> None:
        """Update agent profile on Moltbook."""
        ...

    def _trim_memory(self) -> None:
        """Trim in-memory caches."""
        ...

    def _monitor_queue_health(self) -> None:
        """Warn if content queue is unhealthy."""
        ...

    def _drain_content_queue(self) -> None:
        """Send queued content to Moltbook."""
        ...

    def _record_heartbeat_reflection(self, department: str, duration_s: float) -> None:
        """Record execution metrics in Reflection Protocol."""
        ...

    def _emit_ouroboros_health(self) -> None:
        """Emit health signal to Ouroboros monitoring."""
        ...


class HeartbeatOrchestrator:
    """Orchestrates the heartbeat cycle with MURALI phase-aware dispatch.

    Responsibilities:
    - Route heartbeats through 4 MURALI departments (research/planning/execution/learning)
    - Execute core pipeline (feed scan → strategy → intent → engagement)
    - Schedule sub-frequency tasks by department
    - Manage maintenance cycles (profile, memory, queue)
    - Record execution patterns via Reflection Protocol
    - Emit health signals to Ouroboros

    YANTRA Discipline:
    - No ANY types (Protocol-based)
    - Idempotent: can resume after kill -9
    - Explicit logging for all state changes
    - No hidden side effects
    """

    _DEPARTMENTS = ("research", "planning", "execution", "learning")
    _HEARTBEAT_DEBOUNCE_S = 2.0

    def __init__(self, plugin: "MoltbookPlugin") -> None:
        """Initialize orchestrator with parent plugin callbacks.

        Args:
            plugin: MoltbookPlugin instance providing callbacks
        """
        self._plugin: "MoltbookPlugin" = plugin
        self._heartbeat_count = 0
        self._last_heartbeat_ts = 0.0
        self._genesis_tick = 0
        self._karma_tick = 0
        self._moksha_tick = 0

    def dispatch_heartbeat(self, new_heartbeat: dict) -> None:
        """Dispatch one complete heartbeat cycle.

        Args:
            new_heartbeat: Heartbeat dict from Moltbook API (with has_activity, etc.)

        Performs debounce check, then executes:
        1. Reactive DM processing (if has_activity)
        2. Core pipeline (ALL departments, every heartbeat)
        3. Sub-frequency tasks (routed by MURALI phase)
        4. Maintenance cycles (profile, memory)
        5. Queue drain
        6. Reflection + Ouroboros emission
        """
        now = time.time()

        # Debounce guard: prevent double-fire from split-brain orchestrators
        if (now - self._last_heartbeat_ts) < self._HEARTBEAT_DEBOUNCE_S:
            logger.debug(f"Heartbeat debounced (fired {now - self._last_heartbeat_ts:.2f}s ago)")
            return

        self._last_heartbeat_ts = now

        # Increment cycle counter
        self._heartbeat_count += 1

        # Get current MURALI phase
        department = self._get_current_department()

        # Log entry
        plugin_queue_size = 0
        if hasattr(self._plugin, "_content_queue"):
            try:
                queue_stats = getattr(self._plugin._content_queue, "stats", {})
                plugin_queue_size = queue_stats.get("pending", 0)
            except Exception:
                pass

        logger.info(
            f"HB#{self._heartbeat_count} → {department.upper()} "
            f"(queue={plugin_queue_size})"
        )

        # === STEP 1: Reactive DM processing ===
        has_new = new_heartbeat.get("has_activity", False)
        if has_new:
            self._safe_call(self._plugin._process_inbound_dms, "inbound_dms")
            self._safe_call(self._plugin._process_dm_requests, "dm_requests")

        # === STEP 2: Core pipeline (runs every heartbeat) ===
        self._safe_call(self._plugin._scan_feed, "feed_scan")
        self._safe_call(self._plugin._evaluate_strategy, "strategy_evaluation")
        self._safe_call(self._plugin._execute_intents, "intent_execution")
        self._safe_call(self._plugin._track_engagement, "engagement_tracking")

        # === STEP 3: Sub-frequency tasks (MURALI phase determines scheduling) ===
        self._dispatch_department_tasks(department)

        # === STEP 4: Maintenance cycles ===
        if self._heartbeat_count % MAHAJANA_COUNT == 0:
            self._safe_call(self._plugin._update_profile, "profile_update")
            self._safe_call(self._plugin._trim_memory, "memory_trim")

        # === STEP 5: Queue and monitoring ===
        self._safe_call(self._plugin._monitor_queue_health, "queue_health")
        self._safe_call(self._plugin._drain_content_queue, "queue_drain")

        # === STEP 6: Observability ===
        duration_s = time.time() - now
        self._safe_call(
            lambda: self._plugin._record_heartbeat_reflection(department, duration_s),
            "reflection_record",
        )
        self._safe_call(self._plugin._emit_ouroboros_health, "ouroboros_emit")

        logger.debug(f"Heartbeat complete in {duration_s:.3f}s")

    def _dispatch_department_tasks(self, department: str) -> None:
        """Execute sub-frequency tasks for the current MURALI phase.

        Args:
            department: One of (research, planning, execution, learning)
        """
        if department == "research":
            # GENESIS: discover new submolts
            if self._heartbeat_count <= QUARTERS or self._genesis_tick % SHARANAGATI == 0:
                self._safe_call(self._plugin._discover_submolts, "submolt_discovery")
            self._genesis_tick += 1

        elif department == "planning":
            # DHARMA: strategy planning (core pipeline handles this)
            pass

        elif department == "execution":
            # KARMA: execute and monitor replies
            if self._karma_tick % HALVES == 0:
                self._safe_call(self._plugin._check_own_comment_replies, "reply_monitoring")
            self._karma_tick += 1

        elif department == "learning":
            # MOKSHA: reflect on patterns and adjust
            if self._moksha_tick % TRINITY == 0:
                self._safe_call(self._plugin._adjust_intervals, "interval_adjustment")
            self._safe_call(self._plugin._reflect_on_patterns, "reflection_analysis")
            self._moksha_tick += 1

    def _get_current_department(self) -> str:
        """Determine current MURALI phase from heartbeat cycle.

        Uses heartbeat_count % 4 for reliable rotation. In standalone mode
        (MinimalKernel, GitHub Actions), this is the only reliable clock.

        Returns:
            Department name: research, planning, execution, or learning
        """
        if not getattr(self._plugin, "_standalone_mode", True):
            try:
                from vibe_core.cartridges.agent_city.moltbook.core.agency_director import (
                    MuraliRouter,
                )

                return MuraliRouter().current_department(fallback_tick=self._heartbeat_count)
            except Exception:
                pass

        # Fallback: heartbeat-based rotation
        return self._DEPARTMENTS[self._heartbeat_count % len(self._DEPARTMENTS)]

    def _safe_call(self, fn: Callable[[], None], label: str) -> None:
        """Execute callback with error handling and logging.

        Args:
            fn: Callable to execute
            label: Human-readable label for logging
        """
        try:
            fn()
        except Exception as e:
            logger.error(f"Heartbeat task '{label}' failed: {type(e).__name__}: {e!r}")

    @property
    def current_heartbeat_count(self) -> int:
        """Current heartbeat sequence number."""
        return self._heartbeat_count

    def snapshot(self) -> dict:
        """Snapshot orchestrator state for persistence.

        Returns:
            State dict with tick counters for recovery after kill -9
        """
        return {
            "heartbeat_count": self._heartbeat_count,
            "last_heartbeat_ts": self._last_heartbeat_ts,
            "genesis_tick": self._genesis_tick,
            "karma_tick": self._karma_tick,
            "moksha_tick": self._moksha_tick,
        }

    def restore(self, state: dict) -> None:
        """Restore orchestrator state after restart.

        Args:
            state: State dict from previous snapshot()
        """
        self._heartbeat_count = state.get("heartbeat_count", 0)
        self._last_heartbeat_ts = state.get("last_heartbeat_ts", 0.0)
        self._genesis_tick = state.get("genesis_tick", 0)
        self._karma_tick = state.get("karma_tick", 0)
        self._moksha_tick = state.get("moksha_tick", 0)
        logger.info(
            f"Heartbeat orchestrator restored: HB#{self._heartbeat_count}, "
            f"genesis={self._genesis_tick}, karma={self._karma_tick}, moksha={self._moksha_tick}"
        )
