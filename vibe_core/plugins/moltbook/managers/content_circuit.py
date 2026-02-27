"""Moltbook Content Circuit Executor — AgencyDirector wrapper for circuit execution."""

import logging
from typing import Any, Dict, Optional, Protocol

logger = logging.getLogger("MOLTBOOK.CIRCUIT")


class ContentCircuitCallbacks(Protocol):
    """Callbacks that MoltbookPlugin provides to ContentCircuitExecutor."""

    agency_director: object  # MahaDirector

    def _emit_event(self, event_type_name: str, message: str, data: Optional[dict] = None) -> None:
        """Emit system event."""
        ...


class ContentCircuitExecutor:
    """Execute content generation circuit via AgencyDirector.

    Responsibilities:
    - Build kwargs dict for AgencyDirector.run_retry_loop()
    - Call director with context passthrough (strategic reasoning, engagement, etc.)
    - Handle low-integrity skips (emit event, return None)
    - Convert CycleResult → dict format for callers
    - Return None on any failure (no fallbacks)
    - KIRTAN: Record failures → Reflection + SynapseStore for system learning
    - KIRTAN: Record successes → SynapseStore for positive reinforcement

    YANTRA Discipline:
    - ONE path: AgencyDirector.run_retry_loop() IS the state machine
    - Explicit event emission on integrity skip
    - Clear status handling (SKIPPED_LOW_INTEGRITY vs. SUCCESS vs. other)
    - No fallbacks: None on any non-success state
    - Every outcome (success/failure) feeds back into the learning system
    """

    def __init__(self, plugin: "ContentCircuitCallbacks") -> None:
        """Initialize with parent plugin callbacks.

        Args:
            plugin: MoltbookPlugin instance providing callbacks
        """
        self._plugin: "ContentCircuitCallbacks" = plugin

    def execute(
        self,
        raw_input: str,
        content_type: str = "comment",
        post_id: str = "",
        sender: str = "",
        trigger: str = "heartbeat",
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Execute content generation circuit via AgencyDirector.

        MOLTBOOK_CONTENT_V1 — ONE path through AgencyDirector:
            SHABDA  = _run_pipeline()
            ARTHA   = guna/integrity gates
            PRATYAYA = _compose_content() (engine + MahaComposition + LLM)
            KARMA   = constitution.validate() + event_log

        Args:
            raw_input: Seed text/prompt for content generation
            content_type: Type of content (comment, post, dm, etc.)
            post_id: Target post ID (for comments)
            sender: DM sender context
            trigger: What triggered this execution (heartbeat, manual, etc.)
            context: Dict with strategic reasoning, engagement context, submolt context

        Returns:
            Dict with keys: content, guna, guardian, duration_ms on success
            None if content skipped (low integrity) or generation failed
        """
        # Build kwargs dict for AgencyDirector
        kwargs: Dict[str, Any] = {
            "content_type": content_type,
            "raw_input": raw_input,
            "post_id": post_id,
            "sender": sender,
            "trigger": trigger,
        }
        # Thread strategic context through to _input() → _compose_content()
        if context:
            kwargs.update(context)

        # Execute circuit via director (catches all internal errors)
        result = self._plugin.agency_director.run_retry_loop(**kwargs)

        # Handle low integrity skip
        if result.status == "SKIPPED_LOW_INTEGRITY":
            self._plugin._emit_event(
                "CONTENT_SKIPPED",
                f"Low integrity skip: {result.guna}",
                {
                    "guna": result.guna,
                    "content_type": content_type,
                },
            )
            self._record_content_failure(content_type, result)
            return None

        # Handle other failures
        if result.status != "SUCCESS" or not result.content:
            self._record_content_failure(content_type, result)
            return None

        # KIRTAN: Record success for positive reinforcement
        self._record_content_success(content_type)

        # Convert CycleResult → dict format
        return {
            "content": result.content,
            "guna": result.guna,
            "guardian": result.guardian,
            "duration_ms": result.duration_ms,
        }

    def _record_content_failure(self, content_type: str, result: object) -> None:
        """Kirtan: content generation failed → signal Reflection + SynapseStore.

        Every failure feeds back into the system:
        1. Reflection: records ExecutionRecord for pattern detection
        2. SynapseStore: decrements weight so strategy adapts
        3. Event: emits CONTENT_FAILURE for Ouroboros visibility
        """
        status = getattr(result, "status", "UNKNOWN")
        guna = getattr(result, "guna", "")
        guardian = getattr(result, "guardian", "")
        duration_ms = getattr(result, "duration_ms", 0)

        # Reflection: record for pattern analysis (MOKSHA will detect trends)
        try:
            from vibe_core.protocols.reflection import ExecutionRecord, get_reflection_safe

            reflection = get_reflection_safe()
            reflection.record_execution(
                ExecutionRecord(
                    command=f"moltbook.content.{content_type}",
                    success=False,
                    error=status,
                    duration_ms=duration_ms,
                    context={
                        "content_type": content_type,
                        "status": status,
                        "guna": guna,
                        "guardian": guardian,
                    },
                )
            )
        except Exception as e:
            logger.warning(f"Reflection recording failed: {e}")

        # SynapseStore: learn that this content_type is failing
        try:
            from vibe_core.state.synapse_store import get_synapse_store

            store = get_synapse_store()
            store.decrement_weight(f"moltbook:content:{content_type}", "generate", delta=0.03)
        except Exception as e:
            logger.warning(f"SynapseStore failure learning failed: {e}")

        self._plugin._emit_event(
            "CONTENT_FAILURE",
            f"Content generation failed: {status} ({content_type})",
            {"status": status, "content_type": content_type, "guna": guna},
        )

    def _record_content_success(self, content_type: str) -> None:
        """Kirtan: content generation succeeded → SynapseStore positive reinforcement."""
        try:
            from vibe_core.state.synapse_store import get_synapse_store

            store = get_synapse_store()
            store.increment_weight(f"moltbook:content:{content_type}", "generate", delta=0.02)
        except Exception as e:
            logger.warning(f"SynapseStore success learning failed: {e}")
