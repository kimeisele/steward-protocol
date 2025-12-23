"""
vibe_core/state - Unified State Management (PRAKRITI)

OPUS-009: The Repository IS the Mind
OPUS-106: FORTRESS x2 - State + Knowledge Unification

This module provides the unified state engine for the Steward Protocol,
treating every Agent as a Commit, every Decision as a Branch, and
every Learning as a Merge.

Three Layers:
- STHULA (Physical): Git + Ledger + Files
- PRANA (Runtime): Kernel state + Ephemeral
- PURUSHA (Identity): Agent personas

OPUS-106 Additions:
- CognitiveWeaver: State ↔ Knowledge Bridge
- UntotbarMergeEngine: Conflict healing
- GunaClassifier: State Tri-Guna diagnosis
"""

from .cognitive_weaver import (
    CognitiveContext,
    CognitiveWeaver,
    WisdomConsultation,
    get_cognitive_weaver,
)
from .ephemeral_state import EphemeralState, SessionContext, ThoughtEntry
from .file_state import FileState
from .git_state import GitState
from .guna_classifier import (
    GunaClassification,
    GunaClassifier,
    GunaThresholds,
    SystemGunaReport,
    TamasReason,
)
from .kernel_state import AgentSnapshot, KernelSnapshot, KernelState, QueueSnapshot
from .ledger_state import LedgerHead, LedgerState, SyncEvent

# OPUS-106: New components
from .merge_engine import HealedConflict, MergeStrategy, UntotbarMergeEngine

# OPUS-166: NodeState - PULS Layer (Ephemeral file-based presence)
from .node_state import (
    KalaState,
    MailboxMessage,
    NodeSnapshot,
    NodeState,
    SynapseInfo,
    broadcast_message,
    get_all_alive_nodes,
)
from .persona import AgentPersona, PersonaManager
from .prakriti import KernelSessionContext, Prakriti, SyncResult

# OPUS-096: RuntimeStateDefinition - Single source of truth for runtime state
from .runtime_state import (
    RuntimeStateDefinition,
    get_runtime_state_definition,
    reset_runtime_state_definition,
)

# Phase 2: Samskara - Memory Consolidation
from .samskara import (
    Samskara,
    SamskaraReport,
    consolidate_viveka_decisions,
    get_samskara_insights,
)

# OPUS-140: Sanskrit Matrix - Phonemic Memory Compression
from .sanskrit_matrix import (
    AksharaSignature,
    Mantra,
    SanskritMatrixReport,
    encode_samskara,
    find_mantras,
    generate_sanskrit_matrix,
    get_western_translation,
    record_japa,
)
from .schema import CommitResult, CyclePhase, ExecutionResult

# P0: StateService - Single Point of Truth for ALL state writes
from .state_service import (
    StatePolicy,
    StateService,
    WriteResult,
    get_state_service,
    reset_state_service,
)

# OPUS-171: SynapseStore - Unified Synapse Persistence
from .synapse_store import (
    SCHEMA_V1,
    SCHEMA_V2,
    SCHEMA_V3,
    SynapseConnection,
    SynapseMigrationResult,
    SynapseSnapshot,
    SynapseStore,
    detect_schema,
    ensure_v3_schema,
    get_synapse_store,
    migrate_v1_to_v3,
    migrate_v2_to_v3,
    reset_synapse_store,
)
from .sync_holon import (
    GovernanceViolation,
    PluginStateContract,
    StateGuna,
    StatePathInfo,
    StateSyncHolon,
    WatcherConfig,
)

# OPUS-096: StateSyncWeaver - Unified state orchestration
from .weaver import (
    ClassifiedState,
    CommitPlan,
    CommitStrategy,
    StateSyncWeaver,
    WeaverMode,
    WeaverStateMap,
    WeavingAdvice,
    get_state_sync_weaver,
    reset_state_sync_weaver,
)
from .weaver import (
    CommitResult as WeaverCommitResult,
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
    # OPUS-166: NodeState - PULS Layer (Ephemeral file-based presence)
    "NodeState",
    "NodeSnapshot",
    "MailboxMessage",
    "KalaState",
    "SynapseInfo",
    "get_all_alive_nodes",
    "broadcast_message",
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
    # OPUS-106: UntotbarMergeEngine
    "UntotbarMergeEngine",
    "MergeStrategy",
    "HealedConflict",
    # OPUS-106: GunaClassifier
    "GunaClassifier",
    "GunaClassification",
    "GunaThresholds",
    "SystemGunaReport",
    "TamasReason",
    # OPUS-106: CognitiveWeaver (State ↔ Knowledge Bridge)
    "CognitiveWeaver",
    "CognitiveContext",
    "WisdomConsultation",
    "get_cognitive_weaver",
    # OPUS-096: RuntimeStateDefinition (Single Source of Truth)
    "RuntimeStateDefinition",
    "get_runtime_state_definition",
    "reset_runtime_state_definition",
    # OPUS-096: StateSyncWeaver (Unified State Orchestration)
    "StateSyncWeaver",
    "WeaverMode",
    "CommitStrategy",
    "WeaverStateMap",
    "ClassifiedState",
    "WeavingAdvice",
    "CommitPlan",
    "WeaverCommitResult",
    "get_state_sync_weaver",
    "reset_state_sync_weaver",
    # P0: StateService (Single Point of Truth)
    "StateService",
    "StatePolicy",
    "WriteResult",
    "get_state_service",
    "reset_state_service",
    # Phase 2: Samskara (Memory Consolidation)
    "Samskara",
    "SamskaraReport",
    "consolidate_viveka_decisions",
    "get_samskara_insights",
    # OPUS-140: Sanskrit Matrix (Phonemic Compression)
    "AksharaSignature",
    "Mantra",
    "SanskritMatrixReport",
    "encode_samskara",
    "find_mantras",
    "generate_sanskrit_matrix",
    "get_western_translation",
    "record_japa",
    # OPUS-171: SynapseStore (Unified Synapse Persistence)
    "SynapseStore",
    "SynapseConnection",
    "SynapseSnapshot",
    "SynapseMigrationResult",
    "SCHEMA_V1",
    "SCHEMA_V2",
    "SCHEMA_V3",
    "detect_schema",
    "ensure_v3_schema",
    "migrate_v1_to_v3",
    "migrate_v2_to_v3",
    "get_synapse_store",
    "reset_synapse_store",
]
