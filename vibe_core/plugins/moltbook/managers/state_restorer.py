"""Moltbook State Restorer — Cross-phase state recovery."""

import logging
from typing import Any, Callable, List

from vibe_core.plugins.moltbook.state import MoltbookState

logger = logging.getLogger("MOLTBOOK.RESTORE")


class StateRestorer:
    """Restore cross-phase state from previous run.

    Receives MoltbookState + explicit persistence/heartbeat references.
    No back-reference to plugin — full dependency injection.

    Responsibilities:
    - Restore orchestrator state (phase ticks, debounce timestamp)
    - Restore heartbeat count (synchronized with orchestrator)
    - Restore feed topics (raw dicts, no deserialization)
    - Restore strategic intents (StrategicIntent objects)
    - Idempotent: only restore if state was empty
    """

    def __init__(
        self,
        state: MoltbookState,
        persistence_getter: Callable[[], Any],
        heartbeat_getter: Callable[[], Any],
    ) -> None:
        self._state = state
        self._get_persistence = persistence_getter
        self._get_heartbeat = heartbeat_getter

    def restore_phase_state(self) -> None:
        """Restore cross-phase state from previous run.

        Restores in order:
        1. Orchestrator state (phase ticks, debounce timestamp)
        2. Heartbeat count (synchronized with orchestrator)
        3. Feed topics (raw dicts)
        4. Strategic intents (StrategicIntent objects)

        Idempotent: only restores if current state is empty.
        """
        restored = self._get_persistence().restore_phase_state()
        if not restored:
            return

        heartbeat = self._get_heartbeat()

        # === Restore orchestrator state (phase ticks, debounce timestamp, etc.) ===
        orch_state = restored.get("orchestrator_state", {})
        if orch_state:
            heartbeat.restore(orch_state)

        # === Restore heartbeat_count (from orchestrator, highest wins) ===
        saved_hb = restored.get("heartbeat_count", 0)
        if saved_hb > heartbeat.current_heartbeat_count:
            # Manually set if persistence has a higher count
            if hasattr(heartbeat, "_heartbeat_count"):
                heartbeat._heartbeat_count = saved_hb

        # === Restore feed topics (raw dicts, no deserialization needed) ===
        topics = restored.get("feed_topics", [])
        if topics and not self._state.current_feed_topics:
            self._state.current_feed_topics = topics
            logger.info(f"Restored {len(topics)} feed topics from previous run")

        # === Restore intents as StrategicIntent objects ===
        intent_dicts = restored.get("intent_dicts", [])
        if intent_dicts and not self._state.current_intents:
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
            self._state.current_intents = intents
            logger.info(f"Restored {len(intents)} strategic intents from previous run")
        except Exception as e:
            logger.debug(f"Strategic intent restoration failed: {e}")
