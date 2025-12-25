"""
CircuitService - OPUS-307 Phase C

Unified circuit management service.
Wraps CircuitLoader into single source of truth.

GAD-000: Single service, accessed via ServiceRegistry.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.protocols.circuit import CircuitInfo, CircuitServiceProtocol

logger = logging.getLogger("CIRCUIT_SERVICE")


class CircuitService(CircuitServiceProtocol):
    """
    Unified circuit management.

    Features:
    - Lazy scanning
    - Single cache for all consumers
    - DI integration
    """

    _instance: Optional["CircuitService"] = None

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._circuits: Dict[str, CircuitInfo] = {}
        self._definitions: Dict[str, Dict[str, Any]] = {}
        self._scanned = False

    @classmethod
    def get_instance(cls, workspace: Optional[Path] = None) -> "CircuitService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(workspace)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    def scan(self, force: bool = False) -> int:
        """Scan for circuits."""
        if self._scanned and not force:
            return len(self._circuits)

        self._circuits.clear()
        self._definitions.clear()

        # Use CircuitLoader for discovery
        from vibe_core.loaders.circuit_loader import CircuitLoader

        circuits, metadata = CircuitLoader.discover_and_load(force_refresh=force)

        for circuit_id, meta in metadata.items():
            if not meta.loaded_successfully:
                continue

            info = CircuitInfo(
                circuit_id=circuit_id,
                circuit_type=meta.circuit_type,
                description=meta.description,
                version=meta.version,
                path=meta.file_path,
                triggers=meta.triggers,
                enabled=True,
            )

            self._circuits[circuit_id] = info
            self._definitions[circuit_id] = meta.definition

        self._scanned = True
        logger.info(f"Scanned {len(self._circuits)} circuits")
        return len(self._circuits)

    def get(self, circuit_id: str) -> Optional[CircuitInfo]:
        """Get circuit info by ID."""
        if not self._scanned:
            self.scan()
        return self._circuits.get(circuit_id)

    def list(self) -> List[CircuitInfo]:
        """List all circuits."""
        if not self._scanned:
            self.scan()
        return list(self._circuits.values())

    def load(self, circuit_id: str) -> Optional[Dict[str, Any]]:
        """Load circuit definition."""
        if not self._scanned:
            self.scan()
        return self._definitions.get(circuit_id)
