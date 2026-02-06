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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xac560f43"  # GenesisByte: parampara % 37 == 0

from typing import List

from vibe_core.mahamantra.adapters.cli import (
    AdapterResult,
)
from vibe_core.mahamantra.adapters.cli import (
    get_adapter as get_mahamantra_cli_adapter,
)
from vibe_core.protocols.cli import CLIMeta, register_cli


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
        self._adapter = get_mahamantra_cli_adapter()

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

        # Parse flags (--debug is alias for --explain)
        explain = "--explain" in args or "--debug" in args or "-d" in args
        show_table = "--table" in args
        args = [a for a in args if not a.startswith("--") and a != "-d"]

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
        """Route query through Mahamantra holographic routing."""
        # The adapter handles execution mode internally. We pass 'observe' to just see
        # the routing without running the command, unless --execute is passed (future feature).
        result = self._adapter.execute(query, mode="observe")

        if explain:
            self._print_explain(result)
        else:
            self._print_result(result)

        return result.cli_result if result.executed and result.cli_result is not None else 0

    def _print_result(self, result: AdapterResult) -> None:
        """Print routing result from Mahamantra Adapter."""
        resonance = result.resonance
        guardian = resonance.get("guardian", "UNKNOWN").upper()
        position = resonance.get("position", "?")
        command = result.cli_command or "NO MATCH"
        candidates = ", ".join(result.candidates)

        print(f"[{guardian}] Routed to: {command}")
        print(f"  Position: {position}")
        print(f"  Candidates: {candidates}")
        if result.executed:
            print(f"  Execution Result: {result.cli_result}")

    def _print_explain(self, result: AdapterResult) -> None:
        """
        Print detailed routing explanation from the Mahamantra.
        This is the true "Invisible Backend".
        """
        from vibe_core.mahamantra.mahamantra.__main__ import _render_response

        # The __main__ module's renderer provides the canonical explanation.
        _render_response(result.resonance, result)

    def _show_routing_table(self) -> int:
        """Show full routing table from the Mahamantra Adapter."""
        self._adapter._discover_all_clis()  # Ensure fingerprints are computed
        table = self._adapter._cli_fingerprints

        print("MAHAMANTRA HOLOGRAPHIC ROUTING TABLE")
        print("=" * 60)
        print(f"{'COMMAND':<20} {'POSITION':<10} {'PAYLOAD_SIZE':<15} {'SEED'}")
        print("-" * 60)

        sorted_table = sorted(table.items(), key=lambda item: item[1].position)

        for command, fp in sorted_table:
            print(f"{command:<20} {fp.position:<10} {fp.payload_size:<15} {fp.seed}")

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
