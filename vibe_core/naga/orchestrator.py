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
from vibe_core.naga.scanner import NaradaScanner
from vibe_core.protocols.correction import DriftSource
from vibe_core.protocols.naga import (
    ChitraguptaProtocol,
    KaliyaProtocol,
    NagaFederationProtocol,
    NaradaProtocol,
    PrahladProtocol,
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
    from vibe_core.naga.identity import NagaIdentity
    from vibe_core.naga.ouroboros import NagaOuroboros
    from vibe_core.naga.services.chitragupta import ChitraguptaService
    from vibe_core.naga.services.kaliya import KaliyaService

    # Governance Layer (NOT Nagas by race)
    from vibe_core.naga.services.narada import NaradaService
    from vibe_core.naga.services.prahlad import PrahladService

    # Infrastructure Layer (Real Nagas)
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
        # ===== INFRASTRUCTURE LAYER (Real Nagas - 🐍) =====
        self._sesha: Optional["SeshaService"] = None
        self._vasuki: Optional["VasukiService"] = None
        self._takshaka: Optional["TakshakaService"] = None
        self._kaliya: Optional["KaliyaService"] = None

        # ===== GOVERNANCE LAYER (Personnel - NOT Nagas) =====
        self._narada: Optional["NaradaService"] = None
        self._chitragupta: Optional["ChitraguptaService"] = None
        self._prahlad: Optional["PrahladService"] = None

        # ===== INFRASTRUCTURE COMPONENTS =====
        self._flood_manager: Optional["NagaFloodManager"] = None
        self._commit_watcher: Optional["NagaCommitWatcher"] = None
        self._state_proxy: Optional["NagaStateProxy"] = None
        self._cortex: Optional["NagaCortex"] = None
        self._ouroboros: Optional["NagaOuroboros"] = None

        self._initialized = False
        self._config: Optional["NagaConfig"] = None

        # GAD-000 37th Principle: Sovereign identity for signing decisions
        from vibe_core.naga.identity import NagaIdentity

        self._identity: Optional[NagaIdentity] = None

        # Narada Scanner for auto-discovery and validation
        self._scanner: Optional[NaradaScanner] = None

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

        INFRASTRUCTURE LAYER (Real Nagas 🐍):
        1. Sesha first (foundation - Data/Truth)
        2. Takshaka second (guardian - Security)
        3. Vasuki third (bridge - Network)
        4. Kaliya fourth (quarantine - Isolation)

        GOVERNANCE LAYER (Personnel - NOT Nagas):
        5. Narada (spy - Observation)
        6. Chitragupta (profiler - Behavioral)
        7. Prahlad (governor - Resilience) - LAST, oversees all
        """
        from vibe_core.naga.identity import NagaIdentity
        from vibe_core.naga.services.chitragupta import ChitraguptaService
        from vibe_core.naga.services.kaliya import KaliyaService

        # Governance Layer
        from vibe_core.naga.services.narada import NaradaService
        from vibe_core.naga.services.prahlad import PrahladService

        # Infrastructure Layer
        from vibe_core.naga.services.sesha import SeshaService
        from vibe_core.naga.services.takshaka import TakshakaService
        from vibe_core.naga.services.vasuki import VasukiService

        self._config = self._get_config(config)

        # -1. NARADA SCANNER - Auto-discover available NAGAs
        # "Narada unterrichtete Prahlad im Mutterleib" - discovery before birth
        self._scanner = NaradaScanner()
        discovered = self._scanner.scan()
        logger.info(f"🔍 Narada discovered {len(discovered)} NAGA services")

        # 0. IDENTITY - GAD-000 37th Principle
        # Generate sovereign identity for signing decisions
        self._identity = NagaIdentity.generate("naga_federation")
        logger.info(f"🔑 NAGA Identity: {self._identity.fingerprint}")

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

        # 4. KALIYA - The Quarantine (Isolation Protocol)
        if self._config.kaliya.enabled:
            self._kaliya = KaliyaService(
                cortex=None,  # Will be wired after cortex creation
                identity=self._identity,
            )
            ServiceRegistry.register(KaliyaProtocol, self._kaliya)
            correction_orchestrator.dispatcher.register_handler(
                DriftSource.RELIABILITY,
                self._kaliya.as_handler(),
                handler_id="kaliya",
                priority=80,  # High priority for isolation
            )
            logger.info("🐍 KALIYA registered - Isolation Protocol active")

        # =========================================================================
        # GOVERNANCE LAYER (Personnel - NOT Nagas by race)
        # =========================================================================

        # 5. NARADA - The Messenger/Spy (Decorator-based Observation)
        # NOTE: Narada is pure observer - does NOT register CorrectionHandler
        if self._config.narada.enabled:
            self._narada = NaradaService(
                cortex=None,  # Will be wired after cortex creation
                identity=self._identity,
            )
            ServiceRegistry.register(NaradaProtocol, self._narada)
            # Narada observes only - no CorrectionHandler registration
            logger.info("🎵 NARADA registered - Messenger observes all")

        # 6. CHITRAGUPTA - The Accountant/Profiler (Behavioral Analysis)
        if self._config.chitragupta.enabled:
            self._chitragupta = ChitraguptaService(
                cortex=None,  # Will be wired after cortex creation
                identity=self._identity,
            )
            ServiceRegistry.register(ChitraguptaProtocol, self._chitragupta)
            correction_orchestrator.dispatcher.register_handler(
                DriftSource.PERFORMANCE,
                self._chitragupta.as_handler(),
                handler_id="chitragupta",
                priority=60,  # Medium priority for profiling
            )
            logger.info("📜 CHITRAGUPTA registered - Karma is being recorded")

        # 7. PRAHLAD - The Governor (Resilience & Antifragility)
        # LAST in governance - oversees all NAGAs
        if self._config.prahlad.enabled:
            self._prahlad = PrahladService(
                cortex=None,  # Will be wired after cortex creation
                identity=self._identity,
            )
            ServiceRegistry.register(PrahladProtocol, self._prahlad)
            correction_orchestrator.dispatcher.register_handler(
                DriftSource.STRUCTURAL,
                self._prahlad.as_handler(),
                handler_id="prahlad",
                priority=90,  # Very high - structural integrity
            )
            logger.info("👑 PRAHLAD registered - Governor oversees all")

        # =========================================================================
        # INFRASTRUCTURE COMPONENTS
        # =========================================================================

        # 8. FLOOD MANAGER - Organic Flooding (Phase 2)
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
                # Inject identity for decision signing (37th Principle)
                self._cortex._identity = self._identity
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

                # Wire Cortex to Governance Layer services
                if self._kaliya:
                    self._kaliya._cortex = self._cortex
                    logger.info("🧠 Cortex -> Kaliya wired")

                if self._narada:
                    self._narada._cortex = self._cortex
                    logger.info("🧠 Cortex -> Narada wired")

                if self._chitragupta:
                    self._chitragupta._cortex = self._cortex
                    logger.info("🧠 Cortex -> Chitragupta wired")

                if self._prahlad:
                    self._prahlad._cortex = self._cortex
                    logger.info("🧠 Cortex -> Prahlad wired")

            except Exception as e:
                logger.warning(f"🧠 NAGA Cortex failed to start: {e}")
                # Non-critical - continue without cortex

        # 7. OUROBOROS - GAD-000 Recoverability (NAGAs watching NAGAs)
        # "Die Schlange, die ihren eigenen Schwanz frisst" - self-healing loop
        if self._cortex:
            try:
                from vibe_core.naga.ouroboros import NagaOuroboros

                self._ouroboros = NagaOuroboros(orchestrator=self)
                # Inject OUROBOROS into Cortex for correction observation
                self._cortex._ouroboros = self._ouroboros
                logger.info("🐍 OUROBOROS initialized - Die Schlange wacht")
            except Exception as e:
                logger.warning(f"🐍 OUROBOROS failed to start: {e}")
                # Non-critical - continue without OUROBOROS

        # 8. Register the Federation itself for service discovery
        # This allows other components (like Prakriti) to find the CommitWatcher
        ServiceRegistry.register(NagaFederationProtocol, self)
        logger.info("🐍 NAGA Federation registered in ServiceRegistry")

        self._initialized = True

        # Register created instances with scanner for status reporting
        if self._sesha:
            self._scanner.set_instance("sesha", self._sesha)
        if self._takshaka:
            self._scanner.set_instance("takshaka", self._takshaka)
        if self._vasuki:
            self._scanner.set_instance("vasuki", self._vasuki)
        if self._kaliya:
            self._scanner.set_instance("kaliya", self._kaliya)
        if self._narada:
            self._scanner.set_instance("narada", self._narada)
        if self._chitragupta:
            self._scanner.set_instance("chitragupta", self._chitragupta)
        if self._prahlad:
            self._scanner.set_instance("prahlad", self._prahlad)

        logger.info("🐍 NAGA Federation initialized")

    # =========================================================================
    # Status & Health
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get federation health status - all 7 members + infrastructure."""
        return {
            "initialized": self._initialized,
            # Infrastructure Layer (Real Nagas 🐍)
            "sesha": self._sesha.get_status().to_dict() if self._sesha else None,
            "vasuki": self._vasuki.get_status().to_dict() if self._vasuki else None,
            "takshaka": self._takshaka.get_status().to_dict() if self._takshaka else None,
            "kaliya": self._kaliya.get_status().to_dict() if self._kaliya else None,
            # Governance Layer (Personnel)
            "narada": self._narada.get_status().to_dict() if self._narada else None,
            "chitragupta": self._chitragupta.get_status().to_dict() if self._chitragupta else None,
            "prahlad": self._prahlad.get_status().to_dict() if self._prahlad else None,
            # Infrastructure Components
            "flood_manager": self._flood_manager.get_status() if self._flood_manager else None,
            "commit_watcher": self._commit_watcher.get_stats() if self._commit_watcher else None,
            "cortex": self._cortex.get_status() if self._cortex else None,
            "ouroboros": self._ouroboros.get_status() if self._ouroboros else None,
        }

    def is_ready(self) -> bool:
        """Check if all enabled NAGAs are healthy."""
        if not self._initialized:
            return False

        # Infrastructure Layer
        if self._config.sesha.enabled and (not self._sesha or not self._sesha.get_status().healthy):
            return False
        if self._config.takshaka.enabled and (not self._takshaka or not self._takshaka.get_status().healthy):
            return False
        if self._config.vasuki.enabled and (not self._vasuki or not self._vasuki.get_status().healthy):
            return False
        if self._config.kaliya.enabled and (not self._kaliya or not self._kaliya.get_status().healthy):
            return False

        # Governance Layer
        if self._config.narada.enabled and (not self._narada or not self._narada.get_status().healthy):
            return False
        if self._config.chitragupta.enabled and (not self._chitragupta or not self._chitragupta.get_status().healthy):
            return False
        if self._config.prahlad.enabled and (not self._prahlad or not self._prahlad.get_status().healthy):
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
    def kaliya(self) -> Optional["KaliyaService"]:
        """Get Kaliya service - 🐍 Quarantine/Isolation (or None if disabled)."""
        return self._kaliya

    @property
    def narada(self) -> Optional["NaradaService"]:
        """Get Narada service - 🎵 Deva-Rishi Messenger/Spy (or None if disabled)."""
        return self._narada

    @property
    def chitragupta(self) -> Optional["ChitraguptaService"]:
        """Get Chitragupta service - 📜 Yama's Accountant/Profiler (or None if disabled)."""
        return self._chitragupta

    @property
    def prahlad(self) -> Optional["PrahladService"]:
        """Get Prahlad service - 👑 Daitya Governor/Resilience (or None if disabled)."""
        return self._prahlad

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

    @property
    def identity(self) -> Optional["NagaIdentity"]:
        """Get Federation identity (37th Principle) for signing decisions."""
        return self._identity

    @property
    def ouroboros(self) -> Optional["NagaOuroboros"]:
        """Get OUROBOROS (GAD-000 Recoverability) for self-healing loop detection."""
        return self._ouroboros

    @property
    def scanner(self) -> Optional[NaradaScanner]:
        """Get Narada Scanner for auto-discovery metadata and reports."""
        return self._scanner
