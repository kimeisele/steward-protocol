#!/usr/bin/env python3
"""
Moltbook Heartbeat — GitHub Actions Entry Point
================================================

Runs on schedule to check for new DMs/mentions on Moltbook.
Uses the MoltbookClient directly (no kernel boot required).

Usage:
    PYTHONPATH=. python3 agent-city/scripts/moltbook_heartbeat.py
"""

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MOLTBOOK_HEARTBEAT")


def main() -> int:
    """Run heartbeat check."""
    # Get API key from environment or credentials file
    api_key = os.environ.get("MOLTBOOK_API_KEY", "")

    if not api_key:
        # Try credentials file
        try:
            import json
            from pathlib import Path

            creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
            if creds_path.exists():
                creds = json.loads(creds_path.read_text())
                api_key = creds.get("api_key", "")
        except Exception as e:
            logger.debug(f"Could not read credentials file: {e}")

    if not api_key:
        logger.warning("No MOLTBOOK_API_KEY found. Skipping heartbeat.")
        return 0  # Exit cleanly so CI doesn't fail

    offline_mode = os.environ.get("MOLTBOOK_OFFLINE_MODE", "False").lower() == "true"

    try:
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
    except ImportError as e:
        logger.error(f"Could not import MoltbookClient: {e}")
        return 1

    client = MoltbookClient(api_key=api_key, offline_mode=offline_mode)

    try:
        heartbeat = client.sync_check_heartbeat()
        logger.info(f"Heartbeat: {heartbeat}")

        if heartbeat.get("has_new_messages"):
            logger.info("New messages detected!")
            # In a full implementation, this would route through Govardhan Gateway
            # For now, just log the event
            # TODO: Wire to kernel.dispatch() or emit event

        return 0

    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
