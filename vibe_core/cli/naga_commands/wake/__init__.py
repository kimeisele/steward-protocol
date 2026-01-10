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

WAKE PHASE COMPLETE - All 4 positions filled.
"""

# Import commands to trigger registration (Balarama pattern)
from vibe_core.cli.naga_commands.wake.status import StatusCommand
from vibe_core.cli.naga_commands.wake.identity import IdentityCommand
from vibe_core.cli.naga_commands.wake.resources import ResourcesCommand
from vibe_core.cli.naga_commands.wake.context import ContextCommand

__all__ = [
    "StatusCommand",     # PRITHU - SYS_WAKE (Position 0)
    "IdentityCommand",   # BRAHMA - LOAD_ROOT (Position 1)
    "ResourcesCommand",  # NARADA - ALLOC_MEM (Position 2)
    "ContextCommand",    # SHAMBHU - BIND_CTX (Position 3)
]
