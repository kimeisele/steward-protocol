"""
KAPILA SERVICE - Analysis & Cognition
=====================================

Implements KapilaProtocol (Analysis).
Handles Operator Input Processing and Cognition.

"Kapila analyzes the 24 elements to find the One."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0xc30db303"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.protocols.cognition import CognitiveResult, NullCognitive, OperatorCognitiveProtocol, SignedOperatorInput
from vibe_core.protocols.mahajanas.kapila import (
    AnalysisInput,
    AnalysisResult,
    AnalysisState,
    KapilaProtocol,
    MetricsResult,
    OptimizationResult,
)
from vibe_core.protocols.mahajanas.router import Mahajana

logger = logging.getLogger("KAPILA_SERVICE")


class KapilaService(KapilaProtocol, PanchaTattvaProtocol):
    """
    KapilaService - The Analyzer.
    Manages cognition, intent resolution, and system metrics.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold Truth of Kapila Service."""
        return {
            "chaitanya": "Analysis & Cognition Service",
            "nityananda": "Cognitive Protocol Hook",
            "advaita": "Inference & Optimization Logic",
            "gadadhara": "Operator Input Flow",
            "srivasa": "Metrics & Health Governance",
        }

    def __init__(self):
        self._analyses_performed = 0
        self._cognitive: OperatorCognitiveProtocol = NullCognitive()

    @property
    def owner(self) -> Mahajana:
        return Mahajana.KAPILA  # Position 6

    def analyze(self, target: AnalysisInput) -> AnalysisResult:
        self._analyses_performed += 1
        return {
            "success": True,
            "analysis_type": "inference",
            "conclusion": f"Kapila analyzed: {str(target)[:50]}",
            "confidence": 1.0,
            "duration_ms": 0,
            "error_message": "",
        }

    def resolve(self, query: str) -> AnalysisResult:
        return self.analyze(query)

    def optimize(self, target: str, metric: str) -> OptimizationResult:
        return {
            "success": True,
            "improvement_percent": 0.0,
            "original_metric": 0.0,
            "optimized_metric": 0.0,
            "changes_made": [],
            "error_message": "",
        }

    def enumerate(self, domain: str) -> List[str]:
        return ["prakriti", "purusha", "kala", "karma", "guna"]

    def get_metrics(self) -> MetricsResult:
        return {
            "metrics": {"analyses": float(self._analyses_performed)},
            "collected_at": datetime.now().isoformat(),
            "sample_count": 1,
        }

    def get_state(self) -> AnalysisState:
        return {
            "analyses_performed": self._analyses_performed,
            "optimizations_performed": 0,
            "total_improvement": 0.0,
            "last_analysis": datetime.now().isoformat(),
            "health": "pristine",
        }

    # --- Cognitive Delegation ---

    def register_cognitive(self, cognitive: OperatorCognitiveProtocol) -> None:
        old_type = type(self._cognitive).__name__
        self._cognitive = cognitive
        logger.info(f"🧠 KAPILA: Cognitive hook updated: {old_type} → {type(cognitive).__name__}")

    async def process_operator_input(
        self,
        kernel: Any,
        input_text: str,
        session_id: Optional[str] = None,
        signed_input: Optional[SignedOperatorInput] = None,
    ) -> CognitiveResult:
        """
        Process operator input.
        Moved from Kernel to Kapila (Analysis).
        """
        # GAD-000 v2.0: Verify sovereign signature if provided
        sovereign_verified = False
        if signed_input and signed_input.is_signed():
            try:
                from vibe_core.steward.crypto import verify_signature

                is_valid = verify_signature(signed_input.message, signed_input.signature, signed_input.identity_id)
                if is_valid:
                    sovereign_verified = True
                    logger.info(f"🛡️  KAPILA: Signature verified for {signed_input.identity_id}")
                else:
                    logger.warning(f"⚠️  KAPILA: INVALID signature from {signed_input.identity_id}")
            except Exception as e:
                logger.error(f"❌ KAPILA: Signature verification error: {e}")

        # Route through registered cognitive plugin
        result = await self._cognitive.process_input(input_text, session_id=session_id, signed_input=signed_input)

        # Add metadata
        if hasattr(result, "metadata"):
            result.metadata["sovereign_verified"] = sovereign_verified
            result.metadata["analyzer"] = "kapila"

        return result


# =============================================================================
# SERVICEREGISTRY FACTORY (NAGA-OBSERVED!)
# =============================================================================


def get_kapila_service() -> KapilaService:
    """
    Get KapilaService through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        Raw KapilaService → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees all cognitive operations)
    - NAGA profiling (Chitragupta tracks analysis latency)
    - NAGA isolation (Kaliya handles cognitive errors)

    Returns:
        KapilaService wrapped with NagaProxy (if NAGA blessing enabled)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered (use KapilaProtocol as the key)
    existing = ServiceRegistry.get(KapilaProtocol)
    if existing is not None:
        return existing  # type: ignore

    # Create new instance
    instance = KapilaService()

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(KapilaProtocol, instance)
    logger.info("✅ KapilaService registered via ServiceRegistry (WIRED + NAGA-observed)")

    return ServiceRegistry.get(KapilaProtocol)  # type: ignore


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "KapilaService",
    "get_kapila_service",
]
