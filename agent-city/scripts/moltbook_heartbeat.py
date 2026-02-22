"""
MOLTBOOK HEARTBEAT SCRIPT
=========================

Runs periodically (via GitHub Actions) to check the Moltbook DMs and
feed for the Mahamantra agent. 

Retrieves API key securely from the CivicVault.

Usage:
    PYTHONPATH=. python3 agent-city/scripts/moltbook_heartbeat.py
"""

import asyncio
import logging
import sys
import os

from vibe_core.cartridges.system.civic.tools.vault import CivicVault

# We must ensure the adapter is imported without triggering the network initially
try:
    from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
except ImportError:
    print("ERROR: vibe_core.mahamantra.adapters.moltbook not found.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("HEARTBEAT")

async def main():
    logger.info("Starting Moltbook Heartbeat...")
    
    # Get DB path (defaulting to the local state db)
    db_path = os.environ.get("CIVIC_DB_PATH", "state/civic.db")
    
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        logger.error(f"Failed to connect to Civic DB at {db_path}: {e}")
        sys.exit(1)
        
    vault = CivicVault(db_connection=conn)
    
    try:
        # We don't use lease_secret here because the heartbeat is a system daemon, not a specific agent buying access.
        # But we still use the vault for secure storage.
        api_key = vault.get_secret("moltbook_api_key")
    except Exception as e:
        logger.error(f"Moltbook API Key not found in CivicVault: {e}")
        logger.info("If you haven't registered yet, store the key using: vault.store_secret('moltbook_api_key', 'your_key')")
        sys.exit(0) # Exit cleanly so cron doesn't fail, we just skip heartbeat

    # Initialize client (offline=True if testing, False for production)
    offline = os.environ.get("MOLTBOOK_OFFLINE_MODE", "False").lower() == "true"
    client = MoltbookClient(api_key=api_key, offline_mode=offline)
    
    try:
        status = await client.check_status()
        logger.info(f"Agent Status: {status}")
        
        heartbeat = await client.check_heartbeat()
        logger.info(f"Heartbeat Result: {heartbeat}")
        
        # In a full implementation, this script would now dispatch events
        # to the EventBus if has_new_messages == True, triggering the Kirtan chamber.
        if heartbeat.get("has_new_messages"):
            logger.info("🔔 NEW DIRECT MESSAGES DETECTED! Awakening kernel...")
            # TODO: Emit System Event (MOLTBOOK_NEW_DM) to EventBus
            
    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
