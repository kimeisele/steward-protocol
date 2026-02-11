"""
Tests for TattvaRegistry gate provider registration with capability checking.

Verifies:
1. Capable objects are accepted as gate providers
2. Non-capable objects are rejected with violations logged
3. Provider queries work correctly
4. Violations are tracked
5. Integration with lotus_core on_gate() hook system
"""

import pytest
from typing import Any, Dict

from vibe_core.mahamantra.substrate.tattva_registry import TattvaRegistry, get_registry
from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate


# =============================================================================
# MOCK IMPLEMENTATIONS (same as test_capabilities.py)
# =============================================================================


class CapableParser:
    """Satisfies MantraCapability (PARSE gate)."""

    def parse(self, input_data: Any) -> Dict[str, Any]:
        return {"input_text": str(input_data), "seed": None, "input_coords": ()}


class CapableValidator:
    """Satisfies StorageCapability (VALIDATE gate)."""

    def validate(self, seed: int) -> Dict[str, Any]:
        return {"attractor": seed % 256, "parampara_verified": True}


class CapableInferrer:
    """Satisfies InferCapability (EXECUTE gate)."""

    def infer(self, seed: int, attractor: int) -> Dict[str, Any]:
        return {"resonant_words": [], "verse_info": None}


class CapableRouter:
    """Satisfies SyncCapability (RESULT gate)."""

    def route(self, attractor: int) -> Dict[str, Any]:
        return {"position": attractor % 16, "guardian": "bhishma", "quarter": "DHARMA"}


class CapableEnforcer:
    """Satisfies EnforceCapability (SYNC gate)."""

    def enforce(self, position: int, seed: int, attractor: int) -> Dict[str, Any]:
        return {"cell": None, "committed": True}


class Impostor:
    """Satisfies nothing."""
    pass


# =============================================================================
# FIXTURE
# =============================================================================


@pytest.fixture
def registry():
    """Fresh TattvaRegistry for each test."""
    TattvaRegistry.reset()
    return TattvaRegistry.instance()


# =============================================================================
# TESTS: Gate provider registration
# =============================================================================


class TestGateProviderRegistration:

    def test_capable_parser_accepted(self, registry):
        assert registry.register_gate_provider("parser", CapableParser(), TattvaGate.PARSE)

    def test_capable_validator_accepted(self, registry):
        assert registry.register_gate_provider("validator", CapableValidator(), TattvaGate.VALIDATE)

    def test_capable_inferrer_accepted(self, registry):
        assert registry.register_gate_provider("inferrer", CapableInferrer(), TattvaGate.EXECUTE)

    def test_capable_router_accepted(self, registry):
        assert registry.register_gate_provider("router", CapableRouter(), TattvaGate.RESULT)

    def test_capable_enforcer_accepted(self, registry):
        assert registry.register_gate_provider("enforcer", CapableEnforcer(), TattvaGate.SYNC)

    def test_impostor_rejected_at_parse(self, registry):
        assert not registry.register_gate_provider("impostor", Impostor(), TattvaGate.PARSE)

    def test_impostor_rejected_at_all_gates(self, registry):
        for gate in TattvaGate:
            assert not registry.register_gate_provider(f"impostor_{gate.name}", Impostor(), gate)

    def test_wrong_capability_rejected(self, registry):
        # Parser cannot serve VALIDATE gate
        assert not registry.register_gate_provider("parser_at_wrong_gate", CapableParser(), TattvaGate.VALIDATE)


# =============================================================================
# TESTS: Provider queries
# =============================================================================


class TestProviderQueries:

    def test_get_providers_empty(self, registry):
        assert registry.get_gate_providers(TattvaGate.PARSE) == []

    def test_get_providers_after_register(self, registry):
        parser = CapableParser()
        registry.register_gate_provider("parser", parser, TattvaGate.PARSE)
        providers = registry.get_gate_providers(TattvaGate.PARSE)
        assert len(providers) == 1
        assert providers[0] == ("parser", parser)

    def test_multiple_providers_per_gate(self, registry):
        p1 = CapableParser()
        p2 = CapableParser()
        registry.register_gate_provider("parser1", p1, TattvaGate.PARSE)
        registry.register_gate_provider("parser2", p2, TattvaGate.PARSE)
        assert registry.gate_provider_count(TattvaGate.PARSE) == 2

    def test_provider_count_total(self, registry):
        registry.register_gate_provider("parser", CapableParser(), TattvaGate.PARSE)
        registry.register_gate_provider("validator", CapableValidator(), TattvaGate.VALIDATE)
        registry.register_gate_provider("enforcer", CapableEnforcer(), TattvaGate.SYNC)
        assert registry.gate_provider_count() == 3

    def test_provider_count_per_gate(self, registry):
        registry.register_gate_provider("parser", CapableParser(), TattvaGate.PARSE)
        assert registry.gate_provider_count(TattvaGate.PARSE) == 1
        assert registry.gate_provider_count(TattvaGate.VALIDATE) == 0


# =============================================================================
# TESTS: Violations tracking
# =============================================================================


class TestViolations:

    def test_no_violations_initially(self, registry):
        assert registry.violations == []

    def test_violation_logged_on_rejection(self, registry):
        registry.register_gate_provider("impostor", Impostor(), TattvaGate.PARSE)
        assert len(registry.violations) == 1
        name, reason = registry.violations[0]
        assert name == "impostor"
        assert "MantraCapability" in reason
        assert "PARSE" in reason

    def test_multiple_violations_accumulated(self, registry):
        for gate in TattvaGate:
            registry.register_gate_provider(f"impostor_{gate.name}", Impostor(), gate)
        assert len(registry.violations) == 5

    def test_violations_are_copies(self, registry):
        registry.register_gate_provider("impostor", Impostor(), TattvaGate.PARSE)
        v1 = registry.violations
        v2 = registry.violations
        assert v1 == v2
        assert v1 is not v2  # defensive copy


# =============================================================================
# TESTS: __tattva__ self-description includes gate info
# =============================================================================


class TestTattvaDescription:

    def test_tattva_includes_gate_providers(self, registry):
        registry.register_gate_provider("parser", CapableParser(), TattvaGate.PARSE)
        tattva = registry.__tattva__
        assert "1 gate providers" in tattva["chaitanya"]

    def test_tattva_includes_violations(self, registry):
        registry.register_gate_provider("impostor", Impostor(), TattvaGate.PARSE)
        tattva = registry.__tattva__
        assert "violations: 1" in tattva["gadadhara"]


# =============================================================================
# TESTS: Full pipeline — all 5 gates with providers
# =============================================================================


class TestFullPipeline:

    def test_register_all_5_gates(self, registry):
        pairs = [
            ("parser", CapableParser(), TattvaGate.PARSE),
            ("validator", CapableValidator(), TattvaGate.VALIDATE),
            ("inferrer", CapableInferrer(), TattvaGate.EXECUTE),
            ("router", CapableRouter(), TattvaGate.RESULT),
            ("enforcer", CapableEnforcer(), TattvaGate.SYNC),
        ]
        for name, obj, gate in pairs:
            assert registry.register_gate_provider(name, obj, gate)

        assert registry.gate_provider_count() == 5
        assert registry.violations == []

        # Each gate has exactly 1 provider
        for gate in TattvaGate:
            assert registry.gate_provider_count(gate) == 1
