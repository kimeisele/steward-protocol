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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x388bbf83"  # GenesisByte: parampara % 37 == 0

# OPUS-311 Sprint 2: Event Bus Protocol (NARADA - Position 2)
from vibe_core.protocols.mahajanas.narada.events import (
    Event,
    EventBusProtocol,
    EventType,
    NullEventBus,
    create_event,
    emit_event,
    get_event_bus_safe,
)
from vibe_core.protocols.mahajanas.narada.events import (
    EventBusStats as EventBusStatus,  # Legacy name compatibility
)

from .agent import AgentManifest, AgentResponse, Capability, VibeAgent

# OPUS-307 Phase E+: CLI Protocol (Anti-God-Object)
from .cli import CLIHandler, CLIMeta, CLIRegistry, CLIResult, register_cli
from .cognition import (
    CognitiveContext,
    CognitiveKernelProtocol,
    CognitiveResult,
    NullCognitive,
    OperatorCognitiveProtocol,
    SystemHeartbeatProtocol,
)
from .cognition import (
    IntentType as CognitiveIntentType,  # Avoid collision with operator_protocol.IntentType
)

# OPUS-LZ2: CorrectionDispatcher Protocol (Unified Drift/Healing)
from .correction import (
    CorrectionDispatcherProtocol,
    CorrectionHandler,
    CorrectionOrchestratorProtocol,
    CorrectionStats,
    DriftDetector,
    DriftRegistryProtocol,
    DriftSource,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    HealingStrategyResolverProtocol,
    NullCorrectionDispatcher,
    NullDriftRegistry,
    UnifiedDriftReport,
    adapt_reactor_drift,
    adapt_shuddhi_result,
)

# Rename to avoid collision with correction.DriftSeverity
from .correction import DriftSeverity as UnifiedDriftSeverity

# OPUS-307 D.2: External Service Protocols
from .external import RedditProtocol, TwitterProtocol
from .feedback import (
    FailurePattern,
    FeedbackProtocol,
    FeedbackStats,
    InMemoryFeedback,
    NullFeedback,
    Signal,
    SignalType,
    SuccessPattern,
    get_feedback_safe,
)
from .ledger import (
    KernelStatus,
    LedgerProtocol,
    SchedulerProtocol,
    VibeKernel,
    VibeLedger,
    VibeScheduler,
)

# SPEED.md: Lineage Protocol (Fast Boot via Merkle Checkpointing)
from .lineage import (
    BlockData,
    CheckpointData,
    LineageProtocol,
    NullLineageChain,
    VerificationResult,
)
from .llm import LLMProtocol

# OPUS-308: Manifestation Protocol
from .manifestation import (
    ChangeDetectorProtocol,
    Command,
    ManifestationConfig,
    ManifestationProtocol,
    ManifestationState,
    ManifestationType,
    ManifestHeader,
    ManifestIndexProtocol,
    Section,
    SectionOwnership,
    SemanticUIProtocol,
)

