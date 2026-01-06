"""
NAGA Capability Mixins - The Gene Pool (Refactored for Substrate Architecture)

Each Mixin is a GENE that:
1. Implements IGene protocol from substrate.py
2. Can be BOUND to a host via bind(host: IGeneHost) - TOP-DOWN injection
3. Falls back to ServiceRegistry if not bound - BACKWARD COMPATIBLE
4. Retains its INDIVIDUAL IDENTITY (Vaishnava, not Mayavadi)

Architecture (Acintya-bheda-abheda - simultaneously one and different):
    ANANTA SHESHA (Host/Substrat) - The table, not the food
         ↓ bind(self)
    NAGA MIXINS (Gene/Capabilities) - The guests, retain identity
         ↓ provides capability to
    FLOODED SERVICE - The consumer

The Gene does NOT become the Host. It remains a separate module.
This is proven by: Gene can work with ANY IGeneHost, not just AnantaService.

Usage (New - Preferred):
    class FloodedService(SeshaMixin, OriginalService):
        pass

    service = FloodedService()
    host.bind_gene(service)  # Host injects itself
    service.sesha.record(...)  # Access via mixin

Usage (Legacy - Backward Compatible):
    class FloodedService(SeshaMixin, OriginalService):
        pass

    service = FloodedService()
    service.sesha.record(...)  # Falls back to ServiceRegistry
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

# Import from SUBSTRATE (Layer -1) - NO circular dependency possible
from vibe_core.protocols.substrate import (
    BindingCertificate,
    GeneActivationState,
    GeneManifest,
    IGene,
    IGeneHost,
    create_gene_manifest,
)

if TYPE_CHECKING:
    from vibe_core.protocols.naga import (
        ChitraguptaProtocol,
        KaliyaProtocol,
        KarkotakaProtocol,
        KulikaProtocol,
        NaradaProtocol,
        PadmaProtocol,
        PrahladProtocol,
        SeshaProtocol,
        ShankhaProtocol,
        TakshakaProtocol,
        VasukiProtocol,
    )


# =============================================================================
# BASE MIXIN (Implements IGene Protocol)
# =============================================================================


class NagaCapabilityMixin:
    """
    Base mixin that implements IGene protocol.

    All NAGA mixins inherit from this for:
    1. isinstance checks (_naga_flooded marker)
    2. IGene protocol implementation (bind, activate, etc.)
    3. Backward-compatible ServiceRegistry fallback

    This is the DNA backbone - each specific mixin adds its gene.
    """

    # Marker for flood detection
    _naga_flooded: bool = True
    _naga_capabilities: List[str] = []

    # IGene state
    _gene_host: Optional[IGeneHost] = None
    _gene_state: GeneActivationState = GeneActivationState.DORMANT
    _gene_bound_at: Optional[datetime] = None
    _gene_activated_at: Optional[datetime] = None

    # Override in subclasses
    _gene_manifest: GeneManifest = create_gene_manifest(
        name="base",
        capabilities=[],
        requires=[],
        priority=0,
        optional=True,
    )

    # =========================================================================
    # IGene Protocol Implementation
    # =========================================================================

    @property
    def manifest(self) -> GeneManifest:
        """Get the gene's manifest (static capabilities)."""
        return self._gene_manifest

    @property
    def state(self) -> GeneActivationState:
        """Get the gene's current activation state."""
        return self._gene_state

    # Store binding certificate for chain of custody
    _binding_certificate: Optional[BindingCertificate] = None

    def bind(
        self,
        host: IGeneHost,
        certificate: Optional[BindingCertificate] = None,
    ) -> None:
        """
        Bind this gene to a host.

        This is DEPENDENCY INJECTION from above (Avatara pattern).
        The host calls this method, passing itself.
        The gene stores the reference for capability access.

        ANTI-MAYAVADI: Certificate proves WHO is binding.
        Without certificate, binding is UNVERIFIED (legacy mode).
        With certificate, binding has chain of custody.

        Args:
            host: The IGeneHost that will power this gene
            certificate: Optional binding certificate for verified binding
        """
        self._gene_host = host
        self._gene_state = GeneActivationState.BOUND
        self._gene_bound_at = datetime.now()
        self._binding_certificate = certificate

    def activate(self) -> bool:
        """
        Activate this gene.

        Returns:
            True if activation successful, False otherwise
        """
        if self._gene_state == GeneActivationState.DORMANT:
            # Can't activate without binding first
            return False

        self._gene_state = GeneActivationState.ACTIVE
        self._gene_activated_at = datetime.now()
        return True

    def deactivate(self) -> None:
        """Deactivate this gene (but keep it bound)."""
        if self._gene_state == GeneActivationState.ACTIVE:
            self._gene_state = GeneActivationState.BOUND

    def unbind(self) -> None:
        """Unbind from host completely."""
        self._gene_host = None
        self._gene_state = GeneActivationState.DORMANT
        self._gene_bound_at = None
        self._gene_activated_at = None
        self._binding_certificate = None

    # =========================================================================
    # Host Access (with ServiceRegistry Fallback)
    # =========================================================================

    @property
    def host(self) -> Optional[IGeneHost]:
        """Get the bound host, or None if not bound."""
        return self._gene_host

    def _get_service_from_host_or_registry(
        self,
        capability: str,
        protocol_name: str,
    ) -> Optional[Any]:
        """
        Get a service capability from host OR fall back to ServiceRegistry.

        This enables:
        1. New pattern: Host-injected capabilities (clean, testable)
        2. Legacy pattern: ServiceRegistry lookup (backward compat)

        Args:
            capability: Capability name to request from host
            protocol_name: Protocol class name for ServiceRegistry fallback

        Returns:
            The capability provider, or None if unavailable
        """
        # Try 1: Get from bound host (preferred)
        if self._gene_host is not None:
            cap = self._gene_host.get_capability(capability)
            if cap is not None:
                return cap

        # Try 2: Fall back to ServiceRegistry (backward compat)
        try:
            # Dynamic protocol lookup
            from vibe_core import protocols
            from vibe_core.di import ServiceRegistry

            protocol_module = getattr(protocols, "naga", None)
            if protocol_module:
                protocol_class = getattr(protocol_module, protocol_name, None)
                if protocol_class:
                    return ServiceRegistry.get(protocol_class)
        except Exception:
            pass  # Graceful degradation

        return None


