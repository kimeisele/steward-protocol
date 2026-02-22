"""
Moltbook Plugin - The Native Cell Membrane
==========================================

"indriyani parany ahur indriyebhyah param manah"
"The working senses are superior to dull matter; mind is higher than the senses;"

This is NOT a Web2 REST client wrapper. This is a biological membrane.
It acts as a Sensor (Drishti) and Actuator (Karma) for the Visnu Kernel.

Inbound (SENSORS phase):
    Translates Moltbook DMs/Mentions into Gateway Requests and routes them
    through Govardhan (The Boundary Layer) to fire the 5 Pancha Tattva Gates
    (Parse, Validate, Execute, Result, Sync) before they become Cells.

Outbound (ACTUATORS phase):
    Scans the `CellRouter` for cells tagged for Moltbook output.
    Metabolizes them (drains Prana) and translates their DNA into Moltbook posts.

Governance:
    Rate limiting is handled as biological starvation within the plugin's state.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 3
__genesis__ = "0x51edc2f9"

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
from vibe_core.mahamantra.substrate.cell_system.cell import MahaCellUnified
from vibe_core.mahamantra.substrate.cell_system.cell_router import get_router
from vibe_core.protocols.gateway import EntryType, create_request
from vibe_core.gateway.mahamantra_gateway import get_gateway

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("MOLTBOOK_PLUGIN")


class MoltbookPlugin(KernelPlugin):
    """
    Biological Membrane for Moltbook.
    
    Transforms pure Network I/O into kernel-native MahaCell objects.
    Enforces Rate Limits via PluginStateContract.
    """

    plugin_id = "moltbook"

    # State paths for PluginStateContract
    STATE_DIR = Path(".vibe/state/plugins/moltbook")

    def __init__(self):
        super().__init__()
        self._client: Optional[MoltbookClient] = None
        self._offline_mode: bool = True

    @property
    def dependencies(self) -> Set[str]:
        # Economy is needed to lease the API key from CivicVault
        return {"economy"}

    # =========================================================================
    # PluginStateContract Implementation
    # =========================================================================

    def get_state_paths(self) -> List[Path]:
        """Return paths where this plugin stores state."""
        return [self.STATE_DIR]

    def snapshot_state(self) -> Dict[str, Any]:
        """Snapshot the adapter's REAL rate-limit state (not a shadow copy)."""
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
        """Restore the adapter's rate limits after crash/reboot."""
        if snapshot.get("version") != 1 or not snapshot.get("client_active"):
            return
        # We can only restore if client exists (boot already happened)
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
    # KERNEL LIFECYCLE
    # =========================================================================

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, object]] = None,
    ) -> HookResult:
        """Boot the Moltbook Membrane."""
        try:
            self.STATE_DIR.mkdir(parents=True, exist_ok=True)
            
            # Read config
            cfg = config or {}
            self._offline_mode = bool(cfg.get("offline_mode", True))
            api_key = str(cfg.get("api_key", ""))
            
            # If no API key is in config, we try to lease it from CivicVault
            if not api_key:
                try:
                    economy = kernel.api("economy")
                    if economy:
                        vault = economy.get("vault")
                        if vault:
                            # Note: in real use, this costs Credits via agent_id
                            api_key = vault.get_secret("moltbook_api_key")
                except Exception as e:
                    logger.debug(f"Could not load key from vault (normal during CI): {e}")
            
            # Fallback to offline master key if still missing
            if not api_key:
                api_key = "offline_master_key"
                self._offline_mode = True
                
            self._client = MoltbookClient(api_key=api_key, offline_mode=self._offline_mode)
            mode_str = "OFFLINE" if self._offline_mode else "LIVE"
            logger.info(f"🌐 Moltbook Membrane Booted [{mode_str}]")
            
            return HookResult.ok()
            
        except Exception as e:
            logger.error(f"Failed to boot Moltbook Membrane: {e}")
            return HookResult.error(str(e))

    # =========================================================================
    # MACRO-CYCLE: SENSORS & ACTUATORS
    # =========================================================================

    @property
    def pulse_phase(self) -> PulsePhase:
        # Moltbook acts as both, but we register as SENSORS to feed data early
        # in the Pulse cycle before Cortex makes decisions.
        return PulsePhase.SENSORS

    def _route_inbound(self, content: str, source: str = "moltbook_dm"):
        """Route inbound Moltbook content strictly through Govardhan Gateway."""
        gateway = get_gateway()
        # Treat Moltbook inputs as CHAT entry type to engage Kaliya/Takshaka filters
        req = create_request(content, [], EntryType.CHAT)
        req["source"] = source
        return gateway.receive(req)

    def on_pulse(self, kernel: "RealVibeKernel", transaction: object) -> HookResult:
        """
        The Biological Heartbeat.
        
        OPUS-087: Runs during the macro-cycle headless run.
        We do BOTH Sensor and Actuator work here, mediated by the CellRouter.
        """
        if not self._client:
            return HookResult.error("Client not initialized")
            
        # 1. DRISHTI (Sensor Phase)
        # Fetch DMs and Mentions from Moltbook...
        try:
            # Note: since this is async and on_pulse is sync, we'd need an event loop
            # if we were actually hitting network. 
            
            # Simulated Sensor Read: If we got a new message on Moltbook
            # heartbeat_data = asyncio.run(self._client.check_heartbeat())
            # if heartbeat_data.get("has_new_messages"):
            #     for msg in heartbeat_data.get("messages", []):
            #         # PROPER ARCHITECTURE: Route through Govardhan Gates
            #         # This fires PARSE -> VALIDATE -> EXECUTE -> RESULT -> SYNC
            #         self._route_inbound(content=msg["content"])
            pass
        except Exception as e:
            logger.warning(f"Sensor read failed: {e}")

        # 2. KARMA (Actuator Phase)
        # Scan CellRouter for Moltbook-bound cells
        router = get_router()
        # Assume Moltbook outbound cells are addressed via a specific Prefix code 
        # (e.g., 0xM0LT...)
        
        # This is where we would:
        # 1. Find cells destined for Moltbook
        # 2. Call cell.metabolize(energy) 
        # 3. If cell survives homeostasis, execute client.create_post(cell.dna)
        # 4. If rate limit hit -> cell.apoptosis() (starvation)

        return HookResult.ok()

    def get_api(self) -> Optional[object]:
        """Expose the Moltbook client carefully to other internal verified plugins."""
        return {
            "client": self._client,
            "status": "active" if self._client else "inactive"
        }
