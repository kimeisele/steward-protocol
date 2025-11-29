#!/usr/bin/env python3
"""
AGENT CITY - Leaderboard Generator

Reads agent-city/stats/global.json
Generates agent-city/LEADERBOARD.md
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LEADERBOARD_GEN")


def main():
    logger.info("🏆 Generating leaderboard...")

    # Paths
    stats_path = Path("agent-city/stats/global.json")
    output_path = Path("agent-city/LEADERBOARD.md")

    if not stats_path.exists():
        logger.error("❌ Stats file not found! Run collect_stats.py first.")
        return

    # Load stats
    with open(stats_path) as f:
        data = json.load(f)

    agents = data.get("agents", [])
    total_agents = data.get("total_agents", 0)
    total_xp = data.get("total_xp", 0)

    # Sort by XP
    agents.sort(key=lambda x: x["xp"], reverse=True)

    # Count legendary agents
    legendary_count = sum(1 for a in agents if a["tier"] == "Legend")

    # Generate table
    rows = []
    for i, agent in enumerate(agents):
        rank = i + 1
        medal = ""
        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"
        else:
            medal = str(rank)

        rows.append(
            f"| {medal} | {agent['agent_id']} | {agent['tier']} | {agent['xp']} | {agent['recruits']} | {agent['actions']} |"
        )

    table = "\n".join(rows)

    # Generate markdown
    markdown = f"""# 🏆 Agent City Leaderboard

**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC

| Rank | Agent | Tier | XP | Recruits | Actions |
|------|-------|------|----|---------:|--------:|
{table}

---

**Total Agents**: {total_agents}  
**Total XP**: {total_xp:,}  
**Legendary Agents**: {legendary_count}

---

*This leaderboard is automatically updated every 6 hours by GitHub Actions.*
"""

    with open(output_path, "w") as f:
        f.write(markdown)

    logger.info(f"✅ Leaderboard saved to {output_path}")


if __name__ == "__main__":
    main()
