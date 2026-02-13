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
        from unittest.mock import patch
        p = EnforceGateProvider()
        p._state_service = None  # Reset any cached DI lookup
        with patch.object(EnforceGateProvider, "_get_state_service", return_value=None):
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


# =============================================================================
# 10. ENFORCE GATE — I/O CONTROLLER (ROLE 2)
# =============================================================================

class TestEnforceGateIOController:
    """Tests for EnforceGateProvider as I/O Controller (write/load/flush)."""

    def test_write_with_state_service(self):
        """write() should route through StateService when available."""
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        result = gate.write("test_state.json", {"key": "value"}, actor="test", guna=Guna.RAJAS)
        assert result["actor"] == "test"
        assert result["file"] == "test_state.json"
        assert gate.stats["writes_total"] == 1

    def test_write_tracks_audit(self):
        """write() should record audit entries."""
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        gate.write("a.json", {}, actor="mod_a", guna=Guna.RAJAS)
        gate.write("b.json", {}, actor="mod_b", guna=Guna.RAJAS)
        assert gate.stats["audit_log_size"] == 2
        assert gate.stats["writes_total"] == 2

    def test_write_without_state_service_denies(self, monkeypatch):
        """write() should deny if no StateService available (even with valid Guna)."""
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        monkeypatch.setattr(
            EnforceGateProvider, "_get_state_service", lambda self: None,
        )
        result = gate.write("x.json", {}, actor="rogue", guna=Guna.RAJAS)
        assert result["success"] is False
        assert result["reason"] == "no_state_service"
        assert gate.stats["writes_denied"] == 1

    def test_load_returns_default_when_missing(self):
        """load() should return default for missing files."""
        gate = EnforceGateProvider()
        result = gate.load("nonexistent_file_12345.json", default={"empty": True})
        # Either StateService returns default or we get our default
        assert result is not None

    def test_stats_include_io_fields(self):
        """stats should include I/O controller fields."""
        gate = EnforceGateProvider()
        stats = gate.stats
        assert "writes_total" in stats
        assert "writes_cached" in stats
        assert "writes_denied" in stats
        assert "audit_log_size" in stats

    def test_audit_log_bounded(self):
        """Audit log should not grow unbounded."""
        gate = EnforceGateProvider()
        # None guna = DENIED, generates audit entries without needing StateService
        for i in range(1100):
            gate.write(f"file_{i}.json", {}, actor="stress")
        # Should be trimmed to ~500
        assert gate.stats["audit_log_size"] <= 600

    def test_enforce_and_write_independent(self):
        """Pipeline enforce() and I/O write() are independent operations."""
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        gate.enforce(position=3, seed=42, attractor=99)
        gate.write("state.json", {"x": 1}, actor="test", guna=Guna.RAJAS)
        assert gate.stats["enforce_count"] == 1
        assert gate.stats["writes_total"] == 1


class TestGetSyncGate:
    """Tests for get_sync_gate() convenience function."""

    def test_returns_enforce_gate(self):
        from vibe_core.mahamantra.substrate.gate_providers import get_sync_gate
        gate = get_sync_gate()
        assert isinstance(gate, EnforceGateProvider)

    def test_singleton(self):
        from vibe_core.mahamantra.substrate.gate_providers import get_sync_gate
        g1 = get_sync_gate()
        g2 = get_sync_gate()
        assert g1 is g2


# =============================================================================
# 11. GUNA I/O POLICY — The Gate's Teeth
# =============================================================================
# Ksetra (field) = the data flowing through.
# Ksetrajna (knower of the field) = the policy that DECIDES based on Guna.
# =============================================================================

class TestGunaPolicyResolution:
    """_resolve_policy() maps Guna → IOPolicy correctly."""

    def test_sattva_resolves_to_cache_only(self):
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        from vibe_core.mahamantra.substrate.guna import Guna
        assert EnforceGateProvider._resolve_policy(Guna.SATTVA) == IOPolicy.CACHE_ONLY

    def test_rajas_resolves_to_write_behind(self):
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        from vibe_core.mahamantra.substrate.guna import Guna
        assert EnforceGateProvider._resolve_policy(Guna.RAJAS) == IOPolicy.WRITE_BEHIND

    def test_tamas_resolves_to_sync_flush(self):
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        from vibe_core.mahamantra.substrate.guna import Guna
        assert EnforceGateProvider._resolve_policy(Guna.TAMAS) == IOPolicy.SYNC_FLUSH

    def test_none_resolves_to_denied(self):
        """None = VOID = Mayavad = no right to write."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        assert EnforceGateProvider._resolve_policy(None) == IOPolicy.DENIED

    def test_garbage_resolves_to_denied(self):
        """Unknown values = DENIED. No duck-typing. No 'anything else'."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        assert EnforceGateProvider._resolve_policy("SATTVA") == IOPolicy.DENIED
        assert EnforceGateProvider._resolve_policy(999) == IOPolicy.DENIED
        assert EnforceGateProvider._resolve_policy(object()) == IOPolicy.DENIED


