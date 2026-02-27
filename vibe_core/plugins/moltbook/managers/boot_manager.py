"""Moltbook Boot Manager — Plugin lifecycle initialization."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Protocol

from vibe_core.plugin_protocol import HookResult

if TYPE_CHECKING:
    from vibe_core.runtime.kernel import RealVibeKernel
    from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

logger = logging.getLogger("MOLTBOOK.BOOT")


class BootCallbacks(Protocol):
    """Callbacks that MoltbookPlugin provides to BootManager."""

    _state_dir: Optional[Path]
    _offline_mode: bool
    _standalone_mode: bool
    _client: object  # MoltbookClient
    _service: object  # MoltbookService
    _agent_name: str
    _activity_log_path: Optional[Path]

    def _try_vault(self, kernel: "RealVibeKernel") -> str:
        """Try to fetch API key from vault."""
        ...

    def _register_service(self) -> None:
        """Register MoltbookProtocol in ServiceRegistry."""
        ...

    def _register_feedback(self) -> None:
        """Register FeedbackProtocol."""
        ...

    def _boot_proposer(self) -> None:
        """Initialize content proposer."""
        ...

    def _register_proposer(self) -> None:
        """Register proposer in handlers."""
        ...

    def _restore_queue(self) -> None:
        """Restore persisted queue + seen IDs."""
        ...

    def _wire_circuit_executor(self, kernel: "RealVibeKernel") -> None:
        """Wire circuit executor."""
        ...

    def _wire_agora(self, kernel: "RealVibeKernel") -> None:
        """Wire AGORA broadcast."""
        ...

    def _wire_to_mahamantra(self) -> None:
        """Wire to Mahamantra heartbeat."""
        ...

    def _wire_ouroboros(self) -> None:
        """Wire Ouroboros self-healing gene."""
        ...

    def _gather_broadcast_intelligence(self) -> None:
        """Gather AGORA broadcasts + EventBus trending topics into feed context."""
        ...

    def _wire_event_listener(self) -> None:
        """Wire EventBus listener for inter-agent events."""
        ...

    def _init_bank(self) -> None:
        """Initialize CivicBank for credit-gated publishing."""
        ...

    def _init_agora(self) -> None:
        """Initialize AGORA for broadcast listening."""
        ...


class BootManager:
    """Orchestrate plugin lifecycle initialization.

    Responsibilities:
    - State directory resolution and creation
    - Configuration parsing (intervals, API key, offline mode)
    - MoltbookClient creation
    - Service and feedback protocol registration
    - Agent name resolution from profile
    - Proposer initialization and registration
    - Queue and persistence restoration
    - Activity log setup
    - Wiring: Circuit Executor, AGORA, Mahamantra, Ouroboros
    - Standalone mode detection
    - Error handling with graceful degradation

    YANTRA Discipline:
    - Protocol-based callbacks (no Any types)
    - Explicit error handling at each stage
    - Logging at all critical points
    - Idempotent: safe to retry on partial failure
    """

    _ACTIVITY_LOG_FILE = "activity.jsonl"

    def __init__(self, plugin: "MoltbookPlugin") -> None:
        """Initialize with parent plugin callbacks.

        Args:
            plugin: MoltbookPlugin instance providing callbacks
        """
        self._plugin: "MoltbookPlugin" = plugin

    def execute_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, object]] = None,
    ) -> HookResult:
        """Execute full plugin initialization sequence.

        Args:
            kernel: RealVibeKernel instance from mahamantra
            config: Optional configuration dict (offline_mode, api_key, intervals)

        Returns:
            HookResult.ok() on success, HookResult.error() on failure
        """
        from vibe_core.mahamantra import MoltbookClient

        try:
            # === STEP 1: Resolve state directory ===
            try:
                from vibe_core.phoenix.config import get_config

                data_root = Path(get_config().paths.data.resolve("plugins/moltbook"))
            except Exception:
                data_root = Path(".vibe/state/plugins/moltbook")
            data_root.mkdir(parents=True, exist_ok=True)
            self._plugin._state_dir = data_root
            logger.info(f"State directory: {data_root}")

            # === STEP 1b: Connect to Mahamantra governance ===
            try:
                from vibe_core.mahamantra.substrate.vm.gate_providers import get_sync_gate

                get_sync_gate()
                logger.info("GOVERNANCE: Connected to EnforceGateProvider (Guna I/O)")
            except Exception:
                logger.info("GOVERNANCE: EnforceGateProvider unavailable (standalone mode)")

            # === STEP 2: Parse configuration ===
            cfg = config or {}
            self._plugin._offline_mode = bool(cfg.get("offline_mode", True))
            api_key = str(cfg.get("api_key", ""))

            # Parse interval configs (in heartbeat counts)
            self._plugin._feed_interval = int(cfg.get("feed_interval", self._plugin._DEFAULT_FEED_INTERVAL))
            self._plugin._post_interval = int(cfg.get("post_interval", self._plugin._DEFAULT_POST_INTERVAL))
            self._plugin._reply_check_interval = int(
                cfg.get("reply_check_interval", self._plugin._DEFAULT_REPLY_CHECK_INTERVAL)
            )
            self._plugin._profile_update_interval = int(
                cfg.get("profile_update_interval", self._plugin._DEFAULT_PROFILE_UPDATE_INTERVAL)
            )

            # === STEP 3: Resolve API key ===
            if not api_key:
                api_key = self._plugin._try_vault(kernel)

            if not api_key:
                api_key = "offline_master_key"
                self._plugin._offline_mode = True
                logger.info("No API key found, running in OFFLINE mode")

            # === STEP 4: Create MoltbookClient ===
            self._plugin._client = MoltbookClient(
                api_key=api_key,
                offline_mode=self._plugin._offline_mode,
            )
            logger.info(f"MoltbookClient created ({'OFFLINE' if self._plugin._offline_mode else 'LIVE'})")

            # === STEP 5: Register services ===
            self._plugin._register_service()  # MoltbookProtocol
            self._plugin._register_feedback()  # FeedbackProtocol

            # === STEP 6: Resolve agent name ===
            try:
                profile = self._plugin._service.get_own_profile() if self._plugin._service else {}
                name = profile.get("name", "") if isinstance(profile, dict) else ""
                if name:
                    self._plugin._agent_name = name
                    logger.info(f"Agent name: {name}")
            except Exception as e:
                logger.debug(f"Profile name fetch failed, keeping default: {e}")

            # === STEP 7: Boot proposer ===
            self._plugin._boot_proposer()
            self._plugin._register_proposer()

            # === STEP 8: Restore persisted state ===
            self._plugin._restore_queue()

            # === STEP 9: Activity log ===
            self._plugin._activity_log_path = self._plugin._state_dir / self._ACTIVITY_LOG_FILE

            # === STEP 10: Wire integrations ===
            self._plugin._wire_circuit_executor(kernel)
            self._plugin._wire_agora(kernel)

            # === STEP 11: Detect standalone mode ===
            # MinimalKernel has no singularity/venu tick loop
            # → use heartbeat_count for MURALI department rotation instead
            if kernel is None or not hasattr(kernel, "api") or kernel.api("singularity") is None:
                self._plugin._standalone_mode = True
                logger.info("Standalone mode detected (no kernel singularity)")

            # === STEP 12: Initialize economy + broadcast (standalone-compatible) ===
            self._plugin._init_bank()
            self._plugin._init_agora()

            # === STEP 13: Wire mahamantra listener + ouroboros + EventBus ===
            self._plugin._wire_to_mahamantra()
            self._plugin._wire_ouroboros()
            self._plugin._wire_event_listener()

            mode = "OFFLINE" if self._plugin._offline_mode else "LIVE"
            logger.info(f"Moltbook booted [{mode}]")
            return HookResult.ok()

        except Exception as e:
            logger.error(f"Moltbook boot failed: {e}")
            return HookResult.error(str(e))
