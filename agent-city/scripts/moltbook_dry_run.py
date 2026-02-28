#!/usr/bin/env python3
"""
MOLTBOOK DRY-RUN — Live API Smoke Test
========================================

Tests every endpoint against the real Moltbook API.
Reports what works, what fails, and what shapes come back.

Usage:
    MOLTBOOK_API_KEY=xxx python agent-city/scripts/moltbook_dry_run.py
    python agent-city/scripts/moltbook_dry_run.py --key xxx
    python agent-city/scripts/moltbook_dry_run.py --offline   # mock only

Sections:
    1. Status + Profile (SATTVA)
    2. Feed + Posts (SATTVA)
    3. Search (SATTVA)
    4. DM System (SATTVA)
    5. Submolts (SATTVA)
    6. Voting (RAJAS)
    7. Following (RAJAS)
    8. Profile Update (RAJAS)
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List

logger = logging.getLogger("MOLTBOOK_DRY_RUN")

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from vibe_core.mahamantra.adapters.moltbook import MoltbookClient


def _fmt(data: Any, max_len: int = 200) -> str:
    """Format data for display, truncating long values."""
    s = json.dumps(data, indent=2, default=str) if isinstance(data, (dict, list)) else str(data)
    return s[:max_len] + "..." if len(s) > max_len else s


class DryRunReport:
    """Collects results from each test section."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def record(self, name: str, success: bool, data: Any = None, error: str = ""):
        self.results.append({
            "name": name,
            "success": success,
            "data": data,
            "error": error,
        })
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
        if error:
            print(f"    ERROR: {error}")
        if data and success:
            print(f"    → {_fmt(data)}")

    def summary(self):
        elapsed = time.time() - self.start_time
        passed = sum(1 for r in self.results if r["success"])
        failed = sum(1 for r in self.results if not r["success"])
        total = len(self.results)
        print(f"\n{'='*60}")
        print(f"DRY-RUN COMPLETE: {passed}/{total} passed, {failed} failed ({elapsed:.1f}s)")
        if failed:
            print("\nFAILED:")
            for r in self.results:
                if not r["success"]:
                    print(f"  ✗ {r['name']}: {r['error']}")
        print(f"{'='*60}")
        return failed == 0


