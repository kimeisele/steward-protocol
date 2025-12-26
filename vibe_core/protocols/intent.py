"""
OPUS-310 Phase 4: Intent Matching Protocol

GAD-000: AI operates the system on behalf of human.
PROMPT.md: "Protocol statt konkrete Klassen"

Matches natural language intent to available commands.
No hardcoding. Everything via CommandRegistry.

Usage:
    matcher: IntentMatcherProtocol = CommandAwareIntentMatcher()
    matches = matcher.match("show all agents", commands)
    if matches[0].confidence > 0.8:
        execute(matches[0].command)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from vibe_core.protocols.command import CommandInfo


@dataclass
class IntentMatch:
    """
    Result of intent matching.

    Represents a potential match between natural language
    and a registered command.
    """

    command: CommandInfo  # The matched command
    confidence: float  # 0.0 - 1.0 (higher = more certain)
    extracted_params: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""  # Why this match was chosen (for debugging/transparency)

    def __post_init__(self):
        # Clamp confidence to valid range
        self.confidence = max(0.0, min(1.0, self.confidence))


@runtime_checkable
class IntentMatcherProtocol(Protocol):
    """
    OPUS-310 Phase 4: Intent-to-Command Matching.

    GAD-000: AI operates the system on behalf of human.

    Matches natural language intent to available commands.
    No hardcoding. Everything via CommandRegistry.

    The fractal property:
    - Core commands can be matched
    - Plugin commands can be matched
    - Cartridge commands can be matched
    - Holon commands can be matched

    Same interface, same power, everywhere.
    """

    def match(self, intent: str, commands: List[CommandInfo]) -> List[IntentMatch]:
        """
        Match intent to commands.

        Args:
            intent: Natural language intent from user
            commands: Available commands from CommandRegistry

        Returns:
            Ranked list of matches with confidence scores.
            Sorted by confidence (highest first).
            Empty list if no matches found.
        """
        ...

    def extract_params(self, intent: str, command: CommandInfo) -> Dict[str, Any]:
        """
        Extract parameters from natural language.

        Args:
            intent: Natural language intent
            command: The matched command

        Returns:
            Dict of parameter name -> extracted value

        Example:
            intent: "show agent status for worker-1"
            command: agents.status (params: agent_id)
            returns: {"agent_id": "worker-1"}
        """
        ...


class NullIntentMatcher:
    """
    Arjuna-Pattern: Null implementation for graceful degradation.

    Returns no matches. System falls back to chat.
    """

    def match(self, intent: str, commands: List[CommandInfo]) -> List[IntentMatch]:
        return []

    def extract_params(self, intent: str, command: CommandInfo) -> Dict[str, Any]:
        return {}
