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
__genesis__ = "0x348ce48e2986757649ef37ccd73ad6b0cad14a59f72a1733f9300f8d6673d28f"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

# Avoid circular import - types for annotations only
if TYPE_CHECKING:
    from vibe_core.protocols.mahajanas.kapila import (
        KapilaProtocol,
        AnalysisInput,
        AnalysisResult,
        OptimizationResult,
        MetricsResult,
        AnalysisState,
    )
    from vibe_core.protocols.cognition import (
        OperatorCognitiveProtocol,
        CognitiveResult,
        SignedOperatorInput,
    )

from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.services._executable_mixin import ExecutableMixin

logger = logging.getLogger("KAPILA_SERVICE")


class KapilaService(PanchaTattvaProtocol, ExecutableMixin):
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

        # VARNASHRAMA INTEGRATION:
        # Spawn the JivaShadow qualified for this position.
        # "Subdivision is already sufficient." - User
        from vibe_core.mahamantra.lila.adhikara import spawn_shadow_for_position

        self._shadow = spawn_shadow_for_position(6, context=b"kapila_service_v1")

        # Lazy import to avoid circular dependency
        from vibe_core.protocols.cognition import NullCognitive

        self._cognitive: "OperatorCognitiveProtocol" = NullCognitive()

    @property
    def owner(self) -> Mahajana:
        return Mahajana.KAPILA  # Position 6

    def analyze(self, target: "AnalysisInput") -> "AnalysisResult":
        self._analyses_performed += 1
        return {
            "success": True,
            "analysis_type": "inference",
            "conclusion": f"Kapila analyzed: {str(target)[:50]}",
            "confidence": 1.0,
            "duration_ms": 0,
            "error_message": "",
        }

    def resolve(self, query: str) -> "AnalysisResult":
        return self.analyze(query)

    def optimize(self, target: str, metric: str) -> "OptimizationResult":
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

    def get_metrics(self) -> "MetricsResult":
        return {
            "metrics": {"analyses": float(self._analyses_performed)},
            "collected_at": datetime.now().isoformat(),
            "sample_count": 1,
        }

    def get_state(self) -> "AnalysisState":
        return {
            "analyses_performed": self._analyses_performed,
            "optimizations_performed": 0,
            "total_improvement": 0.0,
            "last_analysis": datetime.now().isoformat(),
            "health": "pristine",
        }

    # --- Cognitive Delegation ---

    def register_cognitive(self, cognitive: "OperatorCognitiveProtocol") -> None:
        old_type = type(self._cognitive).__name__
        self._cognitive = cognitive
        logger.info(f"🧠 KAPILA: Cognitive hook updated: {old_type} → {type(cognitive).__name__}")

    async def process_operator_input(
        self,
        kernel: Any,
        input_text: str,
        session_id: Optional[str] = None,
        signed_input: Optional["SignedOperatorInput"] = None,
    ) -> "CognitiveResult":
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
