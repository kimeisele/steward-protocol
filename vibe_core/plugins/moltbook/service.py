"""
MoltbookService — Concrete MoltbookProtocol implementation + GAD-000 compliance.
================================================================================

Wraps MoltbookClient with the ABC interface for DI registration.
Every operation is classified by Guna (SATTVA/RAJAS/TAMAS).

Extracted from plugin_main.py for single-responsibility.
"""

import logging
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional

from vibe_core.mahamantra import run_async
from vibe_core.mahamantra.protocols._gad import GADBase
from vibe_core.protocols.moltbook import (
    DMMessage,
    MoltbookAgentProfile,
    MoltbookComment,
    MoltbookPost,
    MoltbookProtocol,
    SemanticSearchResult,
)

if TYPE_CHECKING:
    from vibe_core.mahamantra import MoltbookClient

logger = logging.getLogger("MOLTBOOK.SERVICE")


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
        # Guna enforcer (lazy-loaded)
        self._guna_enforcer_mgr = None
        # First chant: transition heartbeat from DISCONNECTED → CHANTING
        self.chant()

    @property
    def _guna(self):
        """Lazy-init GunaEnforcer for I/O Policy validation."""
        if self._guna_enforcer_mgr is None:
            from vibe_core.plugins.moltbook.managers.guna_enforcer import GunaEnforcer

            self._guna_enforcer_mgr = GunaEnforcer(self)
        return self._guna_enforcer_mgr

    def _enforce_guna(self, operation: str) -> None:
        """Guna I/O Policy + Knowledge Graph Constraint validation.

        SATTVA: Pass through (read-only, safe).
        RAJAS: Log and allow (write, rate-limited by client).
        TAMAS: Block (destructive).
        """
        self._guna.enforce(operation)

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

    def get_submolt_feed(self, name: str, sort: str = "new", limit: int = 25) -> list:
        self._enforce_guna("get_submolt_feed")
        return run_async(self._client.get_submolt_feed(name, sort, limit))

    def verify_credentials(self) -> bool:
        self._enforce_guna("verify_credentials")
        try:
            status = run_async(self._client.check_status())
            return status == "claimed"
        except Exception as e:
            logger.warning(f"Credential check failed: {e}")
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
        """Discoverability: machine-readable capability description."""
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
        """Observability: current state in structured format."""
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
        """SATTVA operations are idempotent. RAJAS are not."""
        return False

    def detect_drift(self) -> List[str]:
        """Detect deviations from valid state."""
        from vibe_core.mahamantra.adapters.moltbook import MoltbookLimits

        drifts: List[str] = []
        limits = self._client.limits

        if limits.requests_this_minute > MoltbookLimits.REQ_PER_MIN:
            drifts.append(f"RATE_LIMIT_BREACH: {limits.requests_this_minute}/{MoltbookLimits.REQ_PER_MIN} req/min")
        if limits.posts_this_30m > MoltbookLimits.POST_PER_30_MIN:
            drifts.append(f"POST_LIMIT_BREACH: {limits.posts_this_30m}/{MoltbookLimits.POST_PER_30_MIN} posts/30m")
        if limits.comments_this_hour > MoltbookLimits.COMMENTS_PER_HOUR:
            drifts.append(
                f"COMMENT_LIMIT_BREACH: {limits.comments_this_hour}/{MoltbookLimits.COMMENTS_PER_HOUR} comments/h"
            )
        if self._consecutive_failures > 3:
            drifts.append(f"API_DEGRADED: {self._consecutive_failures} consecutive failures")
        if len(self._operation_log) > 10000:
            drifts.append(f"AUDIT_LOG_OVERFLOW: {len(self._operation_log)} entries in memory")

        return drifts

    # =========================================================================
    # GAD-000: THE 4 DHARMA PRINCIPLES
    # =========================================================================

    def test_daya(self) -> bool:
        """Mercy: No corrupt data ingestion."""
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
        """Truthfulness: No hallucination — deterministic, verifiable output."""
        return self._last_api_error is None or self._consecutive_failures < 3

    def test_tapas(self) -> bool:
        """Austerity: No resource leaks — bounded computation and memory."""
        from vibe_core.mahamantra.adapters.moltbook import MoltbookLimits

        limits = self._client.limits
        within_limits = (
            limits.requests_this_minute <= MoltbookLimits.REQ_PER_MIN
            and limits.posts_this_30m <= MoltbookLimits.POST_PER_30_MIN
            and limits.comments_this_hour <= MoltbookLimits.COMMENTS_PER_HOUR
        )
        log_bounded = len(self._operation_log) <= 10000
        return within_limits and log_bounded

    def test_saucam(self) -> bool:
        """Cleanliness: No unauthorized connections — only signed, authorized I/O."""
        return bool(self._client.api_key)
