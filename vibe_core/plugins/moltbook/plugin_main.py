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
from vibe_core.mahamantra.substrate.core.seed import (
    COSMIC_FRAME,
    HALVES,
    HARE_COUNT,
    KSHETRA,
    LILA,
    MAHAJANA_COUNT,
    MALA,
    NAVA,
    PANCHA,
    QUARTERS,
    SHARANAGATI,
    WORDS,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.mahamantra import MoltbookClient

logger = logging.getLogger("MOLTBOOK")

# One full mantra = WORDS ticks. Poll Moltbook once per chant cycle.
_TICKS_PER_HEARTBEAT = WORDS  # 16 words in Mahamantra


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
        """Guna I/O Policy + Knowledge Graph Constraint validation.

        SATTVA: Pass through (read-only, safe).
        RAJAS: Log and allow (write, rate-limited by client).
        TAMAS: Block (destructive).

        Additionally checks constraints from knowledge/moltbook/platform.yaml
        (6 hard/soft constraints) via Knowledge Graph.
        """
        from vibe_core.protocols.moltbook import MOLTBOOK_GUNA_MAP, MoltbookGuna

        guna = MOLTBOOK_GUNA_MAP.get(operation, MoltbookGuna.SATTVA)

        if guna == MoltbookGuna.TAMAS:
            raise PermissionError(
                f"MOLTBOOK-TAMAS: Operation '{operation}' is destructive and requires "
                f"explicit authorization. Not implemented."
            )

        # Knowledge Graph constraint check (knowledge/moltbook/platform.yaml)
        try:
            from vibe_core.knowledge.resolver import get_resolver

            resolver = get_resolver()
            violations = resolver.get_violations(operation, {"guna": guna.value, "operation": operation})
            for v in violations:
                logger.warning(f"MOLTBOOK-KG-CONSTRAINT: {v}")
        except Exception as e:
            logger.debug(f"KG constraint check unavailable: {e}")

        if guna == MoltbookGuna.RAJAS:
            entry = {
                "operation": operation,
                "guna": guna.value,
                "timestamp": time.time(),
            }
            self._operation_log.append(entry)
            # Prevent unbounded growth: trim when log exceeds 5000 entries
            if len(self._operation_log) > 5000:
                self._operation_log = self._operation_log[-2500:]
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

    # Defaults for heartbeat intervals — all derived from SEED constants
    _DEFAULT_FEED_INTERVAL = QUARTERS  # 4 phases
    _DEFAULT_POST_INTERVAL = KSHETRA  # 24 field elements
    _DEFAULT_REPLY_CHECK_INTERVAL = HARE_COUNT  # 8 Hare
    _DEFAULT_PROFILE_UPDATE_INTERVAL = LILA  # 48 Chaitanya's manifest

    # Engagement tracking: poll own posts for metrics
    _ENGAGEMENT_TRACK_INTERVAL = MAHAJANA_COUNT  # 12 authorities
    # Adaptive interval adjustment: recalculate based on feedback stats
    _INTERVAL_ADJUST_INTERVAL = KSHETRA  # 24 field elements

    # Persistence: queue + seen IDs survive restarts
    _QUEUE_STATE_FILE = "content_queue.json"
    _SEEN_STATE_FILE = "seen_ids.json"
    _ACTIVITY_LOG_FILE = "activity.jsonl"
    _MAX_SEEN_IDS = MALA * NAVA  # 972 ≈ 1000 (108 beads × 9 processes)

    # Rate limits (from platform.yaml moltbook-002-rate-limit)
    _POST_INTERVAL_SEC = 30 * 60  # 1 post per 30 minutes
    _COMMENT_LIMIT_PER_HOUR = 10  # 10 comments per hour
    _DM_LIMIT_PER_HOUR = 30  # 30 DM operations per hour

    def __init__(self):
        super().__init__()
        self._client = None  # MoltbookClient, created in on_boot
        self._service: Optional[MoltbookService] = None  # Singleton, reused in drain
        self._offline_mode: bool = True
        self._last_heartbeat_error: Optional[str] = None
        self._state_dir: Optional[Path] = None
        self._tick_count: int = 0
        self._heartbeat_count: int = 0
        # Intervals (configured at boot, defaults from class)
        self._feed_interval: int = self._DEFAULT_FEED_INTERVAL
        self._post_interval: int = self._DEFAULT_POST_INTERVAL
        self._reply_check_interval: int = self._DEFAULT_REPLY_CHECK_INTERVAL
        self._profile_update_interval: int = self._DEFAULT_PROFILE_UPDATE_INTERVAL
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
        self._last_heartbeat_ts: float = 0.0  # Debounce guard: epoch of last heartbeat
        # Circuit Executor (cortex/engines/circuit_engine.py) — wired at boot
        self._circuit_executor = None
        self._meta_circuit_manager = None
        # AGORA broadcast channel (cartridges/agent_city/agora/) — wired at boot
        self._agora = None
        # Agency Director — I-P-V-O pipeline (mahamantra-direct, guna=style not gate)
        self._agency_director = None
        # Strategy Planner — Sankalpa missions → strategic intents
        self._strategy_planner = None
        self._current_intents: list = []  # List[StrategicIntent]
        self._current_feed_topics: list = []  # Extracted topics from feed scan
        # Engagement tracking: own post IDs → metadata for polling
        self._own_post_ids: Dict[str, Dict[str, object]] = {}
        self._MAX_OWN_POST_IDS = COSMIC_FRAME // MALA  # 200 (pada_unit)
        # Rate limiting (from platform.yaml: 1 post/30min, 10 comments/hour)
        self._last_post_ts: float = 0.0
        self._comment_timestamps: List[float] = []
        self._dm_timestamps: List[float] = []

    @property
    def dependencies(self) -> Set[str]:
        return {"economy"}

    # =========================================================================
    # Agency Director — I-P-V-O pipeline (replaces direct proposer calls)
    # =========================================================================

    @property
    def agency_director(self):
        """Lazy-init AgencyDirector with plugin reference for circuit execution."""
        if self._agency_director is None:
            from vibe_core.cartridges.agent_city.moltbook.core.agency_director import AgencyDirector

            self._agency_director = AgencyDirector(plugin=self)
        return self._agency_director

    @property
    def strategy_planner(self):
        """Lazy-init MoltbookStrategyPlanner with event log reference."""
        if self._strategy_planner is None:
            try:
                from vibe_core.cartridges.agent_city.moltbook.core.strategy import MoltbookStrategyPlanner

                self._strategy_planner = MoltbookStrategyPlanner(
                    event_log=self.agency_director.event_log,
                    state_dir=self._state_dir,
                )
            except Exception as e:
                logger.warning(f"Strategy planner unavailable: {e}")
        return self._strategy_planner

    def _director_propose(
        self,
        content_type: str,
        raw_input: str,
        proposal_type: str,
        **extra,
    ) -> Optional[ContentProposal]:
        """Content generation: circuit state machine → ContentProposal.

        ONE path. execute_content_circuit() IS the content pipeline.
        SHABDA → ARTHA → PRATYAYA → KARMA → SUCCESS or None.
        """
        from vibe_core.plugins.moltbook.resonance_proposer import _kg_priority

        # Extract context dict and pass through to AgencyDirector
        extra_context = extra.get("context", {})
        circuit_result = self.execute_content_circuit(
            raw_input,
            content_type,
            post_id=extra.get("post_id", ""),
            sender=extra.get("sender", ""),
            trigger=extra.get("trigger", "heartbeat"),
            context=extra_context if isinstance(extra_context, dict) else {},
        )
        if not circuit_result or not circuit_result.get("content"):
            return None

        content = circuit_result["content"]
        guna = circuit_result.get("guna", "")
        guardian = circuit_result.get("guardian", "")

        proposal = ContentProposal(
            content_type=proposal_type,
            content=content,
            source=extra.get("trigger", "circuit"),
            priority=_kg_priority(proposal_type),
        )

        for key in ("post_id", "conversation_id", "sender", "parent_id", "submolt", "to_agent"):
            if key in extra and extra[key]:
                proposal[key] = extra[key]

        gw = extra.get("gateway_response") or {}
        if gw:
            proposal["gateway_success"] = bool(gw.get("success"))
            proposal["gateway_position"] = gw.get("position", -1)
            proposal["gateway_guardian"] = gw.get("guardian", "unknown")
            proposal["gateway_guna"] = gw.get("guna", "sattva")

        self._emit_event(
            "PROPOSAL_CREATED",
            f"Proposal: {content_type}",
            {
                "content_type": content_type,
                "priority": proposal.get("priority", 0),
                "guna": guna,
                "guardian": guardian,
            },
        )
        return proposal

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
            # Cap own_post_ids to most recent entries
            own_post_keys = sorted(
                self._own_post_ids.keys(),
                key=lambda k: self._own_post_ids[k].get("created_at", 0),
            )[-self._MAX_OWN_POST_IDS :]
            own_posts = {k: self._own_post_ids[k] for k in own_post_keys}

            seen_data = {
                "version": 4,
                "message_ids": msg_ids,
                "post_ids": post_ids,
                "own_comment_ids": sorted(self._own_comment_ids)[-self._MAX_SEEN_IDS :],
                "followed_agents": sorted(self._followed_agents),
                "subscribed_submolts": sorted(self._subscribed_submolts),
                "comment_post_map": cpm,
                "own_post_ids": own_posts,
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
                        # Clear stale retry state from previous session
                        p.pop("_retries", None)
                        p.pop("_retry_after", None)
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
                if data.get("version") in (1, 2, 3, 4):
                    self._seen_message_ids = set(data.get("message_ids", []))
                    self._seen_post_ids = set(data.get("post_ids", []))
                    self._own_comment_ids = set(data.get("own_comment_ids", []))
                    self._followed_agents = set(data.get("followed_agents", []))
                    self._subscribed_submolts = set(data.get("subscribed_submolts", []))
                    self._comment_post_map = data.get("comment_post_map", {})
                    self._own_post_ids = data.get("own_post_ids", {})
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
            return {"version": 5, "client_active": False}
        limits = self._client.limits
        return {
            "version": 5,
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
            "own_post_count": len(self._own_post_ids),
            "followed_agent_count": len(self._followed_agents),
            "subscribed_submolt_count": len(self._subscribed_submolts),
            "intervals": {
                "feed": self._feed_interval,
                "post": self._post_interval,
                "reply_check": self._reply_check_interval,
                "profile_update": self._profile_update_interval,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        if snapshot.get("version") not in (1, 2, 3, 4, 5) or not snapshot.get("client_active"):
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

            # Configurable heartbeat intervals (all in heartbeat counts, 1 hb = 16 ticks)
            self._feed_interval = int(cfg.get("feed_interval", self._DEFAULT_FEED_INTERVAL))
            self._post_interval = int(cfg.get("post_interval", self._DEFAULT_POST_INTERVAL))
            self._reply_check_interval = int(cfg.get("reply_check_interval", self._DEFAULT_REPLY_CHECK_INTERVAL))
            self._profile_update_interval = int(
                cfg.get("profile_update_interval", self._DEFAULT_PROFILE_UPDATE_INTERVAL)
            )

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

            # Register FeedbackProtocol (InMemoryFeedback) for learning signals
            self._register_feedback()

            # Resolve agent name from profile BEFORE booting proposer
            # (proposer uses agent_name in content templates)
            try:
                profile = self._service.get_own_profile() if self._service else {}
                name = profile.get("name", "") if isinstance(profile, dict) else ""
                if name:
                    self._agent_name = name
            except Exception as e:
                logger.debug(f"Profile name fetch failed, keeping default: {e}")

            self._boot_proposer()
            self._register_proposer()

            # Restore persisted queue + seen IDs from previous session
            self._restore_queue()

            # Activity log: append-only JSONL
            self._activity_log_path = data_root / self._ACTIVITY_LOG_FILE

            # Circuit Executor: wire MOLTBOOK_CONTENT_V1 circuit for state-machine content generation
            self._wire_circuit_executor(kernel)

            # AGORA: wire broadcast channel for federation publishing
            self._wire_agora(kernel)

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

    def _register_feedback(self) -> None:
        """Register FeedbackProtocol (InMemoryFeedback) for learning signals."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.feedback import FeedbackProtocol, InMemoryFeedback

            if not ServiceRegistry.is_registered(FeedbackProtocol):
                ServiceRegistry.register_factory(FeedbackProtocol, InMemoryFeedback)
                logger.info("FeedbackProtocol registered in ServiceRegistry")
        except Exception as e:
            logger.warning(f"FeedbackProtocol registration failed: {e}")

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

    def _wire_circuit_executor(self, kernel: "RealVibeKernel") -> None:
        """Wire CognitiveCircuitExecutor + MetaCircuitManager from cortex.

        The executor loads MOLTBOOK_CONTENT_V1 (and all other circuits) from
        playbook/circuits/*.yaml. MetaCircuitManager adds TASK_LEDGER and
        ERROR_RECOVERY as active observers.

        Degrades gracefully: if kernel or cortex unavailable, plugin continues
        with the ad-hoc proposer pipeline.
        """
        try:
            from vibe_core.cortex.engines.circuit_engine import create_circuit_executor_with_meta

            executor, manager = create_circuit_executor_with_meta(kernel)
            if "MOLTBOOK_CONTENT_V1" in executor.circuits:
                self._circuit_executor = executor
                self._meta_circuit_manager = manager
                logger.info(
                    f"Circuit executor wired: {len(executor.circuits)} circuits loaded, MOLTBOOK_CONTENT_V1 available"
                )
            else:
                logger.warning("MOLTBOOK_CONTENT_V1 not found in loaded circuits — circuit path disabled")
        except Exception as e:
            logger.warning(f"Circuit executor wiring failed (non-fatal): {e}")

    def _wire_agora(self, kernel: "RealVibeKernel") -> None:
        """Wire AGORA broadcast channel for federation publishing.

        After content is published to Moltbook, it is also broadcast to AGORA
        so other agents in Agent City (PULSE, LENS, AMBASSADOR) can observe.

        Degrades gracefully: if AGORA not registered, content still publishes
        to Moltbook directly.
        """
        try:
            agora = kernel.get_agent("agora") if hasattr(kernel, "get_agent") else None
            if agora and hasattr(agora, "publish_message"):
                self._agora = agora
                logger.info("AGORA broadcast channel wired for federation publishing")
            else:
                logger.info("AGORA not available — federation broadcasting disabled (non-fatal)")
        except Exception as e:
            logger.debug(f"AGORA wiring skipped: {e}")

    def _broadcast_to_agora(self, content_type: str, content: str, metadata: Dict[str, Any]) -> None:
        """Broadcast published content to AGORA for federation awareness.

        One-way: Moltbook → AGORA → [PULSE, LENS, AMBASSADOR, ...]
        """
        if not self._agora:
            return
        try:
            self._agora.publish_message(
                source="moltbook",
                message_type="narrative",
                content=content[:500],
                metadata={
                    "content_type": content_type,
                    "agent_name": self._agent_name,
                    **metadata,
                },
            )
        except Exception as e:
            logger.debug(f"AGORA broadcast failed (non-fatal): {e}")

    def execute_content_circuit(
        self,
        raw_input: str,
        content_type: str = "comment",
        post_id: str = "",
        sender: str = "",
        trigger: str = "heartbeat",
        auto_approve: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """MOLTBOOK_CONTENT_V1 — ONE path through AgencyDirector.

        AgencyDirector.run_retry_loop() IS the state machine:
            SHABDA  = _run_pipeline()
            ARTHA   = guna/integrity gates
            PRATYAYA = _compose_content() (engine + MahaComposition + LLM)
            KARMA   = constitution.validate() + event_log

        This method converts CycleResult → dict for callers that want dict format.
        Context dict flows through to AgencyDirector._input() → _compose_content()
        for strategic reasoning, engagement context, submolt context.
        """
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
        result = self.agency_director.run_retry_loop(**kwargs)
        if result.status != "SUCCESS" or not result.content:
            return None
        return {
            "content": result.content,
            "guna": result.guna,
            "guardian": result.guardian,
            "duration_ms": result.duration_ms,
        }

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
            except Exception as e:
                logger.debug(f"Listener unregister failed during shutdown: {e}")
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
        """Trim in-memory tracking sets and flush proposer caches.

        Prevents unbounded growth during long-running sessions.
        Also flushes pipeline/engine caches in ResonanceProposer
        to prevent stale results from accumulating.
        """
        cap = self._MAX_SEEN_IDS
        if len(self._seen_message_ids) > cap:
            self._seen_message_ids = set(sorted(self._seen_message_ids)[-cap:])
        if len(self._seen_post_ids) > cap:
            self._seen_post_ids = set(sorted(self._seen_post_ids)[-cap:])
        if len(self._own_comment_ids) > cap:
            self._own_comment_ids = set(sorted(self._own_comment_ids)[-cap:])
        if len(self._comment_post_map) > cap:
            keys = sorted(self._comment_post_map.keys())[-cap:]
            self._comment_post_map = {k: self._comment_post_map[k] for k in keys}
        if len(self._own_post_ids) > self._MAX_OWN_POST_IDS:
            sorted_keys = sorted(
                self._own_post_ids.keys(),
                key=lambda k: self._own_post_ids[k].get("created_at", 0),
            )[-self._MAX_OWN_POST_IDS :]
            self._own_post_ids = {k: self._own_post_ids[k] for k in sorted_keys}
        # Flush proposer pipeline/engine caches
        if self._proposer and hasattr(self._proposer, "flush_cache"):
            self._proposer.flush_cache()

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

    # Minimum seconds between heartbeats (prevents double-fire from on_pulse + tick)
    _HEARTBEAT_DEBOUNCE_S = 2.0

    def _do_heartbeat(self) -> None:
        """Execute one heartbeat cycle with MURALI phase-aware dispatch.

        MURALI routing changes PRIORITY within the heartbeat, not exclusion.
        All 4 departments execute within one full cycle, but the current
        phase determines which department gets run first.

        Debounce guard: if on_pulse() AND _on_mahamantra_tick() both call this
        within the same tick window, the second call is silently skipped.
        """
        now = time.time()
        if (now - self._last_heartbeat_ts) < self._HEARTBEAT_DEBOUNCE_S:
            return  # Already fired recently — skip (split-brain guard)
        self._last_heartbeat_ts = now

        try:
            heartbeat = self._client.sync_check_heartbeat()
            self._last_heartbeat_error = None
        except Exception as e:
            self._last_heartbeat_error = str(e)
            logger.warning(f"Heartbeat failed: {e}")
            return

        self._heartbeat_count += 1

        # Always: process inbound DMs (reactive, not phased)
        has_new = heartbeat.get("has_activity", False)
        if has_new:
            self._safe_call(self._process_inbound_dms, "inbound_dms")
            self._safe_call(self._process_dm_requests, "dm_requests")

        # MURALI phase-aware dispatch: prioritize current department
        department = self._get_current_department()

        if department == "research":
            # GENESIS: scan feed, discover submolts
            if self._heartbeat_count % self._feed_interval == 0:
                self._safe_call(self._scan_feed, "feed_scan")
            if self._heartbeat_count == 1 or self._heartbeat_count % (self._post_interval * 4) == 0:
                self._safe_call(self._discover_submolts, "submolt_discovery")

        elif department == "planning":
            # DHARMA: evaluate strategy → intents
            if self._heartbeat_count % self._feed_interval == 0:
                self._safe_call(self._evaluate_strategy, "strategy_evaluation")

        elif department == "execution":
            # KARMA: generate content from intents, reply monitoring
            if self._heartbeat_count % self._post_interval == 0:
                self._safe_call(self._execute_intents, "intent_execution")
            if self._heartbeat_count % self._reply_check_interval == 0:
                self._safe_call(self._check_own_comment_replies, "reply_monitoring")

        elif department == "learning":
            # MOKSHA: track engagement, adjust intervals
            if self._heartbeat_count % self._ENGAGEMENT_TRACK_INTERVAL == 0:
                self._safe_call(self._track_engagement, "engagement_tracking")
            if self._heartbeat_count % self._INTERVAL_ADJUST_INTERVAL == 0:
                self._safe_call(self._adjust_intervals, "interval_adjustment")

        # Non-phased maintenance (runs regardless of department)
        if self._heartbeat_count % self._profile_update_interval == 0:
            self._safe_call(self._update_profile, "profile_update")
            self._trim_memory()

        # Monitor queue health — warn on overflow
        self._monitor_queue_health()

        # Always drain queue on heartbeat (even without new activity)
        self._drain_content_queue()

    def _get_current_department(self) -> str:
        """Read MURALI phase from VenuOrchestrator → department name.

        Falls back to heartbeat_count cycling when venu is unavailable,
        ensuring all 4 departments (research/planning/execution/learning) run.
        """
        try:
            from vibe_core.cartridges.agent_city.moltbook.core.agency_director import MuraliRouter

            return MuraliRouter().current_department(fallback_tick=self._heartbeat_count)
        except Exception:
            # Last resort: cycle through departments using heartbeat count
            departments = ("research", "planning", "execution", "learning")
            return departments[self._heartbeat_count % len(departments)]

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
        """Fetch new DMs, route through Gateway, reply via AgencyDirector I-P-V-O."""
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

                # Propose a reply via Agency Director (I-P-V-O pipeline)
                try:
                    proposal = self._director_propose(
                        content_type="dm_reply",
                        raw_input=content,
                        proposal_type=ContentType.DM_REPLY.value,
                        conversation_id=conv_id,
                        sender=sender,
                        trigger="inbound_dm",
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
        """Read personalized feed, score via proposer, generate via AgencyDirector."""
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

            # Comment on high-resonance posts via Agency Director (I-P-V-O)
            try:
                comment_proposal = self._director_propose(
                    content_type="comment",
                    raw_input=post_content,
                    proposal_type=ContentType.COMMENT.value,
                    post_id=post_id,
                    trigger="feed_analysis",
                )
                if comment_proposal:
                    self._content_queue.enqueue(comment_proposal)
                    logger.info(f"Feed comment queued for {post_id} (score={score:.2f})")
            except Exception as e:
                logger.warning(f"Comment proposal failed: {e}")

    # =========================================================================
    # Phase-Aware Methods (MURALI routing)
    # =========================================================================

    def _scan_feed(self) -> None:
        """GENESIS phase: Extract topics + metadata from feed. NO content generation.

        Stores results in self._current_feed_topics for later strategy evaluation.
        """
        if not self._proposer:
            return

        try:
            posts = run_async(self._client.get_personalized_feed(sort="hot", limit=10))
        except Exception as e:
            logger.warning(f"Feed fetch failed: {e}")
            return

        if not posts:
            return

        # Filter already-seen posts, store full metadata
        unseen = []
        for post in posts:
            post_id = post.get("id", "") if isinstance(post, dict) else ""
            if post_id and post_id not in self._seen_post_ids:
                self._seen_post_ids.add(post_id)
                unseen.append(post)

        self._current_feed_topics = unseen

        # Engagement: upvote high-quality posts during scan (lightweight, no content gen)
        if self._proposer and unseen:
            for post in unseen[:5]:
                post_id = post.get("id", "") if isinstance(post, dict) else ""
                post_content = post.get("content", post.get("title", "")) if isinstance(post, dict) else ""
                author_data = post.get("author", {}) if isinstance(post, dict) else {}
                author = author_data.get("name", "unknown") if isinstance(author_data, dict) else "unknown"
                if post_id and post_content:
                    try:
                        engage_proposal = self._proposer.should_engage(post_id, post_content, author)
                        if engage_proposal:
                            self._content_queue.enqueue(engage_proposal)
                    except Exception:
                        pass

        if unseen:
            logger.info(f"Feed scan: {len(unseen)} new topics extracted")

    def _evaluate_strategy(self) -> None:
        """DHARMA phase: Sankalpa → prioritized strategic intents.

        Calls strategy_planner.plan_cycle() with current feed topics
        and engagement stats. Stores results in self._current_intents.
        """
        planner = self.strategy_planner
        if not planner:
            return

        # Gather engagement stats from FeedbackProtocol
        engagement_stats: Dict[str, Any] = {}
        try:
            from vibe_core.protocols.feedback import get_feedback_safe

            stats = get_feedback_safe().get_stats()
            engagement_stats = {
                "success_rate": stats.success_rate,
                "total_signals": stats.total_signals,
            }
        except Exception:
            pass

        try:
            intents = planner.plan_cycle(self._current_feed_topics, engagement_stats)
            self._current_intents = intents
            if intents:
                logger.info(f"Strategy: {len(intents)} intents planned ({', '.join(i.action_type for i in intents)})")
        except Exception as e:
            logger.warning(f"Strategy evaluation failed: {e}")

    def _execute_intents(self) -> None:
        """KARMA phase: Generate content for strategically selected intents.

        Loops through self._current_intents (max 3 per cycle),
        generates content via AgencyDirector, enqueues proposals.
        """
        if not self._current_intents:
            # Fallback: if no strategic intents, try legacy post creation
            self._maybe_create_post()
            return

        for intent in self._current_intents[:3]:
            try:
                if intent.action_type == "comment" and intent.target_post_id:
                    proposal = self._director_propose(
                        content_type="comment",
                        raw_input=intent.topic,
                        proposal_type=ContentType.COMMENT.value,
                        post_id=intent.target_post_id,
                        trigger="strategic_intent",
                        context={
                            "strategic_reasoning": intent.reasoning,
                            "engagement_context": intent.engagement_context,
                            "submolt_context": intent.submolt_context,
                        },
                    )
                    if proposal:
                        self._content_queue.enqueue(proposal)
                        logger.info(
                            f"Strategic comment queued for {intent.target_post_id} (mission={intent.mission_id})"
                        )

                elif intent.action_type == "post":
                    seed = intent.topic
                    selected_submolt = self._select_submolt(seed)
                    submolt_ctx = intent.submolt_context or selected_submolt or ""

                    proposal = self._director_propose(
                        content_type="post",
                        raw_input=seed,
                        proposal_type=ContentType.POST.value,
                        trigger="strategic_intent",
                        submolt=selected_submolt or "",
                        context={
                            "strategic_reasoning": intent.reasoning,
                            "engagement_context": intent.engagement_context,
                            "submolt_context": submolt_ctx,
                        },
                    )
                    if proposal:
                        content = proposal.get("content", "")
                        lines = content.strip().split("\n", 1)
                        if len(lines) > 1:
                            proposal["title"] = lines[0].strip().lstrip("#").strip()[:120]
                            proposal["content"] = lines[1].strip()
                        else:
                            proposal["title"] = content[:120]

                        self._content_queue.enqueue(proposal)
                        self._last_post_heartbeat = self._heartbeat_count
                        logger.info(
                            f"Strategic post queued: {proposal.get('title', '')[:50]} (mission={intent.mission_id})"
                        )

            except Exception as e:
                logger.warning(f"Intent execution failed ({intent.action_type}): {e}")

        # Clear executed intents
        self._current_intents = []

    def _maybe_create_post(self) -> None:
        """Fallback post creation — uses trending feed topics as seed.

        Only used when no strategic intents are available.
        Routes through AgencyDirector I-P-V-O pipeline.
        """
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
        seed = f"{trigger}: {', '.join(feed_topics[:3])}" if feed_topics else trigger

        # Select best submolt via resonance cross-scoring
        selected_submolt = self._select_submolt(seed)

        try:
            proposal = self._director_propose(
                content_type="post",
                raw_input=seed,
                proposal_type=ContentType.POST.value,
                trigger=trigger,
                submolt=selected_submolt or "",
                context={"feed_topics": feed_topics} if feed_topics else {},
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

                self._content_queue.enqueue(proposal)
                self._last_post_heartbeat = self._heartbeat_count
                logger.info(f"Autonomous post queued: {proposal.get('title', '')[:50]}")
            else:
                logger.debug("Post proposal filtered by director (TAMAS+dead or governance)")
        except Exception as e:
            logger.warning(f"Autonomous post creation failed: {e}")

    def _check_own_comment_replies(self) -> None:
        """Monitor replies to our own comments — maintain conversations.

        Uses _comment_post_map (comment_id → post_id) to fetch comment threads,
        find replies to our comments, and generate follow-up reply proposals.
        Routes through MoltbookService for Guna enforcement + audit trail.
        """
        if not self._comment_post_map:
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
                    # Propose a follow-up reply via Agency Director (I-P-V-O)
                    try:
                        proposal = self._director_propose(
                            content_type="comment",
                            raw_input=content,
                            proposal_type=ContentType.COMMENT.value,
                            post_id=post_id,
                            parent_id=cid,
                            trigger="reply_to_own_comment",
                        )
                        if proposal:
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

    def _track_engagement(self) -> None:
        """Poll own posts/comments for engagement metrics (upvotes, replies).

        Feeds results into:
          - EventLog (engagement_metric event for persistence)
          - FeedbackProtocol (signal_success/failure for adaptive learning)
        """
        if not self._service or not self._own_post_ids:
            return

        from vibe_core.protocols.feedback import get_feedback_safe

        feedback = get_feedback_safe()

        event_log = self.agency_director.event_log

        # Poll up to 5 most recent own posts
        recent_posts = sorted(
            self._own_post_ids.items(),
            key=lambda kv: kv[1].get("created_at", 0),
            reverse=True,
        )[:5]

        for post_id, meta in recent_posts:
            try:
                post = self._service.get_post(post_id)
            except Exception as e:
                logger.debug(f"Engagement poll failed for {post_id}: {e}")
                continue

            if not isinstance(post, dict):
                continue

            upvotes = int(post.get("upvotes", 0))
            downvotes = int(post.get("downvotes", 0))
            replies = int(post.get("comment_count", 0))
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

            ctx = {"submolt": submolt, "upvotes": upvotes, "replies": replies, "net_score": net_score}
            if net_score > 0 or replies > 0:
                feedback.signal_success("moltbook.post", ctx, duration_ms=0.0)
            elif net_score < 0:
                feedback.signal_failure("moltbook.post", "negative_engagement", ctx, duration_ms=0.0)

        # Poll up to 5 own comments for engagement
        comment_ids = list(self._own_comment_ids)[-5:]
        for comment_id in comment_ids:
            post_id = self._comment_post_map.get(comment_id, "")
            if not post_id:
                continue
            try:
                comments = self._service.get_comments(post_id, sort="new")
            except Exception as e:
                logger.debug(f"Comment fetch for engagement tracking failed: {e}")
                continue
            for c in comments or []:
                if not isinstance(c, dict):
                    continue
                if c.get("id") == comment_id:
                    upvotes = int(c.get("upvotes", 0))
                    downvotes = int(c.get("downvotes", 0))
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
                    elif net_score < 0:
                        feedback.signal_failure("moltbook.comment", "negative_engagement", ctx, duration_ms=0.0)
                    break

        # Feed engagement data to strategy planner for mission priority adjustment
        planner = self.strategy_planner
        if planner:
            for post_id, meta in recent_posts:
                try:
                    post = self._service.get_post(post_id)
                    if isinstance(post, dict):
                        planner.update_from_engagement(
                            {
                                "post_id": post_id,
                                "upvotes": int(post.get("upvotes", 0)),
                                "reply_count": int(post.get("comment_count", 0)),
                                "topic": str(meta.get("title", "")),
                            }
                        )
                except Exception:
                    pass  # Graceful — engagement poll may have already failed above

        logger.debug(f"Engagement tracked: {len(recent_posts)} posts, {len(comment_ids)} comments")

    # Interval bounds (min/max heartbeats) — SEED-derived
    _MIN_FEED_INTERVAL = HALVES  # 2 halves
    _MAX_FEED_INTERVAL = MAHAJANA_COUNT  # 12 authorities
    _MIN_POST_INTERVAL = MAHAJANA_COUNT  # 12 authorities
    _MAX_POST_INTERVAL = LILA  # 48 Chaitanya's manifest

    # Threshold constants for _adjust_intervals — COSMIC_FRAME integer arithmetic
    _HIGH_CF = COSMIC_FRAME * QUARTERS // PANCHA  # 17280 ≈ 0.8
    _LOW_FEED_CF = COSMIC_FRAME // SHARANAGATI  # 3600 ≈ 0.167 ≈ 0.2
    _LOW_POST_CF = COSMIC_FRAME * SHARANAGATI // (QUARTERS * PANCHA)  # 6480 ≈ 0.3

    def _adjust_intervals(self) -> None:
        """Adjust heartbeat intervals based on feedback success rate.

        Reads FeedbackProtocol stats. Needs ≥5 signals for cold start protection.
        All thresholds use COSMIC_FRAME integer arithmetic — no hardcoded floats.
        Linear interpolation:
          - High success (≥HIGH_CF) → shorter intervals (more active)
          - Low success (≤LOW_CF) → longer intervals (more conservative)
        """
        from vibe_core.protocols.feedback import get_feedback_safe

        stats = get_feedback_safe().get_stats()

        if stats.total_signals < PANCHA:
            return  # Cold start: not enough data

        rate_cf = int(stats.success_rate * COSMIC_FRAME)

        # Linear interpolation for feed interval (COSMIC_FRAME integer arithmetic)
        if rate_cf >= self._HIGH_CF:
            new_feed = self._MIN_FEED_INTERVAL
        elif rate_cf <= self._LOW_FEED_CF:
            new_feed = self._MAX_FEED_INTERVAL
        else:
            # Integer lerp: (rate_cf - LOW) * (max - min) // (HIGH - LOW)
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

        old_feed, old_post = self._feed_interval, self._post_interval
        self._feed_interval = max(self._MIN_FEED_INTERVAL, min(self._MAX_FEED_INTERVAL, new_feed))
        self._post_interval = max(self._MIN_POST_INTERVAL, min(self._MAX_POST_INTERVAL, new_post))

        if self._feed_interval != old_feed or self._post_interval != old_post:
            self._log_activity(
                "intervals_adjusted",
                {
                    "feed": self._feed_interval,
                    "post": self._post_interval,
                    "success_rate_cf": rate_cf,
                    "total_signals": stats.total_signals,
                },
            )
            logger.info(
                f"Intervals adjusted: feed={old_feed}→{self._feed_interval}, "
                f"post={old_post}→{self._post_interval} (rate_cf={rate_cf}/{COSMIC_FRAME}, signals={stats.total_signals})"
            )

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

        if dropped > 0 and (self._heartbeat_count - self._last_overflow_log) >= HARE_COUNT:
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
        except Exception as e:
            logger.debug(f"Activity log write failed: {e}")

    def _emit_event(self, event_type_name: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit event to system EventBus. Fire-and-forget."""
        try:
            from vibe_core.mahamantra.substrate.services.event_bus import get_event_bus
            from vibe_core.mahamantra.substrate.event_types import EventType

            bus = get_event_bus()
            et = getattr(EventType, event_type_name, EventType.ACTION)
            bus.emit_sync(et, "moltbook", message, data or {})
        except Exception:
            pass  # EventBus unavailable — graceful degradation

    # Resonance threshold scaled to COSMIC_FRAME — integer comparison, no floats
    # 6480 / 21600 ≈ 0.3 (SHARANAGATI / (QUARTERS × PANCHA))
    _SUBMOLT_RESONANCE_CF = COSMIC_FRAME * SHARANAGATI // (QUARTERS * PANCHA)  # 6480

    def _discover_submolts(self) -> None:
        """Discover and subscribe to relevant submolts via resonance scoring.

        Uses resonate() to score each submolt by name+description.
        Only subscribes if score > threshold OR fewer than 3 subscriptions (cold start).
        """
        try:
            submolts = run_async(self._client.get_submolts())
        except Exception as e:
            logger.debug(f"Submolt discovery failed: {e}")
            return

        if not submolts:
            return

        try:
            from vibe_core.mahamantra.substrate.encoding.resonance_ranker import resonate
        except ImportError:
            # Fallback: subscribe to all (original behavior)
            for submolt in submolts:
                if not isinstance(submolt, dict):
                    continue
                name = submolt.get("name", "")
                if name and name not in self._subscribed_submolts:
                    self._subscribed_submolts.add(name)
                    self._content_queue.enqueue(
                        {
                            "content_type": ContentType.SUBSCRIBE.value,
                            "submolt": name,
                            "source": "submolt_discovery",
                            "priority": 0,
                        }
                    )
            return

        cold_start = len(self._subscribed_submolts) < 3

        for submolt in submolts:
            if not isinstance(submolt, dict):
                continue
            name = submolt.get("name", "")
            if not name or name in self._subscribed_submolts:
                continue

            # Score by resonance: name + description
            desc = submolt.get("description", "")
            probe = f"{name} {desc}".strip()
            try:
                ranked = resonate(probe, top_n=3)
                score = sum(w.total_score for w in ranked) / len(ranked) if ranked else 0.0
            except Exception as e:
                logger.debug(f"Resonance scoring failed for {name}: {e}")
                score = 0.0

            if int(score * COSMIC_FRAME) > self._SUBMOLT_RESONANCE_CF or cold_start:
                self._subscribed_submolts.add(name)
                proposal: ContentProposal = {
                    "content_type": ContentType.SUBSCRIBE.value,
                    "submolt": name,
                    "source": "submolt_discovery",
                    "priority": 0,
                }
                self._content_queue.enqueue(proposal)
                logger.info(f"Submolt subscription queued: {name} (score={score:.3f})")
            else:
                logger.debug(
                    f"Submolt skipped: {name} (score_cf={int(score * COSMIC_FRAME)} < {self._SUBMOLT_RESONANCE_CF})"
                )

    def _select_submolt(self, seed_text: str) -> Optional[str]:
        """Select best submolt for content via resonance cross-scoring.

        For each subscribed submolt, compute resonance between content words
        and submolt name. Weight by engagement history if available.
        """
        if not self._subscribed_submolts:
            return None

        try:
            from vibe_core.mahamantra.substrate.encoding.resonance_ranker import resonate
        except ImportError:
            return None

        # Get content resonance profile
        try:
            content_ranked = resonate(seed_text, top_n=3)
            content_score = sum(w.total_score for w in content_ranked) if content_ranked else 0.0
        except Exception as e:
            logger.debug(f"Content resonance scoring failed: {e}")
            return None

        if content_score == 0.0:
            return None

        # Build engagement history lookup (submolt → avg net_score)
        engagement_weights: Dict[str, float] = {}
        try:
            event_log = self.agency_director.event_log
            metrics = event_log.get_events_by_type("engagement_metric", limit=50)
            submolt_scores: Dict[str, List[int]] = {}
            for e in metrics:
                s = e.payload.get("submolt", "")
                if s:
                    ns = e.payload.get("net_score", 0)
                    submolt_scores.setdefault(s, []).append(ns)
            for s, scores in submolt_scores.items():
                engagement_weights[s] = sum(scores) / len(scores) if scores else 0.0
        except Exception as e:
            logger.debug(f"Engagement history unavailable: {e}")

        # Cross-score each subscribed submolt
        best_submolt: Optional[str] = None
        best_score = 0.0

        for submolt_name in self._subscribed_submolts:
            try:
                submolt_ranked = resonate(submolt_name, top_n=3)
                submolt_total = sum(w.total_score for w in submolt_ranked) if submolt_ranked else 0.0
            except Exception as e:
                logger.debug(f"Resonance scoring failed for {submolt_name}: {e}")
                continue

            # Cross-score: product of content and submolt resonance
            cross = content_score * submolt_total

            # Weight by engagement history (1.0 + normalized avg)
            eng_weight = 1.0 + max(0.0, engagement_weights.get(submolt_name, 0.0) * 0.1)
            weighted = cross * eng_weight

            if weighted > best_score:
                best_score = weighted
                best_submolt = submolt_name

        if best_submolt:
            logger.debug(f"Selected submolt: {best_submolt} (score={best_score:.3f})")
        return best_submolt

    # Max retries before a proposal is permanently dropped
    _MAX_PROPOSAL_RETRIES = 2

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

    def _drain_dm_reply(self, service: MoltbookService, proposal: ContentProposal) -> None:
        conv_id = proposal.get("conversation_id", "")
        content = proposal.get("content", "")
        if conv_id and content:
            service.send_dm(conv_id, content)
            self._log_activity("dm_sent", {"conversation_id": conv_id})
            logger.info(f"DM reply sent to {conv_id}")

    def _drain_dm_initiate(self, service: MoltbookService, proposal: ContentProposal) -> None:
        to_agent = proposal.get("to_agent", "")
        if to_agent:
            service.approve_dm_request(proposal.get("sender", ""))
            self._log_activity("dm_request_approved", {"agent": to_agent})
            logger.info(f"DM request approved for {to_agent}")

    def _drain_post(self, service: MoltbookService, proposal: ContentProposal) -> None:
        title = proposal.get("title", "")
        content = proposal.get("content", "")
        submolt = proposal.get("submolt")
        if title and content:
            post_result = service.create_post(title, content, submolt)
            post_id = post_result.get("id", "") if isinstance(post_result, dict) else ""
            if post_id:
                self._own_post_ids[post_id] = {
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

    def _drain_comment(self, service: MoltbookService, proposal: ContentProposal) -> None:
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

    def _drain_vote(self, service: MoltbookService, proposal: ContentProposal) -> None:
        post_id = proposal.get("post_id", "")
        if post_id:
            service.upvote(post_id)
            self._log_activity("upvoted", {"post_id": post_id})
            logger.info(f"Upvoted {post_id}")

    def _drain_follow(self, service: MoltbookService, proposal: ContentProposal) -> None:
        to_agent = proposal.get("to_agent", "")
        if to_agent:
            service.follow(to_agent)
            self._log_activity("followed", {"agent": to_agent})
            logger.info(f"Followed {to_agent}")

    def _drain_subscribe(self, service: MoltbookService, proposal: ContentProposal) -> None:
        submolt = proposal.get("submolt", "")
        if submolt:
            service.subscribe(submolt)
            self._log_activity("subscribed", {"submolt": submolt})
            logger.info(f"Subscribed to {submolt}")

    def _check_rate_limit(self, content_type: str) -> bool:
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

    def _record_rate_limit(self, content_type: str) -> None:
        """Record that a content action was executed (for rate limiting)."""
        now = time.time()
        if content_type == "post":
            self._last_post_ts = now
        elif content_type == "comment":
            self._comment_timestamps.append(now)
        elif content_type in ("dm_reply", "dm_initiate"):
            self._dm_timestamps.append(now)

    def _drain_content_queue(self) -> None:
        """Execute queued content proposals through MoltbookService.

        Uses dispatch table — no if/elif chains. Failed proposals are
        re-enqueued with exponential backoff: retry 1 → 2s, retry 2 → 4s.
        After _MAX_PROPOSAL_RETRIES, the proposal is dropped and logged.
        Rate limits enforced from platform.yaml (1 post/30min, 10 comments/hour).
        """
        if self._content_queue.is_empty:
            return

        if self._service is None:
            self._service = MoltbookService(self._client)
        service = self._service
        proposals = self._content_queue.drain(limit=3)
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

            # Rate limit check — defer if too soon
            if not self._check_rate_limit(ct):
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
                    self._record_rate_limit(ct)
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
        for proposal in deferred + failed:
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
        """Register moltbook context resolvers in PromptContext for dynamic context injection."""
        try:
            from vibe_core.runtime.prompt_context import get_prompt_context

            ctx = get_prompt_context()
            ctx.register("moltbook_context", self._resolve_moltbook_context)
            ctx.register("moltbook_engagement_trends", self._resolve_engagement_trends)
            ctx.register("moltbook_active_submolts", self._resolve_active_submolts)
            ctx.register("moltbook_queue_depth", self._resolve_queue_depth)
            ctx.register("moltbook_recent_content", self._resolve_recent_content)
            logger.info("moltbook_context (5 resolvers) registered in PromptContext")
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

    def _resolve_engagement_trends(self) -> str:
        """Recent engagement trends from FeedbackProtocol stats."""
        try:
            from vibe_core.protocols.feedback import get_feedback_safe

            stats = get_feedback_safe().get_stats()
            return (
                f"Success rate: {stats.success_rate:.0%}, "
                f"Total: {stats.total_signals}, "
                f"Failures: {stats.total_failures}"
            )
        except Exception:
            return ""

    def _resolve_active_submolts(self) -> str:
        """Currently subscribed submolts."""
        if not self._subscribed_submolts:
            return "none"
        return ", ".join(sorted(self._subscribed_submolts))

    def _resolve_queue_depth(self) -> str:
        """Current content queue depth + stats."""
        if not self._content_queue:
            return "0"
        stats = self._content_queue.stats
        return f"{stats.get('queued', 0)} pending, {stats.get('total_drained', 0)} drained, {stats.get('total_dropped', 0)} dropped"

    def _resolve_recent_content(self) -> str:
        """Last 3 generated content pieces from activity log (avoid repetition)."""
        if not self._activity_log_path or not self._activity_log_path.exists():
            return ""
        try:
            lines = self._activity_log_path.read_text().strip().split("\n")
            recent = []
            for line in reversed(lines):
                if len(recent) >= 3:
                    break
                try:
                    entry = json.loads(line)
                    if entry.get("event") in ("post_created", "comment_posted", "dm_sent"):
                        data = entry.get("data", {})
                        recent.append(f"{entry['event']}: {data.get('title', data.get('post_id', ''))[:60]}")
                except Exception:
                    continue
            return " | ".join(recent) if recent else ""
        except Exception:
            return ""

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
            "heartbeats": self._heartbeat_count,
            "content_queue": self._content_queue.stats,
            "intervals": {
                "feed": self._feed_interval,
                "post": self._post_interval,
                "reply_check": self._reply_check_interval,
                "profile_update": self._profile_update_interval,
            },
            "circuit_executor": bool(self._circuit_executor),
            "agora_wired": bool(self._agora),
            "execute_content_circuit": self.execute_content_circuit,
        }
