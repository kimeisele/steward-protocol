"""
Cortex Engines - The cognitive processing units.

Each engine is a specialized processor:
- semantic_engine: Neural understanding (optional, requires numpy/sentence-transformers)
- circuit_engine: State machine execution
- reflex_engine: Fast pattern matching
- playbook_engine: DAG workflows (TODO: migrate)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xda025e9c"  # GenesisByte: parampara % 37 == 0

from vibe_core.cortex.engines.circuit_engine import (
    CircuitExecutionResult,
    CircuitState,
    CognitiveCircuitExecutor,
    InvariantChecker,
    MetaCircuitManager,
    create_circuit_executor,
    create_circuit_executor_with_meta,
)
from vibe_core.cortex.engines.reflex_engine import ReflexEngine

# Semantic engine is optional (excluded in binary build for thin kernel)
try:
    from vibe_core.cortex.engines.semantic_engine import (
        ConfidenceLevel,
        SemanticConcept,
        SemanticRouter,
    )

    SEMANTIC_AVAILABLE = True
except ImportError:
    # numpy/sentence-transformers not installed - use None placeholders
    SemanticRouter = None
    SemanticConcept = None
    ConfidenceLevel = None
    SEMANTIC_AVAILABLE = False

__all__ = [
    "SemanticRouter",
    "SemanticConcept",
    "ConfidenceLevel",
    "SEMANTIC_AVAILABLE",
    "CognitiveCircuitExecutor",
    "CircuitState",
    "CircuitExecutionResult",
    "InvariantChecker",
    "MetaCircuitManager",
    "create_circuit_executor",
    "create_circuit_executor_with_meta",
    "ReflexEngine",
]
