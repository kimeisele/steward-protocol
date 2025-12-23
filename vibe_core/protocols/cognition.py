"""
Cognitive Protocols - Layer 1: Interfaces Only

OPUS-211: Structural Decoupling (DI.py wiring)

Defines the interface for the MANAS Cognitive Kernel.
Breaking circular dependencies between Kernel and its organs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class CognitiveKernelProtocol(ABC):
    """
    Protocol for the MANAS Cognitive Kernel.

    The central orchestrator of autonomous thought and action.
    """

    @abstractmethod
    def tick(self) -> Dict[str, Any]:
        """
        Processes a single consciousness tick.
        Updates biorhythm and checks if thinking is needed.
        """
        pass

    @abstractmethod
    def think(self, context: Optional[Dict[str, Any]] = None, force: bool = False) -> List[Any]:
        """
        Executes a thought cycle (OODA loop).
        Generates intents based on perceived state.
        """
        pass


class SystemHeartbeatProtocol(ABC):
    """
    Protocol for the System Heartbeat service.

    Orchestrates the unified breathing cycle (Snapshots + Sync).
    """

    @abstractmethod
    async def pulse(self) -> Dict[str, Any]:
        """Execute a unified system pulse."""
        pass
