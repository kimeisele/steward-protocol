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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.protocols.moltbook import (
    DMMessage,
    MoltbookAgentProfile,
    MoltbookComment,
    MoltbookPost,
    MoltbookProtocol,
    SemanticSearchResult,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.mahamantra import MoltbookClient

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
        self._operation_log: List[Dict[str, Any]] = []

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

    def search(self, query: str, limit: int = 25) -> List[SemanticSearchResult]:
        self._enforce_guna("search")
        from vibe_core.mahamantra import run_async

        return run_async(self._client.semantic_search(query, limit))

    def get_profile(self, name: str) -> MoltbookAgentProfile:
        self._enforce_guna("get_profile")
        from vibe_core.mahamantra import run_async

        return run_async(self._client.get_profile(name))

    def get_conversations(self) -> List[Dict[str, Any]]:
        self._enforce_guna("get_conversations")
        return self._client.sync_get_dm_conversations()

    def get_messages(self, conversation_id: str) -> List[DMMessage]:
        self._enforce_guna("get_messages")
        return self._client.sync_get_dm_messages(conversation_id)

    def verify_credentials(self) -> bool:
        self._enforce_guna("verify_credentials")
        from vibe_core.mahamantra import run_async

        try:
            status = run_async(self._client.check_status())
            return status == "claimed"
        except Exception:
            return False

    # --- RAJAS operations (write, logged) ---

    def create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        self._enforce_guna("create_post")
        return self._client.sync_create_post(title, content, submolt)

    def comment(self, post_id: str, content: str) -> MoltbookComment:
        self._enforce_guna("comment")
        from vibe_core.mahamantra import run_async

        return run_async(self._client.comment_with_verification(post_id, content))

    def send_dm(self, conversation_id: str, content: str) -> Dict[str, Any]:
        self._enforce_guna("send_dm")
        return self._client.sync_send_dm(conversation_id, content)


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
        self._offline_mode: bool = True
        self._last_heartbeat_error: Optional[str] = None
        self._state_dir: Optional[Path] = None
        self._tick_count: int = 0
        self._listener_wired: bool = False

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

    def snapshot_state(self) -> Dict[str, Any]:
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

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
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

            # Register MoltbookProtocol in ServiceRegistry (same as Economy → BankProtocol)
            self._register_service()

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

            service = MoltbookService(self._client)
            ServiceRegistry.register_factory(MoltbookProtocol, lambda: service)
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
        """Execute one heartbeat cycle: check DMs, route inbound."""
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
                content = msg.get("content", "") if isinstance(msg, dict) else ""
                if not content:
                    continue
                try:
                    req = create_request(content, [], EntryType.AGENT)
                    req["context"]["source"] = "moltbook_dm"
                    req["context"]["sender"] = msg.get("sender", "unknown")
                    req["context"]["conversation_id"] = conv_id
                    gateway.receive(req)
                except Exception as e:
                    logger.warning(f"Inbound DM routing failed: {e}")

    # =========================================================================
    # API — exposed to other plugins via kernel.api("moltbook")
    # =========================================================================

    def get_api(self) -> Optional[Dict[str, Any]]:
        return {
            "client": self._client,
            "offline": self._offline_mode,
            "last_error": self._last_heartbeat_error,
            "listener_wired": self._listener_wired,
            "ticks_seen": self._tick_count,
        }
