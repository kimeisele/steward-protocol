"""
LOTUS CLI - The Thin Entry Point
=================================

"From Thought to Chant."

This CLI is THIN. It delegates everything to:
    vibe_core/protocols/universal/semantic_router.py

The SemanticRouter already provides:
    Natural Language → CognitiveResult → MantraOpCode → Mahajana → Result

LOTUS CLI just:
    1. Parses user input
    2. Creates CognitiveResult
    3. Calls SemanticRouter.route()
    4. Displays result

NO MANUAL LABOR. The router CHANTS.

USAGE:
    steward chat "query"           # Routes via semantic router
    steward chat --explain "query" # Show routing path
    steward chat --table           # Show full routing table
"""

from typing import List

from vibe_core.protocols.cli import CLIMeta, register_cli
from vibe_core.protocols.cognition import CognitiveResult, IntentType
from vibe_core.protocols.universal.semantic_router import (
    SemanticRouter,
    SemanticRouteResult,
    get_semantic_router,
)


def _infer_intent_type(query: str) -> IntentType:
    """
    Infer IntentType from natural language.

    Simple keyword matching - the SemanticRouter handles the rest.
    """
    q = query.lower()

    if any(w in q for w in ("create", "make", "spawn", "new", "add")):
        return IntentType.EXECUTE
    elif any(w in q for w in ("find", "search", "get", "fetch", "show", "list")):
        return IntentType.QUERY
    elif any(w in q for w in ("route", "send", "dispatch", "forward")):
        return IntentType.ROUTE
    else:
        return IntentType.CHAT


@register_cli
class LotusCLI:
    """
    LOTUS CLI - Thin wrapper around SemanticRouter.

    Like a lotus flower that opens to reveal its inner beauty,
    this CLI opens to the full semantic routing stack:

        Layer 1 (User):      steward chat "create an agent"
                                  ↓
        Layer 0 (Cognitive): CognitiveResult(EXECUTE, SPAWN_COGNITION)
                                  ↓
        Layer -1 (Bridge):   MantraOpCode.ALLOC_MEM
                                  ↓
        Layer -2 (Router):   Mahajana.BRAHMA
                                  ↓
        Layer -3 (Execute):  Result

    The CLI is THIN. The protocols are THICK.
    """

    def __init__(self) -> None:
        self._router = get_semantic_router()

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata."""
        return CLIMeta(
            command="chat",
            description="Lotus CLI - Thin wrapper around SemanticRouter",
            domain="lotus",
            subcommands=["--explain", "--table", "--help"],
            tags=["lotus", "semantic", "router", "mahamantra"],
        )

    def run(self, args: List[str]) -> int:
        """Main entry point - delegates to SemanticRouter."""
        if not args or args[0] in ("--help", "-h", "help"):
            self._print_help()
            return 0

        # Parse flags
        explain = "--explain" in args
        show_table = "--table" in args
        args = [a for a in args if not a.startswith("--")]

        if show_table:
            return self._show_routing_table()

        if not args:
            self._print_help()
            return 0

        # Combine args as query
        query = " ".join(args)

        # Route via SemanticRouter
        return self._route(query, explain=explain)

    def _route(self, query: str, explain: bool = False) -> int:
        """Route query through semantic stack."""
        # Infer intent
        intent_type = _infer_intent_type(query)

        # Create minimal CognitiveResult
        cognitive = CognitiveResult(
            intent_type=intent_type,
            confidence=1.0,
        )

        # Route through semantic router
        result = self._router.route(cognitive)
        result.original_message = query

        if explain:
            self._print_explain(result)
        else:
            self._print_result(result)

        return 0 if result.success else 1

    def _print_result(self, result: SemanticRouteResult) -> None:
        """Print routing result."""
        print(f"[{result.mahajana.value.upper()}] Routed: {result.original_message}")
        print(f"  OpCode: {result.opcode.name}")
        print(f"  Quarter: {result.quarter} | Position: {result.position}")
        if result.is_head:
            print(f"  HEAD (Avatara-owned)")

    def _print_explain(self, result: SemanticRouteResult) -> None:
        """Print detailed routing explanation."""
        print(f"SEMANTIC ROUTE: {result.original_message}")
        print()
        print("PROCESSING PATH:")
        for i, step in enumerate(result.processing_path):
            indent = "  " * (i + 1)
            print(f"{indent}↓ {step}")
        print()
        print(f"RESULT:")
        print(f"  Intent: {result.intent_type.value}")
        print(f"  OpCode: {result.opcode.name}")
        print(f"  Mahajana: {result.mahajana.value.upper()}")
        print(f"  Quarter: {result.quarter} (of 4)")
        print(f"  Position: {result.position} (of 16)")
        print(f"  Confidence: {result.bridge_confidence:.2f}")
        print(f"  Source: {result.bridge_source}")
        if result.is_head:
            print(f"  HEAD: Yes (Avatara-owned position)")

    def _show_routing_table(self) -> int:
        """Show full routing table."""
        table = self._router.get_routing_table()

        print("SEMANTIC ROUTING TABLE")
        print("=" * 60)

        print("\nINTENT ROUTES:")
        for route in table.get("intent_routes", []):
            head = " [HEAD]" if route.get("is_head") else ""
            print(f"  {route['intent']:12} → {route['opcode']:16} → {route['mahajana'].upper()}{head}")

        print("\nSYSCALL ROUTES:")
        for route in table.get("syscall_routes", [])[:10]:
            head = " [HEAD]" if route.get("is_head") else ""
            print(f"  {route['syscall']:20} → {route['opcode']:16} → {route['mahajana'].upper()}{head}")

        return 0

    def _print_help(self) -> None:
        """Print help."""
        print("""
LOTUS CLI - The Thin Entry Point
=================================

USAGE:
    steward chat "your query here"
    steward chat --explain "query"     Show routing path
    steward chat --table               Show routing table

ARCHITECTURE:
    Layer 1 (User):      steward chat "create an agent"
                              ↓
    Layer 0 (Cognitive): CognitiveResult
                              ↓
    Layer -1 (Bridge):   IntentOpCodeBridge → MantraOpCode
                              ↓
    Layer -2 (Router):   MahajanaRouter → Mahajana
                              ↓
    Layer -3 (Execute):  Result

The CLI is THIN. The protocols do the work.
See: vibe_core/protocols/universal/semantic_router.py
""")


__all__ = ["LotusCLI"]
