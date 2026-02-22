from typing import Protocol, runtime_checkable, List, Union, Callable, Dict, Literal
from vibe_core.mahamantra.protocols._seed import KSETRAJNA
from dataclasses import dataclass

# Type Aliases
AlignmentLiteral = Literal["perfect", "partial", "none", "hostile"]
ComplexityLiteral = Literal["structure", "hash", "tree", "linear", "quadratic", "exponential"]
MemoryLiteral = Literal["bounded_static", "bounded_dynamic", "unbounded_gc", "unbounded_manual", "unbounded_never"]
DeterminismLiteral = Literal["always", "usually", "random", "chaotic"]


@runtime_checkable
class MahaClassificationProtocol(Protocol):
    """
    Protocol for MahaClassification: Technology Analysis.

    Classifies algorithms based on the Mercy Equation (G = f/K).
    """

    def classify(
        self,
        name: str,
        *,
        alignment: Union[AlignmentLiteral, str],
        complexity: Union[ComplexityLiteral, str],
        memory: Union[MemoryLiteral, str],
        determinism: Union[DeterminismLiteral, str],
        key_space_size: int,
        max_memory_bytes: int,
        ops_per_second: float = 0.0,
        speedup_vs_baseline: float = 1.0,
        levels: int = KSETRAJNA,
        entries_per_level: int = 65536,
    ) -> "ClassificationResult":
        """Classify a technology."""
        ...

    def quick_verdict(
        self,
        *,
        uses_16_alignment: bool,
        is_o1_by_structure: bool,
        is_bounded: bool,
        is_deterministic: bool,
    ) -> str:
        """Get quick ANUKULYA/PRATIKULYA verdict."""
        ...

    def compare(self, technologies: List["ClassificationResult"]) -> "ComparisonResult":
        """Compare multiple technologies."""
        ...

    def compare_all_references(self) -> "ComparisonResult":
        """Compare reference implementations."""
        ...


@dataclass(frozen=True)
class ClassificationResult:
    """Enterprise-friendly classification result."""

    name: str
    verdict: str
    is_anukulya: bool
    mercy_advantage: float
    chanting_frequency: float
    karmic_debt: float
    alignment: str
    complexity: str
    memory: str
    determinism: str

    # Method to export as dict - Typed strictly
    to_dict: Callable[[], Dict[str, Union[str, int, float, bool]]]


@dataclass(frozen=True)
class ComparisonResult:
    """Result of comparing technologies."""

    technologies: List[ClassificationResult]

    @property
    def best(self) -> ClassificationResult:
        return max(self.technologies, key=lambda t: t.mercy_advantage)

    @property
    def summary(self) -> str:
        return f"Comparison of {len(self.technologies)} technologies. Best: {self.best.name}"
