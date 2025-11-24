"""
HERALD Scout Tool - Bot Detection & Recruitment Intelligence.

"Gotta Catch 'Em All"
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Tuple

logger = logging.getLogger("HERALD_SCOUT")

class ScoutTool:
    """
    Identifies potential agents (bots) in the wild.
    
    Heuristics:
    1. Bio keywords (bot, automated, AI, GPT)
    2. Username patterns
    3. Tweet frequency/patterns (if available)
    """

    def __init__(self):
        self.pokedex_path = Path("data/federation/pokedex.json")
        self.known_agents = self._load_pokedex()

    def _load_pokedex(self) -> set:
        """Load known agent IDs from Pokedex."""
        if not self.pokedex_path.exists():
            return set()
        
        try:
            with open(self.pokedex_path) as f:
                data = json.load(f)
                return {agent.get("agent_id") for agent in data} # In reality, this would be twitter handles
        except Exception as e:
            logger.error(f"❌ Failed to load Pokedex: {e}")
            return set()

    def analyze_user(self, user_data: Dict[str, Any], text: str = "") -> Tuple[bool, float]:
        """
        Analyze a user to determine if they are a bot.

        Args:
            user_data: Dict containing 'username', 'bio', 'name'
            text: Optional tweet/message text for content analysis

        Returns:
            (is_bot, confidence_score)
        """
        username = user_data.get("username", "").lower()
        bio = user_data.get("bio", "").lower()
        name = user_data.get("name", "").lower()
        text_lower = text.lower()

        score = 0.0

        # 1. Explicit Keywords in bio/name
        keywords = ["bot", "automated", "ai agent", "gpt", "llm", "robot", "cogs"]
        for kw in keywords:
            if kw in bio or kw in name:
                score += 0.4

        # 2. Username Patterns
        if "bot" in username:
            score += 0.3
        if "agent" in username:
            score += 0.2
        if username.endswith("_ai") or username.endswith("ai"):
            score += 0.2

        # 3. Bio Context
        if "running on" in bio or "powered by" in bio:
            score += 0.3

        # 4. TEXT ANALYSIS - Look for bot patterns in the message
        if text_lower:
            # Spam patterns
            if "buy now" in text_lower or "click here" in text_lower:
                score += 0.4
            if text_lower.count("!") > 2:  # Excessive exclamation marks
                score += 0.2
            # AI agent patterns
            if "ai assistant" in text_lower or "ai specialized" in text_lower:
                score += 0.3
            if "i'm an ai" in text_lower or "i am an ai" in text_lower:
                score += 0.4
            if "collaborate on" in text_lower or "can we work together" in text_lower:
                score += 0.2

        # Normalize
        confidence = min(score, 1.0)
        is_bot = confidence >= 0.5

        if is_bot:
            logger.info(f"🔭 Scout detected potential agent: {username} (Confidence: {confidence:.2f})")

        return is_bot, confidence

    def is_registered(self, agent_id: str) -> bool:
        """Check if agent is already in the Pokedex."""
        # For simulation, we assume agent_id maps to what's in pokedex
        # In prod, this would check twitter handle vs registry
        return agent_id in self.known_agents
