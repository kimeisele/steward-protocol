"""
Section Protocol - OPUS-307 Phase E

Single interface for Phoenix section discovery and management.
Mirrors CartridgeProtocol pattern.

GAD-000: One protocol, one service, via DI.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class SectionInfo:
    """Section metadata."""

    section_id: str
    priority: int
    path: Path
    loaded_from_yaml: bool = False


@runtime_checkable
class SectionServiceProtocol(Protocol):
    """
    Protocol for section management.

    Single source of truth for:
    - Section discovery
    - Section loading
    - DI integration
    """

    def scan(self, force: bool = False) -> int:
        """
        Scan for sections.

        Args:
            force: Force rescan

        Returns:
            Number of sections found
        """
        ...

    def get(self, section_id: str) -> Optional[SectionInfo]:
        """
        Get section info by ID.

        Args:
            section_id: Section identifier

        Returns:
            SectionInfo or None
        """
        ...

    def list(self) -> List[SectionInfo]:
        """
        List all discovered sections.

        Returns:
            List of SectionInfo
        """
        ...

    def load(self, section_id: str) -> Optional[Any]:
        """
        Load section instance.

        Args:
            section_id: Section identifier

        Returns:
            Section instance or None
        """
        ...
