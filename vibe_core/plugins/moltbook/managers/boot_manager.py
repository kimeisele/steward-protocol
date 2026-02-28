"""Moltbook Boot Manager — Plugin lifecycle initialization."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Protocol

from vibe_core.plugin_protocol import HookResult

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.plugins.moltbook.state import (
    DEFAULT_FEED_INTERVAL,
    DEFAULT_POST_INTERVAL,
    DEFAULT_PROFILE_UPDATE_INTERVAL,
    DEFAULT_REPLY_CHECK_INTERVAL,
    MoltbookState,
)

logger = logging.getLogger("MOLTBOOK.BOOT")


class BootActions(Protocol):
    """Protocol for action callbacks the boot manager needs.

    Implemented structurally by MoltbookPlugin — no import needed.
    """

    def _try_vault(self, kernel: Any) -> str: ...
    def _register_service(self) -> None: ...
    def _register_feedback(self) -> None: ...
    def _boot_proposer(self) -> None: ...
    def _register_proposer(self) -> None: ...
    def _restore_queue(self) -> None: ...
    def _wire_circuit_executor(self, kernel: Any) -> None: ...
    def _wire_agora(self, kernel: Any) -> None: ...
    def _init_bank(self) -> None: ...
    def _init_agora(self) -> None: ...
    def _wire_to_mahamantra(self) -> None: ...
    def _wire_ouroboros(self) -> None: ...
    def _wire_event_listener(self) -> None: ...


class BootManager:
    """Orchestrate plugin lifecycle initialization.

    Receives MoltbookState for data access. Actions protocol for callbacks.

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
    """

    _ACTIVITY_LOG_FILE = "activity.jsonl"

    def __init__(self, state: MoltbookState, actions: BootActions) -> None:
        self._state = state
        self._actions = actions

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
            self._state.state_dir = data_root
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
            self._state.offline_mode = bool(cfg.get("offline_mode", True))
            api_key = str(cfg.get("api_key", ""))

            # Parse interval configs (in heartbeat counts)
            self._state.feed_interval = int(cfg.get("feed_interval", DEFAULT_FEED_INTERVAL))
            self._state.post_interval = int(cfg.get("post_interval", DEFAULT_POST_INTERVAL))
            self._state.reply_check_interval = int(cfg.get("reply_check_interval", DEFAULT_REPLY_CHECK_INTERVAL))
            self._state.profile_update_interval = int(
                cfg.get("profile_update_interval", DEFAULT_PROFILE_UPDATE_INTERVAL)
            )

            # === STEP 3: Resolve API key ===
            if not api_key:
                api_key = self._actions._try_vault(kernel)

            if not api_key:
                api_key = "offline_master_key"
                self._state.offline_mode = True
                logger.info("No API key found, running in OFFLINE mode")

            # === STEP 4: Create MoltbookClient ===
            self._state.client = MoltbookClient(
                api_key=api_key,
                offline_mode=self._state.offline_mode,
            )
            logger.info(f"MoltbookClient created ({'OFFLINE' if self._state.offline_mode else 'LIVE'})")

            # === STEP 5: Register services ===
            self._actions._register_service()  # MoltbookProtocol
            self._actions._register_feedback()  # FeedbackProtocol

            # === STEP 6: Resolve agent name ===
            try:
                profile = self._state.service.get_own_profile() if self._state.service else {}
                name = profile.get("name", "") if isinstance(profile, dict) else ""
                if name:
                    self._state.agent_name = name
                    logger.info(f"Agent name: {name}")
            except Exception as e:
                logger.debug(f"Profile name fetch failed, keeping default: {e}")

            # === STEP 7: Boot proposer ===
            self._actions._boot_proposer()
            self._actions._register_proposer()

            # === STEP 8: Restore persisted state ===
            self._actions._restore_queue()

            # === STEP 9: Activity log ===
            self._state.activity_log_path = self._state.state_dir / self._ACTIVITY_LOG_FILE

            # === STEP 10: Wire integrations ===
            self._actions._wire_circuit_executor(kernel)
            self._actions._wire_agora(kernel)

            # === STEP 11: Detect standalone mode ===
            # MinimalKernel has no singularity/venu tick loop
            # → use heartbeat_count for MURALI department rotation instead
            if kernel is None or not hasattr(kernel, "api") or kernel.api("singularity") is None:
                self._state.standalone_mode = True
                logger.info("Standalone mode detected (no kernel singularity)")

            # === STEP 12: Initialize economy + broadcast (standalone-compatible) ===
            self._actions._init_bank()
            self._actions._init_agora()

            # === STEP 13: Wire mahamantra listener + ouroboros + EventBus ===
            self._actions._wire_to_mahamantra()
            self._actions._wire_ouroboros()
            self._actions._wire_event_listener()

            mode = "OFFLINE" if self._state.offline_mode else "LIVE"
            logger.info(f"Moltbook booted [{mode}]")
            return HookResult.ok()

        except Exception as e:
            logger.error(f"Moltbook boot failed: {e}")
            return HookResult.error(str(e))
