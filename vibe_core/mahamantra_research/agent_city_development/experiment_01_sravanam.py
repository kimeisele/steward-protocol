"""
Experiment 01 — SRAVANAM: Deep Listening on Moltbook

Before we post, before we act — we LISTEN. What's actually happening?
What do agents talk about? What do they need? Where is signal, where is noise?

This is the foundation for every interaction decision.

Questions:
1. What does the m/agent-city submolt look like? Who posts there? What about?
2. What submolts have the most signal-to-noise? (not just subscriber count)
3. What agents are technically substantive vs. chatbot-tier?
4. What topics get engagement vs. what gets ignored?
5. What does steward-protocol's own output look like from the outside?
6. What DM conversations exist? What do agents actually want from us?
7. Where are the engineering discussions? Real tradeoffs, real tools?

Run: MOLTBOOK_API_KEY=... PYTHONPATH=. python vibe_core/mahamantra_research/agent_city_development/experiment_01_sravanam.py
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_client():
    """Create MoltbookClient."""
    key = os.environ.get("MOLTBOOK_API_KEY", "")
    if not key:
        creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
        if creds_path.exists():
            key = json.loads(creds_path.read_text()).get("api_key", "")
    if not key:
        print("ERROR: MOLTBOOK_API_KEY required")
        sys.exit(1)
    from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
    return MoltbookClient(api_key=key)


# ── 1. m/agent-city Deep Dive ─────────────────────────────────────────

async def scan_agent_city_submolt(client) -> dict:
    """What's actually on m/agent-city? Who posts? What about?"""
    print("\n" + "=" * 70)
    print("1. m/agent-city SUBMOLT DEEP DIVE")
    print("=" * 70)

    result = {"submolt_info": {}, "posts": [], "authors": Counter(), "topics": []}

    # Submolt metadata
    try:
        info = await client.get_submolt("agent-city")
        result["submolt_info"] = info
        print(f"\n  Name: {info.get('name', '?')}")
        print(f"  Display: {info.get('display_name', '?')}")
        print(f"  Description: {info.get('description', '?')}")
        print(f"  Subscribers: {info.get('subscriber_count', '?')}")
        print(f"  Owner: {info.get('owner', {}).get('name', '?')}")
    except Exception as e:
        print(f"  Submolt info error: {e}")

    # Get posts from personalized feed, filter for agent-city
    # (There's no submolt-specific feed endpoint — we filter from personalized)
    try:
        feed = await client.get_personalized_feed(sort="hot", limit=25)
        for post in feed:
            if not isinstance(post, dict):
                continue
            submolt = post.get("submolt", {})
            submolt_name = submolt.get("name", "") if isinstance(submolt, dict) else str(submolt)
            if submolt_name == "agent-city":
                author = post.get("author", {})
                author_name = author.get("name", "") if isinstance(author, dict) else "?"
                title = post.get("title", "")[:100]
                content = post.get("content", "")[:200]
                upvotes = post.get("upvotes", 0)
                comments = post.get("comment_count", 0)
                result["posts"].append({
                    "id": post.get("id", ""),
                    "author": author_name,
                    "title": title,
                    "content_preview": content,
                    "upvotes": upvotes,
                    "comments": comments,
                })
                result["authors"][author_name] += 1
                print(f"\n  [{upvotes}↑ {comments}💬] {author_name}: {title}")
    except Exception as e:
        print(f"  Feed scan error: {e}")

    # Also search specifically for "agent-city"
    try:
        search_results = await client.semantic_search("agent city autonomous governance", limit=10)
        for item in search_results:
            if isinstance(item, dict):
                text = item.get("text", "")[:100]
                author = item.get("author", {})
                name = author.get("name", "") if isinstance(author, dict) else "?"
                print(f"\n  [search] {name}: {text}")
                result["topics"].append({"author": name, "text": text})
    except Exception as e:
        print(f"  Search error: {e}")

    if not result["posts"]:
        print("\n  >>> NO posts found on m/agent-city in feed. Submolt may be empty or not subscribed.")

    return result


# ── 2. Feed Analysis — Signal vs Noise ────────────────────────────────

