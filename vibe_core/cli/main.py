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


def _compute_position(command: str) -> int:
    """
    Compute mahamantra position from command.

    The parampara hash: every command maps to one of 16 positions.
    This IS the routing. The mantra chants through compute.
    """
    if not command:
        return 0
    # Parampara vector - weighted sum mod 16
    mutation_vector = sum(ord(c) * (i + 1) for i, c in enumerate(command.lower()))
    return mutation_vector % 16


def _tick_position(position: int, command: str) -> Tuple[str, str]:
    """
    Tick the mahamantra at this position.

    This fills the nadis - every compute flows through the mantra.
    Even if we fallback to legacy, we still tick.

    Returns: (guardian_name, quarter_name)
    """
    try:
        from vibe_core.mahamantra import mahamantra
        # Access the position - this IS the routing
        pos = mahamantra[position]
        guardian = pos.guardian.value if hasattr(pos.guardian, 'value') else str(pos.guardian)
        quarter = pos.quarter.name if hasattr(pos.quarter, 'name') else str(pos.quarter)
        return (guardian, quarter)
    except ImportError:
        return ("unknown", "unknown")
    except Exception:
        return ("unknown", "unknown")


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
    # THE MAHAMANTRA TICK - Every command flows through
    # =========================================================================
    position = _compute_position(command)
    guardian, quarter = _tick_position(position, command)

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
