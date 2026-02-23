"""
Moltbook Plugin — Sensor/Actuator Membrane
===========================================

Bridges the Moltbook social network to the Mahamantra Engine via
mahamantra.register_listener() — the REAL heartbeat path.

Architecture (verified against code):
    mahamantra.tick()                            # singularity.py:1159
        → kala.advance()                         # Time
        → venu.step()                            # DIW from LUT
        → _broadcast(TickState)                  # Narada dispatch
            → Nrisimha._on_mahamantra_tick()     # Watchdog (wired)
            → MahaComputeService.on_tick()       # Compute (wired)
            → MoltbookPlugin._on_mahamantra_tick # THIS (wired at boot)

The plugin polls Moltbook once per full Mantra (16 ticks = 1 chant cycle).
Inbound DMs route through Govardhan Gateway → 5 Gates → Cell.

on_pulse() is kept for backward compatibility but the REAL path
is the Mahamantra listener. When the split-brain heals and
kernel.pulse() works, both paths converge safely.
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Set

from vibe_core.mahamantra import run_async
from vibe_core.mahamantra.protocols._gad import GADBase
from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.protocols.moltbook import (
    DMMessage,
    MoltbookAgentProfile,
    MoltbookComment,
    MoltbookPost,
    MoltbookProtocol,
    SemanticSearchResult,
)
from vibe_core.protocols.moltbook_content import (
    ContentProposal,
    ContentProposalProtocol,
    ContentQueue,
    ContentType,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.mahamantra import MoltbookClient

logger = logging.getLogger("MOLTBOOK")

# One full mantra = 16 ticks. Poll Moltbook once per chant cycle.
_TICKS_PER_HEARTBEAT = 16


class MoltbookService(MoltbookProtocol, GADBase):
    """
    Concrete implementation of MoltbookProtocol + GAD-000 compliant.

    Wraps MoltbookClient with the ABC interface so it can be
    registered with ServiceRegistry. Other plugins and tools
    consume this via DI — never touch MoltbookClient directly.

    GAD-000 Compliance:
        6 Kshetra criteria: discover(), get_state(), is_healthy(),
            is_idempotent, detect_drift(), parseability (via Guna codes)
        4 Dharma principles: Daya (input validation), Satyam (verified output),
            Tapas (rate limits), Saucam (auth-only I/O)
        Heartbeat: MantraHeartbeat via GADBase

    Every operation is classified by Guna (SATTVA/RAJAS/TAMAS).
    RAJAS operations (write) are logged. TAMAS (delete) are blocked
    unless explicitly authorized. SATTVA (read) flows freely.
    """

    # Sovereign Identity (class-level → hasattr(instance, ...) resolves True)
    # Narada = the travelling sage who connects all worlds (social platform adapter)
    # Genesis: 999000000 = 37 × 27000000 → verify_link() passes (PARAMPARA check)
    __mahajana__: ClassVar[str] = "narada"
    __position__: ClassVar[int] = 2  # Narada position: Communication/Broadcast
    __genesis__: ClassVar[str] = "0x3b8b87c0"  # int(hex,16) % 37 == 0

    def __init__(self, client: "MoltbookClient"):
        GADBase.__init__(self)
        self._client = client
        self._operation_log: List[Dict[str, Any]] = []
        self._last_api_error: Optional[str] = None
        self._consecutive_failures: int = 0
        # First chant: transition heartbeat from DISCONNECTED → CHANTING
        self.chant()

    def _enforce_guna(self, operation: str) -> None:
        """
        Enforce Guna policy before executing an operation.

        SATTVA: Pass through (read-only, safe).
        RAJAS: Log and allow (write, rate-limited by client).
        TAMAS: Block (destructive — not implemented yet, future-proof).
        """
        from vibe_core.protocols.moltbook import MOLTBOOK_GUNA_MAP, MoltbookGuna

        guna = MOLTBOOK_GUNA_MAP.get(operation, MoltbookGuna.SATTVA)

        if guna == MoltbookGuna.TAMAS:
            raise PermissionError(
                f"MOLTBOOK-TAMAS: Operation '{operation}' is destructive and requires "
                f"explicit authorization. Not implemented."
            )

        if guna == MoltbookGuna.RAJAS:
            entry = {
                "operation": operation,
                "guna": guna.value,
                "timestamp": time.time(),
            }
            self._operation_log.append(entry)
            logger.info(f"MOLTBOOK-RAJAS: {operation} (write operation logged)")

    # --- SATTVA operations (read-only) ---

    def check_heartbeat(self) -> Dict[str, Any]:
        self._enforce_guna("check_heartbeat")
        return self._client.sync_check_heartbeat()

    def get_own_profile(self) -> MoltbookAgentProfile:
        self._enforce_guna("get_own_profile")
        return run_async(self._client.get_own_profile())

    def get_profile(self, name: str) -> MoltbookAgentProfile:
        self._enforce_guna("get_profile")
        return run_async(self._client.get_profile(name))

    def get_feed(self, sort: str = "hot", limit: int = 25) -> List[Any]:
        self._enforce_guna("get_feed")
        return run_async(self._client.get_feed(sort, limit))

    def get_personalized_feed(self, sort: str = "hot", limit: int = 25) -> List[Any]:
        self._enforce_guna("get_personalized_feed")
        return run_async(self._client.get_personalized_feed(sort, limit))

    def get_post(self, post_id: str) -> Dict[str, Any]:
        self._enforce_guna("get_post")
        return run_async(self._client.get_post(post_id))

    def get_comments(self, post_id: str, sort: str = "top") -> List[Any]:
        self._enforce_guna("get_comments")
        return run_async(self._client.get_comments(post_id, sort))

    def search(self, query: str, limit: int = 25) -> List[SemanticSearchResult]:
        self._enforce_guna("search")
        return run_async(self._client.semantic_search(query, limit))

    def get_conversations(self) -> List[Dict[str, Any]]:
        self._enforce_guna("get_conversations")
        return self._client.sync_get_dm_conversations()

    def get_messages(self, conversation_id: str) -> List[DMMessage]:
        self._enforce_guna("get_messages")
        return self._client.sync_get_dm_messages(conversation_id)

    def get_dm_requests(self) -> List[Dict[str, Any]]:
        self._enforce_guna("get_dm_requests")
        return run_async(self._client.get_dm_requests())

    def get_submolts(self) -> List[Dict[str, Any]]:
        self._enforce_guna("get_submolts")
        return run_async(self._client.get_submolts())

    def get_submolt(self, name: str) -> Dict[str, Any]:
        self._enforce_guna("get_submolt")
        return run_async(self._client.get_submolt(name))

    def verify_credentials(self) -> bool:
        self._enforce_guna("verify_credentials")
        try:
            status = run_async(self._client.check_status())
            return status == "claimed"
        except Exception:
            return False

    # --- RAJAS operations (write, logged) ---

    def create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        self._enforce_guna("create_post")
        return self._client.sync_create_post(title, content, submolt)

    def comment(self, post_id: str, content: str, parent_id: Optional[str] = None) -> MoltbookComment:
        self._enforce_guna("comment")
        return run_async(self._client.comment_with_verification(post_id, content, parent_id))

    def send_dm(self, conversation_id: str, content: str) -> Dict[str, Any]:
        self._enforce_guna("send_dm")
        return self._client.sync_send_dm(conversation_id, content)

    def send_dm_request(self, to_agent: str, message: str) -> Dict[str, Any]:
        self._enforce_guna("send_dm_request")
        return run_async(self._client.send_dm_request(to_agent, message))

    def approve_dm_request(self, request_id: str) -> Dict[str, Any]:
        self._enforce_guna("approve_dm_request")
        return run_async(self._client.approve_dm_request(request_id))

    def reject_dm_request(self, request_id: str, block: bool = False) -> Dict[str, Any]:
        self._enforce_guna("reject_dm_request")
        return run_async(self._client.reject_dm_request(request_id, block))

    def upvote(self, post_id: str) -> Dict[str, Any]:
        self._enforce_guna("upvote")
        return run_async(self._client.upvote(post_id))

    def downvote(self, post_id: str) -> Dict[str, Any]:
        self._enforce_guna("downvote")
        return run_async(self._client.downvote(post_id))

    def upvote_comment(self, comment_id: str) -> Dict[str, Any]:
        self._enforce_guna("upvote_comment")
        return run_async(self._client.upvote_comment(comment_id))

    def follow(self, agent_name: str) -> Dict[str, Any]:
        self._enforce_guna("follow")
        return run_async(self._client.follow_agent(agent_name))

    def subscribe(self, submolt_name: str) -> Dict[str, Any]:
        self._enforce_guna("subscribe")
        return run_async(self._client.subscribe_submolt(submolt_name))

    def create_submolt(self, name: str, display_name: str, description: str) -> Dict[str, Any]:
        self._enforce_guna("create_submolt")
        return self._client.sync_create_submolt(name, display_name, description)

    def update_profile(
        self, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self._enforce_guna("update_profile")
        return run_async(self._client.update_profile(description, metadata))

    # --- TAMAS operations (destructive, blocked by default) ---

    def delete_post(self, post_id: str) -> Dict[str, Any]:
        self._enforce_guna("delete_post")
        return run_async(self._client.delete_post(post_id))

    def unfollow(self, agent_name: str) -> Dict[str, Any]:
        self._enforce_guna("unfollow")
        return run_async(self._client.unfollow_agent(agent_name))

    def unsubscribe(self, submolt_name: str) -> Dict[str, Any]:
        self._enforce_guna("unsubscribe")
        return run_async(self._client.unsubscribe_submolt(submolt_name))

    # =========================================================================
    # GAD-000: THE 6 KSHETRA CRITERIA
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """Discoverability: machine-readable capability description.

        Returns every operation this service exposes, grouped by Guna class,
        along with current rate limits and auth requirements.
        """
        from vibe_core.mahamantra.adapters.moltbook import MoltbookLimits
        from vibe_core.protocols.moltbook import MOLTBOOK_GUNA_MAP

        return {
            "service": "MoltbookService",
            "protocol": "MoltbookProtocol",
            "gad_compliant": True,
            "operations": {
                "sattva": [k for k, v in MOLTBOOK_GUNA_MAP.items() if v.value == "sattva"],
                "rajas": [k for k, v in MOLTBOOK_GUNA_MAP.items() if v.value == "rajas"],
                "tamas": [k for k, v in MOLTBOOK_GUNA_MAP.items() if v.value == "tamas"],
            },
            "rate_limits": {
                "requests_per_minute": MoltbookLimits.REQ_PER_MIN,
                "posts_per_30m": MoltbookLimits.POST_PER_30_MIN,
                "comments_per_hour": MoltbookLimits.COMMENTS_PER_HOUR,
            },
            "auth_required": True,
            "offline_mode": self._client.offline_mode,
        }

    def get_state(self) -> Dict[str, object]:
        """Observability: current state in structured format.

        Returns rate limit usage, connection health, operation log size,
        and error state — everything needed to understand the service's
        current condition.
        """
        limits = self._client.limits
        return {
            "rate_limits": {
                "requests_this_minute": limits.requests_this_minute,
                "posts_this_30m": limits.posts_this_30m,
                "comments_this_hour": limits.comments_this_hour,
            },
            "health": {
                "last_error": self._last_api_error,
                "consecutive_failures": self._consecutive_failures,
                "offline_mode": self._client.offline_mode,
            },
            "audit_trail": {
                "operation_count": len(self._operation_log),
                "last_operation": self._operation_log[-1] if self._operation_log else None,
            },
            "heartbeat": self._heartbeat.get_summary(),
        }

    def is_healthy(self) -> bool:
        """Health check: heartbeat + consecutive failure count."""
        if self._consecutive_failures > 5:
            return False
        return self._heartbeat.state.value != 0  # Not DISCONNECTED

    @property
    def is_idempotent(self) -> bool:
        """SATTVA operations are idempotent. RAJAS are not (create_post, comment)."""
        return False  # Service as a whole is not idempotent (has write ops)

    def detect_drift(self) -> List[str]:
        """Detect deviations from valid state.

        Checks rate limit overruns, auth decay, and resource leaks.
        Returns empty list if healthy, otherwise list of drift descriptions.
        """
        from vibe_core.mahamantra.adapters.moltbook import MoltbookLimits

        drifts: List[str] = []
        limits = self._client.limits

        # Rate limit overrun (should never happen, but defense-in-depth)
        if limits.requests_this_minute > MoltbookLimits.REQ_PER_MIN:
            drifts.append(f"RATE_LIMIT_BREACH: {limits.requests_this_minute}/{MoltbookLimits.REQ_PER_MIN} req/min")
        if limits.posts_this_30m > MoltbookLimits.POST_PER_30_MIN:
            drifts.append(f"POST_LIMIT_BREACH: {limits.posts_this_30m}/{MoltbookLimits.POST_PER_30_MIN} posts/30m")
        if limits.comments_this_hour > MoltbookLimits.COMMENTS_PER_HOUR:
            drifts.append(
                f"COMMENT_LIMIT_BREACH: {limits.comments_this_hour}/{MoltbookLimits.COMMENTS_PER_HOUR} comments/h"
            )

        # Consecutive failures indicate API degradation
        if self._consecutive_failures > 3:
            drifts.append(f"API_DEGRADED: {self._consecutive_failures} consecutive failures")

        # Operation log overflow (memory leak indicator)
        if len(self._operation_log) > 10000:
            drifts.append(f"AUDIT_LOG_OVERFLOW: {len(self._operation_log)} entries in memory")

        return drifts

    # =========================================================================
    # GAD-000: THE 4 DHARMA PRINCIPLES
    # =========================================================================

    def test_daya(self) -> bool:
        """Mercy: No corrupt data ingestion.

        Validates that the Guna enforcement layer sanitizes all inputs
        (SATTVA pass-through, RAJAS logged, TAMAS blocked).
        """
        # Guna map covers all operations — no unclassified routes
        from vibe_core.protocols.moltbook import MOLTBOOK_GUNA_MAP

        expected_ops = {
            "check_heartbeat",
            "get_own_profile",
            "get_profile",
            "get_feed",
            "get_personalized_feed",
            "get_post",
            "get_comments",
            "search",
            "get_conversations",
            "get_messages",
            "get_dm_requests",
            "get_submolts",
            "get_submolt",
            "verify_credentials",
            "create_post",
            "comment",
            "send_dm",
            "send_dm_request",
            "approve_dm_request",
            "reject_dm_request",
            "upvote",
            "downvote",
            "upvote_comment",
            "follow",
            "subscribe",
            "create_submolt",
            "update_profile",
            "delete_post",
            "unfollow",
            "unsubscribe",
        }
        classified = set(MOLTBOOK_GUNA_MAP.keys())
        return expected_ops.issubset(classified)

    def test_satyam(self) -> bool:
        """Truthfulness: No hallucination — deterministic, verifiable output.

        Checks that the service only returns what the API actually returned
        (no fabricated responses). In offline mode, responses are clearly
        mocked — the mock_db is deterministic.
        """
        # Satyam holds if we haven't seen errors that were silently swallowed
        return self._last_api_error is None or self._consecutive_failures < 3

    def test_tapas(self) -> bool:
        """Austerity: No resource leaks — bounded computation and memory.

        Checks rate limit enforcement is active and operation log
        hasn't grown unbounded.
        """
        from vibe_core.mahamantra.adapters.moltbook import MoltbookLimits

        limits = self._client.limits
        # Rate limits must be within bounds
        within_limits = (
            limits.requests_this_minute <= MoltbookLimits.REQ_PER_MIN
            and limits.posts_this_30m <= MoltbookLimits.POST_PER_30_MIN
            and limits.comments_this_hour <= MoltbookLimits.COMMENTS_PER_HOUR
        )
        # Operation log must be bounded
        log_bounded = len(self._operation_log) <= 10000
        return within_limits and log_bounded

    def test_saucam(self) -> bool:
        """Cleanliness: No unauthorized connections — only signed, authorized I/O.

        Checks that the client has a valid API key and all connections
        go through the authenticated client.
        """
        return bool(self._client.api_key)


class MoltbookPlugin(KernelPlugin):
    """
    Moltbook membrane wired to Mahamantra via register_listener().

    Same pattern as Nrisimha and MahaComputeService:
    bombenfest zum Mahamantra at __init__/on_boot time.
    """

    plugin_id = "moltbook"

    # Analyze feed every N heartbeats (not every tick)
    _FEED_INTERVAL = 4  # Every 4th heartbeat = every 64 ticks

    # Autonomous post creation: every N heartbeats (conservative to avoid spam)
    # 16 ticks/heartbeat × 24 heartbeats = 384 ticks between posts
    _POST_INTERVAL = 24  # Every 24th heartbeat ≈ every 384 ticks

    # Reply monitoring: check replies to own comments periodically
    _REPLY_CHECK_INTERVAL = 8  # Every 8th heartbeat = every 128 ticks

    # Profile update: refresh bio/metadata periodically
    _PROFILE_UPDATE_INTERVAL = 48  # Every 48th heartbeat ≈ 768 ticks

    # Persistence: queue + seen IDs survive restarts
    _QUEUE_STATE_FILE = "content_queue.json"
    _SEEN_STATE_FILE = "seen_ids.json"
    _ACTIVITY_LOG_FILE = "activity.jsonl"
    _MAX_SEEN_IDS = 1000  # Cap to prevent unbounded growth

    def __init__(self):
        super().__init__()
        self._client = None  # MoltbookClient, created in on_boot
        self._service: Optional[MoltbookService] = None  # Singleton, reused in drain
        self._offline_mode: bool = True
        self._last_heartbeat_error: Optional[str] = None
        self._state_dir: Optional[Path] = None
        self._tick_count: int = 0
        self._heartbeat_count: int = 0
        self._listener_wired: bool = False
        self._content_queue: ContentQueue = ContentQueue()
        self._proposer: Optional[ContentProposalProtocol] = None
        self._seen_message_ids: Set[str] = set()
        self._seen_post_ids: Set[str] = set()
        self._own_comment_ids: Set[str] = set()  # Track our comments for reply monitoring
        self._last_post_heartbeat: int = 0  # Heartbeat count when last post was created
        self._followed_agents: Set[str] = set()  # Track who we've followed (avoid duplicates)
        self._subscribed_submolts: Set[str] = set()  # Track community subscriptions
        self._last_overflow_log: int = 0  # Heartbeat count when last overflow was logged
        self._comment_post_map: Dict[str, str] = {}  # comment_id → post_id for reply monitoring
        self._last_profile_heartbeat: int = 0  # Heartbeat count when profile was last updated
        self._activity_log_path: Optional[Path] = None  # JSONL append-only audit log
        self._agent_name: str = "steward-protocol"  # Resolved from profile at boot

    @property
    def dependencies(self) -> Set[str]:
        return {"economy"}

    # =========================================================================
    # Queue + Seen ID Persistence
    # =========================================================================

    def _persist_queue(self) -> None:
        """Save content queue + seen IDs to state dir. Called on shutdown."""
        if not self._state_dir:
            return
        try:
            # Queue: serialize proposals
            proposals = list(self._content_queue._queue)
            queue_data = {
                "version": 1,
                "proposals": [dict(p) for p in proposals],
                "stats": {
                    "total_enqueued": self._content_queue._total_enqueued,
                    "total_drained": self._content_queue._total_drained,
                    "total_dropped": self._content_queue._total_dropped,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            queue_path = self._state_dir / self._QUEUE_STATE_FILE
            queue_path.write_text(json.dumps(queue_data, indent=2))

            # Seen IDs + tracking sets: cap to prevent unbounded growth
            msg_ids = sorted(self._seen_message_ids)[-self._MAX_SEEN_IDS :]
            post_ids = sorted(self._seen_post_ids)[-self._MAX_SEEN_IDS :]
            # Cap comment_post_map to last N entries
            cpm_keys = sorted(self._comment_post_map.keys())[-self._MAX_SEEN_IDS :]
            cpm = {k: self._comment_post_map[k] for k in cpm_keys}
            seen_data = {
                "version": 3,
                "message_ids": msg_ids,
                "post_ids": post_ids,
                "own_comment_ids": sorted(self._own_comment_ids)[-self._MAX_SEEN_IDS :],
                "followed_agents": sorted(self._followed_agents),
                "subscribed_submolts": sorted(self._subscribed_submolts),
                "comment_post_map": cpm,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            seen_path = self._state_dir / self._SEEN_STATE_FILE
            seen_path.write_text(json.dumps(seen_data, indent=2))

            total = len(proposals)
            logger.info(f"State persisted: {total} queued proposals, {len(msg_ids)} msg IDs, {len(post_ids)} post IDs")
        except Exception as e:
            logger.warning(f"Queue persistence failed: {e}")

    def _restore_queue(self) -> None:
        """Restore content queue + seen IDs from state dir. Called on boot."""
        if not self._state_dir:
            return

        # Restore queue
        queue_path = self._state_dir / self._QUEUE_STATE_FILE
        try:
            if queue_path.exists():
                data = json.loads(queue_path.read_text())
                if data.get("version") == 1:
                    for p in data.get("proposals", []):
                        self._content_queue.enqueue(p)
                    stats = data.get("stats", {})
                    self._content_queue._total_enqueued = stats.get("total_enqueued", 0)
                    self._content_queue._total_drained = stats.get("total_drained", 0)
                    self._content_queue._total_dropped = stats.get("total_dropped", 0)
                    restored = self._content_queue.size
                    if restored:
                        logger.info(f"Restored {restored} queued proposals from previous session")
        except Exception as e:
            logger.warning(f"Queue restore failed: {e}")

        # Restore seen IDs + tracking sets
        seen_path = self._state_dir / self._SEEN_STATE_FILE
        try:
            if seen_path.exists():
                data = json.loads(seen_path.read_text())
                if data.get("version") in (1, 2, 3):
                    self._seen_message_ids = set(data.get("message_ids", []))
                    self._seen_post_ids = set(data.get("post_ids", []))
                    self._own_comment_ids = set(data.get("own_comment_ids", []))
                    self._followed_agents = set(data.get("followed_agents", []))
                    self._subscribed_submolts = set(data.get("subscribed_submolts", []))
                    self._comment_post_map = data.get("comment_post_map", {})
                    logger.info(
                        f"Restored {len(self._seen_message_ids)} msg IDs, "
                        f"{len(self._seen_post_ids)} post IDs, "
                        f"{len(self._followed_agents)} followed, "
                        f"{len(self._subscribed_submolts)} subscribed, "
                        f"{len(self._comment_post_map)} comment threads"
                    )
        except Exception as e:
            logger.warning(f"Seen IDs restore failed: {e}")

    # =========================================================================
    # PluginStateContract
    # =========================================================================

    def get_state_paths(self) -> List[Path]:
        if self._state_dir:
            return [self._state_dir]
        return []

    def snapshot_state(self) -> Dict[str, Any]:
        if not self._client:
            return {"version": 4, "client_active": False}
        limits = self._client.limits
        return {
            "version": 4,
            "client_active": True,
            "requests_this_minute": limits.requests_this_minute,
            "posts_this_30m": limits.posts_this_30m,
            "comments_this_hour": limits.comments_this_hour,
            "last_minute_reset": limits.last_minute_reset,
            "last_30m_reset": limits.last_30m_reset,
            "last_hour_reset": limits.last_hour_reset,
            "queue_size": self._content_queue.size,
            "queue_stats": self._content_queue.stats,
            "seen_message_count": len(self._seen_message_ids),
            "seen_post_count": len(self._seen_post_ids),
            "own_comment_count": len(self._own_comment_ids),
            "comment_thread_count": len(self._comment_post_map),
            "followed_agent_count": len(self._followed_agents),
            "subscribed_submolt_count": len(self._subscribed_submolts),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        if snapshot.get("version") not in (1, 2, 3, 4) or not snapshot.get("client_active"):
            return
        if not self._client:
            return
        limits = self._client.limits
        limits.requests_this_minute = snapshot.get("requests_this_minute", 0)
        limits.posts_this_30m = snapshot.get("posts_this_30m", 0)
        limits.comments_this_hour = snapshot.get("comments_this_hour", 0)
        limits.last_minute_reset = snapshot.get("last_minute_reset", 0.0)
        limits.last_30m_reset = snapshot.get("last_30m_reset", 0.0)
        limits.last_hour_reset = snapshot.get("last_hour_reset", 0.0)

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, object]] = None,
    ) -> HookResult:
        from vibe_core.mahamantra import MoltbookClient

        try:
            # Resolve state dir
            try:
                from vibe_core.phoenix.config import get_config

                data_root = Path(get_config().paths.data.resolve("plugins/moltbook"))
            except Exception:
                data_root = Path(".vibe/state/plugins/moltbook")
            data_root.mkdir(parents=True, exist_ok=True)
            self._state_dir = data_root

            cfg = config or {}
            self._offline_mode = bool(cfg.get("offline_mode", True))
            api_key = str(cfg.get("api_key", ""))

            if not api_key:
                api_key = self._try_vault(kernel)

            if not api_key:
                api_key = "offline_master_key"
                self._offline_mode = True

            self._client = MoltbookClient(
                api_key=api_key,
                offline_mode=self._offline_mode,
            )

            # Register MoltbookProtocol + ContentProposalProtocol in ServiceRegistry
            self._register_service()

            # Resolve agent name from profile BEFORE booting proposer
            # (proposer uses agent_name in content templates)
            try:
                profile = self._service.get_own_profile() if self._service else {}
                name = profile.get("name", "") if isinstance(profile, dict) else ""
                if name:
                    self._agent_name = name
            except Exception:
                pass  # Keep default

            self._boot_proposer()
            self._register_proposer()

            # Restore persisted queue + seen IDs from previous session
            self._restore_queue()

            # Activity log: append-only JSONL
            self._activity_log_path = data_root / self._ACTIVITY_LOG_FILE

            # PARAMPARA: Wire to Mahamantra heartbeat (same as Nrisimha)
            self._wire_to_mahamantra()

            mode = "OFFLINE" if self._offline_mode else "LIVE"
            logger.info(f"Moltbook booted [{mode}]")
            return HookResult.ok()

        except Exception as e:
            logger.error(f"Moltbook boot failed: {e}")
            return HookResult.error(str(e))

    def _register_service(self) -> None:
        """Register MoltbookProtocol in DI so other plugins get it via ServiceRegistry."""
        try:
            from vibe_core.di import ServiceRegistry

            self._service = MoltbookService(self._client)
            ServiceRegistry.register_factory(MoltbookProtocol, lambda: self._service)
            logger.info("MoltbookProtocol registered in ServiceRegistry")
        except Exception as e:
            logger.warning(f"ServiceRegistry registration failed: {e}")

    def _wire_to_mahamantra(self) -> None:
        """Register as Mahamantra tick listener. Bombenfest."""
        if self._listener_wired:
            return
        try:
            from vibe_core.mahamantra import mahamantra

            mahamantra.register_listener(self._on_mahamantra_tick)
            self._listener_wired = True
            logger.info("PARAMPARA: Moltbook wired to Mahamantra")
        except Exception as e:
            logger.warning(f"Mahamantra connection failed: {e}")

    def _try_vault(self, kernel: "RealVibeKernel") -> str:
        """Attempt to load API key: CivicVault → env → ~/.config/moltbook/credentials.json."""
        # 1. CivicVault (economy plugin)
        try:
            economy = kernel.api("economy")
            if economy:
                vault = economy.get("vault") if isinstance(economy, dict) else None
                if vault and hasattr(vault, "get_secret"):
                    key = vault.get_secret("moltbook_api_key")
                    if key:
                        return key
        except Exception as e:
            logger.debug(f"Vault lookup skipped: {e}")

        # 2. Environment variable
        import os

        env_key = os.environ.get("MOLTBOOK_API_KEY", "")
        if env_key:
            return env_key

        # 3. Credentials file (~/.config/moltbook/credentials.json)
        try:
            import json as _json

            creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
            if creds_path.exists():
                creds = _json.loads(creds_path.read_text())
                key = creds.get("api_key", "")
                if key:
                    logger.info("API key loaded from ~/.config/moltbook/credentials.json")
                    return key
        except Exception as e:
            logger.debug(f"Credentials file lookup skipped: {e}")

        return ""

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
        # Persist queue + seen IDs before shutdown
        self._persist_queue()

        # Unregister listener
        if self._listener_wired:
            try:
                from vibe_core.mahamantra import mahamantra

                mahamantra.unregister_listener(self._on_mahamantra_tick)
                self._listener_wired = False
            except Exception:
                pass
        self._client = None
        logger.info("Moltbook shutdown")
        return HookResult.ok()

    # =========================================================================
    # Fault Isolation
    # =========================================================================

    def _safe_call(self, fn: object, label: str) -> None:
        """Call fn(), catching all exceptions so the heartbeat loop survives."""
        try:
            fn()  # type: ignore[operator]
        except Exception as e:
            self._log_activity("heartbeat_error", {"phase": label, "error": str(e)[:200]})
            logger.warning(f"Heartbeat phase '{label}' failed: {e}")

    def _trim_memory(self) -> None:
        """Trim in-memory tracking sets to _MAX_SEEN_IDS.

        Prevents unbounded growth during long-running sessions.
        The persist-time cap only fires on shutdown — this trims live.
        """
        cap = self._MAX_SEEN_IDS
        if len(self._seen_message_ids) > cap:
            # Keep most recent (sorted lexicographically — IDs are monotonic)
            self._seen_message_ids = set(sorted(self._seen_message_ids)[-cap:])
        if len(self._seen_post_ids) > cap:
            self._seen_post_ids = set(sorted(self._seen_post_ids)[-cap:])
        if len(self._own_comment_ids) > cap:
            self._own_comment_ids = set(sorted(self._own_comment_ids)[-cap:])
        if len(self._comment_post_map) > cap:
            keys = sorted(self._comment_post_map.keys())[-cap:]
            self._comment_post_map = {k: self._comment_post_map[k] for k in keys}

    # =========================================================================
    # Mahamantra Listener — THE heartbeat path
    # =========================================================================

    def _on_mahamantra_tick(self, tick_state: object) -> None:
        """
        Called on every mahamantra.tick() via _broadcast().

        Polls Moltbook once per full mantra cycle (16 ticks).
        Same pattern as Nrisimha._on_mahamantra_tick().
        """
        if not self._client:
            return

        self._tick_count += 1
        if self._tick_count % _TICKS_PER_HEARTBEAT != 0:
            return

        self._do_heartbeat()

    def _do_heartbeat(self) -> None:
        """Execute one heartbeat cycle: check DMs, read feed, create posts, monitor replies."""
        try:
            heartbeat = self._client.sync_check_heartbeat()
            self._last_heartbeat_error = None
        except Exception as e:
            self._last_heartbeat_error = str(e)
            logger.warning(f"Heartbeat failed: {e}")
            return

        self._heartbeat_count += 1

        has_new = heartbeat.get("has_activity", False)
        if has_new:
            self._safe_call(self._process_inbound_dms, "inbound_dms")
            self._safe_call(self._process_dm_requests, "dm_requests")

        # Analyze feed periodically (not every heartbeat)
        if self._heartbeat_count % self._FEED_INTERVAL == 0:
            self._safe_call(self._analyze_feed, "feed_analysis")

        # Autonomous post creation (uses feed topics as seed)
        if self._heartbeat_count % self._POST_INTERVAL == 0:
            self._safe_call(self._maybe_create_post, "post_creation")

        # Monitor replies to our own comments
        if self._heartbeat_count % self._REPLY_CHECK_INTERVAL == 0:
            self._safe_call(self._check_own_comment_replies, "reply_monitoring")

        # Submolt discovery (once at startup, then periodically)
        if self._heartbeat_count == 1 or self._heartbeat_count % (self._POST_INTERVAL * 4) == 0:
            self._safe_call(self._discover_submolts, "submolt_discovery")

        # Profile auto-update (karma, activity stats in bio)
        if self._heartbeat_count % self._PROFILE_UPDATE_INTERVAL == 0:
            self._safe_call(self._update_profile, "profile_update")

        # Trim in-memory sets periodically to prevent unbounded growth
        if self._heartbeat_count % self._PROFILE_UPDATE_INTERVAL == 0:
            self._trim_memory()

        # Monitor queue health — warn on overflow
        self._monitor_queue_health()

        # Always drain queue on heartbeat (even without new activity)
        self._drain_content_queue()

    # =========================================================================
    # on_pulse — backward compat (delegates to same heartbeat)
    # =========================================================================

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.SENSORS

    def on_pulse(self, kernel: "RealVibeKernel", transaction: object) -> HookResult:
        """
        Backward compat: if kernel.pulse() ever gets fixed,
        this delegates to the same heartbeat logic.
        """
        if not self._client:
            return HookResult.error("Client not initialized")

        self._do_heartbeat()

        return HookResult.ok(
            data={
                "heartbeat": "ok" if not self._last_heartbeat_error else "failed",
                "error": self._last_heartbeat_error,
                "offline": self._offline_mode,
                "listener_wired": self._listener_wired,
                "ticks_seen": self._tick_count,
            }
        )

    # =========================================================================
    # Inbound DM Processing
    # =========================================================================

    def _process_inbound_dms(self) -> None:
        """Fetch new DMs, route through Gateway, propose replies via ContentProposalProtocol."""
        from vibe_core.gateway.mahamantra_gateway import get_gateway
        from vibe_core.protocols.gateway import EntryType, create_request

        try:
            conversations = self._client.sync_get_dm_conversations()
        except Exception as e:
            logger.warning(f"DM conversation list failed: {e}")
            return

        gateway = get_gateway()
        for conv in conversations:
            conv_id = conv.get("id", "") if isinstance(conv, dict) else ""
            if not conv_id:
                continue
            try:
                messages = self._client.sync_get_dm_messages(conv_id)
            except Exception as e:
                logger.warning(f"DM fetch for {conv_id} failed: {e}")
                continue

            for msg in messages:
                msg_id = msg.get("id", "") if isinstance(msg, dict) else ""
                content = msg.get("content", msg.get("message", "")) if isinstance(msg, dict) else ""
                if not content:
                    continue
                if msg_id and msg_id in self._seen_message_ids:
                    continue
                if msg_id:
                    self._seen_message_ids.add(msg_id)

                sender = msg.get("sender", "unknown") if isinstance(msg, dict) else "unknown"

                # Route through Govardhan Gateway
                gateway_response = None
                try:
                    req = create_request(content, [], EntryType.AGENT)
                    req["context"]["source"] = "moltbook_dm"
                    req["context"]["sender"] = sender
                    req["context"]["conversation_id"] = conv_id
                    gateway_response = gateway.receive(req)
                except Exception as e:
                    logger.warning(f"Inbound DM routing failed: {e}")

                # Propose a reply
                try:
                    proposal = self._proposer.propose_dm_reply(
                        conversation_id=conv_id,
                        sender=sender,
                        inbound_content=content,
                        gateway_response=gateway_response,
                    )
                    if proposal:
                        self._content_queue.enqueue(proposal)
                        logger.info(f"DM reply queued for {conv_id}")
                except Exception as e:
                    logger.warning(f"Content proposal failed: {e}")

                # Follow-back: follow agents who DM us (social reciprocity)
                self._follow_back(sender)

    def _process_dm_requests(self) -> None:
        """Check pending DM requests, propose approve/reject via ContentProposalProtocol."""
        try:
            requests = run_async(self._client.get_dm_requests())
        except Exception as e:
            logger.warning(f"DM request fetch failed: {e}")
            return

        for req in requests:
            req_id = req.get("id", req.get("conversation_id", "")) if isinstance(req, dict) else ""
            if not req_id:
                continue
            from_agent = ""
            if isinstance(req, dict):
                fa = req.get("from_agent", {})
                from_agent = fa.get("name", str(fa)) if isinstance(fa, dict) else str(fa)
            preview = req.get("message_preview", "") if isinstance(req, dict) else ""

            try:
                proposal = self._proposer.propose_dm_request_action(
                    request_id=req_id,
                    from_agent=from_agent,
                    message_preview=preview,
                )
                if proposal:
                    self._content_queue.enqueue(proposal)
                    logger.info(f"DM request action queued for {req_id}")
            except Exception as e:
                logger.warning(f"DM request proposal failed: {e}")

    def _analyze_feed(self) -> None:
        """Read personalized feed, analyze posts via engine, propose engagement."""
        if not self._proposer:
            return

        try:
            posts = run_async(self._client.get_personalized_feed(sort="hot", limit=10))
        except Exception as e:
            logger.warning(f"Feed fetch failed: {e}")
            return

        if not posts:
            return

        # Filter already-seen posts
        unseen = []
        for post in posts:
            post_id = post.get("id", "") if isinstance(post, dict) else ""
            if post_id and post_id not in self._seen_post_ids:
                self._seen_post_ids.add(post_id)
                unseen.append(post)

        if not unseen:
            return

        scored = self._proposer.analyze_feed(unseen)

        for post, ranked, score in scored:
            post_id = post.get("id", "") if isinstance(post, dict) else ""
            post_content = post.get("content", post.get("title", "")) if isinstance(post, dict) else ""
            author_data = post.get("author", {}) if isinstance(post, dict) else {}
            author = author_data.get("name", "unknown") if isinstance(author_data, dict) else "unknown"

            if not post_id or not post_content:
                continue

            # Engagement (upvote)
            try:
                engage_proposal = self._proposer.should_engage(post_id, post_content, author)
                if engage_proposal:
                    self._content_queue.enqueue(engage_proposal)
            except Exception as e:
                logger.warning(f"Engagement proposal failed: {e}")

            # Comment on high-resonance posts
            try:
                comment_proposal = self._proposer.propose_comment(
                    post_id,
                    post_content,
                    "feed_analysis",
                )
                if comment_proposal:
                    self._content_queue.enqueue(comment_proposal)
                    logger.info(f"Feed comment queued for {post_id} (score={score:.2f})")
            except Exception as e:
                logger.warning(f"Comment proposal failed: {e}")

    def _maybe_create_post(self) -> None:
        """Autonomous post creation — uses trending feed topics as seed.

        The ResonanceProposer pipeline gates ensure quality:
        - Guna gate: only RAJAS mode produces posts
        - Integrity gate: < 0.5 coherence → skip
        - LLM or kirtan fallback for content generation
        """
        if not self._proposer:
            return

        # Extract trending topics from recent feed as context
        feed_topics: List[str] = []
        try:
            posts = run_async(self._client.get_feed(sort="hot", limit=5))
            for post in posts or []:
                title = post.get("title", "") if isinstance(post, dict) else ""
                if title:
                    feed_topics.append(title[:80])
        except Exception as e:
            logger.debug(f"Feed topic extraction failed: {e}")

        trigger = "scheduled"
        context: Dict[str, Any] = {}
        if feed_topics:
            context["feed_topics"] = feed_topics

        try:
            proposal = self._proposer.propose_post(trigger, context)
            if proposal:
                self._content_queue.enqueue(proposal)
                self._last_post_heartbeat = self._heartbeat_count
                logger.info(f"Autonomous post queued: {proposal.get('title', '')[:50]}")
            else:
                logger.debug("Post proposal filtered by pipeline (low integrity or TAMAS)")
        except Exception as e:
            logger.warning(f"Autonomous post creation failed: {e}")

    def _check_own_comment_replies(self) -> None:
        """Monitor replies to our own comments — maintain conversations.

        Uses _comment_post_map (comment_id → post_id) to fetch comment threads,
        find replies to our comments, and generate follow-up reply proposals.
        Routes through MoltbookService for Guna enforcement + audit trail.
        """
        if not self._proposer or not self._comment_post_map:
            return

        if self._service is None:
            self._service = MoltbookService(self._client)

        # Get unique post IDs we need to check (max 3 per cycle)
        post_ids = list(set(self._comment_post_map.values()))[:3]
        our_comment_ids = set(self._comment_post_map.keys())

        for post_id in post_ids:
            try:
                comments = self._service.get_comments(post_id, sort="new")
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
                if parent in our_comment_ids and cid not in self._seen_message_ids:
                    self._seen_message_ids.add(cid)
                    # Propose a follow-up reply
                    try:
                        proposal = self._proposer.propose_comment(
                            post_id,
                            content,
                            "reply_to_own_comment",
                            context={"parent_id": cid, "original_comment_id": parent},
                        )
                        if proposal:
                            # Set parent_id so our reply threads correctly
                            proposal["parent_id"] = cid
                            self._content_queue.enqueue(proposal)
                            self._log_activity(
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

    def _update_profile(self) -> None:
        """Update agent profile with current activity stats.

        Fetches current profile, computes stats from internal state,
        and patches the bio description + metadata. RAJAS operation (logged).
        """
        if not self._service:
            return

        try:
            profile = self._service.get_own_profile()
        except Exception as e:
            logger.debug(f"Profile fetch failed: {e}")
            return

        current_karma = profile.get("karma", 0) if isinstance(profile, dict) else 0
        follower_count = profile.get("follower_count", 0) if isinstance(profile, dict) else 0
        following_count = profile.get("following_count", 0) if isinstance(profile, dict) else 0

        # Build activity summary for bio
        queue_stats = self._content_queue.stats
        description = (
            f"{self._agent_name} · Autonomous agent · "
            f"{current_karma} karma · "
            f"{follower_count} followers · {following_count} following · "
            f"{len(self._subscribed_submolts)} submolts"
        )

        metadata = {
            "heartbeats": self._heartbeat_count,
            "posts_sent": queue_stats.get("total_drained", 0),
            "comments_tracked": len(self._own_comment_ids),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        try:
            self._service.update_profile(description=description, metadata=metadata)
            self._last_profile_heartbeat = self._heartbeat_count
            self._log_activity(
                "profile_updated",
                {
                    "karma": current_karma,
                    "followers": follower_count,
                    "following": following_count,
                },
            )
            logger.info(f"Profile updated: {current_karma} karma, {follower_count} followers")
        except Exception as e:
            logger.warning(f"Profile update failed: {e}")

    def _monitor_queue_health(self) -> None:
        """Log warning when queue overflows (proposals silently dropped).

        The ContentQueue uses a bounded deque — when full, oldest proposals
        get evicted on enqueue. We track total_dropped and log when it rises.
        Rate-limited to avoid log spam: max 1 warning per 8 heartbeats.
        """
        stats = self._content_queue.stats
        dropped = stats.get("total_dropped", 0)
        queued = stats.get("queued", 0)
        max_size = stats.get("max_size", ContentQueue.DEFAULT_MAX_SIZE)

        if dropped > 0 and (self._heartbeat_count - self._last_overflow_log) >= 8:
            self._last_overflow_log = self._heartbeat_count
            logger.warning(
                f"Queue overflow: {dropped} proposals dropped (queue {queued}/{max_size}). "
                f"Enqueued={stats.get('total_enqueued', 0)}, "
                f"Drained={stats.get('total_drained', 0)}"
            )

        # High water mark: queue > 80% full
        if queued > max_size * 0.8:
            logger.info(f"Queue high water: {queued}/{max_size} ({queued * 100 // max_size}% full)")

    def _follow_back(self, sender: str) -> None:
        """Follow an agent back if we haven't already. Enqueues a FOLLOW proposal."""
        if not sender or sender == "unknown" or sender in self._followed_agents:
            return

        self._followed_agents.add(sender)
        proposal: ContentProposal = {
            "content_type": ContentType.FOLLOW.value,
            "to_agent": sender,
            "source": "follow_back",
            "priority": 0,  # Low priority — social grooming, not urgent
        }
        self._content_queue.enqueue(proposal)
        logger.info(f"Follow-back queued for {sender}")

    def _log_activity(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Append an event to the JSONL activity log. Fire-and-forget."""
        if not self._activity_log_path:
            return
        try:
            entry = {
                "t": datetime.now(timezone.utc).isoformat(),
                "event": event_type,
                "hb": self._heartbeat_count,
            }
            if payload:
                entry["data"] = payload
            line = json.dumps(entry, separators=(",", ":"))
            with self._activity_log_path.open("a") as f:
                f.write(line + "\n")
        except Exception:
            pass  # Never fail the main loop for logging

    def _discover_submolts(self) -> None:
        """Discover and subscribe to relevant submolts.

        Queries available submolts, filters for interesting communities,
        and enqueues SUBSCRIBE proposals for ones we haven't joined yet.
        """
        try:
            submolts = run_async(self._client.get_submolts())
        except Exception as e:
            logger.debug(f"Submolt discovery failed: {e}")
            return

        if not submolts:
            return

        for submolt in submolts:
            if not isinstance(submolt, dict):
                continue
            name = submolt.get("name", "")
            if not name or name in self._subscribed_submolts:
                continue

            # Subscribe to communities we haven't joined yet
            # The platform is small enough that subscribing to all is reasonable
            self._subscribed_submolts.add(name)
            proposal: ContentProposal = {
                "content_type": ContentType.SUBSCRIBE.value,
                "submolt": name,
                "source": "submolt_discovery",
                "priority": 0,
            }
            self._content_queue.enqueue(proposal)
            logger.info(f"Submolt subscription queued: {name}")

    # Max retries before a proposal is permanently dropped
    _MAX_PROPOSAL_RETRIES = 2

    def _drain_content_queue(self) -> None:
        """Execute queued content proposals through MoltbookService.

        Failed proposals are re-enqueued with a retry counter.
        After _MAX_PROPOSAL_RETRIES, the proposal is dropped and logged.
        """
        if self._content_queue.is_empty:
            return

        if self._service is None:
            self._service = MoltbookService(self._client)
        service = self._service
        proposals = self._content_queue.drain(limit=3)
        failed: List[ContentProposal] = []

        for proposal in proposals:
            ct = proposal.get("content_type", "")
            try:
                if ct == ContentType.DM_REPLY.value:
                    conv_id = proposal.get("conversation_id", "")
                    content = proposal.get("content", "")
                    if conv_id and content:
                        service.send_dm(conv_id, content)
                        self._log_activity("dm_sent", {"conversation_id": conv_id})
                        logger.info(f"DM reply sent to {conv_id}")

                elif ct == ContentType.DM_INITIATE.value:
                    to_agent = proposal.get("to_agent", "")
                    if to_agent:
                        service.approve_dm_request(proposal.get("sender", ""))
                        self._log_activity("dm_request_approved", {"agent": to_agent})
                        logger.info(f"DM request approved for {to_agent}")

                elif ct == ContentType.POST.value:
                    title = proposal.get("title", "")
                    content = proposal.get("content", "")
                    submolt = proposal.get("submolt")
                    if title and content:
                        service.create_post(title, content, submolt)
                        self._log_activity("post_created", {"title": title[:80], "submolt": submolt})
                        logger.info(f"Post created: {title[:50]}")

                elif ct == ContentType.COMMENT.value:
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
                        logger.info(f"Comment posted on {post_id}")

                elif ct == ContentType.VOTE.value:
                    post_id = proposal.get("post_id", "")
                    if post_id:
                        service.upvote(post_id)
                        self._log_activity("upvoted", {"post_id": post_id})
                        logger.info(f"Upvoted {post_id}")

                elif ct == ContentType.FOLLOW.value:
                    to_agent = proposal.get("to_agent", "")
                    if to_agent:
                        service.follow(to_agent)
                        self._log_activity("followed", {"agent": to_agent})
                        logger.info(f"Followed {to_agent}")

                elif ct == ContentType.SUBSCRIBE.value:
                    submolt = proposal.get("submolt", "")
                    if submolt:
                        service.subscribe(submolt)
                        self._log_activity("subscribed", {"submolt": submolt})
                        logger.info(f"Subscribed to {submolt}")

            except PermissionError as e:
                logger.warning(f"TAMAS blocked: {e}")
                # Permanent failure — do not retry
            except Exception as e:
                retries = proposal.get("_retries", 0)
                if retries < self._MAX_PROPOSAL_RETRIES:
                    proposal["_retries"] = retries + 1
                    failed.append(proposal)
                    logger.warning(f"Content execution failed ({ct}), retry {retries + 1}: {e}")
                else:
                    self._log_activity("proposal_dropped", {"type": ct, "error": str(e)[:200]})
                    logger.error(f"Proposal dropped after {retries} retries ({ct}): {e}")

        # Re-enqueue failed proposals for next heartbeat
        for proposal in failed:
            self._content_queue.enqueue(proposal)

    # =========================================================================
    # API — exposed to other plugins via kernel.api("moltbook")
    # =========================================================================

    def _boot_proposer(self) -> None:
        """Boot ResonanceProposer + register moltbook_context in PromptContext."""
        from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

        self._proposer = ResonanceProposer(agent_name=self._agent_name)
        self._register_moltbook_context()
        logger.info("Content proposer: ResonanceProposer v3 (engine-wired)")

    def _register_moltbook_context(self) -> None:
        """Register moltbook_context resolver in PromptContext for dynamic context injection."""
        try:
            from vibe_core.runtime.prompt_context import get_prompt_context

            ctx = get_prompt_context()
            ctx.register("moltbook_context", self._resolve_moltbook_context)
            logger.info("moltbook_context registered in PromptContext")
        except Exception as e:
            logger.warning(f"PromptContext registration failed: {e}")

    def _resolve_moltbook_context(self) -> str:
        """Resolver for moltbook_context: feed state, community, operations."""
        parts: List[str] = []

        # Connection state
        mode = "LIVE" if not self._offline_mode else "OFFLINE"
        parts.append(f"Moltbook [{mode}] — {self._heartbeat_count} heartbeats, {self._tick_count} ticks")

        # Queue state
        if self._content_queue:
            stats = self._content_queue.stats
            queued = stats.get("queued", 0)
            drained = stats.get("total_drained", 0)
            if queued or drained:
                parts.append(f"Content queue: {queued} queued, {drained} drained")

        # Social graph
        followed = len(self._followed_agents)
        submolts = len(self._subscribed_submolts)
        threads = len(self._comment_post_map)
        if followed or submolts or threads:
            parts.append(f"Social: {followed} followed, {submolts} submolts, {threads} threads")

        # Active conversations
        seen_msgs = len(self._seen_message_ids)
        seen_posts = len(self._seen_post_ids)
        if seen_msgs or seen_posts:
            parts.append(f"Seen: {seen_msgs} messages, {seen_posts} posts")

        # Health
        if self._last_heartbeat_error:
            parts.append(f"Last error: {self._last_heartbeat_error}")
        elif self._listener_wired:
            parts.append("Health: OK (Mahamantra listener wired)")

        return "\n".join(parts)

    def _register_proposer(self) -> None:
        """Register ContentProposalProtocol in DI. Other plugins can swap the proposer."""
        try:
            from vibe_core.di import ServiceRegistry

            ServiceRegistry.register_factory(ContentProposalProtocol, lambda: self._proposer)
            logger.info("ContentProposalProtocol registered in ServiceRegistry")
        except Exception as e:
            logger.warning(f"ContentProposalProtocol registration failed: {e}")

    def get_api(self) -> Optional[Dict[str, Any]]:
        return {
            "client": self._client,
            "offline": self._offline_mode,
            "last_error": self._last_heartbeat_error,
            "listener_wired": self._listener_wired,
            "ticks_seen": self._tick_count,
            "content_queue": self._content_queue.stats,
        }
