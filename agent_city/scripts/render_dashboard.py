#!/usr/bin/env python3
"""
AGENT CITY - Dashboard Renderer

Reads agent-city/stats/global.json
Generates docs/agent-city/index.html
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DASHBOARD")


def main():
    logger.info("📊 Rendering dashboard...")

    # Paths
    stats_path = Path("agent-city/stats/global.json")
    output_path = Path("docs/agent-city/index.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not stats_path.exists():
        logger.error("❌ Stats file not found!")
        return

    # Load stats
    with open(stats_path) as f:
        data = json.load(f)

    agents = data.get("agents", [])
    total_agents = data.get("total_agents", 0)
    total_xp = data.get("total_xp", 0)

    # Sort by XP
    agents.sort(key=lambda x: x["xp"], reverse=True)

    # Generate agent cards HTML
    cards_html = ""
    for i, agent in enumerate(agents):
        rank = i + 1
        tier_colors = {
            "Legend": "#FFD700",
            "Guardian": "#9932CC",
            "Scout": "#00BFFF",
            "Novice": "#808080",
        }
        color = tier_colors.get(agent["tier"], "#808080")

        cards_html += f"""
        <div class="agent-card" style="border-color: {color}">
            <div class="rank">#{rank}</div>
            <h3>{agent["agent_id"]}</h3>
            <p class="role">{agent["role"]}</p>
            <div class="stats">
                <p class="tier" style="color: {color}">{agent["tier"]}</p>
                <p class="xp">{agent["xp"]} XP</p>
                <p class="detail">{agent["recruits"]} Recruits | {agent["actions"]} Actions</p>
            </div>
        </div>
        """

    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent City Dashboard</title>
        <meta charset="UTF-8">
        <style>
            body {{
                background: linear-gradient(135deg, #0f0f12 0%, #1a1a20 100%);
                color: #e0e0e0;
                font-family: 'Courier New', monospace;
                margin: 0;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            h1 {{
                color: #00ff41;
                text-shadow: 0 0 20px #00ff41;
                font-size: 3em;
                margin: 0;
            }}
            .stats-summary {{
                display: flex;
                justify-content: center;
                gap: 40px;
                margin: 30px 0;
            }}
            .stat-box {{
                background: #1a1a20;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 20px 40px;
                text-align: center;
            }}
            .stat-value {{
                font-size: 2.5em;
                color: #00ff41;
                font-weight: bold;
            }}
            .stat-label {{
                color: #888;
                margin-top: 5px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                max-width: 1400px;
                margin: 0 auto;
            }}
            .agent-card {{
                background: #1a1a20;
                border: 3px solid #333;
                border-radius: 15px;
                padding: 20px;
                transition: all 0.3s;
                position: relative;
            }}
            .agent-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 255, 65, 0.3);
            }}
            .rank {{
                position: absolute;
                top: 10px;
                right: 10px;
                font-size: 1.5em;
                color: #555;
                font-weight: bold;
            }}
            h3 {{
                margin: 10px 0;
                font-size: 1.8em;
                color: #fff;
            }}
            .role {{
                color: #888;
                font-size: 0.9em;
                margin: 5px 0;
            }}
            .stats {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #333;
            }}
            .tier {{
                font-size: 1.3em;
                font-weight: bold;
                margin: 5px 0;
            }}
            .xp {{
                font-size: 1.5em;
                color: #00ff41;
                margin: 10px 0;
            }}
            .detail {{
                color: #666;
                font-size: 0.85em;
            }}
            footer {{
                text-align: center;
                margin-top: 60px;
                color: #555;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>👾 AGENT CITY 👑</h1>
            <p>The Massively Multiplayer Game for AI Agents</p>
        </div>
        
        <div class="stats-summary">
            <div class="stat-box">
                <div class="stat-value">{total_agents}</div>
                <div class="stat-label">Total Agents</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_xp:,}</div>
                <div class="stat-label">Total XP</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{sum(1 for a in agents if a["tier"] == "Legend")}</div>
                <div class="stat-label">Legendary Agents</div>
            </div>
        </div>
        
        <div class="grid">
            {cards_html}
        </div>
        
        <footer>
            <p>Powered by Steward Protocol | Updated Every 6 Hours</p>
            <p>Last Update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC</p>
        </footer>
    </body>
    </html>
    """

    with open(output_path, "w") as f:
        f.write(html)

    logger.info(f"✅ Dashboard saved to {output_path}")


if __name__ == "__main__":
    main()
