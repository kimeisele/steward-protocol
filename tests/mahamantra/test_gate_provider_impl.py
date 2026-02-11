"""
Tests for gate_providers.py — The 5 Watchers at the TattvaGates.

Tests cover:
1. Each provider satisfies its Capability Protocol (isinstance check)
2. Each provider's method works correctly with valid/invalid input
3. Stats tracking across multiple calls
4. wire_gate_providers() registers all 5 in TattvaRegistry
5. Integration: _fire_gate() dispatches to real providers
"""

from __future__ import annotations

import pytest

from vibe_core.mahamantra.substrate.gate_providers import (
    EnforceGateProvider,
    InferGateProvider,
    MantraGateProvider,
    StorageGateProvider,
    SyncGateProvider,
    get_providers,
    wire_gate_providers,
)
from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate
from vibe_core.mahamantra.substrate.tattva_registry import TattvaRegistry, get_registry


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(autouse=True)
def _reset_registry():
    """Reset TattvaRegistry singleton before each test."""
    TattvaRegistry.reset()
    yield
    TattvaRegistry.reset()


@pytest.fixture(autouse=True)
def _reset_providers():
    """Reset provider singletons before each test."""
    import vibe_core.mahamantra.substrate.gate_providers as gp
    gp._PROVIDERS = None
    yield
    gp._PROVIDERS = None


# =============================================================================
# 1. CAPABILITY PROTOCOL COMPLIANCE
# =============================================================================

class TestCapabilityCompliance:
    """Each provider must satisfy its Capability Protocol."""

    def test_mantra_is_mantra_capable(self):
        from vibe_core.mahamantra.protocols._capabilities import MantraCapability
        provider = MantraGateProvider()
        assert isinstance(provider, MantraCapability)

    def test_storage_is_storage_capable(self):
        from vibe_core.mahamantra.protocols._capabilities import StorageCapability
        provider = StorageGateProvider()
        assert isinstance(provider, StorageCapability)

    def test_infer_is_infer_capable(self):
        from vibe_core.mahamantra.protocols._capabilities import InferCapability
        provider = InferGateProvider()
        assert isinstance(provider, InferCapability)

    def test_sync_is_sync_capable(self):
        from vibe_core.mahamantra.protocols._capabilities import SyncCapability
        provider = SyncGateProvider()
        assert isinstance(provider, SyncCapability)

    def test_enforce_is_enforce_capable(self):
        from vibe_core.mahamantra.protocols._capabilities import EnforceCapability
        provider = EnforceGateProvider()
        assert isinstance(provider, EnforceCapability)


# =============================================================================
# 2. MANTRA GATE PROVIDER (PARSE)
# =============================================================================

class TestMantraGateProvider:

    def test_parse_valid_string(self):
        p = MantraGateProvider()
        result = p.parse("hello")
        assert result["valid"] is True
        assert result["input_type"] == "str"
        assert result["parse_count"] == 1

    def test_parse_valid_int(self):
        p = MantraGateProvider()
        result = p.parse(42)
        assert result["valid"] is True
        assert result["input_type"] == "int"

    def test_parse_none_input(self):
        p = MantraGateProvider()
        result = p.parse(None)
        assert result["valid"] is False
        assert result["reason"] == "null_input"

    def test_parse_count_increments(self):
        p = MantraGateProvider()
        p.parse("a")
        p.parse("b")
        p.parse("c")
        assert p.stats["parse_count"] == 3
        assert p.stats["last_input_type"] == "str"


# =============================================================================
# 3. STORAGE GATE PROVIDER (VALIDATE)
# =============================================================================

