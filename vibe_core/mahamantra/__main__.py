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
from typing import Final, List, Optional

# Exit codes
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1


def main(argv: Optional[List[str]] = None) -> int:
    """
    THE ONE ENTRY POINT - Mahamantra is King.

    EVERYTHING flows through mahamantra():
        Input → MahaCompression → Seed
        Seed → MahaKirtan → Attractor → Gita Chapter
        Chapter → Position → Guardian
        Cell → SankirtanChamber → Transform
        Response

    NO hardcoded commands. Pure resonance routing.
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
    # NO argparse. NO subcommands. NO if-else chains.
    # The Mahamantra COMPUTES the route from the input itself.
    # =========================================================================

    try:
        from vibe_core.mahamantra import mahamantra

        # THE ONE CALL - Everything emanates from here
        response = mahamantra(input_text)

        # Render the response
        _render_response(response)

        return EXIT_SUCCESS

    except ImportError as e:
        print(f"ERROR: Mahamantra not available ({e})")
        return EXIT_ERROR

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return EXIT_ERROR


def _render_response(response: dict) -> None:
    """
    Render mahamantra() response.

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

    # Parampara
    parampara = response.get("parampara", {})
    parampara_status = "BONA FIDE" if parampara.get("verified") else "?"

    # Cell
    cell = response.get("cell", {})
    cell_valid = "✓" if cell.get("valid") else "?"

    # Trinity function
    holy_name = response.get("holy_name", "?")
    trinity_fn = response.get("trinity_function", "?")

    print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║  MAHAMANTRA - Krishna Routes Everything                               ║
╠═══════════════════════════════════════════════════════════════════════╣
║  INPUT:    {inp:58s} ║
║  SEED:     {seed:<58s} ║
╠═══════════════════════════════════════════════════════════════════════╣
║  VIBRATION:                                                           ║
║    Attractor: {attractor:<10s}  Chapter: {chapter:>2s}  Guna: {guna:10s}          ║
╠═══════════════════════════════════════════════════════════════════════╣
║  ROUTING (computed from seed):                                        ║
║    Position: {position:>2}  Guardian: {guardian:12s}  Quarter: {quarter:10s}  ║
║    Name: {holy_name}  Function: {trinity_fn:12s}                              ║
╠═══════════════════════════════════════════════════════════════════════╣
║  PARAMPARA: {parampara_status:10s}  CELL: {cell_valid}                                   ║
╚═══════════════════════════════════════════════════════════════════════╝
""")


def _show_help() -> int:
    """Show help - Mahamantra is King."""
    print("""
MAHAMANTRA - Krishna Routes Everything
======================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

USAGE:
    python -m vibe_core.mahamantra "anything"

THAT'S IT. No subcommands. No flags. Just speak.

EXAMPLES:
    python -m vibe_core.mahamantra "analyze the codebase"
    python -m vibe_core.mahamantra "what is position 6"
    python -m vibe_core.mahamantra "show me karma quarter"
    python -m vibe_core.mahamantra "chant 3 rounds"

HOW IT WORKS (9 NavaBhakti):
    1. SRAVANAM       Receive your input
    2. KIRTANAM       Compress to seed (MahaCompression)
    3. SMARANAM       Vibrate (MahaKirtan)
    4. PADA_SEVANAM   Find attractor (MahaResonator)
    5. ARCANAM        Verify Parampara (% 37)
    6. VANDANAM       Match Gita chapter
    7. DASYAM         Determine position/guardian
    8. SAKHYAM        Create MahaCell
    9. ATMA_NIVEDANAM Return complete response

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