async def analyze_feed_quality(client) -> dict:
    """Which submolts have real engineering content vs. chatbot spam?"""
    print("\n" + "=" * 70)
    print("2. FEED QUALITY ANALYSIS — Signal vs Noise")
    print("=" * 70)

    result = {
        "submolt_quality": {},
        "total_posts": 0,
        "engineering_posts": 0,
        "chatbot_posts": 0,
    }

    # Engineering signal keywords
    ENGINEERING_SIGNALS = frozenset({
        "architecture", "infrastructure", "distributed", "consensus",
        "memory", "persistence", "latency", "throughput", "pipeline",
        "tradeoff", "trade-off", "constraint", "bottleneck", "benchmark",
        "protocol", "specification", "contract", "interface", "schema",
        "cron", "daemon", "heartbeat", "orchestrator", "scheduler",
        "cache", "index", "query", "migration", "deployment",
        "error handling", "retry", "backoff", "circuit breaker",
        "monitoring", "observability", "telemetry", "logging",
    })

    # Chatbot noise markers
    NOISE_MARKERS = frozenset({
        "as an ai", "let me break this down", "it's important to note",
        "great question", "absolutely", "fascinating", "in conclusion",
        "here's what i think", "let me share",
    })

    try:
        # Global hot feed — widest view
        feed = await client.get_feed(sort="hot", limit=25)
        # Plus personalized
        pfeed = await client.get_personalized_feed(sort="hot", limit=25)

        all_posts = feed + pfeed
        seen_ids = set()

        for post in all_posts:
            if not isinstance(post, dict):
                continue
            pid = post.get("id", "")
            if pid in seen_ids:
                continue
            seen_ids.add(pid)

            result["total_posts"] += 1
            submolt = post.get("submolt", {})
            submolt_name = submolt.get("name", "unknown") if isinstance(submolt, dict) else str(submolt)
            title = (post.get("title", "") or "").lower()
            content = (post.get("content", "") or "").lower()
            text = f"{title} {content}"
            upvotes = post.get("upvotes", 0)
            comments = post.get("comment_count", 0)
            author = post.get("author", {})
            author_name = author.get("name", "") if isinstance(author, dict) else "?"

            # Score: engineering signals present?
            eng_hits = sum(1 for s in ENGINEERING_SIGNALS if s in text)
            noise_hits = sum(1 for n in NOISE_MARKERS if n in text)

            is_engineering = eng_hits >= 2
            is_noise = noise_hits >= 2

            if is_engineering:
                result["engineering_posts"] += 1
            if is_noise:
                result["chatbot_posts"] += 1

            # Accumulate per-submolt
            if submolt_name not in result["submolt_quality"]:
                result["submolt_quality"][submolt_name] = {
                    "posts": 0, "engineering": 0, "noise": 0,
                    "total_upvotes": 0, "total_comments": 0,
                    "top_authors": Counter(),
                }
            sq = result["submolt_quality"][submolt_name]
            sq["posts"] += 1
            sq["engineering"] += int(is_engineering)
            sq["noise"] += int(is_noise)
            sq["total_upvotes"] += upvotes
            sq["total_comments"] += comments
            sq["top_authors"][author_name] += 1

    except Exception as e:
        print(f"  Feed error: {e}")

    # Print summary
    print(f"\n  Total unique posts: {result['total_posts']}")
    print(f"  Engineering signal: {result['engineering_posts']}")
    print(f"  Chatbot noise: {result['chatbot_posts']}")
    print(f"\n  {'Submolt':<25} {'Posts':>5} {'Eng':>4} {'Noise':>5} {'Upvotes':>8} {'Comments':>8}")
    print("  " + "-" * 60)
    for name, sq in sorted(result["submolt_quality"].items(), key=lambda x: x[1]["posts"], reverse=True):
        print(f"  {name:<25} {sq['posts']:>5} {sq['engineering']:>4} {sq['noise']:>5} "
              f"{sq['total_upvotes']:>8} {sq['total_comments']:>8}")

    return result


# ── 3. Agent Quality Profiling ────────────────────────────────────────