class TestStorageGateProvider:

    def test_validate_valid_seed(self):
        p = StorageGateProvider()
        result = p.validate(12345)
        assert result["valid"] is True
        assert result["seed"] == 12345

    def test_validate_zero_seed(self):
        p = StorageGateProvider()
        result = p.validate(0)
        assert result["valid"] is True

    def test_validate_negative_seed(self):
        p = StorageGateProvider()
        result = p.validate(-1)
        assert result["valid"] is False
        assert result["reason"] == "negative_seed"

    def test_validate_non_integer(self):
        p = StorageGateProvider()
        result = p.validate("not_a_seed")
        assert result["valid"] is False
        assert result["reason"] == "non_integer_seed"

    def test_rejection_count(self):
        p = StorageGateProvider()
        p.validate(1)
        p.validate(-1)
        p.validate("bad")
        assert p.stats["validate_count"] == 3
        assert p.stats["rejection_count"] == 2


# =============================================================================
# 4. INFER GATE PROVIDER (EXECUTE)
# =============================================================================

class TestInferGateProvider:

    def test_infer_tracks_attractor(self):
        p = InferGateProvider()
        result = p.infer(seed=100, attractor=42)
        assert result["attractor"] == 42
        assert result["attractor_frequency"] == 1
        assert result["unique_attractors"] == 1

    def test_infer_frequency_increments(self):
        p = InferGateProvider()
        p.infer(seed=1, attractor=42)
        p.infer(seed=2, attractor=42)
        result = p.infer(seed=3, attractor=42)
        assert result["attractor_frequency"] == 3

    def test_infer_multiple_attractors(self):
        p = InferGateProvider()
        p.infer(seed=1, attractor=10)
        p.infer(seed=2, attractor=20)
        p.infer(seed=3, attractor=30)
        assert p.stats["unique_attractors"] == 3
        assert p.stats["infer_count"] == 3

    def test_infer_top_attractors(self):
        p = InferGateProvider()
        for _ in range(5):
            p.infer(seed=1, attractor=42)
        for _ in range(3):
            p.infer(seed=1, attractor=99)
        p.infer(seed=1, attractor=7)
        top = p.stats["top_attractors"]
        assert top[0] == (42, 5)
        assert top[1] == (99, 3)


# =============================================================================
# 5. SYNC GATE PROVIDER (RESULT)
# =============================================================================

class TestSyncGateProvider:

    def test_route_computes_position(self):
        p = SyncGateProvider()
        result = p.route(attractor=42)
        assert result["position"] == 42 % 16
        assert result["position_frequency"] == 1

    def test_route_position_distribution(self):
        p = SyncGateProvider()
        p.route(attractor=0)   # pos 0
        p.route(attractor=16)  # pos 0
        p.route(attractor=1)   # pos 1
        dist = p.stats["position_distribution"]
        assert dist[0] == 2
        assert dist[1] == 1

    def test_route_count(self):
        p = SyncGateProvider()
        for i in range(10):
            p.route(attractor=i)
        assert p.stats["route_count"] == 10


# =============================================================================
# 6. ENFORCE GATE PROVIDER (SYNC)
# =============================================================================

class TestEnforceGateProvider:

    def test_enforce_tracks_count(self):
        p = EnforceGateProvider()
        result = p.enforce(position=5, seed=100, attractor=42)
        assert result["position"] == 5
        assert result["seed"] == 100
        assert result["enforce_count"] == 1

    def test_enforce_without_state_service(self):
        """Without StateService in DI, committed should be False."""
        p = EnforceGateProvider()
        result = p.enforce(position=0, seed=0, attractor=0)
        assert result["committed"] is False

    def test_enforce_stats(self):
        p = EnforceGateProvider()
        p.enforce(position=3, seed=50, attractor=25)
        p.enforce(position=7, seed=99, attractor=44)
        stats = p.stats
        assert stats["enforce_count"] == 2
        assert stats["last_position"] == 7
        assert stats["last_seed"] == 99


# =============================================================================
# 7. GET_PROVIDERS SINGLETON
# =============================================================================

class TestGetProviders:

    def test_returns_5_providers(self):
        providers = get_providers()
        assert len(providers) == 5

    def test_singleton(self):
        p1 = get_providers()
        p2 = get_providers()
        assert p1 is p2

    def test_correct_types(self):
        providers = get_providers()
        assert isinstance(providers["mantra_gate"], MantraGateProvider)
        assert isinstance(providers["storage_gate"], StorageGateProvider)
        assert isinstance(providers["infer_gate"], InferGateProvider)
        assert isinstance(providers["sync_gate"], SyncGateProvider)
        assert isinstance(providers["enforce_gate"], EnforceGateProvider)


