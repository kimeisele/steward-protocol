"""Moltbook Intent Executor — Strategic Intent → Content Generation."""

import logging
from typing import TYPE_CHECKING, Optional, Protocol

if TYPE_CHECKING:
    from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

logger = logging.getLogger("MOLTBOOK.INTENT")


class IntentExecutorCallbacks(Protocol):
    """Callbacks that MoltbookPlugin provides to IntentExecutor."""

    _content_queue: object  # ContentQueue
    _current_intents: list  # List[StrategicIntent]
    _commented_post_ids: set  # Set[str]
    _submolt_descriptions: dict  # Dict[str, str]
    _last_post_heartbeat: int
    _heartbeat_count: int

    def _director_propose(
        self,
        content_type: str,
        raw_input: str,
        proposal_type: str,
        **extra,
    ) -> object:  # Optional[ContentProposal]
        """Content generation via AgencyDirector I-P-V-O pipeline."""
        ...

    def _select_submolt(self, seed_text: str) -> Optional[str]:
        """Select best submolt for content."""
        ...

    def _emit_event(self, event_type_name: str, message: str, data: Optional[dict] = None) -> None:
        """Emit system event."""
        ...


class IntentExecutor:
    """Execute strategic intents → content generation & queueing.

    Responsibilities:
    - Process strategically ranked intents (max 3 per cycle)
    - Generate comments with post-level deduplication
    - Generate posts with submolt selection
    - Extract titles from multi-line post content
    - Track post creation timestamps
    - Emit strategic silence events when no quality intents
    - Explicit error handling per intent

    YANTRA Discipline:
    - Protocol-based callbacks (no Any types)
    - Idempotent: processes intents once per cycle
    - Clear separation: comment vs. post handling
    - State tracking: last_post_heartbeat for rate limiting
    """

    def __init__(self, plugin: "MoltbookPlugin") -> None:
        """Initialize with parent plugin callbacks.

        Args:
            plugin: MoltbookPlugin instance providing callbacks
        """
        self._plugin: "MoltbookPlugin" = plugin

    def execute_intents(self) -> None:
        """Execute strategic intents through content generation pipeline.

        KARMA phase: Generate content for strategically ranked intents.

        Performs:
        1. Check if intents exist (strategic silence if not)
        2. For each intent (max 3):
           - Comment: check post dedup, generate, enqueue
           - Post: select submolt, generate, enqueue
        3. Clear executed intents after processing
        """
        if not self._plugin._current_intents:
            # Strategic silence: no quality intents = don't force-post garbage
            logger.info("No quality intents — strategic silence")
            self._plugin._emit_event("STRATEGIC_SILENCE", "No intents met quality threshold")
            return

        for intent in self._plugin._current_intents[:3]:
            try:
                if intent.action_type == "comment" and intent.target_post_id:
                    self._execute_comment_intent(intent)

                elif intent.action_type == "post":
                    self._execute_post_intent(intent)

            except Exception as e:
                logger.warning(f"Intent execution failed ({intent.action_type}): {e}")

        # Clear executed intents
        self._plugin._current_intents = []

    def _execute_comment_intent(self, intent: object) -> None:
        """Execute a comment intent with post-level deduplication.

        Args:
            intent: StrategicIntent with target_post_id and topic
        """
        from vibe_core.protocols.moltbook_content import ContentType

        # Post-level dedup: don't comment on same post twice
        intent_dict = intent.__dict__ if hasattr(intent, "__dict__") else intent
        target_post_id = intent_dict.get("target_post_id", "") if isinstance(intent_dict, dict) else ""

        if target_post_id in self._plugin._commented_post_ids:
            logger.info(f"Already commented on {target_post_id}, skipping")
            return

        # Look up full post content from feed cache
        post_content = ""
        for post in getattr(self._plugin, "_current_feed_topics", []):
            if isinstance(post, dict) and post.get("id") == target_post_id:
                post_content = str(post.get("content", ""))
                break

        proposal = self._plugin._director_propose(
            content_type="comment",
            raw_input=intent_dict.get("topic", ""),
            proposal_type=ContentType.COMMENT.value,
            post_id=target_post_id,
            trigger="strategic_intent",
            context={
                "strategic_reasoning": intent_dict.get("reasoning", ""),
                "engagement_context": intent_dict.get("engagement_context", ""),
                "submolt_context": intent_dict.get("submolt_context", ""),
                "content_format": intent_dict.get("content_format", ""),
                "post_content": post_content,
                "mission_id": intent_dict.get("mission_id", ""),
                "priority": intent_dict.get("priority", 5),
            },
        )
        if proposal:
            self._plugin._content_queue.enqueue(proposal)
            self._plugin._commented_post_ids.add(target_post_id)
            logger.info(
                f"Strategic comment queued for {target_post_id} (mission={intent_dict.get('mission_id', '')})"
            )
        else:
            # KIRTAN: Content generation failed for this intent
            logger.warning(f"Content generation returned None for comment on {target_post_id}")
            self._plugin._emit_event(
                "INTENT_FAILURE",
                f"Comment intent failed (no content): {target_post_id}",
                {"action": "comment", "post_id": target_post_id, "mission_id": intent_dict.get("mission_id", "")},
            )

    def _execute_post_intent(self, intent: object) -> None:
        """Execute a post intent with submolt selection and title extraction.

        Args:
            intent: StrategicIntent with topic for seed text
        """
        from vibe_core.protocols.moltbook_content import ContentType

        intent_dict = intent.__dict__ if hasattr(intent, "__dict__") else intent
        seed = intent_dict.get("topic", "")

        # Select best submolt via resonance cross-scoring
        selected_submolt = self._plugin._select_submolt(seed)

        # Build meaningful context: name + description (not bare name)
        submolt_ctx = intent_dict.get("submolt_context", "")
        if not submolt_ctx and selected_submolt:
            desc = self._plugin._submolt_descriptions.get(selected_submolt, "")
            submolt_ctx = f"{selected_submolt} — {desc}" if desc else selected_submolt

        proposal = self._plugin._director_propose(
            content_type="post",
            raw_input=seed,
            proposal_type=ContentType.POST.value,
            trigger="strategic_intent",
            submolt=selected_submolt or "",
            context={
                "strategic_reasoning": intent_dict.get("reasoning", ""),
                "engagement_context": intent_dict.get("engagement_context", ""),
                "submolt_context": submolt_ctx,
                "content_format": intent_dict.get("content_format", ""),
                "mission_id": intent_dict.get("mission_id", ""),
                "priority": intent_dict.get("priority", 5),
            },
        )
        if proposal:
            # Extract title from first line if present (markdown-style)
            content = proposal.get("content", "")
            lines = content.strip().split("\n", 1)
            if len(lines) > 1:
                proposal["title"] = lines[0].strip().lstrip("#").strip()[:120]
                proposal["content"] = lines[1].strip()
            else:
                proposal["title"] = content[:120]

            self._plugin._content_queue.enqueue(proposal)
            self._plugin._last_post_heartbeat = self._plugin._heartbeat_count
            logger.info(
                f"Strategic post queued: {proposal.get('title', '')[:50]} (mission={intent_dict.get('mission_id', '')})"
            )
        else:
            # KIRTAN: Content generation failed for this intent
            logger.warning("Content generation returned None for post intent")
            self._plugin._emit_event(
                "INTENT_FAILURE",
                "Post intent failed (no content)",
                {"action": "post", "mission_id": intent_dict.get("mission_id", "")},
            )
