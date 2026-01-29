"""
CLI MAIN - Routes to Mahamantra CLI Entry
=========================================

"ekam evādvitīyam" - One without a second.

This file ONLY delegates to MahamantraCLIEntry.
NO logic here. Just the bridge.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x03936f7f"  # GenesisByte: parampara % 37 == 0

import sys
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    """Delegate to MahamantraCLIEntry - the REAL entry point."""
    if argv is None:
        argv = sys.argv[1:]

    try:
        from vibe_core.mahamantra.cli.entry import MahamantraCLIEntry

        entry = MahamantraCLIEntry()
        result = entry.run(argv)
        return result.exit_code if hasattr(result, 'exit_code') else (0 if result else 1)

    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def cli_entry() -> None:
    """Console script entry point."""
    import logging
    import os

    verbose = "--verbose" in sys.argv or "-v" in sys.argv or os.environ.get("STEWARD_DEBUG")
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s", force=True)

    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
