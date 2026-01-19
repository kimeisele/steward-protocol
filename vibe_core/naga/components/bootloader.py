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
from typing import Optional

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
from vibe_core.protocols.correction import CorrectionOrchestratorProtocol
from vibe_core.protocols.identity import IdentityProtocol, KeyStoreProtocol
from vibe_core.steward.crypto import generate_keys
from vibe_core.steward.keystore import FileKeyStore

logger = logging.getLogger("NAGA.BRAHMA")


class NagaBootloader:
    """
    Constructs the NAGA Kernel.
    """

    @classmethod
    def boot(
        cls,
        config: Optional[NagaConfig],
        correction_orchestrator: "CorrectionOrchestratorProtocol" = None,
        key_store: Optional[KeyStoreProtocol] = None,
    ) -> "NagaKernel":
        """
        The Act of Creation.
        """
        if config is None:
            config = NagaConfig()

        # -1. Scan for Services (Narada)
        sys.stderr.write(">>> BOOTSTRAP: Scanning...\n")
        from vibe_core.naga.scanner import NaradaScanner

        scanner = NaradaScanner()
        discovered = scanner.scan()
        logger.info(f"🔍 Narada discovered {len(discovered)} NAGA services")

        # 0. Identity (Atman) - IMPL-214 Persistence (Ashvamedha Refactoring)
        if key_store is None:
            key_store = FileKeyStore()

        keys = key_store.load("naga_federation")

        if keys:
            priv_bytes, pub_bytes = keys
            priv_pem = priv_bytes.decode("utf-8")
            pub_pem = pub_bytes.decode("utf-8")
        else:
            # Generate new keys (if L1 Missing)
            logger.info("Generating new keys for naga_federation")
            priv_pem, pub_pem = generate_keys()
            key_store.save("naga_federation", priv_pem.encode("utf-8"), pub_pem.encode("utf-8"))

        identity = NagaIdentity.from_keys(agent_id="naga_federation", private_key=priv_pem, public_key=pub_pem)
        logger.info(f"Identity loaded: {identity.fingerprint}")

        # 0.5 Steward (The Sovereign) - IMPL-217 Operation Narasimha Phase 2
        from vibe_core.phoenix.section_loader import SectionLoader
        from vibe_core.phoenix.sections.steward.section_main import StewardConfig
        from vibe_core.protocols.steward import StewardProtocol
        from vibe_core.steward.manager import DigitalSteward

        # Load "Persona" from config/steward.yaml via SectionLoader
        try:
            sections, _ = SectionLoader.discover()
            steward_config = sections.get("steward", StewardConfig())
        except Exception:
            logger.warning("SectionLoader failed - creating default Steward Config")
            steward_config = StewardConfig()  # Default empty persona

        # Create Active Steward (Hand + Stift)
        steward = DigitalSteward(identity=identity, config=steward_config)
        logger.info(f"Steward activated: Role='{steward.config.user_context.default_user.role}'")

        # 1. Registry
        registry = KulikaRegistry()

        # Register Steward in ServiceRegistry (Global DI, NOT KulikaRegistry)
        # Steward is accessed via ServiceRegistry.get(StewardProtocol)
        ServiceRegistry.register(StewardProtocol, steward)

        # 2. Base Services (Kings)
        # ------------------------

        # Sesha (Memory)
        sesha = None
        if config.sesha.enabled:
            # NOTE: Legacy SeshaService init doesn't take registry, it might use global.
            # We follow existing patterns.
            sesha = SeshaService()
            registry.register(sesha, force=True)
            if correction_orchestrator:
                correction_orchestrator.dispatcher.register_handler("sesha", sesha)

        # Takshaka (Biter)
        takshaka = None
        if config.takshaka.enabled:
            if sesha:
                # Pass trust_mode from config
                takshaka = TakshakaService(sesha=sesha, trust_mode=config.takshaka.trust_mode)
                registry.register(takshaka, force=True)
                if correction_orchestrator:
                    correction_orchestrator.dispatcher.register_handler("takshaka", takshaka)
            else:
                logger.warning("Takshaka disabled: Sesha is required.")

        # Vasuki (Monitor)
        vasuki = None
        if config.vasuki.enabled:
            # Vasuki needs Sesha and Takshaka
            if sesha and takshaka:
                vasuki = VasukiService(sesha=sesha, takshaka=takshaka)
                registry.register(vasuki, force=True)
                if correction_orchestrator:
                    correction_orchestrator.dispatcher.register_handler("vasuki", vasuki)
            else:
                logger.warning("Vasuki disabled: Sesha and Takshaka are required.")

        # Karkotaka (Secrets)
        karkotaka = None
        if config.karkotaka.enabled:
            karkotaka = KarkotakaService()
            registry.register(karkotaka, force=True)

        # 3. Intelligence
        # ---------------

        # Cortex (Mind)
        cortex = None
        if config.cortex.enabled:
            # Cortex needs orchestrator reference? Or just services?
            # It usually takes `naga_orchestrator`.
            # We will pass the KERNEL later?
            # Wait, Cortex expects an object with .takshaka etc.
            # The Kernel satisfies that duck-typing mostly, but Cortex takes `naga_orchestrator`.
            # We might need to pass `None` first and attach Kernel later, or pass a proxy.
            # For now, let's instantiate.
            cortex = NagaCortex(naga_orchestrator=None, config=config.cortex)

        # 4. Governance & Reliability (The Judges)
        # ----------------------------------------

        # Kaliya (Quarantine)
        kaliya = None
        # Using config fallback or default enabled
        if getattr(config, "kaliya_enabled", True):
            kaliya = KaliyaService(cortex=cortex, identity=identity)
            registry.register(kaliya, force=True)
            if correction_orchestrator:
                correction_orchestrator.dispatcher.register_handler("kaliya", kaliya)

        # Chitragupta (Profiler)
        chitragupta = None
        if getattr(config, "chitragupta_enabled", True):
            chitragupta = ChitraguptaService(cortex=cortex, identity=identity)
            registry.register(chitragupta, force=True)
            if correction_orchestrator:
                correction_orchestrator.dispatcher.register_handler("chitragupta", chitragupta)

        # Narada (Observer - The Cosmic Journalist)
        # NOTE: Narada is GOVERNANCE, not Infrastructure - no CorrectionHandler
        narada = None
        if getattr(config, "narada_enabled", True):
            narada = NaradaService(cortex=cortex, identity=identity)
            registry.register(narada, force=True)
            logger.info("🎵 NARADA activated - The Observer sees all")

        # Prahlad (Resilience)
        prahlad = None
        if config.prahlad.enabled:
            prahlad = PrahladService(cortex=cortex, identity=identity)
            registry.register(prahlad, force=True)
            if correction_orchestrator:
                correction_orchestrator.dispatcher.register_handler("prahlad", prahlad)

        # 4. Stability & Observability
        # ----------------------------

        # Ouroboros (Watcher)
        ouroboros = None
        if config.prahlad.enabled:
            # Config field might be slightly different, checking standard
            # Assuming 'ouroboros_enabled' or similar exists on NagaConfig or implicity
            # Going safe, assuming default enabled if not found or explicit
            ouroboros = NagaOuroboros(orchestrator=None)  # type: ignore
            if cortex:
                cortex.set_ouroboros(ouroboros)

        # Flood Manager
        flood = None
        if config.flood.enabled:
            flood = NagaFloodManager(sesha=sesha, takshaka=takshaka, enabled=True, config=config.flood)
            flood.start()

            if cortex:
                flood.set_cortex_callback(cortex.receive_signal)

        # Commit Watcher
        watcher = None
        if config.commit_watcher.enabled:
            watcher = CommitWatcher(
                sesha=sesha, takshaka=takshaka, enabled=config.commit_watcher.enabled, config=config.commit_watcher
            )

        # 4.5 PROTOCOL REGISTRATION (ServiceRegistry Binding)
        # ---------------------------------------------------
        # NagaProxy._resolve_nagas() needs Protocol-keyed services.
        # Without this, observations are created but NOT routed to NAGA services.
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

        # 5. Assemble Kernel
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

        # 6. Post-Wiring (Circular deps)
        if cortex:
            # Cortex needs access to the system.
            # Previously it took 'naga_orchestrator'.
            # We should inject the Kernel (Vishnu) as the source of truth.
            # Note: Cortex might still expect 'orchestrator' typing.
            # We rely on Duck Typing or we might updating Cortex later.
            cortex._naga_orchestrator = kernel  # type: ignore

            # Also bootstrapping cortex deps if not passed in init
            cortex._shesha_service = sesha
            cortex._takshaka_service = takshaka

        if ouroboros:
            ouroboros._orchestrator = kernel  # type: ignore

        # 7. Hiranyakashipu (Attack Framework)
        # ------------------------------------
        if config.prahlad.enabled and config.prahlad.chaos_probe_enabled:
            try:
                from pathlib import Path

                from vibe_core.naga.hiranyakashipu import (
                    LivingTestFramework,
                    inject_seeds_from_narada,
                    wire_hiranyakashipu_to_protocols,
                )

                # Create the LIVING framework
                living_framework = LivingTestFramework()

                # Load seeds from the package
                # adjust path to be relative to this file or vibe_core/naga
                # This file is vibe_core/naga/components/bootloader.py
                # seeds are in vibe_core/naga/hiranyakashipu/seeds
                seed_dir = Path(__file__).parent.parent / "hiranyakashipu" / "seeds"

                if seed_dir.exists():
                    living_framework.add_seed_dir(seed_dir)
                    seed_count = living_framework.load_seeds()
                    logger.info(f"🔥 BRAHMA: Loaded {seed_count} Hiranyakashipu attack seeds")

                # Wire to protocols
                # Note: wire_hiranyakashipu_to_protocols expects module name or object?
                # It usually patches vibe_core.
                wire_hiranyakashipu_to_protocols(living_framework, "vibe_core")

                # Narada Injection
                try:
                    # We inject seeds from the scanner we created earlier
                    inject_seeds_from_narada(scanner, living_framework)
                    logger.info("🔥 BRAHMA: Narada seeds injected")
                except Exception as e:
                    logger.warning(f"!!! BRAHMA: Narada seed injection failed: {e}")

                logger.info("🔥 BRAHMA: HIRANYAKASHIPU wired - Attack Framework active")
            except Exception as e:
                logger.warning(f"!!! BRAHMA: HIRANYAKASHIPU failed to wire: {e}")

        logger.info("🪷 BRAHMA: Creation complete. The Lotus opens.")
        return kernel
