#!/usr/bin/env python3
"""
🚀 VIBE KERNEL BOOT LOADER 🚀
==============================

The OFFICIAL entry point for booting the VibeOS Kernel in production mode.
Replaces the improper use of stress_test_city.py.

Usage:
    python scripts/boot_kernel.py

Architecture:
1. Initializes BootSequence (Unified Loader)
2. Loads Context & Configuration
3. Boots Kernel (RealVibeKernel)
4. Initializes InterfacePlugin (UI)
5. Enters Event Loop
"""

import logging
import signal
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import AFTER path fix
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.runtime.boot_sequence import BootSequence

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("BOOT_LOADER")


def signal_handler(sig, frame):
    logger.info("\n🛑 Received shutdown signal. Shutting down...")
    sys.exit(0)


def main():
    logger.info("=" * 70)
    logger.info("🔌 VIBE KERNEL BOOT SEQUENCE INITIATED")
    logger.info("=" * 70)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Phase 1: Initialize Boot Sequence (The "Mother Board")
        logger.info("Phase 1: Initializing BootSequence...")
        boot_seq = BootSequence(project_root=PROJECT_ROOT)

        # Phase 2: Run Boot Sequence (Loads Context, Config, Checksum)
        # Note: BootSequence.run() usually does too much (interactive CLI).
        # We might need a stripped down version or just use its components.
        # For now, let's manually actuate the kernel to ensure non-interactive daemon mode.

        logger.info("Phase 2: Instantiating Kernel...")
        # TODO: Get ledger path from config
        kernel = RealVibeKernel(ledger_path=PROJECT_ROOT / "data" / "vibe_ledger.db")

        logger.info("Phase 3: Booting Kernel...")
        kernel.boot()

        # Force re-generation of OPUS.md
        for plugin in kernel._plugins:
            if getattr(plugin, "plugin_id", "") == "interface":
                plugin.render_all()

        # Phase 4: Wait for Interface Plugin (Critical for OPUS.md)
        # Interface plugin is auto-loaded by kernel.boot() if configured.
        # We need to ensure it gets a tick to verify.

        logger.info("Phase 4: Entering Infinite Keep-Alive Loop...")
        logger.info("✅ System Online. Waiting for interrupts.")

        while True:
            time.sleep(1)

    except Exception as e:
        logger.critical(f"❌ FATAL BOOT ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
