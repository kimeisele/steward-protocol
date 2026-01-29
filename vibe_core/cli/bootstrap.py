"""
CLI BOOTSTRAP - Minimal entry point that configures logging FIRST.

This module exists to silence logging spam BEFORE any vibe_core imports.
The pyproject.toml entry point should use: vibe_core.cli.bootstrap:main

"śrī-gaṇeśāya namaḥ" - First, we clear the obstacles.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x8c3a0fb4"  # GenesisByte: parampara % 37 == 0


def main() -> None:
    """
    Bootstrap entry point - configures logging BEFORE imports.

    SEQUENCE:
    1. Configure logging (silence INFO spam)
    2. Import the real CLI
    3. Run it
    """
    import logging
    import os
    import sys

    # Check for verbose mode
    verbose = "--verbose" in sys.argv or "-v" in sys.argv or os.environ.get("STEWARD_DEBUG")
    level = logging.DEBUG if verbose else logging.WARNING

    # Configure BEFORE any vibe_core imports
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s" if not verbose else "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )

    # Pre-silence known noisy loggers
    for logger_name in [
        "vibe_core",
        "vibe_core.runtime",
        "vibe_core.runtime.prompt_registry",
        "vibe_core.mahamantra",
        "CARTRIDGE_BRIDGE",
        "CARTRIDGE_SERVICE",
        "urllib3",
        "httpx",
    ]:
        logging.getLogger(logger_name).setLevel(level)

    # NOW import and run
    from vibe_core.cli.main import cli_entry

    cli_entry()


if __name__ == "__main__":
    main()
