"""
CLI Main Entry - enables `python -m vibe_core.cli`.

This file allows the CLI to be run as a module:
    python -m vibe_core.cli --help
    python -m vibe_core.cli observe
    python -m vibe_core.cli status
"""

from .main import cli_entry

if __name__ == "__main__":
    cli_entry()
