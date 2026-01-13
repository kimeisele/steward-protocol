"""
NAGA CLI COMMANDS - Fractal Command Architecture
=================================================

"If no Protocol, it doesn't exist."

This package contains the fractal CLI commands for NAGA.
Each command is a protocol that maps to:
- MantraOpCode (which operation)
- Owner (who owns it: Avatara for HEADs, Mahajana for Workers)
- Phase (WAKE/PURIFY/SERVE/SUSTAIN)

CHATUR-VYUHA ARCHITECTURE:
==========================
16 = 4 Avataras (HEADs) + 12 Mahajanas (Workers)

Avataras (Vishnu's incarnations, own HEAD positions):
    - PRITHU (Q1 HEAD) - SYS_WAKE
    - VYASA (Q2 HEAD) - ASSERT_TRUTH
    - PARASHURAMA (Q3 HEAD) - FETCH_RES
    - NRISIMHA (Q4 HEAD) - CACHE_STATE

Mahajanas (Devotee authorities, own Worker positions):
    - 12 workers from BRAHMA to YAMARAJA

Directory Structure (4 Phases × 4 Commands = 16 Total):
    naga_commands/
    ├── __init__.py       # This file (auto-discovery)
    ├── wake/             # Phase 0-3: System boot
    │   ├── status.py     # SYS_WAKE (PRITHU - Avatara)
    │   ├── identity.py   # LOAD_ROOT (BRAHMA - Mahajana)
    │   ├── resources.py  # ALLOC_MEM (NARADA - Mahajana)
    │   └── context.py    # BIND_CTX (SHAMBHU - Mahajana)
    ├── purify/           # Phase 4-7: Validation
    │   ├── scan.py       # ASSERT_TRUTH (VYASA - Avatara)
    │   ├── detect.py     # RESOLVE_REQ (KUMARAS - Mahajana)
    │   ├── gc.py         # GARBAGE_COLLECT (KAPILA - Mahajana)
    │   └── flood.py      # PULSE_SYNC (MANU - Mahajana)
    ├── serve/            # Phase 8-11: Execution
    │   ├── intel.py      # FETCH_RES (PARASHURAMA - Avatara)
    │   ├── chat.py       # EXEC_SERVICE (PRAHLADA - Mahajana)
    │   ├── validate.py   # CHECK_DHARMA (JANAKA - Mahajana)
    │   └── commit.py     # COMMIT_LOG (BHISHMA - Mahajana)
    └── sustain/          # Phase 12-15: Maintenance
        ├── cache.py      # CACHE_STATE (NRISIMHA - Avatara)
        ├── optimize.py   # OPTIMIZE (BALI - Mahajana)
        ├── yield_cmd.py  # YIELD_CPU (SHUKA - Mahajana)
        └── reset.py      # RESET_IP (YAMARAJA - Mahajana)

ALL 16 POSITIONS FILLED - MAHAMANTRA COMPLETE.
4 Avataras + 12 Mahajanas = 16 Owners

Auto-Discovery (Balarama Pattern):
    Commands are auto-discovered and registered at import time.
    Use the @naga_command decorator with owner=Owner.X to register.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x5e6cdfed"  # GenesisByte: parampara % 37 == 0

from typing import List

from vibe_core.protocols.naga.cli_command import (
    Avatara,
    INagaCommand,
    Mahajana,
    NagaCommandBase,
    NagaCommandRegistry,
    NagaCommandResult,
    NAGA_COMMAND_REGISTRY,
    naga_command,
    OPCODE_TO_OWNER,
    Owner,
    Phase,
    route_opcode,
)
from vibe_core.protocols.substrate import MantraOpCode


def discover_commands() -> List[INagaCommand]:
    """
    Discover all commands in this package.

    Balarama pattern: imports trigger registration.
    All 4 phases × 4 commands = 16 total positions.
    """
    # Import subpackages to trigger @naga_command decorators
    try:
        from vibe_core.cli.naga_commands import wake
    except ImportError:
        pass

    try:
        from vibe_core.cli.naga_commands import purify
    except ImportError:
        pass

    try:
        from vibe_core.cli.naga_commands import serve
    except ImportError:
        pass

    try:
        from vibe_core.cli.naga_commands import sustain
    except ImportError:
        pass

    return NAGA_COMMAND_REGISTRY.list_all()


__all__ = [
    # Protocol
    "INagaCommand",
    # Base
    "NagaCommandBase",
    # Registry
    "NagaCommandRegistry",
    "NAGA_COMMAND_REGISTRY",
    # Result
    "NagaCommandResult",
    # CHATUR-VYUHA Types (from real infrastructure)
    "Avatara",      # 4 HEADs (from protocols/avataras)
    "Mahajana",     # 12 Workers (from protocols/mahajanas/router)
    "Owner",        # Union[Avatara, Mahajana] - derived from opcode!
    "Phase",        # 4 Phases
    # Routing (via vyuha - "The Mahamantra links back")
    "route_opcode",
    "OPCODE_TO_OWNER",
    # Decorator
    "naga_command",
    # Discovery
    "discover_commands",
]
