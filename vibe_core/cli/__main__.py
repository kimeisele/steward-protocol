"""
CLI Main Entry - enables `python -m vibe_core.cli`.

This file allows the CLI to be run as a module:
    python -m vibe_core.cli --help
    python -m vibe_core.cli observe
    python -m vibe_core.cli status

IMPORTANT: Logging is configured HERE, BEFORE any vibe_core imports,
to prevent INFO spam from flooding the terminal.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x71305ec8"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# CONFIGURE LOGGING FIRST - BEFORE ANY VIBE_CORE IMPORTS
# =============================================================================
import logging
import os
import sys

# Check for verbose mode BEFORE imports
_verbose = "--verbose" in sys.argv or "-v" in sys.argv or os.environ.get("STEWARD_DEBUG")
_level = logging.DEBUG if _verbose else logging.WARNING

# Configure root logger with force=True to override any existing config
logging.basicConfig(
    level=_level,
    format="%(levelname)s: %(message)s" if not _verbose else "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)

# Pre-create loggers at correct level (they'll be reused when modules import)
for _logger_name in [
    "vibe_core",
    "vibe_core.runtime",
    "vibe_core.runtime.prompt_registry",
    "vibe_core.mahamantra",
    "CARTRIDGE_BRIDGE",
    "CARTRIDGE_SERVICE",
    "urllib3",
    "httpx",
]:
    logging.getLogger(_logger_name).setLevel(_level)

# =============================================================================
# NOW SAFE TO IMPORT
# =============================================================================
from .main import cli_entry

if __name__ == "__main__":
    cli_entry()
