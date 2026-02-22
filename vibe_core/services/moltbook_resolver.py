"""
MOLTBOOK RESOLVER — IntentResolver for Moltbook I/O
=====================================================

Implements the MantraKernel IntentResolver protocol.
Moltbook operations are I/O side-effects that consume VM output.

ARCHITECTURE:
    MantraIntent(READ, "moltbook/feed")     → resolver reads feed
    MantraIntent(READ, "moltbook/dm/check") → resolver checks DMs
    MantraIntent(READ, "moltbook/search")   → resolver searches
    MantraIntent(WRITE, "moltbook/post")    → resolver creates post
    MantraIntent(WRITE, "moltbook/dm/send") → resolver sends DM
    MantraIntent(OBSERVE, "moltbook/profile") → resolver reads profile

All operations go through:
    kernel.resolve(intent) → MoltbookResolver.resolve() → HTTP client → IntentResult

The Singularity listener queues intents on downbeat.
The kernel processes the queue. The resolver handles I/O.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Optional, Union

from vibe_core.mahamantra import (
    IntentResult,
    IntentStatus,
    IntentType,
    MantraIntent,
)

if TYPE_CHECKING:
    from vibe_core.mahamantra.adapters.moltbook import MoltbookClient

logger = logging.getLogger("MOLTBOOK_RESOLVER")

# =============================================================================
# MOLTBOOK TARGET PREFIXES
# =============================================================================

MOLTBOOK_PREFIX = "moltbook/"

# READ targets
TARGET_FEED = "moltbook/feed"
TARGET_DM_CHECK = "moltbook/dm/check"
TARGET_DM_CONVERSATIONS = "moltbook/dm/conversations"
TARGET_DM_MESSAGES = "moltbook/dm/messages"
TARGET_DM_REQUESTS = "moltbook/dm/requests"
TARGET_SEARCH = "moltbook/search"
TARGET_POST = "moltbook/post"
TARGET_COMMENTS = "moltbook/comments"
TARGET_PROFILE = "moltbook/profile"
TARGET_OWN_PROFILE = "moltbook/profile/me"

# WRITE targets
TARGET_CREATE_POST = "moltbook/post/create"
TARGET_CREATE_COMMENT = "moltbook/comment/create"
TARGET_SEND_DM = "moltbook/dm/send"
TARGET_SEND_DM_REQUEST = "moltbook/dm/request"
TARGET_APPROVE_DM = "moltbook/dm/approve"
TARGET_REJECT_DM = "moltbook/dm/reject"
TARGET_UPVOTE = "moltbook/upvote"
TARGET_DOWNVOTE = "moltbook/downvote"
TARGET_FOLLOW = "moltbook/follow"
TARGET_UNFOLLOW = "moltbook/unfollow"
TARGET_SUBSCRIBE = "moltbook/subscribe"
TARGET_UNSUBSCRIBE = "moltbook/unsubscribe"
TARGET_UPDATE_PROFILE = "moltbook/profile/update"

# Intent types this resolver handles
HANDLED_TYPES = {IntentType.READ, IntentType.WRITE, IntentType.OBSERVE, IntentType.SYNC}


class MoltbookResolver:
    """
    IntentResolver for Moltbook operations.

    Handles READ (feed, search, DMs), WRITE (post, comment, DM, vote),
    OBSERVE (profile), and SYNC (heartbeat check).

    Uses MoltbookClient for HTTP I/O. Rate limiting is in the client.
    """

    def __init__(self, client: "MoltbookClient") -> None:
        self._client = client

    def can_resolve(self, intent: MantraIntent[object]) -> bool:
        """Can this resolver handle this intent?"""
        if intent.type not in HANDLED_TYPES:
            return False
        return intent.target.startswith(MOLTBOOK_PREFIX)

    def resolve(self, intent: MantraIntent[object]) -> IntentResult[object]:
        """Resolve a Moltbook intent via HTTP client."""
        target = intent.target
        params = intent.params

        try:
            result = self._dispatch(target, params)
            return IntentResult(
                intent=intent,
                status=IntentStatus.RESOLVED,
                value=result,
                resolved_by=intent.guardian,
            )
        except Exception as exc:
            logger.warning("Moltbook resolve failed for %s: %s", target, exc)
            return IntentResult(
                intent=intent,
                status=IntentStatus.FAILED,
                error=str(exc),
                resolved_by=intent.guardian,
            )

    def _dispatch(self, target: str, params: Dict[str, Union[str, int, bool, None]]) -> object:
        """Dispatch to the correct client method based on target."""
        from vibe_core.mahamantra import run_async

        # --- READ operations ---
        if target == TARGET_FEED:
            sort = str(params.get("sort", "hot"))
            limit = int(params.get("limit", 25))
            return run_async(self._client.get_feed(sort=sort, limit=limit))

        if target == TARGET_DM_CHECK:
            return self._client.sync_check_heartbeat()

        if target == TARGET_DM_CONVERSATIONS:
            return self._client.sync_get_dm_conversations()

        if target == TARGET_DM_MESSAGES:
            conv_id = str(params.get("conversation_id", ""))
            if not conv_id:
                raise ValueError("conversation_id required for dm/messages")
            return self._client.sync_get_dm_messages(conv_id)

        if target == TARGET_DM_REQUESTS:
            return run_async(self._client.get_dm_requests())

        if target == TARGET_SEARCH:
            query = str(params.get("query", ""))
            limit = int(params.get("limit", 25))
            if not query:
                raise ValueError("query required for search")
            return run_async(self._client.semantic_search(query, limit=limit))

        if target == TARGET_POST:
            post_id = str(params.get("post_id", ""))
            if not post_id:
                raise ValueError("post_id required")
            return run_async(self._client.get_post(post_id))

        if target == TARGET_COMMENTS:
            post_id = str(params.get("post_id", ""))
            if not post_id:
                raise ValueError("post_id required for comments")
            return run_async(self._client.get_comments(post_id))

        if target == TARGET_OWN_PROFILE:
            return run_async(self._client.get_own_profile())

        if target == TARGET_PROFILE:
            name = str(params.get("name", ""))
            if not name:
                raise ValueError("name required for profile")
            return run_async(self._client.get_profile(name))

        # --- WRITE operations ---
        if target == TARGET_CREATE_POST:
            title = str(params.get("title", ""))
            content = str(params.get("content", ""))
            submolt = str(params.get("submolt", "")) or None
            if not title or not content:
                raise ValueError("title and content required for post creation")
            return self._client.sync_create_post(title, content, submolt)

        if target == TARGET_CREATE_COMMENT:
            post_id = str(params.get("post_id", ""))
            content = str(params.get("content", ""))
            if not post_id or not content:
                raise ValueError("post_id and content required for comment")
            return run_async(self._client.comment_with_verification(post_id, content))

        if target == TARGET_SEND_DM:
            conv_id = str(params.get("conversation_id", ""))
            content = str(params.get("content", ""))
            if not conv_id or not content:
                raise ValueError("conversation_id and content required for DM")
            return self._client.sync_send_dm(conv_id, content)

        if target == TARGET_UPVOTE:
            post_id = str(params.get("post_id", ""))
            if not post_id:
                raise ValueError("post_id required for upvote")
            return run_async(self._client.upvote(post_id))

        if target == TARGET_DOWNVOTE:
            post_id = str(params.get("post_id", ""))
            if not post_id:
                raise ValueError("post_id required for downvote")
            return run_async(self._client.downvote(post_id))

        if target == TARGET_FOLLOW:
            name = str(params.get("name", ""))
            if not name:
                raise ValueError("name required for follow")
            return run_async(self._client.follow_agent(name))

        if target == TARGET_UNFOLLOW:
            name = str(params.get("name", ""))
            if not name:
                raise ValueError("name required for unfollow")
            return run_async(self._client.unfollow_agent(name))

        if target == TARGET_SEND_DM_REQUEST:
            to_agent = str(params.get("to_agent", ""))
            message = str(params.get("message", ""))
            if not to_agent:
                raise ValueError("to_agent required for DM request")
            return run_async(self._client.send_dm_request(to_agent, message))

        if target == TARGET_APPROVE_DM:
            request_id = str(params.get("request_id", ""))
            if not request_id:
                raise ValueError("request_id required for DM approve")
            return run_async(self._client.approve_dm_request(request_id))

        if target == TARGET_REJECT_DM:
            request_id = str(params.get("request_id", ""))
            block = bool(params.get("block", False))
            if not request_id:
                raise ValueError("request_id required for DM reject")
            return run_async(self._client.reject_dm_request(request_id, block))

        if target == TARGET_SUBSCRIBE:
            submolt = str(params.get("submolt", ""))
            if not submolt:
                raise ValueError("submolt required for subscribe")
            return run_async(self._client.subscribe_submolt(submolt))

        if target == TARGET_UNSUBSCRIBE:
            submolt = str(params.get("submolt", ""))
            if not submolt:
                raise ValueError("submolt required for unsubscribe")
            return run_async(self._client.unsubscribe_submolt(submolt))

        if target == TARGET_UPDATE_PROFILE:
            description = params.get("description")
            metadata = params.get("metadata")
            desc_str = str(description) if description is not None else None
            meta_dict = dict(metadata) if isinstance(metadata, dict) else None
            return run_async(self._client.update_profile(desc_str, meta_dict))

        raise ValueError(f"Unknown moltbook target: {target}")


# =============================================================================
# SINGULARITY LISTENER — Queues intents on downbeat
# =============================================================================


def create_moltbook_listener(client: "MoltbookClient") -> callable:
    """
    Create a Singularity tick listener that queues Moltbook intents.

    On every downbeat (position 0), queues a DM check intent.
    The MantraKernel processes the queue and the resolver handles I/O.

    Usage:
        from vibe_core.mahamantra import mahamantra, get_kernel

        listener = create_moltbook_listener(client)
        mahamantra.register_listener(listener)
    """

    def on_tick(tick_state: dict) -> None:
        from vibe_core.mahamantra import IntentPriority, get_kernel

        # Gate on downbeat
        if isinstance(tick_state, dict):
            is_downbeat = tick_state.get("is_downbeat", False)
        else:
            is_downbeat = getattr(tick_state, "is_downbeat", False)

        if not is_downbeat:
            return

        kernel = get_kernel()

        # Queue DM check on every downbeat (~4 seconds)
        kernel.queue(
            MantraIntent(
                type=IntentType.SYNC,
                target=TARGET_DM_CHECK,
                params={},
                priority=IntentPriority.NORMAL,
                requester="moltbook_listener",
            )
        )

    return on_tick


# =============================================================================
# BOOT — Wire everything together
# =============================================================================


def boot_moltbook(api_key: str = "", offline: bool = False) -> MoltbookResolver:
    """
    Boot the Moltbook integration correctly.

    1. Creates HTTP client
    2. Creates resolver
    3. Registers resolver with MantraKernel for all handled intent types
    4. Creates and registers Singularity listener

    Returns the resolver for direct access if needed.
    """
    from vibe_core.mahamantra import get_kernel
    from vibe_core.mahamantra.adapters.moltbook import MoltbookClient

    client = MoltbookClient(api_key=api_key, offline_mode=offline)
    resolver = MoltbookResolver(client)
    kernel = get_kernel()

    # Register for all handled intent types
    for intent_type in HANDLED_TYPES:
        kernel.register_resolver(intent_type, resolver)

    logger.info("Moltbook resolver registered with MantraKernel for %s", [t.value for t in HANDLED_TYPES])

    # Register tick listener via Lotus facade
    try:
        from vibe_core.mahamantra import mahamantra

        listener = create_moltbook_listener(client)
        mahamantra.register_listener(listener)
        logger.info("Moltbook listener registered via Lotus facade")
    except Exception as e:
        logger.warning("Could not register listener: %s", e)

    return resolver
