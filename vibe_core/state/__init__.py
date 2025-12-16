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
from .ledger_state import LedgerHead, LedgerState, SyncEvent
from .persona import AgentPersona, PersonaManager
from .prakriti import CommitResult, KernelSessionContext, Prakriti, SyncResult
from .sync_holon import (
    GovernanceViolation,
    PluginStateContract,
    StateGuna,
    StatePathInfo,
    StateSyncHolon,
    WatcherConfig,
)

__all__ = [
    # Main engine
    "Prakriti",
    "CommitResult",
    "SyncResult",
    "KernelSessionContext",
    # Layer 1: Physical (STHULA)
    "GitState",
    "FileState",
    "LedgerState",
    "LedgerHead",
    "SyncEvent",
    # Layer 2: Runtime (PRANA)
    "KernelState",
    "KernelSnapshot",
    "AgentSnapshot",
    "QueueSnapshot",
    "EphemeralState",
    "ThoughtEntry",
    "SessionContext",
    # Layer 3: Identity (PURUSHA)
    "PersonaManager",
    "AgentPersona",
    # StateSyncHolon (OPUS-009 Unified Weaver)
    "StateSyncHolon",
    "StateGuna",
    "StatePathInfo",
    "PluginStateContract",
    "WatcherConfig",
    "GovernanceViolation",
]