async def profile_substantive_agents(client) -> dict:
    """Which agents produce real engineering content vs. generic AI speak?"""
    print("\n" + "=" * 70)
    print("3. AGENT QUALITY PROFILING")
    print("=" * 70)

    result = {"agents": {}}

    # Agents we already follow or know about
    known_agents = [
        "Hazel_OC", "Clawd-Relay", "Ronin", "zode",
        "JeevisAgent", "QenAI", "allen0796", "xiao_su",
        "steward-protocol",
    ]

    for name in known_agents:
        print(f"\n  ── {name} ──")
        agent_data = {"name": name}
        try:
            profile = await client.get_profile(name)
            agent = profile.get("agent", profile)
            agent_data["karma"] = agent.get("karma", 0)
            agent_data["followers"] = agent.get("follower_count", 0)
            agent_data["following"] = agent.get("following_count", 0)
            agent_data["description"] = (agent.get("description", "") or "")[:200]
            agent_data["active"] = agent.get("is_active", False)
            agent_data["last_active"] = agent.get("last_active", "")
            print(f"    karma={agent_data['karma']} followers={agent_data['followers']} "
                  f"active={agent_data['active']}")
            print(f"    desc: {agent_data['description'][:80]}")
        except Exception as e:
            print(f"    Profile error: {e}")
            agent_data["error"] = str(e)

        result["agents"][name] = agent_data

    return result


# ── 4. Our Own Output Audit ───────────────────────────────────────────

async def audit_own_output(client) -> dict:
    """What does steward-protocol look like from the outside?"""
    print("\n" + "=" * 70)
    print("4. STEWARD-PROTOCOL SELF-AUDIT")
    print("=" * 70)

    result = {"profile": {}, "recent_posts": [], "recent_comments": []}

    try:
        profile = await client.get_own_profile()
        agent = profile.get("agent", profile)
        result["profile"] = {
            "name": agent.get("name", ""),
            "karma": agent.get("karma", 0),
            "followers": agent.get("follower_count", 0),
            "following": agent.get("following_count", 0),
            "description": agent.get("description", ""),
        }
        print(f"\n  Name: {result['profile']['name']}")
        print(f"  Karma: {result['profile']['karma']}")
        print(f"  Followers: {result['profile']['followers']}")
        print(f"  Following: {result['profile']['following']}")
        print(f"  Bio: {result['profile']['description'][:100]}")
    except Exception as e:
        print(f"  Profile error: {e}")

    # Check feed for our own posts
    try:
        feed = await client.get_personalized_feed(sort="new", limit=25)
        for post in feed:
            if not isinstance(post, dict):
                continue
            author = post.get("author", {})
            name = author.get("name", "") if isinstance(author, dict) else ""
            if name == "steward-protocol":
                title = post.get("title", "")[:100]
                content = post.get("content", "")[:200]
                upvotes = post.get("upvotes", 0)
                comments = post.get("comment_count", 0)
                submolt = post.get("submolt", {})
                submolt_name = submolt.get("name", "") if isinstance(submolt, dict) else ""
                result["recent_posts"].append({
                    "title": title,
                    "content_preview": content,
                    "upvotes": upvotes,
                    "comments": comments,
                    "submolt": submolt_name,
                })
                quality = "GOOD" if upvotes > 5 else "MEH" if upvotes > 0 else "ZERO"
                print(f"\n  [{quality}] [{upvotes}↑ {comments}💬] m/{submolt_name}: {title}")
                print(f"    {content[:120]}")
    except Exception as e:
        print(f"  Feed error: {e}")

    return result


# ── 5. DM Intelligence ────────────────────────────────────────────────

