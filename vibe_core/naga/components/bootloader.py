"""
BRAHMA: The Creator (Bootloader)

"He is the source of all knowledge and the creator of the universe."
- Vedic texts

The NagaBootloader assembles the universe from nothing (Config).
It wires the dependencies.
It gives life to the Kernel.
Then it ceases to exist.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xba4beefb"  # GenesisByte: parampara % 37 == 0

import logging
import sys
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from vibe_core.protocols.ledger import VibeLedger

from vibe_core.di import ServiceRegistry
from vibe_core.naga.commit_watcher import NagaCommitWatcher as CommitWatcher
from vibe_core.naga.components.destructor import NagaDestructor
from vibe_core.naga.components.kernel import NagaKernel
from vibe_core.naga.cortex.cortex_main import NagaCortex
from vibe_core.naga.flood import NagaFloodManager
from vibe_core.naga.identity import NagaIdentity

# Services
from vibe_core.naga.kulika import KulikaRegistry
from vibe_core.naga.ouroboros import NagaOuroboros
from vibe_core.naga.services.chitragupta import ChitraguptaService
from vibe_core.naga.services.kaliya import KaliyaService
from vibe_core.naga.services.karkotaka import KarkotakaService
from vibe_core.naga.services.narada import NaradaService
from vibe_core.naga.services.prahlad.service import PrahladService
from vibe_core.naga.services.sesha import SeshaService
from vibe_core.naga.services.takshaka import TakshakaService
from vibe_core.naga.services.vasuki import VasukiService

# Protocols (for ServiceRegistry binding)
from vibe_core.protocols.naga import (
    ChitraguptaProtocol,
    KaliyaProtocol,
    NaradaProtocol,
    SeshaProtocol,
    TakshakaProtocol,
    VasukiProtocol,
)
from vibe_core.phoenix.sections.naga.section_main import NagaConfig
from vibe_core.protocols.correction import CorrectionOrchestratorProtocol, DriftSource
from vibe_core.protocols.identity import IdentityProtocol, KeyStoreProtocol
from vibe_core.steward.crypto import generate_keys
from vibe_core.steward.keystore import FileKeyStore

logger = logging.getLogger("NAGA.BRAHMA")


class NagaBootloader:
    """
    Constructs the NAGA Kernel.
    """

    # =========================================================================
    # BOOT STEPS — Atomic, granular, individually callable
    # Scan → Identity → Steward → Services → Governance → Bind → Assemble
    # =========================================================================

    @classmethod
    def _boot_scan(cls) -> tuple:
        """Boot Step 0: Narada service discovery. Returns (scanner, discovered)."""
        sys.stderr.write(">>> BOOTSTRAP: Scanning...\n")
        from vibe_core.naga.scanner import NaradaScanner

        scanner = NaradaScanner()
        discovered = scanner.scan()
        logger.info(f"🔍 Narada discovered {len(discovered)} NAGA services")
        return scanner, discovered

    @classmethod
    def _boot_identity(cls, key_store: Optional[KeyStoreProtocol]) -> NagaIdentity:
        """Boot Step 1: Load or generate identity keys. Returns NagaIdentity."""
        if key_store is None:
            key_store = FileKeyStore()
        keys = key_store.load("naga_federation")
        if keys:
            priv_bytes, pub_bytes = keys
            priv_pem = priv_bytes.decode("utf-8")
            pub_pem = pub_bytes.decode("utf-8")
        else:
            logger.info("Generating new keys for naga_federation")
            priv_pem, pub_pem = generate_keys()
            key_store.save("naga_federation", priv_pem.encode("utf-8"), pub_pem.encode("utf-8"))
        identity = NagaIdentity.from_keys(agent_id="naga_federation", private_key=priv_pem, public_key=pub_pem)
        logger.info(f"Identity loaded: {identity.fingerprint}")
        return identity

    @classmethod
    def _boot_steward(cls, identity: NagaIdentity) -> object:
        """Boot Step 2: Create and register DigitalSteward. Returns steward."""
        from vibe_core.phoenix.section_loader import SectionLoader
        from vibe_core.phoenix.sections.steward.section_main import StewardConfig
        from vibe_core.protocols.steward import StewardProtocol
        from vibe_core.steward.manager import DigitalSteward

        try:
            sections, _ = SectionLoader.discover()
            steward_config = sections.get("steward", StewardConfig())
        except Exception:
            logger.warning("SectionLoader failed - creating default Steward Config")
            steward_config = StewardConfig()
        steward = DigitalSteward(identity=identity, config=steward_config)
        logger.info(f"Steward activated: Role='{steward.config.user_context.default_user.role}'")
        ServiceRegistry.register(StewardProtocol, steward)
        return steward

    @classmethod
    def _boot_base_services(
        cls,
        config: NagaConfig,
        registry: KulikaRegistry,
        correction_orchestrator: "CorrectionOrchestratorProtocol",
        ledger: Optional["VibeLedger"],
    ) -> tuple:
        """Boot Step 3: Create base services (Sesha, Takshaka, Vasuki, Karkotaka).
        Returns (sesha, takshaka, vasuki, karkotaka)."""
        sesha = None
        if config.sesha.enabled:
            sesha = SeshaService()
            registry.register(sesha, force=True)
            if correction_orchestrator:
                correction_orchestrator.dispatcher.register_handler(
                    DriftSource.STATE, sesha.as_handler(), handler_id="sesha"
                )
            if ledger:
                sesha.inject_ledger(ledger)
                logger.info("🐍 SESHA: Kernel ledger injected - Full persistence active")

        takshaka = None
        if config.takshaka.enabled:
            if sesha:
                takshaka = TakshakaService(sesha=sesha, trust_mode=config.takshaka.trust_mode)
                registry.register(takshaka, force=True)
                if correction_orchestrator:
                    correction_orchestrator.dispatcher.register_handler(
                        DriftSource.COGNITIVE, takshaka.as_handler(), handler_id="takshaka"
                    )
            else:
                logger.warning("Takshaka disabled: Sesha is required.")

        vasuki = None
        if config.vasuki.enabled:
            if sesha and takshaka:
                vasuki = VasukiService(sesha=sesha, takshaka=takshaka)
                registry.register(vasuki, force=True)
                if correction_orchestrator:
                    correction_orchestrator.dispatcher.register_handler(
                        DriftSource.CONFIG, vasuki.as_handler(), handler_id="vasuki"
                    )
            else:
                logger.warning("Vasuki disabled: Sesha and Takshaka are required.")

        karkotaka = None
        if config.karkotaka.enabled:
            karkotaka = KarkotakaService()
            registry.register(karkotaka, force=True)

        return sesha, takshaka, vasuki, karkotaka

    @classmethod
    def _boot_intelligence_governance(
        cls,
        config: NagaConfig,
        registry: KulikaRegistry,
        identity: NagaIdentity,
        cortex: object,
        correction_orchestrator: "CorrectionOrchestratorProtocol",
    ) -> tuple:
        """Boot Step 4: Create governance services (Kaliya, Chitragupta, Narada, Prahlad).
        Returns (kaliya, chitragupta, narada, prahlad)."""
        kaliya = None
        if getattr(config, "kaliya_enabled", True):
            kaliya = KaliyaService(cortex=cortex, identity=identity)
            registry.register(kaliya, force=True)
            if correction_orchestrator:
                correction_orchestrator.dispatcher.register_handler(
                    DriftSource.RELIABILITY, kaliya.as_handler(), handler_id="kaliya"
                )

        chitragupta = None
        if getattr(config, "chitragupta_enabled", True):
            chitragupta = ChitraguptaService(cortex=cortex, identity=identity)
            registry.register(chitragupta, force=True)
            if correction_orchestrator:
                correction_orchestrator.dispatcher.register_handler(
                    DriftSource.PERFORMANCE, chitragupta.as_handler(), handler_id="chitragupta"
                )

        narada = None
        if getattr(config, "narada_enabled", True):
            narada = NaradaService(cortex=cortex, identity=identity)
            registry.register(narada, force=True)
            logger.info("🎵 NARADA activated - The Observer sees all")

        prahlad = None
        if config.prahlad.enabled:
            prahlad = PrahladService(cortex=cortex, identity=identity)
            registry.register(prahlad, force=True)
            if correction_orchestrator:
                correction_orchestrator.dispatcher.register_handler(
                    DriftSource.STRUCTURAL, prahlad.as_handler(), handler_id="prahlad"
                )

        return kaliya, chitragupta, narada, prahlad

    @classmethod
    def _boot_stability(cls, config: NagaConfig, cortex: object, sesha: object, takshaka: object) -> tuple:
        """Boot Step 5: Create stability services (Ouroboros, Flood, CommitWatcher).
        Returns (ouroboros, flood, watcher)."""
        ouroboros = None
        if config.prahlad.enabled:
            ouroboros = NagaOuroboros(orchestrator=None)  # type: ignore
            if cortex:
                cortex.set_ouroboros(ouroboros)

        flood = None
        if config.flood.enabled:
            flood = NagaFloodManager(sesha=sesha, takshaka=takshaka, enabled=True, config=config.flood)
            flood.start()
            if cortex:
                flood.set_cortex_callback(cortex.receive_signal)

        watcher = None
        if config.commit_watcher.enabled:
            watcher = CommitWatcher(
                sesha=sesha, takshaka=takshaka, enabled=config.commit_watcher.enabled, config=config.commit_watcher
            )

        return ouroboros, flood, watcher

    @classmethod
    def _boot_bind_protocols(cls, sesha, takshaka, vasuki, kaliya, chitragupta, narada) -> None:
        """Boot Step 6: Register NAGA services in ServiceRegistry for protocol routing."""
        if sesha:
            ServiceRegistry.register(SeshaProtocol, sesha)
        if takshaka:
            ServiceRegistry.register(TakshakaProtocol, takshaka)
        if vasuki:
            ServiceRegistry.register(VasukiProtocol, vasuki)
        if kaliya:
            ServiceRegistry.register(KaliyaProtocol, kaliya)
        if chitragupta:
            ServiceRegistry.register(ChitraguptaProtocol, chitragupta)
        if narada:
            ServiceRegistry.register(NaradaProtocol, narada)
        logger.info("🐍 BRAHMA: Protocol bindings complete - NAGA services observable")

    @classmethod
    def _boot_wire_hiranyakashipu(cls, config: NagaConfig, scanner: object) -> None:
        """Boot Step 7: Wire Hiranyakashipu attack framework (if enabled)."""
        if not (config.prahlad.enabled and config.prahlad.chaos_probe_enabled):
            return
        try:
            from pathlib import Path
            from vibe_core.naga.hiranyakashipu import (
                LivingTestFramework,
                inject_seeds_from_narada,
                wire_hiranyakashipu_to_protocols,
            )

            living_framework = LivingTestFramework()
            seed_dir = Path(__file__).parent.parent / "hiranyakashipu" / "seeds"
            if seed_dir.exists():
                living_framework.add_seed_dir(seed_dir)
                seed_count = living_framework.load_seeds()
                logger.info(f"🔥 BRAHMA: Loaded {seed_count} Hiranyakashipu attack seeds")
            wire_hiranyakashipu_to_protocols(living_framework, "vibe_core")
            try:
                inject_seeds_from_narada(scanner, living_framework)
                logger.info("🔥 BRAHMA: Narada seeds injected")
            except Exception as e:
                logger.warning(f"!!! BRAHMA: Narada seed injection failed: {e}")
            logger.info("🔥 BRAHMA: HIRANYAKASHIPU wired - Attack Framework active")
        except Exception as e:
            logger.warning(f"!!! BRAHMA: HIRANYAKASHIPU failed to wire: {e}")

    @classmethod
    def boot(
        cls,
        config: Optional[NagaConfig],
        correction_orchestrator: "CorrectionOrchestratorProtocol" = None,
        key_store: Optional[KeyStoreProtocol] = None,
        ledger: Optional["VibeLedger"] = None,
    ) -> "NagaKernel":
        """The Act of Creation. Chains the atomic _boot_* steps."""
        if config is None:
            config = NagaConfig()

        scanner, _discovered = cls._boot_scan()
        identity = cls._boot_identity(key_store)
        cls._boot_steward(identity)
        registry = KulikaRegistry()

        sesha, takshaka, vasuki, karkotaka = cls._boot_base_services(config, registry, correction_orchestrator, ledger)

        cortex = None
        if config.cortex.enabled:
            cortex = NagaCortex(naga_orchestrator=None, config=config.cortex)

        kaliya, chitragupta, narada, prahlad = cls._boot_intelligence_governance(
            config, registry, identity, cortex, correction_orchestrator
        )

        ouroboros, flood, watcher = cls._boot_stability(config, cortex, sesha, takshaka)

        cls._boot_bind_protocols(sesha, takshaka, vasuki, kaliya, chitragupta, narada)

        kernel = NagaKernel(
            identity=identity,
            registry=registry,
            sesha=sesha,
            vasuki=vasuki,
            takshaka=takshaka,
            karkotaka=karkotaka,
            kaliya=kaliya,
            chitragupta=chitragupta,
            narada=narada,
            cortex=cortex,
            ouroboros=ouroboros,
            flood_manager=flood,
            commit_watcher=watcher,
        )

        if cortex:
            cortex._naga_orchestrator = kernel  # type: ignore
            cortex._shesha_service = sesha
            cortex._takshaka_service = takshaka
        if ouroboros:
            ouroboros._orchestrator = kernel  # type: ignore

        cls._boot_wire_hiranyakashipu(config, scanner)

        logger.info("🪷 BRAHMA: Creation complete. The Lotus opens.")
        return kernel
