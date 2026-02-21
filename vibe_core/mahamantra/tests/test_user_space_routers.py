"""
Tests for User-Space Routers (AdapterRouter, AuditRouter, HealRouter).

These routers are exposed via mahamantra.adapt, mahamantra.audit, mahamantra.heal.
They are Layer 6/7 syscall facades — NEVER used in hot loops.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# AdapterRouter — mahamantra.adapt
# =============================================================================

class TestAdapterRouter:
    """Prove mahamantra.adapt routes to adapters/ dynamically."""

    def test_adapt_returns_adapter_router(self):
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        router = mahamantra.adapt
        assert repr(router) == "AdapterRouter(dynamic)"

    def test_adapt_resolves_transform(self):
        """mahamantra.adapt.MahaTransform must resolve to the real class."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        cls = mahamantra.adapt.MahaTransform
        assert cls is not None
        assert hasattr(cls, '__call__') or isinstance(cls, type)

    def test_adapt_resolves_hash(self):
        """mahamantra.adapt.DeterministicHash must resolve."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        cls = mahamantra.adapt.DeterministicHash
        assert cls is not None

    def test_adapt_caches_result(self):
        """Second access must come from cache (no re-import)."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        first = mahamantra.adapt.MahaTransform
        second = mahamantra.adapt.MahaTransform
        assert first is second

    def test_adapt_raises_on_private(self):
        """Private attributes must raise AttributeError."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        with pytest.raises(AttributeError):
            _ = mahamantra.adapt._secret

    def test_adapt_raises_on_nonexistent(self):
        """Non-existent adapter must raise AttributeError."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        with pytest.raises(AttributeError):
            _ = mahamantra.adapt.this_adapter_does_not_exist_xyz


# =============================================================================
# AuditRouter — mahamantra.audit
# =============================================================================

class TestAuditRouter:
    """Prove mahamantra.audit routes to audit/ dynamically."""

    def test_audit_returns_audit_router(self):
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        router = mahamantra.audit
        assert repr(router) == "AuditRouter(dynamic)"

    def test_audit_resolves_drift_module(self):
        """mahamantra.audit.drift must resolve to the drift module."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        drift = mahamantra.audit.drift
        assert hasattr(drift, 'Auditor')

    def test_audit_kernel_returns_instance(self):
        """mahamantra.audit.kernel() must return an AuditKernel instance."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        kernel = mahamantra.audit.kernel()
        assert kernel is not None
        assert type(kernel).__name__ == 'AuditKernel'


# =============================================================================
# HealRouter — mahamantra.heal
# =============================================================================

class TestHealRouter:
    """Prove mahamantra.heal routes to dharma/kapila/remedies/ dynamically."""

    def test_heal_returns_heal_router(self):
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        router = mahamantra.heal
        assert repr(router) == "HealRouter(dynamic)"

    def test_heal_resolves_broken_genesis(self):
        """mahamantra.heal.broken_genesis must resolve to the remedy module."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        mod = mahamantra.heal.broken_genesis
        assert mod is not None

    def test_heal_run_all_dry_run(self):
        """mahamantra.heal.run_all(dry_run=True) must return a list."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        results = mahamantra.heal.run_all(dry_run=True)
        assert isinstance(results, list)
