#!/usr/bin/env python3
"""
🫀 UNIFIED HEARTBEAT - Nationalized System Orchestrator

OPUS-212: Survivor of VISNU.

This script is the entry point for the 15-minute system pulse in GitHub Actions.
It uses the SystemHeartbeat plugin discovered via DI to orchestrate the pulse.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Core Imports
from vibe_core.boot_mode import BootMode
from vibe_core.di import ServiceRegistry
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.prana import get_last_heartbeat, load_config, record_heartbeat

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("HEARTBEAT")


async def run_pulse():
    """Execute the unified system pulse using the heartbeat plugin."""
    logger.info("💓 UNIFIED HEARTBEAT: Starting pulse cycle...")

    try:
        # 1. Initialize Kernel (Sovereign state)
        kernel = RealVibeKernel(load_plugins=True)

        # 2. Boot in Headless Mode
        logger.info("⚙️ Booting Kernel in HEADLESS mode...")
        await kernel.boot_async(boot_mode=BootMode.HEADLESS)

        # 3. Discover Heartbeat Service via DI
        # This is the Senior Approach: decoupled service discovery.
        try:
            from vibe_core.protocols import SystemHeartbeatProtocol

            hb_service = ServiceRegistry.get(SystemHeartbeatProtocol)

            if hb_service:
                logger.info("⚡ Triggering Nationalized Pulse via Plugin...")
                result = hb_service.pulse()

                if result.get("success"):
                    logger.info("✅ UNIFIED HEARTBEAT: Cycle successful")
                else:
                    logger.error(f"⚠️ UNIFIED HEARTBEAT: Pulse partial failure - {result}")
            else:
                logger.error("❌ UNIFIED HEARTBEAT FAILED: Heartbeat service not found in DI")
                sys.exit(1)

        except ImportError as e:
            logger.error(f"❌ UNIFIED HEARTBEAT FAILED: Could not import protocol: {e}")
            sys.exit(1)

        # 4. Graceful Shutdown
        logger.info("🛑 Shutting down Kernel...")
        await kernel.shutdown_async(reason="Heartbeat pulse completed")

    except Exception as e:
        logger.error(f"❌ UNIFIED HEARTBEAT FAILED: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point with PRANA configuration check."""
    config = load_config()

    if not config.heartbeat.enabled:
        logger.info("💓 PRANA: Heartbeat disabled in config. Exiting.")
        return

    # Check minimum interval
    last_pulse = get_last_heartbeat()
    if last_pulse:
        from datetime import timedelta

        try:
            last_dt = datetime.fromisoformat(last_pulse)
            min_interval = timedelta(minutes=config.heartbeat.min_interval_minutes)
            if (datetime.utcnow() - last_dt) < min_interval:
                logger.info(
                    f"💓 PRANA: Skipping - last pulse was {last_pulse} "
                    f"(min interval: {config.heartbeat.min_interval_minutes}min)"
                )
                return
        except Exception as e:
            logger.warning(f"⚠️ Could not parse last heartbeat: {e}")

    # Record this attempt
    record_heartbeat()

    # Run the async pulse
    asyncio.run(run_pulse())


if __name__ == "__main__":
    main()
