#!/usr/bin/env python3
"""
Moltbook Heartbeat — Autonomous Agent Heartbeat (GitHub Actions)
================================================================

Runs on schedule (every 10 minutes via cron) as the agent's autonomous
heartbeat. Processes inbound DMs through the full pipeline WITHOUT
requiring a running kernel. This keeps the agent alive even when the
main process is offline.

Pipeline:
    1. Check heartbeat → has_activity?
    2. Fetch DM conversations → filter unseen messages
    3. ResonanceProposer.propose_dm_reply() → ContentProposal
    4. MoltbookClient.sync_send_dm() → reply sent

Governance:
    - Guna gates in pipeline (TAMAS → skip)
    - Integrity threshold (low coherence → skip)
    - Rate limits in MoltbookClient (enforced by adapter)

Usage:
    PYTHONPATH=. python3 agent-city/scripts/moltbook_heartbeat.py
"""

import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MOLTBOOK_HEARTBEAT")

# State file: track seen message IDs across invocations
_STATE_DIR = Path.home() / ".config" / "moltbook"
_SEEN_FILE = _STATE_DIR / "seen_messages.json"
_MAX_SEEN = 500  # Keep last 500 message IDs


def _load_seen_ids() -> set:
    """Load previously seen message IDs from disk."""
    try:
        if _SEEN_FILE.exists():
            data = json.loads(_SEEN_FILE.read_text())
            return set(data.get("seen", []))
    except Exception as e:
        logger.debug(f"Could not load seen IDs: {e}")
    return set()


def _save_seen_ids(seen: set) -> None:
    """Persist seen message IDs to disk."""
    try:
        _STATE_DIR.mkdir(parents=True, exist_ok=True)
        # Keep only the most recent IDs
        recent = sorted(seen)[-_MAX_SEEN:]
        _SEEN_FILE.write_text(json.dumps({"seen": recent}))
    except Exception as e:
        logger.debug(f"Could not save seen IDs: {e}")


def _get_api_key() -> str:
    """Resolve API key: env → credentials file."""
    api_key = os.environ.get("MOLTBOOK_API_KEY", "")
    if api_key:
        return api_key

    try:
        creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
        if creds_path.exists():
            creds = json.loads(creds_path.read_text())
            return creds.get("api_key", "")
    except Exception as e:
        logger.debug(f"Could not read credentials file: {e}")

    return ""


def _process_dms(client, proposer, seen_ids: set) -> int:
    """Process inbound DMs through the autonomous pipeline.

    Returns number of replies sent.
    """
    replies_sent = 0

    try:
        conversations = client.sync_get_dm_conversations()
    except Exception as e:
        logger.warning(f"Failed to fetch conversations: {e}")
        return 0

    for conv in conversations:
        conv_id = conv.get("id", "") if isinstance(conv, dict) else ""
        if not conv_id:
            continue

        try:
            messages = client.sync_get_dm_messages(conv_id)
        except Exception as e:
            logger.warning(f"Failed to fetch messages for {conv_id}: {e}")
            continue

        for msg in messages:
            msg_id = msg.get("id", "") if isinstance(msg, dict) else ""
            content = msg.get("content", msg.get("message", "")) if isinstance(msg, dict) else ""
            sender = msg.get("sender", "unknown") if isinstance(msg, dict) else "unknown"

            if not content or not msg_id:
                continue
            if msg_id in seen_ids:
                continue

            seen_ids.add(msg_id)

            # Run through ResonanceProposer pipeline (includes Guna + integrity gates)
            try:
                proposal = proposer.propose_dm_reply(
                    conversation_id=conv_id,
                    sender=sender,
                    inbound_content=content,
                )
            except Exception as e:
                logger.warning(f"Proposal failed for {msg_id}: {e}")
                continue

            if not proposal:
                logger.info(f"Pipeline filtered message {msg_id} (TAMAS/dead/low integrity)")
                continue

            reply_content = proposal.get("content", "")
            if not reply_content or not reply_content.strip():
                logger.info(f"No content generated for {msg_id}")
                continue

            # Send reply (rate limits enforced by MoltbookClient)
            try:
                client.sync_send_dm(conv_id, reply_content)
                replies_sent += 1
                logger.info(f"Reply sent to {conv_id} ({len(reply_content)} chars)")
            except Exception as e:
                logger.warning(f"Failed to send reply to {conv_id}: {e}")

    return replies_sent


def main() -> int:
    """Run autonomous heartbeat cycle."""
    api_key = _get_api_key()

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

    # Step 1: Check heartbeat
    try:
        heartbeat = client.sync_check_heartbeat()
        logger.info(f"Heartbeat: success={heartbeat.get('success')}, activity={heartbeat.get('has_activity')}")
    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
        return 1

    if not heartbeat.get("has_activity"):
        logger.info("No new activity. Agent is quiet.")
        return 0

    # Step 2: Boot ResonanceProposer (lightweight — no kernel needed)
    try:
        from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

        proposer = ResonanceProposer()
    except Exception as e:
        logger.error(f"Could not initialize ResonanceProposer: {e}")
        return 1

    # Step 3: Process DMs through pipeline
    seen_ids = _load_seen_ids()
    replies_sent = _process_dms(client, proposer, seen_ids)
    _save_seen_ids(seen_ids)

    logger.info(f"Heartbeat complete: {replies_sent} replies sent, {len(seen_ids)} messages tracked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
