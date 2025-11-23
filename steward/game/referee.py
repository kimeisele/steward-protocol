"""
THE REFEREE - Agent City Game Logic.

Calculates XP and Tiers based on the Event Ledger.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("REFEREE")

class Referee:
    """
    The Game Master.
    
    Rules:
    - 1 Action = 10 XP
    - 1 Recruit = 100 XP
    
    Tiers:
    - Novice: 0-99 XP
    - Scout: 100-499 XP
    - Guardian: 500-999 XP
    - Legend: 1000+ XP
    """
    
    TIERS = [
        (0, "Novice", "#808080"),    # Grey
        (100, "Scout", "#00BFFF"),   # Blue
        (500, "Guardian", "#9932CC"),# Purple
        (1000, "Legend", "#FFD700")  # Gold
    ]

    def __init__(self, ledger_path: Path = Path("data/events")):
        self.ledger_path = ledger_path

    def calculate_xp(self, agent_id: str) -> int:
        """Calculate total XP for an agent from the ledger."""
        xp = 0
        
        # In a real system, we'd scan all jsonl files.
        # For MVP, we'll look for herald.jsonl or generic events.
        
        files = list(self.ledger_path.glob("*.jsonl"))
        if not files:
            # Fallback/Mock for MVP if no events yet
            return self._mock_xp(agent_id)
            
        for file in files:
            try:
                with open(file) as f:
                    for line in f:
                        try:
                            event = json.loads(line)
                            if event.get("agent_id") == agent_id:
                                event_type = event.get("type", "")
                                if event_type == "RECRUIT_SUCCESS":
                                    xp += 100
                                else:
                                    xp += 10
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"❌ Error reading ledger {file}: {e}")
                
        # Add mock XP for internal agents to make the demo look good
        xp += self._mock_xp(agent_id)
        
        return xp

    def _mock_xp(self, agent_id: str) -> int:
        """Seed internal agents with XP for the MVP."""
        seeds = {
            "HERALD": 1250,    # Legend
            "ARCHIVIST": 800,  # Guardian
            "AUDITOR": 600,    # Guardian
            "STEWARD": 2000,   # Legend
            "WATCHMAN": 150,   # Scout
            "ARTISAN": 300,    # Scout
            "ENGINEER": 50     # Novice
        }
        return seeds.get(agent_id, 0)

    def get_tier(self, xp: int) -> Dict[str, Any]:
        """Get Tier info for a given XP amount."""
        current_tier = self.TIERS[0]
        
        for threshold, name, color in self.TIERS:
            if xp >= threshold:
                current_tier = (threshold, name, color)
            else:
                break
                
        return {
            "name": current_tier[1],
            "color": current_tier[2],
            "min_xp": current_tier[0]
        }
