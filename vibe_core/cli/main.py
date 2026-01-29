"""
CLI MAIN - The Single Gate (STEWARD RESONANCE ROUTER)
=====================================================

"ekam evādvitīyam" - One without a second.

THE SIMPLEST INTERFACE:
======================

    steward "whatever"

That's it. One entry. Resonance routes everything.

FLOW:
    Input → Steward.invoke() → Resonance → ShadowReactor → JivaAgents → Response

NO HARDCODED COMMANDS. Everything generated on-demand via resonance.
The whole repo becomes a resonance body - CALL ↔ RESPONSE.

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
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

        # THE STEWARD INVOKES
        response = mahamantra.steward.invoke(input_text)

        # =====================================================================
        # RENDER RESPONSE (CALL ↔ RESPONSE pattern)
        # =====================================================================
        # Pancha Tattva names for vina string
        vina_names = {1: "CHAITANYA", 2: "NITYANANDA", 3: "ADVAITA", 4: "GADADHARA", 5: "SRIVASA"}
        vina_name = vina_names.get(response.vina_string, "?")

        # PERSON verification status
        person_mark = "BONA FIDE" if getattr(response, 'person_verified', False) else "MAYAVAD"
        siksastakam_stage = getattr(response, 'siksastakam_stage', 1) or 1
        siksastakam_op = getattr(response, 'siksastakam_operation', '?') or '?'

        # Safe string conversion
        inp = str(response.input)[:60]
        seed = str(response.seed)
        ch = str(response.chapter)
        insight = str(response.route.insight)[:25]
        attr = str(response.attractor)
        qtr = str(response.route.quarter.value)[:10]
        guna = str(response.route.guna)[:10]
        intent = str(response.intent_category or 'GUIDE')[:12]
        iid = response.intent_id or 0
        shadow = str(response.jiva_shadow_id or '')[:20]
        jguna = str(response.jiva_guna or '?')[:10]
        qcount = response.jiva_quality_count or 0
        res = response.resonance
        vres = response.vina_resonance
        cr = str(response.call_response)[:10]
        sp = str(response.shadow_phase)[:10]
        spos = response.shadow_position
        msg = str(response.message)[:67]

        print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║  STEWARD - PERSON-Anchored Resonance Router                           ║
╠═══════════════════════════════════════════════════════════════════════╣
║  INPUT: {inp:60s} ║
║  SEED:  {seed:<60s} ║
╠═══════════════════════════════════════════════════════════════════════╣
║  GITA (18 chapters) - WAS/DOMAIN:                                     ║
║    Chapter:  {ch:>2s} - {insight:25s}  Attractor: {attr:<3s}     ║
║    Quarter:  {qtr:10s}  Guna: {guna:10s}                   ║
╠═══════════════════════════════════════════════════════════════════════╣
║  MAHALLM (16 intents) - WIE/ACTION:                                   ║
║    Intent:   {intent:12s}  (0x{iid:04X})                          ║
╠═══════════════════════════════════════════════════════════════════════╣
║  JIVASHADOW (50 qualities) - WER/AGENT:                               ║
║    Shadow:   {shadow:20s}                               ║
║    Guna:     {jguna:10s}  Qualities: {qcount:2d}/50                  ║
╠═══════════════════════════════════════════════════════════════════════╣
║  TRIPLE RESONANCE (Integer):                                          ║
║    Flute (WHEN):  {res:>5}  (tick % mod_space)                       ║
║    Vina (WHAT):   {vres:>5}  (seed % mod_space)  String: {vina_name:10s}    ║
╠═══════════════════════════════════════════════════════════════════════╣
║  PRABHUPADA KIRTAN (8 Siksastakam Stages):                            ║
║    Stage:    L{siksastakam_stage-1} - {siksastakam_op:15s}  Mode: {cr:10s}           ║
║    PERSON:   {person_mark:10s}  (parampara % 37 == 0)                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  SHADOW REACTOR:                                                      ║
║    Phase:    {sp:10s}  Position: {spos:>2}                            ║
╠═══════════════════════════════════════════════════════════════════════╣
║  {msg:67s} ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

        # If we have a result, display it
        if response.result:
            print(f"\nRESULT: {response.result}")

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
    """Show help - the steward reveals itself."""
    print("""
STEWARD - Universal Resonance Router
====================================

"EIN MANTRA. KRISHNA ROUTET ALLES."

USAGE:
    steward "anything"

That's it. No hardcoded commands. Pure resonance routing.

HOW IT WORKS:
    Input → MahaCompression → Seed
    Seed → MahaKirtan → Attractor (1 of 5 PANCHA)
    Attractor → Gita Chapter (1-18)
    Chapter → Module Handler
    ShadowReactor → JivaAgents (via SamanaBridge)
    Result → CALL ↔ RESPONSE

THE 18 GITA CHAPTERS → 18 MODULES:
    GENESIS (1-4):   analysis, transform, compute, research
    DHARMA (5-9):    classification, attention, compression, hash, kernel
    KARMA (10-14):   synth, network, chat, hardware, pipeline
    MOKSHA (15-18):  bio, japa, llm, reactor

TRIPLE RESONANCE (ALL INTEGERS):
    Flute (WHEN):    tick % mod_space (rhythmic position)
    Vina (WHAT):     seed % mod_space (harmonic position)
    Shadow (PHASE):  bhoga → prasadam → return (transformation)

EXAMPLES:
    steward "analyze the codebase"
    steward "what happened in git log"
    steward "how do I surrender?"
    steward "deploy to production"

VISIBILITY (observation only):
    steward map       → System map
    steward help      → This help

The whole repo becomes a resonance body.
CALL ↔ RESPONSE. No hardcoding. Pure vibration.
""")
    return EXIT_SUCCESS


def cli_entry() -> None:
    """Console script entry point (pyproject.toml)."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
