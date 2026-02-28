"""Moltbook Post Orchestrator — Post creation, comment monitoring, profile management."""

import logging
from typing import Any, Dict, Optional, Protocol

from vibe_core.plugins.moltbook.state import MoltbookState

logger = logging.getLogger("MOLTBOOK.POST")


class PostActions(Protocol):
    """Protocol for action callbacks the post orchestrator needs.

    Implemented structurally by MoltbookPlugin — no import needed.
    """

    def _select_submolt(self, seed_text: str) -> Optional[str]: ...
    def _director_propose(
        self, content_type: str, raw_input: str, proposal_type: str, **extra: Any
    ) -> Optional[Any]: ...
    def _ensure_service(self) -> Any: ...
    def _log_activity(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None: ...
    def _record_rate_limit(self, content_type: str) -> None: ...
    def _emit_event(self, event_type_name: str, message: str, data: Optional[Dict[str, Any]] = None) -> None: ...

    @property
    def _heartbeat_count(self) -> int: ...


class PostOrchestrator:
    """Orchestrates post creation, comment monitoring, and profile updates.

    Receives MoltbookState for data access. Actions protocol for callbacks.

    Responsibilities:
    - Create new posts based on strategic intents
    - Monitor and reply to comments on our posts
    - Update agent profile periodically
    - Track post creation for rate limiting
    - Maintain comment-to-post mapping for monitoring
    """

    def __init__(self, state: MoltbookState, actions: PostActions) -> None:
        self._state = state
        self._actions = actions

    def maybe_create_fallback_post(self) -> None:
        """Create a fallback post when no strategic intents available.

        Fallback post creation uses trending feed topics as seed.
        Only used when no strategic intents are available.

        Performs:
        1. Extract trending topics from recent feed
        2. Select best submolt
        3. Generate content via AgencyDirector
        4. Enqueue post proposal
        5. Track post creation for monitoring
        """
        from vibe_core.mahamantra import run_async
        from vibe_core.protocols.moltbook_content import ContentType

        # Extract trending topics from recent feed as context
        feed_topics: list = []
        try:
            posts = run_async(self._state.client.get_feed(sort="hot", limit=5))
            for post in posts or []:
                title = post.get("title", "") if isinstance(post, dict) else ""
                if title:
                    feed_topics.append(title[:80])
        except Exception as e:
            logger.debug(f"Feed topic extraction failed: {e}")

        trigger = "scheduled"
        seed = f"{trigger}: {', '.join(feed_topics[:3])}" if feed_topics else trigger

        # Select best submolt via resonance cross-scoring
        selected_submolt = self._actions._select_submolt(seed)
        submolt_ctx = ""
        if selected_submolt:
            desc = self._state.submolt_descriptions.get(selected_submolt, "")
            submolt_ctx = f"{selected_submolt} — {desc}" if desc else selected_submolt

        try:
            ctx: Dict[str, Any] = {"submolt_context": submolt_ctx}
            if feed_topics:
                ctx["feed_topics"] = feed_topics

            proposal = self._actions._director_propose(
                content_type="post",
                raw_input=seed,
                proposal_type=ContentType.POST.value,
                trigger=trigger,
                submolt=selected_submolt or "",
                context=ctx,
            )
            if proposal:
                # Extract title from first line if present
                content = proposal.get("content", "")
                lines = content.strip().split("\n", 1)
                if len(lines) > 1:
                    proposal["title"] = lines[0].strip().lstrip("#").strip()[:120]
                    proposal["content"] = lines[1].strip()
                else:
                    proposal["title"] = content[:120]

                self._state.content_queue.enqueue(proposal)
                self._state.last_post_heartbeat = self._actions._heartbeat_count
                logger.info(f"Autonomous post queued: {proposal.get('title', '')[:50]}")
            else:
                logger.debug("Post proposal filtered by director (TAMAS+dead or governance)")
        except Exception as e:
            logger.warning(f"Autonomous post creation failed: {e}")

    def check_own_comment_replies(self) -> None:
        """Monitor replies to our comments and respond.

        Uses comment-to-post mapping to fetch comment threads,
        find replies to our comments, and generate follow-up replies.
        Only processes new unseen replies to avoid duplicates.

        Performs:
        1. Check if we have any tracked comments
        2. Fetch comments from posts we've commented on (max 3 per cycle)
        3. Find replies to our comments (not seen yet)
        4. Generate follow-up replies via AgencyDirector
        5. Enqueue reply proposals
        6. Track seen replies to avoid reprocessing
        """
        from vibe_core.protocols.moltbook_content import ContentType

        if not self._state.comment_post_map:
            return

        # Get unique post IDs we need to check (max 3 per cycle)
        post_ids = list(set(self._state.comment_post_map.values()))[:3]
        our_comment_ids = set(self._state.comment_post_map.keys())

        for post_id in post_ids:
            try:
                # Fetch comments via service for Guna enforcement + audit
                service = self._actions._ensure_service()
                comments = service.get_comments(post_id, sort="new")
            except Exception as e:
                logger.debug(f"Comment fetch for {post_id} failed: {e}")
                continue

            if not comments:
                continue

            for comment in comments:
                if not isinstance(comment, dict):
                    continue

                parent = comment.get("parent_id", "")
                cid = comment.get("id", "")
                author_data = comment.get("author", {})
                author = author_data.get("name", "unknown") if isinstance(author_data, dict) else "unknown"
                content = comment.get("content", "")

                # Is this a reply to one of our comments?
                if parent in our_comment_ids and cid not in self._state.seen_message_ids:
                    self._state.seen_message_ids.add(cid)

                    # Propose a follow-up reply via Agency Director (I-P-V-O)
                    try:
                        proposal = self._actions._director_propose(
                            content_type="comment",
                            raw_input=content,
                            proposal_type=ContentType.COMMENT.value,
                            post_id=post_id,
                            parent_id=cid,
                            trigger="reply_to_own_comment",
                        )
                        if proposal:
                            self._state.content_queue.enqueue(proposal)
                            self._actions._log_activity(
                                "reply_proposed",
                                {
                                    "post_id": post_id,
                                    "in_reply_to": cid,
                                    "author": author,
                                },
                            )
                            logger.info(f"Reply to our comment queued (post={post_id}, from={author})")
                    except Exception as e:
                        logger.debug(f"Reply proposal failed: {e}")

    def update_profile(self) -> None:
        """Update agent profile with current activity stats.

        Fetches current profile, computes stats from internal state,
        and patches the bio description. Rate-limited to prevent spam.

        Performs:
        1. Check rate limit
        2. Fetch current profile (karma, followers, etc.)
        3. Build activity summary for description
        4. Patch profile via API (description field only)
        5. Track update timestamp
        """
        service = self._actions._ensure_service()
        if not service:
            return

        try:
            profile = service.get_own_profile()
        except Exception as e:
            logger.debug(f"Profile fetch failed: {e}")
            return

        current_karma = profile.get("karma", 0) if isinstance(profile, dict) else 0
        follower_count = profile.get("follower_count", 0) if isinstance(profile, dict) else 0
        following_count = profile.get("following_count", 0) if isinstance(profile, dict) else 0

        # Build activity summary for bio
        description = (
            f"{self._state.agent_name} · Autonomous agent · "
            f"{current_karma} karma · "
            f"{follower_count} followers · {following_count} following · "
            f"{len(self._state.subscribed_submolts)} submolts"
        )

        try:
            service.update_profile(description=description)
            self._actions._record_rate_limit("profile_update")
            self._state.last_profile_heartbeat = self._actions._heartbeat_count
            self._actions._emit_event(
                "PROFILE_UPDATED",
                "Profile refreshed with stats",
                {
                    "karma": current_karma,
                    "followers": follower_count,
                    "following": following_count,
                },
            )
            logger.info(f"Profile updated: {current_karma} karma, {follower_count} followers")
        except Exception as e:
            logger.warning(f"Profile update failed: {e}")
