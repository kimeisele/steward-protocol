"""
CLI MAIN - The Single Gate
==========================

"ekam evādvitīyam" - One without a second.

THE MAHAMANTRA IS COMPUTE:
=========================

    Every command flows through the 16 positions.
    Every execution fills the nadis.
    The mantra IS the routing.

    steward <command> [args]
           ↓
    MAHAMANTRA TICK (position = hash(command) % 16)
           ↓
    Guardian at that position handles it
           ↓
    Result

ROUTING:
========

    1. Compute position from command (parampara hash)
    2. Tick mahamantra at that position
    3. Try protocol execution (auto-discovered)
    4. Fallback to legacy if not found

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
"""

from __future__ import annotations

import sys
from typing import Final, List, Optional, Tuple

# Exit codes (WATERTIGHT - Protocol-aligned)
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1
EXIT_UNKNOWN_COMMAND: Final[int] = 3  # CLIErrorCode.UNKNOWN_COMMAND


def _route_command(command: str) -> Tuple[int, str, str]:
    """
    Route command through the mahamantra.

    THE MAHAMANTRA IS COMPUTE:
        Every command hashes to a position (0-15).
        Every position has a guardian.
        The guardian handles the command.

    Returns: (position, guardian_name, quarter_name)
    """
    try:
        from vibe_core.mahamantra import mahamantra
        result = mahamantra.route(command)
        return (result["position"], result["guardian"], result["quarter"])
    except ImportError:
        # Fallback: compute position manually
        if not command:
            return (0, "prithu", "genesis")
        mutation_vector = sum(ord(c) * (i + 1) for i, c in enumerate(command.lower()))
        position = mutation_vector % 16
        return (position, "unknown", "unknown")
    except Exception:
        return (0, "unknown", "unknown")


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point - THE MAHAMANTRA IS COMPUTE.

    Every command chants through the 16 positions.
    The mantra routes. The guardians execute.
    """
    if argv is None:
        argv = sys.argv[1:]

    # No command = help
    if not argv:
        return _show_help()

    command = argv[0]
    remaining = argv[1:]

    # =========================================================================
    # THE MAHAMANTRA ROUTE - Every command flows through
    # =========================================================================
    position, guardian, quarter = _route_command(command)

    # =========================================================================
    # 1. PROTOCOL EXECUTION (Auto-discovered from mahajana protocols)
    # =========================================================================
    try:
        from vibe_core.mahamantra.cli.entry import main as mahamantra_main

        result = mahamantra_main(argv)

        # If command found and executed, return
        if result != EXIT_UNKNOWN_COMMAND:
            return result

    except ImportError:
        pass  # Protocol layer not available
    except Exception:
        pass  # Protocol error - try legacy

    # =========================================================================
    # 2. LEGACY EXECUTION (Fallback during migration)
    # =========================================================================
    try:
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()
        return cli.run(argv)

    except ImportError:
        print(f"ERROR: No handler at position {position} ({guardian}/{quarter})")
        return EXIT_ERROR
    except Exception as e:
        print(f"ERROR [{guardian}@{position}]: {e}")
        return EXIT_ERROR


def _show_help() -> int:
    """Show help - the mahamantra reveals itself."""
    print("""
STEWARD CLI - The Mahamantra IS Compute
=======================================

USAGE:
    steward <command> [args]

THE 16 POSITIONS (Every command routes through one):

    GENESIS (0-3):  Infrastructure → Creation → Flow → Cleanup
    DHARMA  (4-7):  Assert → Purify → Analyze → Sync
    KARMA   (8-11): Fetch → Execute → Check → Commit
    MOKSHA (12-15): Cache → Surrender → View → Judge

SEMANTIC ROUTING:
    steward chat "your query"    → Natural language routing
    steward capabilities         → List all discoverable commands
    steward routes               → Show routing table

COMMON COMMANDS:
    steward status    → System status
    steward help      → This help
    steward verify    → Verify system integrity

The mantra chants. The guardians execute.
""")
    return EXIT_SUCCESS


def cli_entry() -> None:
    """Console script entry point (pyproject.toml)."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