# =============================================================================
# SESHA MIXIN - Truth/Ledger/Audit
# =============================================================================


class SeshaMixin(NagaCapabilityMixin):
    """
    SESHA Capability - Truth/Ledger/Audit.

    Gene Manifest:
        - Provides: ledger, audit, sync, truth
        - Requires: storage (optional)
        - Priority: 100 (critical, load first)

    Use for: Recording operations, audit trails, state tracking.
    """

    _sesha: Optional["SeshaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="sesha",
        capabilities=["ledger", "audit", "sync", "truth"],
        requires=["storage"],
        priority=100,
        optional=False,
    )

    @property
    def sesha(self) -> Optional["SeshaProtocol"]:
        """Access to SESHA (Truth/Ledger)."""
        if self._sesha is None:
            self._sesha = self._get_service_from_host_or_registry(
                capability="sesha",
                protocol_name="SeshaProtocol",
            )
        return self._sesha


# =============================================================================
# VASUKI MIXIN - Network/External Boundaries
# =============================================================================


class VasukiMixin(NagaCapabilityMixin):
    """
    VASUKI Capability - Network/External Boundaries.

    Gene Manifest:
        - Provides: network, http, external, boundary
        - Requires: none
        - Priority: 90

    Use for: HTTP calls, subprocess, external API access.
    """

    _vasuki: Optional["VasukiProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="vasuki",
        capabilities=["network", "http", "external", "boundary"],
        requires=[],
        priority=90,
        optional=False,
    )

    @property
    def vasuki(self) -> Optional["VasukiProtocol"]:
        """Access to VASUKI (Network)."""
        if self._vasuki is None:
            self._vasuki = self._get_service_from_host_or_registry(
                capability="vasuki",
                protocol_name="VasukiProtocol",
            )
        return self._vasuki


# =============================================================================
# TAKSHAKA MIXIN - Security/Validation
# =============================================================================


