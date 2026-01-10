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
"""

# Import commands to trigger registration (Balarama pattern)
from vibe_core.cli.naga_commands.purify.scan import ScanCommand
from vibe_core.cli.naga_commands.purify.detect import DetectCommand
from vibe_core.cli.naga_commands.purify.flood import FloodCommand

__all__ = [
    "ScanCommand",
    "DetectCommand",
    "FloodCommand",
]
