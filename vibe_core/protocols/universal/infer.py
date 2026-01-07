from typing import Optional, Protocol, runtime_checkable

from .types import Classification, ClassifyInput, Evaluation, Inference, InferenceInput, SovereignContext


@runtime_checkable
class InferProtocol(Protocol):
    """
    Atomic protocol for inference and cognition (The Intellect/Buddhi).

    GAD-000 COMPLIANCE:
    - Discoverability: clearly defined input/output schemas.
    - Observability: Inference results include reasoning and confidence.
    - Parseability: Structured returns (Inference/Classification objects).
    - Composability: Output of one inference feeds input of another.
    - Idempotency: Inference should be pure function of input ideally.
    - Recoverability: Fallback to heuristic or safe defaults.
    """

    def infer(self, input: InferenceInput) -> Inference:
        """
        Draw a general inference from input.
        Input object carries Sovereign Context.
        """
        ...

    def classify(self, input: ClassifyInput) -> Classification:
        """
        Classify input into defined categories.
        Input object carries Sovereign Context.
        """
        ...

    def evaluate(self, claim: str, context: Optional[SovereignContext] = None) -> Evaluation:
        """
        Evaluate the truth or validity of a claim.
        Args:
            claim: The statement to verify.
            context: (Required for Anti-Mayavad) Identity requesting eval.
        """
        ...
