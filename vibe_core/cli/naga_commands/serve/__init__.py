"""
SERVE PHASE COMMANDS (8-11)
===========================

Phase 3 of the Mahamantra CPU cycle.
Commands in this phase handle execution and service.

Mahajanas:
    8.  PARASHURAMA (Avatara) - FETCH_RES (intel)
    9.  PRAHLADA - EXEC_SERVICE (chat)
    10. JANAKA - CHECK_DHARMA (validate)
    11. BHISHMA - COMMIT_LOG (commit)
"""

# Import commands to trigger registration
from vibe_core.cli.naga_commands.serve.chat import ChatCommand
from vibe_core.cli.naga_commands.serve.intel import IntelCommand

__all__ = [
    "ChatCommand",
    "IntelCommand",
]
