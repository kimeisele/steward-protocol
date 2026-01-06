"""
KULIKA Protocol - Der Ordnungshüter (Schema Registry Protocol)

Kulika - Kula = Familie/Ordnung.
PROMPT.md: "Kulika FIRST - You can't auto-discover without knowing what you're looking for."

Responsibilities:
- Maintain schema definitions for all NAGA services
- Validate manifests against expected structure
- Provide runtime API for schema queries
- Single Source of Truth for service metadata

Integration:
- Narada DISCOVERS, Kulika VALIDATES
- All services MUST register with Kulika
"""

from typing import List, Optional, Protocol, runtime_checkable

# Import types for ANY-elimination
from vibe_core.protocols.agent import AgentManifest  # Existing type
from vibe_core.protocols.naga.types import ManifestDict, NagaStatus, NagaType


@runtime_checkable
class KulikaProtocol(Protocol):
    """
    Kulika - Der Ordnungshüter. Schema Registry.

    Usage:
        kulika = ServiceRegistry.get(KulikaProtocol)
        errors = kulika.validate_manifest(manifest)
        service_class = kulika.get_service_class("sesha")
    """

    def validate_manifest(self, manifest: AgentManifest) -> List[str]:
        """Validate a NagaManifest against schema requirements."""
        ...

    def validate_service(self, cls: type) -> List[str]:
        """Validate a service class for NAGA compliance."""
        ...

    def register_service(self, cls: type, instance: Optional[object] = None) -> bool:
        """Register a NAGA service."""
        ...

    def get_service_class(self, name: str) -> Optional[type]:
        """Get a registered service class by name."""
        ...

    def get_service_instance(self, name: str) -> Optional[object]:
        """Get a registered service instance by name."""
        ...

    def get_all_manifests(self) -> List[ManifestDict]:
        """Get all registered NagaManifests."""
        ...

    def get_services_by_capability(self, capability: str) -> List[object]:
        """Get all services with a specific capability."""
        ...

    def is_registered(self, name: str) -> bool:
        """Check if a service is registered."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullKulika:
    """No-op Kulika for when schema registry is unavailable."""

    def validate_manifest(self, manifest: AgentManifest) -> List[str]:
        return ["Kulika not available"]

    def validate_service(self, cls: type) -> List[str]:
        return ["Kulika not available"]

    def register_service(self, cls: type, instance: Optional[object] = None) -> bool:
        return False

    def get_service_class(self, name: str) -> Optional[type]:
        return None

    def get_service_instance(self, name: str) -> Optional[object]:
        return None

    def get_all_manifests(self) -> List[ManifestDict]:
        return []

    def get_services_by_capability(self, capability: str) -> List[object]:
        return []

    def is_registered(self, name: str) -> bool:
        return False

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Not initialized")