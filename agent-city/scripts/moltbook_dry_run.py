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
import os
import sys
import time
from typing import Any, Dict, List

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
            print(f"\nFAILED:")
            for r in self.results:
                if not r["success"]:
                    print(f"  ✗ {r['name']}: {r['error']}")
        print(f"{'='*60}")
        return failed == 0


async def run_dry_run(client: MoltbookClient) -> bool:
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
    # 6. VOTING (read-only check — don't actually vote in dry-run)
    # =========================================================================
    print("\n[6/8] VOTING (skipped in dry-run — would mutate state)")
    report.record("upvote (skipped)", True, data="dry-run: no mutation")
    report.record("downvote (skipped)", True, data="dry-run: no mutation")
    report.record("upvote_comment (skipped)", True, data="dry-run: no mutation")

    # =========================================================================
    # 7. FOLLOWING (read-only check)
    # =========================================================================
    print("\n[7/8] FOLLOWING (skipped in dry-run — would mutate state)")
    report.record("follow_agent (skipped)", True, data="dry-run: no mutation")
    report.record("unfollow_agent (skipped)", True, data="dry-run: no mutation")
    report.record("subscribe_submolt (skipped)", True, data="dry-run: no mutation")
    report.record("unsubscribe_submolt (skipped)", True, data="dry-run: no mutation")

    # =========================================================================
    # 8. PROFILE UPDATE (read-only check)
    # =========================================================================
    print("\n[8/8] PROFILE UPDATE (skipped in dry-run — would mutate state)")
    report.record("update_profile (skipped)", True, data="dry-run: no mutation")
    report.record("delete_post (skipped)", True, data="dry-run: no mutation")

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
    except Exception:
        pass

    return ""


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Moltbook API Dry-Run")
    parser.add_argument("--offline", action="store_true", help="Use offline mock")
    args = parser.parse_args()

    offline = args.offline
    api_key = "" if offline else _resolve_api_key()

    if not api_key and not offline:
        print("No API key found.")
        print("  Checked: MOLTBOOK_API_KEY env, ~/.config/moltbook/credentials.json")
        print("  Use --offline for mock mode.")
        sys.exit(1)

    if not api_key:
        api_key = "offline_dry_run_key"

    client = MoltbookClient(api_key=api_key, offline_mode=offline)
    mode = "OFFLINE MOCK" if offline else "LIVE API"
    print(f"\n{'='*60}")
    print(f"MOLTBOOK DRY-RUN — {mode}")
    print(f"{'='*60}")

    success = asyncio.run(run_dry_run(client))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
