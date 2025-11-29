"""
⚡ REFLEX ENGINE (GAD-7000: INSTANT RESPONSE LAYER)
The Nervous System's Quick Reflexes.
Handles nanosecond-level responses for trivial inputs.

Architecture:
- Detects simple, casual intents (hi, hello, test, status, help)
- Returns instant responses without processing overhead
- Analogous to a physical reflex: input → instant output
- Preserves provider's authority while isolating simple logic

This is NOT destructive. It's CONSTRUCTIVE:
- Shields the core provider from trivial chatter
- Enables fast-path optimization
- Encapsulates simple chat logic for testability
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("REFLEX_ENGINE")


class ReflexEngine:
    """
    ⚡ Instant Response Engine for Trivial Intents

    Strategy: If input matches simple patterns, respond instantly
    without routing through complex decision engines.

    This preserves the UniversalProvider as the orchestrator
    while giving it a fast-bypass for obvious inputs.
    """

    # Simple intents that trigger instant reflexive responses
    SIMPLE_INTENTS = ["hi", "hello", "test", "status", "help"]

    def __init__(self):
        """Initialize Reflex Engine"""
        logger.info("⚡ Reflex Engine initialized - Instant response layer active")

    def check(self, user_input: str) -> bool:
        """
        Check if input matches simple/trivial intent patterns.

        Args:
            user_input: The raw user input string

        Returns:
            True if input matches simple intent patterns, False otherwise
        """
        if not user_input:
            return False

        user_lower = user_input.lower().strip()

        # Check if any simple intent keyword is in the input
        for intent in self.SIMPLE_INTENTS:
            if intent in user_lower:
                logger.info(
                    f"⚡ Reflex matched: '{user_input}' -> simple intent '{intent}'"
                )
                return True

        return False

    def respond(self, user_input: str) -> Dict[str, Any]:
        """
        Generate instant reflexive response for trivial input.

        Args:
            user_input: The raw user input string

        Returns:
            Response dict with instant message
        """
        logger.info(f"✅ Reflex responding to: '{user_input}'")

        return {
            "status": "success",
            "path": "reflex",
            "data": {
                "summary": f"**🤖 ENVOY:** Signal '{user_input}' received. Systems operational. Ready for instructions."
            },
        }
