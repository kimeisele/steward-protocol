"""
Circuit Protocol - OPUS-307 Phase C

Single interface for circuit discovery and management.
Mirrors CartridgeProtocol/PluginServiceProtocol pattern.

GAD-000: One protocol, one service, via DI.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class CircuitInfo:
    """Circuit metadata."""

    circuit_id: str
    circuit_type: str  # "state_machine", "dag", "sequence"
    description: str
    version: str
    path: Path
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True


@runtime_checkable
class CircuitServiceProtocol(Protocol):
    """
    Protocol for circuit management.

    Single source of truth for:
    - Circuit discovery
    - Circuit loading
    - DI integration
    """

    def scan(self, force: bool = False) -> int:
        """
        Scan for circuits.

        Args:
            force: Force rescan

        Returns:
            Number of circuits found
        """
        ...

    def get(self, circuit_id: str) -> Optional[CircuitInfo]:
        """
        Get circuit info by ID.

        Args:
            circuit_id: Circuit identifier

        Returns:
            CircuitInfo or None
        """
        ...

    def list(self) -> List[CircuitInfo]:
        """
        List all discovered circuits.

        Returns:
            List of CircuitInfo
        """
        ...

    def load(self, circuit_id: str) -> Optional[Dict[str, Any]]:
        """
        Load circuit definition.

        Args:
            circuit_id: Circuit identifier

        Returns:
            Circuit definition dict or None
        """
        ...
