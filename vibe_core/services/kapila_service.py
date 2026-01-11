"""
KAPILA SERVICE - Analysis & Cognition
=====================================

Implements KapilaProtocol (Analysis).
Handles Operator Input Processing and Cognition.

"Kapila analyzes the 24 elements to find the One."
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from vibe_core.protocols.mahajanas.kapila import (
    KapilaProtocol,
    AnalysisInput,
    AnalysisResult,
    OptimizationResult,
    MetricsResult,
    AnalysisState,
    OWNER
)
from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.protocols.cognition import (
    OperatorCognitiveProtocol,
    CognitiveResult,
    SignedOperatorInput,
    NullCognitive
)

logger = logging.getLogger("KAPILA_SERVICE")

class KapilaService(KapilaProtocol):
    """
    KapilaService - The Analyzer.
    Manages cognition, intent resolution, and system metrics.
    """

    def __init__(self):
        self._analyses_performed = 0
        self._cognitive: OperatorCognitiveProtocol = NullCognitive()

    @property
    def owner(self) -> Mahajana:
        return OWNER

    def analyze(self, target: AnalysisInput) -> AnalysisResult:
        self._analyses_performed += 1
        return {
            "success": True,
            "analysis_type": "inference",
            "conclusion": f"Kapila analyzed: {str(target)[:50]}",
            "confidence": 1.0,
            "duration_ms": 0,
            "error_message": ""
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
            "error_message": ""
        }

    def enumerate(self, domain: str) -> List[str]:
        return ["prakriti", "purusha", "kala", "karma", "guna"]

    def get_metrics(self) -> MetricsResult:
        return {
            "metrics": {"analyses": float(self._analyses_performed)},
            "collected_at": datetime.now().isoformat(),
            "sample_count": 1
        }

    def get_state(self) -> AnalysisState:
        return {
            "analyses_performed": self._analyses_performed,
            "optimizations_performed": 0,
            "total_improvement": 0.0,
            "last_analysis": datetime.now().isoformat(),
            "health": "pristine"
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
                is_valid = verify_signature(
                    signed_input.message,
                    signed_input.signature,
                    signed_input.identity_id
                )
                if is_valid:
                    sovereign_verified = True
                    logger.info(f"🛡️  KAPILA: Signature verified for {signed_input.identity_id}")
                else:
                    logger.warning(f"⚠️  KAPILA: INVALID signature from {signed_input.identity_id}")
            except Exception as e:
                logger.error(f"❌ KAPILA: Signature verification error: {e}")

        # Route through registered cognitive plugin
        result = await self._cognitive.process_input(
            input_text, 
            session_id=session_id, 
            signed_input=signed_input
        )
        
        # Add metadata
        if hasattr(result, "metadata"):
            result.metadata["sovereign_verified"] = sovereign_verified
            result.metadata["analyzer"] = "kapila"
            
        return result
