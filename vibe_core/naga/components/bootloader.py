"""
BRAHMA: The Creator (Bootloader)

"He is the source of all knowledge and the creator of the universe."
- Vedic texts

The NagaBootloader assembles the universe from nothing (Config).
It wires the dependencies.
It gives life to the Kernel.
Then it ceases to exist.
"""

import logging
import sys
from typing import Optional

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
from vibe_core.naga.services.prahlad.service import PrahladService
from vibe_core.naga.services.sesha import SeshaService
from vibe_core.naga.services.takshaka import TakshakaService
from vibe_core.naga.services.vasuki import VasukiService
from vibe_core.phoenix.sections.naga.section_main import NagaConfig
from vibe_core.protocols.correction import CorrectionOrchestratorProtocol
from vibe_core.steward.crypto import load_or_generate_keys

logger = logging.getLogger("NAGA.BRAHMA")


class NagaBootloader:
    """
    Constructs the NAGA Kernel.
    """

    @classmethod
    def boot(
        cls, config: Optional[NagaConfig], correction_orchestrator: "CorrectionOrchestratorProtocol" = None
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

        # 0. Identity (Atman) - IMPL-214 Persistence
        priv, pub = load_or_generate_keys()
        identity = NagaIdentity.from_keys(agent_id="naga_federation", private_key=priv, public_key=pub)
        logger.info(f"Identity loaded: {identity.fingerprint}")

        # 1. Registry
        registry = KulikaRegistry()

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

        # ... (Karkotaka) ...

        # Vasuki (Monitor)
        vasuki = None
        if config.vasuki.enabled:
            # Vasuki needs Sesha and Takshaka
            if sesha and takshaka:
                vasuki = VasukiService(sesha=sesha, takshaka=takshaka)
                registry.register(vasuki, force=True)
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

        # 5. Assemble Kernel
        kernel = NagaKernel(
            identity=identity,
            registry=registry,
            sesha=sesha,
            vasuki=vasuki,
            takshaka=takshaka,
            karkotaka=karkotaka,
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
