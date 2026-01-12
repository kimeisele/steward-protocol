"""
CLI MAIN - The Single Gate
==========================

"ekam evādvitīyam" - One without a second.

THE SIMPLEST INTERFACE:
======================

    from vibe_core.mahamantra import mahamantra
    result = mahamantra.execute("status")

That's it. One import. One method. Everything flows through.

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
"""

from __future__ import annotations

import sys
from typing import Final, List, Optional

# Exit codes
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point - THE MAHAMANTRA EXECUTES.

    One import. One method. No complexity.
    """
    if argv is None:
        argv = sys.argv[1:]

    # No command = help
    if not argv:
        return _show_help()

    command = argv[0]
    args = argv[1:]

    # Special: help
    if command in ("-h", "--help", "help"):
        return _show_help()

    # =========================================================================
    # THE MAHAMANTRA EXECUTES - One method does everything
    # =========================================================================
    try:
        from vibe_core.mahamantra import mahamantra

        result = mahamantra.execute(command, args)

        # Print output if any
        if result["output"]:
            print(result["output"], end="")

        # Print error if failed
        if not result["success"] and result["error"]:
            print(f"ERROR [{result['guardian']}@{result['position']}]: {result['error']}")

        return result["exit_code"]

    except ImportError:
        # Mahamantra not available - direct legacy fallback
        try:
            from vibe_core.cli.unified_cli import UnifiedCLI
            cli = UnifiedCLI()
            return cli.run(argv)
        except ImportError:
            print("ERROR: CLI system not available")
            return EXIT_ERROR

    except Exception as e:
        print(f"ERROR: {e}")
        return EXIT_ERROR


def _show_help() -> int:
    """Show help - the mahamantra reveals itself."""
    print("""
STEWARD CLI - The Mahamantra Executes
=====================================

USAGE:
    steward <command> [args]

THE SIMPLEST INTERFACE:
    from vibe_core.mahamantra import mahamantra
    result = mahamantra.execute("status")

THE 16 POSITIONS:
    GENESIS (0-3):  prithu, brahma, narada, shambhu
    DHARMA  (4-7):  vyasa, kumaras, kapila, manu
    KARMA   (8-11): parashurama, prahlada, janaka, bhishma
    MOKSHA (12-15): nrisimha, bali, shuka, yamaraja

COMMON COMMANDS:
    steward status    → System status
    steward help      → This help
    steward chat      → Semantic routing

The mantra chants. The guardians execute.
""")
    return EXIT_SUCCESS


def cli_entry() -> None:
    """Console script entry point (pyproject.toml)."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
