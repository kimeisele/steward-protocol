"""
GATE PROVIDERS — Observer Pattern Tests
=========================================

Tests the 5 gate providers:
- MantraGateProvider (PARSE)
- StorageGateProvider (VALIDATE)
- InferGateProvider (EXECUTE)
- SyncGateProvider (RESULT)
- EnforceGateProvider (SYNC)

Plus IOPolicy enum and wire_gate_providers().
"""

import pytest

from vibe_core.mahamantra.substrate.vm.gate_providers import (
    EnforceGateProvider,
    InferGateProvider,
    IOPolicy,
    MantraGateProvider,
    StorageGateProvider,
    SyncGateProvider,
    get_providers,
    wire_gate_providers,
)


# ============================================================================
# IOPolicy Enum
# ============================================================================


class TestIOPolicy:
    """IOPolicy maps Guna to I/O behavior."""

    def test_policy_members(self):
        assert IOPolicy.VISHUDDHA.value == "vishuddha"
        assert IOPolicy.CACHE_ONLY.value == "cache_only"
        assert IOPolicy.WRITE_BEHIND.value == "write_behind"
        assert IOPolicy.SYNC_FLUSH.value == "sync_flush"
        assert IOPolicy.DENIED.value == "denied"

    def test_policy_count(self):
        assert len(IOPolicy) == 5


# ============================================================================
# Provider Instantiation
# ============================================================================


class TestProviderInstantiation:
    """All providers instantiate with no args."""

    def test_mantra_gate(self):
        p = MantraGateProvider()
        assert p is not None
        assert hasattr(p, "parse")
        assert hasattr(p, "stats")

    def test_storage_gate(self):
        p = StorageGateProvider()
        assert p is not None
        assert hasattr(p, "validate")
        assert hasattr(p, "stats")

    def test_infer_gate(self):
        p = InferGateProvider()
        assert p is not None
        assert hasattr(p, "infer")
        assert hasattr(p, "stats")

    def test_sync_gate(self):
        p = SyncGateProvider()
        assert p is not None
        assert hasattr(p, "route")
        assert hasattr(p, "stats")

    def test_enforce_gate(self):
        p = EnforceGateProvider()
        assert p is not None
        assert hasattr(p, "enforce")
        assert hasattr(p, "write")
        assert hasattr(p, "load")
        assert hasattr(p, "flush")
        assert hasattr(p, "stats")


# ============================================================================
# get_providers() singleton
# ============================================================================


class TestGetProviders:
    """get_providers() returns dict of 5 singleton providers."""

    def test_returns_dict(self):
        providers = get_providers()
        assert isinstance(providers, dict)

    def test_has_all_five(self):
        providers = get_providers()
        expected = {"mantra_gate", "storage_gate", "infer_gate", "sync_gate", "enforce_gate"}
        assert set(providers.keys()) == expected

    def test_correct_types(self):
        providers = get_providers()
        assert isinstance(providers["mantra_gate"], MantraGateProvider)
        assert isinstance(providers["storage_gate"], StorageGateProvider)
        assert isinstance(providers["infer_gate"], InferGateProvider)
        assert isinstance(providers["sync_gate"], SyncGateProvider)
        assert isinstance(providers["enforce_gate"], EnforceGateProvider)

    def test_singleton(self):
        """Same dict on repeated calls."""
        a = get_providers()
        b = get_providers()
        assert a is b


# ============================================================================
# Provider Operations
# ============================================================================


class TestMantraGateProvider:
    """MantraGateProvider parses input."""

    def test_parse_returns_result(self):
        p = MantraGateProvider()
        result = p.parse("test input")
        assert result is not None
        assert "valid" in result
        assert result["valid"] is True
        assert result["input_type"] == "str"

    def test_stats_after_parse(self):
        p = MantraGateProvider()
        p.parse("test")
        stats = p.stats
        assert stats is not None


class TestStorageGateProvider:
    """StorageGateProvider validates seeds."""

    def test_validate(self):
        p = StorageGateProvider()
        result = p.validate(37)
        assert result is not None

    def test_stats(self):
        p = StorageGateProvider()
        p.validate(42)
        stats = p.stats
        assert stats is not None


class TestInferGateProvider:
    """InferGateProvider infers from seed + attractor."""

    def test_infer(self):
        p = InferGateProvider()
        result = p.infer(seed=37, attractor=7)
        assert result is not None

    def test_stats(self):
        p = InferGateProvider()
        p.infer(seed=37, attractor=7)
        stats = p.stats
        assert stats is not None

