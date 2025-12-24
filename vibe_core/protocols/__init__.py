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
from .cognition import CognitiveKernelProtocol, SystemHeartbeatProtocol
from .llm import LLMProtocol
from .opus import OpusAssistantProtocol
from .ledger import (
    KernelStatus,
    VibeKernel,
    VibeLedger,
    VibeScheduler,
)
from .operator_protocol import (
    GitState,
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
from .registry import ManifestRegistry  # Canonical source for ManifestRegistry
from .state import (
    PrakritiProtocol,
    StateServiceProtocol,
    StateSyncHolonProtocol,
    StateSyncWeaverProtocol,
)

# Universal Testable Protocol
from .testable import (
    AgentTestableAdapter,
    BaseTestable,
    EventBusTestableAdapter,
    LedgerTestableAdapter,
    PluginTestableAdapter,
    SchedulerTestableAdapter,
    Testable,
    TestableType,
    TestCase,
    ToolTestableAdapter,
)
from .testable_registry import (
    TestableRegistry,
    get_global_registry,
    reset_global_registry,
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
    # State Protocols
    "PrakritiProtocol",
    "StateServiceProtocol",
    "StateSyncHolonProtocol",
    "StateSyncWeaverProtocol",
    # Operator Protocol (Phoenix Vimana - Strict Typing)
    "OperatorSocket",
    "SystemContext",
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
    # Universal Testable Protocol (Fractal Testing)
    "Testable",
    "TestableType",
    "TestCase",
    "BaseTestable",
    "AgentTestableAdapter",
    "PluginTestableAdapter",
    "ToolTestableAdapter",
    "LedgerTestableAdapter",
    "SchedulerTestableAdapter",
    "EventBusTestableAdapter",
    "TestableRegistry",
    "get_global_registry",
    "reset_global_registry",
]
