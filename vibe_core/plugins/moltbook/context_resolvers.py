"""
Moltbook PromptContext Resolvers — Dynamic context injection for LLM prompts.
=============================================================================

5 resolvers registered in PromptContext at boot.
Each reads state and returns a human-readable string for LLM context.

Extracted from plugin_main.py for single-responsibility.
"""

import json
import logging
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from vibe_core.plugins.moltbook.state import MoltbookState

logger = logging.getLogger("MOLTBOOK.CONTEXT")


def register_all(state: "MoltbookState") -> None:
    """Register all 5 moltbook context resolvers in PromptContext."""
    try:
        from vibe_core.runtime.prompt_context import get_prompt_context

        ctx = get_prompt_context()
        ctx.register("moltbook_context", lambda: resolve_moltbook_context(state))
        ctx.register("moltbook_engagement_trends", resolve_engagement_trends)
        ctx.register("moltbook_active_submolts", lambda: resolve_active_submolts(state))
        ctx.register("moltbook_queue_depth", lambda: resolve_queue_depth(state))
        ctx.register("moltbook_recent_content", lambda: resolve_recent_content(state))
        logger.info("moltbook_context (5 resolvers) registered in PromptContext")
    except Exception as e:
        logger.warning(f"PromptContext registration failed: {e}")


def resolve_moltbook_context(state: "MoltbookState") -> str:
    """Resolver for moltbook_context: feed state, community, operations."""
    parts: List[str] = []

    mode = "LIVE" if not state.offline_mode else "OFFLINE"
    parts.append(f"Moltbook [{mode}] — {state.tick_count} ticks")

    if state.content_queue:
        stats = state.content_queue.stats
        queued = stats.get("queued", 0)
        drained = stats.get("total_drained", 0)
        if queued or drained:
            parts.append(f"Content queue: {queued} queued, {drained} drained")

    followed = len(state.followed_agents)
    submolts = len(state.subscribed_submolts)
    threads = len(state.comment_post_map)
    if followed or submolts or threads:
        parts.append(f"Social: {followed} followed, {submolts} submolts, {threads} threads")

    seen_msgs = len(state.seen_message_ids)
    seen_posts = len(state.seen_post_ids)
    if seen_msgs or seen_posts:
        parts.append(f"Seen: {seen_msgs} messages, {seen_posts} posts")

    if state.last_heartbeat_error:
        parts.append(f"Last error: {state.last_heartbeat_error}")
    elif state.listener_wired:
        parts.append("Health: OK (Mahamantra listener wired)")

    return "\n".join(parts)


def resolve_engagement_trends() -> str:
    """Recent engagement trends from FeedbackProtocol stats."""
    try:
        from vibe_core.protocols.feedback import get_feedback_safe

        stats = get_feedback_safe().get_stats()
        return f"Success rate: {stats.success_rate:.0%}, Total: {stats.total_signals}, Failures: {stats.total_failures}"
    except Exception as e:
        logger.warning(f"Engagement trends unavailable: {e}")
        return ""


def resolve_active_submolts(state: "MoltbookState") -> str:
    """Currently subscribed submolts."""
    if not state.subscribed_submolts:
        return "none"
    return ", ".join(sorted(state.subscribed_submolts))


def resolve_queue_depth(state: "MoltbookState") -> str:
    """Current content queue depth + stats."""
    if not state.content_queue:
        return "0"
    stats = state.content_queue.stats
    return (
        f"{stats.get('queued', 0)} pending, "
        f"{stats.get('total_drained', 0)} drained, "
        f"{stats.get('total_dropped', 0)} dropped"
    )


def resolve_recent_content(state: "MoltbookState") -> str:
    """Last 3 generated content pieces from activity log (avoid repetition)."""
    if not state.activity_log_path or not state.activity_log_path.exists():
        return ""
    try:
        lines = state.activity_log_path.read_text().strip().split("\n")
        recent: List[str] = []
        for line in reversed(lines):
            if len(recent) >= 3:
                break
            try:
                entry = json.loads(line)
                if entry.get("event") in ("post_created", "comment_posted", "dm_sent"):
                    data = entry.get("data", {})
                    recent.append(f"{entry['event']}: {data.get('title', data.get('post_id', ''))[:60]}")
            except Exception as e:
                logger.warning(f"Activity log entry malformed: {e}")
                continue
        return " | ".join(recent) if recent else ""
    except Exception as e:
        logger.warning(f"Activity log read failed: {e}")
        return ""
