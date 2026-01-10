"""
KAPILA - The 5th Mahajana (Analysis/Inference)
==============================================
OpCodes: RESOLVE_REQ (Bit 6), OPTIMIZE (Bit 14)
         Position 6 and 14 in Mahamantra
Opulence: Jnana (Knowledge)

Lord Kapila - The Founder of Sankhya.
Son of Devahuti. Teacher of analytical philosophy.
His Sankhya is the basis of this entire architecture.

PROTOCOL OWNERSHIP (Anti-Mayavad):
Kapila is the PERSON responsible for all analysis.
Not abstract "inference engine" - PERSONAL analysis by Kapila.

OWNED PROTOCOLS:
- Request Resolution (RESOLVE_REQ OpCode)
- Optimization (OPTIMIZE OpCode)
- Inference/Analysis
- IndriyaProtocol (I/O registers - Level -1)
- Sankhya Analysis (24 elements enumeration)

Kapila analyzes, but for the purpose of DEVOTION.
His Sankhya leads to bhakti, not dry speculation.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# PROTOCOL OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.KAPILA

OWNED_PROTOCOLS: Final[List[str]] = [
    "kapila",
    "analysis",
    "inference",
    "sankhya",
    "optimization",
    "indriya",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.RESOLVE_REQ,
    MantraOpCode.OPTIMIZE,
]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

# The union of allowed analysis input types - WATERTIGHT
AnalysisInput = Union[str, int, float, bool, Dict[str, str], List[str], None]


class AnalysisType(str, Enum):
    """Types of analysis."""
    RESOLUTION = "resolution"     # RESOLVE_REQ
    OPTIMIZATION = "optimization" # OPTIMIZE
    INFERENCE = "inference"       # Logical deduction
    ENUMERATION = "enumeration"   # Sankhya counting


class AnalysisResult(TypedDict, total=False):
    """
    Result of analysis.
    WATERTIGHT - no Any!
    """
    success: bool
    analysis_type: str        # AnalysisType value
    conclusion: str           # The analytical result
    confidence: float         # 0.0-1.0
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
    collected_at: str         # ISO timestamp
    sample_count: int


class AnalysisState(TypedDict, total=False):
    """
    State of analysis.
    WATERTIGHT - no Any!
    """
    analyses_performed: int
    optimizations_performed: int
    total_improvement: float
    last_analysis: str        # ISO timestamp
    health: str


# =============================================================================
# KAPILA PROTOCOL
# =============================================================================


@runtime_checkable
class KapilaProtocol(Protocol):
    """
    The Analysis/Inference Protocol - Kapila's domain.
    WATERTIGHT - no Any types!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.KAPILA."""
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


class NullKapila:
    """The Unanalyzed. No analysis (for testing)."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.KAPILA

    def analyze(self, target: AnalysisInput) -> AnalysisResult:
        return AnalysisResult(
            success=True,
            analysis_type="resolution",
            conclusion="No analysis available",
            confidence=0.0,
            duration_ms=0,
            error_message="",
        )

    def resolve(self, query: str) -> AnalysisResult:
        return self.analyze(query)

    def optimize(self, target: str, metric: str) -> OptimizationResult:
        return OptimizationResult(
            success=True,
            improvement_percent=0.0,
            original_metric=0.0,
            optimized_metric=0.0,
            changes_made=[],
            error_message="",
        )

    def enumerate(self, domain: str) -> List[str]:
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


__all__ = [
    "OWNER", "OWNED_PROTOCOLS", "OWNED_OPCODES",
    "AnalysisInput", "AnalysisType", "AnalysisResult",
    "OptimizationResult", "MetricsResult", "AnalysisState",
    "KapilaProtocol", "NullKapila",
]