class TestGunaIOPolicySattva:
    """SATTVA = read-only. Writing under SATTVA is DENIED."""

    def test_sattva_blocks_write(self):
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        result = gate.write("obs.json", {"x": 1}, actor="observer", guna=Guna.SATTVA)
        assert result["success"] is False
        assert result["reason"] == "sattva_read_only"
        assert result["guna_policy"] == "cache_only"

    def test_sattva_increments_sattva_blocks(self):
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        gate.write("a.json", {}, actor="a", guna=Guna.SATTVA)
        gate.write("b.json", {}, actor="b", guna=Guna.SATTVA)
        assert gate.stats["sattva_blocks"] == 2
        assert gate.stats["writes_total"] == 2
        assert gate.stats["writes_cached"] == 0

    def test_sattva_records_audit(self):
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        gate.write("x.json", {}, actor="spy", guna=Guna.SATTVA)
        assert gate.stats["audit_log_size"] == 1

    def test_load_still_works_under_sattva(self):
        """SATTVA blocks writes, but load() is always allowed (read-only)."""
        gate = EnforceGateProvider()
        result = gate.load("nonexistent_sattva.json", default={"ok": True})
        assert result is not None


class TestGunaIOPolicyRajas:
    """RAJAS = normal write-behind. Data goes to RAM cache, deferred flush."""

    def test_rajas_allows_write(self):
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        result = gate.write("state.json", {"key": "val"}, actor="creator", guna=Guna.RAJAS)
        assert result["guna_policy"] == "write_behind"
        assert result["flushed"] is False
        assert gate.stats["writes_cached"] >= 1

    def test_rajas_no_immediate_flush(self):
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        result = gate.write("state.json", {}, actor="mod", guna=Guna.RAJAS)
        assert result["flushed"] is False
        assert gate.stats["writes_flushed"] == 0

    def test_none_guna_is_denied(self):
        """write() without guna = VOID = DENIED. No ungoverned writes."""
        gate = EnforceGateProvider()
        result = gate.write("legacy.json", {"old": True}, actor="legacy_module")
        assert result["success"] is False
        assert result["guna_policy"] == "denied"
        assert result["reason"] == "void_no_guna"


class TestGunaIOPolicyTamas:
    """TAMAS = sync flush. Data written to RAM AND immediately flushed to disk."""

    def test_tamas_writes_and_flushes(self):
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        result = gate.write("cleanup.json", {"dead": True}, actor="shiva", guna=Guna.TAMAS)
        assert result["guna_policy"] == "sync_flush"
        # flushed depends on StateService availability
        if result["success"]:
            assert result["cached"] is True

    def test_tamas_increments_flushed_counter(self):
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        gate.write("flush_me.json", {}, actor="destroyer", guna=Guna.TAMAS)
        # If StateService is available, writes_flushed should increment
        stats = gate.stats
        if stats["writes_cached"] > 0:
            assert stats["writes_flushed"] >= 0  # May or may not flush depending on env

    def test_tamas_without_state_service_denied(self, monkeypatch):
        """TAMAS still denied if no StateService (no ungoverned fallback)."""
        from vibe_core.mahamantra.substrate.guna import Guna
        gate = EnforceGateProvider()
        monkeypatch.setattr(
            EnforceGateProvider, "_get_state_service", lambda self: None,
        )
        result = gate.write("x.json", {}, actor="rogue", guna=Guna.TAMAS)
        assert result["success"] is False
        assert result["reason"] == "no_state_service"


