"""
KIRTAN CLI - Live Maha Computing Interface
===========================================

"kirtaniyah sada harih"
"One should always chant the holy name of the Lord."
— Chaitanya Charitamrita, Adi 17.31

This CLI provides access to the MahaKirtan compute system and
the MahaOperator live loop interface.

USAGE:
======

    # Enter live operator mode (infinite loop until "37")
    vibe kirtan live

    # Run a single beat
    vibe kirtan beat 1966

    # Run a round (7 beats)
    vibe kirtan round 1966

    # Run a mala (108 rounds = 756 beats)
    vibe kirtan mala 1966

    # Research mode (queries)
    vibe kirtan research "what is the scale"

    # Synth control
    vibe kirtan synth --preset trinity --mod 256

    # Show presets
    vibe kirtan presets

THE CODEWORT:
=============

    In live mode, type "37" to exit (PARAMPARA - disciplic succession).
    This is not arbitrary - 37 validates the transmission channel.

ALL CONSTANTS DERIVED FROM SEED.PY.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xc8bad21b"  # GenesisByte: kirtan-cli

import logging
import sys
from typing import Any, Dict, Final, List, Optional

from vibe_core.protocols.cli import CLIMeta, register_cli

# Lazy import to avoid circular deps
logger = logging.getLogger("KIRTAN_CLI")


# =============================================================================
# CONSTANTS
# =============================================================================

# From seed.py
MAHA_QUANTUM: Final[int] = 137
PARAMPARA: Final[int] = 37


# =============================================================================
# KIRTAN CLI
# =============================================================================


@register_cli
class KirtanCLI:
    """
    Kirtan CLI - Live Maha Computing Interface.

    THE SYNTH PLAYER'S CONSOLE.

    Subcommands:
    - live: Enter live operator mode (infinite loop)
    - beat: Single beat computation
    - round: Full 7-beat round
    - mala: Full 108-round mala
    - research: Query ResearchChat
    - synth: Synth control
    - presets: Show available presets
    - state: Show current state
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="kirtan",
            description="Live Maha Computing Interface (MahaKirtan + MahaOperator)",
            domain="research",
            subcommands=["live", "beat", "round", "mala", "research", "synth", "presets", "state"],
            tags=["kirtan", "maha", "compute", "synth", "live", "research"],
        )

    def __init__(self):
        self._operator = None
        self._kirtan = None
        self._research_chat = None

    def _ensure_kirtan(self):
        """Lazy-load MahaKirtan."""
        if self._kirtan is None:
            from vibe_core.mahamantra import MahaKirtan

            self._kirtan = MahaKirtan()
        return self._kirtan

    def _ensure_operator(self, **kwargs):
        """Lazy-load PersonAnchoredOperator."""
        if self._operator is None:
            from vibe_core.mahamantra import PersonAnchoredOperator

            self._operator = PersonAnchoredOperator(**kwargs)
        return self._operator

    def _ensure_research(self):
        """Lazy-load ResearchChat."""
        if self._research_chat is None:
            from vibe_core.mahamantra_research.research_chat import get_research_chat

            self._research_chat = get_research_chat()
        return self._research_chat

    def run(self, args: List[str]) -> int:
        """
        Main entry point.

        Routes to subcommands: live, beat, round, mala, research, synth, presets, state
        """
        if not args:
            self._print_usage()
            return 0

        # Parse subcommand
        subcmd = args[0].lower()
        subargs = args[1:] if len(args) > 1 else []

        # Route to handler
        handlers = {
            "live": self._cmd_live,
            "l": self._cmd_live,
            "beat": self._cmd_beat,
            "b": self._cmd_beat,
            "round": self._cmd_round,
            "r": self._cmd_round,
            "mala": self._cmd_mala,
            "m": self._cmd_mala,
            "research": self._cmd_research,
            "?": self._cmd_research,
            "synth": self._cmd_synth,
            "s": self._cmd_synth,
            "presets": self._cmd_presets,
            "p": self._cmd_presets,
            "state": self._cmd_state,
            "help": self._cmd_help,
            "h": self._cmd_help,
        }

        handler = handlers.get(subcmd)
        if handler:
            return handler(subargs)

        # Check if it's a number (shortcut for beat)
        try:
            seed = int(subcmd)
            return self._cmd_beat([str(seed)])
        except ValueError as _exc:
            logger.exception("Unexpected error: %s", _exc)

        # Unknown command
        print(f"Unknown command: {subcmd}")
        self._print_usage()
        return 1

    # =========================================================================
    # SUBCOMMAND HANDLERS
    # =========================================================================

    def _cmd_live(self, args: List[str]) -> int:
        """
        Enter live operator mode.

        Usage: vibe kirtan live [--seed N] [--preset NAME] [--mod N]
        """
        # Parse args
        seed = 0
        preset = "quantum"
        mod_space = MAHA_QUANTUM
        no_metrics = False

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ("--seed", "-s") and i + 1 < len(args):
                seed = int(args[i + 1])
                i += 2
            elif arg in ("--preset", "-p") and i + 1 < len(args):
                preset = args[i + 1]
                i += 2
            elif arg in ("--mod", "-m") and i + 1 < len(args):
                mod_space = int(args[i + 1])
                i += 2
            elif arg == "--no-metrics":
                no_metrics = True
                i += 1
            else:
                # Try as seed
                try:
                    seed = int(arg)
                except ValueError as _exc:
                    logger.exception("Unexpected error: %s", _exc)
                i += 1

        # Create and run operator
        from vibe_core.mahamantra import PersonAnchoredOperator

        operator = PersonAnchoredOperator(
            mod_space=mod_space,
        )

        try:
            # PersonAnchoredOperator uses siksastakam stages (8 beats)
            print(f"Entering Live Mode (Seed: {seed}, Mod: {mod_space})")
            results = operator.run_siksastakam(seed=seed)
            print(f"\nRound complete: {len(results)} beats")
            return 0
        except Exception as e:
            logger.error(f"Operator error: {e}")
            print(f"Error: {e}")
            return 1

    def _cmd_beat(self, args: List[str]) -> int:
        """
        Execute a single beat.

        Usage: vibe kirtan beat [seed]
        """
        seed = int(args[0]) if args else 0

        kirtan = self._ensure_kirtan()
        result = kirtan.compute(seed)

        oracle_str = "✓" if result.oracle_validated else "✗"
        print(f"Beat #{result.beat_number} ({result.call_response})")
        print(f"  Seed: {result.seed} → {result.transformed_value}")
        print(f"  Year: {result.beat_year} (delta: {result.beat_delta})")
        print(f"  Resonance: {result.resonance_level:.2f}")
        print(f"  Oracle: {oracle_str}")

        return 0

    def _cmd_round(self, args: List[str]) -> int:
        """
        Execute a full round (7 beats).

        Usage: vibe kirtan round [seed]
        """
        seed = int(args[0]) if args else 0

        kirtan = self._ensure_kirtan()
        results = kirtan.compute_round(seed)

        print(f"Round complete: {len(results)} beats")
        print()

        for r in results:
            oracle_str = "✓" if r.oracle_validated else "✗"
            print(f"  [{r.beat_number}] {r.call_response}: {r.seed} → {r.transformed_value} (oracle: {oracle_str})")

        print()
        last = results[-1]
        print(f"Final resonance: {last.resonance_level:.2f}")
        print(f"Accumulated: {kirtan.get_state()['accumulated_value']}")

        return 0

    def _cmd_mala(self, args: List[str]) -> int:
        """
        Execute a full mala (108 rounds = 756 beats).

        Usage: vibe kirtan mala [seed]
        """
        seed = int(args[0]) if args else 0

        print(f"Executing mala with seed {seed}...")
        print("(108 rounds × 7 beats = 756 computations)")
        print()

        kirtan = self._ensure_kirtan()
        results = kirtan.compute_mala(seed)

        print(f"Mala complete: {len(results)} beats")

        last = results[-1]
        state = kirtan.get_state()

        print()
        print(f"Final seed: {last.transformed_value}")
        print(f"Final resonance: {last.resonance_level:.2f}")
        print(f"Accumulated: {state['accumulated_value']}")
        print(f"Total computations: {state['total_computations']}")

        return 0

    def _cmd_research(self, args: List[str]) -> int:
        """
        Query ResearchChat.

        Usage: vibe kirtan research <query>
        """
        if not args:
            # Enter interactive research mode
            from vibe_core.mahamantra_research.research_chat import main as research_main

            research_main()
            return 0

        query = " ".join(args)
        research = self._ensure_research()
        response = research.query(query)

        print()
        print(response.content)
        print()

        return 0

    def _cmd_synth(self, args: List[str]) -> int:
        """
        Synth control.

        Usage: vibe kirtan synth [--preset NAME] [--mod N]
        """
        from vibe_core.mahamantra import MahaModularSynth
        from vibe_core.mahamantra.substrate.algorithm.maha import SYNTH_PRESETS

        preset = "quantum"
        mod_space = MAHA_QUANTUM
        seed = None

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ("--preset", "-p") and i + 1 < len(args):
                preset = args[i + 1]
                i += 2
            elif arg in ("--mod", "-m") and i + 1 < len(args):
                mod_space = int(args[i + 1])
                i += 2
            elif arg in ("--seed", "-s") and i + 1 < len(args):
                seed = int(args[i + 1])
                i += 2
            else:
                # Try as preset name
                if arg in SYNTH_PRESETS:
                    preset = arg
                i += 1

        synth = MahaModularSynth(default_preset=preset)

        print(f"Synth: {preset}")
        print(f"mod_space: {mod_space}")

        if seed is not None:
            result = synth.transform(seed % mod_space)
            print(f"Transform: {seed} → {result}")

        print()
        print("Preset config:")
        if preset in SYNTH_PRESETS:
            from dataclasses import fields

            params = SYNTH_PRESETS[preset]
            for f in fields(params):
                val = getattr(params, f.name)
                print(f"  {f.name}: {val}")

        return 0

    def _cmd_presets(self, args: List[str]) -> int:
        """
        Show available synth presets.

        Usage: vibe kirtan presets
        """
        from dataclasses import fields

        from vibe_core.mahamantra.substrate.algorithm.maha import SYNTH_PRESETS

        print("Available Synth Presets:")
        print("=" * 40)

        for name, params in SYNTH_PRESETS.items():
            print(f"\n{name}:")
            # MahaSynthParams is a dataclass - iterate over fields
            for f in fields(params):
                val = getattr(params, f.name)
                print(f"  {f.name}: {val}")

        return 0

    def _cmd_state(self, args: List[str]) -> int:
        """
        Show current state.

        Usage: vibe kirtan state
        """
        kirtan = self._ensure_kirtan()
        state = kirtan.get_state()

        print("MahaKirtan State:")
        print("=" * 40)
        for k, v in state.items():
            print(f"  {k}: {v}")

        return 0

    def _cmd_help(self, args: List[str]) -> int:
        """Show help."""
        self._print_usage()
        return 0

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def _print_usage(self) -> None:
        """Print usage information."""
        print("""
KIRTAN CLI - Live Maha Computing Interface
===========================================

USAGE:
    vibe kirtan <command> [args]

COMMANDS:
    live [--seed N] [--preset P]   Enter live operator mode (exit with "37")
    beat [seed]                    Single beat computation
    round [seed]                   Full 7-beat round
    mala [seed]                    Full 108-round mala (756 beats)
    research [query]               Query ResearchChat (interactive if no query)
    synth [--preset P] [--mod N]   Synth control
    presets                        Show available synth presets
    state                          Show current state
    help                           This help

ALIASES:
    l = live, b = beat, r = round, m = mala, s = synth, p = presets, ? = research

EXAMPLES:
    vibe kirtan live --seed 1966
    vibe kirtan beat 42
    vibe kirtan round 1896
    vibe kirtan mala 108
    vibe kirtan synth --preset trinity
    vibe kirtan research "what is the scale"
    vibe kirtan 1966              # shortcut for 'beat 1966'

THE CODEWORT:
    In live mode, type "37" to exit (PARAMPARA).
    The number validates the disciplic succession channel.
""")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "KirtanCLI",
]
