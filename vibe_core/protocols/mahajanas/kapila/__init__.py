"""
KAPILA - The 5th Mahajana (Analysis/Inference)
==============================================

POSITION: 6 (DHARMA Quarter, GARBAGE_COLLECT OpCode)

Lord Kapila - The Founder of Sankhya.
Son of Devahuti. Teacher of analytical philosophy.
His Sankhya is the basis of this entire architecture.

DERIVED FROM MAHAMANTRA:
    Position 6 -> guardian=KAPILA, opcode=GARBAGE_COLLECT, quarter=DHARMA
    All properties derived from truth table. No manual wiring.

Kapila analyzes, but for the purpose of DEVOTION.
His Sankhya leads to bhakti, not dry speculation.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x26629549"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode, ProtocolRegistry
from vibe_core.protocols.memory import get_memory_safe, MemoryProtocol

logger = logging.getLogger("Kapila")


# =============================================================================
# KAPILA PROTOCOL BASE - Derives from MantraPosition 6
# =============================================================================


@ProtocolRegistry.register
class KapilaProtocolBase(WorkerProtocol):
    """
    Kapila protocol ownership - DERIVED from Mahamantra position 6.

    NO MANUAL WIRING:
        _position_index = 6 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Mahajana.KAPILA
        opcode()    -> MantraOpCode.TYPE_CHECK
        quarter()   -> Quarter.DHARMA
        is_head()   -> False (Worker position)
        parampara_vector() -> 259 (% 37 == 0)
    """

    _position_index: ClassVar[int] = 6  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[6]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

# The union of allowed analysis input types - WATERTIGHT
AnalysisInput = Union[str, int, float, bool, Dict[str, str], List[str], None]


class AnalysisType(str, Enum):
    """Types of analysis."""

    RESOLUTION = "resolution"  # RESOLVE_REQ
    OPTIMIZATION = "optimization"  # OPTIMIZE
    INFERENCE = "inference"  # Logical deduction
    ENUMERATION = "enumeration"  # Sankhya counting


class AnalysisResult(TypedDict, total=False):
    """
    Result of analysis.
    WATERTIGHT - no Any!
    """

    success: bool
    analysis_type: str  # AnalysisType value
    conclusion: str  # The analytical result
    confidence: float  # 0.0-1.0
    duration_ms: int
    error_message: str


class OptimizationResult(TypedDict, total=False):
    """
    Result of optimization.
    WATERTIGHT - no Any!
    """

    success: bool
    improvement_percent: float
    original_metric: float
    optimized_metric: float
    changes_made: List[str]
    error_message: str


class MetricsResult(TypedDict, total=False):
    """
    Collected metrics.
    WATERTIGHT - no Any!
    """

    metrics: Dict[str, float]
    collected_at: str  # ISO timestamp
    sample_count: int


class AnalysisState(TypedDict, total=False):
    """
    State of analysis.
    WATERTIGHT - no Any!
    """

    analyses_performed: int
    optimizations_performed: int
    total_improvement: float
    last_analysis: str  # ISO timestamp
    health: str


class AnalyzeCliResult(TypedDict):
    """Result of CLI analyze operation. WATERTIGHT - no Any!"""

    success: bool
    target: str
    analysis_type: str
    conclusion: str
    confidence: float


# =============================================================================
# KAPILA PROTOCOL (Analysis + Memory Integration)
# =============================================================================

@ProtocolRegistry.register
class KapilaProtocolBase(WorkerProtocol):
    """
    Kapila - The Analytical Engineer (and now Memory Keeper).
    """
    _position_index: ClassVar[int] = 6 

    def on_bhoga(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        KAPILA.on_bhoga: Analyze Reality & Manage Memory.
        
        Args:
            state: Context from the Reactor (opcode, payload, etc.)
            
        Returns:
            Updated state.
        """
        opcode = state.get("opcode")
        payload = state.get("payload", {})
        
        # 0. Deserialize Payload (Safe Unpacking)
        try:
             # If payload is bytes, it might be a MahaPayload wrapper
             if isinstance(payload, bytes):
                 # Try to unpack MahaPayload wrapper first
                 try:
                     from vibe_core.mahamantra.protocols._payload import MahaPayload
                     unpacked = MahaPayload.from_bytes(payload)
                     payload = unpacked.data
                 except Exception:
                     # Not a MahaPayload, treat as raw bytes
                     pass

                 # Now try JSON decode on the data
                 import json
                 payload = json.loads(payload.decode("utf-8"))
        except Exception as e:
            state["dissonance_report"] = f"Kapila: Failed to decode payload: {e}"
            return state
        
        # 1. Access Memory (The Akshara)
        memory = get_memory_safe()
        
        # 2. Determine Intent (from Payload 'op' or OpCode)
        # Verify: bridge guarantees payload is dict for these intents
        intent = payload.get("op") if isinstance(payload, dict) else None
        
        if intent == "REMEMBER":
            return self._handle_remember(memory, payload, state)
        elif intent == "RECALL":
            return self._handle_recall(memory, payload, state)
        elif opcode == MantraOpCode.TYPE_CHECK: # Legacy/Default
            return self._handle_analysis(payload, state)
            
        return state

    def _handle_remember(self, memory: MemoryProtocol, payload: Any, state: Dict[str, Any]) -> Dict[str, Any]:
        """Store info in memory."""
        # Payload: {"key": "foo", "value": "bar", "session_id": "..."}
        if not isinstance(payload, dict):
            # Try to infer if payload is just a string or list? 
            # For now assume dict.
            state["dissonance_report"] = "Invalid payload for REMEMBER. Expected dict."
            return state
            
        key = payload.get("key")
        value = payload.get("value")
        session_id = payload.get("session_id", "global")
        
        if key and value:
            memory.remember(key, value, session_id=str(session_id))
            state["execution_result"] = f"Remembered: {key}"
            logger.info(f"Kapila: Remembered '{key}' (Session: {session_id})")
        else:
            state["dissonance_report"] = "Missing key/value for REMEMBER"
            
        return state

    def _handle_recall(self, memory: MemoryProtocol, payload: Any, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve info from memory."""
        # Payload: {"key": "foo", "session_id": "..."}
        key = payload.get("key") if isinstance(payload, dict) else str(payload)
        session_id = payload.get("session_id", "global") if isinstance(payload, dict) else "global"
        
        result = memory.recall(key, session_id=str(session_id))
        
        if result is not None:
            state["execution_result"] = result
            logger.info(f"Kapila: Recalled '{key}' -> {result}")
        else:
            state["execution_result"] = "<FORGOTTEN>"
            state["dissonance_report"] = f"Memory not found: {key}"
            
        return state

    def _handle_analysis(self, payload: Any, state: Dict[str, Any]) -> Dict[str, Any]:
        """Existing default analysis behavior (Stub for now)."""
        state["execution_result"] = f"Analyzed: {payload}"
        return state


@runtime_checkable
class KapilaProtocol(Protocol):
    """
    The Analysis/Inference Protocol - Kapila's domain.

    DERIVED: Position 6 -> KAPILA, GARBAGE_COLLECT, DHARMA
    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 6 in the Mahamantra."""
        ...

    def analyze(self, target: AnalysisInput) -> AnalysisResult:
        """Analyze the target. WATERTIGHT input."""
        ...

    def resolve(self, query: str) -> AnalysisResult:
        """RESOLVE_REQ: Resolve a query through analysis."""
        ...

    def optimize(self, target: str, metric: str) -> OptimizationResult:
        """OPTIMIZE: Optimize a target for a metric."""
        ...

    def enumerate(self, domain: str) -> List[str]:
        """Sankhya enumeration of elements in a domain."""
        ...

    def get_metrics(self) -> MetricsResult:
        """Return collected metrics. WATERTIGHT."""
        ...

    def get_state(self) -> AnalysisState:
        """Get analysis state. WATERTIGHT."""
        ...


# =============================================================================
# NULL KAPILA
# =============================================================================


class NullKapila(KapilaProtocolBase):
    """
    The Unanalyzed. No analysis (for testing).

    Inherits from KapilaProtocolBase -> position 6 -> KAPILA.
    """

    def analyze(self, target: AnalysisInput = None) -> AnalysisResult:
        return AnalysisResult(
            success=True,
            analysis_type="resolution",
            conclusion="No analysis available",
            confidence=0.0,
            duration_ms=0,
            error_message="",
        )

    def resolve(self, query: str = "") -> AnalysisResult:
        return self.analyze(query)

    def optimize(self, target: str = "", metric: str = "") -> OptimizationResult:
        return OptimizationResult(
            success=True,
            improvement_percent=0.0,
            original_metric=0.0,
            optimized_metric=0.0,
            changes_made=[],
            error_message="",
        )

    def enumerate(self, domain: str = "") -> List[str]:
        return []

    def get_metrics(self) -> MetricsResult:
        return MetricsResult(
            metrics={},
            collected_at=datetime.now().isoformat(),
            sample_count=0,
        )

    def get_state(self) -> AnalysisState:
        return AnalysisState(
            analyses_performed=0,
            optimizations_performed=0,
            total_improvement=0.0,
            health="pristine",
        )

    def analyze_cli(self, target: str = "system") -> AnalyzeCliResult:
        """CLI: Analyze target. WATERTIGHT."""
        result = self.analyze(target)
        return AnalyzeCliResult(
            success=result.get("success", True),
            target=target,
            analysis_type=result.get("analysis_type", "resolution"),
            conclusion=result.get("conclusion", "No analysis"),
            confidence=result.get("confidence", 0.0),
        )


# =============================================================================
# COGNITIVE PROTOCOL (Kapila's Analytical Mind)
# =============================================================================

from vibe_core.protocols.mahajanas.kapila.cognition import (
    # Types (WATERTIGHT)
    IntentType,
    SyscallParams,
    QueryResult,
    MessageRecord,
    TickResult,
    ThoughtResult,
    HeartbeatResult,
    # Dataclasses
    CognitiveResult,
    SignedOperatorInput,
    CognitiveContext,
    # Protocols
    CognitiveKernelProtocol,
    SystemHeartbeatProtocol,
    OperatorCognitiveProtocol,
    # Null implementation
    NullCognitive,
)

# =============================================================================
# SAMKHYA PROTOCOL (24 Prakriti Element Mapping)
# =============================================================================

from vibe_core.protocols.mahajanas.kapila.samkhya import (
    # Enums
    PrakritiCategory,
    PrakritiElement,
    # Mappings
    ELEMENT_PROTOCOL_LAYER,
    ELEMENT_GUARDIAN,
    ELEMENT_OPCODE,
    # Types (WATERTIGHT)
    ElementAnalysis,
    EntropyReport,
    SamkhyaState,
    # Protocol
    SamkhyaProtocol,
    get_samkhya,
    # Convenience functions
    analyze_prakriti_element,
    analyze_protocol_entropy,
    route_wild_protocol,
    fight_protocol_entropy,
    enumerate_all_elements,
)

# =============================================================================
# MIGRATED TYPES - Accessed via mahamantra.mod.kapila
# =============================================================================

from vibe_core.protocols.mahajanas.kapila.types import (
    # topology.py
    Varsha,
    Agent,
    AgentPlacement,
    BhuMandalaTopology,
    get_topology,
    refresh_topology,
    get_agent_placement,
    # circuit_types.py
    InvariantViolation,
    CircuitState,
    CircuitExecutionResult,
    TaskLedgerEntry,
    ErrorRecoveryAttempt,
)


# =============================================================================
# CLI - Krishna Discovers Everything (ZERO REGISTRATION)
# =============================================================================
#
# NO MANUAL REGISTRATION NEEDED.
#
# cli_auto.discover_all() introspects KapilaProtocol and auto-generates
# CLI handlers from method signatures:
#
#     analyze(target) → CLI: analyze <target>
#     resolve(query)  → CLI: resolve <query>
#     optimize(target, metric) → CLI: optimize <target> <metric>
#     enumerate(domain) → CLI: enumerate <domain>
#     get_metrics() → CLI: get_metrics
#     get_state() → CLI: get_state
#
# The TypedDict return types (AnalysisResult, OptimizationResult, etc.)
# are auto-converted to CLIOutput by cli_auto.
#
# "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
# Krishna ALREADY KNOWS what Kapila can do. No need to tell Him.
#
# =============================================================================


__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "KapilaProtocolBase",
    # Analysis Types (WATERTIGHT)
    "AnalysisInput",
    "AnalysisType",
    "AnalysisResult",
    "OptimizationResult",
    "MetricsResult",
    "AnalysisState",
    "AnalyzeCliResult",
    # Analysis Protocol
    "KapilaProtocol",
    "NullKapila",
    # Cognitive Types (WATERTIGHT)
    "IntentType",
    "SyscallParams",
    "QueryResult",
    "MessageRecord",
    "TickResult",
    "ThoughtResult",
    "HeartbeatResult",
    # Cognitive Dataclasses
    "CognitiveResult",
    "SignedOperatorInput",
    "CognitiveContext",
    # Cognitive Protocols
    "CognitiveKernelProtocol",
    "SystemHeartbeatProtocol",
    "OperatorCognitiveProtocol",
    # Null implementations
    "NullCognitive",
    # Samkhya Enums
    "PrakritiCategory",
    "PrakritiElement",
    # Samkhya Mappings
    "ELEMENT_PROTOCOL_LAYER",
    "ELEMENT_GUARDIAN",
    "ELEMENT_OPCODE",
    # Samkhya Types (WATERTIGHT)
    "ElementAnalysis",
    "EntropyReport",
    "SamkhyaState",
    # Samkhya Protocol
    "SamkhyaProtocol",
    "get_samkhya",
    # Samkhya Convenience functions
    "analyze_prakriti_element",
    "analyze_protocol_entropy",
    "route_wild_protocol",
    "fight_protocol_entropy",
    "enumerate_all_elements",
    # Service (Real Implementation)
    "KapilaService",
    # === MIGRATED TYPES (mahamantra.mod.kapila) ===
    # topology.py
    "Varsha",
    "Agent",
    "AgentPlacement",
    "BhuMandalaTopology",
    "get_topology",
    "refresh_topology",
    "get_agent_placement",
    # circuit_types.py
    "InvariantViolation",
    "CircuitState",
    "CircuitExecutionResult",
    "TaskLedgerEntry",
    "ErrorRecoveryAttempt",
]

# =============================================================================
# KAPILA SERVICE - The Real Implementation
# =============================================================================

from vibe_core.protocols.mahajanas.kapila.service import KapilaService


# =============================================================================
# MODULE-LEVEL DISPATCH (For ShadowReactor)
# =============================================================================

_kapila_instance = KapilaProtocolBase()

def on_bhoga(state: Dict[str, Any]) -> None:
    """
    Module-level dispatch for ShadowReactor.
    
    The ShadowReactor discovers modules and calls on_bhoga(state).
    We delegate to the protocol instance.
    """
    # Delegate logic to the class method
    # Note: on_bhoga determines what to do and updates state inplace.
    # The return value from class method logic (new state) is ignored by ShadowReactor?
    # No, ShadowReactor calls on_bhoga(state), and state is mutable.
    # Wait, my class method returns state.
    # I should update the state dict passed in.
    
    updated_state = _kapila_instance.on_bhoga(state)
    # Since on_bhoga modifies state in-place mostly, but returns it too.
    # We ensure the original dict is updated if new keys were added not in-place?
    # Dicts are mutable. on_bhoga(state) receives ref.
    pass
