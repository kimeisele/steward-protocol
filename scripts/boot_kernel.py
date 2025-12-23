#!/usr/bin/env python3
"""
🚀 VIBE KERNEL BOOT LOADER 🚀
==============================

The OFFICIAL entry point for booting the VibeOS Kernel in production mode.

Usage:
    python scripts/boot_kernel.py

Architecture:
1. Zombie Cleanup (kill stale processes)
2. Loads Context & Configuration
3. Boots Kernel (RealVibeKernel)
4. Initializes InterfacePlugin (UI)
5. Enters ACTIVE Tick Loop (drives heartbeat)
"""

import logging
import os
import signal
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# PID file location
PID_FILE = Path("/tmp/vibe_os/kernel/boot.pid")

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("BOOT_LOADER")

# Global kernel reference for signal handler
_kernel = None


async def async_signal_handler():
    """Graceful shutdown for async context."""
    logger.info("\n🛑 Received shutdown signal. Shutting down async...")
    if _kernel:
        try:
            await _kernel.shutdown_async()
        except Exception as e:
            logger.warning(f"Shutdown error: {e}")
    # Cleanup PID file
    if PID_FILE.exists():
        PID_FILE.unlink()
    sys.exit(0)


def cleanup_zombie_processes():
    """
    Zombie Cleanup: Kill any stale kernel process before starting.

    If PID file exists:
      - If process is running: kill it
      - If process is dead: delete stale PID file
    """
    if not PID_FILE.exists():
        return

    try:
        old_pid = int(PID_FILE.read_text().strip())

        # Check if process is running
        try:
            os.kill(old_pid, 0)  # Signal 0 = check if exists
            # Process exists - kill it
            logger.warning(f"⚠️  Killing stale kernel process (PID: {old_pid})")
            os.kill(old_pid, signal.SIGTERM)
            time.sleep(1)
            # Force kill if still running
            try:
                os.kill(old_pid, 0)
                os.kill(old_pid, signal.SIGKILL)
                logger.info(f"   Force-killed PID {old_pid}")
            except ProcessLookupError:
                pass  # Process terminated
        except ProcessLookupError:
            # Process not running - stale PID file
            logger.info(f"🧹 Cleaning stale PID file (PID {old_pid} not running)")

        PID_FILE.unlink()

    except (ValueError, FileNotFoundError) as e:
        logger.warning(f"⚠️  Error reading PID file: {e}")
        if PID_FILE.exists():
            PID_FILE.unlink()


def write_pid_file():
    """Write current process PID to file."""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))
    logger.info(f"📝 PID file written: {PID_FILE} (PID: {os.getpid()})")


async def main():
    global _kernel

    logger.info("=" * 70)
    logger.info("🔌 VIBE KERNEL BOOT SEQUENCE INITIATED (ASYNC)")
    logger.info("=" * 70)

    # Register signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(async_signal_handler()))

    try:
        # Phase 0: Zombie Cleanup
        logger.info("Phase 0: Zombie Cleanup...")
        cleanup_zombie_processes()
        write_pid_file()

        # Phase 1: Import after cleanup
        logger.info("Phase 1: Loading Kernel...")
        from vibe_core.kernel_impl import RealVibeKernel

        # Phase 2: Instantiate Kernel
        logger.info("Phase 2: Instantiating Kernel...")
        kernel = RealVibeKernel(ledger_path=PROJECT_ROOT / "data" / "vibe_ledger.db")
        _kernel = kernel

        # Phase 3: Async Boot
        logger.info("Phase 3: Booting Kernel Async...")
        await kernel.boot_async()

        # Force re-generation of OPUS.md
        for plugin in kernel._plugins:
            if getattr(plugin, "plugin_id", "") == "interface":
                plugin.render_all()

        # Phase 4: UNIFIED ASYNC LOOP
        logger.info("Phase 4: Entering Unified Async Loop...")
        logger.info("✅ System Online. Heartbeat active.")

        await kernel.run_forever()

    except Exception as e:
        logger.critical(f"❌ FATAL BOOT ERROR: {e}")
        import traceback

        traceback.print_exc()
        if PID_FILE.exists():
            PID_FILE.unlink()
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
