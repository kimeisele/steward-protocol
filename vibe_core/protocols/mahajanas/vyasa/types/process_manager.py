"""
PROCESS MANAGER — Re-export Shim
=================================

SSOT: vibe_core.mahamantra.substrate.process_manager
This file re-exports all symbols from the SSOT to maintain backward compatibility.
The SSOT version uses Seed constants (KSETRAJNA, HALVES) instead of hardcoded values.

DO NOT add new code here. Edit the SSOT instead.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x70acde90"  # GenesisByte: parampara % 37 == 0

# Re-export everything from SSOT
from vibe_core.mahamantra.substrate.process_manager import (  # noqa: F401
    AgentProcess,
    AgentProcessInfo,
    MAX_MESSAGE_SIZE,
    ProcessManager,
    ProcessStatus,
    _run_agent_process,
    get_max_message_size,
)
