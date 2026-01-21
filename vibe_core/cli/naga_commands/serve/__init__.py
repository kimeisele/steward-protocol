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

SERVE PHASE COMPLETE - All 4 positions filled.
"""

# Import commands to trigger registration (Balarama pattern)
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xd73acabf"  # GenesisByte: parampara % 37 == 0

from vibe_core.cli.naga_commands.serve.chat import ChatCommand
from vibe_core.cli.naga_commands.serve.intel import IntelCommand
from vibe_core.cli.naga_commands.serve.validate import ValidateCommand
from vibe_core.cli.naga_commands.serve.commit import CommitCommand
from vibe_core.cli.naga_commands.serve.diagnose import DiagnoseCommand

__all__ = [
    "DiagnoseCommand",  # NARADA - System diagnostics (NOT shravana!)
    "IntelCommand",  # SHUKA - FETCH_RES (Position 8)
    "ChatCommand",  # PRAHLADA - EXEC_SERVICE (Position 9)
    "ValidateCommand",  # JANAKA - CHECK_DHARMA (Position 10)
    "CommitCommand",  # BHISHMA - COMMIT_LOG (Position 11)
]
