"""
CLI MAIN - The Single Gate
==========================

"ekam evādvitīyam" - One without a second.

THE SIMPLEST INTERFACE:
    steward "whatever"

FLOW:
    main() → UnifiedCLI.run() → Full dispatch chain → Gates → Vibration

UnifiedCLI handles:
1. Legacy commands (system)
2. CLIRegistry (protocol-based)
3. Plugin commands (discovered)
4. PRAKRITI/MANAS/Conductor
5. GATES (Pancha Tattva = Mahamantra vibration)
6. Unknown → Error

NO SPAGHETTI. One entry. Unified routing.
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
    Main CLI entry point - delegates to UnifiedCLI.

    UnifiedCLI has the full dispatch chain including:
    - CommandRegistry (exact matches)
    - Gates (Pancha Tattva vibration routing)
    - Everything else
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()
        return cli.run(argv)

    except ImportError as e:
        print(f"ERROR: CLI not available ({e})")
        return EXIT_ERROR
    except Exception as e:
        print(f"ERROR: {e}")
        return EXIT_ERROR


def cli_entry() -> None:
    """Console script entry point (pyproject.toml)."""
    # Configure logging before imports
    import logging
    import os

    verbose = "--verbose" in sys.argv or "-v" in sys.argv or os.environ.get("STEWARD_DEBUG")
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s", force=True)

    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
