"""
INFER PROTOCOL - Layer 2 (Cognition/Buddhi)

GAD-000 COMPLIANT:
- Discoverability: clearly defined input/output schemas
- Observability: Inference results include reasoning and confidence
- Parseability: Structured returns (Inference/Classification objects)
- Composability: Output of one inference feeds input of another
- Idempotency: Inference should be pure function of input
- Recoverability: fallback parameter ← RED-004 FIX
"""

from typing import Optional, Protocol, runtime_checkable

from .types import Classification, ClassifyInput, Evaluation, Inference, InferenceInput, SovereignContext


@runtime_checkable
class InferProtocol(Protocol):
    """
    Atomic protocol for inference and cognition (The Intellect/Buddhi).

    GAD-000: Recoverability via fallback parameter.
    """

    def infer(
        self,
        input: InferenceInput,
        fallback: Optional[Inference] = None,  # RED-004 FIX
    ) -> Inference:
        """
        Draw a general inference from input.

        Args:
            input: InferenceInput with content + context.
            fallback: Optional fallback if inference fails (GAD-000 Recoverability).

        Returns:
            Inference result, or fallback if provided and inference fails.
        """
        ...

    def classify(
        self,
        input: ClassifyInput,
        fallback: Optional[Classification] = None,  # RED-004 FIX
    ) -> Classification:
        """
        Classify input into defined categories.

        Args:
            input: ClassifyInput with content + categories.
            fallback: Optional fallback classification (GAD-000 Recoverability).
        """
        ...

    def evaluate(
        self,
        claim: str,
        context: Optional[SovereignContext] = None,
        fallback: Optional[Evaluation] = None,  # RED-004 FIX
    ) -> Evaluation:
        """
        Evaluate the truth or validity of a claim.

        Args:
            claim: The statement to verify.
            context: (Required for Anti-Mayavad) Identity requesting eval.
            fallback: Optional fallback evaluation (GAD-000 Recoverability).
        """
        ...
