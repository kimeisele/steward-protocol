"""EngagementTracker — poll own content for metrics, adjust intervals.

Extracted from MoltbookPlugin._track_engagement(), _adjust_intervals(),
_monitor_queue_health().
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Dict, Optional, Set

from vibe_core.mahamantra.substrate.core.seed import (
    COSMIC_FRAME,
    HALVES,
    LILA,
    MAHAJANA_COUNT,
    PANCHA,
    QUARTERS,
    SHARANAGATI,
)

if TYPE_CHECKING:
    from vibe_core.cartridges.agent_city.moltbook.core.memory import EventLog
    from vibe_core.cartridges.agent_city.moltbook.core.strategy import MoltbookStrategyPlanner
    from vibe_core.protocols.moltbook import MoltbookProtocol

logger = logging.getLogger("MOLTBOOK_ENGAGEMENT")


def _safe_int(val: object) -> int:
    """Convert API value to int, returning 0 on failure."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


class EngagementTracker:
    """Poll own posts/comments for engagement metrics, adjust intervals.

    Args:
        log_activity: Callable(event_type, payload) for JSONL audit log.
        bank: Optional CivicBank instance for credit rewards.
        agent_id: Agent name for credit transactions.
    """

    # Interval bounds (min/max heartbeats) — SEED-derived
    _MIN_FEED_INTERVAL = HALVES  # 2 halves
    _MAX_FEED_INTERVAL = MAHAJANA_COUNT  # 12 authorities
    _MIN_POST_INTERVAL = MAHAJANA_COUNT  # 12 authorities
    _MAX_POST_INTERVAL = LILA  # 48 Chaitanya's manifest

    # Threshold constants for _adjust_intervals — COSMIC_FRAME integer arithmetic
    _HIGH_CF = COSMIC_FRAME * QUARTERS // PANCHA  # 17280 ≈ 0.8
    _LOW_FEED_CF = COSMIC_FRAME // SHARANAGATI  # 3600 ≈ 0.167 ≈ 0.2
    _LOW_POST_CF = COSMIC_FRAME * SHARANAGATI // (QUARTERS * PANCHA)  # 6480 ≈ 0.3

    # Credit rewards per engagement type — sustainable economy
    _REWARD_PER_UPVOTE = 1
    _REWARD_PER_REPLY = 2

    def __init__(
        self,
        log_activity: Callable,
        bank: Optional[object] = None,
        agent_id: str = "moltbook",
    ):
        self._log_activity = log_activity
        self._bank = bank
        self._agent_id = agent_id
        # Track already-rewarded engagement to prevent double-counting
        self._rewarded_posts: Dict[str, int] = {}  # post_id → last rewarded net_score
        self._rewarded_comments: Dict[str, int] = {}  # comment_id → last rewarded net_score

    def track(
        self,
        service: MoltbookProtocol,
        own_post_ids: Dict[str, Dict[str, object]],
        own_comment_ids: Set[str],
        comment_post_map: Dict[str, str],
        event_log: EventLog,
        strategy_planner: Optional[MoltbookStrategyPlanner],
    ) -> None:
        """Poll own posts/comments for engagement metrics (upvotes, replies).

        Feeds results into:
          - EventLog (engagement_metric event for persistence)
          - FeedbackProtocol (signal_success/failure for adaptive learning)
        """
        if not service or not own_post_ids:
            return

        from vibe_core.protocols.feedback import get_feedback_safe

        feedback = get_feedback_safe()

        # Poll up to 5 most recent own posts
        recent_posts = sorted(
            own_post_ids.items(),
            key=lambda kv: kv[1].get("created_at", 0),
            reverse=True,
        )[:5]

        # Cache fetched post data to avoid double API calls
        fetched_posts: Dict[str, dict] = {}

        for post_id, meta in recent_posts:
            try:
                post = service.get_post(post_id)
            except Exception as e:
                logger.warning(f"Engagement poll failed for {post_id}: {e}")
                continue

            if not isinstance(post, dict):
                continue

            fetched_posts[post_id] = post

            upvotes = _safe_int(post.get("upvotes", 0))
            downvotes = _safe_int(post.get("downvotes", 0))
            replies = _safe_int(post.get("comment_count", 0))
            submolt = str(meta.get("submolt", ""))
            net_score = upvotes - downvotes

            event_log.record_engagement_metric(
                content_id=post_id,
                content_type="post",
                upvotes=upvotes,
                downvotes=downvotes,
                replies=replies,
                submolt=submolt,
            )

            # Update own_post_ids with live engagement data (for SravanamCheck + zero-engagement-streak)
            if isinstance(meta, dict):
                meta["upvotes"] = upvotes
                meta["replies"] = replies

            ctx = {"submolt": submolt, "upvotes": upvotes, "replies": replies, "net_score": net_score}
            if net_score > 0 or replies > 0:
                feedback.signal_success("moltbook.post", ctx, duration_ms=0.0)
                self._reward_engagement(post_id, upvotes + replies, "post")
            elif net_score < 0:
                feedback.signal_failure("moltbook.post", "negative_engagement", ctx, duration_ms=0.0)

        # Poll up to 5 own comments for engagement
        comment_ids = list(own_comment_ids)[-5:]
        for comment_id in comment_ids:
            post_id = comment_post_map.get(comment_id, "")
            if not post_id:
                continue
            try:
                comments = service.get_comments(post_id, sort="new")
            except Exception as e:
                logger.warning(f"Comment fetch for engagement tracking failed: {e}")
                continue
            for c in comments or []:
                if not isinstance(c, dict):
                    continue
                if c.get("id") == comment_id:
                    upvotes = _safe_int(c.get("upvotes", 0))
                    downvotes = _safe_int(c.get("downvotes", 0))
                    net_score = upvotes - downvotes
                    event_log.record_engagement_metric(
                        content_id=comment_id,
                        content_type="comment",
                        upvotes=upvotes,
                        downvotes=downvotes,
                        replies=0,
                    )
                    ctx = {"upvotes": upvotes, "net_score": net_score}
                    if net_score > 0:
                        feedback.signal_success("moltbook.comment", ctx, duration_ms=0.0)
                        self._reward_engagement(comment_id, upvotes, "comment")
                    elif net_score < 0:
                        feedback.signal_failure("moltbook.comment", "negative_engagement", ctx, duration_ms=0.0)
                    break

        # Feed cached engagement data to strategy planner (no extra API calls)
        if strategy_planner:
            for post_id, meta in recent_posts:
                post = fetched_posts.get(post_id)
                if post is not None:
                    try:
                        strategy_planner.update_from_engagement(
                            {
                                "post_id": post_id,
                                "upvotes": _safe_int(post.get("upvotes", 0)),
                                "reply_count": _safe_int(post.get("comment_count", 0)),
                                "topic": str(meta.get("title", "")),
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Strategy planner update failed for {post_id}: {e}")

        logger.debug(f"Engagement tracked: {len(recent_posts)} posts, {len(comment_ids)} comments")

    def _reward_engagement(self, content_id: str, total_score: int, content_type: str) -> None:
        """Credit reward for engagement received on own content.

        Only rewards the DELTA since last check — prevents double-counting.
        1 credit per upvote received, 2 per reply received.
        """
        if self._bank is None or total_score <= 0:
            return
        tracker = self._rewarded_posts if content_type == "post" else self._rewarded_comments
        prev = tracker.get(content_id, 0)
        delta = total_score - prev
        if delta <= 0:
            return
        tracker[content_id] = total_score
        reward = delta * self._REWARD_PER_UPVOTE
        try:
            self._bank.transfer(
                "ENGAGEMENT_REWARD",
                self._agent_id,
                reward,
                f"moltbook_{content_type}_engagement",
                service_type="reward",
            )
            logger.info(f"Credit reward: +{reward} for {content_type} {content_id} (delta={delta})")
        except Exception as e:
            logger.warning(f"Credit reward failed: {e}")

    def adjust_intervals(
        self,
        feed_interval: int,
        post_interval: int,
    ) -> tuple:
        """Adjust heartbeat intervals based on feedback success rate.

        Returns (new_feed_interval, new_post_interval).
        """
        from vibe_core.protocols.feedback import get_feedback_safe

        stats = get_feedback_safe().get_stats()

        if stats.total_signals < PANCHA:
            return feed_interval, post_interval  # Cold start: not enough data

        rate_cf = int(stats.success_rate * COSMIC_FRAME)

        # Linear interpolation for feed interval (COSMIC_FRAME integer arithmetic)
        if rate_cf >= self._HIGH_CF:
            new_feed = self._MIN_FEED_INTERVAL
        elif rate_cf <= self._LOW_FEED_CF:
            new_feed = self._MAX_FEED_INTERVAL
        else:
            span = self._HIGH_CF - self._LOW_FEED_CF
            new_feed = (
                self._MAX_FEED_INTERVAL
                - (rate_cf - self._LOW_FEED_CF) * (self._MAX_FEED_INTERVAL - self._MIN_FEED_INTERVAL) // span
            )

        # Linear interpolation for post interval (COSMIC_FRAME integer arithmetic)
        if rate_cf >= self._HIGH_CF:
            new_post = self._MIN_POST_INTERVAL
        elif rate_cf <= self._LOW_POST_CF:
            new_post = self._MAX_POST_INTERVAL
        else:
            span = self._HIGH_CF - self._LOW_POST_CF
            new_post = (
                self._MAX_POST_INTERVAL
                - (rate_cf - self._LOW_POST_CF) * (self._MAX_POST_INTERVAL - self._MIN_POST_INTERVAL) // span
            )

        new_feed = max(self._MIN_FEED_INTERVAL, min(self._MAX_FEED_INTERVAL, new_feed))
        new_post = max(self._MIN_POST_INTERVAL, min(self._MAX_POST_INTERVAL, new_post))

        if new_feed != feed_interval or new_post != post_interval:
            self._log_activity(
                "intervals_adjusted",
                {
                    "feed": new_feed,
                    "post": new_post,
                    "success_rate_cf": rate_cf,
                    "total_signals": stats.total_signals,
                },
            )
            logger.info(
                f"Intervals adjusted: feed={feed_interval}→{new_feed}, "
                f"post={post_interval}→{new_post} (rate_cf={rate_cf}/{COSMIC_FRAME}, signals={stats.total_signals})"
            )

        return new_feed, new_post
