"""
ARCH-062: Heads-Up Display (HUD) & Discovery
=============================================

Provides rich visual feedback for system state, making the invisible visible.
The HUD transforms the "blank canvas" problem into a discoverable interface.

Components:
1. StatusBar - Visualizes current system state
2. CapabilitiesMenu - Shows available cartridges and features
3. HintSystem - Provides contextual guidance
"""

import json
import logging
from pathlib import Path
from typing import Any

from vibe_core.runtime.prompt_context import get_prompt_context

logger = logging.getLogger(__name__)


class StatusBar:
    """
    Renders the system status bar shown at startup.

    Design Philosophy:
    - Shows key system state at a glance
    - Makes settings discoverable (user sees "Tone: German Tech" → knows it can be changed)
    - No technical jargon; human-readable
    """

    def __init__(self, vibe_root: Path | None = None):
        """Initialize status bar renderer."""
        if vibe_root is None:
            vibe_root = Path.cwd()
        self.vibe_root = vibe_root
        self.steward_json = vibe_root / "steward.json"

    def get_user_name(self) -> str:
        """Get user name from steward.json or git config."""
        try:
            if self.steward_json.exists():
                with open(self.steward_json) as f:
                    config = json.load(f)
                    if "preferences" in config and "user_name" in config["preferences"]:
                        return config["preferences"]["user_name"]

            # Fallback to git config
            import subprocess

            try:
                result = subprocess.run(
                    ["git", "config", "user.name"],
                    cwd=self.vibe_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception:
                pass

            # Fallback to environment
            import os

            return os.environ.get("USER", "User")
        except Exception:
            return "User"

    def get_operator_tone(self) -> str:
        """Get operator tone from steward.json or environment variable."""
        try:
            if self.steward_json.exists():
                with open(self.steward_json) as f:
                    config = json.load(f)
                    if "preferences" in config and "operator_tone" in config["preferences"]:
                        return config["preferences"]["operator_tone"]
        except Exception:
            pass

        # ARCH-063: Check environment variable (VIBE_OPERATOR_TONE)
        import os
        env_tone = os.environ.get("VIBE_OPERATOR_TONE")
        if env_tone:
            return env_tone

        # Fallback to default
        return "Professional"

    def render(self) -> str:
        """
        Render the status bar.

        Returns:
            Formatted status bar string
        """
        # Get live context
        context_engine = get_prompt_context()
        context = context_engine.resolve(
            ["inbox_count", "agenda_summary", "git_sync_status", "system_time"]
        )

        inbox_count = context.get("inbox_count", "0")
        agenda_summary = json.loads(context.get("agenda_summary", '{"total": 0}'))
        git_sync = context.get("git_sync_status", "UNKNOWN")
        timestamp = context.get("system_time", "")

        # Get user preferences
        user_name = self.get_user_name()
        operator_tone = self.get_operator_tone()

        # Determine online status (simplified: if git sync is available, we have internet)
        online = "Yes" if git_sync != "UNKNOWN" else "No"

        # Build status bar
        status_bar = (
            f"🤖 VIBE OS v1.0.1 | 👤 User: {user_name} | 🎭 Tone: {operator_tone}\n"
            f"📡 Online: {online} | 📨 Inbox: {inbox_count} | 📋 Tasks: {agenda_summary.get('total', 0)}\n"
            f"{'─' * 70}\n"
        )

        return status_bar

    def render_compact(self) -> str:
        """Render a compact single-line status bar."""
        user_name = self.get_user_name()
        operator_tone = self.get_operator_tone()

        try:
            context_engine = get_prompt_context()
            context = context_engine.resolve(["inbox_count", "agenda_summary"])
            inbox_count = context.get("inbox_count", "0")
            agenda_summary = json.loads(context.get("agenda_summary", '{"total": 0}'))
            agenda_total = agenda_summary.get("total", 0)
        except Exception:
            inbox_count = "0"
            agenda_total = 0

        return (
            f"🤖 VIBE OS | {user_name} | 🎭 {operator_tone} "
            f"| 📨 {inbox_count} | 📋 {agenda_total}"
        )


class CapabilitiesMenu:
    """
    Shows available cartridges and what they do.

    When user asks "What can you do?" or "Help", this generates
    human-readable descriptions of installed cartridges.
    """

    # Hardcoded cartridge descriptions (can be extended)
    CARTRIDGES = {
        "steward": {
            "name": "Steward",
            "description": "Manage your configuration, API keys, and operator tone",
            "example": "Change my tone to 'German Technical'",
        },
        "studio": {
            "name": "Studio",
            "description": "Build software with Planning, Coding, and Testing specialists",
            "example": "Build a REST API for user authentication",
        },
        "archivist": {
            "name": "Archivist",
            "description": "Analyze documents, PDFs, and research topics",
            "example": "Analyze this PDF and summarize it",
        },
    }

    def render(self) -> str:
        """
        Render the capabilities menu.

        Returns:
            Formatted capabilities string
        """
        menu = "📖 WHAT YOU CAN DO:\n\n"

        for cartridge_id, info in self.CARTRIDGES.items():
            menu += f"**{info['name']}**\n"
            menu += f"  {info['description']}\n"
            menu += f"  Example: \"{info['example']}\"\n\n"

        return menu.strip()

    def get_cartridge_description(self, name: str) -> str | None:
        """Get description for a specific cartridge."""
        cart = self.CARTRIDGES.get(name.lower())
        if cart:
            return f"{cart['name']}: {cart['description']}"
        return None


class HintSystem:
    """
    Provides contextual hints to guide users.

    - If user input is very short (e.g., just "help"), suggest related actions
    - If no input for a while, offer hints
    - Based on system state (e.g., if tasks pending, suggest checking them)
    """

    GENERAL_HINTS = [
        "💡 You can ask: 'Change my tone to German Technical'",
        "💡 Type 'help' or 'capabilities' to see what you can do",
        "💡 Add tasks with: 'Add task: implement dark mode'",
        "💡 Check your inbox with: 'Show my inbox'",
    ]

    CONTEXT_HINTS = {
        "high_inbox": "You have unread messages! Ask: 'Show my inbox'",
        "high_tasks": "You have pending tasks. Ask: 'Show my agenda'",
        "behind_git": "Your code is out of sync. Consider: 'Sync with origin'",
        "no_api_key": "No API key configured. Try: 'Configure Google API key'",
    }

    @staticmethod
    def get_hint_for_input(user_input: str) -> str | None:
        """
        Get a hint based on user input.

        Args:
            user_input: What the user typed

        Returns:
            Hint string or None if not applicable
        """
        input_lower = user_input.lower().strip()

        # If asking for help
        if input_lower in ["help", "?", "what can i do", "capabilities", "menu"]:
            return "📋 Use the menu above to see available features, or ask naturally: 'Build an app', 'Change my settings', etc."

        # If input is very short and unclear
        if len(input_lower) < 3 and input_lower not in ["help", "exit", "quit", "q"]:
            return "💡 That's unclear. Try: 'Show my tasks', 'Build something', or 'Change my tone'"

        return None

    @staticmethod
    def get_contextual_hint() -> str | None:
        """
        Get a hint based on current system state.

        Returns:
            Hint string or None if no hint needed
        """
        try:
            context_engine = get_prompt_context()
            context = context_engine.resolve(
                ["inbox_count", "agenda_summary", "git_sync_status"]
            )

            inbox_count = int(context.get("inbox_count", "0"))
            agenda_summary = json.loads(context.get("agenda_summary", '{"total": 0}'))
            git_sync = context.get("git_sync_status", "UNKNOWN")

            # Check conditions
            if inbox_count > 0:
                return HintSystem.CONTEXT_HINTS["high_inbox"]
            if agenda_summary.get("total", 0) > 3:
                return HintSystem.CONTEXT_HINTS["high_tasks"]
            if git_sync.startswith("BEHIND_BY_"):
                return HintSystem.CONTEXT_HINTS["behind_git"]

        except Exception:
            pass

        return None

    @staticmethod
    def get_random_hint() -> str:
        """Get a random general hint."""
        import random

        return random.choice(HintSystem.GENERAL_HINTS)


__all__ = ["StatusBar", "CapabilitiesMenu", "HintSystem"]
