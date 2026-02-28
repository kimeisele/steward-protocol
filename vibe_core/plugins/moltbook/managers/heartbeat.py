"""Moltbook Heartbeat Orchestration — MURALI Phase Router + Pipeline Dispatcher."""

import logging
import time
from typing import TYPE_CHECKING, Callable

from vibe_core.mahamantra.substrate.core.seed import HALVES, MAHAJANA_COUNT, QUARTERS, SHARANAGATI, TRINITY
from vibe_core.plugins.moltbook.state import MoltbookState

if TYPE_CHECKING:
    from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

logger = logging.getLogger("MOLTBOOK.HEARTBEAT")


class HeartbeatOrchestrator:
    """Orchestrates the heartbeat cycle with MURALI phase-aware dispatch.

    Receives MoltbookState for data access. Plugin reference used only
    for action method callbacks.

    Responsibilities:
    - Route heartbeats through 4 MURALI departments (research/planning/execution/learning)
    - Execute core pipeline (feed scan → strategy → intent → engagement)
    - Schedule sub-frequency tasks by department
    - Manage maintenance cycles (profile, memory, queue)
    - Record execution patterns via Reflection Protocol
    - Emit health signals to Ouroboros
    """

    _DEPARTMENTS = ("research", "planning", "execution", "learning")
    _HEARTBEAT_DEBOUNCE_S = 2.0

    def __init__(self, state: MoltbookState, plugin: "MoltbookPlugin") -> None:
        self._state = state
        self._plugin = plugin
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
        try:
            queue_stats = self._state.content_queue.stats
            plugin_queue_size = queue_stats.get("pending", 0) if isinstance(queue_stats, dict) else 0
        except Exception:
            pass

        logger.info(f"HB#{self._heartbeat_count} → {department.upper()} (queue={plugin_queue_size})")

        # === STEP 1: Reactive DM processing ===
        has_new = new_heartbeat.get("has_activity", False)
        if has_new:
            self._safe_call(self._plugin._process_inbound_dms, "inbound_dms")
            self._safe_call(self._plugin._process_dm_requests, "dm_requests")

        # === STEP 2: Department-specific work (MURALI: each heartbeat = one job) ===
        # GENESIS → gather intelligence
        # DHARMA  → plan strategy
        # KARMA   → produce content
        # MOKSHA  → learn + heal
        self._dispatch_department(department)

        # === STEP 3: Always-on systems (reactive, lightweight) ===
        self._safe_call(self._plugin._monitor_queue_health, "queue_health")
        self._safe_call(self._plugin._drain_content_queue, "queue_drain")

        # === STEP 4: Maintenance cycles (low frequency) ===
        if self._heartbeat_count % MAHAJANA_COUNT == 0:
            self._safe_call(self._plugin._update_profile, "profile_update")
            self._safe_call(self._plugin._trim_memory, "memory_trim")

        # === STEP 5: Observability (record BEFORE reflect, not after) ===
        duration_s = time.time() - now
        self._safe_call(
            lambda: self._plugin._record_heartbeat_reflection(department, duration_s),
            "reflection_record",
        )
        self._safe_call(self._plugin._emit_ouroboros_health, "ouroboros_emit")

        logger.info(f"HB#{self._heartbeat_count} {department.upper()} complete in {duration_s:.3f}s")

    def _dispatch_department(self, department: str) -> None:
        """Execute the ONE department job for this heartbeat.

        Each heartbeat = one workday. 4 heartbeats = 1 full MURALI cycle.
        GENESIS gathers intelligence. DHARMA plans. KARMA produces. MOKSHA learns.
        """
        if department == "research":
            # GENESIS: gather ALL intelligence — feed, AGORA, submolts
            self._safe_call(self._plugin._scan_feed, "feed_scan")
            self._safe_call(self._plugin._gather_broadcast_intelligence, "agora_listen")
            if self._heartbeat_count <= QUARTERS or self._genesis_tick % SHARANAGATI == 0:
                self._safe_call(self._plugin._discover_submolts, "submolt_discovery")
            self._genesis_tick += 1

        elif department == "planning":
            # DHARMA: evaluate strategy from gathered intelligence → intents
            self._safe_call(self._plugin._evaluate_strategy, "strategy_evaluation")

        elif department == "execution":
            # KARMA: produce content from intents + monitor replies
            self._safe_call(self._plugin._execute_intents, "intent_execution")
            if self._karma_tick % HALVES == 0:
                self._safe_call(self._plugin._check_own_comment_replies, "reply_monitoring")
            self._karma_tick += 1

        elif department == "learning":
            # MOKSHA: measure engagement → reflect → adjust → heal
            self._safe_call(self._plugin._track_engagement, "engagement_tracking")
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
        if not self._state.standalone_mode:
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
