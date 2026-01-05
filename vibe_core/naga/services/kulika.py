"""
KULIKA SERVICE - Der Ordnungshüter.

Kulika - The 8th Naga Lord who maintains ORDER.
"Kula = Familie/Ordnung" - Without order, discovery is chaos.

PROMPT.md: "Kulika FIRST - You can't auto-discover without knowing what you're looking for."

Responsibilities:
- Validate NagaManifests against schema requirements
- Provide runtime API for service registration and lookup
- Single Source of Truth for service metadata
- Bridge between passive KulikaRegistry and active NAGA infrastructure

Integration:
- Does NOT register as CorrectionHandler (pure registry service)
- Narada DISCOVERS services, Kulika VALIDATES them
- All services MUST register with Kulika to be valid

Philosophy:
    "Ohne Gesetz gibt es keine Ordnung.
     Ohne Ordnung gibt es keine Entdeckung.
     Ohne Entdeckung gibt es keine Heilung."
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from vibe_core.naga.kulika import (
    KulikaRegistry,
    NagaCapability,
    NagaDomain,
    NagaLord,
    NagaManifest,
    get_kulika,
    naga_service,
)
from vibe_core.protocols.naga import (
    KulikaProtocol,
    NagaStatus,
    NagaType,
)

logger = logging.getLogger("KULIKA")


@naga_service(
    name="Kulika",
    lord=NagaLord.KULIKA,
    drift_source=None,  # Pure registry, no drift handling
    priority=100,  # Highest priority - must initialize first
    capabilities=[NagaCapability.SCHEMA],
    protocol_class="vibe_core.protocols.naga.KulikaProtocol",
)
class KulikaService(KulikaProtocol):
    """
    Kulika - The Schema Lord.

    Active service wrapper around the passive KulikaRegistry.
    Provides validation API and runtime service lookups.

    The 8th Naga Lord maintains ORDER so that Narada can DISCOVER.
    """

    def __init__(self, registry: Optional[KulikaRegistry] = None) -> None:
        """
        Initialize Kulika.

        Args:
            registry: Optional pre-existing registry. Uses singleton if None.
        """
        self._registry = registry if registry is not None else get_kulika()
        self._validation_count = 0
        self._registration_count = 0
        self._errors = 0
        self._last_heartbeat = datetime.now()

        logger.info("KULIKA initialized - Order established")

    @property
    def registry(self) -> KulikaRegistry:
        """Access the underlying registry."""
        return self._registry

    # =========================================================================
    # Validation API
    # =========================================================================

    def validate_manifest(self, manifest: Any) -> List[str]:
        """
        Validate a NagaManifest against schema requirements.

        Args:
            manifest: The manifest to validate (NagaManifest or dict)

        Returns:
            List of validation errors (empty = valid)
        """
        self._last_heartbeat = datetime.now()
        errors: List[str] = []

        try:
            # Handle dict input
            if isinstance(manifest, dict):
                manifest = NagaManifest.from_dict(manifest)

            if not isinstance(manifest, NagaManifest):
                errors.append(f"Invalid manifest type: {type(manifest).__name__}")
                self._errors += 1
                return errors

            # Required fields
            if not manifest.name:
                errors.append("Missing required field: name")

            if not manifest.lord:
                errors.append("Missing required field: lord")

            if not manifest.domain:
                errors.append("Missing required field: domain")

            # Validate lord matches domain
            if manifest.lord and manifest.domain:
                expected_domain = manifest.lord.domain
                if manifest.domain != expected_domain:
                    errors.append(
                        f"Domain mismatch: {manifest.lord.value} should be "
                        f"{expected_domain.value}, got {manifest.domain.value}"
                    )

            # Validate capabilities are appropriate for lord
            if manifest.capabilities and manifest.lord:
                if manifest.lord.is_infrastructure:
                    governance_only = [NagaCapability.AUDIT, NagaCapability.RESILIENCE]
                    for cap in manifest.capabilities:
                        if cap in governance_only:
                            errors.append(
                                f"Capability {cap.value} is governance-only, "
                                f"but {manifest.lord.value} is infrastructure"
                            )

            self._validation_count += 1

        except Exception as e:
            errors.append(f"Validation error: {e}")
            self._errors += 1

        return errors

    def validate_service(self, cls: Type) -> List[str]:
        """
        Validate a service class for NAGA compliance.

        Checks:
        - Has @naga_service decorator
        - Has required methods (get_status)
        - If has drift_source, has as_handler()

        Args:
            cls: The service class to validate

        Returns:
            List of validation errors (empty = valid)
        """
        self._last_heartbeat = datetime.now()

        # Delegate to registry's validate method
        errors = self._registry.validate(cls)

        # Additional checks
        if hasattr(cls, "_naga_manifest"):
            manifest: NagaManifest = cls._naga_manifest
            manifest_errors = self.validate_manifest(manifest)
            errors.extend(manifest_errors)

        self._validation_count += 1
        return errors

    # =========================================================================
    # Registration API
    # =========================================================================

    def register_service(self, cls: Type, instance: Optional[Any] = None) -> bool:
        """
        Register a NAGA service after validation.

        Args:
            cls: The service class (must have _naga_manifest)
            instance: Optional instance (if already created)

        Returns:
            True if registered successfully
        """
        self._last_heartbeat = datetime.now()

        # Validate first
        errors = self.validate_service(cls)
        if errors:
            logger.warning(f"KULIKA: Cannot register {cls.__name__}: {errors}")
            return False

        # Delegate registration
        success = self._registry.register(cls, instance)
        if success:
            self._registration_count += 1
            logger.debug(f"KULIKA: Registered {cls.__name__}")

        return success

    def unregister_service(self, name: str) -> bool:
        """
        Unregister a service by name.

        Args:
            name: The service name to unregister

        Returns:
            True if unregistered successfully
        """
        return self._registry.unregister(name)

    # =========================================================================
    # Query API
    # =========================================================================

    def get_service_class(self, name: str) -> Optional[Type]:
        """Get a registered service class by name."""
        return self._registry.get_class(name)

    def get_service_instance(self, name: str) -> Optional[Any]:
        """Get a registered service instance by name."""
        return self._registry.get_instance(name)

    def set_service_instance(self, name: str, instance: Any) -> None:
        """Set a service instance (for lazy init)."""
        self._registry.set_instance(name, instance)

    def get_manifest(self, name: str) -> Optional[NagaManifest]:
        """Get a manifest by service name."""
        return self._registry.get(name)

    def get_all_manifests(self) -> List[NagaManifest]:
        """Get all registered NagaManifests."""
        return self._registry.all_manifests()

    def get_all_names(self) -> List[str]:
        """Get all registered service names."""
        return self._registry.all_names()

    def get_services_by_capability(self, capability: str) -> List[NagaManifest]:
        """
        Get all services with a specific capability.

        Args:
            capability: The capability string (e.g., "ledger", "security")

        Returns:
            List of manifests for services with that capability
        """
        try:
            cap = NagaCapability(capability)
        except ValueError:
            return []

        result = []
        for manifest in self._registry.all_manifests():
            if cap in manifest.capabilities:
                result.append(manifest)
        return result

    def get_services_by_lord(self, lord: NagaLord) -> List[NagaManifest]:
        """Get all services of a specific lord type."""
        return self._registry.by_lord(lord)

    def get_services_by_domain(self, domain: NagaDomain) -> List[NagaManifest]:
        """Get all services in a domain (infrastructure/governance)."""
        return self._registry.by_domain(domain)

    def get_services_by_drift_source(self, drift_source: str) -> List[NagaManifest]:
        """Get all services handling a specific drift source."""
        return self._registry.by_drift_source(drift_source)

    def is_registered(self, name: str) -> bool:
        """Check if a service is registered."""
        return self._registry.is_registered(name)

    # =========================================================================
    # Status API
    # =========================================================================

    def get_registry_status(self) -> Dict[str, Any]:
        """Get detailed registry status."""
        return self._registry.get_status()

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        registry_status = self._registry.get_status()
        return NagaStatus(
            naga_type=NagaType.SESHA,  # Using SESHA as placeholder (no KULIKA in NagaType)
            healthy=True,
            last_heartbeat=self._last_heartbeat,
            events_processed=self._validation_count + self._registration_count,
            errors=self._errors,
            message=f"services={registry_status['total_services']}, validations={self._validation_count}",
            details=registry_status,
        )

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def clear(self) -> None:
        """Clear all registrations (for testing)."""
        self._registry.clear()
        self._validation_count = 0
        self._registration_count = 0
        self._errors = 0

    def __repr__(self) -> str:
        status = self._registry.get_status()
        return f"KulikaService(services={status['total_services']})"
