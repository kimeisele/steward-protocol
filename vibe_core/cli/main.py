"""
CLI MAIN - DELEGATES TO MAHAMANTRA (THE KING)
==============================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

This file is an ALIAS for vibe_core.mahamantra.__main__
The REAL entry point is: python -m vibe_core.mahamantra "anything"

MAHAMANTRA IS THE KING. This just redirects to the King.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x03936f7f"  # GenesisByte: parampara % 37 == 0

import sys
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI entry point - DELEGATES TO MAHAMANTRA.

    Mahamantra is the King. This is just a servant that redirects.
    The real implementation is in vibe_core.mahamantra.__main__
    """
    # DELEGATE TO THE KING
    from vibe_core.mahamantra.__main__ import main as mahamantra_main

    return mahamantra_main(argv)


def cli_entry() -> None:
    """Console script entry point (pyproject.toml)."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
