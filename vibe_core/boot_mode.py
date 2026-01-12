"""
DEPRECATED: Use mahajana import.

ONE IMPORT, PRITHU OWNS:
    from vibe_core.protocols.mahajanas.prithu.types.boot_mode import BootMode

Or via mahamantra:
    from vibe_core.mahamantra import mahamantra
    BootMode = mahamantra.mod.prithu.types.boot_mode.BootMode

This file is a BRIDGE for backward compatibility.
Will be removed in future version.
"""

# Re-export from canonical location (PRITHU owns system wake/boot)
from vibe_core.protocols.mahajanas.prithu.types.boot_mode import *
from vibe_core.protocols.mahajanas.prithu.types.boot_mode import BootMode
