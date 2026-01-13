"""
PRITHU Types - Position 0 (GENESIS Quarter HEAD, SYS_WAKE)
==========================================================

PRITHU - The King who leveled the Earth.
Types for boot, system, and process management.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xcbb6664f"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.prithu.types.boot_mode import (
    BootMode,
)

from vibe_core.protocols.mahajanas.prithu.types.process_manager import (
    ProcessStatus,
    ProcessManager,
    AgentProcessInfo,
)

__all__ = [
    # boot_mode.py
    "BootMode",
    # process_manager.py
    "ProcessStatus",
    "ProcessManager",
    "AgentProcessInfo",
]
