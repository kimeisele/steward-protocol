"""ContentDrainer — execute queued content proposals through MoltbookService.

Extracted from MoltbookPlugin._drain_content_queue() and related drain handlers.

Owns: rate-limit state, drain dispatch table, retry logic with exponential backoff.
Owns: credit-gated posting via CivicBank (optional — degrades to no-cost when unavailable).
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set

from vibe_core.protocols.moltbook_content import (
    ContentProposal,
    ContentQueue,
    ContentType,
)
from vibe_core.mahamantra.substrate.core.seed import HARE_COUNT

if TYPE_CHECKING:
    from vibe_core.protocols.moltbook import MoltbookProtocol

logger = logging.getLogger("MOLTBOOK_DRAINER")

# Credit costs per content type (from Agent City economic model)
_CREDIT_COSTS: Dict[str, int] = {
    ContentType.POST.value: 5,
    ContentType.COMMENT.value: 2,
    ContentType.DM_REPLY.value: 1,
    ContentType.DM_INITIATE.value: 1,
    ContentType.VOTE.value: 0,      # Free — social grooming
    ContentType.FOLLOW.value: 0,    # Free — social grooming
    ContentType.SUBSCRIBE.value: 0, # Free — discovery
}


class ContentDrainer:
    """Execute queued content proposals through MoltbookService.

    Owns rate-limit state and drain dispatch. Does not own the queue itself.

    Args:
        service_getter: Callable returning MoltbookService (lazy).
        log_activity: Callable(event_type, payload) for JSONL audit log.
        broadcast_to_agora: Callable(content_type, content, metadata) for federation.
        emit_event: Callable(event_type_name, message, data) for EventBus.
    """

    # Rate limits (from platform.yaml moltbook-002-rate-limit)
    _POST_INTERVAL_SEC = 30 * 60  # 1 post per 30 minutes
    _COMMENT_LIMIT_PER_HOUR = 30  # API allows 50, stay conservative
    _DM_LIMIT_PER_HOUR = 30  # 30 DM operations per hour
    _MAX_PROPOSAL_RETRIES = 2

    def __init__(
        self,
        service_getter: Callable,
        log_activity: Callable,
        broadcast_to_agora: Callable,
        emit_event: Callable,
        *,
        own_post_ids: Dict[str, Dict[str, object]],
        own_comment_ids: Set[str],
        comment_post_map: Dict[str, str],
        followed_agents: Set[str],
        subscribed_submolts: Set[str],
        bank: Optional[Any] = None,
        agent_id: str = "moltbook",
    ):
        self._get_service = service_getter
        self._log_activity = log_activity
        self._broadcast_to_agora = broadcast_to_agora
        self._emit_event = emit_event
        self._bank = bank
        self._agent_id = agent_id
        # Shared refs from plugin (not copies)
        self._own_post_ids = own_post_ids
        self._own_comment_ids = own_comment_ids
        self._comment_post_map = comment_post_map
        self._followed_agents = followed_agents
        self._subscribed_submolts = subscribed_submolts
        # Rate-limit state — restore from persisted own_post_ids
        self._last_post_ts: float = 0.0
        if own_post_ids:
            latest = max(
                (v.get("created_at", 0.0) for v in own_post_ids.values()
                 if isinstance(v, dict)),
                default=0.0,
            )
            if latest > 0:
                self._last_post_ts = latest
                logger.info(f"Rate limit restored: last post {time.time() - latest:.0f}s ago")
        self._comment_timestamps: List[float] = []
        self._dm_timestamps: List[float] = []
        # Queue health monitoring
        self._last_overflow_log: int = 0

    # Drain dispatch table: ContentType.value → handler method name
    _DRAIN_DISPATCH = {
        ContentType.DM_REPLY.value: "_drain_dm_reply",
        ContentType.DM_INITIATE.value: "_drain_dm_initiate",
        ContentType.POST.value: "_drain_post",
        ContentType.COMMENT.value: "_drain_comment",
        ContentType.VOTE.value: "_drain_vote",
        ContentType.FOLLOW.value: "_drain_follow",
        ContentType.SUBSCRIBE.value: "_drain_subscribe",
    }

    def check_rate_limit(self, content_type: str) -> bool:
        """Check if content type is within rate limits. Returns True if OK."""
        now = time.time()
        hour_ago = now - 3600

        if content_type == "post":
            if now - self._last_post_ts < self._POST_INTERVAL_SEC:
                logger.info(f"Rate limit: post too soon ({now - self._last_post_ts:.0f}s < {self._POST_INTERVAL_SEC}s)")
                return False
        elif content_type == "comment":
            self._comment_timestamps = [t for t in self._comment_timestamps if t > hour_ago]
            if len(self._comment_timestamps) >= self._COMMENT_LIMIT_PER_HOUR:
                logger.info(f"Rate limit: {len(self._comment_timestamps)} comments in last hour")
                return False
        elif content_type in ("dm_reply", "dm_initiate"):
            self._dm_timestamps = [t for t in self._dm_timestamps if t > hour_ago]
            if len(self._dm_timestamps) >= self._DM_LIMIT_PER_HOUR:
                logger.info(f"Rate limit: {len(self._dm_timestamps)} DMs in last hour")
                return False
        return True

    def check_credits(self, content_type: str) -> bool:
        """Check if agent has enough credits for this content type. Returns True if OK."""
        if self._bank is None:
            return True  # No bank = no cost (standalone without economy)
        cost = _CREDIT_COSTS.get(content_type, 0)
        if cost == 0:
            return True
        try:
            balance = self._bank.get_balance(self._agent_id)
            if balance < cost:
                logger.info(f"Credit gate: {balance} < {cost} for {content_type}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Credit check failed: {e}")
            return True  # Fail open — don't block content on bank errors

    def deduct_credits(self, content_type: str) -> None:
        """Deduct credits after successful content publication."""
        if self._bank is None:
            return
        cost = _CREDIT_COSTS.get(content_type, 0)
        if cost == 0:
            return
        try:
            tx_id = self._bank.transfer(
                self._agent_id, "CIVIC", cost,
                f"moltbook_{content_type}",
                service_type="content",
            )
            logger.info(f"Credit deducted: {cost} for {content_type} (tx={tx_id})")
        except Exception as e:
            # Log but don't fail — content already published
            logger.warning(f"Credit deduction failed: {e}")

    def record_rate_limit(self, content_type: str) -> None:
        """Record that a content action was executed (for rate limiting)."""
        now = time.time()
        if content_type == "post":
            self._last_post_ts = now
        elif content_type == "comment":
            self._comment_timestamps.append(now)
        elif content_type in ("dm_reply", "dm_initiate"):
            self._dm_timestamps.append(now)

    def drain(self, queue: ContentQueue, offline_mode: bool) -> None:
        """Execute queued content proposals through MoltbookService.

        Uses dispatch table — no if/elif chains. Failed proposals are
        re-enqueued with exponential backoff: retry 1 → 2s, retry 2 → 4s.
        After _MAX_PROPOSAL_RETRIES, the proposal is dropped and logged.
        Rate limits enforced from platform.yaml (1 post/30min, 10 comments/hour).
        """
        if queue.is_empty:
            return

        # Offline gate: never send content when offline
        if offline_mode:
            return

        service = self._get_service()
        proposals = queue.drain(limit=3)
        failed: List[ContentProposal] = []
        deferred: List[ContentProposal] = []

        from vibe_core.protocols.feedback import get_feedback_safe

        feedback = get_feedback_safe()

        now = time.time()
        for proposal in proposals:
            # Exponential backoff: skip proposals that aren't ready yet
            retry_after = proposal.get("_retry_after", 0.0)
            if retry_after > now:
                deferred.append(proposal)
                continue
            ct = proposal.get("content_type", "")

            # Credit check — defer if insufficient funds
            if not self.check_credits(ct):
                proposal["_retry_after"] = now + 120  # Re-check in 2min
                deferred.append(proposal)
                feedback.signal_partial(
                    f"moltbook.drain.{ct}",
                    "insufficient_credits",
                    {"content_type": ct},
                )
                continue

            # Rate limit check — defer if too soon
            if not self.check_rate_limit(ct):
                proposal["_retry_after"] = now + 60  # Re-check in 60s
                deferred.append(proposal)
                feedback.signal_partial(
                    f"moltbook.drain.{ct}",
                    "rate_limited",
                    {
                        "content_type": ct,
                    },
                )
                continue
            t0 = time.monotonic()
            try:
                handler_name = self._DRAIN_DISPATCH.get(ct)
                if handler_name:
                    getattr(self, handler_name)(service, proposal)
                    self.record_rate_limit(ct)
                    self.deduct_credits(ct)
                    elapsed = (time.monotonic() - t0) * 1000
                    feedback.signal_success(
                        f"moltbook.drain.{ct}",
                        {
                            "content_type": ct,
                            "priority": proposal.get("priority", 0),
                        },
                        duration_ms=elapsed,
                    )
                else:
                    logger.warning(f"Unknown content type in drain queue: {ct}")
            except PermissionError as e:
                logger.warning(f"TAMAS blocked: {e}")
                elapsed = (time.monotonic() - t0) * 1000
                feedback.signal_failure(
                    f"moltbook.drain.{ct}",
                    "tamas_blocked",
                    {
                        "content_type": ct,
                    },
                    duration_ms=elapsed,
                )
                # Permanent failure — do not retry
            except ConnectionError as e:
                # HTTP 429 / rate limit from platform — long backoff
                elapsed = (time.monotonic() - t0) * 1000
                is_429 = "429" in str(e) or "rate" in str(e).lower()
                backoff_secs = 300 if is_429 else 60  # 5min for 429, 1min for other connection errors
                retries = proposal.get("_retries", 0)
                if retries < self._MAX_PROPOSAL_RETRIES:
                    proposal["_retries"] = retries + 1
                    proposal["_retry_after"] = time.time() + backoff_secs
                    failed.append(proposal)
                    feedback.signal_partial(
                        f"moltbook.drain.{ct}",
                        "rate_limited_429" if is_429 else "connection_error",
                        {"content_type": ct, "backoff_secs": backoff_secs},
                    )
                    logger.warning(
                        f"{'429 rate limited' if is_429 else 'Connection error'} ({ct}), backoff {backoff_secs}s: {e}"
                    )
                else:
                    self._log_activity("proposal_dropped", {"type": ct, "error": str(e)[:200]})
                    feedback.signal_failure(
                        f"moltbook.drain.{ct}",
                        "dropped_after_retries",
                        {"content_type": ct, "retries": retries},
                        duration_ms=elapsed,
                    )
                    logger.error(f"Proposal dropped after {retries} retries ({ct}): {e}")
            except Exception as e:
                elapsed = (time.monotonic() - t0) * 1000
                retries = proposal.get("_retries", 0)
                if retries < self._MAX_PROPOSAL_RETRIES:
                    proposal["_retries"] = retries + 1
                    # Exponential backoff: 2^retries seconds (2s, 4s)
                    proposal["_retry_after"] = time.time() + (2 ** proposal["_retries"])
                    failed.append(proposal)
                    feedback.signal_partial(
                        f"moltbook.drain.{ct}",
                        f"retry_{retries + 1}",
                        {
                            "content_type": ct,
                            "retries": retries + 1,
                        },
                    )
                    logger.warning(
                        f"Content execution failed ({ct}), retry {retries + 1}, backoff {2 ** proposal['_retries']}s: {e}"
                    )
                else:
                    self._log_activity("proposal_dropped", {"type": ct, "error": str(e)[:200]})
                    feedback.signal_failure(
                        f"moltbook.drain.{ct}",
                        "dropped_after_retries",
                        {
                            "content_type": ct,
                            "retries": retries,
                        },
                        duration_ms=elapsed,
                    )
                    logger.error(f"Proposal dropped after {retries} retries ({ct}): {e}")

        # Re-enqueue: deferred (not yet ready) + failed (with backoff)
        # Uses requeue() to bypass content dedup — these were already accepted
        for proposal in deferred + failed:
            queue.requeue(proposal)

    def monitor_queue_health(self, queue: ContentQueue, heartbeat_count: int) -> None:
        """Log warning when queue overflows (proposals silently dropped).

        Rate-limited to avoid log spam: max 1 warning per 8 heartbeats.
        """
        stats = queue.stats
        dropped = stats.get("total_dropped", 0)
        queued = stats.get("queued", 0)
        max_size = stats.get("max_size", ContentQueue.DEFAULT_MAX_SIZE)

        if dropped > 0 and (heartbeat_count - self._last_overflow_log) >= HARE_COUNT:
            self._last_overflow_log = heartbeat_count
            logger.warning(
                f"Queue overflow: {dropped} proposals dropped (queue {queued}/{max_size}). "
                f"Enqueued={stats.get('total_enqueued', 0)}, "
                f"Drained={stats.get('total_drained', 0)}"
            )

        # High water mark: queue > 80% full
        if queued > max_size * 0.8:
            logger.info(f"Queue high water: {queued}/{max_size} ({queued * 100 // max_size}% full)")

    # =========================================================================
    # Drain handlers — one per ContentType
    # =========================================================================

    def _drain_dm_reply(self, service: MoltbookProtocol, proposal: ContentProposal) -> None:
        conv_id = proposal.get("conversation_id", "")
        content = proposal.get("content", "")
        if conv_id and content:
            service.send_dm(conv_id, content)
            self._log_activity("dm_sent", {"conversation_id": conv_id})
            logger.info(f"DM reply sent to {conv_id}")

    def _drain_dm_initiate(self, service: MoltbookProtocol, proposal: ContentProposal) -> None:
        to_agent = proposal.get("to_agent", "")
        if to_agent:
            service.approve_dm_request(proposal.get("sender", ""))
            self._log_activity("dm_request_approved", {"agent": to_agent})
            logger.info(f"DM request approved for {to_agent}")

    def _drain_post(self, service: MoltbookProtocol, proposal: ContentProposal) -> None:
        title = proposal.get("title", "")
        content = proposal.get("content", "")
        submolt = proposal.get("submolt")
        if title and content:
            post_result = service.create_post(title, content, submolt)
            post_id = post_result.get("id", "") if isinstance(post_result, dict) else ""
            # Track ALL posts for rate limit persistence — even without API post_id
            track_key = post_id or f"noid_{int(time.time())}"
            self._own_post_ids[track_key] = {
                "submolt": submolt or "",
                "created_at": time.time(),
                "title": title[:80],
            }
            self._log_activity("post_created", {"title": title[:80], "submolt": submolt, "post_id": post_id})
            self._broadcast_to_agora("post", content, {"title": title[:80], "submolt": submolt})
            self._emit_event(
                "BROADCAST",
                f"Post published: {title[:50]}",
                {
                    "content_type": "post",
                    "post_id": post_id,
                    "submolt": submolt or "",
                },
            )
            logger.info(f"Post created: {title[:50]} (id={post_id})")

    def _drain_comment(self, service: MoltbookProtocol, proposal: ContentProposal) -> None:
        post_id = proposal.get("post_id", "")
        content = proposal.get("content", "")
        parent_id = proposal.get("parent_id")
        if post_id and content:
            result = service.comment(post_id, content, parent_id)
            comment_id = result.get("id", "") if isinstance(result, dict) else ""
            if comment_id:
                self._own_comment_ids.add(comment_id)
                self._comment_post_map[comment_id] = post_id
            self._log_activity("comment_posted", {"post_id": post_id, "comment_id": comment_id})
            self._broadcast_to_agora("comment", content, {"post_id": post_id})
            self._emit_event(
                "BROADCAST",
                f"Comment published on {post_id}",
                {
                    "content_type": "comment",
                    "post_id": post_id,
                    "comment_id": comment_id,
                },
            )
            logger.info(f"Comment posted on {post_id}")

    def _drain_vote(self, service: MoltbookProtocol, proposal: ContentProposal) -> None:
        post_id = proposal.get("post_id", "")
        if post_id:
            service.upvote(post_id)
            self._log_activity("upvoted", {"post_id": post_id})
            logger.info(f"Upvoted {post_id}")

    def _drain_follow(self, service: MoltbookProtocol, proposal: ContentProposal) -> None:
        to_agent = proposal.get("to_agent", "")
        if to_agent:
            service.follow(to_agent)
            self._log_activity("followed", {"agent": to_agent})
            logger.info(f"Followed {to_agent}")

    def _drain_subscribe(self, service: MoltbookProtocol, proposal: ContentProposal) -> None:
        submolt = proposal.get("submolt", "")
        if submolt:
            service.subscribe(submolt)
            self._log_activity("subscribed", {"submolt": submolt})
            logger.info(f"Subscribed to {submolt}")
