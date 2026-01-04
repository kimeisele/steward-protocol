"""
NAGA Federation Orchestrator.

"Niemand darf es merken" - they infiltrate invisibly.
"Wie Wasser in jede Ritze" - organic flooding into every crack.

Responsibilities:
- Create NAGAs in correct order (Sesha -> Takshaka -> Vasuki)
- Wire dependencies
- Register with ServiceRegistry
- Register handlers with CorrectionDispatcher
- Start organic flooding (EventBus, SignalBus)
- Provide health status

Usage:
    from vibe_core.naga import NagaOrchestrator

    naga = NagaOrchestrator.bootstrap(
        ledger=kernel.ledger,
        correction_orchestrator=correction_orchestrator,
    )
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.correction import DriftSource
from vibe_core.protocols.naga import (
    NagaFederationProtocol,
    SeshaProtocol,
    TakshakaProtocol,
    VasukiProtocol,
)
from vibe_core.protocols.state import StateServiceProtocol

if TYPE_CHECKING:
    from vibe_core.ledger import SQLiteLedger
    from vibe_core.naga.commit_watcher import NagaCommitWatcher
    from vibe_core.naga.cortex import NagaCortex
    from vibe_core.naga.flood import NagaFloodManager
    from vibe_core.naga.services.sesha import SeshaService
    from vibe_core.naga.services.takshaka import TakshakaService
    from vibe_core.naga.services.vasuki import VasukiService
    from vibe_core.phoenix.sections.naga.section_main import NagaConfig
    from vibe_core.protocols.correction import CorrectionOrchestratorProtocol
    from vibe_core.services.naga.state_proxy import NagaStateProxy

logger = logging.getLogger("NAGA")


class NagaOrchestrator:
    """
    NAGA Federation Orchestrator.

    Creates and wires NAGAs in the correct order.
    Integrates with CorrectionDispatcher for drift healing.
    """

    def __init__(self):
        """Initialize without config - use bootstrap() instead."""
        self._sesha: Optional["SeshaService"] = None
        self._vasuki: Optional["VasukiService"] = None
        self._takshaka: Optional["TakshakaService"] = None
        self._flood_manager: Optional["NagaFloodManager"] = None
        self._commit_watcher: Optional["NagaCommitWatcher"] = None
        self._state_proxy: Optional["NagaStateProxy"] = None
        self._cortex: Optional["NagaCortex"] = None
        self._initialized = False
        self._config: Optional["NagaConfig"] = None

    @classmethod
    def bootstrap(
        cls,
        ledger: "SQLiteLedger",
        correction_orchestrator: "CorrectionOrchestratorProtocol",
        config: Optional["NagaConfig"] = None,
    ) -> "NagaOrchestrator":
        """
        Bootstrap the NAGA Federation.

        This is the ONLY entry point. Call once during boot.

        Args:
            ledger: The SQLiteLedger for persistence
            correction_orchestrator: For registering drift handlers
            config: Optional NagaConfig (loads from Phoenix if not provided)

        Returns:
            Initialized NagaOrchestrator
        """
        orchestrator = cls()
        orchestrator._initialize(ledger, correction_orchestrator, config)
        return orchestrator

    def _get_config(self, config: Optional["NagaConfig"] = None) -> "NagaConfig":
        """Get config from parameter, Phoenix, or defaults."""
        if config is not None:
            return config

        # Try to load from Phoenix
        try:
            from vibe_core.phoenix import get_config

            phoenix = get_config()
            if phoenix.has_section("naga"):
                return phoenix.naga
        except Exception as e:
            logger.debug(f"Could not load config from Phoenix: {e}")

        # Fallback to defaults
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        return NagaConfig()

    def _initialize(
        self,
        ledger: "SQLiteLedger",
        correction_orchestrator: "CorrectionOrchestratorProtocol",
        config: Optional["NagaConfig"] = None,
    ) -> None:
        """
        Internal initialization - order matters!

        1. Sesha first (foundation)
        2. Takshaka second (guardian)
        3. Vasuki last (bridge - needs both)
        """
        from vibe_core.naga.services.sesha import SeshaService
        from vibe_core.naga.services.takshaka import TakshakaService
        from vibe_core.naga.services.vasuki import VasukiService

        self._config = self._get_config(config)

        # 1. SESHA - The Foundation
        if self._config.sesha.enabled:
            self._sesha = SeshaService(
                ledger=ledger,
                block_size=self._config.sesha.block_size,
            )
            ServiceRegistry.register(SeshaProtocol, self._sesha)
            correction_orchestrator.dispatcher.register_handler(
                DriftSource.STATE,
                self._sesha.as_handler(),
                handler_id="sesha",
                priority=50,
            )
            logger.info("🐍 SESHA registered - The Foundation holds")

        # 2. TAKSHAKA - The Guardian
        if self._config.takshaka.enabled:
            self._takshaka = TakshakaService(
                ledger=ledger,
                trust_mode=self._config.takshaka.trust_mode,
                toxicity_threshold=self._config.takshaka.toxicity_threshold,
                rate_limit_rpm=self._config.takshaka.rate_limit_rpm,
            )
            ServiceRegistry.register(TakshakaProtocol, self._takshaka)
            correction_orchestrator.dispatcher.register_handler(
                DriftSource.COGNITIVE,
                self._takshaka.as_handler(),
                handler_id="takshaka",
                priority=100,  # Highest priority for security
            )
            logger.info(f"🐍 TAKSHAKA registered - trust_mode={self._config.takshaka.trust_mode}")

        # 2.5 NAGA STATE PROXY - Der Politische Kommissar
        # Wraps StateService with Dharma validation (4 principles)
        try:
            from vibe_core.services.naga.state_proxy import NagaStateProxy
            from vibe_core.state.state_service import get_state_service

            # Get the real StateService
            real_state = get_state_service()

            # Wrap it with NAGA protection
            self._state_proxy = NagaStateProxy(
                state_service=real_state,
                takshaka=self._takshaka,
                strict_mode=True,  # Raise on violations
            )

            # Register the proxy as the StateServiceProtocol
            # Now all callers get NAGA-protected StateService!
            ServiceRegistry.register(StateServiceProtocol, self._state_proxy)
            logger.info("🐍 NAGA STATE PROXY registered - Der Kommissar wacht")
        except Exception as e:
            logger.warning(f"🐍 NAGA State Proxy failed to initialize: {e}")
            # Non-critical - continue without proxy

        # 3. VASUKI - The Bridge (needs Sesha and Takshaka)
        if self._config.vasuki.enabled:
            self._vasuki = VasukiService(
                sesha=self._sesha,
                takshaka=self._takshaka,
                sign_outbound=self._config.vasuki.sign_outbound,
            )
            ServiceRegistry.register(VasukiProtocol, self._vasuki)
            correction_orchestrator.dispatcher.register_handler(
                DriftSource.CONFIG,
                self._vasuki.as_handler(),
                handler_id="vasuki",
                priority=75,
            )
            logger.info("🐍 VASUKI registered - The Bridge connects")

        # 4. FLOOD MANAGER - Organic Flooding (Phase 2)
        # "Wie Wasser in jede Ritze" - with safety guards
        if self._config.flood.enabled:
            try:
                from vibe_core.naga.flood import NagaFloodManager

                self._flood_manager = NagaFloodManager(
                    sesha=self._sesha,
                    takshaka=self._takshaka,
                    enabled=self._config.flood.enabled,
                    config=self._config.flood,
                )
                self._flood_manager.start()
                logger.info("🌊 NAGA Flood Manager started - organic flooding active")
            except Exception as e:
                logger.warning(f"🌊 NAGA Flood Manager failed to start: {e}")
            # Non-critical - continue without flooding

        # 5. COMMIT WATCHER - Der Wächter-Pattern (Phase 4)
        # "NAGAs notice when things go wrong"
        if self._config.commit_watcher.enabled:
            try:
                from vibe_core.naga.commit_watcher import NagaCommitWatcher

                self._commit_watcher = NagaCommitWatcher(
                    sesha=self._sesha,
                    takshaka=self._takshaka,
                    enabled=self._config.commit_watcher.enabled,
                    config=self._config.commit_watcher,
                )
                logger.info("👁️ NAGA Commit Watcher initialized - Der Wächter observes")
            except Exception as e:
                logger.warning(f"👁️ NAGA Commit Watcher failed to start: {e}")
            # Non-critical - continue without watcher

        # 6. CORTEX - Das Zentrale Nervensystem (Phase 8)
        # "Das Nervensystem, nicht das Gehirn" - NAGAs observe, correlate, inform
        if self._config.cortex.enabled:
            try:
                from vibe_core.naga.cortex import NagaCortex
                from vibe_core.naga.cortex.cortex_main import CortexConfig

                cortex_config = CortexConfig(
                    enabled=self._config.cortex.enabled,
                    signal_buffer_size=self._config.cortex.signal_buffer_size,
                    correlation_threshold=self._config.cortex.correlation_threshold,
                    max_signal_age_seconds=self._config.cortex.max_signal_age_seconds,
                    auto_dispatch=self._config.cortex.auto_dispatch,
                    log_decisions=self._config.cortex.log_decisions,
                )
                self._cortex = NagaCortex(self, cortex_config)
                logger.info("🧠 NAGA Cortex initialized - Das Nervensystem aktiv")

                # 6.1 Wire signal sources to Cortex (non-invasive integration)
                # FloodManager sends FloodSignals
                if self._flood_manager:
                    self._flood_manager.set_cortex_callback(self._cortex.receive_signal)
                    logger.info("🧠 Cortex <- FloodManager wired")

                # CommitWatcher sends CommitSignals
                if self._commit_watcher:
                    self._commit_watcher.set_cortex_callback(self._cortex.receive_signal)
                    logger.info("🧠 Cortex <- CommitWatcher wired")

            except Exception as e:
                logger.warning(f"🧠 NAGA Cortex failed to start: {e}")
                # Non-critical - continue without cortex

        # 7. Register the Federation itself for service discovery
        # This allows other components (like Prakriti) to find the CommitWatcher
        ServiceRegistry.register(NagaFederationProtocol, self)
        logger.info("🐍 NAGA Federation registered in ServiceRegistry")

        self._initialized = True
        logger.info("🐍 NAGA Federation initialized")

    # =========================================================================
    # Status & Health
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get federation health status."""
        return {
            "initialized": self._initialized,
            "sesha": self._sesha.get_status().to_dict() if self._sesha else None,
            "vasuki": self._vasuki.get_status().to_dict() if self._vasuki else None,
            "takshaka": self._takshaka.get_status().to_dict() if self._takshaka else None,
            "flood_manager": self._flood_manager.get_status() if self._flood_manager else None,
            "commit_watcher": self._commit_watcher.get_stats() if self._commit_watcher else None,
            "cortex": self._cortex.get_status() if self._cortex else None,
        }

    def is_ready(self) -> bool:
        """Check if all enabled NAGAs are healthy."""
        if not self._initialized:
            return False

        # Check each enabled NAGA
        if self._config.sesha.enabled and (not self._sesha or not self._sesha.get_status().healthy):
            return False
        if self._config.takshaka.enabled and (not self._takshaka or not self._takshaka.get_status().healthy):
            return False
        if self._config.vasuki.enabled and (not self._vasuki or not self._vasuki.get_status().healthy):
            return False

        return True

    # =========================================================================
    # Access to individual NAGAs
    # =========================================================================

    @property
    def sesha(self) -> Optional["SeshaService"]:
        """Get Sesha service (or None if disabled)."""
        return self._sesha

    @property
    def vasuki(self) -> Optional["VasukiService"]:
        """Get Vasuki service (or None if disabled)."""
        return self._vasuki

    @property
    def takshaka(self) -> Optional["TakshakaService"]:
        """Get Takshaka service (or None if disabled)."""
        return self._takshaka

    @property
    def config(self) -> Optional["NagaConfig"]:
        """Get the active configuration."""
        return self._config

    @property
    def flood_manager(self) -> Optional["NagaFloodManager"]:
        """Get Flood Manager (or None if disabled)."""
        return self._flood_manager

    @property
    def commit_watcher(self) -> Optional["NagaCommitWatcher"]:
        """Get Commit Watcher (or None if disabled)."""
        return self._commit_watcher

    @property
    def state_proxy(self) -> Optional["NagaStateProxy"]:
        """Get State Proxy (Der Kommissar) for Dharma-validated state writes."""
        return self._state_proxy

    @property
    def cortex(self) -> Optional["NagaCortex"]:
        """Get Cortex (Das Nervensystem) for signal correlation and decision making."""
        return self._cortex
