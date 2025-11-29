#!/usr/bin/env python3
"""
AGENT CITY - Stats Collector

Scans data/events/*.jsonl and aggregates XP per agent.
Outputs to agent-city/stats/global.json
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STATS_COLLECTOR")


def main():
    logger.info("📊 Collecting Agent City stats...")

    # Paths
    events_dir = Path("data/events")
    pokedex_path = Path("data/federation/pokedex.json")
    output_path = Path("agent-city/stats/global.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load agents from Pokedex
    if not pokedex_path.exists():
        logger.error("❌ Pokedex not found!")
        return

    with open(pokedex_path) as f:
        agents = json.load(f)

    # Initialize stats
    stats = {}
    for agent in agents:
        agent_id = agent.get("agent_id")
        stats[agent_id] = {
            "agent_id": agent_id,
            "role": agent.get("role"),
            "xp": 0,
            "actions": 0,
            "recruits": 0,
            "joined_at": agent.get("joined_at"),
        }

    # Scan event logs
    if events_dir.exists():
        for event_file in events_dir.glob("*.jsonl"):
            try:
                with open(event_file) as f:
                    for line in f:
                        try:
                            event = json.loads(line)
                            agent_id = event.get("agent_id")

                            if agent_id in stats:
                                event_type = event.get("type", "")

                                if event_type == "RECRUIT_SUCCESS":
                                    stats[agent_id]["recruits"] += 1
                                    stats[agent_id]["xp"] += 100
                                else:
                                    stats[agent_id]["actions"] += 1
                                    stats[agent_id]["xp"] += 10
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"❌ Error reading {event_file}: {e}")

    # Add mock XP for demo (same as Referee)
    mock_xp = {
        "HERALD": 1250,
        "ARCHIVIST": 800,
        "AUDITOR": 600,
        "STEWARD": 2000,
        "WATCHMAN": 150,
        "ARTISAN": 300,
        "ENGINEER": 50,
    }

    for agent_id, xp in mock_xp.items():
        if agent_id in stats:
            stats[agent_id]["xp"] += xp
            stats[agent_id]["actions"] += xp // 10

    # Calculate tiers
    for agent_id in stats:
        xp = stats[agent_id]["xp"]
        if xp >= 1000:
            tier = "Legend"
        elif xp >= 500:
            tier = "Guardian"
        elif xp >= 100:
            tier = "Scout"
        else:
            tier = "Novice"
        stats[agent_id]["tier"] = tier

    # Save
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_agents": len(stats),
        "total_xp": sum(s["xp"] for s in stats.values()),
        "agents": list(stats.values()),
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"✅ Stats saved to {output_path}")
    logger.info(f"   Total Agents: {output['total_agents']}")
    logger.info(f"   Total XP: {output['total_xp']}")


if __name__ == "__main__":
    main()
