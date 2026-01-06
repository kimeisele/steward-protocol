"""
NAGA Test Harness - Protocol-Based Testing Infrastructure.

PROMPT.md: "Protocol statt konkrete Klassen (Dependency Inversion)"
INTEL.md: "Wire, don't invent" - use existing infrastructure

This module is THE SINGLE INJECTION POINT for NAGA testing:
1. NO MagicMock - uses Protocol-compliant NullObjects
2. ServiceRegistry-based DI - same as production
3. Config-driven - via NagaTestConfig
4. Isolated - each test gets fresh registry
5. Provides InMemoryLedger - no need to mock ledger
6. Provides CorrectionOrchestrator - no need to mock dispatcher

Usage:
    from vibe_core.naga.testing import NagaTestHarness

    def test_something():
        with NagaTestHarness() as harness:
            sesha = harness.sesha  # NullSesha via ServiceRegistry
            ledger = harness.ledger  # InMemoryLedger (real!)
            correction = harness.correction_orchestrator  # Real orchestrator!
            # Test against Protocol, not implementation

    # For NagaOrchestrator tests:
    def test_orchestrator():
        with NagaTestHarness.for_orchestrator() as harness:
            from vibe_core.naga import NagaOrchestrator
            naga = NagaOrchestrator.bootstrap(
                ledger=harness.ledger,
                correction_orchestrator=harness.correction_orchestrator,
            )
            assert naga.is_ready()

    # Or as pytest fixture (see conftest.py):
    def test_with_fixture(naga_harness):
        assert naga_harness.sesha.get_top_hash() == ""
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

from vibe_core.di import ServiceRegistry

# Import Protocols
from vibe_core.protocols.naga import (
    AnantaProtocol,
    ChitraguptaProtocol,
    KaliyaProtocol,
    KarkotakaProtocol,
    KulikaProtocol,
    NagaCortexProtocol,
    NaradaProtocol,
    PadmaProtocol,
    PrahladProtocol,
    SeshaProtocol,
    ShankhaProtocol,
    TakshakaProtocol,
    VasukiProtocol,
)

# Import NullObjects
from vibe_core.protocols.naga import (
    NullAnanta,
    NullChitragupta,
    NullKaliya,
    NullKarkotaka,
    NullKulika,
    NullNagaCortex,
    NullNarada,
    NullPadma,
    NullPrahlad,
    NullSesha,
    NullShankha,
    NullTakshaka,
    NullVasuki,
)

if TYPE_CHECKING:
    from vibe_core.protocols.correction import (
        CorrectionOrchestratorProtocol,
        DriftRegistryProtocol,
        CorrectionDispatcherProtocol,
    )
    from vibe_core.protocols.ledger import LedgerProtocol


# =============================================================================
# Null Implementations for Testing
# =============================================================================


class NullCorrectionOrchestrator:
    """
    Protocol-compliant CorrectionOrchestrator for testing.

    NO MagicMock. Implements CorrectionOrchestratorProtocol.
    """

    def __init__(self) -> None:
        from vibe_core.protocols.correction import (
            NullDriftRegistry,
            NullCorrectionDispatcher,
        )
        self._registry = NullDriftRegistry()
        self._dispatcher = NullCorrectionDispatcher()

    @property
    def registry(self) -> "DriftRegistryProtocol":
        return self._registry

    @property
    def dispatcher(self) -> "CorrectionDispatcherProtocol":
        return self._dispatcher

    def detect_and_report(
        self,
        source: Optional["DriftSource"] = None,
    ) -> List:
        return []

    def detect_and_heal(
        self,
        source: Optional["DriftSource"] = None,
        strategy: Optional["HealingStrategy"] = None,
        auto_only: bool = True,
    ) -> List:
        return []

    def get_healable_count(self) -> Dict:
        return {}


@dataclass
class NagaTestConfig:
    """Configuration for test harness."""

    # Which NAGAs to register (all by default)
    enable_sesha: bool = True
    enable_vasuki: bool = True
    enable_takshaka: bool = True
    enable_kaliya: bool = True
    enable_karkotaka: bool = True
    enable_kulika: bool = True
    enable_padma: bool = True
    enable_shankha: bool = True
    enable_narada: bool = True
    enable_chitragupta: bool = True
    enable_prahlad: bool = True
    enable_ananta: bool = True
    enable_cortex: bool = True

    # Reset registry on enter (default True for isolation)
    reset_on_enter: bool = True

    # Reset registry on exit (default True for cleanup)
    reset_on_exit: bool = True

    # Enable InMemoryLedger (for NagaOrchestrator tests)
    enable_ledger: bool = False

    # Enable CorrectionOrchestrator (for NagaOrchestrator tests)
    enable_correction_orchestrator: bool = False


class NagaTestHarness:
    """
    Protocol-based test harness for NAGA services.

    Uses NullObjects registered via ServiceRegistry.
    No MagicMock. No brittle patches. Just Protocols.

    Context manager for automatic setup/teardown.

    THE SINGLE INJECTION POINT for all NAGA testing.
    """

    def __init__(self, config: Optional[NagaTestConfig] = None):
        self._config = config or NagaTestConfig()
        self._registered: list[type] = []
        self._ledger: Optional["LedgerProtocol"] = None
        self._correction_orchestrator: Optional["CorrectionOrchestratorProtocol"] = None

    @classmethod
    def for_orchestrator(cls) -> "NagaTestHarness":
        """
        Factory for NagaOrchestrator testing.

        Returns harness with ledger and correction_orchestrator enabled.
        This provides everything NagaOrchestrator.bootstrap() needs.

        Usage:
            with NagaTestHarness.for_orchestrator() as harness:
                naga = NagaOrchestrator.bootstrap(
                    ledger=harness.ledger,
                    correction_orchestrator=harness.correction_orchestrator,
                )
        """
        config = NagaTestConfig(
            enable_ledger=True,
            enable_correction_orchestrator=True,
            # Don't register NullObjects - let Orchestrator create real ones
            enable_sesha=False,
            enable_vasuki=False,
            enable_takshaka=False,
            enable_kaliya=False,
            enable_karkotaka=False,
            enable_kulika=False,
            enable_padma=False,
            enable_shankha=False,
            enable_narada=False,
            enable_chitragupta=False,
            enable_prahlad=False,
            enable_ananta=False,
            enable_cortex=False,
        )
        return cls(config)

    def __enter__(self) -> "NagaTestHarness":
        """Setup: Reset registry and register NullObjects."""
        if self._config.reset_on_enter:
            ServiceRegistry.reset()

        self._register_null_objects()

        # Create ledger if enabled
        if self._config.enable_ledger:
            from vibe_core.ledger import InMemoryLedger
            self._ledger = InMemoryLedger()

        # Create correction orchestrator if enabled
        if self._config.enable_correction_orchestrator:
            self._correction_orchestrator = NullCorrectionOrchestrator()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Teardown: Reset registry for isolation."""
        if self._config.reset_on_exit:
            ServiceRegistry.reset()

    def _register_null_objects(self) -> None:
        """Register NullObjects for enabled NAGAs."""
        # Infrastructure Layer (Real Nagas - 8)
        if self._config.enable_sesha:
            ServiceRegistry.register(SeshaProtocol, NullSesha())
            self._registered.append(SeshaProtocol)

        if self._config.enable_vasuki:
            ServiceRegistry.register(VasukiProtocol, NullVasuki())
            self._registered.append(VasukiProtocol)

        if self._config.enable_takshaka:
            ServiceRegistry.register(TakshakaProtocol, NullTakshaka())
            self._registered.append(TakshakaProtocol)

        if self._config.enable_kaliya:
            ServiceRegistry.register(KaliyaProtocol, NullKaliya())
            self._registered.append(KaliyaProtocol)

        if self._config.enable_karkotaka:
            ServiceRegistry.register(KarkotakaProtocol, NullKarkotaka())
            self._registered.append(KarkotakaProtocol)

        if self._config.enable_kulika:
            ServiceRegistry.register(KulikaProtocol, NullKulika())
            self._registered.append(KulikaProtocol)

        if self._config.enable_padma:
            ServiceRegistry.register(PadmaProtocol, NullPadma())
            self._registered.append(PadmaProtocol)

        if self._config.enable_shankha:
            ServiceRegistry.register(ShankhaProtocol, NullShankha())
            self._registered.append(ShankhaProtocol)

        # Governance Layer (Personnel - 4)
        if self._config.enable_narada:
            ServiceRegistry.register(NaradaProtocol, NullNarada())
            self._registered.append(NaradaProtocol)

        if self._config.enable_chitragupta:
            ServiceRegistry.register(ChitraguptaProtocol, NullChitragupta())
            self._registered.append(ChitraguptaProtocol)

        if self._config.enable_prahlad:
            ServiceRegistry.register(PrahladProtocol, NullPrahlad())
            self._registered.append(PrahladProtocol)

        if self._config.enable_ananta:
            ServiceRegistry.register(AnantaProtocol, NullAnanta())
            self._registered.append(AnantaProtocol)

        # Cortex
        if self._config.enable_cortex:
            ServiceRegistry.register(NagaCortexProtocol, NullNagaCortex())
            self._registered.append(NagaCortexProtocol)

    # =========================================================================
    # Protocol Accessors - Get from ServiceRegistry (same as production)
    # =========================================================================

    @property
    def sesha(self) -> SeshaProtocol:
        """Get Sesha via ServiceRegistry."""
        return ServiceRegistry.get(SeshaProtocol) or NullSesha()

    @property
    def vasuki(self) -> VasukiProtocol:
        """Get Vasuki via ServiceRegistry."""
        return ServiceRegistry.get(VasukiProtocol) or NullVasuki()

    @property
    def takshaka(self) -> TakshakaProtocol:
        """Get Takshaka via ServiceRegistry."""
        return ServiceRegistry.get(TakshakaProtocol) or NullTakshaka()

    @property
    def kaliya(self) -> KaliyaProtocol:
        """Get Kaliya via ServiceRegistry."""
        return ServiceRegistry.get(KaliyaProtocol) or NullKaliya()

    @property
    def karkotaka(self) -> KarkotakaProtocol:
        """Get Karkotaka via ServiceRegistry."""
        return ServiceRegistry.get(KarkotakaProtocol) or NullKarkotaka()

    @property
    def kulika(self) -> KulikaProtocol:
        """Get Kulika via ServiceRegistry."""
        return ServiceRegistry.get(KulikaProtocol) or NullKulika()

    @property
    def padma(self) -> PadmaProtocol:
        """Get Padma via ServiceRegistry."""
        return ServiceRegistry.get(PadmaProtocol) or NullPadma()

    @property
    def shankha(self) -> ShankhaProtocol:
        """Get Shankha via ServiceRegistry."""
        return ServiceRegistry.get(ShankhaProtocol) or NullShankha()

    @property
    def narada(self) -> NaradaProtocol:
        """Get Narada via ServiceRegistry."""
        return ServiceRegistry.get(NaradaProtocol) or NullNarada()

    @property
    def chitragupta(self) -> ChitraguptaProtocol:
        """Get Chitragupta via ServiceRegistry."""
        return ServiceRegistry.get(ChitraguptaProtocol) or NullChitragupta()

    @property
    def prahlad(self) -> PrahladProtocol:
        """Get Prahlad via ServiceRegistry."""
        return ServiceRegistry.get(PrahladProtocol) or NullPrahlad()

    @property
    def ananta(self) -> AnantaProtocol:
        """Get Ananta via ServiceRegistry."""
        return ServiceRegistry.get(AnantaProtocol) or NullAnanta()

    @property
    def cortex(self) -> NagaCortexProtocol:
        """Get Cortex via ServiceRegistry."""
        return ServiceRegistry.get(NagaCortexProtocol) or NullNagaCortex()

    # =========================================================================
    # Infrastructure Accessors (for NagaOrchestrator tests)
    # =========================================================================

    @property
    def ledger(self) -> "LedgerProtocol":
        """
        Get InMemoryLedger for testing.

        Raises RuntimeError if enable_ledger=False in config.
        Use NagaTestHarness.for_orchestrator() for automatic setup.
        """
        if self._ledger is None:
            raise RuntimeError(
                "Ledger not enabled. Use NagaTestHarness.for_orchestrator() "
                "or set enable_ledger=True in config."
            )
        return self._ledger

    @property
    def correction_orchestrator(self) -> "CorrectionOrchestratorProtocol":
        """
        Get NullCorrectionOrchestrator for testing.

        Raises RuntimeError if enable_correction_orchestrator=False in config.
        Use NagaTestHarness.for_orchestrator() for automatic setup.
        """
        if self._correction_orchestrator is None:
            raise RuntimeError(
                "CorrectionOrchestrator not enabled. Use NagaTestHarness.for_orchestrator() "
                "or set enable_correction_orchestrator=True in config."
            )
        return self._correction_orchestrator

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_registered_protocols(self) -> list[type]:
        """Get list of registered protocols."""
        return self._registered.copy()

    def is_registered(self, protocol: type) -> bool:
        """Check if protocol is registered."""
        return ServiceRegistry.is_registered(protocol)


# =============================================================================
# Pytest Fixture Factory
# =============================================================================


def create_naga_fixture(config: Optional[NagaTestConfig] = None):
    """
    Factory for creating pytest fixtures.

    Usage in conftest.py:
        import pytest
        from vibe_core.naga.testing import create_naga_fixture

        @pytest.fixture
        def naga_harness():
            yield from create_naga_fixture()
    """
    harness = NagaTestHarness(config)
    with harness:
        yield harness


__all__ = [
    # Primary harness
    "NagaTestHarness",
    "NagaTestConfig",
    # Null implementations
    "NullCorrectionOrchestrator",
    # Factory
    "create_naga_fixture",
]
