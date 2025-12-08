"""
CLI Main Entry Point - Unified CLI System.
Delegates to UnifiedCLI for all operations.
"""

import sys
from typing import List, Optional

from vibe_core.cli.unified_cli import UnifiedCLI


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.
    Delegates to UnifiedCLI.
    """
    if argv is None:
        argv = sys.argv[1:]

    cli = UnifiedCLI()
    return cli.run(argv)


def cli_entry():
    """Entry point for console_scripts."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
