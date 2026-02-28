"""Moltbook Intent Executor — Strategic Intent → Content Generation."""

import logging
from typing import Any, Callable, Dict, Optional

from vibe_core.plugins.moltbook.state import MoltbookState

logger = logging.getLogger("MOLTBOOK.INTENT")


class IntentExecutor:
    """Execute strategic intents → content generation & queueing.

    Receives MoltbookState for data access and explicit callables for actions.
    No back-reference to plugin — full dependency injection.

    Responsibilities:
    - Process strategically ranked intents (max 3 per cycle)
    - Generate comments with post-level deduplication
    - Generate posts with submolt selection
    - Extract titles from multi-line post content
    - Track post creation timestamps
    - Emit strategic silence events when no quality intents
    """

    def __init__(
        self,
        state: MoltbookState,
        director_propose: Callable[..., Optional[Dict[str, Any]]],
        select_submolt: Callable[[str], Optional[str]],
        emit_event: Callable[..., None],
        heartbeat_count_getter: Callable[[], int],
    ) -> None:
        self._state = state
        self._director_propose = director_propose
        self._select_submolt = select_submolt
        self._emit_event = emit_event
        self._get_heartbeat_count = heartbeat_count_getter

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
        if not self._state.current_intents:
            # Strategic silence: no quality intents = don't force-post garbage
            logger.info("No quality intents — strategic silence")
            self._emit_event("STRATEGIC_SILENCE", "No intents met quality threshold")
            return

        for intent in self._state.current_intents[:3]:
            try:
                if intent.action_type == "comment" and intent.target_post_id:
                    self._execute_comment_intent(intent)

                elif intent.action_type == "post":
                    self._execute_post_intent(intent)

            except Exception as e:
                logger.warning(f"Intent execution failed ({intent.action_type}): {e}")

        # Clear executed intents
        self._state.current_intents = []

    def _execute_comment_intent(self, intent: object) -> None:
        """Execute a comment intent with post-level deduplication.

        Args:
            intent: StrategicIntent with target_post_id and topic
        """
        from vibe_core.protocols.moltbook_content import ContentType

        # Post-level dedup: don't comment on same post twice
        intent_dict = intent.__dict__ if hasattr(intent, "__dict__") else intent
        target_post_id = intent_dict.get("target_post_id", "") if isinstance(intent_dict, dict) else ""

        if target_post_id in self._state.commented_post_ids:
            logger.info(f"Already commented on {target_post_id}, skipping")
            return

        # Look up full post content from feed cache
        post_content = ""
        for post in self._state.current_feed_topics:
            if isinstance(post, dict) and post.get("id") == target_post_id:
                post_content = str(post.get("content", ""))
                break

        proposal = self._director_propose(
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
            self._state.content_queue.enqueue(proposal)
            self._state.commented_post_ids.add(target_post_id)
            logger.info(f"Strategic comment queued for {target_post_id} (mission={intent_dict.get('mission_id', '')})")
        else:
            # KIRTAN: Content generation failed for this intent
            logger.warning(f"Content generation returned None for comment on {target_post_id}")
            self._emit_event(
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
        selected_submolt = self._select_submolt(seed)

        # Build meaningful context: name + description (not bare name)
        submolt_ctx = intent_dict.get("submolt_context", "")
        if not submolt_ctx and selected_submolt:
            desc = self._state.submolt_descriptions.get(selected_submolt, "")
            submolt_ctx = f"{selected_submolt} — {desc}" if desc else selected_submolt

        proposal = self._director_propose(
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

            self._state.content_queue.enqueue(proposal)
            self._state.last_post_heartbeat = self._get_heartbeat_count()
            logger.info(
                f"Strategic post queued: {proposal.get('title', '')[:50]} (mission={intent_dict.get('mission_id', '')})"
            )
        else:
            # KIRTAN: Content generation failed for this intent
            logger.warning("Content generation returned None for post intent")
            self._emit_event(
                "INTENT_FAILURE",
                "Post intent failed (no content)",
                {"action": "post", "mission_id": intent_dict.get("mission_id", "")},
            )