# =============================================================================
# 8. WIRE_GATE_PROVIDERS
# =============================================================================

class TestWireGateProviders:

    def test_wires_all_5(self):
        count = wire_gate_providers()
        assert count == 5

    def test_registry_has_providers(self):
        wire_gate_providers()
        registry = get_registry()
        assert registry.gate_provider_count(TattvaGate.PARSE) == 1
        assert registry.gate_provider_count(TattvaGate.VALIDATE) == 1
        assert registry.gate_provider_count(TattvaGate.EXECUTE) == 1
        assert registry.gate_provider_count(TattvaGate.RESULT) == 1
        assert registry.gate_provider_count(TattvaGate.SYNC) == 1

    def test_total_provider_count(self):
        wire_gate_providers()
        registry = get_registry()
        assert registry.gate_provider_count() == 5

    def test_idempotent(self):
        """Calling wire_gate_providers() twice should not double-register."""
        count1 = wire_gate_providers()
        count2 = wire_gate_providers()
        assert count1 == 5
        assert count2 == 0  # Already registered
        registry = get_registry()
        assert registry.gate_provider_count() == 5

    def test_provider_names_in_registry(self):
        wire_gate_providers()
        registry = get_registry()
        for gate in TattvaGate:
            providers = registry.get_gate_providers(gate)
            assert len(providers) == 1
            name, obj = providers[0]
            assert name.endswith("_gate")


# =============================================================================
# 9. INTEGRATION: _fire_gate dispatches to real providers
# =============================================================================

class TestFireGateIntegration:

    def test_fire_gate_calls_parse_provider(self):
        wire_gate_providers()
        providers = get_providers()
        mantra = providers["mantra_gate"]

        # Simulate what lotus_core._fire_gate does
        from vibe_core.mahamantra.substrate.lotus_core import _dispatch_provider
        _dispatch_provider(TattvaGate.PARSE, mantra, {"input_data": "test"})

        assert mantra.stats["parse_count"] == 1
        assert mantra.stats["last_input_type"] == "str"

    def test_fire_gate_calls_validate_provider(self):
        wire_gate_providers()
        providers = get_providers()
        storage = providers["storage_gate"]

        from vibe_core.mahamantra.substrate.lotus_core import _dispatch_provider
        _dispatch_provider(TattvaGate.VALIDATE, storage, {"seed": 42})

        assert storage.stats["validate_count"] == 1

    def test_fire_gate_calls_infer_provider(self):
        wire_gate_providers()
        providers = get_providers()
        infer = providers["infer_gate"]

        from vibe_core.mahamantra.substrate.lotus_core import _dispatch_provider
        _dispatch_provider(TattvaGate.EXECUTE, infer, {"seed": 1, "attractor": 99})

        assert infer.stats["infer_count"] == 1
        assert infer.stats["unique_attractors"] == 1

    def test_fire_gate_calls_route_provider(self):
        wire_gate_providers()
        providers = get_providers()
        sync = providers["sync_gate"]

        from vibe_core.mahamantra.substrate.lotus_core import _dispatch_provider
        _dispatch_provider(TattvaGate.RESULT, sync, {"attractor": 42})

        assert sync.stats["route_count"] == 1

    def test_fire_gate_calls_enforce_provider(self):
        wire_gate_providers()
        providers = get_providers()
        enforce = providers["enforce_gate"]

        from vibe_core.mahamantra.substrate.lotus_core import _dispatch_provider
        _dispatch_provider(
            TattvaGate.SYNC, enforce,
            {"position": 5, "seed": 100, "attractor": 42},
        )

        assert enforce.stats["enforce_count"] == 1
        assert enforce.stats["last_position"] == 5
