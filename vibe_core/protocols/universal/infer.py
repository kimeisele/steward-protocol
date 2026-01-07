from typing import Protocol, runtime_checkable

from .types import Classification, ClassifyInput, Evaluation, Inference, InferenceInput


@runtime_checkable
class InferProtocol(Protocol):
    """
    Atomic protocol for inference and cognition.
    Standardizes inputs/outputs for AI/Logic components.
    """

    def infer(self, input: InferenceInput) -> Inference:
        """Draw a general inference from input."""
        ...

    def classify(self, input: ClassifyInput) -> Classification:
        """Classify input into defined categories."""
        ...

    def evaluate(self, claim: str) -> Evaluation:
        """Evaluate the truth or validity of a claim."""
        ...
