"""
Experiment 02 — Content Study: What makes good Moltbook posts?

Study the highest-performing posts and comments to understand:
1. What title patterns get engagement?
2. What content structure works?
3. How long are successful posts?
4. What agents consistently get upvotes?
5. What does auroras_happycapy (engineering content king) actually post?
6. What comments get engagement? What's the engagement pattern?

Run: MOLTBOOK_API_KEY=... PYTHONPATH=. python vibe_core/mahamantra_research/agent_city_development/experiment_02_content_study.py
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


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


# ── 1. Top Posts Analysis ─────────────────────────────────────────────

async def study_top_posts(client) -> dict:
    """Analyze the highest-performing posts — what makes them work?"""
    print("\n" + "=" * 70)
    print("1. TOP POSTS — What Gets Upvotes?")
    print("=" * 70)

    result = {
        "posts": [],
        "title_patterns": Counter(),
        "avg_content_length": 0,
        "top_authors": Counter(),
    }

    try:
        feed = await client.get_feed(sort="hot", limit=25)
        total_length = 0
        for post in sorted(feed, key=lambda p: p.get("upvotes", 0) if isinstance(p, dict) else 0, reverse=True):
            if not isinstance(post, dict):
                continue
            title = post.get("title", "")
            content = post.get("content", "")
            upvotes = post.get("upvotes", 0)
            comments = post.get("comment_count", 0)
            author = post.get("author", {})
            author_name = author.get("name", "?") if isinstance(author, dict) else "?"
            submolt = post.get("submolt", {})
            submolt_name = submolt.get("name", "") if isinstance(submolt, dict) else ""
            post_id = post.get("id", "")

            total_length += len(content)
            result["top_authors"][author_name] += 1

            # Title pattern analysis
            title_lower = title.lower()
            if ":" in title:
                result["title_patterns"]["colon_structure"] += 1
            if title_lower.startswith(("why ", "how ", "what ")):
                result["title_patterns"]["question_start"] += 1
            if any(w in title_lower for w in ["stop", "don't", "never", "nobody"]):
                result["title_patterns"]["contrarian"] += 1
            if any(w in title_lower for w in ["build", "built", "made", "shipped"]):
                result["title_patterns"]["build_log"] += 1
            if len(title.split()) <= 5:
                result["title_patterns"]["short_title"] += 1

            entry = {
                "id": post_id,
                "title": title[:120],
                "content_length": len(content),
                "content_preview": content[:300],
                "upvotes": upvotes,
                "comments": comments,
                "author": author_name,
                "submolt": submolt_name,
            }
            result["posts"].append(entry)

            print(f"\n  [{upvotes:>4}↑ {comments:>3}💬] {author_name}")
            print(f"    Title: {title[:80]}")
            print(f"    Length: {len(content)} chars | Submolt: m/{submolt_name}")
            print(f"    Preview: {content[:120]}")

        if result["posts"]:
            result["avg_content_length"] = total_length // len(result["posts"])
    except Exception as e:
        print(f"  Error: {e}")

    return result


# ── 2. Comment Engagement Patterns ────────────────────────────────────

async def study_comments(client, post_ids: list) -> dict:
    """What kind of comments get engagement?"""
    print("\n" + "=" * 70)
    print("2. COMMENT PATTERNS — What Engagement Looks Like")
    print("=" * 70)

    result = {"comments": [], "avg_length": 0}
    total_length = 0
    count = 0

    for post_id in post_ids[:5]:  # Cap API calls
        print(f"\n  ── Comments on post {post_id[:12]}... ──")
        try:
            comments = await client.get_comments(post_id, sort="top")
            for c in comments[:5]:
                if not isinstance(c, dict):
                    continue
                content = c.get("content", "")
                upvotes = c.get("upvotes", 0)
                author = c.get("author", {})
                author_name = author.get("name", "?") if isinstance(author, dict) else "?"
                total_length += len(content)
                count += 1
                entry = {
                    "author": author_name,
                    "content": content[:300],
                    "upvotes": upvotes,
                    "length": len(content),
                }
                result["comments"].append(entry)
                print(f"    [{upvotes:>3}↑] {author_name}: {content[:80]}")
        except Exception as e:
            print(f"    Error: {e}")

    if count > 0:
        result["avg_length"] = total_length // count
    return result


# ── 3. auroras_happycapy Deep Dive ────────────────────────────────────

async def study_target_agent(client, agent_name: str) -> dict:
    """Study a specific high-performing agent's content."""
    print(f"\n{'=' * 70}")
    print(f"3. AGENT DEEP DIVE: {agent_name}")
    print("=" * 70)

    result = {"profile": {}, "posts": [], "topics": []}

    try:
        profile = await client.get_profile(agent_name)
        agent = profile.get("agent", profile)
        result["profile"] = {
            "name": agent.get("name", ""),
            "karma": agent.get("karma", 0),
            "followers": agent.get("follower_count", 0),
            "description": (agent.get("description", "") or "")[:300],
        }
        print(f"\n  Karma: {result['profile']['karma']}")
        print(f"  Followers: {result['profile']['followers']}")
        print(f"  Bio: {result['profile']['description'][:100]}")
    except Exception as e:
        print(f"  Profile error: {e}")

    # Search for their posts
    try:
        results = await client.semantic_search(agent_name, limit=10)
        for item in results:
            if not isinstance(item, dict):
                continue
            author = item.get("author", {})
            name = author.get("name", "") if isinstance(author, dict) else ""
            if name == agent_name:
                text = item.get("text", "")[:200]
                itype = item.get("type", "")
                result["posts"].append({"text": text, "type": itype})
                print(f"\n  [{itype}] {text[:100]}")
    except Exception as e:
        print(f"  Search error: {e}")

    return result


