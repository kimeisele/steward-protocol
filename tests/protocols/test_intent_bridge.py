"""
TEST INTENT-OPCODE BRIDGE
=========================

Verifies the semantic translation from IntentType to MantraOpCode.

THE BRIDGE MUST:
1. Translate all IntentTypes to valid MantraOpCodes
2. Handle SyscallType → OpCode mapping with high confidence
3. Handle route targets → OpCode mapping
4. Handle query types → OpCode mapping
5. Provide sensible defaults (never fail, always grace)
"""

import pytest

from vibe_core.protocols.cognition import IntentType, CognitiveResult
from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.protocols.universal.intent_bridge import (
    IntentOpCodeBridge,
    BridgeResult,
    get_bridge,
    translate,
    INTENT_TO_DEFAULT_OPCODE,
    SYSCALL_TO_OPCODE,
    ROUTE_TARGET_TO_OPCODE,
    QUERY_TYPE_TO_OPCODE,
)
from vibe_core.semantic_syscalls import SyscallType


class TestIntentBridgeBasics:
    """Basic bridge functionality tests."""

    def test_bridge_singleton(self):
        """get_bridge() returns singleton instance."""
        bridge1 = get_bridge()
        bridge2 = get_bridge()
        assert bridge1 is bridge2

    def test_all_intent_types_have_defaults(self):
        """Every IntentType has a default OpCode mapping."""
        for intent in IntentType:
            assert intent in INTENT_TO_DEFAULT_OPCODE, f"Missing default for {intent}"

    def test_all_syscall_types_have_mappings(self):
        """Every SyscallType has an OpCode mapping."""
        for syscall in SyscallType:
            assert syscall in SYSCALL_TO_OPCODE, f"Missing mapping for {syscall}"


class TestIntentTypeTranslation:
    """Test IntentType → OpCode default translations."""

    def test_chat_intent_defaults_to_exec_service(self):
        """CHAT intent routes to EXEC_SERVICE (Prahlada)."""
        result = CognitiveResult(intent_type=IntentType.CHAT, confidence=0.9)
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.EXTEND_CAP
        assert "intent:chat" in bridge_result.source

    def test_execute_intent_defaults_to_exec_service(self):
        """EXECUTE intent without syscall routes to EXEC_SERVICE."""
        result = CognitiveResult(intent_type=IntentType.EXECUTE, confidence=0.9)
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.EXTEND_CAP

    def test_query_intent_defaults_to_fetch_res(self):
        """QUERY intent routes to FETCH_RES (Prahlada fetches)."""
        result = CognitiveResult(intent_type=IntentType.QUERY, confidence=0.9)
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.EXEC_OP

    def test_route_intent_defaults_to_resolve_req(self):
        """ROUTE intent without target routes to RESOLVE_REQ (Kumaras)."""
        result = CognitiveResult(intent_type=IntentType.ROUTE, confidence=0.9)
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.BIND_SYMBOL


class TestSyscallTypeTranslation:
    """Test SyscallType → OpCode translations (high priority).

    SSOT: substrate/opcode.py defines Position = OpCode = Mahajana
    - Position 1: BRAHMA → LOAD_ROOT (Creation)
    - Position 2: NARADA → ALLOC_MEM (Communication)
    - Position 3: SHAMBHU → INIT_THREAD (Destruction)
    - Position 7: MANU → DHARMA_TEST (Law)
    - Position 11: BHISHMA → LEDGER_SIGN (Vow)
    """

    def test_spawn_cognition_maps_to_load_root(self):
        """SPAWN_COGNITION → LOAD_ROOT (Position 1 = Brahma creates)."""
        result = CognitiveResult(intent_type=IntentType.EXECUTE, confidence=0.9, syscall_type="SPAWN_COGNITION")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.LOAD_ROOT
        assert bridge_result.confidence >= 0.9
        assert "syscall" in bridge_result.source

    def test_destroy_cognition_maps_to_init_thread(self):
        """DESTROY_COGNITION → INIT_THREAD (Position 3 = Shambhu destroys)."""
        result = CognitiveResult(intent_type=IntentType.EXECUTE, confidence=0.9, syscall_type="DESTROY_COGNITION")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.INIT_THREAD

    def test_grant_mandate_maps_to_dharma_test(self):
        """GRANT_MANDATE → DHARMA_TEST (Position 7 = Manu binds permissions)."""
        result = CognitiveResult(intent_type=IntentType.EXECUTE, confidence=0.9, syscall_type="GRANT_MANDATE")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.DHARMA_TEST

    def test_swear_oath_maps_to_ledger_sign(self):
        """SWEAR_OATH → LEDGER_SIGN (Position 11 = Bhishma commits vows)."""
        result = CognitiveResult(intent_type=IntentType.EXECUTE, confidence=0.9, syscall_type="SWEAR_OATH")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.LEDGER_SIGN

    def test_broadcast_event_maps_to_alloc_mem(self):
        """BROADCAST_EVENT → ALLOC_MEM (Position 2 = Narada broadcasts)."""
        result = CognitiveResult(intent_type=IntentType.EXECUTE, confidence=0.9, syscall_type="BROADCAST_EVENT")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.ALLOC_MEM


