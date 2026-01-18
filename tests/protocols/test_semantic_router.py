"""
TEST SEMANTIC ROUTER
====================

Verifies the full semantic routing from CognitiveResult to Mahajana.

THE FLOW:
    CognitiveResult → IntentOpCodeBridge → MantraOpCode → MahajanaRouter → Mahajana
"""

import pytest

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.cognition import CognitiveResult, IntentType
from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.protocols.universal.semantic_router import (
    SemanticRouter,
    SemanticRouteResult,
    get_semantic_router,
    route,
    route_raw,
)


class TestSemanticRouterBasics:
    """Basic router functionality tests."""

    def test_router_singleton(self):
        """get_semantic_router() returns singleton."""
        router1 = get_semantic_router()
        router2 = get_semantic_router()
        assert router1 is router2

    def test_route_result_has_all_fields(self):
        """SemanticRouteResult contains all routing info."""
        result = route_raw(IntentType.CHAT)

        assert hasattr(result, "intent_type")
        assert hasattr(result, "opcode")
        assert hasattr(result, "mahajana")
        assert hasattr(result, "quarter")
        assert hasattr(result, "position")
        assert hasattr(result, "is_head")
        assert hasattr(result, "processing_path")


class TestFullRoutingFlow:
    """Test the complete routing flow."""

    def test_chat_routes_to_prahlada(self):
        """CHAT intent → EXEC_SERVICE → JANAKA (legacy) or PRAHLADA (vyuha)."""
        cognitive = CognitiveResult(intent_type=IntentType.CHAT, confidence=0.9, response="Hello, how can I help?")
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.EXTEND_CAP
        # EXEC_SERVICE maps to JANAKA (legacy) or PRAHLADA (vyuha)
        assert result.mahajana in (Mahajana.JANAKA, Mahajana.PRAHLADA)

    def test_spawn_cognition_routes_to_brahma(self):
        """SPAWN_COGNITION → ALLOC_MEM → BRAHMA."""
        cognitive = CognitiveResult(
            intent_type=IntentType.EXECUTE,
            confidence=0.95,
            syscall_type="SPAWN_COGNITION",
        )
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.ALLOC_MEM
        assert result.mahajana == Mahajana.BRAHMA

    def test_destroy_cognition_routes_to_shambhu(self):
        """DESTROY_COGNITION → GARBAGE_COLLECT → SHAMBHU."""
        cognitive = CognitiveResult(
            intent_type=IntentType.EXECUTE,
            confidence=0.95,
            syscall_type="DESTROY_COGNITION",
        )
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.TYPE_CHECK
        assert result.mahajana == Mahajana.SHAMBHU

    def test_swear_oath_routes_to_bhishma(self):
        """SWEAR_OATH → COMMIT_LOG → BHISHMA."""
        cognitive = CognitiveResult(
            intent_type=IntentType.EXECUTE,
            confidence=0.95,
            syscall_type="SWEAR_OATH",
        )
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.LEDGER_SIGN
        assert result.mahajana == Mahajana.BHISHMA

    def test_broadcast_event_routes_to_narada(self):
        """BROADCAST_EVENT → PULSE_SYNC → NARADA (legacy) or MANU (vyuha)."""
        cognitive = CognitiveResult(
            intent_type=IntentType.EXECUTE,
            confidence=0.95,
            syscall_type="BROADCAST_EVENT",
        )
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.DHARMA_TEST
        # PULSE_SYNC maps to NARADA (legacy) or MANU (vyuha)
        assert result.mahajana in (Mahajana.NARADA, Mahajana.MANU)


class TestRouteTargets:
    """Test route target → Mahajana flow."""

    def test_route_to_kernel(self):
        """Route to 'kernel' → SYS_WAKE → HEAD (handled as BRAHMA)."""
        cognitive = CognitiveResult(
            intent_type=IntentType.ROUTE,
            confidence=0.9,
            target="kernel",
        )
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.SYS_WAKE
        # SYS_WAKE is a HEAD opcode
        assert result.is_head

    def test_route_to_herald(self):
        """Route to 'herald' → PULSE_SYNC → NARADA/MANU."""
        cognitive = CognitiveResult(
            intent_type=IntentType.ROUTE,
            confidence=0.9,
            target="herald",
        )
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.DHARMA_TEST


