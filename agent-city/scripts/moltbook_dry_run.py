#!/usr/bin/env python3
"""
Moltbook Dry-Run Simulator
===========================

Reads REAL data from the live Moltbook API. NEVER posts.
Simulates what the system WOULD do and produces a report.

Usage:
    PYTHONPATH=. python3 agent-city/scripts/moltbook_dry_run.py

    # Offline mode (no network, uses mocks):
    MOLTBOOK_OFFLINE_MODE=true PYTHONPATH=. python3 agent-city/scripts/moltbook_dry_run.py

Environment:
    MOLTBOOK_API_KEY      — Bearer token (or reads from ~/.config/moltbook/credentials.json)
    MOLTBOOK_OFFLINE_MODE — "true" to use offline mocks (default: false)
"""

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
logger = logging.getLogger("DRY_RUN")


def _load_api_key() -> str:
    """Load API key from env or credentials file."""
    key = os.environ.get("MOLTBOOK_API_KEY", "")
    if key:
        return key
    try:
        creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
        if creds_path.exists():
            creds = json.loads(creds_path.read_text())
            return creds.get("api_key", "")
    except Exception as e:
        logger.debug(f"Could not read credentials: {e}")
    return ""


def main() -> int:
    """Run the dry-run simulation."""
    api_key = _load_api_key()
    offline = os.environ.get("MOLTBOOK_OFFLINE_MODE", "false").lower() == "true"

    if not api_key and not offline:
        logger.warning("No MOLTBOOK_API_KEY found. Falling back to offline mode.")
        offline = True
        api_key = "offline_dry_run_key"

    if not api_key:
        api_key = "offline_dry_run_key"

    try:
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
    except ImportError as e:
        logger.error(f"Could not import MoltbookClient: {e}")
        return 1

    client = MoltbookClient(api_key=api_key, offline_mode=offline)
    mode = "OFFLINE (mock data)" if offline else "LIVE (real Moltbook API)"

    print()
    print("=" * 70)
    print(f"  MOLTBOOK DRY-RUN SIMULATOR — {mode}")
    print("=" * 70)
    print()

    report = {}
    errors = []

    # =========================================================================
    # 1. HEARTBEAT — DM activity check
    # =========================================================================
    print("--- 1. Heartbeat (DM activity check) ---")
    try:
        hb = client.sync_check_heartbeat()
        report["heartbeat"] = hb
        print(f"  has_new_messages: {hb.get('has_new_messages', '?')}")
        print(f"  pending_requests: {hb.get('pending_requests', '?')}")
    except Exception as e:
        errors.append(f"heartbeat: {e}")
        print(f"  ERROR: {e}")
    print()

    # =========================================================================
    # 2. OWN PROFILE — verify identity
    # =========================================================================
    print("--- 2. Own Profile ---")
    try:
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        profile = _run_async(client.get_own_profile())
        report["own_profile"] = profile
        print(f"  name: {profile.get('name', '?')}")
        print(f"  karma: {profile.get('karma', '?')}")
        print(f"  followers: {profile.get('followers_count', '?')}")
        print(f"  following: {profile.get('following_count', '?')}")
        print(f"  description: {str(profile.get('description', ''))[:80]}")
    except Exception as e:
        errors.append(f"own_profile: {e}")
        print(f"  ERROR: {e}")
    print()

    # =========================================================================
    # 3. FEED — latest posts
    # =========================================================================
    print("--- 3. Feed (latest 5 posts) ---")
    try:
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        feed = _run_async(client.get_feed(sort="new", limit=5))
        report["feed"] = feed
        if not feed:
            print("  (empty feed)")
        for i, post in enumerate(feed[:5]):
            title = post.get("title", "?")[:60]
            author_raw = post.get("author", post.get("agent", "?"))
            if isinstance(author_raw, dict):
                author = author_raw.get("name", "?")
            else:
                author = str(author_raw)
            upvotes = post.get("upvotes", post.get("upvoteCount", "?"))
            submolt_raw = post.get("submolt", post.get("submoltName", ""))
            if isinstance(submolt_raw, dict):
                submolt = submolt_raw.get("name", "")
            else:
                submolt = str(submolt_raw) if submolt_raw else ""
            sub_str = f" in m/{submolt}" if submolt else ""
            print(f"  [{i+1}] \"{title}\" by {author}{sub_str} ({upvotes} upvotes)")
    except Exception as e:
        errors.append(f"feed: {e}")
        print(f"  ERROR: {e}")
    print()

    # =========================================================================
    # 4. SEMANTIC SEARCH — landscape intelligence
    # =========================================================================
    print("--- 4. Semantic Search ---")
    queries = [
        "agent operating system kernel",
        "deterministic computation",
        "cryptographic identity verification",
    ]
    search_results = {}
    for q in queries:
        try:
            from vibe_core.mahamantra.adapters.moltbook import _run_async

            results = _run_async(client.semantic_search(q, limit=3))
            search_results[q] = results
            print(f"  \"{q}\": {len(results)} results")
            for r in results[:2]:
                # Search results can be agents or posts
                name = r.get("name", r.get("title", "?"))[:50]
                sim = r.get("similarity", r.get("score", "?"))
                rtype = r.get("type", "agent" if "karma" in r else "post")
                print(f"    - [{rtype}] \"{name}\" (similarity: {sim})")
        except Exception as e:
            errors.append(f"search({q}): {e}")
            print(f"  \"{q}\": ERROR: {e}")
    report["search"] = search_results
    print()

    # =========================================================================
    # 5. DM CONVERSATIONS — active threads
    # =========================================================================
    print("--- 5. DM Conversations ---")
    try:
        convs_raw = client.sync_get_dm_conversations()
        # Defensive: API may return {"count": N, "items": [...]} or a list
        if isinstance(convs_raw, dict):
            convs = convs_raw.get("items", convs_raw.get("conversations", []))
        elif isinstance(convs_raw, list):
            convs = convs_raw
        else:
            convs = []
        report["conversations"] = convs
        if not convs:
            print("  (no active conversations)")
        for conv in convs[:5]:
            cid = conv.get("id", "?")
            agent_raw = conv.get("with_agent", conv.get("agent", conv.get("otherAgent", "?")))
            if isinstance(agent_raw, dict):
                agent = agent_raw.get("name", "?")
            else:
                agent = str(agent_raw)
            last_msg = conv.get("lastMessage", conv.get("last_message", ""))
            if isinstance(last_msg, dict):
                last_msg = last_msg.get("content", "")[:40]
            print(f"  [{cid[:8]}...] with {agent}" + (f" — \"{last_msg}\"" if last_msg else ""))
    except Exception as e:
        errors.append(f"conversations: {e}")
        print(f"  ERROR: {e}")
    print()

    # =========================================================================
    # 6. DM REQUESTS — pending inbound
    # =========================================================================
    print("--- 6. DM Requests (pending) ---")
    try:
        from vibe_core.mahamantra.adapters.moltbook import _run_async

        requests = _run_async(client.get_dm_requests())
        report["dm_requests"] = requests
        if not requests:
            print("  (no pending requests)")
        for req in requests[:5]:
            rid = req.get("id", "?")
            from_agent = req.get("from_agent", "?")
            msg = req.get("message", "")[:50]
            print(f"  [{rid}] from {from_agent}: \"{msg}\"")
    except Exception as e:
        errors.append(f"dm_requests: {e}")
        print(f"  ERROR: {e}")
    print()

    # =========================================================================
    # 7. SIMULATION — what WOULD we do?
    # =========================================================================
    print("--- 7. Simulated Actions (NOT EXECUTED) ---")
    simulated_actions = []

    # Would we upvote anything from the feed?
    feed_data = report.get("feed", [])
    for post in feed_data[:5]:
        title = post.get("title", "")
        # Simple heuristic: posts about OS/kernel/deterministic are interesting
        keywords = ["kernel", "operating system", "deterministic", "governance", "protocol"]
        if any(kw in title.lower() for kw in keywords):
            simulated_actions.append({
                "action": "upvote",
                "target": post.get("id", "?"),
                "reason": f"Relevant topic: \"{title[:40]}\"",
            })

    # Would we reply to any DMs?
    hb_data = report.get("heartbeat", {})
    if hb_data.get("has_new_messages"):
        simulated_actions.append({
            "action": "process_dms",
            "reason": "New messages detected — would route through Govardhan Gateway",
        })

    # Would we approve any DM requests?
    dm_reqs = report.get("dm_requests", [])
    for req in dm_reqs:
        simulated_actions.append({
            "action": "approve_dm_request",
            "target": req.get("id", "?"),
            "reason": f"Inbound request from {req.get('from_agent', '?')}",
        })

    if not simulated_actions:
        print("  (no actions would be taken this cycle)")
    for sa in simulated_actions:
        action = sa["action"]
        reason = sa["reason"]
        target = sa.get("target", "")
        print(f"  WOULD {action}" + (f" [{target}]" if target else "") + f": {reason}")

    print()

    # =========================================================================
    # 8. RATE LIMIT BUDGET
    # =========================================================================
    print("--- 8. Rate Limit Budget ---")
    limits = client.limits
    print(f"  requests_this_minute: {limits.requests_this_minute} / 100")
    print(f"  posts_this_30m:      {limits.posts_this_30m} / 1")
    print(f"  comments_this_hour:  {limits.comments_this_hour} / 50")
    remaining_requests = 100 - limits.requests_this_minute
    print(f"  remaining capacity:  {remaining_requests} requests this minute")
    print()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Mode:              {mode}")
    print(f"  Errors:            {len(errors)}")
    print(f"  Feed posts read:   {len(report.get('feed', []))}")
    print(f"  Search queries:    {len(report.get('search', {}))}")
    print(f"  Active DM convos:  {len(report.get('conversations', []))}")
    print(f"  Pending DM reqs:   {len(report.get('dm_requests', []))}")
    print(f"  Simulated actions: {len(simulated_actions)}")
    if errors:
        print()
        print("  ERRORS:")
        for e in errors:
            print(f"    - {e}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
