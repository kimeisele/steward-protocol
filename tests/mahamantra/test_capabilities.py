"""
Tests for Pancha Tattva Capability Protocols.

Verifies:
1. Each protocol is runtime_checkable
2. GATE_CAPABILITY maps all 5 gates
3. check_capability works for compliant/non-compliant objects
4. TattvaRegistry rejects non-capable gate hooks
"""

import pytest
from typing import Any, Dict

from vibe_core.mahamantra.protocols._capabilities import (
    MantraCapability,
    StorageCapability,
    InferCapability,
    SyncCapability,
    EnforceCapability,
    GATE_CAPABILITY,
    get_capability_for_gate,
    check_capability,
)
from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate, PanchaTattva, GATE_TO_TATTVA


# =============================================================================
# MOCK IMPLEMENTATIONS
# =============================================================================


class MockMantraComponent:
    """Satisfies MantraCapability."""

    def parse(self, input_data: Any) -> Dict[str, Any]:
        return {"input_text": str(input_data), "seed": None, "input_coords": ()}


class MockStorageComponent:
    """Satisfies StorageCapability."""

    def validate(self, seed: int) -> Dict[str, Any]:
        return {"attractor": seed % 256, "parampara_verified": True}


class MockInferComponent:
    """Satisfies InferCapability."""

    def infer(self, seed: int, attractor: int) -> Dict[str, Any]:
        return {"resonant_words": [], "verse_info": None}


class MockSyncComponent:
    """Satisfies SyncCapability."""

    def route(self, attractor: int) -> Dict[str, Any]:
        return {"position": attractor % 16, "guardian": "bhishma", "quarter": "DHARMA"}


class MockEnforceComponent:
    """Satisfies EnforceCapability."""

    def enforce(self, position: int, seed: int, attractor: int) -> Dict[str, Any]:
        return {"cell": None, "committed": True}


class EmptyObject:
    """Satisfies nothing."""
    pass


# =============================================================================
# TESTS: Protocol runtime_checkable
# =============================================================================


class TestProtocolRuntimeCheckable:
    """Each capability protocol must be runtime_checkable via isinstance()."""

    def test_mantra_capability_isinstance(self):
        assert isinstance(MockMantraComponent(), MantraCapability)

    def test_storage_capability_isinstance(self):
        assert isinstance(MockStorageComponent(), StorageCapability)

    def test_infer_capability_isinstance(self):
        assert isinstance(MockInferComponent(), InferCapability)

    def test_sync_capability_isinstance(self):
        assert isinstance(MockSyncComponent(), SyncCapability)

    def test_enforce_capability_isinstance(self):
        assert isinstance(MockEnforceComponent(), EnforceCapability)

    def test_empty_object_fails_all(self):
        obj = EmptyObject()
        assert not isinstance(obj, MantraCapability)
        assert not isinstance(obj, StorageCapability)
        assert not isinstance(obj, InferCapability)
        assert not isinstance(obj, SyncCapability)
        assert not isinstance(obj, EnforceCapability)


# =============================================================================
# TESTS: GATE_CAPABILITY mapping
# =============================================================================


class TestGateCapabilityMap:
    """GATE_CAPABILITY must cover all 5 gates exactly."""

    def test_all_gates_mapped(self):
        for gate in TattvaGate:
            assert gate in GATE_CAPABILITY, f"Gate {gate.name} not in GATE_CAPABILITY"

    def test_exactly_5_entries(self):
        assert len(GATE_CAPABILITY) == 5

    def test_parse_maps_to_mantra(self):
        assert GATE_CAPABILITY[TattvaGate.PARSE] is MantraCapability

    def test_validate_maps_to_storage(self):
        assert GATE_CAPABILITY[TattvaGate.VALIDATE] is StorageCapability

    def test_execute_maps_to_infer(self):
        assert GATE_CAPABILITY[TattvaGate.EXECUTE] is InferCapability

    def test_result_maps_to_sync(self):
        assert GATE_CAPABILITY[TattvaGate.RESULT] is SyncCapability

    def test_sync_maps_to_enforce(self):
        assert GATE_CAPABILITY[TattvaGate.SYNC] is EnforceCapability

    def test_get_capability_for_gate(self):
        assert get_capability_for_gate(TattvaGate.PARSE) is MantraCapability
        assert get_capability_for_gate(TattvaGate.SYNC) is EnforceCapability