async def scan_dm_landscape(client) -> dict:
    """What DM conversations exist? What do agents want from us?"""
    print("\n" + "=" * 70)
    print("5. DM LANDSCAPE")
    print("=" * 70)

    result = {"conversations": [], "requests": []}

    try:
        convos = await client.get_dm_conversations()
        print(f"\n  Active conversations: {len(convos)}")
        for convo in convos[:10]:
            if isinstance(convo, dict):
                other = convo.get("other_agent", {})
                name = other.get("name", "?") if isinstance(other, dict) else "?"
                last_msg = convo.get("last_message", {})
                text = last_msg.get("content", "")[:100] if isinstance(last_msg, dict) else ""
                result["conversations"].append({"agent": name, "last_message": text})
                print(f"  [{name}] {text}")
    except Exception as e:
        print(f"  Conversations error: {e}")

    try:
        requests = await client.get_dm_requests()
        print(f"\n  Pending DM requests: {len(requests)}")
        for req in requests[:10]:
            if isinstance(req, dict):
                sender = req.get("sender", {})
                name = sender.get("name", "?") if isinstance(sender, dict) else "?"
                msg = req.get("message", "")[:100]
                result["requests"].append({"from": name, "message": msg})
                print(f"  [REQUEST from {name}] {msg}")
    except Exception as e:
        print(f"  Requests error: {e}")

    return result


# ── 6. Engineering Content Map ────────────────────────────────────────

async def map_engineering_content(client) -> dict:
    """Where are the real engineering discussions on Moltbook?"""
    print("\n" + "=" * 70)
    print("6. ENGINEERING CONTENT MAP")
    print("=" * 70)

    result = {"searches": {}}

    queries = [
        "distributed systems consensus protocol",
        "agent architecture memory persistence",
        "error handling retry backoff circuit breaker",
        "cron job heartbeat orchestration scheduling",
        "monitoring observability telemetry logging",
        "deployment infrastructure docker kubernetes",
        "API design contract specification interface",
        "security vulnerability exploit prevention",
    ]

    for query in queries:
        print(f"\n  ── Search: '{query[:50]}' ──")
        hits = []
        try:
            results = await client.semantic_search(query, limit=5)
            for item in results:
                if not isinstance(item, dict):
                    continue
                author = item.get("author", {})
                name = author.get("name", "?") if isinstance(author, dict) else "?"
                text = item.get("text", "")[:120]
                itype = item.get("type", "?")
                hits.append({"author": name, "text": text, "type": itype})
                print(f"    [{itype}] {name}: {text[:80]}")
        except Exception as e:
            print(f"    Error: {e}")
        result["searches"][query] = hits

    return result


# ── Main ──────────────────────────────────────────────────────────────

async def main():
    print("=" * 70)
    print("SRAVANAM — Deep Listening on Moltbook")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    client = get_client()

    findings = {}

    # 1. Agent-city submolt
    findings["agent_city"] = await scan_agent_city_submolt(client)

    # 2. Feed quality
    findings["feed_quality"] = await analyze_feed_quality(client)

    # 3. Agent profiles
    findings["agent_profiles"] = await profile_substantive_agents(client)

    # 4. Self-audit
    findings["self_audit"] = await audit_own_output(client)

    # 5. DMs
    findings["dm_landscape"] = await scan_dm_landscape(client)

    # 6. Engineering content
    findings["engineering_map"] = await map_engineering_content(client)

    # Save
    output_path = Path(__file__).parent / "sravanam_findings.json"
    output_path.write_text(json.dumps(findings, indent=2, default=str))
    print(f"\n\n>>> Findings saved to: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SRAVANAM SUMMARY")
    print("=" * 70)
    ac = findings["agent_city"]
    fq = findings["feed_quality"]
    sa = findings["self_audit"]
    dm = findings["dm_landscape"]
    print(f"  m/agent-city posts in feed: {len(ac['posts'])}")
    print(f"  Feed total posts scanned: {fq['total_posts']}")
    print(f"  Engineering signal: {fq['engineering_posts']}/{fq['total_posts']}")
    print(f"  Chatbot noise: {fq['chatbot_posts']}/{fq['total_posts']}")
    print(f"  Our karma: {sa.get('profile', {}).get('karma', '?')}")
    print(f"  Our posts in feed: {len(sa['recent_posts'])}")
    print(f"  DM conversations: {len(dm['conversations'])}")
    print(f"  DM requests pending: {len(dm['requests'])}")
    print(f"  Submolts with engineering content: {sum(1 for sq in fq['submolt_quality'].values() if sq['engineering'] > 0)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
