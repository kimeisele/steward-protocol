"""
CLI MAIN - MAHAMANTRA IS THE KING
=================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

THE SIMPLEST INTERFACE:
======================

    steward "whatever"

That's it. One entry. MAHAMANTRA routes everything.

FLOW (9 NavaBhakti):
    Input → mahamantra(input) → SRAVANAM → KIRTANAM → ... → ATMA_NIVEDANAM → Response

NO HARDCODED COMMANDS. NO legacy routers.
Direct __call__ to MahamantraLotus. Pure computation.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x03936f7f"  # GenesisByte: parampara % 37 == 0

import sys
from typing import Final, List, Optional

# Exit codes
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point - STEWARD RESONANCE ROUTER.

    EVERYTHING flows through Steward.invoke():
        Input → MahaCompression → Seed
        Seed → MahaKirtan → Attractor → Gita Chapter
        Chapter → ShadowReactor → JivaAgents
        JivaAgents → CALL ↔ RESPONSE

    NO hardcoded commands. Pure resonance routing.
    """
    if argv is None:
        argv = sys.argv[1:]

    # No command = help
    if not argv:
        return _show_help()

    # Join all args into one input string (resonance doesn't care about structure)
    input_text = " ".join(argv)

    # Special: help (the only hardcoded escape hatch)
    if input_text in ("-h", "--help", "help"):
        return _show_help()

    # Special: map - System visibility (SATTVA observation, not action)
    if input_text.startswith("map"):
        return _show_map(argv[1:] if len(argv) > 1 else [])

    # =========================================================================
    # STEWARD RESONANCE ROUTER - The Universal Entry Point
    # =========================================================================
    # Everything else flows through resonance. No hardcoded commands.
    # The system FEELS the input and routes via:
    #   1. MahaCompression → seed
    #   2. MahaKirtan → attractor
    #   3. Attractor → Gita chapter (1-18)
    #   4. Chapter → Module handler
    #   5. ShadowReactor → JivaAgents (via SamanaBridge)
    # =========================================================================

    try:
        from vibe_core.mahamantra import mahamantra

        # =====================================================================
        # MAHAMANTRA IS THE KING - Direct __call__ (9 NavaBhakti steps)
        # =====================================================================
        # NO legacy steward.invoke() - direct computation through mahamantra
        response = mahamantra(input_text)

        # =====================================================================
        # RENDER RESPONSE - From __call__ result (dictionary)
        # =====================================================================
        # Pancha Tattva names for vina string
        vina_names = {1: "CHAITANYA", 2: "NITYANANDA", 3: "ADVAITA", 4: "GADADHARA", 5: "SRIVASA"}
        vib = response["vibration"]
        vina_name = vina_names.get(vib.get("vina_string", 0), "?")

        # Extract response data
        inp = str(response["input"])[:60]
        seed = str(vib["seed"])
        ch = str(response["chapter"])
        attr = str(vib["attractor"])
        qtr = response["quarter"][:10]
        position = response["position"]
        guardian = response["guardian"][:12]

        # Gita verse info
        verse = response.get("verse") or {}
        guna = str(verse.get("guna", "?"))[:10]
        dominant = str(verse.get("dominant_name", "?"))[:20]

        # Parampara
        parampara = response["parampara"]
        parampara_mark = "BONA FIDE" if parampara["verified"] else "MAYAVAD"
        oracle_mark = "✓" if parampara["oracle_validated"] else "✗"

        # Vibration values
        flute_res = vib.get("flute_resonance", 0)
        vina_res = vib.get("vina_resonance", 0)
        beat = vib.get("beat", 0)

        # MahaCell
        cell = response["cell"]
        cell_valid = "✓" if cell["valid"] else "✗"

        # Akash state
        akash = response["akash"]
        total_beats = akash.get("total_beats", 0)

        print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║  MAHAMANTRA - Krishna Routes Everything (9 NavaBhakti)                ║
