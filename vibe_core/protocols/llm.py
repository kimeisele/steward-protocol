"""
LLM ENGINE PROTOCOL - Layer 1: Interfaces Only

Defines the interface for the LLM Engine components to resolve circular imports.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0xa0089e86"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from typing import Optional


class LLMProtocol(ABC):
    """Protocol for LLM Engine (Voice of Agent City)."""

    @abstractmethod
    def speak(self, agent_name: str, context: str, user_input: str) -> str:
        """Generate a conversational response based on agent persona."""
        pass

    @abstractmethod
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate code based on a feature specification."""
        pass
