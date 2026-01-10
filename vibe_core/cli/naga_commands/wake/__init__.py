"""
WAKE PHASE COMMANDS (0-3)
=========================

Phase 0 of the Mahamantra CPU cycle.
Commands in this phase handle system initialization.

Mahajanas:
    0. PRITHU (Avatara) - SYS_WAKE (status)
    1. BRAHMA - LOAD_ROOT (identity)
    2. NARADA - ALLOC_MEM (resources)
    3. SHAMBHU - BIND_CTX (context)
"""

# Import commands to trigger registration
from vibe_core.cli.naga_commands.wake.status import StatusCommand

__all__ = [
    "StatusCommand",
]
