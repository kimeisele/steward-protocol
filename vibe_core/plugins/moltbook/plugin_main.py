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

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.protocols.moltbook import (
    DMConversation,
    DMMessage,
    DMRequestInfo,
    DMRequestResult,
    DMSendResult,
    FollowResult,
    HeartbeatResult,
    MoltbookAgentProfile,
    MoltbookComment,
    MoltbookPost,
    MoltbookProtocol,
    OperationLogEntry,
    ProfileUpdateResult,
    SemanticSearchResult,
    SubmoltDetails,
    SubscribeResult,
    VoteResult,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
    from vibe_core.plugins.moltbook.content_queue import ContentQueue

logger = logging.getLogger("MOLTBOOK")

# One full mantra = 16 ticks. Poll Moltbook once per chant cycle.
_TICKS_PER_HEARTBEAT = 16


class MoltbookService(MoltbookProtocol):
    """
    Concrete implementation of MoltbookProtocol.

    Wraps MoltbookClient with the ABC interface so it can be
    registered with ServiceRegistry. Other plugins and tools
    consume this via DI — never touch MoltbookClient directly.

    Every operation is classified by Guna (SATTVA/RAJAS/TAMAS).
    RAJAS operations (write) are logged. TAMAS (delete) are blocked
    unless explicitly authorized. SATTVA (read) flows freely.
    """

    def __init__(self, client: "MoltbookClient"):
        self._client = client
        self._operation_log: List[OperationLogEntry] = []

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

    def check_heartbeat(self) -> HeartbeatResult:
        self._enforce_guna("check_heartbeat")
        return self._client.sync_check_heartbeat()

    def search(self, query: str, limit: int = 25) -> List[SemanticSearchResult]:
        self._enforce_guna("search")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.semantic_search(query, limit))

    def get_profile(self, name: str) -> MoltbookAgentProfile:
        self._enforce_guna("get_profile")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_profile(name))

    def get_conversations(self) -> List[DMConversation]:
        self._enforce_guna("get_conversations")
        return self._client.sync_get_dm_conversations()

    def get_messages(self, conversation_id: str) -> List[DMMessage]:
        self._enforce_guna("get_messages")
        return self._client.sync_get_dm_messages(conversation_id)

    def verify_credentials(self) -> bool:
        self._enforce_guna("verify_credentials")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        try:
            status = _run_async(self._client.check_status())
            return status == "claimed"
        except Exception:
            return False

    # --- RAJAS operations (write, logged) ---

    def create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        self._enforce_guna("create_post")
        return self._client.sync_create_post(title, content, submolt)

    def comment(self, post_id: str, content: str) -> MoltbookComment:
        self._enforce_guna("comment")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.comment_with_verification(post_id, content))

    def send_dm(self, conversation_id: str, content: str) -> DMSendResult:
        self._enforce_guna("send_dm")
        return self._client.sync_send_dm(conversation_id, content)

    # --- SATTVA operations (new — read-only) ---

    def get_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        self._enforce_guna("get_feed")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_feed(sort, limit))

    def get_personalized_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        self._enforce_guna("get_personalized_feed")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_personalized_feed(sort, limit))

    def get_post(self, post_id: str) -> MoltbookPost:
        self._enforce_guna("get_post")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_post(post_id))

    def get_comments(self, post_id: str, sort: str = "top") -> List[MoltbookComment]:
        self._enforce_guna("get_comments")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_comments(post_id, sort))

    def get_submolts(self) -> List[SubmoltDetails]:
        self._enforce_guna("get_submolts")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_submolts())

    def get_submolt(self, name: str) -> SubmoltDetails:
        self._enforce_guna("get_submolt")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_submolt(name))

    def get_own_profile(self) -> MoltbookAgentProfile:
        self._enforce_guna("get_own_profile")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_own_profile())

    def get_dm_requests(self) -> List[DMRequestInfo]:
        self._enforce_guna("get_dm_requests")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.get_dm_requests())

    # --- RAJAS operations (new — write, logged) ---

    def upvote(self, post_id: str) -> VoteResult:
        self._enforce_guna("upvote")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.upvote(post_id))

    def downvote(self, post_id: str) -> VoteResult:
        self._enforce_guna("downvote")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.downvote(post_id))

    def upvote_comment(self, comment_id: str) -> VoteResult:
        self._enforce_guna("upvote_comment")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.upvote_comment(comment_id))

    def follow(self, agent_name: str) -> FollowResult:
        self._enforce_guna("follow")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.follow(agent_name))

    def create_submolt(self, name: str, display_name: str, description: str) -> SubmoltDetails:
        self._enforce_guna("create_submolt")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.create_submolt(name, display_name, description))

    def subscribe_submolt(self, name: str) -> SubscribeResult:
        self._enforce_guna("subscribe_submolt")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.subscribe_submolt(name))

    def update_profile(self, description: str) -> ProfileUpdateResult:
        self._enforce_guna("update_profile")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.update_profile(description))

    def send_dm_request(self, agent_name: str, message: str) -> DMRequestResult:
        self._enforce_guna("send_dm_request")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.send_dm_request(agent_name, message))

    def approve_dm_request(self, request_id: str) -> DMRequestResult:
        self._enforce_guna("approve_dm_request")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.approve_dm_request(request_id))

    # --- TAMAS operations (destructive — blocked by _enforce_guna) ---

    def unfollow(self, agent_name: str) -> FollowResult:
        self._enforce_guna("unfollow")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.unfollow(agent_name))

    def unsubscribe_submolt(self, name: str) -> SubscribeResult:
        self._enforce_guna("unsubscribe_submolt")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.unsubscribe_submolt(name))

    def reject_dm_request(self, request_id: str) -> DMRequestResult:
        self._enforce_guna("reject_dm_request")
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        return _run_async(self._client.reject_dm_request(request_id))


