"""
CircuitService - OPUS-307 Phase C

Unified circuit management service.
Wraps CircuitLoader into single source of truth.

GAD-000: Single service, accessed via ServiceRegistry.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x690e400f"  # GenesisByte: parampara % 37 == 0

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

    NOTE: Use get_circuit_service() to access via ServiceRegistry.
    """

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._circuits: Dict[str, CircuitInfo] = {}
        self._definitions: Dict[str, Dict[str, Any]] = {}
        self._scanned = False

    @classmethod
    def get_instance(cls, workspace: Optional[Path] = None) -> "CircuitService":
        """Get singleton instance (backward compat - use get_circuit_service())."""
        return get_circuit_service(workspace)

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        from vibe_core.di import ServiceRegistry

        ServiceRegistry.unregister(CircuitServiceProtocol)

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


# =============================================================================
# SERVICEREGISTRY FACTORY (NAGA-OBSERVED!)
# =============================================================================


def get_circuit_service(workspace: Optional[Path] = None) -> CircuitService:
    """
    Get CircuitService through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        CircuitService → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees circuit operations)
    - NAGA profiling (Chitragupta tracks scan/load timing)
    - NAGA isolation (Kaliya handles circuit errors)

    Args:
        workspace: Optional workspace path (only used on first creation)

    Returns:
        CircuitService wrapped with NagaProxy (if NAGA blessing enabled)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(CircuitServiceProtocol)
    if existing is not None:
        return existing

    # Create new instance
    instance = CircuitService(workspace)

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(CircuitServiceProtocol, instance)
    logger.info("✅ CircuitService registered via ServiceRegistry (NAGA-observed)")

    return ServiceRegistry.get(CircuitServiceProtocol)  # type: ignore
