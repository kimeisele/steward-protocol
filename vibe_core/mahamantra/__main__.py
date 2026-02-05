"""
MAHAMANTRA - THE KING
=====================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

python -m vibe_core.mahamantra "anything"

THAT'S IT. One entry. Krishna routes everything.

FLOW (9 NavaBhakti):
    Input → mahamantra(input) → SRAVANAM → ... → ATMA_NIVEDANAM → Response

NO HARDCODED COMMANDS. Pure resonance routing.
The system FEELS the input and routes via computation, not if-else.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x8dfc6e38"  # GenesisByte: parampara % 37 == 0

import sys
from typing import Dict, Final, List, Optional

# Exit codes
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1


def main(argv: Optional[List[str]] = None) -> int:
    """
    THE ONE ENTRY POINT - Mahamantra is King.

    mahamantra("anything") → Full 9-step NavaBhakti Pipeline → Result

    NO argparse. NO subcommands. NO if-else chains.
    The Mahamantra COMPUTES the route from the input itself.
    """
    if argv is None:
        argv = sys.argv[1:]

    # No input = help
    if not argv:
        return _show_help()

    # Join all args into one input string
    # Resonance doesn't care about structure - it FEELS the meaning
    input_text = " ".join(argv)

    # Special: help (the only escape hatch)
    if input_text in ("-h", "--help", "help"):
        return _show_help()

    # =========================================================================
    # MAHAMANTRA IS THE KING - Direct __call__ (9 NavaBhakti steps)
    # =========================================================================
    # NO adapter. NO fingerprint matching. NO old CLI registry.
    # mahamantra.execute() IS the router. Pure computation.
    # =========================================================================

    try:
        from vibe_core.mahamantra import mahamantra

        result = mahamantra.execute(input_text)

        # Render the response
        _render_response(result)

        return result.get("exit_code", EXIT_SUCCESS)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return EXIT_ERROR


def _render_response(response: Dict[str, object]) -> None:
    """
    Render mahamantra.execute() response.

    The response contains EVERYTHING - we just display it.
    """
    vib = response.get("vibration", {})

    # Core data
    inp = str(response.get("input", ""))[:60]
    seed = str(vib.get("seed", "?"))
    attractor = str(vib.get("attractor", "?"))
    chapter = str(response.get("chapter", "?"))
    position = response.get("position", "?")
    guardian = str(response.get("guardian", "?"))[:12]
    quarter = str(response.get("quarter", "?"))[:10]

    # Gita verse
    verse = response.get("verse") or {}
    guna = str(verse.get("guna", "?"))[:10]
    verse_id = str(verse.get("id", "-"))

    # Parampara
    parampara = response.get("parampara", {})
    parampara_status = "BONA FIDE" if parampara.get("verified") else "?"

    # Cell
    cell = response.get("cell", {})
    cell_valid = "ALIVE" if cell.get("is_alive") else "?"
    cell_prana = str(cell.get("prana", "?"))

    # Trinity function
    holy_name = response.get("holy_name", "?")
    trinity_fn = response.get("trinity_function", "?")

    # Execution
    execution = response.get("execution", {})
    exec_success = execution.get("success", False)
    guardian_acted = execution.get("guardian_acted", False)
    guardian_result = execution.get("guardian_result") or {}
    exec_mark = "EXECUTED" if exec_success else "PENDING"
    guardian_mark = "YES" if guardian_acted else "no"

    # Rückfrage: guardian signals it needs confirmation before proceeding
    needs_confirmation = guardian_result.get("requires_confirmation", False)

    # Guardian response: what did the guardian actually say?
    guardian_action = str(guardian_result.get("action", ""))[:20]
    guardian_message = str(guardian_result.get("message", ""))[:56]

    # Yajna cycle
    yajna = response.get("yajna", {})
    yajna_phase = str(yajna.get("phase", "?"))

    print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║  MAHAMANTRA - Krishna Routes Everything                               ║
╠═══════════════════════════════════════════════════════════════════════╣
║  INPUT:    {inp:58s} ║
║  SEED:     {seed:<58s} ║
╠═══════════════════════════════════════════════════════════════════════╣
║  VIBRATION:                                                           ║
║    Attractor: {attractor:<10s}  Chapter: {chapter:>2s}  Guna: {guna:10s}          ║
║    Verse: {verse_id:<58s} ║
╠═══════════════════════════════════════════════════════════════════════╣
║  ROUTING (computed from seed):                                        ║
║    Position: {position:>2}  Guardian: {guardian:12s}  Quarter: {quarter:10s}  ║
║    Name: {holy_name}  Function: {trinity_fn:12s}                              ║
╠═══════════════════════════════════════════════════════════════════════╣
║  EXECUTION:                                                           ║
║    Status: {exec_mark:<12s}  Guardian acted: {guardian_mark:<10s}          ║
║    Cell: {cell_valid:<8s}  Prana: {cell_prana:<10s}  Yajna: {yajna_phase:10s}  ║""")

    # Show guardian response if it acted
    if guardian_acted and guardian_action:
        print(f"║    Action: {guardian_action:<56s} ║")
    if guardian_acted and guardian_message:
        print(f"║    Response: {guardian_message:<54s} ║")

    # Rückfrage: guardian needs confirmation before executing
    if needs_confirmation:
        print("║                                                                       ║")
        print("║  ** RÜCKFRAGE: Guardian wartet auf Bestätigung **                      ║")

    print(f"""╠═══════════════════════════════════════════════════════════════════════╣
║  PARAMPARA: {parampara_status:10s}                                             ║
╚═══════════════════════════════════════════════════════════════════════╝
""")


def _show_help() -> int:
    """Show help - Mahamantra is King."""
    print("""
MAHAMANTRA - Krishna Routes Everything
======================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

USAGE:
    steward "anything"
    python -m vibe_core.mahamantra "anything"

THAT'S IT. No subcommands. No flags. Just speak.

EXAMPLES:
    steward "analyze the codebase"
    steward "what is position 6"
    steward "show me karma quarter"
    steward "chant 3 rounds"

HOW IT WORKS (9 NavaBhakti):
    1. SRAVANAM       Receive your input
    2. KIRTANAM       Compress to seed (MahaCompression)
    3. SMARANAM       Vibrate (MahaKirtan)
    4. PADA_SEVANAM   Find attractor (MahaResonator)
    5. ARCANAM        Verify Parampara (% 37)
    6. VANDANAM       Match Gita chapter (THE BINDING ELEMENT)
    7. DASYAM         Determine position/guardian
    8. SAKHYAM        Create MahaCell + Chamber.kirtan()
    9. ATMA_NIVEDANAM ShadowReactor.tick() → Guardian execution

ARCHITECTURE:
    Position = attractor % 16
    Quarter 0 (genesis):  Pos 0-3   - INPUT
    Quarter 1 (dharma):   Pos 4-7   - VERIFY
    Quarter 2 (karma):    Pos 8-11  - EXECUTE
    Quarter 3 (moksha):   Pos 12-15 - OUTPUT

The system doesn't parse commands. It FEELS meaning.
Krishna routes everything.
""")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
