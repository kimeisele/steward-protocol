#!/usr/bin/env python3
"""
Moltbook Agent — Full MURALI Heartbeat Runner
==============================================

Boots the MoltbookPlugin with full pipeline:
    GENESIS  → scan feed, discover submolts
    DHARMA   → evaluate strategy, plan intents
    KARMA    → generate content via AgencyDirector
    MOKSHA   → track engagement, learn from patterns

Works in GitHub Actions (env secrets) and locally (~/.config/moltbook/credentials.json).
Kernel optional — all subsystems degrade gracefully.

Usage:
    PYTHONPATH=. python3 agent-city/scripts/moltbook_heartbeat.py
    PYTHONPATH=. python3 agent-city/scripts/moltbook_heartbeat.py --cycles 8
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MOLTBOOK_AGENT")

# Default: 4 heartbeats = one full MURALI rotation (research → planning → execution → learning)
DEFAULT_CYCLES = 4


class MinimalKernel:
    """Stub kernel for standalone operation. Plugin degrades gracefully."""

    def api(self, name):
        return None

    def get_agent(self, name):
        return None


def _get_kernel():
    """Get StandaloneKernel (full VibeKernel interface) or fallback to MinimalKernel."""
    try:
        from vibe_core.standalone_kernel import get_standalone_kernel

        return get_standalone_kernel()
    except Exception as e:
        logger.warning(f"StandaloneKernel unavailable, using MinimalKernel: {e}")
        return MinimalKernel()


def _resolve_api_key() -> str:
    """Resolve API key: env → credentials file."""
    api_key = os.environ.get("MOLTBOOK_API_KEY", "")
    if api_key:
        logger.info("API key from environment")
        return api_key

    try:
        creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
        if creds_path.exists():
            creds = json.loads(creds_path.read_text())
            api_key = creds.get("api_key", "")
            if api_key:
                logger.info("API key from ~/.config/moltbook/credentials.json")
                return api_key
    except Exception as e:
        logger.debug(f"Credentials file read failed: {e}")

    return ""


def main() -> int:
    """Boot MoltbookPlugin and run MURALI heartbeat cycles."""
    parser = argparse.ArgumentParser(description="Moltbook Agent — Full MURALI Runner")
    parser.add_argument("--cycles", type=int, default=DEFAULT_CYCLES, help="Number of heartbeat cycles")
    parser.add_argument("--offline", action="store_true", help="Force offline mode (no API writes)")
    args = parser.parse_args()

    api_key = _resolve_api_key()
    if not api_key:
        logger.warning("No MOLTBOOK_API_KEY found. Skipping.")
        return 0

    offline_env = os.environ.get("MOLTBOOK_OFFLINE_MODE", "False").lower() == "true"
    offline = args.offline or offline_env

    mode = "OFFLINE" if offline else "LIVE"
    logger.info(f"Moltbook Agent starting [{mode}] — {args.cycles} cycles")

    try:
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin
    except ImportError as e:
        logger.error(f"Could not import MoltbookPlugin: {e}")
        return 1

    plugin = MoltbookPlugin()
    kernel = _get_kernel()

    # Boot with config
    config = {
        "api_key": api_key,
        "offline_mode": offline,
    }

    try:
        result = plugin.on_boot(kernel, config=config)
        # HookResult.status is PluginResult enum — check .value for string comparison
        status_val = getattr(getattr(result, "status", None), "value", str(result)) if result else "error"
        if status_val not in ("ok", "success"):
            logger.error(f"Boot failed: {result}")
            return 1
    except Exception as e:
        logger.error(f"Boot exception: {e}")
        return 1

    logger.info(f"Plugin booted. Running {args.cycles} heartbeat cycles...")

    # Run MURALI cycles
    t0 = time.time()
    for i in range(args.cycles):
        try:
            # Advance VenuOrchestrator — drives MURALI phase rotation
            try:
                from vibe_core.mahamantra import mahamantra

                mahamantra.venu.step()
            except Exception as e:
                logger.warning(f"VenuOrchestrator step failed: {e}")

            plugin.on_pulse(kernel, None)
            logger.info(f"Heartbeat {i + 1}/{args.cycles} complete")
        except Exception as e:
            logger.error(f"Heartbeat {i + 1} failed: {e}")

        # Brief pause between cycles (avoid rate limiting)
        if i < args.cycles - 1:
            time.sleep(2)

    elapsed = time.time() - t0
    logger.info(f"Agent run complete: {args.cycles} cycles in {elapsed:.1f}s")

    # Shutdown: persist state
    try:
        plugin.on_shutdown(kernel)
        logger.info("Shutdown complete — state persisted")
    except Exception as e:
        logger.warning(f"Shutdown error: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
