"""
⚡ BOOT ORCHESTRATOR ⚡
======================

The unified boot sequence for Agent City OS.

PHOENIX VIMANA UNIFIED BOOT - Sarga Integration
-----------------------------------------------
This orchestrator now follows the Sarga (cosmic creation) sequence:
1. SHABDA (Sound) → Boot command received
2. AKASHA (Space) → Kernel memory allocated
3. VAYU (Air) → Communication channels established
4. AGNI (Fire) → Form/visibility (UI, capabilities)
5. JALA (Water) → Data streams flow (Knowledge Graph, context)
6. PRITHVI (Earth) → Persistence (Ledger, agents registered)

The system creates itself from nothing. Sound becomes form.

USAGE:
    from vibe_core.boot_orchestrator import BootOrchestrator

    orchestrator = BootOrchestrator()
    kernel = orchestrator.boot()
    # kernel now has all agents registered, Sarga complete
"""

import logging
from pathlib import Path
from typing import Optional

from steward.system_agents.discoverer.agent import Discoverer
from vibe_core.config import CityConfig
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.sarga import Element, get_sarga

logger = logging.getLogger("BOOT_ORCHESTRATOR")


class BootOrchestrator:
    """
    Unified boot orchestration for Agent City OS.

    Ensures consistent agent discovery and registration across all entry points.
    """

    def __init__(
        self,
        ledger_path: Optional[str] = None,
        project_root: Optional[Path] = None,
        config: Optional[CityConfig] = None,
    ):
        """
        Initialize the boot orchestrator.

        Args:
            ledger_path: Path to SQLite ledger (default: data/vibe_ledger.db)
            project_root: Project root directory (default: auto-detected)
            config: CityConfig instance (REQUIRED: Phoenix Config for agents)
        """
        self.ledger_path = ledger_path or "data/vibe_ledger.db"
        self.project_root = project_root or Path.cwd()
        self.config = config  # BLOCKER #0: Phoenix Config integration
        self.kernel: Optional[RealVibeKernel] = None
        self.discoverer: Optional[Discoverer] = None

        # Sarga phase components (initialized during boot)
        self.prompt_context = None  # VAYU phase
        self.oracle = None  # AGNI phase

    def boot(self) -> RealVibeKernel:
        """
        Execute the unified boot sequence via Sarga (cosmic creation).

        Sarga Phases:
        1. SHABDA (Sound) → Boot initiated
        2. AKASHA (Space) → Kernel created
        3. VAYU (Air) → Communication established
        4. AGNI (Fire) → Form rendered (capabilities)
        5. JALA (Water) → Data flows (Knowledge Graph, discovery)
        6. PRITHVI (Earth) → Persistence (agents registered, ledger ready)

        Returns:
            RealVibeKernel: Fully initialized kernel with all agents

        Raises:
            RuntimeError: If boot sequence fails
        """
        # Get global Sarga instance
        sarga = get_sarga()

        # Begin the cosmic creation
        sarga.begin_boot()

        # =================================================================
        # PHASE 1: SHABDA (Sound/Command) - Boot initiated
        # =================================================================
        sarga.register_phase_handler(Element.SHABDA, self._phase_shabda)
        if not sarga.execute_phase(Element.SHABDA):
            raise RuntimeError("Sarga SHABDA phase failed: Boot initiation error")

        # =================================================================
        # PHASE 2: AKASHA (Space/Memory) - Kernel created
        # =================================================================
        sarga.register_phase_handler(Element.AKASHA, self._phase_akasha)
        if not sarga.execute_phase(Element.AKASHA):
            raise RuntimeError("Sarga AKASHA phase failed: Kernel creation error")

        # =================================================================
        # PHASE 3: VAYU (Air/Communication) - Message bus + PromptContext
        # =================================================================
        sarga.register_phase_handler(Element.VAYU, self._phase_vayu)
        if not sarga.execute_phase(Element.VAYU):
            raise RuntimeError("Sarga VAYU phase failed: Communication setup error")

        # =================================================================
        # PHASE 4: AGNI (Fire/Form) - Capabilities visible
        # =================================================================
        sarga.register_phase_handler(Element.AGNI, self._phase_agni)
        if not sarga.execute_phase(Element.AGNI):
            raise RuntimeError("Sarga AGNI phase failed: Form rendering error")

        # =================================================================
        # PHASE 5: JALA (Water/Data) - Knowledge Graph + Discovery
        # =================================================================
        sarga.register_phase_handler(Element.JALA, self._phase_jala)
        if not sarga.execute_phase(Element.JALA):
            raise RuntimeError("Sarga JALA phase failed: Data stream error")

        # =================================================================
        # PHASE 6: PRITHVI (Earth/Persistence) - Agents + Ledger
        # =================================================================
        sarga.register_phase_handler(Element.PRITHVI, self._phase_prithvi)
        if not sarga.execute_phase(Element.PRITHVI):
            raise RuntimeError("Sarga PRITHVI phase failed: Persistence error")

        # Complete the cosmic creation
        sarga.complete_boot()

        # Print boot report
        logger.info(sarga.generate_boot_report())

        return self.kernel

    # =========================================================================
    # SARGA PHASE HANDLERS
    # =========================================================================

    def _phase_shabda(self) -> bool:
        """SHABDA: Sound - Boot command received, initiation logged."""
        logger.info("      → Boot command received")
        logger.info(f"      → Project root: {self.project_root}")
        logger.info(f"      → Ledger path: {self.ledger_path}")
        return True

    def _phase_akasha(self) -> bool:
        """AKASHA: Space - Create kernel, allocate memory."""
        try:
            self.kernel = RealVibeKernel(ledger_path=self.ledger_path)
            logger.info(f"      → Kernel space allocated (ledger: {self.ledger_path})")
            return True
        except Exception as e:
            logger.error(f"      → Kernel creation failed: {e}")
            return False

    def _phase_vayu(self) -> bool:
        """VAYU: Air - Establish communication channels."""
        try:
            # Initialize PromptContext (dynamic prompt generation)
            from vibe_core.runtime.prompt_context import PromptContext

            self.prompt_context = PromptContext()

            # Wire kernel to prompt context (late binding)
            if self.kernel:
                self.prompt_context.set_kernel(self.kernel)
                logger.info("      → PromptContext initialized and kernel bound")

            return True
        except Exception as e:
            logger.warning(f"      → PromptContext setup warning: {e}")
            # Non-fatal - communication still works via kernel
            return True

    def _phase_agni(self) -> bool:
        """AGNI: Fire - Make system visible (capabilities, UI)."""
        try:
            # Initialize KernelOracle (capability discovery)
            from vibe_core.runtime.oracle import KernelOracle

            if self.kernel:
                self.oracle = KernelOracle(self.kernel, self.project_root)
                capabilities = self.oracle.get_system_capabilities()
                logger.info(
                    f"      → Oracle active: {len(capabilities.get('tools', []))} tools, "
                    f"{len(capabilities.get('cartridges', []))} cartridges"
                )
            return True
        except Exception as e:
            logger.warning(f"      → Oracle setup warning: {e}")
            # Non-fatal - capabilities still work via kernel
            return True

    def _phase_jala(self) -> bool:
        """JALA: Water - Data streams flow (Knowledge Graph, discovery)."""
        try:
            # Load Knowledge Graph
            from vibe_core.knowledge.graph import get_knowledge_graph

            graph = get_knowledge_graph()
            logger.info(
                f"      → Knowledge loaded: {len(graph.nodes)} nodes, "
                f"{sum(len(e) for e in graph.edges.values())} edges"
            )

            # Register Discoverer (Genesis Agent)
            self.discoverer = Discoverer(kernel=self.kernel, config=self.config)
            self.kernel.register_agent(self.discoverer)
            logger.info("      → Discoverer (Genesis Agent) registered")

            # Discover all agents
            discovered_count = self.discoverer.discover_agents()
            logger.info(f"      → Discovered {discovered_count} agents")

            return True
        except Exception as e:
            logger.error(f"      → Data stream error: {e}")
            return False

    def _phase_prithvi(self) -> bool:
        """PRITHVI: Earth - Persistence (boot kernel, ledger ready)."""
        try:
            # Boot the kernel (finalizes manifests, ledger, scheduler)
            self.kernel.boot()
            logger.info("      → Kernel booted, ledger active")

            # Final status
            status = self.kernel.get_status()
            total_agents = status.get("agents_registered", 0)
            logger.info(f"      → Total agents registered: {total_agents}")

            return True
        except Exception as e:
            logger.error(f"      → Persistence error: {e}")
            return False

    def get_kernel(self) -> Optional[RealVibeKernel]:
        """
        Get the booted kernel instance.

        Returns:
            RealVibeKernel or None if not yet booted
        """
        return self.kernel

    def get_discoverer(self) -> Optional[Discoverer]:
        """
        Get the Discoverer agent instance.

        Returns:
            Discoverer or None if not yet created
        """
        return self.discoverer


def quick_boot(ledger_path: Optional[str] = None) -> RealVibeKernel:
    """
    Quick boot helper for simple use cases.

    Args:
        ledger_path: Optional custom ledger path

    Returns:
        RealVibeKernel: Fully initialized kernel

    Example:
        kernel = quick_boot()
        # Use kernel...
    """
    orchestrator = BootOrchestrator(ledger_path=ledger_path)
    return orchestrator.boot()
