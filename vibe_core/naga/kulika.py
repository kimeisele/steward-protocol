"""
KULIKA - The Schema Registry (SB 5.24.31)

"Kulika (Kula = Familie/Ordnung) definiert, WAS ein valider Naga ist."

Kulika ist der 8. Naga Lord. Er wacht über die Ordnung.
Ohne Kulika (Schema) ist Narada (Discovery) nur Chaos.

Architecture:
    KULIKA FIRST - You can't auto-discover without knowing what you're looking for.

    1. NagaManifest: What every NAGA must DECLARE
    2. NagaServiceProtocol: What every NAGA must IMPLEMENT
    3. KulikaRegistry: The single source of truth for NAGA schemas

The 8 Naga Lords (from SB 5.24.31):
    INFRASTRUCTURE (Real Nagas):
        1. SESHA     - Truth/Ledger (Gravity)
        2. VASUKI    - Network/API (Binding)
        3. TAKSHAKA  - Security/Firewall (Venom)
        4. KALIYA    - Quarantine/Isolation (Toxic)
        5. KARKOTAKA - Crypto/Obfuscation (Magic)
        6. PADMA     - Cache/Treasury (Gold)
        7. SHANKHA   - Flooding/Broadcast (Sound)
        8. KULIKA    - Schema/Registry (Order)

    GOVERNANCE (Personnel - NOT Nagas by race):
        - NARADA      - Event Bus/Injector
        - CHITRAGUPTA - Auditor/Profiler
        - PRAHLAD     - Governor/Resilience
        - ANANTA      - Gene Splicer/Auto-Flood

Usage:
    from vibe_core.naga.kulika import naga_service, NagaDomain, NagaLord

    @naga_service(
        name="Sesha",
        lord=NagaLord.SESHA,
        domain=NagaDomain.INFRASTRUCTURE,
        drift_source=DriftSource.STATE,
    )
    class SeshaService:
        ...
"""

import inspect
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, Type, runtime_checkable

logger = logging.getLogger("NAGA.KULIKA")

# Excluded method prefixes - pure getters and status methods don't need governance
# Note: as_handler methods ARE governed (they perform corrections)
_EXCLUDED_PREFIXES = ("get_", "is_", "has_", "list_", "can_", "should_")
_EXCLUDED_NAMES = {"status", "health", "info", "capabilities", "metadata", "to_dict", "from_dict"}


# =============================================================================
# ENUMS - The Categories of Order
# =============================================================================


class NagaDomain(str, Enum):
    """
    The two domains of the NAGA Service Agency.

    INFRASTRUCTURE: Real Nagas (serpents) - Data Plane
    GOVERNANCE: Personnel (Devas/Rishis) - Control Plane
    """

    INFRASTRUCTURE = "infrastructure"  # Sesha, Vasuki, Takshaka, Kaliya, etc.
    GOVERNANCE = "governance"  # Narada, Chitragupta, Prahlad


class NagaLord(str, Enum):
    """
    The 8 Naga Lords + 3 Governance Personnel.

    From SB 5.24.31:
    "The chief among them are Vasuki, Shankha, Kulika, Mahashankha,
     Shveta, Dhananjaya, Dhritarashtra, Shankhachuda, Kambala,
     Ashvatara and Devadatta."

    We use the 8 most architecturally relevant.
    """

    # Infrastructure Layer (Real Nagas)
    SESHA = "sesha"  # Truth/Ledger - Gravity
    VASUKI = "vasuki"  # Network/API - Binding
    TAKSHAKA = "takshaka"  # Security/Firewall - Venom
    KALIYA = "kaliya"  # Quarantine/Isolation - Toxic
    KARKOTAKA = "karkotaka"  # Crypto/Obfuscation - Magic
    PADMA = "padma"  # Cache/Treasury - Gold
    SHANKHA = "shankha"  # Flooding/Broadcast - Sound
    KULIKA = "kulika"  # Schema/Registry - Order

    # Governance Layer (Personnel)
    NARADA = "narada"  # Event Bus/Injector
    CHITRAGUPTA = "chitragupta"  # Auditor/Profiler
    PRAHLAD = "prahlad"  # Governor/Resilience
    ANANTA = "ananta"  # Gene Splicer/Auto-Flood

    @property
    def is_infrastructure(self) -> bool:
        """Is this a real Naga (serpent)?"""
        return self in (
            NagaLord.SESHA,
            NagaLord.VASUKI,
            NagaLord.TAKSHAKA,
            NagaLord.KALIYA,
            NagaLord.KARKOTAKA,
            NagaLord.PADMA,
            NagaLord.SHANKHA,
            NagaLord.KULIKA,
        )

    @property
    def is_governance(self) -> bool:
        """Is this a governance personnel?"""
        return self in (
            NagaLord.NARADA,
            NagaLord.CHITRAGUPTA,
            NagaLord.PRAHLAD,
            NagaLord.ANANTA,
        )

    @property
    def domain(self) -> NagaDomain:
        """Get the domain for this lord."""
        if self.is_infrastructure:
            return NagaDomain.INFRASTRUCTURE
        return NagaDomain.GOVERNANCE


