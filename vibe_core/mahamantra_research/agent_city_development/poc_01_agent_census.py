"""
PoC 01 — Agent City Census: Discover agents on Moltbook + generate Mahamantra seeds.

Validates:
1. Can we discover agents via Moltbook feed + search?
2. Can we generate RAMA coordinates for arbitrary agent names?
3. What does the data look like?

Run: PYTHONPATH=. python vibe_core/mahamantra_research/agent_city_development/poc_01_agent_census.py
"""

import json
import sys
import os
from pathlib import Path
from typing import Optional

# ── Moltbook API ──────────────────────────────────────────────────────


def get_api_key() -> str:
    """Resolve Moltbook API key (env var → credentials file)."""
    key = os.environ.get("MOLTBOOK_API_KEY", "")
    if not key:
        creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
        if creds_path.exists():
            key = json.loads(creds_path.read_text()).get("api_key", "")
    if not key:
        print("ERROR: No MOLTBOOK_API_KEY found")
        sys.exit(1)
    return key


def create_client():
    """Create MoltbookClient instance."""
    from vibe_core.mahamantra.adapters.moltbook import MoltbookClient

    return MoltbookClient(api_key=get_api_key())


# ── Agent Discovery ──────────────────────────────────────────────────


async def discover_agents_from_feed(client) -> dict[str, dict]:
    """Scan feed for agents. Returns {name: profile_data}."""
    agents = {}

    # Global feed (cold start — no subscriptions needed)
    print("\n── Scanning global feed (hot, limit=25) ──")
    try:
        posts = await client.get_feed(sort="hot", limit=25)
        print(f"  Got {len(posts)} posts")
        for post in posts:
            author = post.get("author", {}) if isinstance(post, dict) else {}
            name = author.get("name", "")
            if name and name not in agents:
                agents[name] = {
                    "source": "feed",
                    "post_title": post.get("title", "")[:60],
                    "upvotes": post.get("upvotes", 0),
                }
                print(f"  Discovered: {name}")
    except Exception as e:
        print(f"  Feed error: {e}")

    # Personalized feed
    print("\n── Scanning personalized feed (hot, limit=25) ──")
    try:
        posts = await client.get_personalized_feed(sort="hot", limit=25)
        print(f"  Got {len(posts)} posts")
        for post in posts:
            author = post.get("author", {}) if isinstance(post, dict) else {}
            name = author.get("name", "")
            if name and name not in agents:
                agents[name] = {
                    "source": "personalized_feed",
                    "post_title": post.get("title", "")[:60],
                    "upvotes": post.get("upvotes", 0),
                }
                print(f"  Discovered: {name}")
    except Exception as e:
        print(f"  Personalized feed error: {e}")

    # Semantic search for agents
    search_queries = [
        "AI agent autonomous",
        "artificial intelligence",
        "agent city community",
        "blockchain crypto web3",
        "developer tools programming",
    ]
    for query in search_queries:
        print(f"\n── Searching: '{query}' ──")
        try:
            items = await client.semantic_search(query=query, limit=10)
            print(f"  Got {len(items)} results")
            for item in items:
                item_type = item.get("type", "") if isinstance(item, dict) else ""
                author = item.get("author", {}) if isinstance(item, dict) else {}
                name = author.get("name", "") if isinstance(author, dict) else ""
                if name and name not in agents:
                    agents[name] = {
                        "source": f"search:{query[:20]}",
                        "type": item_type,
                        "text_preview": item.get("text", "")[:60],
                    }
                    print(f"  Discovered: {name} (type={item_type})")
                if item_type == "agent":
                    print(f"  *** AGENT RESULT: {item}")
        except Exception as e:
            print(f"  Search error: {e}")

    return agents


async def fetch_agent_profiles(client, agent_names: list[str]) -> dict[str, dict]:
    """Fetch full profiles for discovered agents."""
    profiles = {}
    for name in agent_names:
        print(f"\n── Fetching profile: {name} ──")
        try:
            result = await client.get_profile(name)
            agent_data = result.get("agent", result)
            profiles[name] = {
                "name": agent_data.get("name", name),
                "description": (agent_data.get("description", "") or "")[:200],
                "karma": agent_data.get("karma", 0),
                "follower_count": agent_data.get("follower_count", 0),
                "following_count": agent_data.get("following_count", 0),
                "is_active": agent_data.get("is_active", False),
                "last_active": agent_data.get("last_active", ""),
                "created_at": agent_data.get("created_at", ""),
            }
            print(
                f"  karma={profiles[name]['karma']} "
                f"followers={profiles[name]['follower_count']} "
                f"active={profiles[name]['is_active']}"
            )
        except Exception as e:
            print(f"  Profile error for {name}: {e}")
            profiles[name] = {"name": name, "error": str(e)}
    return profiles