╠═══════════════════════════════════════════════════════════════════════╣
║  INPUT: {inp:60s} ║
║  SEED:  {seed:<60s} ║
╠═══════════════════════════════════════════════════════════════════════╣
║  GITA (18 chapters) - VANDANAM:                                       ║
║    Chapter:  {ch:>2s}  Guna: {guna:10s}  Dominant: {dominant:20s}  ║
║    Attractor: {attr:<5s}  Matches: {response['matches']:<3}                                ║
╠═══════════════════════════════════════════════════════════════════════╣
║  POSITION (DASYAM) - attractor % 16:                                  ║
║    Position: {position:>2}  Guardian: {guardian:12s}  Quarter: {qtr:10s} ║
╠═══════════════════════════════════════════════════════════════════════╣
║  VIBRATION (KIRTANAM + SMARANAM + PADA_SEVANAM):                      ║
║    Flute:  {flute_res:>5}  (WHEN)   Vina: {vina_res:>5}  (WHAT)  String: {vina_name:10s}   ║
║    Beat:   {beat:>5}  Transformed: {vib['transformed_value']:<10}                  ║
╠═══════════════════════════════════════════════════════════════════════╣
║  PARAMPARA (ARCANAM) - seed % 37 == 0:                                ║
║    Status: {parampara_mark:10s}  Channel: {parampara['channel']:>2}  Oracle: {oracle_mark}             ║
╠═══════════════════════════════════════════════════════════════════════╣
║  MAHACELL (SAKHYAM) - Universal Format:                               ║
║    Header: 72 bytes  Payload: {cell['payload_size']:>5} bytes  Valid: {cell_valid}              ║
╠═══════════════════════════════════════════════════════════════════════╣
║  AKASH (persistent field):  Total Beats: {total_beats:<10}                  ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

        return EXIT_SUCCESS

    except ImportError as e:
        print(f"ERROR: Steward not available ({e})")
        return EXIT_ERROR

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return EXIT_ERROR


def _show_map(args: List[str]) -> int:
    """
    Show system map - SATTVA (observation).

    Usage:
        steward map           → Overview
        steward map --verbose → With details
    """
    try:
        from vibe_core.mahamantra.cli.map import map_command

        print(map_command(args))
        return EXIT_SUCCESS
    except ImportError as e:
        print(f"ERROR: Map not available ({e})")
        return EXIT_ERROR


def _show_help() -> int:
    """Show help - mahamantra is the king."""
    print("""
MAHAMANTRA - Krishna Routes Everything
======================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

USAGE:
    steward "anything"

NINE NAVABHAKTI STEPS (__call__):
    1. SRAVANAM       Receive input (hearing)
    2. KIRTANAM       MahaCompression → seed (chanting)
    3. SMARANAM       MahaKirtan → vibration (remembering)
    4. PADA_SEVANAM   MahaResonator → attractor (serving)
    5. ARCANAM        Parampara verification (worshiping)
    6. VANDANAM       GitaResonance → verse (praying)
    7. DASYAM         Position/Quarter (servitude)
    8. SAKHYAM        MahaCell creation (friendship)
    9. ATMA_NIVEDANAM Complete response (surrender)

ARCHITECTURE (from Mantra):
    Position = attractor % 16
    Quarter 0 (genesis):  Pos 0-3   → INPUT
    Quarter 1 (dharma):   Pos 4-7   → VERIFY
    Quarter 2 (karma):    Pos 8-11  → EXECUTE
    Quarter 3 (moksha):   Pos 12-15 → OUTPUT

RESPONSE FIELDS:
    chapter   → Gita chapter (1-18)
    verse     → Gita verse + guna
    position  → 0-15 (Mahajana position)
    guardian  → Responsible Mahajana
    quarter   → genesis/dharma/karma/moksha

EXAMPLES:
    steward "analyze the codebase"
    steward "what happened in git log"
    steward "show me the karma quarter"

VISIBILITY:
    steward map       → System map
    steward help      → This help

Frag das System. Es weiß mehr als du.
""")
    return EXIT_SUCCESS


def cli_entry() -> None:
    """Console script entry point (pyproject.toml)."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
