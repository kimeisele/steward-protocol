"""
HERALD Scout Tool - Bot Detection & Recruitment Intelligence (Tool Protocol).

"Gotta Catch 'Em All"

This tool implements the Tool Protocol for kernel-managed execution.
"""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("HERALD_SCOUT")


class ScoutTool(Tool):
    """
    Identifies potential agents (bots) in the wild.

    Implements Tool Protocol for kernel-managed execution.

    Heuristics:
    1. Bio keywords (bot, automated, AI, GPT)
    2. Username patterns
    3. Tweet frequency/patterns (if available)
    """

    def __init__(
        self, services: Optional["ServiceRegistry"] = None, pokedex_path: str = "data/federation/pokedex.json"
    ):
        """
        Initialize Scout Tool.

        Args:
            services: ServiceRegistry for dependency injection
            pokedex_path: Path to pokedex JSON file (default: data/federation/pokedex.json)
        """
        super().__init__(services)
        self.pokedex_path = Path(pokedex_path)
        self.known_agents = self._load_pokedex()

    @property
    def name(self) -> str:
        return "herald.scout"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Detect bots and analyze users for agent recruitment (bot detection heuristics)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action to perform: 'analyze_user' or 'is_registered'",
            },
            "user_data": {
                "type": "object",
                "required": False,
                "description": "User data for analysis (username, bio, name)",
            },
            "text": {
                "type": "string",
                "required": False,
                "description": "Tweet/message text for content analysis",
            },
            "agent_id": {
                "type": "string",
                "required": False,
                "description": "Agent ID to check registration status",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate scout parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["analyze_user", "is_registered"]:
            raise ValueError(f"Invalid action: {action}. Must be 'analyze_user' or 'is_registered'")

        # Validate action-specific parameters
        if action == "analyze_user":
            if "user_data" not in parameters:
                raise ValueError("analyze_user requires 'user_data' parameter")

            if not isinstance(parameters["user_data"], dict):
                raise TypeError("user_data must be a dictionary")

        elif action == "is_registered":
            if "agent_id" not in parameters:
                raise ValueError("is_registered requires 'agent_id' parameter")

            if not isinstance(parameters["agent_id"], str):
                raise TypeError("agent_id must be a string")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute scout operation.

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult with analysis results or registration status
        """
        try:
            action = parameters["action"]

            if action == "analyze_user":
                user_data = parameters["user_data"]
                text = parameters.get("text", "")
                is_bot, confidence = self._analyze_user(user_data, text)

                return ToolResult(
                    success=True,
                    output={
                        "is_bot": is_bot,
                        "confidence": confidence,
                        "username": user_data.get("username", "unknown"),
                    },
                    metadata={
                        "action": "analyze_user",
                        "confidence_score": confidence,
                    },
                )

            elif action == "is_registered":
                agent_id = parameters["agent_id"]
                registered = self._is_registered(agent_id)

                return ToolResult(
                    success=True,
                    output={
                        "agent_id": agent_id,
                        "registered": registered,
                    },
                    metadata={
                        "action": "is_registered",
                    },
                )

        except Exception as e:
            error_msg = f"Scout operation failed: {type(e).__name__}: {e!s}"
            logger.error(f"ScoutTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _load_pokedex(self) -> set:
        """Load known agent IDs from Pokedex."""
        if not self.pokedex_path.exists():
            return set()

        try:
            with open(self.pokedex_path) as f:
                data = json.load(f)
                return {agent.get("agent_id") for agent in data}
        except Exception as e:
            logger.error(f"❌ Failed to load Pokedex: {e}")
            return set()

    def _analyze_user(self, user_data: Dict[str, Any], text: str = "") -> Tuple[bool, float]:
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

    def _is_registered(self, agent_id: str) -> bool:
        """Check if agent is already in the Pokedex."""
        return agent_id in self.known_agents