class TestRouteTargetTranslation:
    """Test route target → OpCode translations."""

    def test_envoy_target_maps_to_exec_service(self):
        """Route to 'envoy' → EXEC_SERVICE."""
        result = CognitiveResult(intent_type=IntentType.ROUTE, confidence=0.9, target="envoy")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.EXTEND_CAP
        assert "target:envoy" in bridge_result.source

    def test_kernel_target_maps_to_sys_wake(self):
        """Route to 'kernel' → SYS_WAKE."""
        result = CognitiveResult(intent_type=IntentType.ROUTE, confidence=0.9, target="kernel")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.SYS_WAKE

    def test_herald_target_maps_to_pulse_sync(self):
        """Route to 'herald' → PULSE_SYNC (messenger)."""
        result = CognitiveResult(intent_type=IntentType.ROUTE, confidence=0.9, target="herald")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.DHARMA_TEST

    def test_unknown_target_falls_back_to_resolve_req(self):
        """Unknown target falls back to RESOLVE_REQ with low confidence."""
        result = CognitiveResult(intent_type=IntentType.ROUTE, confidence=0.9, target="unknown_agent_xyz")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.BIND_SYMBOL
        assert bridge_result.confidence <= 0.6  # Low confidence for fallback
        assert "unknown" in bridge_result.source


class TestQueryTypeTranslation:
    """Test query type → OpCode translations."""

    def test_status_query_maps_to_fetch_res(self):
        """Query type 'status' → FETCH_RES."""
        result = CognitiveResult(intent_type=IntentType.QUERY, confidence=0.9, query_type="status")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.EXEC_OP

    def test_health_query_maps_to_assert_truth(self):
        """Query type 'health' → ASSERT_TRUTH (verification)."""
        result = CognitiveResult(intent_type=IntentType.QUERY, confidence=0.9, query_type="health")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.COMPILE_AST

    def test_config_query_maps_to_load_root(self):
        """Query type 'config' → LOAD_ROOT."""
        result = CognitiveResult(intent_type=IntentType.QUERY, confidence=0.9, query_type="config")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.LOAD_ROOT


class TestTranslationPriority:
    """Test that translation follows correct priority."""

    def test_syscall_takes_priority_over_default(self):
        """SyscallType overrides default IntentType mapping."""
        # EXECUTE defaults to EXTEND_CAP
        # But SPAWN_COGNITION should override to LOAD_ROOT (Brahma)
        result = CognitiveResult(intent_type=IntentType.EXECUTE, confidence=0.9, syscall_type="SPAWN_COGNITION")
        bridge_result = translate(result)
        assert bridge_result.opcode == MantraOpCode.LOAD_ROOT
        assert "syscall" in bridge_result.source

    def test_target_takes_priority_for_route(self):
        """Target overrides default for ROUTE intent."""
        result = CognitiveResult(intent_type=IntentType.ROUTE, confidence=0.9, target="herald")
        bridge_result = translate(result)
        # ROUTE defaults to RESOLVE_REQ, but herald → PULSE_SYNC
        assert bridge_result.opcode == MantraOpCode.DHARMA_TEST


class TestBridgeDiscoverability:
    """Test GAD-000 Discoverability compliance."""

    def test_get_all_mappings_returns_complete_data(self):
        """get_all_mappings() provides full discoverability."""
        bridge = get_bridge()
        mappings = bridge.get_all_mappings()

        assert "intent_defaults" in mappings
        assert "syscall_mappings" in mappings
        assert "route_targets" in mappings
        assert "query_types" in mappings

        # Verify structure
        assert len(mappings["intent_defaults"]) == len(IntentType)
        assert len(mappings["syscall_mappings"]) == len(SyscallType)

    def test_all_mappings_have_valid_opcodes(self):
        """All mapped OpCodes are valid MantraOpCode values."""
        valid_opcodes = {op.name for op in MantraOpCode}

        bridge = get_bridge()
        mappings = bridge.get_all_mappings()

        for category, items in mappings.items():
            for item in items:
                assert item["opcode"] in valid_opcodes, f"Invalid opcode {item['opcode']} in {category}"


