"""
CORTEX - The Cognitive Engine Layer

The brain of the Steward Protocol. Contains all cognitive engines:
- SemanticEngine: Neural embedding and routing (PROJECT JNANA) - optional
- CircuitEngine: State machine executor (Neuro-Symbolic)
- ReflexEngine: Fast deterministic responses
- PlaybookEngine: DAG-based workflow execution

Architecture:
    User Input -> Cortex -> Kernel -> Agents

The Cortex is the ARTHA (meaning/code) layer that processes
CONFIG (SHABDA/PRATYAYA) and produces RUNTIME (KARMA) state.
"""

# Re-export from engines (which handles optional semantic imports)
from vibe_core.cortex.engines import (
    SEMANTIC_AVAILABLE,
    CircuitExecutionResult,
    CircuitState,
    CognitiveCircuitExecutor,
    ConfidenceLevel,
    InvariantChecker,
    MetaCircuitManager,
    ReflexEngine,
    SemanticConcept,
    SemanticRouter,
    create_circuit_executor,
    create_circuit_executor_with_meta,
)

__all__ = [
    # Semantic Engine (optional - requires numpy/sentence-transformers)
    "SemanticRouter",
    "SemanticConcept",
    "ConfidenceLevel",
    "SEMANTIC_AVAILABLE",
    # Circuit Engine
    "CognitiveCircuitExecutor",
    "CircuitState",
    "CircuitExecutionResult",
    "InvariantChecker",
    "MetaCircuitManager",
    "create_circuit_executor",
    "create_circuit_executor_with_meta",
    # Reflex Engine
    "ReflexEngine",
]
