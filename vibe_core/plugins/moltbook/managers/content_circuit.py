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

    YANTRA Discipline:
    - ONE path: AgencyDirector.run_retry_loop() IS the state machine
    - Explicit event emission on integrity skip
    - Clear status handling (SKIPPED_LOW_INTEGRITY vs. SUCCESS vs. other)
    - No fallbacks: None on any non-success state
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
            return None

        # Handle other failures
        if result.status != "SUCCESS" or not result.content:
            return None

        # Convert CycleResult → dict format
        return {
            "content": result.content,
            "guna": result.guna,
            "guardian": result.guardian,
            "duration_ms": result.duration_ms,
        }