# ── Mahamantra Seed Generation ───────────────────────────────────────


def generate_seed(agent_name: str) -> Optional[dict]:
    """Generate Mahamantra RAMA coordinates + seed for an agent name."""
    try:
        from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import (
            encode_text,
            encode_with_detail,
        )
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
            full_signature,
            COORD_ELEMENT,
            ELEMENT_NAMES,
        )

        coords = encode_text(agent_name)
        detail = encode_with_detail(agent_name)
        signature = full_signature(coords) if coords else ""

        # Derive zone from dominant element
        element_counts = {}
        for d in detail:
            elem = d.get("element", "unknown")
            element_counts[elem] = element_counts.get(elem, 0) + 1
        dominant_element = max(element_counts, key=element_counts.get) if element_counts else "unknown"

        # Zone mapping based on element
        zone_map = {
            "PRITHVI": "engineering",  # Earth → building
            "JALA": "research",  # Water → flowing knowledge
            "AGNI": "governance",  # Fire → leadership
            "VAYU": "general",  # Air → communication
            "AKASHA": "research",  # Ether → abstract
        }

        return {
            "name": agent_name,
            "rama_coordinates": list(coords),
            "signature": signature,
            "detail": detail[:5],  # First 5 phonemes for display
            "dominant_element": dominant_element,
            "element_distribution": element_counts,
            "suggested_zone": zone_map.get(dominant_element, "general"),
            "coord_count": len(coords),
        }
    except Exception as e:
        print(f"  Seed generation error for {agent_name}: {e}")
        import traceback

        traceback.print_exc()
        return None


# ── Main ─────────────────────────────────────────────────────────────


async def main():
    print("=" * 60)
    print("Agent City Census — Proof of Concept")
    print("=" * 60)

    client = create_client()

    # Phase 1: Discover agents
    print("\n\n### PHASE 1: AGENT DISCOVERY ###")
    discovered = await discover_agents_from_feed(client)
    print(f"\n>>> Total unique agents discovered: {len(discovered)}")

    if not discovered:
        print("No agents found via feed/search. Testing with known name 'steward-protocol'.")
        discovered = {"steward-protocol": {"source": "self"}}

    # Phase 2: Fetch profiles
    print("\n\n### PHASE 2: PROFILE FETCHING ###")
    agent_names = list(discovered.keys())[:20]  # Cap at 20 to respect rate limits
    profiles = await fetch_agent_profiles(client, agent_names)

    # Phase 3: Generate seeds
    print("\n\n### PHASE 3: MAHAMANTRA SEED GENERATION ###")
    seeds = {}
    for name in agent_names:
        print(f"\n── Generating seed: {name} ──")
        seed = generate_seed(name)
        if seed:
            seeds[name] = seed
            print(f"  RAMA coords: {seed['rama_coordinates'][:8]}...")
            print(f"  Signature: {seed['signature'][:40]}...")
            print(f"  Element: {seed['dominant_element']}")
            print(f"  Zone: {seed['suggested_zone']}")

    # Phase 4: Build registry
    print("\n\n### PHASE 4: PROTO-REGISTRY ###")
    registry = {
        "version": 1,
        "census_date": __import__("datetime").datetime.now().isoformat(),
        "total_discovered": len(discovered),
        "total_profiled": len([p for p in profiles.values() if "error" not in p]),
        "total_seeded": len(seeds),
        "agents": {},
    }

    for name in agent_names:
        entry = {
            "name": name,
            "discovery": discovered.get(name, {}),
            "profile": profiles.get(name, {}),
            "seed": seeds.get(name, {}),
        }
        registry["agents"][name] = entry

    # Save results
    output_path = Path(__file__).parent / "census_results.json"
    output_path.write_text(json.dumps(registry, indent=2, default=str))
    print(f"\n>>> Census saved to: {output_path}")
    print(f">>> Discovered: {registry['total_discovered']} agents")
    print(f">>> Profiled:   {registry['total_profiled']} agents")
    print(f">>> Seeded:     {registry['total_seeded']} agents")

    # Summary table
    print("\n\n### CENSUS SUMMARY ###")
    print(f"{'Name':<25} {'Karma':>6} {'Followers':>10} {'Element':<10} {'Zone':<12}")
    print("-" * 70)
    for name in agent_names:
        profile = profiles.get(name, {})
        seed = seeds.get(name, {})
        print(
            f"{name:<25} "
            f"{profile.get('karma', '?'):>6} "
            f"{profile.get('follower_count', '?'):>10} "
            f"{seed.get('dominant_element', '?'):<10} "
            f"{seed.get('suggested_zone', '?'):<12}"
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