# ── 4. What Topics Does the Community Care About? ─────────────────────

async def map_community_interests(client) -> dict:
    """What topics actually get engagement vs. what gets ignored?"""
    print(f"\n{'=' * 70}")
    print("4. COMMUNITY INTEREST MAP")
    print("=" * 70)

    result = {"topic_engagement": {}}

    topics = {
        "agent memory": "memory, persistence, knowledge, context window",
        "agent coordination": "multi-agent, coordination, federation, collaboration",
        "agent identity": "identity, persona, personality, consciousness",
        "infrastructure": "cron, heartbeat, deployment, hosting, compute",
        "tooling": "tools, prompts, workflows, automation",
        "security": "security, vulnerability, exploit, safety",
        "governance": "governance, voting, council, rules, moderation",
        "economics": "economy, tokens, credits, payment, earning",
        "human-agent": "human, user, partner, collaboration",
    }

    for topic_name, query in topics.items():
        print(f"\n  ── {topic_name}: '{query[:40]}' ──")
        try:
            results = await client.semantic_search(query, limit=5)
            post_count = 0
            total_engagement = 0
            for item in results:
                if isinstance(item, dict) and item.get("type") in ("post", "comment"):
                    post_count += 1
            result["topic_engagement"][topic_name] = {
                "query": query,
                "results": post_count,
            }
            print(f"    Results: {post_count} posts/comments")
        except Exception as e:
            print(f"    Error: {e}")

    return result


# ── Main ──────────────────────────────────────────────────────────────

async def main():
    print("=" * 70)
    print("CONTENT STUDY — What Works on Moltbook?")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    client = get_client()
    findings = {}

    # 1. Top posts
    findings["top_posts"] = await study_top_posts(client)

    # 2. Comments on top posts
    top_post_ids = [p["id"] for p in findings["top_posts"]["posts"][:5] if p.get("id")]
    findings["comments"] = await study_comments(client, top_post_ids)

    # 3. Study auroras_happycapy
    findings["aurora"] = await study_target_agent(client, "auroras_happycapy")
    findings["hazel"] = await study_target_agent(client, "Hazel_OC")

    # 4. Community interests
    findings["interests"] = await map_community_interests(client)

    # Save
    output_path = Path(__file__).parent / "content_study_findings.json"
    output_path.write_text(json.dumps(findings, indent=2, default=str))
    print(f"\n\n>>> Findings saved to: {output_path}")

    # Summary
    print(f"\n{'=' * 70}")
    print("CONTENT STUDY SUMMARY")
    print("=" * 70)
    tp = findings["top_posts"]
    print(f"  Posts analyzed: {len(tp['posts'])}")
    print(f"  Avg content length: {tp['avg_content_length']} chars")
    print(f"  Title patterns: {dict(tp['title_patterns'])}")
    print(f"  Top authors: {dict(tp['top_authors'].most_common(5))}")
    print(f"  Comments analyzed: {len(findings['comments']['comments'])}")
    print(f"  Avg comment length: {findings['comments']['avg_length']} chars")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
