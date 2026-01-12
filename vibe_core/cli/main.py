"""
CLI MAIN - The Single Gate
==========================

"ekam evādvitīyam" - One without a second.

ROUTING HIERARCHY:
==================

    steward <command> [args]
           ↓
    1. MAHAMANTRA CLI (Protocol introspection)
       → 16 positions (12 mahajanas + 4 avataras)
       → Auto-discovered from Protocol definitions
       → ZERO manual wiring
           ↓
    2. UNIFIED CLI (Legacy fallback)
       → Only if MahamantraCLI returns NOT_FOUND (127)
       → Temporary bridge during migration

PROTOCOL-BASED:
===============

    Every command traces to a guardian.
    Every guardian owns a Protocol.
    Protocol introspection discovers capabilities.
    No manual registration. FOLDER = WIRING.

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
"""

from __future__ import annotations

import sys
from typing import Final, List, Optional

# Exit codes (WATERTIGHT - Protocol-aligned)
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1
EXIT_UNKNOWN_COMMAND: Final[int] = 3  # CLIErrorCode.UNKNOWN_COMMAND


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point - MahamantraCLI WINS.

    Protocol-based routing through 16 positions.
    Legacy fallback only for unmigrated commands.
    """
    if argv is None:
        argv = sys.argv[1:]

    # =========================================================================
    # 1. MAHAMANTRA CLI - Protocol introspection (PRIMARY)
    # =========================================================================
    try:
        from vibe_core.mahamantra.cli.entry import main as mahamantra_main

        result = mahamantra_main(argv)

        # If command found and executed (even if error), return result
        # Only fall through to legacy if UNKNOWN_COMMAND
        if result != EXIT_UNKNOWN_COMMAND:
            return result

    except ImportError:
        # MahamantraCLI not available - fall through to legacy
        pass
    except Exception:
        # MahamantraCLI error - fall through to legacy
        pass

    # =========================================================================
    # 2. UNIFIED CLI - Legacy fallback (TEMPORARY)
    # =========================================================================
    try:
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()
        return cli.run(argv)

    except ImportError:
        print("ERROR: CLI system not available")
        return EXIT_ERROR


def cli_entry() -> None:
    """Console script entry point (pyproject.toml)."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