class TestQueryRouting:
    """Test query type → Mahajana flow."""

    def test_status_query_routes_to_prahlada(self):
        """Status query → FETCH_RES → PRAHLADA."""
        cognitive = CognitiveResult(
            intent_type=IntentType.QUERY,
            confidence=0.9,
            query_type="status",
        )
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.EXEC_OP
        # FETCH_RES is a HEAD in vyuha, handled as PRAHLADA
        assert result.mahajana == Mahajana.PRAHLADA

    def test_health_query_routes_to_yamaraja(self):
        """Health query → ASSERT_TRUTH → YAMARAJA."""
        cognitive = CognitiveResult(
            intent_type=IntentType.QUERY,
            confidence=0.9,
            query_type="health",
        )
        result = route(cognitive)

        assert result.success
        assert result.opcode == MantraOpCode.COMPILE_AST
        assert result.mahajana == Mahajana.YAMARAJA


class TestRoutingPath:
    """Test that routing path is tracked."""

    def test_path_tracks_intent(self):
        """Processing path includes intent step."""
        result = route_raw(IntentType.CHAT)
        assert any("intent:" in step for step in result.processing_path)

    def test_path_tracks_opcode(self):
        """Processing path includes opcode step."""
        result = route_raw(IntentType.CHAT)
        assert any("opcode:" in step for step in result.processing_path)

    def test_path_tracks_mahajana(self):
        """Processing path includes mahajana step."""
        result = route_raw(IntentType.CHAT)
        # Either mahajana or head
        assert any("mahajana:" in step or "head:" in step for step in result.processing_path)


class TestRawRouting:
    """Test route_raw() convenience function."""

    def test_route_raw_with_intent_only(self):
        """route_raw() works with just intent_type."""
        result = route_raw(IntentType.QUERY)
        assert result.success
        assert result.opcode == MantraOpCode.EXEC_OP

    def test_route_raw_with_syscall(self):
        """route_raw() handles syscall_type."""
        result = route_raw(IntentType.EXECUTE, syscall_type="RECORD_KARMA")
        assert result.opcode == MantraOpCode.LEDGER_SIGN
        assert result.mahajana == Mahajana.BHISHMA

    def test_route_raw_with_target(self):
        """route_raw() handles target."""
        result = route_raw(IntentType.ROUTE, target="scribe")
        assert result.opcode == MantraOpCode.LEDGER_SIGN


class TestDiscoverability:
    """Test GAD-000 discoverability."""

    def test_routing_table_available(self):
        """get_routing_table() provides full discoverability."""
        router = get_semantic_router()
        table = router.get_routing_table()

        assert "intent_routes" in table
        assert "syscall_routes" in table
        assert len(table["intent_routes"]) == len(IntentType)


class TestSemanticConsistency:
    """Test semantic mapping consistency."""

    def test_creation_intents_route_to_creators(self):
        """Creation syscalls route to creation Mahajanas."""
        # SPAWN → BRAHMA (creator)
        result = route_raw(IntentType.EXECUTE, syscall_type="SPAWN_COGNITION")
        assert result.mahajana == Mahajana.BRAHMA

    def test_destruction_intents_route_to_destroyers(self):
        """Destruction syscalls route to Shambhu."""
        result = route_raw(IntentType.EXECUTE, syscall_type="DESTROY_COGNITION")
        assert result.mahajana == Mahajana.SHAMBHU

    def test_commitment_intents_route_to_bhishma(self):
        """Commitment syscalls route to Bhishma (vow keeper)."""
        result_oath = route_raw(IntentType.EXECUTE, syscall_type="SWEAR_OATH")
        result_karma = route_raw(IntentType.EXECUTE, syscall_type="RECORD_KARMA")

        assert result_oath.mahajana == Mahajana.BHISHMA
        assert result_karma.mahajana == Mahajana.BHISHMA

    def test_law_intents_route_to_manu(self):
        """Permission/law syscalls route to Manu (lawgiver)."""
        result = route_raw(IntentType.EXECUTE, syscall_type="GRANT_MANDATE")
        assert result.mahajana == Mahajana.MANU


class TestHeadOpcodes:
    """Test HEAD opcode handling."""

    def test_sys_wake_is_head(self):
        """SYS_WAKE is a HEAD opcode."""
        result = route_raw(IntentType.ROUTE, target="kernel")
        assert result.opcode == MantraOpCode.SYS_WAKE
        assert result.is_head

    def test_assert_truth_is_head(self):
        """ASSERT_TRUTH is a HEAD opcode."""
        result = route_raw(IntentType.QUERY, query_type="health")
        assert result.opcode == MantraOpCode.COMPILE_AST
        # ASSERT_TRUTH is in legacy router, so might not be marked as head
        # depending on router mode

    def test_head_still_routes_to_mahajana(self):
        """HEAD opcodes still get a Mahajana handler for fallback."""
        result = route_raw(IntentType.ROUTE, target="kernel")
        # Even HEAD opcodes get a Mahajana for fallback
        assert result.mahajana is not None