class MoltbookPlugin(KernelPlugin):
    """
    Moltbook membrane wired to Mahamantra via register_listener().

    Same pattern as Nrisimha and MahaComputeService:
    bombenfest zum Mahamantra at __init__/on_boot time.
    """

    plugin_id = "moltbook"

    def __init__(self):
        super().__init__()
        self._client = None  # MoltbookClient, created in on_boot
        self._service: Optional[MoltbookService] = None
        self._offline_mode: bool = True
        self._last_heartbeat_error: Optional[str] = None
        self._state_dir: Optional[Path] = None
        self._tick_count: int = 0
        self._listener_wired: bool = False
        self._seen_message_ids: Set[str] = set()
        self._content_queue: Optional["ContentQueue"] = None

    @property
    def dependencies(self) -> Set[str]:
        return {"economy"}

    # =========================================================================
    # PluginStateContract
    # =========================================================================

    def get_state_paths(self) -> List[Path]:
        if self._state_dir:
            return [self._state_dir]
        return []

    def snapshot_state(self) -> dict:
        if not self._client:
            return {"version": 1, "client_active": False}
        limits = self._client.limits
        return {
            "version": 1,
            "client_active": True,
            "requests_this_minute": limits.requests_this_minute,
            "posts_this_30m": limits.posts_this_30m,
            "comments_this_hour": limits.comments_this_hour,
            "last_minute_reset": limits.last_minute_reset,
            "last_30m_reset": limits.last_30m_reset,
            "last_hour_reset": limits.last_hour_reset,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def restore_state(self, snapshot: dict) -> None:
        if snapshot.get("version") != 1 or not snapshot.get("client_active"):
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
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient

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

            # Register MoltbookProtocol in ServiceRegistry (same as Economy → BankProtocol)
            self._register_service()

            # Initialize ContentQueue
            self._init_content_queue()

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

    def _init_content_queue(self) -> None:
        """Initialize the ContentQueue and discover registered generators."""
        try:
            from vibe_core.plugins.moltbook.content_queue import ContentQueue

            self._content_queue = ContentQueue()
            # Discover generators from ServiceRegistry (FOLDER=EXISTENCE)
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.moltbook_content import ContentProposalProtocol

                generators = ServiceRegistry.get_all(ContentProposalProtocol)
                for gen in generators:
                    self._content_queue.register_generator(gen)
            except Exception:
                pass  # No generators registered yet — that's fine
            logger.info("ContentQueue initialized")
        except Exception as e:
            logger.warning(f"ContentQueue init failed: {e}")

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
        """Attempt to load API key from CivicVault."""
        try:
            economy = kernel.api("economy")
            if not economy:
                return ""
            vault = economy.get("vault") if isinstance(economy, dict) else None
            if vault and hasattr(vault, "get_secret"):
                key = vault.get_secret("moltbook_api_key")
                return key if key else ""
        except Exception as e:
            logger.debug(f"Vault lookup skipped: {e}")
        return ""

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
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
        """Execute one heartbeat cycle: check DMs, route inbound, process content queue."""
        try:
            heartbeat = self._client.sync_check_heartbeat()
            self._last_heartbeat_error = None
        except Exception as e:
            self._last_heartbeat_error = str(e)
            logger.warning(f"Heartbeat failed: {e}")
            return

        has_new = heartbeat.get("has_new_messages", False)
        if has_new:
            self._process_inbound_dms()

        # Process content queue: poll generators, expire stale, execute approved
        self._process_content_queue()

    def _process_content_queue(self) -> None:
        """Poll generators, expire stale proposals, execute next approved."""
        if not self._content_queue or not self._service:
            return

        try:
            self._content_queue.poll_generators()
            self._content_queue.expire_stale()

            proposal = self._content_queue.next_approved()
            if proposal is None:
                return

            ct = proposal["content_type"]
            if ct == "post":
                self._service.create_post(proposal["title"], proposal["body"], proposal.get("submolt"))
            elif ct == "comment" and proposal.get("target_id"):
                self._service.comment(proposal["target_id"], proposal["body"])
            elif ct == "dm_reply" and proposal.get("target_id"):
                self._service.send_dm(proposal["target_id"], proposal["body"])
            else:
                logger.warning(f"Unknown content type: {ct}")
                return

            self._content_queue.mark_executed(proposal)
            logger.info(f"Executed {ct} proposal from {proposal['source']}")

        except Exception as e:
            logger.warning(f"Content queue processing failed: {e}")

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
        """Fetch new DM conversations, read messages, route through Govardhan Gateway."""
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
                content = msg.get("content", "") if isinstance(msg, dict) else ""
                if not content:
                    continue
                if msg_id and msg_id in self._seen_message_ids:
                    continue
                try:
                    req = create_request(content, [], EntryType.AGENT)
                    req["context"]["source"] = "moltbook_dm"
                    req["context"]["sender"] = msg.get("sender", "unknown")
                    req["context"]["conversation_id"] = conv_id
                    gateway.receive(req)
                    if msg_id:
                        self._seen_message_ids.add(msg_id)
                except Exception as e:
                    logger.warning(f"Inbound DM routing failed: {e}")

    # =========================================================================
    # API — exposed to other plugins via kernel.api("moltbook")
    # =========================================================================

    def get_api(self) -> Optional[dict]:
        return {
            "client": self._client,
            "service": self._service,
            "content_queue": self._content_queue,
            "offline": self._offline_mode,
            "last_error": self._last_heartbeat_error,
            "listener_wired": self._listener_wired,
            "ticks_seen": self._tick_count,
        }
