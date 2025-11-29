"""
⚡ BOOT ORCHESTRATOR ⚡
======================

The unified boot sequence for Agent City OS.

PROBLEM SOLVED:
- Before: 3 different entry points booting empty/partial kernels
- After: ONE orchestrator ensuring consistent 23-agent boot

ARCHITECTURE:
1. Create RealVibeKernel
2. Register Discoverer (first citizen)
3. Discoverer scans for steward.json manifests (23 agents)
4. Auto-register all discovered agents
5. Boot kernel (manifests, ledger, scheduler ready)

USAGE:
    from vibe_core.boot_orchestrator import BootOrchestrator

    orchestrator = BootOrchestrator()
    kernel = orchestrator.boot()
    # kernel now has 23 agents registered
"""

import logging
from pathlib import Path
from typing import Optional

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.config import CityConfig
from steward.system_agents.discoverer.agent import Discoverer

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

    def boot(self) -> RealVibeKernel:
        """
        Execute the unified boot sequence.

        Steps:
        1. Create kernel instance
        2. Register Discoverer (Genesis Agent)
        3. Discover all agents via steward.json scan
        4. Boot kernel (initialize manifests, ledger, scheduler)

        Returns:
            RealVibeKernel: Fully initialized kernel with all agents

        Raises:
            RuntimeError: If boot sequence fails
        """
        logger.info("=" * 70)
        logger.info("⚡ BOOT ORCHESTRATOR - UNIFIED BOOT SEQUENCE")
        logger.info("=" * 70)

        # Step 1: Create Kernel
        logger.info("\n[1/4] Creating RealVibeKernel...")
        self.kernel = RealVibeKernel(ledger_path=self.ledger_path)
        logger.info(f"      ✅ Kernel created (ledger: {self.ledger_path})")

        # Step 2: Register Discoverer (Genesis Agent)
        logger.info("\n[2/4] Registering Discoverer (Genesis Agent)...")
        self.discoverer = Discoverer(kernel=self.kernel, config=self.config)

        try:
            self.kernel.register_agent(self.discoverer)
            logger.info("      ✅ Discoverer registered successfully")
        except Exception as e:
            logger.error(f"      ❌ Failed to register Discoverer: {e}")
            raise RuntimeError(f"Boot failed: Could not register Discoverer - {e}")

        # Step 3: Discover all agents
        logger.info("\n[3/4] Discovering agents via steward.json scan...")
        logger.info("      Scanning: steward/system_agents/ + agent_city/registry/")

        try:
            discovered_count = self.discoverer.discover_agents()
            logger.info(f"      ✅ Discovered and registered {discovered_count} agents")

            # Show total agent count (discoverer + discovered)
            total_agents = len(self.kernel.agent_registry)
            logger.info(f"      📊 Total agents registered: {total_agents}")

        except Exception as e:
            logger.error(f"      ❌ Discovery failed: {e}")
            raise RuntimeError(f"Boot failed: Agent discovery error - {e}")

        # Step 4: Boot kernel
        logger.info("\n[4/4] Booting kernel (manifests, ledger, scheduler)...")

        try:
            self.kernel.boot()
            logger.info("      ✅ Kernel boot complete")
        except Exception as e:
            logger.error(f"      ❌ Kernel boot failed: {e}")
            raise RuntimeError(f"Boot failed: Kernel initialization error - {e}")

        # Final status
        status = self.kernel.get_status()
        logger.info("\n" + "=" * 70)
        logger.info("✅ BOOT COMPLETE - AGENT CITY OS READY")
        logger.info("=" * 70)
        logger.info(f"📊 Agents Registered: {status.get('agents_registered', 0)}")
        logger.info(f"📜 Manifests: {status.get('manifests', 0)}")
        logger.info(f"📖 Ledger Events: {status.get('ledger_events', 0)}")
        logger.info("=" * 70 + "\n")

        return self.kernel

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
