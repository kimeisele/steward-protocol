"""
VIBE_CORE PROTOCOLS - Layer 1: Interfaces Only

This module contains ONLY abstract base classes (ABCs) that define the interfaces
for all vibe-agency components. No implementations here.

Protocol Modules:
- agent: VibeAgent ABC
- ledger: VibeLedger ABC
- scheduler: VibeScheduler ABC
- registry: ManifestRegistry ABC

These are pure interfaces. All implementations belong in Layer 2.
All wiring belongs in Layer 3 (runtime/).

BLOCKER #2: 3-Layer Architecture - Canonical Protocol Layer
"""

from .agent import AgentManifest, AgentResponse, Capability, VibeAgent
from .ledger import (
    KernelStatus,
    ManifestRegistry,
    VibeKernel,
    VibeLedger,
    VibeScheduler,
)
from .operator_protocol import (
    GitState,
    Intent,
    IntentType,
    KernelStatusType,
    OperatorResponse,
    OperatorSocket,
    OperatorType,
    PriorityLevel,
    SystemContext,
    TaskState,
    create_intent,
    create_response,
    create_system_context,
)

# Note: ManifestRegistry and VibeScheduler are re-exported from .ledger module
# The .registry and .scheduler modules exist for backwards compatibility

__all__ = [
    # Agent Protocol
    "VibeAgent",
    "AgentManifest",
    "AgentResponse",
    "Capability",
    # Kernel Protocol
    "VibeLedger",
    "VibeScheduler",
    "VibeKernel",
    "ManifestRegistry",
    "KernelStatus",
    # Operator Protocol (Phoenix Vimana - Strict Typing)
    "OperatorSocket",
    "SystemContext",
    "Intent",
    "OperatorResponse",
    "IntentType",
    "OperatorType",
    "KernelStatusType",
    "PriorityLevel",
    "GitState",
    "TaskState",
    "create_system_context",
    "create_intent",
    "create_response",
]
