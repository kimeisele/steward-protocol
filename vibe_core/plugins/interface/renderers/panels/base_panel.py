"""
Base Panel - Abstract base class for OPUS panels.

All panels extend this and implement:
- panel_id: unique identifier
- priority: render order (lower = first)
- render(): returns markdown content
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class OpusPanel(ABC):
    """Abstract base class for OPUS dashboard panels."""

    @property
    @abstractmethod
    def panel_id(self) -> str:
        """Unique panel identifier."""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """Render priority (lower = rendered first)."""
        pass

    @abstractmethod
    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Render panel content as markdown.

        Args:
            config: Panel configuration
            context: Runtime context (kernel, etc.)

        Returns:
            Markdown string
        """
        pass
