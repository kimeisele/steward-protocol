"""
NAGA Capability Mixins - The Toolbox.

Each Mixin provides LAZY access to a NAGA service via ServiceRegistry.
No logic, just capabilities. The Flood Classes do the actual work.

Pattern:
    @property
    def naga_name(self) -> Protocol:
        if self._naga_name is None:
            self._naga_name = ServiceRegistry.get(Protocol)
        return self._naga_name

Usage:
    class FloodedService(SeshaMixin, VasukiMixin, OriginalService):
        def risky_method(self):
            self.sesha.record(...)  # Access via mixin
            result = super().risky_method()
            self.vasuki.validate(...)
            return result
"""

from typing import TYPE_CHECKING, Optional

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


class NagaCapabilityMixin:
    """
    Base mixin that marks a class as NAGA-capable.

    All NAGA mixins inherit from this for isinstance checks.
    """

    _naga_flooded: bool = True
    _naga_capabilities: list = []


class SeshaMixin(NagaCapabilityMixin):
    """
    SESHA Capability - Truth/Ledger/Audit.

    Use for: Recording operations, audit trails, state tracking.
    """

    _sesha: Optional["SeshaProtocol"] = None

    @property
    def sesha(self) -> Optional["SeshaProtocol"]:
        """Lazy access to SESHA (Truth/Ledger)."""
        if self._sesha is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import SeshaProtocol

                self._sesha = ServiceRegistry.get(SeshaProtocol)
            except Exception:
                pass  # Graceful degradation
        return self._sesha


class VasukiMixin(NagaCapabilityMixin):
    """
    VASUKI Capability - Network/External Boundaries.

    Use for: HTTP calls, subprocess, external API access.
    """

    _vasuki: Optional["VasukiProtocol"] = None

    @property
    def vasuki(self) -> Optional["VasukiProtocol"]:
        """Lazy access to VASUKI (Network)."""
        if self._vasuki is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import VasukiProtocol

                self._vasuki = ServiceRegistry.get(VasukiProtocol)
            except Exception:
                pass
        return self._vasuki


class TakshakaMixin(NagaCapabilityMixin):
    """
    TAKSHAKA Capability - Security/Validation.

    Use for: Input validation, data sanitization, security checks.
    """

    _takshaka: Optional["TakshakaProtocol"] = None

    @property
    def takshaka(self) -> Optional["TakshakaProtocol"]:
        """Lazy access to TAKSHAKA (Security)."""
        if self._takshaka is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import TakshakaProtocol

                self._takshaka = ServiceRegistry.get(TakshakaProtocol)
            except Exception:
                pass
        return self._takshaka


class KaliyaMixin(NagaCapabilityMixin):
    """
    KALIYA Capability - Isolation/Sandboxing.

    Use for: Process isolation, resource limits, containment.
    """

    _kaliya: Optional["KaliyaProtocol"] = None

    @property
    def kaliya(self) -> Optional["KaliyaProtocol"]:
        """Lazy access to KALIYA (Isolation)."""
        if self._kaliya is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import KaliyaProtocol

                self._kaliya = ServiceRegistry.get(KaliyaProtocol)
            except Exception:
                pass
        return self._kaliya


class KarkotakaMixin(NagaCapabilityMixin):
    """
    KARKOTAKA Capability - Crypto/Secrets.

    Use for: Encryption, key management, secret storage.
    """

    _karkotaka: Optional["KarkotakaProtocol"] = None

    @property
    def karkotaka(self) -> Optional["KarkotakaProtocol"]:
        """Lazy access to KARKOTAKA (Crypto)."""
        if self._karkotaka is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import KarkotakaProtocol

                self._karkotaka = ServiceRegistry.get(KarkotakaProtocol)
            except Exception:
                pass
        return self._karkotaka


class KulikaMixin(NagaCapabilityMixin):
    """
    KULIKA Capability - Schema/Order.

    Use for: Schema validation, type enforcement, structure.
    """

    _kulika: Optional["KulikaProtocol"] = None

    @property
    def kulika(self) -> Optional["KulikaProtocol"]:
        """Lazy access to KULIKA (Schema)."""
        if self._kulika is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import KulikaProtocol

                self._kulika = ServiceRegistry.get(KulikaProtocol)
            except Exception:
                pass
        return self._kulika


class PadmaMixin(NagaCapabilityMixin):
    """
    PADMA Capability - Cache/Treasury.

    Use for: Caching, memoization, resource pooling.
    """

    _padma: Optional["PadmaProtocol"] = None

    @property
    def padma(self) -> Optional["PadmaProtocol"]:
        """Lazy access to PADMA (Cache)."""
        if self._padma is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import PadmaProtocol

                self._padma = ServiceRegistry.get(PadmaProtocol)
            except Exception:
                pass
        return self._padma


class ShankhaMixin(NagaCapabilityMixin):
    """
    SHANKHA Capability - Broadcast/PubSub.

    Use for: Event emission, notifications, messaging.
    """

    _shankha: Optional["ShankhaProtocol"] = None

    @property
    def shankha(self) -> Optional["ShankhaProtocol"]:
        """Lazy access to SHANKHA (Broadcast)."""
        if self._shankha is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import ShankhaProtocol

                self._shankha = ServiceRegistry.get(ShankhaProtocol)
            except Exception:
                pass
        return self._shankha


class NaradaMixin(NagaCapabilityMixin):
    """
    NARADA Capability - Observation/Discovery.

    Use for: Service discovery, health checks, monitoring.
    """

    _narada: Optional["NaradaProtocol"] = None

    @property
    def narada(self) -> Optional["NaradaProtocol"]:
        """Lazy access to NARADA (Observation)."""
        if self._narada is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import NaradaProtocol

                self._narada = ServiceRegistry.get(NaradaProtocol)
            except Exception:
                pass
        return self._narada


class ChitraguptaMixin(NagaCapabilityMixin):
    """
    CHITRAGUPTA Capability - Profiling/Metrics.

    Use for: Performance tracking, metrics collection, profiling.
    """

    _chitragupta: Optional["ChitraguptaProtocol"] = None

    @property
    def chitragupta(self) -> Optional["ChitraguptaProtocol"]:
        """Lazy access to CHITRAGUPTA (Profiling)."""
        if self._chitragupta is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import ChitraguptaProtocol

                self._chitragupta = ServiceRegistry.get(ChitraguptaProtocol)
            except Exception:
                pass
        return self._chitragupta


class PrahladMixin(NagaCapabilityMixin):
    """
    PRAHLAD Capability - Resilience/Recovery.

    Use for: Retry logic, circuit breakers, recovery patterns.
    """

    _prahlad: Optional["PrahladProtocol"] = None

    @property
    def prahlad(self) -> Optional["PrahladProtocol"]:
        """Lazy access to PRAHLAD (Resilience)."""
        if self._prahlad is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import PrahladProtocol

                self._prahlad = ServiceRegistry.get(PrahladProtocol)
            except Exception:
                pass
        return self._prahlad
