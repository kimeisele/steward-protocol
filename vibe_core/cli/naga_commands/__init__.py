"""
NAGA CLI COMMANDS - Fractal Command Architecture
=================================================

"If no Protocol, it doesn't exist."

This package contains the fractal CLI commands for NAGA.
Each command is a protocol that maps to:
- MantraOpCode (which operation)
- Mahajana (who owns it)
- Phase (WAKE/PURIFY/SERVE/SUSTAIN)

Directory Structure (4 Phases):
    naga_commands/
    ├── __init__.py       # This file (auto-discovery)
    ├── wake/             # Phase 0-3: System boot
    │   ├── status.py     # SYS_WAKE (PRITHU)
    │   └── identity.py   # LOAD_ROOT (BRAHMA)
    ├── purify/           # Phase 4-7: Validation
    │   ├── scan.py       # ASSERT_TRUTH (VYASA)
    │   ├── detect.py     # RESOLVE_REQ (KUMARAS)
    │   └── gc.py         # GARBAGE_COLLECT (KAPILA)
    ├── serve/            # Phase 8-11: Execution
    │   ├── chat.py       # EXEC_SERVICE (PRAHLADA)
    │   ├── intel.py      # FETCH_RES (PARASHURAMA)
    │   └── commit.py     # COMMIT_LOG (BHISHMA)
    └── sustain/          # Phase 12-15: Maintenance
        ├── cache.py      # CACHE_STATE (NRISIMHA)
        └── reset.py      # RESET_IP (YAMARAJA)

Auto-Discovery (Balarama Pattern):
    Commands are auto-discovered and registered at import time.
    Use the @naga_command decorator to register a command.
"""

from typing import List

from vibe_core.protocols.naga.cli_command import (
    INagaCommand,
    Mahajana,
    NagaCommandBase,
    NagaCommandRegistry,
    NagaCommandResult,
    NAGA_COMMAND_REGISTRY,
    naga_command,
    Phase,
)
from vibe_core.protocols.substrate import MantraOpCode


def discover_commands() -> List[INagaCommand]:
    """
    Discover all commands in this package.

    Balarama pattern: imports trigger registration.
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
    # Enums
    "Mahajana",
    "Phase",
    # Decorator
    "naga_command",
    # Discovery
    "discover_commands",
]
