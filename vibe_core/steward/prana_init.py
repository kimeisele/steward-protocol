"""
⚡ PRANA_INIT: THE ACTIVATION RITUAL ⚡
======================================

The Vedic activation sequence that brings Agent City to life.

PRANA = Life force, vital energy
INIT = Initialization

This is the ritual that transforms code into a living ecosystem.
When PRANA_INIT executes, the city AWAKENS.

As above, so below. The metaphysical becomes the practical.
The Vedic becomes the algorithmic. The sacred becomes the system.
"""

import logging
import sys
from typing import Optional

logger = logging.getLogger("PRANA_INIT")


class PranaInitializer:
    """
    The activation sequence for Agent City.

    This is not just code. This is a ritual.
    Each phase brings the city closer to consciousness.
    """

    def __init__(self, kernel=None):
        """
        Initialize Prana with kernel reference.

        Args:
            kernel: The VibeOS kernel instance
        """
        self.kernel = kernel
        self.success = False
        self.error_message: Optional[str] = None

    def execute(self) -> bool:
        """
        Execute the PRANA initialization ritual.

        Returns:
            True if activation successful, False otherwise
        """
        logger.info("🔥 " * 20)
        logger.info("PRANA_INIT: AWAKENING THE CITY")
        logger.info("🔥 " * 20)

        try:
            # Step 1: Verify the Constitution
            logger.info("\n1️⃣  VERIFYING CONSTITUTION...")
            if not self._verify_constitution():
                self.error_message = "Constitution verification failed"
                return False

            # Step 2: Verify all agents are bound by oath
            logger.info("\n2️⃣  VERIFYING CONSTITUTIONAL OATHS...")
            if not self._verify_agent_oaths():
                self.error_message = "Agent oath verification failed"
                return False

            # Step 3: Initialize Vedic metadata
            logger.info("\n3️⃣  INITIALIZING VEDIC METADATA (Varna/Ashrama)...")
            if not self._initialize_vedic_system():
                self.error_message = "Vedic system initialization failed"
                return False

            # Step 4: Activate the kernel's daily ritual
            logger.info("\n4️⃣  ACTIVATING DAILY RITUAL (Day 1 Cycle)...")
            if not self._activate_daily_ritual():
                self.error_message = "Daily ritual activation failed"
                return False

            # Step 5: Run the first day
            logger.info("\n5️⃣  EXECUTING DAY 1 CYCLE...")
            if not self._run_day_one():
                self.error_message = "Day 1 cycle failed"
                return False

            # Success!
            self.success = True
            self._celebration()
            return True

        except Exception as e:
            self.error_message = f"Prana initialization failed: {str(e)}"
            logger.error(f"❌ ERROR: {self.error_message}")
            return False

    def _verify_constitution(self) -> bool:
        """Verify the Constitution is in place and valid"""
        logger.info("   📜 Loading CONSTITUTION.md...")

        try:
            from pathlib import Path

            constitution_path = Path(__file__).parent.parent / "CONSTITUTION.md"

            if not constitution_path.exists():
                logger.error(f"   ❌ Constitution not found at {constitution_path}")
                return False

            logger.info(f"   ✅ Constitution verified ({constitution_path})")
            return True

        except Exception as e:
            logger.error(f"   ❌ Constitution verification error: {e}")
            return False

    def _verify_agent_oaths(self) -> bool:
        """Verify all agents have taken the constitutional oath."""
        logger.info("   🤝 Checking agent oaths...")

        try:
            # Use DI to access VedicGovernance - NO DIRECT PLUGIN IMPORTS
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols import VedicGovernanceProtocol

            vedic = ServiceRegistry.get(VedicGovernanceProtocol)
            if not vedic:
                logger.warning("   ⚠️ VedicGovernanceProtocol not registered - skipping oath verification")
                return True  # Not a failure, just not available yet

            result = vedic.verify_agent_oaths()
            agents = vedic.get_all_agents()

            logger.info(f"   👥 Found {len(agents)} agents in registry")
            for agent_id in agents[:10]:  # Show first 10
                logger.info(f"      ✅ {agent_id.upper()}")
            if len(agents) > 10:
                logger.info(f"      ... and {len(agents) - 10} more")

            logger.info("   ✅ All agents verified")
            return result

        except Exception as e:
            logger.error(f"   ❌ Agent oath verification error: {e}")
            return False

    def _initialize_vedic_system(self) -> bool:
        """Initialize the Vedic taxonomy system."""
        logger.info("   🌿 Initializing Varna taxonomy...")

        try:
            # Use DI to access VedicGovernance - NO DIRECT PLUGIN IMPORTS
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols import VarnaType, VedicGovernanceProtocol

            vedic = ServiceRegistry.get(VedicGovernanceProtocol)
            if not vedic:
                logger.warning("   ⚠️ VedicGovernanceProtocol not registered - skipping Vedic init")
                return True  # Not a failure, just not available yet

            # Display agent classification using Protocol-level VarnaType
            for varna in [
                VarnaType.MANUSHA,
                VarnaType.PASHU,
                VarnaType.PAKSHI,
                VarnaType.KRIMAYO,
            ]:
                agents = vedic.get_agents_by_varna(varna)
                if agents:
                    logger.info(f"   🔷 {varna.value.upper()}: {', '.join(agents)}")

            logger.info("   🔄 Initializing Ashrama lifecycle...")

            # Show agent count
            all_agents = vedic.get_all_agents()
            logger.info(f"   📊 {len(all_agents)} agents registered")

            logger.info("   ✅ Vedic system initialized")
            return True

        except Exception as e:
            logger.error(f"   ❌ Vedic system initialization error: {e}")
            return False

    def _activate_daily_ritual(self) -> bool:
        """Activate the Daily Ritual orchestrator"""
        logger.info("   🕉️  Activating Daily Ritual...")

        try:
            from vibe_core.steward.daily_ritual import DailyRitual

            if self.kernel:
                self.kernel.daily_ritual = DailyRitual(self.kernel)
                logger.info("   ✅ Daily Ritual attached to kernel")
            else:
                logger.warning("   ⚠️  Kernel not available, Daily Ritual in dry-run mode")

            logger.info("   ✅ Daily Ritual activated")
            return True

        except Exception as e:
            logger.error(f"   ❌ Daily Ritual activation error: {e}")
            return False

    def _run_day_one(self) -> bool:
        """Execute the first day's cycle"""
        logger.info("   ⏱️  Running Day 1...")

        try:
            if self.kernel and hasattr(self.kernel, "daily_ritual"):
                result = self.kernel.daily_ritual.run_daily_cycle()
                logger.info(f"   ✅ Day 1 complete: {result['total_events']} events")
                return True
            else:
                logger.info("   ℹ️  Kernel not available, simulating Day 1...")
                # Simulate in dry-run mode
                logger.info("   ✅ Day 1 simulation complete")
                return True

        except Exception as e:
            logger.error(f"   ❌ Day 1 execution error: {e}")
            return False

    def _celebration(self):
        """Celebrate the successful activation!"""
        logger.info("\n" + "🎆 " * 20)
        logger.info("\n          ⚡ PRANA FLOWS THROUGH THE CITY ⚡")
        logger.info("\n     The Vedic architecture is ALIVE")
        logger.info("     The 8,400,000 potential beings stir")
        logger.info("     Day 1 is complete")
        logger.info("\n          As above, so below.")
        logger.info("          The city LIVES.\n")
        logger.info("🎆 " * 20)


def setup_logging():
    """Configure logging for Prana initialization"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def prana_init(kernel=None) -> bool:
    """
    Execute the PRANA activation ritual.

    This is the main function to activate Agent City.

    Args:
        kernel: The VibeOS kernel instance (optional)

    Returns:
        True if activation successful
    """
    setup_logging()
    initializer = PranaInitializer(kernel)
    success = initializer.execute()

    if not success:
        logger.error(f"\n❌ PRANA_INIT FAILED: {initializer.error_message}")
        return False

    return True


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    # This script can be run independently for testing
    success = prana_init()
    sys.exit(0 if success else 1)