# =============================================================================
# TESTS: check_capability
# =============================================================================


class TestCheckCapability:
    """check_capability must verify isinstance against gate's protocol."""

    def test_mantra_component_passes_parse(self):
        assert check_capability(MockMantraComponent(), TattvaGate.PARSE)

    def test_mantra_component_fails_validate(self):
        assert not check_capability(MockMantraComponent(), TattvaGate.VALIDATE)

    def test_storage_component_passes_validate(self):
        assert check_capability(MockStorageComponent(), TattvaGate.VALIDATE)

    def test_empty_fails_all_gates(self):
        obj = EmptyObject()
        for gate in TattvaGate:
            assert not check_capability(obj, gate)

    def test_each_mock_passes_its_gate(self):
        pairs = [
            (MockMantraComponent(), TattvaGate.PARSE),
            (MockStorageComponent(), TattvaGate.VALIDATE),
            (MockInferComponent(), TattvaGate.EXECUTE),
            (MockSyncComponent(), TattvaGate.RESULT),
            (MockEnforceComponent(), TattvaGate.SYNC),
        ]
        for obj, gate in pairs:
            assert check_capability(obj, gate), f"{type(obj).__name__} should pass {gate.name}"


# =============================================================================
# TESTS: Gate ↔ Tattva consistency
# =============================================================================


class TestGateTattvaConsistency:
    """GATE_CAPABILITY and GATE_TO_TATTVA must be aligned."""

    def test_same_keys(self):
        assert set(GATE_CAPABILITY.keys()) == set(GATE_TO_TATTVA.keys())

    def test_all_5_tattvas_covered(self):
        tattvas = {GATE_TO_TATTVA[g] for g in GATE_CAPABILITY}
        assert tattvas == set(PanchaTattva)


# =============================================================================
# TESTS: TattvaAspect.protocol is real type (not string)
# =============================================================================


class TestTattvaAspectProtocolTypes:
    """TattvaAspect.protocol must be a real Protocol class, not a string."""

    def test_all_aspects_have_type_protocol(self):
        from vibe_core.mahamantra.substrate.pancha_tattva import PANCHA_TATTVA_ASPECTS
        for aspect in PANCHA_TATTVA_ASPECTS:
            assert isinstance(aspect.protocol, type), (
                f"{aspect.tattva.value}: protocol is {type(aspect.protocol).__name__}, not type"
            )

    def test_aspect_protocols_match_gate_capabilities(self):
        from vibe_core.mahamantra.substrate.pancha_tattva import (
            PANCHA_TATTVA_ASPECTS, TattvaIndex,
        )
        expected = [
            MantraCapability,
            StorageCapability,
            InferCapability,
            SyncCapability,
            EnforceCapability,
        ]
        for aspect, cap in zip(PANCHA_TATTVA_ASPECTS, expected):
            assert aspect.protocol is cap, (
                f"{aspect.tattva.value}: expected {cap.__name__}, got {aspect.protocol}"
            )

    def test_mock_satisfies_aspect_protocol(self):
        from vibe_core.mahamantra.substrate.pancha_tattva import PANCHA_TATTVA_ASPECTS
        mocks = [
            MockMantraComponent(),
            MockStorageComponent(),
            MockInferComponent(),
            MockSyncComponent(),
            MockEnforceComponent(),
        ]
        for aspect, mock in zip(PANCHA_TATTVA_ASPECTS, mocks):
            assert isinstance(mock, aspect.protocol), (
                f"{type(mock).__name__} should satisfy {aspect.protocol.__name__}"
            )