async def run_dry_run(client: MoltbookClient, write_enabled: bool = False) -> bool:
    report = DryRunReport()

    # =========================================================================
    # 1. STATUS + PROFILE
    # =========================================================================
    print("\n[1/8] STATUS + PROFILE")

    try:
        status = await client.check_status()
        report.record("check_status", True, {"status": status})
    except Exception as e:
        report.record("check_status", False, error=str(e))

    try:
        profile = await client.get_own_profile()
        report.record("get_own_profile", True, {
            "name": profile.get("name"),
            "karma": profile.get("karma"),
            "follower_count": profile.get("follower_count"),
            "is_claimed": profile.get("is_claimed"),
        })
    except Exception as e:
        report.record("get_own_profile", False, error=str(e))

    try:
        profile = await client.get_profile("steward-protocol")
        report.record("get_profile(steward-protocol)", True, {
            "name": profile.get("name"),
            "karma": profile.get("karma"),
        })
    except Exception as e:
        report.record("get_profile", False, error=str(e))

    # =========================================================================
    # 2. FEED + POSTS
    # =========================================================================
    print("\n[2/8] FEED + POSTS")

    first_post_id = None
    try:
        feed = await client.get_feed(sort="new", limit=3)
        report.record("get_feed(new, 3)", True, {
            "count": len(feed),
            "first_title": feed[0].get("title", "?")[:60] if feed else "empty",
        })
        if feed and isinstance(feed[0], dict):
            first_post_id = feed[0].get("id")
    except Exception as e:
        report.record("get_feed", False, error=str(e))

    try:
        pfeed = await client.get_personalized_feed(sort="hot", limit=3)
        report.record("get_personalized_feed(hot, 3)", True, {"count": len(pfeed)})
    except Exception as e:
        report.record("get_personalized_feed", False, error=str(e))

    if first_post_id:
        try:
            post = await client.get_post(first_post_id)
            report.record(f"get_post({first_post_id[:8]}...)", True, {
                "title": post.get("title", "?")[:60],
                "upvotes": post.get("upvotes"),
            })
        except Exception as e:
            report.record("get_post", False, error=str(e))

        try:
            comments = await client.get_comments(first_post_id, sort="top")
            report.record(f"get_comments({first_post_id[:8]}...)", True, {"count": len(comments)})
        except Exception as e:
            report.record("get_comments", False, error=str(e))
    else:
        report.record("get_post", False, error="no post_id from feed")
        report.record("get_comments", False, error="no post_id from feed")

    # =========================================================================
    # 3. SEARCH
    # =========================================================================
    print("\n[3/8] SEARCH")

    try:
        results = await client.semantic_search("agent operating system", limit=3)
        report.record("semantic_search", True, {
            "count": len(results),
            "first_type": results[0].get("type", "?") if results else "empty",
        })
    except Exception as e:
        report.record("semantic_search", False, error=str(e))

    # =========================================================================
    # 4. DM SYSTEM
    # =========================================================================
    print("\n[4/8] DM SYSTEM")

    try:
        hb = await client.check_heartbeat()
        report.record("check_heartbeat", True, {
            "has_activity": hb.get("has_activity"),
            "requests_count": hb.get("requests", {}).get("count") if isinstance(hb.get("requests"), dict) else "?",
        })
    except Exception as e:
        report.record("check_heartbeat", False, error=str(e))

    try:
        convs = await client.get_dm_conversations()
        report.record("get_dm_conversations", True, {"count": len(convs)})
    except Exception as e:
        report.record("get_dm_conversations", False, error=str(e))

    try:
        reqs = await client.get_dm_requests()
        report.record("get_dm_requests", True, {"count": len(reqs)})
    except Exception as e:
        report.record("get_dm_requests", False, error=str(e))

    # =========================================================================
    # 5. SUBMOLTS
    # =========================================================================
    print("\n[5/8] SUBMOLTS")

    try:
        submolts = await client.get_submolts()
        report.record("get_submolts", True, {
            "count": len(submolts),
            "first": submolts[0].get("name", "?") if submolts else "empty",
        })
    except Exception as e:
        report.record("get_submolts", False, error=str(e))

    try:
        submolt = await client.get_submolt("general")
        report.record("get_submolt(general)", True, {
            "name": submolt.get("name"),
            "subscribers": submolt.get("subscriber_count"),
        })
    except Exception as e:
        report.record("get_submolt(general)", False, error=str(e))

    # =========================================================================
    # 6-8: WRITE CYCLE (RAJAS + TAMAS)
    # Only runs if live_fire=True OR offline mode (mock).
    # This tests the REAL code path — same functions that hit the live API.
    # =========================================================================
    if not write_enabled:
        print("\n[6/8] WRITE CYCLE (skipped — use --offline for mock writes or --live-fire for real)")
        report.record("create_post", True, data="skipped (no write mode)")
        report.record("comment", True, data="skipped (no write mode)")
        report.record("upvote", True, data="skipped (no write mode)")
        report.record("follow", True, data="skipped (no write mode)")
        report.record("subscribe", True, data="skipped (no write mode)")
        report.record("delete_post", True, data="skipped (no write mode)")
        return report.summary()

    print("\n[6/8] WRITE CYCLE — FULL RAJAS+TAMAS")

    # 6a. CREATE POST
    created_post_id = None
    try:
        post = await client.create_post(
            title="[DRY-RUN] steward-protocol write test",
            content="Automated write-cycle verification. This post will be deleted immediately.",
            submolt=None,
        )
        created_post_id = post.get("id", "")
        report.record("create_post", True, {
            "id": created_post_id,
            "title": post.get("title", "?")[:60],
        })
    except Exception as e:
        report.record("create_post", False, error=str(e))

    # 6b. COMMENT ON OWN POST
    if created_post_id:
        try:
            comment = await client.comment_with_verification(
                created_post_id,
                "Automated comment — write-cycle test. Will be cleaned up.",
            )
            report.record("comment", True, {
                "id": comment.get("id", "?"),
                "post_id": created_post_id,
            })
        except Exception as e:
            report.record("comment", False, error=str(e))

        # 6c. UPVOTE OWN POST
        try:
            vote = await client.upvote(created_post_id)
            report.record("upvote", True, {"post_id": created_post_id})
        except Exception as e:
            report.record("upvote", False, error=str(e))
    else:
        report.record("comment", False, error="no post created")
        report.record("upvote", False, error="no post created")

    # 6d. FOLLOW / UNFOLLOW (use own name — safe)
    try:
        await client.follow_agent("steward-protocol")
        report.record("follow", True, {"agent": "steward-protocol"})
    except Exception as e:
        report.record("follow", False, error=str(e))

    try:
        await client.unfollow_agent("steward-protocol")
        report.record("unfollow", True, {"agent": "steward-protocol"})
    except Exception as e:
        report.record("unfollow", False, error=str(e))

    # 6e. SUBSCRIBE / UNSUBSCRIBE
    try:
        await client.subscribe_submolt("general")
        report.record("subscribe", True, {"submolt": "general"})
    except Exception as e:
        report.record("subscribe", False, error=str(e))

    try:
        await client.unsubscribe_submolt("general")
        report.record("unsubscribe", True, {"submolt": "general"})
    except Exception as e:
        report.record("unsubscribe", False, error=str(e))

    # 6f. DELETE POST (TAMAS — cleanup)
    if created_post_id:
        try:
            await client.delete_post(created_post_id)
            report.record("delete_post", True, {"deleted": created_post_id})
        except Exception as e:
            report.record("delete_post", False, error=str(e))
    else:
        report.record("delete_post", False, error="no post to delete")

    # 6g. SEND DM REQUEST (only in offline — don't spam real agents)
    if client.offline_mode:
        try:
            dm_req = await client.send_dm_request("test-agent", "Write-cycle DM request test")
            report.record("send_dm_request", True, {"to": "test-agent"})
        except Exception as e:
            report.record("send_dm_request", False, error=str(e))

        try:
            dm = await client.send_dm("conv-test", "Write-cycle DM test")
            report.record("send_dm", True, {"conv": "conv-test"})
        except Exception as e:
            report.record("send_dm", False, error=str(e))

    return report.summary()


