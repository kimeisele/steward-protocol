"""
SUSTAIN PHASE COMMANDS (12-15)
==============================

Phase 4 of the Mahamantra CPU cycle.
Commands in this phase handle persistence and shutdown.

Mahajanas:
    12. NRISIMHA (Avatara) - CACHE_STATE (cache)
    13. BALI - OPTIMIZE (optimize)
    14. SHUKA - YIELD_CPU (yield)
    15. YAMARAJA - RESET_IP (reset)

SUSTAIN PHASE COMPLETE - All 4 positions filled.
"""

# Import commands to trigger registration (Balarama pattern)
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xf2f4234d"  # GenesisByte: parampara % 37 == 0

from vibe_core.cli.naga_commands.sustain.cache import CacheCommand
from vibe_core.cli.naga_commands.sustain.optimize import OptimizeCommand
from vibe_core.cli.naga_commands.sustain.yield_cmd import YieldCommand
from vibe_core.cli.naga_commands.sustain.reset import ResetCommand

__all__ = [
    "CacheCommand",  # NRISIMHA - CACHE_STATE (Position 12)
    "OptimizeCommand",  # BALI - OPTIMIZE (Position 13)
    "YieldCommand",  # SHUKA - YIELD_CPU (Position 14)
    "ResetCommand",  # YAMARAJA - RESET_IP (Position 15)
]
