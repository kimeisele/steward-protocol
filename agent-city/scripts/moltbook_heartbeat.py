#!/usr/bin/env python3
"""
Moltbook Heartbeat — GitHub Actions Entry Point

Called by .github/workflows/scheduled-agents.yml (Ring-0 protected).
Boots the kernel in headless mode, triggers MoltbookPlugin.on_pulse().

This script exists because scheduled-agents.yml references this exact path.
The YAML is Ring-0 (SHA256-locked in governance/keys.py) — cannot be changed.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("MOLTBOOK-HEARTBEAT")


async def run_moltbook_heartbeat():
    """Boot kernel, find moltbook plugin, trigger heartbeat."""
    from vibe_core.boot_mode import BootMode
    from vibe_core.kernel_impl import RealVibeKernel

    offline_mode = os.environ.get("MOLTBOOK_OFFLINE_MODE", "False").lower() == "true"
    logger.info(f"Moltbook heartbeat starting (offline={offline_mode})")

    kernel = RealVibeKernel(load_plugins=True)
    await kernel.boot_async(boot_mode=BootMode.HEADLESS)

    # Get moltbook plugin API
    moltbook_api = kernel.api("moltbook")
    if not moltbook_api:
        logger.error("Moltbook plugin not loaded — check manifest.json and dependencies")
        await kernel.shutdown_async(reason="Moltbook plugin missing")
        sys.exit(1)

    client = moltbook_api.get("client")
    if not client:
        logger.error("Moltbook client not initialized")
        await kernel.shutdown_async(reason="Moltbook client missing")
        sys.exit(1)

    # Run heartbeat check
    try:
        result = client.sync_check_heartbeat()
        has_new = result.get("has_new_messages", False)
        pending = result.get("pending_requests", 0)
        logger.info(f"Heartbeat OK — new_messages={has_new}, pending={pending}")
    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
        # Don't exit — let shutdown happen cleanly

    await kernel.shutdown_async(reason="Moltbook heartbeat complete")
    logger.info("Moltbook heartbeat finished")


def main():
    asyncio.run(run_moltbook_heartbeat())


if __name__ == "__main__":
    main()
