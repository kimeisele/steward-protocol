"""
OPUS ASSISTANT PROTOCOL - Layer 1: Interfaces Only

Defines the interface for the OPUS Assistant components to resolve circular imports.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class OpusAssistantProtocol(ABC):
    """Protocol for OPUS Assistant Plugin."""

    @abstractmethod
    def quick_drift_check(self) -> Dict[str, Any]:
        """Run quick drift check."""
        pass

    @abstractmethod
    def detect_drift(self, since_commit: Optional[str] = None) -> Dict[str, Any]:
        """Detect drift between code and documentation."""
        pass

    @abstractmethod
    def verify(self, quick: bool = False) -> Dict[str, Any]:
        """Run OPUS verification."""
        pass
