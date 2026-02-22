"""
Moltbook Plugin — Sensor/Actuator Membrane
===========================================

Bridges the Moltbook social network to the Visnu Kernel via the
standard Plugin lifecycle (on_boot / on_pulse / on_shutdown).

Inbound (SENSORS phase in on_pulse):
    Polls Moltbook for new DMs → routes them through Govardhan Gateway
    → the 5 Pancha Tattva Gates fire → result becomes a Cell.

Outbound (ACTUATORS, future):
    Content approved by NAGA Cortex → posted to Moltbook via the adapter.

All network I/O goes through MoltbookClient (adapters/moltbook.py).
Rate-limit state survives reboots via PluginStateContract.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("MOLTBOOK")


class MoltbookPlugin(KernelPlugin):
    """
    Moltbook membrane for the Visnu Kernel.

    Follows the same pattern as EconomyPlugin / SanghaNetworkPlugin:
    - Lazy client creation in on_boot
    - State snapshot/restore for crash recovery
    - Single codepath for heartbeat (no separate script)
    """

    plugin_id = "moltbook"

    def __init__(self):
        super().__init__()
        self._client = None  # MoltbookClient, created in on_boot
        self._offline_mode: bool = True
        self._last_heartbeat_error: Optional[str] = None
        self._state_dir: Optional[Path] = None

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
            "comments_today": limits.comments_today,
            "last_minute_reset": limits.last_minute_reset,
            "last_30m_reset": limits.last_30m_reset,
            "last_day_reset": limits.last_day_reset,
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
        limits.comments_today = snapshot.get("comments_today", 0)
        limits.last_minute_reset = snapshot.get("last_minute_reset", 0.0)
        limits.last_30m_reset = snapshot.get("last_30m_reset", 0.0)
        limits.last_day_reset = snapshot.get("last_day_reset", 0.0)

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
            # Resolve state dir via phoenix config or fallback
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
            mode = "OFFLINE" if self._offline_mode else "LIVE"
            logger.info(f"Moltbook booted [{mode}]")
            return HookResult.ok()

        except Exception as e:
            logger.error(f"Moltbook boot failed: {e}")
            return HookResult.error(str(e))

    def _try_vault(self, kernel: "RealVibeKernel") -> str:
        """Attempt to load API key from CivicVault. Returns empty string on failure."""
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
        self._client = None
        logger.info("Moltbook shutdown")
        return HookResult.ok()

    # =========================================================================
    # Pulse — The heartbeat
    # =========================================================================

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.SENSORS

    def on_pulse(self, kernel: "RealVibeKernel", transaction: object) -> HookResult:
        """
        Runs during the macro-cycle (GitHub Actions headless or kernel tick).

        SENSOR work: poll Moltbook for new DMs, route inbound through Govardhan.
        ACTUATOR work: deferred to Phase 4 (content proposals via NAGA Cortex).
        """
        if not self._client:
            return HookResult.error("Client not initialized")

        try:
            heartbeat = self._client.sync_check_heartbeat()
            self._last_heartbeat_error = None
        except Exception as e:
            self._last_heartbeat_error = str(e)
            logger.warning(f"Heartbeat failed: {e}")
            return HookResult.ok(data={"heartbeat": "failed", "error": str(e)})

        has_new = heartbeat.get("has_new_messages", False)
        pending = heartbeat.get("pending_requests", 0)

        if has_new:
            self._process_inbound_dms()

        return HookResult.ok(
            data={
                "heartbeat": "ok",
                "has_new_messages": has_new,
                "pending_requests": pending,
                "offline": self._offline_mode,
            }
        )

    def _process_inbound_dms(self) -> None:
        """Fetch new DM messages and route each through Govardhan Gateway."""
        from vibe_core.gateway.mahamantra_gateway import get_gateway
        from vibe_core.protocols.gateway import EntryType, create_request

        try:
            conversations = self._client.sync_get_dm_messages("__latest__")
        except Exception as e:
            logger.warning(f"DM fetch failed: {e}")
            return

        gateway = get_gateway()
        for msg in conversations:
            content = msg.get("content", "") if isinstance(msg, dict) else ""
            if not content:
                continue
            try:
                req = create_request(content, [], EntryType.AGENT)
                req["context"]["source"] = "moltbook_dm"
                req["context"]["sender"] = msg.get("sender", "unknown")
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
        }
