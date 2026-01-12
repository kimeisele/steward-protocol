"""
SEMANTIC ROUTER - The Full Flow
================================

"From Thought to Chant."

This module provides the complete semantic routing from natural language
intent to Mahajana execution, closing the full loop:

    Natural Language → CognitiveResult → MantraOpCode → Mahajana → Result

ARCHITECTURE (The Semantic Stack):
    Layer 1 (User):      "create an agent"
                              ↓
    Layer 0 (Cognitive): OperatorCognitiveProtocol.process_intent()
                              ↓
                        CognitiveResult(IntentType.EXECUTE, syscall="SPAWN_COGNITION")
                              ↓
    Layer -1 (Bridge):   IntentOpCodeBridge.translate()
                              ↓
                        MantraOpCode.ALLOC_MEM
                              ↓
    Layer -2 (Router):   MahajanaRouter.route()
                              ↓
                        Mahajana.BRAHMA (Creator)
                              ↓
    Layer -3 (Execute):  Mahajana.handle() → Result

THE SEMANTIC ROUTER combines all layers into one coherent flow.
This is the "steward chat 'anything'" protocol.

STRICT TYPING (NO ANY):
Per PROMPT.md §IV.1 - All types are explicit.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from datetime import datetime

from vibe_core.protocols.cognition import (
    CognitiveResult,
    CognitiveContext,
    IntentType,
)
from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.protocols.universal.intent_bridge import (
    IntentOpCodeBridge,
    BridgeResult,
    get_bridge,
)
from vibe_core.protocols.mahajanas.router import (
    MahajanaRouter,
    Mahajana,
    MahajanaRoute,
    get_router,
)


# =============================================================================
# SEMANTIC ROUTE RESULT
# =============================================================================

@dataclass
class SemanticRouteResult:
    """
    Complete result of semantic routing.

    Contains:
    - Original intent (CognitiveResult)
    - Bridge translation (MantraOpCode + confidence)
    - Mahajana routing (who handles this)
    - Execution metadata

    GAD-000 Compliant: All fields explicit, machine-readable.
    """

    # Input
    intent_type: IntentType
    original_message: Optional[str] = None

    # Bridge layer
    opcode: MantraOpCode = MantraOpCode.EXTEND_CAP
    bridge_confidence: float = 0.0
    bridge_source: str = "unknown"

    # Router layer
    mahajana: Mahajana = Mahajana.PRAHLADA  # Default handler
    quarter: int = 0
    position: int = 0
    is_head: bool = False

    # Result
    success: bool = False
    response: Optional[str] = None
    error: Optional[str] = None

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    processing_path: List[str] = field(default_factory=list)

    def add_to_path(self, step: str) -> None:
        """Track the routing path (for debugging/observability)."""
        self.processing_path.append(step)


# =============================================================================
# SEMANTIC ROUTER
# =============================================================================

class SemanticRouter:
    """
    The Full Semantic Flow.

    Combines:
    1. IntentOpCodeBridge (CognitiveResult → MantraOpCode)
    2. MahajanaRouter (MantraOpCode → Mahajana)

    Usage:
        router = SemanticRouter()

        # From CognitiveResult (post-cognitive processing)
        result = router.route(cognitive_result)
        print(f"Handled by: {result.mahajana}")

        # From raw intent components
        result = router.route_raw(IntentType.EXECUTE, syscall_type="SPAWN_COGNITION")
        print(f"OpCode: {result.opcode}, Mahajana: {result.mahajana}")
    """

    def __init__(self):
        """Initialize with default bridge and router."""
        self._bridge = get_bridge()
        self._router = get_router()

    def route(self, cognitive_result: CognitiveResult) -> SemanticRouteResult:
        """
        Route a CognitiveResult through the semantic stack.

        Args:
            cognitive_result: Result from cognitive processing

        Returns:
            SemanticRouteResult with full routing information
        """
        result = SemanticRouteResult(
            intent_type=cognitive_result.intent_type,
        )
        result.add_to_path(f"intent:{cognitive_result.intent_type.value}")

        # Step 1: Bridge - translate to OpCode
        try:
            bridge_result = self._bridge.translate(cognitive_result)
            result.opcode = bridge_result.opcode
            result.bridge_confidence = bridge_result.confidence
            result.bridge_source = bridge_result.source
            result.add_to_path(f"opcode:{bridge_result.opcode.name}")
        except Exception as e:
            result.error = f"Bridge failed: {e}"
            result.add_to_path(f"bridge_error:{e}")
            return result

        # Step 2: Router - get Mahajana
        try:
            route = self._router.get_route(result.opcode)
            result.mahajana = route.mahajana
            result.quarter = route.quarter
            result.position = route.position
            result.is_head = self._is_head_opcode(result.opcode)
            result.add_to_path(f"mahajana:{route.mahajana.value}")
        except ValueError:
            # HEAD opcode - not in worker table
            result.is_head = True
            result.mahajana = self._get_head_handler(result.opcode)
            result.add_to_path(f"head:{result.mahajana.value}")
        except Exception as e:
            result.error = f"Router failed: {e}"
            result.add_to_path(f"router_error:{e}")
            return result

        result.success = True
        return result

    def route_raw(
        self,
        intent_type: IntentType,
        syscall_type: Optional[str] = None,
        target: Optional[str] = None,
        query_type: Optional[str] = None,
        message: Optional[str] = None,
    ) -> SemanticRouteResult:
        """
        Route from raw intent components.

        Convenience method when you don't have a full CognitiveResult.
        """
        # Build minimal CognitiveResult
        cognitive = CognitiveResult(
            intent_type=intent_type,
            confidence=1.0,
            syscall_type=syscall_type,
            target=target,
            query_type=query_type,
        )

        result = self.route(cognitive)
        result.original_message = message
        return result

    def _is_head_opcode(self, opcode: MantraOpCode) -> bool:
        """Check if opcode is a HEAD (Avatara-owned)."""
        from vibe_core.protocols.mahajanas.router import HEAD_OPCODES
        return opcode in HEAD_OPCODES

    def _get_head_handler(self, opcode: MantraOpCode) -> Mahajana:
        """
        Get the Mahajana-equivalent handler for HEAD opcodes.

        HEADs are owned by Avataras, but we still need a Mahajana
        for fallback handling.

        Mapping:
            SYS_WAKE → BRAHMA (Prithu's domain is creation/infrastructure)
            ASSERT_TRUTH → YAMARAJA (Vyasa's domain is dharma/truth)
            FETCH_RES → PRAHLADA (Parashurama's domain is resources)
            CACHE_STATE → SHUKA (Nrisimha's domain is preservation)
        """
        from vibe_core.protocols.mahajanas.router import HEAD_OPCODES

        head_to_mahajana = {
            MantraOpCode.SYS_WAKE: Mahajana.BRAHMA,
            MantraOpCode.COMPILE_AST: Mahajana.YAMARAJA,
            MantraOpCode.EXEC_OP: Mahajana.PRAHLADA,
            MantraOpCode.YIELD_CPU: Mahajana.SHUKA,
        }
        return head_to_mahajana.get(opcode, Mahajana.PRAHLADA)

    def get_routing_table(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get the full routing table for discoverability.

        GAD-000: AI can discover all possible routes.
        """
        mappings = self._bridge.get_all_mappings()

        # Enhance with Mahajana info
        enhanced = {
            "intent_routes": [],
            "syscall_routes": [],
            "target_routes": [],
            "query_routes": [],
        }

        # Intent defaults
        for item in mappings["intent_defaults"]:
            opcode = MantraOpCode(item["opcode"].lower())
            try:
                route = self._router.get_route(opcode)
                enhanced["intent_routes"].append({
                    "intent": item["intent"],
                    "opcode": item["opcode"],
                    "mahajana": route.mahajana.value,
                    "quarter": route.quarter,
                })
            except ValueError:
                # HEAD opcode
                enhanced["intent_routes"].append({
                    "intent": item["intent"],
                    "opcode": item["opcode"],
                    "mahajana": self._get_head_handler(opcode).value,
                    "quarter": 0,
                    "is_head": True,
                })

        # Syscall routes
        for item in mappings["syscall_mappings"]:
            opcode = MantraOpCode(item["opcode"].lower())
            try:
                route = self._router.get_route(opcode)
                enhanced["syscall_routes"].append({
                    "syscall": item["syscall"],
                    "opcode": item["opcode"],
                    "mahajana": route.mahajana.value,
                })
            except ValueError:
                enhanced["syscall_routes"].append({
                    "syscall": item["syscall"],
                    "opcode": item["opcode"],
                    "mahajana": self._get_head_handler(opcode).value,
                    "is_head": True,
                })

        return enhanced


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_semantic_router: Optional[SemanticRouter] = None


def get_semantic_router() -> SemanticRouter:
    """Get the global SemanticRouter instance."""
    global _semantic_router
    if _semantic_router is None:
        _semantic_router = SemanticRouter()
    return _semantic_router


def route(cognitive_result: CognitiveResult) -> SemanticRouteResult:
    """Convenience function: Route a CognitiveResult."""
    return get_semantic_router().route(cognitive_result)


def route_raw(
    intent_type: IntentType,
    syscall_type: Optional[str] = None,
    target: Optional[str] = None,
    query_type: Optional[str] = None,
) -> SemanticRouteResult:
    """Convenience function: Route from raw components."""
    return get_semantic_router().route_raw(
        intent_type, syscall_type, target, query_type
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "SemanticRouter",
    "SemanticRouteResult",
    "get_semantic_router",
    "route",
    "route_raw",
]
