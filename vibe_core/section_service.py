"""
SectionService - OPUS-307 Phase E

Unified section management service.
Wraps SectionLoader into single source of truth.

GAD-000: Single service, accessed via ServiceRegistry.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x6352d515"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.protocols.section import SectionInfo, SectionServiceProtocol

logger = logging.getLogger("SECTION_SERVICE")


class SectionService(SectionServiceProtocol):
    """
    Unified section management.

    Features:
    - Lazy scanning
    - Single cache for all consumers
    - DI integration

    NOTE: Use get_section_service() to access via ServiceRegistry.
    """

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._sections: Dict[str, SectionInfo] = {}
        self._instances: Dict[str, Any] = {}
        self._scanned = False

    @classmethod
    def get_instance(cls, workspace: Optional[Path] = None) -> "SectionService":
        """Get singleton instance (backward compat - use get_section_service())."""
        return get_section_service(workspace)

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        from vibe_core.di import ServiceRegistry

        ServiceRegistry.unregister(SectionServiceProtocol)

    def scan(self, force: bool = False) -> int:
        """Scan for sections."""
        if self._scanned and not force:
            return len(self._sections)

        self._sections.clear()
        self._instances.clear()

        # Use SectionLoader for discovery
        from vibe_core.phoenix.section_loader import SectionLoader

        instances, metadata = SectionLoader.discover()

        for section_id, meta in metadata.items():
            info = SectionInfo(
                section_id=section_id,
                priority=meta.priority,
                path=meta.source_file if meta.source_file else Path("."),
                loaded_from_yaml=meta.loaded_from_yaml,
            )
            self._sections[section_id] = info

            # Cache the loaded instance
            if section_id in instances:
                self._instances[section_id] = instances[section_id]

        self._scanned = True
        logger.info(f"Scanned {len(self._sections)} sections")
        return len(self._sections)

    def get(self, section_id: str) -> Optional[SectionInfo]:
        """Get section info by ID."""
        if not self._scanned:
            self.scan()
        return self._sections.get(section_id)

    def list(self) -> List[SectionInfo]:
        """List all sections."""
        if not self._scanned:
            self.scan()
        return sorted(self._sections.values(), key=lambda s: s.priority)

    def load(self, section_id: str) -> Optional[Any]:
        """Load section instance."""
        if not self._scanned:
            self.scan()
        return self._instances.get(section_id)


# =============================================================================
# SERVICEREGISTRY FACTORY (NAGA-OBSERVED!)
# =============================================================================


def get_section_service(workspace: Optional[Path] = None) -> SectionService:
    """
    Get SectionService through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        SectionService → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees section operations)
    - NAGA profiling (Chitragupta tracks scan/load timing)
    - NAGA isolation (Kaliya handles section errors)

    Args:
        workspace: Optional workspace path (only used on first creation)

    Returns:
        SectionService wrapped with NagaProxy (if NAGA blessing enabled)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(SectionServiceProtocol)
    if existing is not None:
        return existing

    # Create new instance
    instance = SectionService(workspace)

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(SectionServiceProtocol, instance)
    logger.info("✅ SectionService registered via ServiceRegistry (NAGA-observed)")

    return ServiceRegistry.get(SectionServiceProtocol)  # type: ignore