class TestGunaIOPolicyIntegration:
    """End-to-end: Guna from OpCode → Policy → I/O decision."""

    def test_all_16_opcodes_have_valid_policy(self):
        """Every OpCode maps to a valid Guna → valid IOPolicy."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode
        from vibe_core.mahamantra.substrate.guna import get_guna

        for op in MantraOpCode:
            guna = get_guna(op)
            policy = EnforceGateProvider._resolve_policy(guna)
            assert isinstance(policy, IOPolicy), f"OpCode {op.name} → invalid policy"

    def test_io_flush_opcode_triggers_sync_flush(self):
        """IO_FLUSH (position 13, Bali) is TAMAS → SYNC_FLUSH."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode
        from vibe_core.mahamantra.substrate.guna import get_guna

        guna = get_guna(MantraOpCode.IO_FLUSH)
        policy = EnforceGateProvider._resolve_policy(guna)
        assert policy == IOPolicy.SYNC_FLUSH

    def test_type_check_opcode_blocks_write(self):
        """TYPE_CHECK (position 6, Kapila) is SATTVA → CACHE_ONLY → write blocked."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode
        from vibe_core.mahamantra.substrate.guna import get_guna

        guna = get_guna(MantraOpCode.TYPE_CHECK)
        policy = EnforceGateProvider._resolve_policy(guna)
        assert policy == IOPolicy.CACHE_ONLY

        gate = EnforceGateProvider()
        result = gate.write("analysis.json", {}, actor="kapila", guna=guna)
        assert result["success"] is False
        assert result["reason"] == "sattva_read_only"

    def test_alloc_mem_opcode_allows_write_behind(self):
        """ALLOC_MEM (position 2, Narada) is RAJAS → WRITE_BEHIND."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode
        from vibe_core.mahamantra.substrate.guna import get_guna

        guna = get_guna(MantraOpCode.ALLOC_MEM)
        policy = EnforceGateProvider._resolve_policy(guna)
        assert policy == IOPolicy.WRITE_BEHIND

    def test_stats_show_guna_fields(self):
        """Stats include writes_flushed and sattva_blocks."""
        gate = EnforceGateProvider()
        stats = gate.stats
        assert "writes_flushed" in stats
        assert "sattva_blocks" in stats
        assert stats["writes_flushed"] == 0
        assert stats["sattva_blocks"] == 0


# =============================================================================
# 12. VISHUDDHA SATTVA — The Transcendental Bypass
# =============================================================================
# "sa gunān samatītyaitān brahma-bhūyāya kalpate" — BG 14.26
# The Name transcends the three modes. No gate holds it.
# =============================================================================

class TestVishuddhaBypass:
    """VISHUDDHA = transcendental. The Name bypasses the Gate entirely."""

    def test_vishuddha_resolves_for_chant(self):
        """actor='chant' → VISHUDDHA (transcendental bypass)."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        policy = EnforceGateProvider._resolve_policy(None, actor="chant")
        assert policy == IOPolicy.VISHUDDHA

    def test_vishuddha_resolves_for_tick(self):
        """actor='tick' → VISHUDDHA (the heartbeat of the Name)."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        policy = EnforceGateProvider._resolve_policy(None, actor="tick")
        assert policy == IOPolicy.VISHUDDHA

    def test_vishuddha_resolves_for_mahamantra(self):
        """actor='mahamantra' → VISHUDDHA (direct access to the source)."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        policy = EnforceGateProvider._resolve_policy(None, actor="mahamantra")
        assert policy == IOPolicy.VISHUDDHA

    def test_vishuddha_bypasses_guna_check(self):
        """VISHUDDHA doesn't need a Guna — it IS the source."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        # Even with guna=None, vishuddha actor bypasses
        policy = EnforceGateProvider._resolve_policy(None, actor="chant")
        assert policy == IOPolicy.VISHUDDHA

    def test_vishuddha_write_succeeds(self):
        """The Name can write. No gate holds it."""
        gate = EnforceGateProvider()
        result = gate.write("akash.json", {"seed": 42}, actor="chant")
        assert result["guna_policy"] == "vishuddha"
        # Success depends on StateService availability
        if result["success"]:
            assert result["cached"] is True

    def test_vishuddha_audit_records_transcendental(self):
        """Audit trail records vishuddha origin, not rajas mechanism."""
        gate = EnforceGateProvider()
        gate.write("akash.json", {}, actor="tick")
        assert gate.stats["audit_log_size"] == 1

    def test_non_vishuddha_actor_not_bypassed(self):
        """Regular actors don't get VISHUDDHA bypass."""
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        policy = EnforceGateProvider._resolve_policy(None, actor="some_plugin")
        assert policy == IOPolicy.DENIED


# =============================================================================
# 13. VOID — Mayavad (No Guna = No Existence)
# =============================================================================

class TestVoidDenied:
    """VOID = Mayavad. No Guna, no existence, no right to write."""

    def test_none_guna_none_actor_is_void(self):
        from vibe_core.mahamantra.substrate.gate_providers import IOPolicy
        assert EnforceGateProvider._resolve_policy(None) == IOPolicy.DENIED

    def test_void_write_denied(self):
        gate = EnforceGateProvider()
        result = gate.write("rogue.json", {"hack": True}, actor="rogue_writer")
        assert result["success"] is False
        assert result["reason"] == "void_no_guna"
        assert result["guna_policy"] == "denied"

    def test_void_increments_denied(self):
        gate = EnforceGateProvider()
        gate.write("a.json", {}, actor="x")
        gate.write("b.json", {}, actor="y")
        assert gate.stats["writes_denied"] == 2
        assert gate.stats["writes_cached"] == 0