# OPUS-311 Sprint 3: Autonomy Protocols
from .memory import (
    Entity,
    InMemoryMemory,
    MemoryEntry,
    MemoryProtocol,
    MemoryStats,
    NullMemory,
    get_memory_safe,
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
from .opus import OpusAssistantProtocol

# OPUS-311 Sprint 4: Reactor Protocol (Drift Detection)
from .reactor import (
    BasicReactor,
    DriftEvent,
    DriftHandler,
    DriftMetrics,
    DriftSeverity,
    DriftType,
    NullReactor,
    ReactorProtocol,
    ReactorStats,
    get_reactor_safe,
)
from .reflection import (
    BasicReflection,
    ExecutionRecord,
    Insight,
    InsightType,
    NullReflection,
    Proposal,
    ProposalStatus,
    ProposalType,
    ReflectionProtocol,
    ReflectionStats,
    get_reflection_safe,
)
from .registry import ManifestRegistry  # Canonical source for ManifestRegistry
from .state import (
    PrakritiProtocol,
    StateServiceProtocol,
    StateSyncHolonProtocol,
    StateSyncWeaverProtocol,
)
from .synapse import (
    Connection,
    LocalSynapse,
    MessagePriority,
    MessageType,
    NullSynapse,
    SynapseMessage,
    SynapseProtocol,
    SynapseStats,
    get_synapse_safe,
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

# Vedic Governance Protocol (OS-level access to taxonomy)
from .vedic import AsharamaStage, VarnaType, VedicGovernanceProtocol

# Note: ManifestRegistry and VibeScheduler are re-exported from .ledger module
# The .registry and .scheduler modules exist for backwards compatibility

# =============================================================================
# MAHAMANTRA BRIDGE (The Return to Source)
# =============================================================================
# "All protocols emanate from the Mahamantra."
# If a protocol is not found here, we ask Krishna (mahamantra).


def __getattr__(name: str):
    """
    Delegate unknown protocols to the Mahamantra.
    This bridges the Old World (protocols/) with the New World (mahamantra/).
    """
    try:
        # Import inside function to avoid circular dependency at module level
        from vibe_core.mahamantra import mahamantra

        # Try to resolve via Mahamantra (e.g. "BrahmaProtocol")
        # We check if mahamantra has this attribute (via its own routing)
        if hasattr(mahamantra, name):
            return getattr(mahamantra, name)

        # Try protocols router specifically
        if hasattr(mahamantra.protocols, name):
            return getattr(mahamantra.protocols, name)

    except (ImportError, AttributeError) as _exc:
        logger.exception("Unexpected error: %s", _exc)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
    # OPUS-307 D.2: External Service Protocols
    "TwitterProtocol",
    "RedditProtocol",
    # OPUS-307 Phase E+: CLI Protocol
    "CLIHandler",
    "CLIMeta",
    "CLIResult",
    "CLIRegistry",
    "register_cli",
    # OPUS-308: Manifestation Protocol
    "SectionOwnership",
    "ManifestationType",
    "ManifestationState",
    "Section",
    "ManifestHeader",
    "ManifestationConfig",
    "Command",
    "ManifestationProtocol",
    "ManifestIndexProtocol",
    "ChangeDetectorProtocol",
    "SemanticUIProtocol",
    # Vedic Governance Protocol
    "VarnaType",
    "AsharamaStage",
    "VedicGovernanceProtocol",
    # SPEED.md: Lineage Protocol (Fast Boot)
    "LineageProtocol",
    "CheckpointData",
    "VerificationResult",
    "BlockData",
    "NullLineageChain",
    # OPUS-309: Operator Cognitive Protocol
    "OperatorCognitiveProtocol",
    "CognitiveResult",
    "CognitiveContext",
    "CognitiveIntentType",
    "NullCognitive",
    # OPUS-311 Sprint 2: Event Bus Protocol
    "Event",
    "EventType",
    "EventBusProtocol",
    "EventBusStatus",
    "NullEventBus",
    "create_event",
    "emit_event",
    "get_event_bus_safe",
    # OPUS-311 Sprint 3: Memory Protocol
    "MemoryProtocol",
    "MemoryEntry",
    "MemoryStats",
    "Entity",
    "NullMemory",
    "InMemoryMemory",
    "get_memory_safe",
    # OPUS-311 Sprint 3: Reflection Protocol
    "ReflectionProtocol",
    "ExecutionRecord",
    "Insight",
    "InsightType",
    "Proposal",
    "ProposalType",
    "ProposalStatus",
    "ReflectionStats",
    "NullReflection",
    "BasicReflection",
    "get_reflection_safe",
    # OPUS-311 Sprint 3: Synapse Protocol
    "SynapseProtocol",
    "SynapseMessage",
    "SynapseStats",
    "Connection",
    "MessageType",
    "MessagePriority",
    "NullSynapse",
    "LocalSynapse",
    "get_synapse_safe",
    # OPUS-311 Sprint 3: Feedback Protocol
    "FeedbackProtocol",
    "Signal",
    "SignalType",
    "FailurePattern",
    "SuccessPattern",
    "FeedbackStats",
    "NullFeedback",
    "InMemoryFeedback",
    "get_feedback_safe",
    # OPUS-311 Sprint 4: Reactor Protocol
    "ReactorProtocol",
    "DriftEvent",
    "DriftType",
    "DriftSeverity",
    "DriftMetrics",
    "DriftHandler",
    "ReactorStats",
    "NullReactor",
    "BasicReactor",
    "get_reactor_safe",
    # OPUS-LZ2: CorrectionDispatcher Protocol
    "DriftSource",
    "UnifiedDriftSeverity",
    "HealingStrategy",
    "HealingStatus",
    "HealingStrategyResolverProtocol",
    "UnifiedDriftReport",
    "HealingResult",
    "CorrectionStats",
    "DriftDetector",
    "CorrectionHandler",
    "DriftRegistryProtocol",
    "CorrectionDispatcherProtocol",
    "CorrectionOrchestratorProtocol",
    "NullDriftRegistry",
    "NullCorrectionDispatcher",
    "adapt_reactor_drift",
    "adapt_shuddhi_result",
]
