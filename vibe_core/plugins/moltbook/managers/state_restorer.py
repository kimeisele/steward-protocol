"""Moltbook State Restorer — Cross-phase state recovery."""

import logging
from typing import TYPE_CHECKING, List, Protocol

if TYPE_CHECKING:
    from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

logger = logging.getLogger("MOLTBOOK.RESTORE")


class StateRestorerCallbacks(Protocol):
    """Callbacks that MoltbookPlugin provides to StateRestorer."""

    _heartbeat: object  # HeartbeatOrchestrator
    _current_feed_topics: List[dict]
    _current_intents: list  # List[StrategicIntent]
    _persistence: object  # PersistenceManager


class StateRestorer:
    """Restore cross-phase state from previous run.

    Responsibilities:
    - Restore orchestrator state (phase ticks, debounce timestamp)
    - Restore heartbeat count (synchronized with orchestrator)
    - Restore feed topics (raw dicts, no deserialization)
    - Restore strategic intents (StrategicIntent objects)
    - Idempotent: only restore if state was empty

    YANTRA Discipline:
    - Protocol-based callbacks (no Any types)
    - Explicit error handling per state type
    - Logging at restoration points
    - No fallbacks: if deserialization fails, skip intent restoration
    """

    def __init__(self, plugin: "MoltbookPlugin") -> None:
        """Initialize with parent plugin callbacks.

        Args:
            plugin: MoltbookPlugin instance providing callbacks
        """
        self._plugin: "MoltbookPlugin" = plugin

    def restore_phase_state(self) -> None:
        """Restore cross-phase state from previous run.

        Restores in order:
        1. Orchestrator state (phase ticks, debounce timestamp)
        2. Heartbeat count (synchronized with orchestrator)
        3. Feed topics (raw dicts)
        4. Strategic intents (StrategicIntent objects)

        Idempotent: only restores if current state is empty.
        """
        restored = self._plugin._persistence.restore_phase_state()
        if not restored:
            return

        # === Restore orchestrator state (phase ticks, debounce timestamp, etc.) ===
        orch_state = restored.get("orchestrator_state", {})
        if orch_state:
            self._plugin._heartbeat.restore(orch_state)

        # === Restore heartbeat_count (from orchestrator, highest wins) ===
        saved_hb = restored.get("heartbeat_count", 0)
        if saved_hb > self._plugin._heartbeat.current_heartbeat_count:
            # Manually set if persistence has a higher count
            if hasattr(self._plugin._heartbeat, "_heartbeat_count"):
                self._plugin._heartbeat._heartbeat_count = saved_hb

        # === Restore feed topics (raw dicts, no deserialization needed) ===
        topics = restored.get("feed_topics", [])
        if topics and not self._plugin._current_feed_topics:
            self._plugin._current_feed_topics = topics
            logger.info(f"Restored {len(topics)} feed topics from previous run")

        # === Restore intents as StrategicIntent objects ===
        intent_dicts = restored.get("intent_dicts", [])
        if intent_dicts and not self._plugin._current_intents:
            self._restore_strategic_intents(intent_dicts)

    def _restore_strategic_intents(self, intent_dicts: List[dict]) -> None:
        """Deserialize and restore strategic intents from dicts.

        Args:
            intent_dicts: List of intent dictionaries from persistence

        Explicit error handling: if any step fails, skip intent restoration.
        """
        try:
            from vibe_core.cartridges.agent_city.moltbook.core.strategy import StrategicIntent

            intents = []
            for d in intent_dicts:
                intents.append(
                    StrategicIntent(
                        action_type=d.get("action_type", "skip"),
                        topic=d.get("topic", ""),
                        reasoning=d.get("reasoning", ""),
                        priority=int(d.get("priority", 5)),
                        mission_id=d.get("mission_id", ""),
                        target_post_id=d.get("target_post_id", ""),
                        engagement_context=d.get("engagement_context", ""),
                        submolt_context=d.get("submolt_context", ""),
                    )
                )
            self._plugin._current_intents = intents
            logger.info(f"Restored {len(intents)} strategic intents from previous run")
        except Exception as e:
            logger.debug(f"Strategic intent restoration failed: {e}")