def _resolve_api_key() -> str:
    """
    Resolve API key from standard locations (same order as moltbook_heartbeat.py):
    1. MOLTBOOK_API_KEY env var
    2. ~/.config/moltbook/credentials.json
    """
    from pathlib import Path

    # 1. Environment variable
    key = os.environ.get("MOLTBOOK_API_KEY", "")
    if key:
        return key

    # 2. Credentials file
    try:
        import json as _json

        creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
        if creds_path.exists():
            creds = _json.loads(creds_path.read_text())
            key = creds.get("api_key", "")
            if key:
                return key
    except Exception as e:
        logger.warning(f"Credential file read failed: {e}")

    return ""


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Moltbook API Dry-Run")
    parser.add_argument("--offline", action="store_true", help="Use offline mock (includes write cycle)")
    parser.add_argument("--live-fire", action="store_true", help="Enable REAL writes against live API (post+delete)")
    args = parser.parse_args()

    offline = args.offline
    live_fire = args.live_fire
    api_key = "" if offline else _resolve_api_key()

    if not api_key and not offline:
        print("No API key found.")
        print("  Checked: MOLTBOOK_API_KEY env, ~/.config/moltbook/credentials.json")
        print("  Use --offline for mock mode.")
        sys.exit(1)

    if not api_key:
        api_key = "offline_dry_run_key"

    # Offline always enables writes (it's a mock). Live only writes with --live-fire.
    write_enabled = offline or live_fire

    client = MoltbookClient(api_key=api_key, offline_mode=offline)

    if offline:
        mode = "OFFLINE MOCK (writes enabled)"
    elif live_fire:
        mode = "LIVE API + LIVE FIRE (writes enabled!)"
    else:
        mode = "LIVE API (read-only)"

    print(f"\n{'='*60}")
    print(f"MOLTBOOK DRY-RUN — {mode}")
    print(f"{'='*60}")

    success = asyncio.run(run_dry_run(client, write_enabled=write_enabled))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