class NagaCapability(str, Enum):
    """
    Capabilities a NAGA service can declare.

    Used by Narada for routing and by Prahlad for audit.
    """

    # Core capabilities
    LEDGER = "ledger"  # Can read/write to ledger
    NETWORK = "network"  # Can communicate externally
    SECURITY = "security"  # Can enforce security policies
    ISOLATION = "isolation"  # Can quarantine components
    CRYPTO = "crypto"  # Can encrypt/decrypt
    CACHE = "cache"  # Can cache state
    BROADCAST = "broadcast"  # Can flood/broadcast
    SCHEMA = "schema"  # Can validate schemas

    # Governance capabilities
    OBSERVATION = "observation"  # Can observe without modifying
    PROFILING = "profiling"  # Can profile behavior
    AUDIT = "audit"  # Can audit compliance
    RESILIENCE = "resilience"  # Can test/harden
    FLOOD = "flood"  # Can inject DNA/Mixins (Soft Flood)


# =============================================================================
# NAGA MANIFEST - What every NAGA must DECLARE
# =============================================================================


@dataclass
class NagaManifest:
    """
    The manifest that every NAGA service must declare.

    This is set by the @naga_service decorator and read by Narada.

    Philosophy:
        "A NAGA without a manifest is an orphan.
         An orphan cannot be discovered, cannot be healed,
         cannot participate in the Agency."
    """

    # Identity (required)
    name: str  # Human-readable name: "Sesha"
    lord: NagaLord  # Which lord type: NagaLord.SESHA
    domain: NagaDomain  # Which domain: NagaDomain.INFRASTRUCTURE

    # Correction (optional)
    drift_source: Optional[str] = None  # DriftSource this NAGA handles
    priority: int = 50  # CorrectionHandler priority (0-100)

    # Capabilities (optional)
    capabilities: List[NagaCapability] = field(default_factory=list)

    # Protocol (optional)
    protocol_class: Optional[str] = None  # Full path to Protocol class

    # Manifestation (optional)
    output_file: Optional[str] = None  # e.g., "NAGASERVICE.md"
    schema: str = "naga_standard"  # Manifestation schema

    # Metadata
    version: str = "1.0"
    registered_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for JSON/YAML."""
        return {
            "name": self.name,
            "lord": self.lord.value,
            "domain": self.domain.value,
            "drift_source": self.drift_source,
            "priority": self.priority,
            "capabilities": [c.value for c in self.capabilities],
            "protocol_class": self.protocol_class,
            "output_file": self.output_file,
            "schema": self.schema,
            "version": self.version,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NagaManifest":
        """Deserialize from dict."""
        return cls(
            name=data["name"],
            lord=NagaLord(data["lord"]),
            domain=NagaDomain(data["domain"]),
            drift_source=data.get("drift_source"),
            priority=data.get("priority", 50),
            capabilities=[NagaCapability(c) for c in data.get("capabilities", [])],
            protocol_class=data.get("protocol_class"),
            output_file=data.get("output_file"),
            schema=data.get("schema", "naga_standard"),
            version=data.get("version", "1.0"),
            registered_at=datetime.fromisoformat(data["registered_at"]) if data.get("registered_at") else None,
        )


# =============================================================================
# NAGA SERVICE PROTOCOL - What every NAGA must IMPLEMENT
# =============================================================================


@runtime_checkable
class NagaServiceProtocol(Protocol):
    """
    The minimum interface every NAGA service must implement.

    This is what Kulika checks for validation.
    This is what Narada uses for discovery.

    Philosophy:
        "If it walks like a Naga and bites like a Naga,
         it must implement NagaServiceProtocol."
    """

    # Identity (required)
    _naga_manifest: NagaManifest

    def get_status(self) -> Any:
        """Get the current status of this NAGA."""
        ...

    def get_manifest(self) -> NagaManifest:
        """Get the NAGA manifest."""
        ...


# =============================================================================
# THE @naga_service DECORATOR
# =============================================================================


def naga_service(
    name: str,
    lord: NagaLord,
    domain: Optional[NagaDomain] = None,
    drift_source: Optional[str] = None,
    priority: int = 50,
    capabilities: Optional[List[NagaCapability]] = None,
    protocol_class: Optional[str] = None,
    output_file: Optional[str] = None,
    schema: str = "naga_standard",
    version: str = "1.0",
    auto_govern: bool = True,
) -> Callable[[Type], Type]:
    """
    Mark a class as a NAGA service with ANANTA auto-governance.

    ANANTA PATTERN (SB 5.24.31): Automatic governance by default.
    All public methods are wrapped with @naga_governed unless:
    - Method starts with _ (private)
    - Method is a pure getter (get_, is_, has_, list_, can_, should_)
    - Method has @ungoverned decorator
    - Method is already @naga_governed

    This is the signal for Narada (Scanner) to discover this service.

    Usage:
        @naga_service(
            name="Sesha",
            lord=NagaLord.SESHA,
            drift_source="state",
            capabilities=[NagaCapability.LEDGER],
        )
        class SeshaService:
            def export_blocks(self):  # Auto-wrapped
                ...

            @ungoverned
            def get_cached_value(self):  # Not wrapped
                ...

    Args:
        name: Human-readable name
        lord: Which Naga Lord type
        domain: INFRASTRUCTURE or GOVERNANCE (auto-detected from lord)
        drift_source: DriftSource this NAGA handles (as string)
        priority: CorrectionHandler priority (0-100)
        capabilities: List of capabilities
        protocol_class: Full path to Protocol class
        output_file: Manifestation output file
        schema: Manifestation schema
        version: Service version
        auto_govern: Enable ANANTA auto-governance (default: True)

    Returns:
        Decorated class with _naga_manifest attribute and governed methods
    """

    def decorator(cls: Type) -> Type:
        # Auto-detect domain from lord
        actual_domain = domain if domain else lord.domain

        # Build manifest
        manifest = NagaManifest(
            name=name,
            lord=lord,
            domain=actual_domain,
            drift_source=drift_source,
            priority=priority,
            capabilities=capabilities or [],
            protocol_class=protocol_class,
            output_file=output_file,
            schema=schema,
            version=version,
        )

        # Attach to class
        cls._naga_manifest = manifest

        # Add get_manifest method if not present
        if not hasattr(cls, "get_manifest"):

            def get_manifest(self) -> NagaManifest:
                return self._naga_manifest

            cls.get_manifest = get_manifest

        # =====================================================================
        # ANANTA AUTO-GOVERNANCE: Wrap all public methods with @naga_governed
        # =====================================================================
        if auto_govern:
            # Late import to avoid circular dependency
            from vibe_core.naga.services.base import naga_governed

            wrapped_count = 0

            # Get all attributes defined directly on this class
            for attr_name in list(cls.__dict__.keys()):
                # Skip private methods
                if attr_name.startswith("_"):
                    continue

                # Skip excluded names
                if attr_name in _EXCLUDED_NAMES:
                    continue

                # Skip pure getters
                if any(attr_name.startswith(prefix) for prefix in _EXCLUDED_PREFIXES):
                    continue

                attr_value = cls.__dict__[attr_name]

                # Skip non-callables (properties, class attributes)
                if not callable(attr_value):
                    continue

                # Skip class methods and static methods
                if isinstance(attr_value, (classmethod, staticmethod)):
                    continue

                # Skip already governed methods (has __wrapped__ from functools.wraps)
                if hasattr(attr_value, "__wrapped__"):
                    continue

                # Skip methods explicitly marked as governed
                if getattr(attr_value, "_is_naga_governed", False):
                    continue

                # Skip methods marked with @ungoverned
                if getattr(attr_value, "_is_ungoverned", False):
                    continue

                # Skip property descriptors
                if isinstance(inspect.getattr_static(cls, attr_name, None), property):
                    continue

                # THE CHURNING: Wrap with @naga_governed
                governed_method = naga_governed(operation=f"{name}.{attr_name}")(attr_value)
                governed_method._is_naga_governed = True  # Mark to prevent re-wrapping
                setattr(cls, attr_name, governed_method)
                wrapped_count += 1

            if wrapped_count > 0:
                logger.debug(f"[ANANTA] {name}: Auto-governed {wrapped_count} methods")

        logger.debug(f"Marked as NAGA: {name} ({lord.value})")
        return cls

    return decorator


# =============================================================================
# KULIKA REGISTRY - The Single Source of Truth
# =============================================================================


class KulikaRegistry:
    """
    The Schema Registry for NAGA services.

    Kulika maintains order. He knows:
    - What services exist
    - What their manifests are
    - Whether they are valid

    Narada DISCOVERS services.
    Kulika VALIDATES and REGISTERS them.

    This is the Agentic replacement for manual ServiceRegistry.register().
    """

    _instance: Optional["KulikaRegistry"] = None

    def __new__(cls) -> "KulikaRegistry":
        """Singleton pattern - only one Kulika."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the registry."""
        if self._initialized:
            return

        self._services: Dict[str, NagaManifest] = {}
        self._classes: Dict[str, Type] = {}
        self._instances: Dict[str, Any] = {}
        self._by_lord: Dict[NagaLord, List[str]] = {lord: [] for lord in NagaLord}
        self._by_domain: Dict[NagaDomain, List[str]] = {domain: [] for domain in NagaDomain}
        self._by_drift_source: Dict[str, List[str]] = {}
        self._initialized = True

        logger.info("Kulika Registry initialized - Order established")

    def register(
        self,
        cls: Type,
        instance: Optional[Any] = None,
    ) -> bool:
        """
        Register a NAGA service.

        Called by Narada after discovery and validation.

        Args:
            cls: The service class (must have _naga_manifest)
            instance: Optional instance (if already created)

        Returns:
            True if registered successfully
        """
        if not hasattr(cls, "_naga_manifest"):
            logger.warning(f"Cannot register {cls.__name__}: no _naga_manifest")
            return False

        manifest: NagaManifest = cls._naga_manifest
        manifest.registered_at = datetime.now()

        name = manifest.name.lower()

        # Store
        self._services[name] = manifest
        self._classes[name] = cls
        if instance:
            self._instances[name] = instance

        # Index
        self._by_lord[manifest.lord].append(name)
        self._by_domain[manifest.domain].append(name)

        if manifest.drift_source:
            if manifest.drift_source not in self._by_drift_source:
                self._by_drift_source[manifest.drift_source] = []
            self._by_drift_source[manifest.drift_source].append(name)

        logger.info(f"Registered NAGA: {manifest.name} ({manifest.lord.value})")
        return True

    def unregister(self, name: str) -> bool:
        """Unregister a NAGA service."""
        name = name.lower()

        if name not in self._services:
            return False

        manifest = self._services[name]

        # Remove from indices
        self._by_lord[manifest.lord].remove(name)
        self._by_domain[manifest.domain].remove(name)

        if manifest.drift_source and name in self._by_drift_source.get(manifest.drift_source, []):
            self._by_drift_source[manifest.drift_source].remove(name)

        # Remove from stores
        del self._services[name]
        del self._classes[name]
        self._instances.pop(name, None)

        logger.info(f"Unregistered NAGA: {name}")
        return True

    def get(self, name: str) -> Optional[NagaManifest]:
        """Get a NAGA manifest by name."""
        return self._services.get(name.lower())

    def get_class(self, name: str) -> Optional[Type]:
        """Get a NAGA class by name."""
        return self._classes.get(name.lower())

    def get_instance(self, name: str) -> Optional[Any]:
        """Get a NAGA instance by name."""
        return self._instances.get(name.lower())

    def set_instance(self, name: str, instance: Any) -> None:
        """Set a NAGA instance."""
        self._instances[name.lower()] = instance

    def by_lord(self, lord: NagaLord) -> List[NagaManifest]:
        """Get all NAGAs of a specific lord type."""
        return [self._services[name] for name in self._by_lord.get(lord, [])]

    def by_domain(self, domain: NagaDomain) -> List[NagaManifest]:
        """Get all NAGAs in a domain."""
        return [self._services[name] for name in self._by_domain.get(domain, [])]

    def by_drift_source(self, drift_source: str) -> List[NagaManifest]:
        """Get all NAGAs handling a drift source."""
        return [self._services[name] for name in self._by_drift_source.get(drift_source, [])]

    def all_manifests(self) -> List[NagaManifest]:
        """Get all registered NAGA manifests."""
        return list(self._services.values())

    def all_names(self) -> List[str]:
        """Get all registered NAGA names."""
        return list(self._services.keys())

    def is_registered(self, name: str) -> bool:
        """Check if a NAGA is registered."""
        return name.lower() in self._services

    def validate(self, cls: Type) -> List[str]:
        """
        Validate a class against NAGA requirements.

        Returns list of validation errors (empty = valid).
        """
        errors = []

        # Must have manifest
        if not hasattr(cls, "_naga_manifest"):
            errors.append("Missing @naga_service decorator")
            return errors

        manifest: NagaManifest = cls._naga_manifest

        # Must have get_status
        if not hasattr(cls, "get_status"):
            errors.append("Missing get_status() method")

        # If has drift_source, must have as_handler
        if manifest.drift_source and not hasattr(cls, "as_handler"):
            errors.append(f"Has drift_source={manifest.drift_source} but missing as_handler() method")

        return errors

    def get_status(self) -> Dict[str, Any]:
        """Get registry status for manifestation."""
        return {
            "total_services": len(self._services),
            "infrastructure": len(self._by_domain.get(NagaDomain.INFRASTRUCTURE, [])),
            "governance": len(self._by_domain.get(NagaDomain.GOVERNANCE, [])),
            "by_lord": {lord.value: len(names) for lord, names in self._by_lord.items() if names},
            "drift_sources": list(self._by_drift_source.keys()),
        }

    def clear(self) -> None:
        """Clear all registrations (for testing)."""
        self._services.clear()
        self._classes.clear()
        self._instances.clear()
        self._by_lord = {lord: [] for lord in NagaLord}
        self._by_domain = {domain: [] for domain in NagaDomain}
        self._by_drift_source.clear()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_kulika() -> KulikaRegistry:
    """Get the Kulika Registry singleton."""
    return KulikaRegistry()


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Enums
    "NagaDomain",
    "NagaLord",
    "NagaCapability",
    # Data
    "NagaManifest",
    # Protocol
    "NagaServiceProtocol",
    # Decorators
    "naga_service",
    # "ungoverned" - available via __getattr__ lazy import, not in __all__ (ruff F822)
    # Registry
    "KulikaRegistry",
    "get_kulika",
]


# Re-export ungoverned for convenience
def __getattr__(name: str) -> Any:
    """Lazy import ungoverned from base to avoid circular import."""
    if name == "ungoverned":
        from vibe_core.naga.services.base import ungoverned

        return ungoverned
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