class TakshakaMixin(NagaCapabilityMixin):
    """
    TAKSHAKA Capability - Security/Validation.

    Gene Manifest:
        - Provides: security, validation, toxicity, sanitization
        - Requires: none
        - Priority: 95 (high - security first)

    Use for: Input validation, data sanitization, security checks.
    """

    _takshaka: Optional["TakshakaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="takshaka",
        capabilities=["security", "validation", "toxicity", "sanitization"],
        requires=[],
        priority=95,
        optional=False,
    )

    @property
    def takshaka(self) -> Optional["TakshakaProtocol"]:
        """Access to TAKSHAKA (Security)."""
        if self._takshaka is None:
            self._takshaka = self._get_service_from_host_or_registry(
                capability="takshaka",
                protocol_name="TakshakaProtocol",
            )
        return self._takshaka


# =============================================================================
# KALIYA MIXIN - Isolation/Sandboxing
# =============================================================================


class KaliyaMixin(NagaCapabilityMixin):
    """
    KALIYA Capability - Isolation/Sandboxing.

    Gene Manifest:
        - Provides: isolation, sandbox, quarantine, containment
        - Requires: none
        - Priority: 85

    Use for: Process isolation, resource limits, containment.
    """

    _kaliya: Optional["KaliyaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="kaliya",
        capabilities=["isolation", "sandbox", "quarantine", "containment"],
        requires=[],
        priority=85,
        optional=True,
    )

    @property
    def kaliya(self) -> Optional["KaliyaProtocol"]:
        """Access to KALIYA (Isolation)."""
        if self._kaliya is None:
            self._kaliya = self._get_service_from_host_or_registry(
                capability="kaliya",
                protocol_name="KaliyaProtocol",
            )
        return self._kaliya


# =============================================================================
# KARKOTAKA MIXIN - Crypto/Secrets
# =============================================================================


class KarkotakaMixin(NagaCapabilityMixin):
    """
    KARKOTAKA Capability - Crypto/Secrets.

    Gene Manifest:
        - Provides: crypto, secrets, encryption, signing
        - Requires: none
        - Priority: 80

    Use for: Encryption, key management, secret storage.
    """

    _karkotaka: Optional["KarkotakaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="karkotaka",
        capabilities=["crypto", "secrets", "encryption", "signing"],
        requires=[],
        priority=80,
        optional=True,
    )

    @property
    def karkotaka(self) -> Optional["KarkotakaProtocol"]:
        """Access to KARKOTAKA (Crypto)."""
        if self._karkotaka is None:
            self._karkotaka = self._get_service_from_host_or_registry(
                capability="karkotaka",
                protocol_name="KarkotakaProtocol",
            )
        return self._karkotaka


# =============================================================================
# KULIKA MIXIN - Schema/Order
# =============================================================================


class KulikaMixin(NagaCapabilityMixin):
    """
    KULIKA Capability - Schema/Order.

    Gene Manifest:
        - Provides: schema, validation, order, structure
        - Requires: none
        - Priority: 75

    Use for: Schema validation, type enforcement, structure.
    """

    _kulika: Optional["KulikaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="kulika",
        capabilities=["schema", "validation", "order", "structure"],
        requires=[],
        priority=75,
        optional=True,
    )

    @property
    def kulika(self) -> Optional["KulikaProtocol"]:
        """Access to KULIKA (Schema)."""
        if self._kulika is None:
            self._kulika = self._get_service_from_host_or_registry(
                capability="kulika",
                protocol_name="KulikaProtocol",
            )
        return self._kulika


# =============================================================================
# PADMA MIXIN - Cache/Treasury
# =============================================================================


class PadmaMixin(NagaCapabilityMixin):
    """
    PADMA Capability - Cache/Treasury.

    Gene Manifest:
        - Provides: cache, treasury, memoization, pool
        - Requires: none
        - Priority: 70

    Use for: Caching, memoization, resource pooling.
    """

    _padma: Optional["PadmaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="padma",
        capabilities=["cache", "treasury", "memoization", "pool"],
        requires=[],
        priority=70,
        optional=True,
    )

    @property
    def padma(self) -> Optional["PadmaProtocol"]:
        """Access to PADMA (Cache)."""
        if self._padma is None:
            self._padma = self._get_service_from_host_or_registry(
                capability="padma",
                protocol_name="PadmaProtocol",
            )
        return self._padma