class TestRawTranslation:
    """Test translate_raw() convenience method."""

    def test_translate_raw_without_details(self):
        """translate_raw() works with just intent_type."""
        bridge = get_bridge()
        result = bridge.translate_raw(IntentType.CHAT)
        assert result.opcode == MantraOpCode.EXTEND_CAP

    def test_translate_raw_with_syscall(self):
        """translate_raw() handles syscall_type parameter."""
        bridge = get_bridge()
        result = bridge.translate_raw(IntentType.EXECUTE, syscall_type="RECORD_KARMA")
        assert result.opcode == MantraOpCode.LEDGER_SIGN

    def test_translate_raw_with_target(self):
        """translate_raw() handles target parameter."""
        bridge = get_bridge()
        result = bridge.translate_raw(IntentType.ROUTE, target="oracle")
        assert result.opcode == MantraOpCode.EXEC_OP


class TestBridgeResult:
    """Test BridgeResult dataclass."""

    def test_bridge_result_is_frozen(self):
        """BridgeResult is immutable."""
        result = BridgeResult(opcode=MantraOpCode.EXTEND_CAP, confidence=0.9, source="test")
        with pytest.raises(Exception):  # FrozenInstanceError
            result.opcode = MantraOpCode.EXEC_OP

    def test_bridge_result_optional_notes(self):
        """BridgeResult.notes is optional."""
        result = BridgeResult(opcode=MantraOpCode.EXTEND_CAP, confidence=0.9, source="test")
        assert result.notes is None

        result_with_notes = BridgeResult(
            opcode=MantraOpCode.EXTEND_CAP, confidence=0.9, source="test", notes="Some explanation"
        )
        assert result_with_notes.notes == "Some explanation"


class TestSemanticConsistency:
    """Test that mappings are semantically consistent.

    SSOT: substrate/opcode.py defines Position = OpCode = Mahajana
    - Position 1: BRAHMA → LOAD_ROOT (Creation)
    - Position 2: NARADA → ALLOC_MEM (Communication/Allocation)
    - Position 3: SHAMBHU → INIT_THREAD (Destruction)
    - Position 11: BHISHMA → LEDGER_SIGN (Vow/Commitment)
    """

    def test_creation_syscalls_map_to_creation_opcodes(self):
        """Creation-related syscalls map to BRAHMA (LOAD_ROOT)."""
        # SPAWN = creation → LOAD_ROOT (Position 1 = Brahma)
        assert SYSCALL_TO_OPCODE[SyscallType.SPAWN_COGNITION] == MantraOpCode.LOAD_ROOT
        # ALLOCATE = allocation → ALLOC_MEM (Position 2 = Narada handles communication/allocation)
        assert SYSCALL_TO_OPCODE[SyscallType.ALLOCATE_PRANA] == MantraOpCode.ALLOC_MEM

    def test_destruction_syscalls_map_to_cleanup_opcodes(self):
        """Destruction-related syscalls map to SHAMBHU (INIT_THREAD)."""
        # DESTROY = destruction → INIT_THREAD (Position 3 = Shambhu)
        assert SYSCALL_TO_OPCODE[SyscallType.DESTROY_COGNITION] == MantraOpCode.INIT_THREAD
        assert SYSCALL_TO_OPCODE[SyscallType.REVOKE_MANDATE] == MantraOpCode.INIT_THREAD

    def test_commitment_syscalls_map_to_ledger_sign(self):
        """Commitment-related syscalls map to BHISHMA (LEDGER_SIGN)."""
        assert SYSCALL_TO_OPCODE[SyscallType.SWEAR_OATH] == MantraOpCode.LEDGER_SIGN
        assert SYSCALL_TO_OPCODE[SyscallType.RECORD_KARMA] == MantraOpCode.LEDGER_SIGN

    def test_communication_syscalls_map_to_alloc_mem(self):
        """Communication-related syscalls map to NARADA (ALLOC_MEM)."""
        # BROADCAST = communication → ALLOC_MEM (Position 2 = Narada)
        assert SYSCALL_TO_OPCODE[SyscallType.BROADCAST_EVENT] == MantraOpCode.ALLOC_MEM
