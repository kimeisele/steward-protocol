"""
vibe_core/state - Unified State Management (PRAKRITI)
=====================================================

MAHASTATE IS KING. All access routes through MahaState.

"alte struktur in neue struktur"
Old imports still work, but singleton getters route through MahaState.
MahaState is the sovereign - the SINGLE POINT OF TRUTH.

OPUS-009: The Repository IS the Mind
OPUS-106: FORTRESS x2 - State + Knowledge Unification

Three Layers:
- STHULA (Physical): Git + Ledger + Files
- PRANA (Runtime): Kernel state + Ephemeral
- PURUSHA (Identity): Agent personas

ROUTING:
- get_prakriti()         → MahaState.prakriti
- get_state_service()    → MahaState.state_service
- get_sync_holon()       → MahaState.sync_holon
- get_weaver()           → MahaState.weaver
- get_cognitive_weaver() → MahaState.cognitive_weaver
- get_guna_classifier()  → MahaState.guna_classifier
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x1f10b83d"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# MAHASTATE - THE KING (Import first, route through it)
# =============================================================================

from vibe_core.mahamantra.substrate.maha_state import (
    MahaState,
    StateEntry,
    get_maha_state,
    pierce,
)

# =============================================================================
# SOVEREIGN SINGLETON GETTERS (Route through MahaState)
# =============================================================================


def get_prakriti(workspace: Optional[Path] = None) -> Optional["Prakriti"]:
    """Get Prakriti through MahaState (the sovereign)."""
    return get_maha_state(workspace).prakriti


def get_sync_holon(workspace: Optional[Path] = None) -> Optional["StateSyncHolon"]:
    """Get StateSyncHolon through MahaState (the sovereign)."""
    return get_maha_state(workspace).sync_holon


def get_guna_classifier(workspace: Optional[Path] = None) -> Optional["GunaClassifier"]:
    """Get GunaClassifier through MahaState (the sovereign)."""
    return get_maha_state(workspace).guna_classifier


# =============================================================================
# RAW CLASSES (For direct instantiation if needed - legacy compat)
# =============================================================================

from .cognitive_weaver import (
    CognitiveContext,
    CognitiveWeaver,
    WisdomConsultation,
)
# OVERRIDE: Route through MahaState
from .cognitive_weaver import get_cognitive_weaver as _raw_get_cognitive_weaver


def get_cognitive_weaver(workspace: Optional[Path] = None) -> Optional[CognitiveWeaver]:
    """Get CognitiveWeaver through MahaState (the sovereign)."""
    return get_maha_state(workspace).cognitive_weaver


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
)
# OVERRIDE: Route through MahaState
from .state_service import get_state_service as _raw_get_state_service
from .state_service import reset_state_service


def get_state_service(
    workspace: Optional[Path] = None,
    agent_id: Optional[str] = None,
    plugin_id: Optional[str] = None,
) -> Optional[StateService]:
    """Get StateService through MahaState (the sovereign)."""
    return get_maha_state(workspace).state_service


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
)
# OVERRIDE: Route through MahaState
from .weaver import get_state_sync_weaver as _raw_get_state_sync_weaver
from .weaver import reset_state_sync_weaver


def get_state_sync_weaver(
    prakriti: Optional["Prakriti"] = None,
    holon: Optional["StateSyncHolon"] = None,
    workspace: Optional[Path] = None,
) -> Optional[StateSyncWeaver]:
    """Get StateSyncWeaver through MahaState (the sovereign)."""
    return get_maha_state(workspace).weaver


from .weaver import (
    CommitResult as WeaverCommitResult,
)

__all__ = [
    # ==========================================================================
    # MAHASTATE - THE KING (All access routes through here)
    # ==========================================================================
    "MahaState",
    "StateEntry",
    "get_maha_state",
    "pierce",
    # Sovereign getters (route through MahaState)
    "get_prakriti",
    "get_sync_holon",
    "get_guna_classifier",
    # ==========================================================================
    # LEGACY CLASSES (For direct instantiation - backwards compat)
    # ==========================================================================
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
    "get_cognitive_weaver",  # Routes through MahaState
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
    "get_state_sync_weaver",  # Routes through MahaState
    "reset_state_sync_weaver",
    # P0: StateService (Single Point of Truth)
    "StateService",
    "StatePolicy",
    "WriteResult",
    "get_state_service",  # Routes through MahaState
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
