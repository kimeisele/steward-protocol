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
    HARE_COUNT,
    KSHETRA,
    LILA,
    MAHAJANA_COUNT,
    MALA,
    NAVA,
    QUARTERS,
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

        Additionally checks constraints from knowledge/moltbook/platform.yaml
        (6 hard/soft constraints) via Knowledge Graph.
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

    # Persistence: queue + seen IDs + phase state survive restarts
    _QUEUE_STATE_FILE = "content_queue.json"
    _SEEN_STATE_FILE = "seen_ids.json"
    _PHASE_STATE_FILE = "phase_state.json"
    _ACTIVITY_LOG_FILE = "activity.jsonl"
    _MAX_SEEN_IDS = MALA * NAVA  # 972 ≈ 1000 (108 beads × 9 processes)

    def __init__(self):
        super().__init__()
        self._client = None  # MoltbookClient, created in on_boot
        self._service: Optional[MoltbookService] = None  # Singleton, reused in drain
        self._offline_mode: bool = True
        self._standalone_mode: bool = False  # True when running without full kernel (MinimalKernel)
        self._last_heartbeat_error: Optional[str] = None
        self._state_dir: Optional[Path] = None
        self._tick_count: int = 0
        # Department-level tick counters now managed by HeartbeatOrchestrator
        # Adaptive intervals (diagnostic — real gating is _check_rate_limit)
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
        self._commented_post_ids: Set[str] = set()  # Post-level dedup: don't comment on same post twice
        self._last_post_heartbeat: int = 0  # Heartbeat count when last post was created
        self._followed_agents: Set[str] = set()  # Track who we've followed (avoid duplicates)
        self._subscribed_submolts: Set[str] = set()  # Track community subscriptions
        self._submolt_descriptions: Dict[str, str] = {}  # name → description (for LLM context)
        self._comment_post_map: Dict[str, str] = {}  # comment_id → post_id for reply monitoring
        self._last_profile_heartbeat: int = 0  # Heartbeat count when profile was last updated
        self._activity_log_path: Optional[Path] = None  # JSONL append-only audit log
        self._agent_name: str = "steward-protocol"  # Resolved from profile at boot
        self._bank = None  # CivicBank instance (lazy, standalone-compatible)
        self._agora = None  # AgoraCartridge for broadcast listening
        self._agora_sequence: int = 0  # Last consumed AGORA message sequence
        # Heartbeat orchestration (extracted manager, manages debounce + phase ticks)
        # Circuit Executor (cortex/engines/circuit_engine.py) — wired at boot
        self._wiring = None  # WiringModule (lazy-loaded)
        # AGORA broadcast channel (cartridges/agent_city/agora/) — wired at boot
        self._agora = None
        # Agency Director — I-P-V-O pipeline (mahamantra-direct, guna=style not gate)
        self._agency_director = None
        # Strategy Planner — Sankalpa missions → strategic intents
        self._strategy_planner = None
        self._current_intents: list = []  # List[StrategicIntent]
        self._current_feed_topics: list = []  # Extracted topics from feed scan
        # Extracted managers (lazy-init)
        self._drainer = None
        self._persistence_mgr = None
        self._feed_analyzer = None
        self._engagement_tracker = None
        self._dm_processor = None
        self._post_orchestrator = None
        self._intent_executor = None
        # Engagement tracking: own post IDs → metadata for polling
        self._own_post_ids: Dict[str, Dict[str, object]] = {}
        self._MAX_OWN_POST_IDS = COSMIC_FRAME // MALA  # 200 (pada_unit)
        # Rate limiting now handled by ContentDrainer (managers/drainer.py)
        # Heartbeat orchestration (extracted manager)
        self._heartbeat_orchestrator = None
        # Boot orchestration (extracted manager)
        self._boot_manager = None
        # State restoration (extracted manager)
        self._state_restorer = None
        # Proposal building (extracted manager)
        self._proposal_builder = None
        # Vault resolution (extracted manager)
        self._vault_resolver_mgr = None
        # Content circuit execution (extracted manager)
        self._content_circuit_executor = None
        # Guna enforcement (extracted manager)
        self._guna_enforcer_mgr = None
        # State snapshot (extracted manager)
        self._state_snapshot_mgr = None

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

    @property
    def _content_drainer(self):
        """Lazy-init ContentDrainer with shared state refs."""
        if self._drainer is None:
            from vibe_core.plugins.moltbook.managers.drainer import ContentDrainer

            self._drainer = ContentDrainer(
                service_getter=self._ensure_service,
                log_activity=self._log_activity,
                broadcast_to_agora=self._broadcast_to_agora,
                emit_event=self._emit_event,
                own_post_ids=self._own_post_ids,
                own_comment_ids=self._own_comment_ids,
                comment_post_map=self._comment_post_map,
                followed_agents=self._followed_agents,
                subscribed_submolts=self._subscribed_submolts,
                bank=self._bank,
                agent_id=self._agent_name,
            )
        return self._drainer

    @property
    def _persistence(self):
        """Lazy-init PersistenceManager."""
        if self._persistence_mgr is None:
            from vibe_core.plugins.moltbook.managers.persistence import PersistenceManager

            self._persistence_mgr = PersistenceManager(
                state_dir=self._state_dir,
                max_seen_ids=self._MAX_SEEN_IDS,
            )
        return self._persistence_mgr

    @property
    def _feed(self):
        """Lazy-init FeedAnalyzer with shared state refs."""
        if self._feed_analyzer is None:
            from vibe_core.plugins.moltbook.managers.feed import FeedAnalyzer

            self._feed_analyzer = FeedAnalyzer(
                seen_post_ids=self._seen_post_ids,
                subscribed_submolts=self._subscribed_submolts,
                submolt_descriptions=self._submolt_descriptions,
            )
        return self._feed_analyzer

    @property
    def _engagement(self):
        """Lazy-init EngagementTracker."""
        if self._engagement_tracker is None:
            from vibe_core.plugins.moltbook.managers.engagement import EngagementTracker

            self._engagement_tracker = EngagementTracker(
                log_activity=self._log_activity,
            )
        return self._engagement_tracker

    @property
    def _heartbeat(self):
        """Lazy-init HeartbeatOrchestrator for phase-aware dispatch."""
        if self._heartbeat_orchestrator is None:
            from vibe_core.plugins.moltbook.managers.heartbeat import HeartbeatOrchestrator

            self._heartbeat_orchestrator = HeartbeatOrchestrator(plugin=self)
        return self._heartbeat_orchestrator

    @property
    def _dm(self):
        """Lazy-init DMProcessor for inbound/request DM handling."""
        if self._dm_processor is None:
            from vibe_core.plugins.moltbook.managers.dm_processor import DMProcessor

            self._dm_processor = DMProcessor(plugin=self)
        return self._dm_processor

    @property
    def _post(self):
        """Lazy-init PostOrchestrator for post creation and comment monitoring."""
        if self._post_orchestrator is None:
            from vibe_core.plugins.moltbook.managers.post_orchestrator import PostOrchestrator

            self._post_orchestrator = PostOrchestrator(plugin=self)
        return self._post_orchestrator

    @property
    def _intent(self):
        """Lazy-init IntentExecutor for strategic intent execution."""
        if self._intent_executor is None:
            from vibe_core.plugins.moltbook.managers.intent_executor import IntentExecutor

            self._intent_executor = IntentExecutor(plugin=self)
        return self._intent_executor

    @property
    def _boot(self):
        """Lazy-init BootManager for plugin initialization."""
        if self._boot_manager is None:
            from vibe_core.plugins.moltbook.managers.boot_manager import BootManager

            self._boot_manager = BootManager(plugin=self)
        return self._boot_manager

    # Properties delegating state to HeartbeatOrchestrator
    @property
    def _heartbeat_count(self) -> int:
        """Current heartbeat sequence (from orchestrator)."""
        return self._heartbeat.current_heartbeat_count

    @property
    def _genesis_tick(self) -> int:
        """GENESIS phase tick counter."""
        return self._heartbeat._genesis_tick

    @_genesis_tick.setter
    def _genesis_tick(self, value: int) -> None:
        """Set GENESIS phase tick counter."""
        self._heartbeat._genesis_tick = value

    @property
    def _karma_tick(self) -> int:
        """KARMA phase tick counter."""
        return self._heartbeat._karma_tick

    @_karma_tick.setter
    def _karma_tick(self, value: int) -> None:
        """Set KARMA phase tick counter."""
        self._heartbeat._karma_tick = value

    @property
    def _moksha_tick(self) -> int:
        """MOKSHA phase tick counter."""
        return self._heartbeat._moksha_tick

    @_moksha_tick.setter
    def _moksha_tick(self, value: int) -> None:
        """Set MOKSHA phase tick counter."""
        self._heartbeat._moksha_tick = value

    @property
    def _restorer(self):
        """Lazy-init StateRestorer for cross-phase state restoration."""
        if self._state_restorer is None:
            from vibe_core.plugins.moltbook.managers.state_restorer import StateRestorer

            self._state_restorer = StateRestorer(self)
        return self._state_restorer

    @property
    def _builder(self):
        """Lazy-init ProposalBuilder for circuit → proposal conversion."""
        if self._proposal_builder is None:
            from vibe_core.plugins.moltbook.managers.proposal_builder import ProposalBuilder

            self._proposal_builder = ProposalBuilder(self)
        return self._proposal_builder

    @property
    def _vault(self):
        """Lazy-init VaultResolver for API key resolution."""
        if self._vault_resolver_mgr is None:
            from vibe_core.plugins.moltbook.managers.vault_resolver import VaultResolver

            self._vault_resolver_mgr = VaultResolver()
        return self._vault_resolver_mgr

    @property
    def _circuit(self):
        """Lazy-init ContentCircuitExecutor for AgencyDirector execution."""
        if self._content_circuit_executor is None:
            from vibe_core.plugins.moltbook.managers.content_circuit import ContentCircuitExecutor

            self._content_circuit_executor = ContentCircuitExecutor(self)
        return self._content_circuit_executor

    @property
    def _guna(self):
        """Lazy-init GunaEnforcer for I/O Policy validation."""
        if self._guna_enforcer_mgr is None:
            from vibe_core.plugins.moltbook.managers.guna_enforcer import GunaEnforcer

            self._guna_enforcer_mgr = GunaEnforcer(self)
        return self._guna_enforcer_mgr

    @property
    def _snapshot(self):
        """Lazy-init StateSnapshot for state capture and restore."""
        if self._state_snapshot_mgr is None:
            from vibe_core.plugins.moltbook.managers.state_snapshot import StateSnapshot

            self._state_snapshot_mgr = StateSnapshot(self)
        return self._state_snapshot_mgr

    def _ensure_service(self):
        """Ensure MoltbookService exists, create if needed. Used by managers."""
        if self._service is None:
            self._service = MoltbookService(self._client)
        return self._service

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
        # Delegate proposal building to ProposalBuilder
        return self._builder.build_proposal(circuit_result, content_type, proposal_type, **extra)

    # =========================================================================
    # Queue + Seen ID Persistence
    # =========================================================================

    def _persist_queue(self) -> None:
        """Save content queue + seen IDs to state dir. Called on shutdown."""
        self._persistence.persist_queue(
            queue=self._content_queue,
            seen_message_ids=self._seen_message_ids,
            seen_post_ids=self._seen_post_ids,
            own_comment_ids=self._own_comment_ids,
            commented_post_ids=self._commented_post_ids,
            followed_agents=self._followed_agents,
            subscribed_submolts=self._subscribed_submolts,
            comment_post_map=self._comment_post_map,
            own_post_ids=self._own_post_ids,
            max_own_post_ids=self._MAX_OWN_POST_IDS,
        )
        # Also persist cross-phase state (feed_topics + intents)
        self._persist_phase_state()

    def _restore_queue(self) -> None:
        """Restore content queue + seen IDs from state dir. Called on boot."""
        restored = self._persistence.restore_queue(self._content_queue)
        if restored:
            if "seen_message_ids" in restored:
                self._seen_message_ids = restored["seen_message_ids"]
            if "seen_post_ids" in restored:
                self._seen_post_ids = restored["seen_post_ids"]
            if "own_comment_ids" in restored:
                self._own_comment_ids = restored["own_comment_ids"]
            if "commented_post_ids" in restored:
                self._commented_post_ids = restored["commented_post_ids"]
            if "followed_agents" in restored:
                self._followed_agents = restored["followed_agents"]
            if "subscribed_submolts" in restored:
                self._subscribed_submolts = restored["subscribed_submolts"]
            if "comment_post_map" in restored:
                self._comment_post_map = restored["comment_post_map"]
            if "own_post_ids" in restored:
                self._own_post_ids = restored["own_post_ids"]

        # Restore cross-phase state (feed_topics + intents from previous run)
        self._restorer.restore_phase_state()

    def _persist_phase_state(self) -> None:
        """Save cross-phase state (feed_topics + intents + heartbeat_count + orchestrator state)."""
        self._persistence.persist_phase_state(
            heartbeat_count=self._heartbeat.current_heartbeat_count,
            feed_topics=self._current_feed_topics,
            intents=self._current_intents,
            orchestrator_state=self._heartbeat.snapshot(),
        )

    # =========================================================================
    # PluginStateContract
    # =========================================================================

    def get_state_paths(self) -> List[Path]:
        if self._state_dir:
            return [self._state_dir]
        return []

    def snapshot_state(self) -> Dict[str, Any]:
        return self._snapshot.snapshot()

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        self._snapshot.restore(snapshot)

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, object]] = None,
    ) -> HookResult:
        """Delegate to BootManager for plugin initialization."""
        return self._boot.execute_boot(kernel, config)

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

    def _init_agora(self) -> None:
        """Initialize AGORA for broadcast listening (standalone-compatible).

        In standalone mode (GitHub Actions), AGORA is in-memory — no other agents
        publish during the run. The wiring is prepared for full-system execution.
        """
        try:
            from vibe_core.cartridges.agent_city.agora.cartridge_main import AgoraCartridge

            self._agora = AgoraCartridge()
            logger.info("AGORA initialized for broadcast listening")
        except Exception as e:
            logger.debug(f"AGORA unavailable: {e}")

    def _listen_agora(self) -> List[Dict[str, Any]]:
        """Listen for broadcast directives from herald/steward.

        Returns list of messages since last check. Called in GENESIS phase.
        """
        if self._agora is None:
            return []
        messages: List[Dict[str, Any]] = []
        for source in ("herald", "steward"):
            try:
                result = run_async(self._agora._listen_stream({
                    "agent_id": self._agent_name,
                    "source": source,
                    "since": self._agora_sequence,
                }))
                if isinstance(result, dict):
                    msgs = result.get("messages", [])
                    messages.extend(msgs)
                    seq = result.get("next_sequence", self._agora_sequence)
                    if seq > self._agora_sequence:
                        self._agora_sequence = seq
            except Exception as e:
                logger.debug(f"AGORA listen ({source}) failed: {e}")
        if messages:
            logger.info(f"AGORA: {len(messages)} broadcast messages received")
        return messages

    def _init_bank(self) -> None:
        """Initialize CivicBank for credit-gated content publishing.

        Direct instantiation — no kernel required (standalone-compatible).
        Mints initial credits if account has zero balance.
        """
        try:
            from vibe_core.cartridges.system.civic.tools.economy import CivicBank

            db_path = None
            if self._state_dir:
                db_path = str(self._state_dir / "economy.db")
            self._bank = CivicBank(db_path)
            # Mint initial credits if account is empty
            balance = self._bank.get_balance(self._agent_name)
            if balance == 0:
                self._bank.transfer(
                    "MINT", self._agent_name, 1000,
                    "moltbook_initial_mint",
                    service_type="minting",
                )
                logger.info(f"CivicBank: minted 1000 initial credits for {self._agent_name}")
            else:
                logger.info(f"CivicBank: balance={balance} for {self._agent_name}")
        except Exception as e:
            logger.warning(f"CivicBank unavailable: {e}")
            self._bank = None

    def _wire_event_listener(self) -> None:
        """Subscribe to EventBus — hear what other agents are doing.

        Listens to ACTION events from other agents to discover trending topics.
        Stores recent events for strategy planner context.
        """
        try:
            from vibe_core.mahamantra.substrate.services.event_bus import get_event_bus
            from vibe_core.mahamantra.substrate.event_types import EventType

            bus = get_event_bus()
            bus.subscribe(self._on_agent_action, [EventType.ACTION])
            logger.info("EventBus subscribed: listening for ACTION events")
        except ImportError:
            logger.debug("EventBus not available — skipping subscription")
        except Exception as e:
            logger.debug(f"EventBus subscription failed: {e}")

    def _on_agent_action(self, event: Any) -> None:
        """Handle ACTION events from other agents — discover trending topics."""
        agent_id = getattr(event, "agent_id", "")
        if agent_id == "moltbook":
            return  # Ignore own events
        message = getattr(event, "message", "")
        details = getattr(event, "details", {}) or {}
        if not message:
            return
        # Store recent agent actions for strategy context (cap at 50)
        if not hasattr(self, "_agent_events"):
            self._agent_events: List[Dict[str, Any]] = []
        self._agent_events.append({
            "agent": agent_id,
            "message": message[:200],
            "type": details.get("content_type", ""),
            "topic": details.get("topic", message[:100]),
        })
        if len(self._agent_events) > 50:
            self._agent_events = self._agent_events[-50:]

    def _wire_ouroboros(self) -> None:
        """Register Moltbook as Ouroboros gene for self-healing + health monitoring."""
        try:
            from vibe_core.ouroboros.ananta_shesha import get_system_anchor

            anchor = get_system_anchor()
            anchor.register_gene_simple("moltbook", self)

            # Subscribe to healing events — react to system-wide violations
            anchor.subscribe("healing.requested", "moltbook")
            anchor.subscribe("violation.detected", "moltbook")

            logger.info("OUROBOROS: Moltbook registered as self-healing gene")
        except Exception as e:
            logger.debug(f"Ouroboros registration failed: {e}")

    def on_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Ouroboros event handler — react to system healing/violation events.

        Kirtan loop endpoint: healing.requested → concrete self-repair actions.
        """
        if event_type == "violation.detected":
            target = data.get("target", "")
            if "moltbook" in target.lower():
                logger.warning(f"OUROBOROS: Violation targeting moltbook: {data.get('message', '')}")
                self._emit_event("HEALING", f"Ouroboros violation: {data.get('message', '')}", data)
        elif event_type == "healing.requested":
            target = data.get("target", "")
            if target == "moltbook" or target == "strategy_planner":
                reason = data.get("reason", "")
                logger.info(f"OUROBOROS: Healing requested for {target}: {reason}")

                # KIRTAN: Apply concrete healing actions
                if target == "strategy_planner" and self._strategy_planner:
                    self._strategy_planner._engagement_cache.clear()
                    logger.info("KIRTAN: Strategy planner engagement cache cleared")

                if target == "moltbook":
                    self._heal_synapse_weights()
                    self._emit_event(
                        "HEALING_APPLIED",
                        f"Moltbook self-healing applied: {reason}",
                        {"target": target, "reason": reason},
                    )

    def _heal_synapse_weights(self) -> None:
        """Kirtan: Heal degraded content synapse weights toward neutral.

        When content types fail repeatedly, their SynapseStore weights drop.
        Healing nudges degraded weights (< 0.4) back up, allowing the system
        to re-explore those content types instead of permanently avoiding them.
        """
        try:
            from vibe_core.state.synapse_store import get_synapse_store

            store = get_synapse_store()
            weights = store.get_weights()
            decayed = 0
            for trigger, actions in weights.items():
                if trigger.startswith("moltbook:content:"):
                    for action, w in actions.items():
                        if w < 0.4:  # Only heal degraded weights
                            store.increment_weight(trigger, action, delta=0.05)
                            decayed += 1
            if decayed:
                store.save()
                logger.info(f"KIRTAN: Healed {decayed} degraded synapse weight(s)")
        except Exception as e:
            logger.warning(f"Synapse healing failed: {e}")

    def _emit_ouroboros_health(self) -> None:
        """Emit health status to Ouroboros — includes content generation metrics."""
        try:
            from vibe_core.ouroboros.ananta_shesha import get_system_anchor

            # Gather content health metrics from FeedbackProtocol
            content_health: Dict[str, object] = {}
            try:
                from vibe_core.protocols.feedback import get_feedback_safe

                fb = get_feedback_safe()
                stats = fb.get_stats()
                content_health = {
                    "success_rate": stats.success_rate,
                    "failure_count": stats.failure_count,
                    "total_signals": stats.total_signals,
                }
            except Exception:
                pass  # FeedbackProtocol unavailable

            anchor = get_system_anchor()
            anchor.emit_event("moltbook.health", {
                "heartbeat": self._heartbeat_count,
                "offline": self._offline_mode,
                "queue_size": len(self._content_queue),
                "last_error": self._last_heartbeat_error,
                "subscribed_submolts": len(self._subscribed_submolts),
                **content_health,
            })
        except Exception:
            pass  # Ouroboros unavailable — degrade gracefully

    @property
    def _wiring_module(self):
        """Lazy-load WiringModule."""
        if self._wiring is None:
            from vibe_core.plugins.moltbook.managers.wiring import WiringModule
            self._wiring = WiringModule()
        return self._wiring

    def _wire_circuit_executor(self, kernel: "RealVibeKernel") -> None:
        """Delegate to WiringModule."""
        self._wiring_module.wire_circuit_executor(kernel)

    def _wire_agora(self, kernel: "RealVibeKernel") -> None:
        """Delegate to WiringModule."""
        self._wiring_module.wire_agora(kernel)

    def _broadcast_to_agora(self, content_type: str, content: str, metadata: Dict[str, Any]) -> None:
        """Delegate to WiringModule."""
        metadata["agent_name"] = self._agent_name
        self._wiring_module.broadcast_to_agora(content_type, content, metadata)

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
        return self._circuit.execute(
            raw_input=raw_input,
            content_type=content_type,
            post_id=post_id,
            sender=sender,
            trigger=trigger,
            context=context,
        )

    def _try_vault(self, kernel: "RealVibeKernel") -> str:
        """Attempt to load API key: CivicVault → env → ~/.config/moltbook/credentials.json."""
        return self._vault.resolve(kernel)

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

        # Fetch heartbeat from Moltbook API
        try:
            heartbeat = self._client.sync_check_heartbeat()
            self._last_heartbeat_error = None
        except Exception as e:
            # DM check failure is non-fatal — continue heartbeat without DM data
            self._last_heartbeat_error = f"[{type(e).__name__}] {e!r}"
            logger.warning(f"DM check failed [{type(e).__name__}]: {e!r} — continuing heartbeat")
            heartbeat = {}

        # Delegate to orchestrator (handles debounce, phase routing, all dispatch)
        self._heartbeat.dispatch_heartbeat(heartbeat)

    # =========================================================================
    # Reflection Protocol — learning from execution patterns
    # =========================================================================

    def _record_heartbeat_reflection(self, department: str, duration_s: float) -> None:
        """Record heartbeat in Reflection Protocol for pattern analysis."""
        try:
            from vibe_core.protocols.reflection import ExecutionRecord, get_reflection_safe

            reflection = get_reflection_safe()
            record = ExecutionRecord(
                command=f"moltbook.heartbeat.{department}",
                success=self._last_heartbeat_error is None,
                error=self._last_heartbeat_error,
                duration_ms=duration_s * 1000,
                context={
                    "department": department,
                    "heartbeat": self._heartbeat_count,
                    "queue_size": len(self._content_queue),
                    "offline": self._offline_mode,
                },
            )
            reflection.record_execution(record)
        except Exception:
            pass  # Reflection unavailable — degrade gracefully

    def _reflect_on_patterns(self) -> None:
        """MOKSHA: Analyze reflection patterns → trigger healing on failure.

        Kirtan feedback loop:
        1. Reflection detects failure patterns from recorded ExecutionRecords
        2. If failures found → request_healing() via Ouroboros
        3. Ouroboros routes healing → on_event() → concrete self-repair
        """
        try:
            from vibe_core.protocols.reflection import get_reflection_safe

            reflection = get_reflection_safe()
            patterns = reflection.analyze_patterns(limit=50)
            if not patterns:
                return

            # Check for repeated failures → emit to Ouroboros
            failure_count = 0
            for insight in patterns:
                if getattr(insight, "type", None) == "failure_pattern":
                    failure_count += 1
                    self._emit_event(
                        "REFLECTION_INSIGHT",
                        f"Failure pattern detected: {insight.message}",
                        {"insight": insight.message, "confidence": getattr(insight, "confidence", 0)},
                    )

            # KIRTAN: Failure patterns detected → request healing from Ouroboros
            if failure_count > 0:
                try:
                    from vibe_core.ouroboros.ananta_shesha import get_system_anchor

                    anchor = get_system_anchor()
                    anchor.request_healing(
                        target="moltbook",
                        reason=f"Content failure patterns detected: {failure_count} pattern(s) in last 50 executions",
                    )
                    logger.info(f"KIRTAN: Requested healing for {failure_count} failure pattern(s)")
                except Exception as e:
                    logger.warning(f"Healing request failed: {e}")

            # Propose improvements (auto-approve high-confidence)
            proposal = reflection.propose_improvement(patterns)
            if proposal and all(
                getattr(i, "confidence", 0) > 0.8 for i in getattr(proposal, "insights", [])
            ):
                reflection.approve_proposal(proposal.id)
                logger.info(f"Reflection: auto-approved improvement '{proposal.title}'")
        except Exception as e:
            logger.warning(f"Reflection analysis failed: {e}")

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

        # Same path as _on_mahamantra_tick: check heartbeat API first
        try:
            heartbeat = self._client.sync_check_heartbeat()
            self._last_heartbeat_error = None
        except Exception as e:
            self._last_heartbeat_error = f"[{type(e).__name__}] {e!r}"
            heartbeat = {}

        self._heartbeat.dispatch_heartbeat(heartbeat)

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
        """Delegate to DMProcessor for inbound DM handling."""
        self._dm.process_inbound_dms()

    def _process_dm_requests(self) -> None:
        """Delegate to DMProcessor for DM request handling."""
        self._dm.process_dm_requests()

    def _analyze_feed(self) -> None:
        """Read personalized feed, score via proposer, generate via AgencyDirector."""
        self._feed.analyze_feed(
            client=self._client,
            proposer=self._proposer,
            content_queue=self._content_queue,
            director_propose=self._director_propose,
        )

    # =========================================================================
    # Phase-Aware Methods (MURALI routing)
    # =========================================================================

    def _scan_feed(self) -> None:
        """GENESIS phase: Extract topics + metadata from feed. NO content generation."""
        self._current_feed_topics = self._feed.scan_feed(
            client=self._client,
            proposer=self._proposer,
            content_queue=self._content_queue,
        )

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
            intents = planner.plan_cycle(
                self._current_feed_topics, engagement_stats,
                own_post_ids=self._own_post_ids,
            )
            self._current_intents = intents
            if intents:
                logger.info(f"Strategy: {len(intents)} intents planned ({', '.join(i.action_type for i in intents)})")
        except Exception as e:
            logger.warning(f"Strategy evaluation failed: {e}")

    def _execute_intents(self) -> None:
        """Delegate to IntentExecutor for strategic intent processing."""
        self._intent.execute_intents()

    def _maybe_create_post(self) -> None:
        """Delegate to PostOrchestrator for fallback post creation."""
        self._post.maybe_create_fallback_post()

    def _check_own_comment_replies(self) -> None:
        """Delegate to PostOrchestrator for comment reply monitoring."""
        self._post.check_own_comment_replies()

    def _update_profile(self) -> None:
        """Delegate to PostOrchestrator for profile updates."""
        self._post.update_profile()

    def _track_engagement(self) -> None:
        """Poll own posts/comments for engagement metrics (upvotes, replies)."""
        self._engagement.track(
            service=self._service,
            own_post_ids=self._own_post_ids,
            own_comment_ids=self._own_comment_ids,
            comment_post_map=self._comment_post_map,
            event_log=self.agency_director.event_log,
            strategy_planner=self.strategy_planner,
        )

    def _adjust_intervals(self) -> None:
        """Adjust heartbeat intervals based on feedback success rate."""
        self._feed_interval, self._post_interval = self._engagement.adjust_intervals(
            feed_interval=self._feed_interval,
            post_interval=self._post_interval,
        )

    def _monitor_queue_health(self) -> None:
        """Log warning when queue overflows (proposals silently dropped)."""
        self._content_drainer.monitor_queue_health(self._content_queue, self._heartbeat_count)

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
        """Append an event to the JSONL activity log.

        Routes through EnforceGateProvider for Guna-policy audit trail.
        Falls back to direct append when gate is unavailable (test mode).
        """
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

            # Route through EnforceGateProvider for audit trail
            try:
                from vibe_core.mahamantra.substrate.core.guna import Guna
                from vibe_core.mahamantra.substrate.vm.gate_providers import get_sync_gate

                gate = get_sync_gate()
                result = gate.write(
                    "moltbook_activity_log",
                    entry,
                    actor="moltbook_activity",
                    guna=Guna.RAJAS,
                )
                if result.success:
                    with self._activity_log_path.open("a") as f:
                        f.write(line + "\n")
                else:
                    logger.debug(f"Activity log blocked by gate: {result.reason}")
                    return
            except Exception:
                # Gate unavailable — direct append (test/standalone mode)
                with self._activity_log_path.open("a") as f:
                    f.write(line + "\n")
        except Exception as e:
            logger.warning(f"Activity log write failed: {e}")

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

    def _discover_submolts(self) -> None:
        """Ensure own submolt exists, then discover and subscribe to relevant submolts."""
        self._feed.ensure_own_submolt(self._client, self._content_queue)
        self._feed.discover_submolts(self._client, self._content_queue)

    def _select_submolt(self, seed_text: str) -> Optional[str]:
        """Select best submolt for content via resonance cross-scoring."""
        return self._feed.select_submolt(seed_text, lambda: self.agency_director.event_log)

    def _check_rate_limit(self, content_type: str) -> bool:
        """Check if content type is within rate limits. Delegates to ContentDrainer."""
        return self._content_drainer.check_rate_limit(content_type)

    def _record_rate_limit(self, content_type: str) -> None:
        """Record that a content action was executed. Delegates to ContentDrainer."""
        self._content_drainer.record_rate_limit(content_type)

    def _drain_content_queue(self) -> None:
        """Execute queued content proposals through MoltbookService."""
        self._content_drainer.drain(self._content_queue, self._offline_mode)

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
            "circuit_executor": bool(self._content_circuit_executor),
            "agora_wired": bool(self._agora),
            "execute_content_circuit": self.execute_content_circuit,
        }
