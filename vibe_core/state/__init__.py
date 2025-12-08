"""
vibe_core/state - Unified State Management (PRAKRITI)

OPUS-009: The Repository IS the Mind

This module provides the unified state engine for the Steward Protocol,
treating every Agent as a Commit, every Decision as a Branch, and
every Learning as a Merge.

Three Layers:
- STHULA (Physical): Git + Ledger + Files
- PRANA (Runtime): Kernel state + Ephemeral
- PURUSHA (Identity): Agent personas
"""

from .ephemeral_state import EphemeralState, SessionContext, ThoughtEntry
from .file_state import FileState
from .git_state import GitState
from .kernel_state import AgentSnapshot, KernelSnapshot, KernelState, QueueSnapshot
from .persona import AgentPersona, PersonaManager
from .prakriti import Prakriti

__all__ = [
    # Main engine
    "Prakriti",
    # Layer 1: Physical
    "GitState",
    "FileState",
    # Layer 2: Runtime
    "KernelState",
    "KernelSnapshot",
    "AgentSnapshot",
    "QueueSnapshot",
    "EphemeralState",
    "ThoughtEntry",
    "SessionContext",
    # Layer 3: Identity
    "PersonaManager",
    "AgentPersona",
]
