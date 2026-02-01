"""
MAHACLASSIFIER - Technology Classification Adapter
===================================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"Know that I am the eternal seed of all existences."
— Bhagavad Gita 7.10

ENTERPRISE INTERFACE FOR:
    Cold engineering classification of algorithms and data structures.
    No metaphors. No philosophy. Pure metrics.

THE MERCY EQUATION:
    G(x) = f / K
    Where:
        G = Grace (engineering advantage)
        f = Chanting frequency (Mahamantra structure usage)
        K = Karmic debt (technical debt)

USAGE:
    from vibe_core.mahamantra import mahamantra

    classifier = mahamantra.classifier()

    # Classify a custom algorithm
    result = classifier.classify(
        name="MyRouter",
        alignment="perfect",
        complexity="structure",
        memory="bounded_static",
        determinism="always",
        key_space_size=65536,
        max_memory_bytes=512_000,
    )

    print(result.verdict)           # "ANUKULYA: Truth-aligned (G=100.0)"
    print(result.mercy_advantage)   # 100.0

    # Get pre-classified reference implementations
    lotus = classifier.lotus_array()
    ipv4 = classifier.ipv4_router()
    kmer = classifier.kmer_index()

    # Compare technologies
    comparison = classifier.compare([lotus, ipv4, result])
    print(comparison.summary)

    # Quick verdict on custom implementation
    verdict = classifier.quick_verdict(
        uses_16_alignment=True,
        is_o1_by_structure=True,
        is_bounded=True,
        is_deterministic=True,
    )
    print(verdict)  # "ANUKULYA"
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 3
__genesis__ = "0x6e44c339"  # GenesisByte: parampara % 37 == 0

from typing import Dict, Final, List, Literal, Optional, Union

from vibe_core.mahamantra.protocols.classification import (
    MahaClassificationProtocol,
    ClassificationResult,
    ComparisonResult,
)
from vibe_core.mahamantra.substrate.classifier import (
    MAHAMANTRA_ADDRESS_SPACE,
    MAHAMANTRA_QUARTERS,
    MAHAMANTRA_WORDS,
    PARAMPARA_PRIME,
    Classification,
    ComplexitySource,
    Determinism,
    MemoryModel,
    StructuralAlignment,
    classify_algorithm,
    classify_blockchain,
    classify_lotus_8mer_index,
    classify_lotus_array_int,
    classify_lotus_ipv4_router,
    classify_lotus_radix_n,
    classify_neural_network_attention,
    classify_python_dict,
    is_golden_age_viable,
)

# =============================================================================
# CONSTANTS
# =============================================================================

WORDS: Final[int] = MAHAMANTRA_WORDS  # 16
QUARTERS: Final[int] = MAHAMANTRA_QUARTERS  # 4
ADDRESS_SPACE: Final[int] = MAHAMANTRA_ADDRESS_SPACE  # 65536
PARAMPARA: Final[int] = PARAMPARA_PRIME  # 37

# =============================================================================
# TYPE ALIASES FOR CONVENIENCE
# =============================================================================

AlignmentLiteral = Literal["perfect", "partial", "none", "hostile"]
ComplexityLiteral = Literal["structure", "hash", "tree", "linear", "quadratic", "exponential"]
MemoryLiteral = Literal["bounded_static", "bounded_dynamic", "unbounded_gc", "unbounded_manual", "unbounded_never"]
DeterminismLiteral = Literal["always", "usually", "random", "chaotic"]


# =============================================================================
# MAHACLASSIFIER - THE ADAPTER
# =============================================================================


class MahaClassifier(MahaClassificationProtocol):
    """
    Technology Classification Engine.

    Cold engineering analysis. No philosophy. Pure metrics.

    THE MERCY EQUATION:
        G(x) = f / K

    Technologies with higher G are more efficient.
    ANUKULYA (favorable) technologies have G >> 1.
    """

    # === CONSTANTS ===
    WORDS: Final[int] = WORDS
    QUARTERS: Final[int] = QUARTERS
    ADDRESS_SPACE: Final[int] = ADDRESS_SPACE
    PARAMPARA: Final[int] = PARAMPARA

    def __init__(self) -> None:
        """Initialize classifier."""
        pass

    # === CLASSIFICATION ===

    def classify(
        self,
        name: str,
        *,
        alignment: Union[AlignmentLiteral, StructuralAlignment],
        complexity: Union[ComplexityLiteral, ComplexitySource],
        memory: Union[MemoryLiteral, MemoryModel],
        determinism: Union[DeterminismLiteral, Determinism],
        key_space_size: int,
        max_memory_bytes: int,
        ops_per_second: float = 0.0,
        speedup_vs_baseline: float = 1.0,
        levels: int = 1,
        entries_per_level: int = ADDRESS_SPACE,
    ) -> ClassificationResult:
        """
        Classify a technology or algorithm.

        Args:
            name: Technology name
            alignment: Structural alignment (perfect/partial/none/hostile)
            complexity: Complexity source (structure/hash/tree/linear/quadratic/exponential)
            memory: Memory model (bounded_static/bounded_dynamic/unbounded_*)
            determinism: Determinism level (always/usually/random/chaotic)
            key_space_size: Number of unique keys
            max_memory_bytes: Maximum memory usage (-1 for unbounded)
            ops_per_second: Measured throughput
            speedup_vs_baseline: Speedup vs dict/linear
            levels: Number of hierarchical levels (1=flat, 8=IPv4-style)
            entries_per_level: Entries per level (16=Mahamantra-aligned)

        Returns:
            ClassificationResult with verdict and metrics
        """
        # Convert string literals to enums
        align = self._to_alignment(alignment)
        comp = self._to_complexity(complexity)
        mem = self._to_memory(memory)
        det = self._to_determinism(determinism)

        inner = classify_algorithm(
            name=name,
            alignment=align,
            complexity=comp,
            memory=mem,
            determinism=det,
            key_space_size=key_space_size,
            max_memory_bytes=max_memory_bytes,
            ops_per_second=ops_per_second,
            speedup_vs_baseline=speedup_vs_baseline,
            levels=levels,
            entries_per_level=entries_per_level,
        )



        return self._to_result(inner)

    def quick_verdict(
        self,
        *,
        uses_16_alignment: bool,
        is_o1_by_structure: bool,
        is_bounded: bool,
        is_deterministic: bool,
    ) -> str:
        """
        Quick ANUKULYA/PRATIKULYA verdict without full classification.

        Args:
            uses_16_alignment: Uses 16-aligned or 65536 bounded structures?
            is_o1_by_structure: O(1) from structure (not hash)?
            is_bounded: Memory is bounded?
            is_deterministic: Output is always predictable?

        Returns:
            "ANUKULYA" or "PRATIKULYA"
        """
        if uses_16_alignment and is_o1_by_structure and is_bounded and is_deterministic:
            return "ANUKULYA"
        return "PRATIKULYA"

    # === PRE-CLASSIFIED TECHNOLOGIES ===

    def lotus_array(self) -> ClassificationResult:
        """
        LotusArrayInt - The reference implementation.

        65536-entry array, O(1) by structure, 512KB fixed.
        50x faster range queries than dict.
        """
        return self._to_result(classify_lotus_array_int())

    def ipv4_router(self) -> ClassificationResult:
        """
        LotusIPv4Router - O(1) Longest Prefix Match.

        8-level radix (16 entries each = 32-bit IPv4).
        1557x faster than linear search.
        """
        return self._to_result(classify_lotus_ipv4_router())

    def kmer_index(self) -> ClassificationResult:
        """
        Lotus8merIndex - DNA k-mer counting.

        4^8 = 65536 = perfect Mahamantra fit.
        6.5x faster than Counter.
        """
        return self._to_result(classify_lotus_8mer_index())

    def radix_n(self, levels: int = 8) -> ClassificationResult:
        """
        LotusRadixN - Generic N-level radix structure.

        Scales to any key size while maintaining 16-alignment.
        levels=4: 16-bit, levels=8: 32-bit, levels=32: 128-bit
        """
        return self._to_result(classify_lotus_radix_n(levels))

    def python_dict(self) -> ClassificationResult:
        """
        Python dict - The common baseline.

        O(1) by HASH (not structure!). Unbounded. Non-deterministic.
        """
        return self._to_result(classify_python_dict())

    def neural_network(self) -> ClassificationResult:
        """
        Neural Network (Attention) - The Tamas exemplar.

        O(N^2) quadratic. Unbounded. Random.
        """
        return self._to_result(classify_neural_network_attention())

    def blockchain(self) -> ClassificationResult:
        """
        Blockchain - The growth addiction.

        O(N) linear, grows forever, never shrinks.
        """
        return self._to_result(classify_blockchain())

    # === COMPARISON ===

    def compare(self, technologies: List[ClassificationResult]) -> ComparisonResult:
        """
        Compare multiple technologies.

        Args:
            technologies: List of ClassificationResult

        Returns:
            ComparisonResult with rankings and summary
        """
        return ComparisonResult(technologies=technologies)

    def compare_all_references(self) -> ComparisonResult:
        """Compare all pre-classified reference technologies."""
        return self.compare([
            self.lotus_array(),
            self.ipv4_router(),
            self.kmer_index(),
            self.radix_n(8),
            self.python_dict(),
            self.neural_network(),
            self.blockchain(),
        ])

    # === HELPERS ===

    def _to_result(self, inner: Classification) -> ClassificationResult:
        """Convert substrate Classification to protocol ClassificationResult."""
        return ClassificationResult(
            name=inner.name,
            verdict=inner.get_engineering_verdict(),
            is_anukulya=inner.is_anukulya,
            mercy_advantage=inner.mercy_advantage,
            chanting_frequency=inner.chanting_frequency,
            karmic_debt=inner.karmic_debt,
            alignment=inner.alignment.name.lower(),
            complexity=inner.complexity.name.lower(),
            memory=inner.memory.name.lower(),
            determinism=inner.determinism.name.lower(),
            to_dict=lambda: {
                "name": inner.name,
                "verdict": inner.get_engineering_verdict(),
                "is_anukulya": inner.is_anukulya,
                "mercy_advantage": inner.mercy_advantage,
                "chanting_frequency": inner.chanting_frequency,
                "karmic_debt": inner.karmic_debt,
                "alignment": inner.alignment.name.lower(),
                "complexity": inner.complexity.name.lower(),
                "memory": inner.memory.name.lower(),
                "determinism": inner.determinism.name.lower(),
            }
        )

    def _to_alignment(self, value: Union[str, StructuralAlignment]) -> StructuralAlignment:
        """Convert string to StructuralAlignment enum."""
        if isinstance(value, StructuralAlignment):
            return value
        mapping = {
            "perfect": StructuralAlignment.PERFECT,
            "partial": StructuralAlignment.PARTIAL,
            "none": StructuralAlignment.NONE,
            "hostile": StructuralAlignment.HOSTILE,
        }
        return mapping[value.lower()]

    def _to_complexity(self, value: Union[str, ComplexitySource]) -> ComplexitySource:
        """Convert string to ComplexitySource enum."""
        if isinstance(value, ComplexitySource):
            return value
        mapping = {
            "structure": ComplexitySource.STRUCTURE,
            "hash": ComplexitySource.HASH,
            "tree": ComplexitySource.TREE,
            "linear": ComplexitySource.LINEAR,
            "quadratic": ComplexitySource.QUADRATIC,
            "exponential": ComplexitySource.EXPONENTIAL,
        }
        return mapping[value.lower()]

    def _to_memory(self, value: Union[str, MemoryModel]) -> MemoryModel:
        """Convert string to MemoryModel enum."""
        if isinstance(value, MemoryModel):
            return value
        mapping = {
            "bounded_static": MemoryModel.BOUNDED_STATIC,
            "bounded_dynamic": MemoryModel.BOUNDED_DYNAMIC,
            "unbounded_gc": MemoryModel.UNBOUNDED_GC,
            "unbounded_manual": MemoryModel.UNBOUNDED_MANUAL,
            "unbounded_never": MemoryModel.UNBOUNDED_NEVER,
        }
        return mapping[value.lower()]

    def _to_determinism(self, value: Union[str, Determinism]) -> Determinism:
        """Convert string to Determinism enum."""
        if isinstance(value, Determinism):
            return value
        mapping = {
            "always": Determinism.ALWAYS,
            "usually": Determinism.USUALLY,
            "random": Determinism.RANDOM,
            "chaotic": Determinism.CHAOTIC,
        }
        return mapping[value.lower()]


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Main class
    "MahaClassifier",
    # Result types
    "ClassificationResult",
    "ComparisonResult",
    # Constants
    "WORDS",
    "QUARTERS",
    "ADDRESS_SPACE",
    "PARAMPARA",
]
