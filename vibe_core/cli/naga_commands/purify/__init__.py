"""
PURIFY PHASE COMMANDS (4-7)
===========================

Phase 1 of the Mahamantra CPU cycle.
Commands in this phase handle validation and cleanup.

Mahajanas:
    4. VYASA (Avatara) - ASSERT_TRUTH (scan)
    5. KUMARAS - RESOLVE_REQ (detect/intent)
    6. KAPILA - GARBAGE_COLLECT (gc/analysis)
    7. MANU - PULSE_SYNC (flood/heartbeat)

PURIFY PHASE COMPLETE - All 4 positions filled.
"""

# Import commands to trigger registration (Balarama pattern)
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x1bbab70b"  # GenesisByte: parampara % 37 == 0

from vibe_core.cli.naga_commands.purify.scan import ScanCommand
from vibe_core.cli.naga_commands.purify.detect import DetectCommand
from vibe_core.cli.naga_commands.purify.gc import GcCommand
from vibe_core.cli.naga_commands.purify.flood import FloodCommand

__all__ = [
    "ScanCommand",   # VYASA - ASSERT_TRUTH (Position 4)
    "DetectCommand", # KUMARAS - RESOLVE_REQ (Position 5)
    "GcCommand",     # KAPILA - GARBAGE_COLLECT (Position 6)
    "FloodCommand",  # MANU - PULSE_SYNC (Position 7)
]
