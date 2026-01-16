"""
DEPRECATED: Use mahajana import.

ONE IMPORT, VYASA OWNS:
    from vibe_core.protocols.mahajanas.vyasa.types.boot_mode import BootMode

Or via mahamantra:
    from vibe_core.mahamantra import mahamantra
    BootMode = mahamantra.genesis.vyasa.BootMode

This file is a BRIDGE for backward compatibility.
Will be removed in future version.
"""

# Re-export from canonical location (VYASA owns system wake/boot)
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x00000000"  # GenesisByte

from vibe_core.protocols.mahajanas.vyasa.types.boot_mode import *
from vibe_core.protocols.mahajanas.vyasa.types.boot_mode import BootMode