# =============================================================================
# SHANKHA MIXIN - Broadcast/PubSub
# =============================================================================


class ShankhaMixin(NagaCapabilityMixin):
    """
    SHANKHA Capability - Broadcast/PubSub.

    Gene Manifest:
        - Provides: broadcast, pubsub, events, notifications
        - Requires: none
        - Priority: 65

    Use for: Event emission, notifications, messaging.
    """

    _shankha: Optional["ShankhaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="shankha",
        capabilities=["broadcast", "pubsub", "events", "notifications"],
        requires=[],
        priority=65,
        optional=True,
    )

    @property
    def shankha(self) -> Optional["ShankhaProtocol"]:
        """Access to SHANKHA (Broadcast)."""
        if self._shankha is None:
            self._shankha = self._get_service_from_host_or_registry(
                capability="shankha",
                protocol_name="ShankhaProtocol",
            )
        return self._shankha


# =============================================================================
# NARADA MIXIN - Observation/Discovery
# =============================================================================


class NaradaMixin(NagaCapabilityMixin):
    """
    NARADA Capability - Observation/Discovery.

    Gene Manifest:
        - Provides: observation, discovery, monitoring, health
        - Requires: none
        - Priority: 60

    Use for: Service discovery, health checks, monitoring.
    """

    _narada: Optional["NaradaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="narada",
        capabilities=["observation", "discovery", "monitoring", "health"],
        requires=[],
        priority=60,
        optional=True,
    )

    @property
    def narada(self) -> Optional["NaradaProtocol"]:
        """Access to NARADA (Observation)."""
        if self._narada is None:
            self._narada = self._get_service_from_host_or_registry(
                capability="narada",
                protocol_name="NaradaProtocol",
            )
        return self._narada


# =============================================================================
# CHITRAGUPTA MIXIN - Profiling/Metrics
# =============================================================================


class ChitraguptaMixin(NagaCapabilityMixin):
    """
    CHITRAGUPTA Capability - Profiling/Metrics.

    Gene Manifest:
        - Provides: profiling, metrics, timing, performance
        - Requires: none
        - Priority: 55

    Use for: Performance tracking, metrics collection, profiling.
    """

    _chitragupta: Optional["ChitraguptaProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="chitragupta",
        capabilities=["profiling", "metrics", "timing", "performance"],
        requires=[],
        priority=55,
        optional=True,
    )

    @property
    def chitragupta(self) -> Optional["ChitraguptaProtocol"]:
        """Access to CHITRAGUPTA (Profiling)."""
        if self._chitragupta is None:
            self._chitragupta = self._get_service_from_host_or_registry(
                capability="chitragupta",
                protocol_name="ChitraguptaProtocol",
            )
        return self._chitragupta


# =============================================================================
# PRAHLAD MIXIN - Resilience/Recovery
# =============================================================================


class PrahladMixin(NagaCapabilityMixin):
    """
    PRAHLAD Capability - Resilience/Recovery.

    Gene Manifest:
        - Provides: resilience, recovery, retry, circuit_breaker
        - Requires: none
        - Priority: 50

    Use for: Retry logic, circuit breakers, recovery patterns.
    """

    _prahlad: Optional["PrahladProtocol"] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="prahlad",
        capabilities=["resilience", "recovery", "retry", "circuit_breaker"],
        requires=[],
        priority=50,
        optional=True,
    )

    @property
    def prahlad(self) -> Optional["PrahladProtocol"]:
        """Access to PRAHLAD (Resilience)."""
        if self._prahlad is None:
            self._prahlad = self._get_service_from_host_or_registry(
                capability="prahlad",
                protocol_name="PrahladProtocol",
            )
        return self._prahlad


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "NagaCapabilityMixin",
    # Individual Genes (in priority order)
    "SeshaMixin",
    "TakshakaMixin",
    "VasukiMixin",
    "KaliyaMixin",
    "KarkotakaMixin",
    "KulikaMixin",
    "PadmaMixin",
    "ShankhaMixin",
    "NaradaMixin",
    "ChitraguptaMixin",
    "PrahladMixin",
]
