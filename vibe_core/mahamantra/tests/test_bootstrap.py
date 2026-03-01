"""
BOOTSTRAP — Safety Net Tests (Complexity 42)
==============================================

Tests the MahamantraLotus.bootstrap() function to enable
safe decomposition. Every assertion here must pass before
AND after any refactoring of bootstrap().

Tests:
- Idempotency (double-call safety)
- _bootstrapped flag
- Gate provider wiring
- Subsystem availability post-bootstrap
"""

import pytest
import logging


class TestBootstrapIdempotency:
    """bootstrap() must be safe to call multiple times."""

    def test_bootstrapped_flag_set(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        assert lotus._bootstrapped is False
        lotus.bootstrap(silent=True)
        assert lotus._bootstrapped is True

    def test_double_bootstrap_is_noop(self):
        """Second call returns immediately (idempotent)."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        lotus.bootstrap(silent=True)
        # Second call should not raise
        lotus.bootstrap(silent=True)
        assert lotus._bootstrapped is True

    def test_silent_mode_no_logging(self, caplog):
        """silent=True suppresses all logging."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        with caplog.at_level(logging.INFO, logger="MAHAMANTRA"):
            lotus.bootstrap(silent=True)
        # Should have no INFO messages from MAHAMANTRA logger
        mahamantra_infos = [r for r in caplog.records if r.name == "MAHAMANTRA" and r.levelno >= logging.INFO]
        assert len(mahamantra_infos) == 0


class TestBootstrapWiring:
    """After bootstrap, subsystems must be wired."""

    @pytest.fixture
    def bootstrapped_lotus(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        lotus.bootstrap(silent=True, lazy=True)
        return lotus

    def test_gate_providers_available(self, bootstrapped_lotus):
        """Gate providers should be registered after bootstrap."""
        from vibe_core.mahamantra.substrate.vm.gate_providers import get_providers

        providers = get_providers()
        assert len(providers) == 5
        assert "mantra_gate" in providers
        assert "enforce_gate" in providers

    def test_balarama_proxies_attribute(self, bootstrapped_lotus):
        """_balarama_proxies should exist (may be empty list if no services found)."""
        assert hasattr(bootstrapped_lotus, "_balarama_proxies")

    def test_orbital_reactors_attribute(self, bootstrapped_lotus):
        """_orbital_reactors should exist (may be empty list)."""
        assert hasattr(bootstrapped_lotus, "_orbital_reactors")


class TestBootstrapLazyVsEager:
    """lazy=True defers heavy loading, lazy=False loads eagerly."""

    def test_lazy_mode_default(self):
        """Default is lazy=True."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        import inspect

        sig = inspect.signature(MahamantraLotus.bootstrap)
        assert sig.parameters["lazy"].default is True

    def test_lazy_bootstrap_succeeds(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        lotus.bootstrap(silent=True, lazy=True)
        assert lotus._bootstrapped is True

    def test_eager_bootstrap_succeeds(self):
        """Eager mode loads more but should not crash."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        lotus.bootstrap(silent=True, lazy=False)
        assert lotus._bootstrapped is True


class TestBootstrapGracefulDegradation:
    """Each phase in bootstrap is wrapped in try-except.
    Even if subsystems fail to load, bootstrap must complete."""

    def test_bootstrap_always_completes(self):
        """bootstrap() must set _bootstrapped=True even if subsystems fail."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        # This should never raise, regardless of environment
        lotus.bootstrap(silent=True)
        assert lotus._bootstrapped is True
